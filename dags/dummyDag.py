from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os
import subprocess
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File Paths
SOURCE1_PATH = "/opt/airflow/data/source1/source1.csv"
SOURCE2_PATH = "/opt/airflow/data/source2/source2.csv"
MERGED_CSV_PATH = "/opt/airflow/output/merged.csv"
OUTPUT_PATH = "/opt/airflow/output/enriched_students.json"
JAR_PATH = "/opt/airflow/javaLib/refdata-1.0-SNAPSHOT.jar"  # Java JAR file path

default_args = {
    'start_date': datetime(2024, 3, 5),
    'catchup': False,
}

dag = DAG(
    'TD_pipeline_POC',
    schedule_interval='@daily',
    default_args=default_args,
)

# 1️ Merge CSV Files
def merge_csv():
    """Reads and merges CSV files"""
    if not os.path.exists(SOURCE1_PATH) or not os.path.exists(SOURCE2_PATH):
        raise FileNotFoundError("One or both source CSV files are missing!")

    df1 = pd.read_csv(SOURCE1_PATH)
    df2 = pd.read_csv(SOURCE2_PATH)
    merged_df = pd.concat([df1, df2], ignore_index=True)

    # Rename columns
    column_mapping = {
        "id": "studentID",
        "name": "Name",
        "age": "Age"
    }
    merged_df = merged_df.rename(columns=column_mapping)
    merged_df.to_csv(MERGED_CSV_PATH, index=False)

merge_csv_task = PythonOperator(
    task_id='merge_csv',
    python_callable=merge_csv,
    dag=dag,
)

# 2️ Extract Student IDs
def extract_student_ids(**kwargs):
    """Extracts student IDs from merged CSV and pushes them to XCom"""
    df = pd.read_csv(MERGED_CSV_PATH)
    student_ids = df["studentID"].tolist()
    kwargs['ti'].xcom_push(key='student_ids', value=student_ids)

extract_ids_task = PythonOperator(
    task_id='extract_student_ids',
    python_callable=extract_student_ids,
    provide_context=True,
    dag=dag,
)

# 3️ Fetch Data from Java JAR
def fetch_student_data(**kwargs):
    """Calls Java JAR for each student ID and returns enriched data"""
    ti = kwargs['ti']
    student_ids = ti.xcom_pull(task_ids='extract_student_ids', key='student_ids')

    if not student_ids:
        logger.error("No student IDs found in XCom! Exiting.")
        return

    logger.info(f"Processing {len(student_ids)} students: {student_ids}")

    enriched_students = []

    for student_id in student_ids:
        command = ["java", "-jar", JAR_PATH, str(student_id)]
        logger.info(f"Executing command: {' '.join(command)}")

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )

            if result.stdout:
                logger.info(f"Java Output for student {student_id}: {result.stdout}")
                student_data = json.loads(result.stdout)  # Parse JSON from Java output
                enriched_students.append(student_data)
            else:
                logger.warning(f"No output received from Java for student {student_id}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Error processing student {student_id}: {e}")
            logger.error(f"Standard Error: {e.stderr}")

    logger.info(f"Enriched students data: {enriched_students}")
    ti.xcom_push(key='enriched_students', value=enriched_students)

fetch_data_task = PythonOperator(
    task_id='Data_enrichment',
    python_callable=fetch_student_data,
    provide_context=True,
    dag=dag,
)

def save_to_json(**kwargs):
    """Saves processed student data as JSON"""
    ti = kwargs['ti']
    enriched_students = ti.xcom_pull(task_ids='Data_enrichment', key='enriched_students')

    if not enriched_students:
        logger.error("❌ No data retrieved from XCom! Exiting save_to_json.")
        return

    logger.info(f"✅ Retrieved {len(enriched_students)} students from XCom: {enriched_students}")

    try:
        with open(OUTPUT_PATH, "w") as f:
            json.dump(enriched_students, f, indent=4)
        logger.info(f"✅ Enriched student data saved to {OUTPUT_PATH}")
    except Exception as e:
        logger.error(f"❌ Failed to write JSON file: {e}")

save_json_task = PythonOperator(
    task_id='save_json',
    python_callable=save_to_json,
    provide_context=True,
    dag=dag,
)


# Define Task Order
merge_csv_task >> extract_ids_task >> fetch_data_task >> save_json_task
