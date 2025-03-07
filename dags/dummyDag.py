import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import csv
import io
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
# API URL
API_URL = "https://23d753f7-3609-4c1a-85b9-83209377f25c.mock.pstmn.io/refdata"

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

def fetch_student_data(**kwargs):
    """Fetches student data from an API, filters by student IDs, and formats as JSON for XCom."""
    ti = kwargs['ti']
    student_ids = ti.xcom_pull(task_ids='extract_student_ids', key='student_ids')

    if not student_ids:
        logger.error("❌ No student IDs found in XCom! Exiting.")
        return

    logger.info(f"🔍 Fetching student data from API for {len(student_ids)} students.")

    try:
        # Call the API
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise error for bad responses

        # Read the CSV response properly using `csv.DictReader`
        csv_data = io.StringIO(response.text)
        reader = csv.DictReader(csv_data)

        # Convert CSV to a list of dictionaries
        students_data = [row for row in reader]

        # Filter students based on extracted IDs
        enriched_students = [student for student in students_data if student["id"] in map(str, student_ids)]

        logger.info(f"✅ Enriched student data: {json.dumps(enriched_students, indent=4)}")

        # Push enriched data to XCom for the next Airflow task
        ti.xcom_push(key='enriched_students', value=enriched_students)

    except requests.RequestException as e:
        logger.error(f"❌ API request failed: {e}")

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
