# 🚀 Airflow POC for Student Data Processing

##  Overview
This Proof of Concept (POC) demonstrates an **Apache Airflow** pipeline that processes student data using **CSV files**, **a Java JAR file**, and **Dockerized Airflow setup**. The pipeline extracts student data, enriches it using a **Java application**, and stores the results in **JSON format**.

---

##  High-Level Architecture
The system consists of the following key components:

1. **Apache Airflow DAG (`dummyDag.py`)**
   - Extracts student data from CSV files.
   - Calls a **Java JAR** file to enrich student data.
   - Saves the enriched data to a JSON file.

2. **Java JAR (`refdata-1.0-SNAPSHOT.jar`)**
   - Fetches additional student information (e.g., **Address, Major**) based on the Student ID.

3. **Dockerized Environment**
   - Uses a **Dockerfile** to set up Airflow with Java 8 support.
   - `docker-compose.yml` orchestrates the Airflow services.

---

## ️ DAG Workflow

The DAG processes student data through the following tasks:

- **merge_csv**: Reads two CSV source files and merges them into one, renaming columns.
- **extract_student_ids**: Extracts student IDs from the merged CSV file.
- **Data_enrichment**: Calls a Java JAR to enrich student data based on student IDs.
- **save_json**: Saves the enriched student data to a JSON file.

**DAG Flow**:

