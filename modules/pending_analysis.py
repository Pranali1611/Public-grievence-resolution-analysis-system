"""
Module 3 - Pending Grievance Analysis
Analyzes grievances that are still pending, across departments/states
and across pending-duration categories.
"""

import matplotlib.pyplot as plt

COL_NAME = "Ministry/Department/State"
COL_PENDING = "Total Pending as on 01.11.2019"
COL_P_1Y = "Pending More Than 1 Year"
COL_P_6_12M = "Pending Between 6 To 12 Months"
COL_P_2_6M = "Pending Between 2 To 6 Months"
COL_P_L2M = "Pending Less Than 2 Months"

DURATION_COLS = [COL_P_1Y, COL_P_6_12M, COL_P_2_6M, COL_P_L2M]
DURATION_LABELS = ["More Than 1 Year", "6 To 12 Months", "2 To 6 Months", "Less Than 2 Months"]


def get_pending_analysis(df):
    """Same as pending_analysis.head(10) in Figure 6 of the report."""
    pending_analysis = df[[COL_NAME, COL_PENDING] + DURATION_COLS]
    return pending_analysis


def plot_pending_by_department(df, output_path="outputs/pending_by_department.png", top_n=10):
    """Figure 7 (Activity 2) / Figure 4 (Activity 3): Top 10 Departments with Pending Grievances."""
    top = df.sort_values(by=COL_PENDING, ascending=False).head(top_n)

    plt.figure(figsize=(10, 6))
    plt.bar(top[COL_NAME], top[COL_PENDING], color="tab:blue")
    plt.title("Top 10 Departments with Pending Grievances")
    plt.xlabel("Ministry / Department / State")
    plt.ylabel("Number of Pending Grievances")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def plot_pending_by_duration(df, output_path="outputs/pending_by_duration.png"):
    """Figure 8 (Activity 2) / Figure 5 (Activity 3): Pending Grievances by Duration."""
    totals = [df[col].sum() for col in DURATION_COLS]

    plt.figure(figsize=(8, 6))
    plt.bar(DURATION_LABELS, totals, color="tab:blue")
    plt.title("Pending Grievances by Duration")
    plt.xlabel("Pending Duration")
    plt.ylabel("Number of Grievances")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")
