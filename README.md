# Batch MapReduce Clickstream Log Analysis
**Course:** Big Data Analytics Lab  
**Domain:** Distributed Log Analytics & Web Intelligence  
**Paradigm:** MapReduce (Hadoop Streaming Standard)

---

## 1. Project Overview

In web applications and e-commerce platforms (e.g., Amazon, Netflix), server logs record every user click, navigation step, and HTTP status code. These access logs represent classic **Big Data** characterized by:
* **High Volume:** Millions of clickstream events generated daily.
* **Semi-Structured Variety:** Comma-separated or log-formatted text containing timestamps, user IDs, URLs, HTTP status codes, and latencies.
* **Batch Processing Need:** Daily or hourly batch processing using the **MapReduce paradigm** to compute traffic trends, system error rates, and user engagement metrics without overloading a relational database.

This project implements an end-to-end Big Data batch log processing pipeline utilizing standard **Mappers and Reducers** (reading from `stdin`, writing to `stdout`), automated key sorting (Shuffle/Sort), and an interactive analytics web dashboard.

---

## 2. Big Data Architecture & MapReduce Workflow

```
+-----------------------------------------------------------------------------------------+
|                                  MAPREDUCE PIPELINE                                     |
+-----------------------------------------------------------------------------------------+
       [ Raw Clickstream Logs: clickstream.csv (25,000+ Records) ]
                                   │
                                   ▼
                            [ Input Splits ]
                                   │
            ┌──────────────────────┼──────────────────────┐
            ▼                      ▼                      ▼
    [ mapper_pages.py ]    [ mapper_status.py ]    [ mapper_users.py ]
      Emits: (URL, 1)        Emits: (Status, 1)      Emits: (UserID, 1)
            │                      │                      │
            └──────────────────────┼──────────────────────┘
                                   ▼
                        [ Shuffle & Sort Phase ]
                 (Intermediate keys sorted & grouped)
                                   │
            ┌──────────────────────┼──────────────────────┐
            ▼                      ▼                      ▼
    [ reducer_pages.py ]   [ reducer_status.py ]   [ reducer_users.py ]
      Sums views per URL     Sums code counts        Sums user requests
            │                      │                      │
            └──────────────────────┼──────────────────────┘
                                   ▼
                   [ Output Files (output/*.txt) ]
          (output_pages.txt, output_status.txt, output_users.txt)
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
       [ Static Report Chart ]       [ Interactive Web Dashboard ]
         (summary_chart.png)             (streamlit run app.py)
+-----------------------------------------------------------------------------------------+
```

---

## 3. Directory Structure

```
bda project/
│
├── generate_logs.py        # Generates realistic batch clickstream logs (25,000 rows)
├── clickstream.csv         # Generated raw log dataset (~1.2 MB)
│
├── mapper_pages.py         # Job 1: Mapper for URL page visits
├── reducer_pages.py        # Job 1: Reducer for URL page visits
│
├── mapper_status.py        # Job 2: Mapper for HTTP status code distribution
├── reducer_status.py       # Job 2: Reducer for HTTP status code distribution
│
├── mapper_users.py         # Job 3: Mapper for User activity count
├── reducer_users.py        # Job 3: Reducer for User activity count
│
├── run_analysis.py         # One-click runner for all 3 jobs + generates summary chart
├── app.py                  # Interactive Streamlit Web Dashboard
├── summary_chart.png       # Generated visualization chart for the lab report
│
├── output/                 # MapReduce output directory
│   ├── output_pages.txt    # Results for Job 1 (URL \t Count)
│   ├── output_status.txt   # Results for Job 2 (Status_Code \t Count)
│   └── output_users.txt    # Results for Job 3 (User_ID \t Count)
│
└── README.md               # Lab project report and viva guide
```

---

## 4. How to Run the Project & Show Output to the Reviewer

### Option A: The One-Click Batch Pipeline (Terminal Execution)
Run the master runner to execute all three MapReduce jobs and generate the report chart:
```powershell
python run_analysis.py
```
**What happens:**
* Executes each Mapper $\rightarrow$ sorts intermediate keys $\rightarrow$ executes Reducer.
* Times each job (proving batch processing speed).
* Saves the output into `output/output_pages.txt`, `output_status.txt`, and `output_users.txt`.
* Generates `summary_chart.png`.

---

### Option B: The Pure Hadoop-Streaming Pipeline (Classic Viva Demo)
If your professor asks to see standard Unix/Hadoop piping in the terminal:

**1. Page Visit Analysis (Job 1):**
```powershell
Get-Content clickstream.csv | python mapper_pages.py | sort | python reducer_pages.py
```

**2. HTTP Status Code Analysis (Job 2):**
```powershell
Get-Content clickstream.csv | python mapper_status.py | sort | python reducer_status.py
```

**3. User Activity Analysis (Job 3):**
```powershell
Get-Content clickstream.csv | python mapper_users.py | sort | python reducer_users.py
```

---

### Option C: The Interactive Web Dashboard (Visual Presentation)
Launch the web interface in your browser:
```powershell
streamlit run app.py
```
* **Visual Cards:** Displays total log volume (25,000 records), system health %, and top pages.
* **Interactive Graphs:** Page popularity chart, HTTP Status donut chart (200 OK vs 404/500 errors), and top active users.
* **Raw Outputs Tab:** Allows the reviewer to inspect the raw `Key \t Value` files directly.
* **Re-run Button:** Easily re-executes the pipeline on demand from the sidebar.

---

## 5. Sample Output Results

### Job 1: Page Visit Count (`output/output_pages.txt`)
```tsv
/about                  2764
/cart                   2790
/checkout               2778
/contact                2837
/home                   2798
/login                  2818
/products               2673
/products/electronics   2857
/products/fashion       2685
```

### Job 2: HTTP Status Codes (`output/output_status.txt`)
```tsv
200     20555   (82.2% - Healthy Requests)
301     776     (3.1%  - Redirects)
404     2402    (9.6%  - Page Not Found Errors)
500     1267    (5.1%  - Internal Server Errors)
```

---

## 6. Lab Viva Q&A Guide (Be Ready for Examiner Questions)

### Q1: Why is this considered a Big Data project rather than an ordinary Python script?
> **Answer:** We are using the **MapReduce distributed computing paradigm**. Instead of loading the entire dataset into memory or using monolithic loops/SQL queries, data processing is split into stateless, independent **Mappers** and **Reducers**. This architecture conforms to standard **Hadoop Streaming**, allowing the exact same code to scale across a multi-node Hadoop cluster without modification.

### Q2: What is the purpose of the "Shuffle & Sort" phase?
> **Answer:** Mappers emit independent `(key, value)` pairs in arbitrary order. The **Shuffle and Sort** phase is the backbone of MapReduce: it groups all identical keys together and feeds them consecutively to the Reducer. This ensures the Reducer can aggregate counts in linear $O(N)$ time with minimal memory consumption.

### Q3: What is the format of the intermediate data between Mapper and Reducer?
> **Answer:** Intermediate data is formatted as **tab-separated key-value pairs (`Key \t Value`)** printed to standard output (`stdout`) and received by the Reducer via standard input (`stdin`).

### Q4: How do you identify website errors in this project?
> **Answer:** In Job 2, the Mapper extracts the HTTP response code (`parts[3]`). The Reducer aggregates counts for status codes `404` (client not found) and `500` (server failure), enabling site administrators to monitor site reliability and error spikes.
