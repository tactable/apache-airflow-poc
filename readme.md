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

| Feature                                      | Airflow Support | Workaround |
|----------------------------------------------|-----------------|------------|
| **BAS can configure the mapping easily from the UI**  | ❌ No built-in UI configuration; requires DAG updates | Use **environment variables** or **external config files** for dynamic mapping? |
| **BAS can run the pipeline easily from the UI**  | ✅ Yes, DAGs can be triggered manually from the UI | N/A |
| **The tool has a good logging solution**      | ✅ Yes, logs are available per task in the UI | N/A
| **The tool can access the data enrichment service easily (refData)** | ✅ Yes, supports calling external JARs and APIs | N/A |
| **The tool can perform streaming efficiently** | ❌ No, Airflow is designed for batch processing, not real-time streaming | Use **Apache Kafka + Spark Streaming** for real-time processing? |