```
merge_csv ➡️ extract_student_ids ➡️ Data_enrichment ➡️ save_json
```
![Image](https://github.com/user-attachments/assets/8c254cf9-384f-4ad6-bcd4-d63569b6f789)
---

📌 **How to Run the Airflow POC**

## 1️⃣ Start Airflow with devcontainer

```bash
docker-compose up -d   
``` 
<!-- Install devcontainer plugin on VScode
![Image](https://github.com/user-attachments/assets/882c9cd8-2049-4b6f-8f59-9f57c7714a42)

Search command: win+shift+p - rebuild And Reopen In Container
```bash
@command:remote-containers.rebuildAndReopenInContainer
```
![Image](https://github.com/user-attachments/assets/e738b49c-3148-4dbd-ae9f-113aed68b348) -->

## 2️⃣ Access the Airflow Web UI  

Open your browser and navigate to:

```bash
http://localhost:8080
```

- **Username:** `airflow`
- **Password:** `airflow`


## 3️⃣ Trigger the DAG from the Airflow Web UI  

1. In the **Airflow UI**, go to the **DAGs** list.  
2. Locate `TD_pipeline_POC` (or your DAG name). ![Image](https://github.com/user-attachments/assets/99deb574-95b2-45cb-91c7-311000471ab1)
3. Click the **Trigger DAG** button ▶️.![Image](https://github.com/user-attachments/assets/34a8af78-c256-4949-9cba-9153e3dc9b16)


## 4️⃣ Verify the Output  

Once the DAG has successfully run:

- Check the **output JSON file** inside your **project's `output/` folder** (since it is mounted in Docker):

```bash
cat output/enriched_students.json
```

- Alternatively, check from your **file explorer** (e.g., VS Code, Finder, Windows Explorer).

---

## ** Expected Output**
After running the DAG, the JSON file `/output/enriched_students.json` should contain:
```json
[
  {
    "studentID": "1",
    "Name": "Alice",
    "Age": 27,
    "Address": "123 Main St",
    "Major": "Computer Science"
  },
  {
    "studentID": "2",
    "Name": "Bob",
    "Age": 30,
    "Address": "456 Queen St",
    "Major": "Mathematics"
  }
]
```
---

## ✅ Airflow Feature Evaluation


| Requirement                                      | Airflow Support                                    | Workaround / Notes                           |
|--------------------------------------------------|----------------------------------------------------|-----------------------------------------------------|
| **Batch & Streaming Support**      | ⚠️ Partial: ✅ Batch, ❌ Limited Streaming           | Use **Apache Kafka + NIFI/Flink** for streaming.  |
| **Configurable Transformations**         | ✅ Yes (via code)                                  | Use external **config files or Airflow Variables**.|
| **Horizontal Scalability**         | ✅ Yes                                             | Supports CeleryExecutor and KubernetesExecutor for distributed execution across multiple workers.      |
| **Self-Hosted Deployment**                             | ✅ Yes                                             | Airflow can be deployed on on-premise servers, private cloud, or Kubernetes.                                               |
| **Real-Time Stream Processing (<1 sec latency)**     | ❌ No                                              | Use **Apache Kafka + NIFI/Flink** for streaming.            |
| **End-to-End Testability**        | ⚠️ Partial                                        | Integrate testing tools like **pytest-airflow**.   |
| **Retry Mechanism**                          | ✅ Yes                                             | Airflow supports automatic retries, exponential backoff, and custom error handling via retries, retry_delay, and retry_exponential_backoff.                                                |
| **Re-Runnable Workflows**                        | ✅ Yes                                             | DAGs support rerunning only failed tasks via UI, CLI, API, or depends_on_past.                                               |

---

## 🧪 **Testability in Airflow**

Airflow provides effective support for **unit and task-level testing**, but true **end-to-end testing** is limited.

### ✅ **Unit & Task-Level Testing**

Airflow DAGs are defined in Python, making them easily testable using standard Python testing frameworks such as **`pytest`**.

- **Test Individual Tasks:**
  - Each task can be tested independently by calling its Python functions directly.
  - Ideal for verifying **logic, configurations, and outputs**.

### ✅ **pytest-airflow**

[`pytest-airflow`](https://github.com/apache/airflow/tree/main/tests) is a testing framework designed specifically for Airflow, allowing you to:

- Test DAG structures and task definitions.
- Validate task dependencies and scheduling logic.
- Run tasks in isolation, verifying behavior and exceptions.


---

## 🔄 **Retry Mechanism in Airflow Tasks**

In Apache Airflow, a built-in retry mechanism can be configured directly within task definitions, significantly improving the robustness and reliability of workflows, especially when tasks involve external dependencies or network calls.

### ✅ **How to Configure Task Retries**
When defining tasks in Airflow, retries are specified through two main parameters:

- `retries`: Defines how many times Airflow should automatically retry a failed task.
- `retry_delay`: Specifies the delay between retry attempts (can be set precisely, e.g., in seconds or minutes).

**Example Task Configuration:**

```python
fetch_data_task = PythonOperator(
    task_id='Data_enrichment',
    python_callable=fetch_student_data,
    provide_context=True,
    retries=2,  # ✅ Retry up to 2 times
    retry_delay=timedelta(seconds=2),  # Retry after waiting 2 seconds
    dag=dag,
)
```

In this example:

- The task `Data_enrichment` will retry **up to two times** if an initial failure occurs.
- After a failure, the system will **wait exactly 2 seconds** before attempting a retry.

---

### 📋 **Traceability and Monitoring Retry Events**

Airflow provides clear traceability of retry activities through its built-in monitoring interface. Users can easily review retry attempts, including timing and reasons for failures, using the **Event Log**:

- Navigate to the Airflow Web UI.
- Select your DAG and the specific task instance.
- Open the **"Event Log"** tab to view detailed retry records.

In the **Event Log**, Airflow explicitly logs information such as:

- When a task retry occurs.
- How many retry attempts have been executed.
- Error messages that triggered the retries.
- Timestamps of each retry event.

![image](https://github.com/user-attachments/assets/35d3d889-479e-4bf6-8f55-a3f69c0ad835)


This detailed logging facilitates debugging, transparency, and improved task reliability, enabling developers and operations teams to quickly identify and rectify underlying issues causing task failures.

---

Here's a refined and detailed section for your research document regarding the rerun-ability of tasks in Airflow:

---


### ✅ **Rerunning Failed Tasks**

When a task fails, Airflow visually marks it clearly in red within the DAG's Graph View. The downstream tasks impacted by the failed task are labeled as `upstream_failed`, making it straightforward to identify the point of failure and affected tasks.

**Procedure to Rerun a Failed Task:**

1. Navigate to the Airflow Web UI.
2. Select the DAG that contains the failed task.
3. Go to the **Graph View**.
4. Identify the failed task (highlighted in red).
5. Click on the failed task and select **"Clear task"**.

By clicking **"Clear task"**, Airflow resets the state of only that particular task (and optionally downstream tasks if selected), causing it to rerun without triggering the successful upstream tasks again.
![image](https://github.com/user-attachments/assets/2c8a1f08-6021-4ac5-9613-78c80161aceb)


---

Here's a refined section on **Logging and XCom functionality in Airflow**, based on your provided details and screenshot:

---

### 📌 **Task-Level Logging**

Each task executed by Airflow generates detailed logs. You can access these logs directly via the Airflow Web UI, greatly simplifying the process of debugging.


Airflow logs provide:

- Detailed timestamps for each log entry.
- Standard output and error outputs (`stdout` and `stderr`).
- Clear error messages and stack traces for failed tasks.
![image](https://github.com/user-attachments/assets/47269c08-e1a7-4846-bab7-03c6fb5b1f5b)


---

### 🔗 **Tracing Output with XCom**

Airflow's XCom (Cross-communication) feature allows tasks to exchange small amounts of data. It is useful for passing intermediate results or statuses from one task to subsequent tasks.


Through XCom, you can:

- View and debug data passed between tasks.
- Understand task dependencies based on actual runtime data.
- Easily verify the correctness of intermediate outputs in the pipeline.
![image](https://github.com/user-attachments/assets/1b265d12-975d-407f-ae05-320a5be887ba)


---

## 🗓 **Scheduling in Airflow**

Airflow has a powerful built-in scheduling engine, enabling precise and flexible execution of tasks:

### ✅ **Key Features**

- **Cron-based Scheduling**:  
  Schedule DAGs using standard cron expressions (`0 0 * * *`) or presets (`@daily`, `@weekly`, `@hourly`, etc.).

- **Task Dependencies**:  
  Clearly define task dependencies to ensure correct execution order:
  ```python
  task_a >> task_b >> task_c
  ```

- **Flexible Scheduling Options:**
  - Time-based intervals (`@daily`, `@hourly`)
  - Custom cron schedules (`0 6 * * *` to run daily at 6 AM)
  - Event-triggered schedules using sensors (e.g., file arrival, external events)

- **Backfill & Catch-up:**  
  Automatically run past instances using `catchup=True`.

- **Manual Triggering:**  
  You can manually trigger DAG runs from Airflow UI or CLI, making ad-hoc execution easy for troubleshooting or ad-hoc runs.

![image](https://github.com/user-attachments/assets/13188689-266c-45af-81e8-57d061d1694a)


