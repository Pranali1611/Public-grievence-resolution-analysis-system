# Public Grievance Resolution Analysis System

Micro Project — Python for Data Science (BE05000231), BE Semester V
Group No. 28 — GTU, Apollo Institute of Engineering and Technology

This project matches the 3 report activities exactly:
1. Collection of Datasets
2. Analyze the Data and Create Pages (Modules)
3. Representation of Final Work

## Folder structure
```
Public_Grievance_Analysis/
├── data/
│   └── Dept_stat_receipt_disposal_010112019.csv   <- dataset used in the report
├── modules/
│   ├── dashboard.py              <- Module 1: Dashboard
│   ├── department_analysis.py    <- Module 2: Department-wise Analysis
│   ├── pending_analysis.py       <- Module 3: Pending Grievance Analysis
│   └── efficiency_analysis.py    <- Module 4: Efficiency & Insights
├── outputs/                      <- generated graphs (png) will be saved here
├── main.py                       <- run this file
├── requirements.txt
└── README.md
```

## How to run in VS Code

1. Open this folder in VS Code (`File > Open Folder`).
2. Open a terminal in VS Code (`Ctrl + ~`).
3. (Recommended) Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate      (Windows)
   source venv/bin/activate   (Mac/Linux)
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the project:
   ```
   python main.py
   ```

## Interactive local dashboard

Install the requirements, then start the Streamlit website from this folder:
```
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
Open the URL printed in the terminal (by default, `http://localhost:8501`).

## Output

Running `main.py` reproduces, in order, everything shown in the reports:
- Dataset loading & preview (Figure 1 / Activity 2)
- Data exploration / df.info() (Figure 2 / Activity 2)
- **Dashboard**: Total Received 4,779,587 | Total Disposed 3,798,755 |
  Total Pending 980,832 | Disposal Rate 79.48%
- Department-wise analysis table (Figure 4)
- `outputs/received_vs_disposed.png` — Top 10 Departments: Received vs Disposed (Figure 5 / Figure 3)
- Pending grievance table (Figure 6)
- `outputs/pending_by_department.png` — Top 10 Departments with Pending Grievances (Figure 7 / Figure 4)
- `outputs/pending_by_duration.png` — Pending Grievances by Duration (Figure 8 / Figure 5)
- Efficiency table (Figure 9)
- `outputs/disposal_rate.png` — Top 10 Departments by Disposal Rate (Figure 10 / Figure 6)
- Grievance Management Insights
- Final Testing table (all Pass)

All numbers and graphs match the report exactly — no report changes needed.
