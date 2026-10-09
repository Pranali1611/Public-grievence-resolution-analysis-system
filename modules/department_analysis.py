"""
Module 2 - Department-wise Analysis
Compares grievance statistics (Received, Disposed, Pending) across
different ministries, departments and states.
"""

import matplotlib.pyplot as plt

COL_NAME = "Ministry/Department/State"
COL_RECEIVED = "Total Receipts (01.01.2016 to 01.11.2019)"
COL_DISPOSED = "Total Disposal (01.01.2016 to 01.11.2019)"
COL_PENDING = "Total Pending as on 01.11.2019"


def get_department_analysis(df):
    """Return department_analysis dataframe sorted by Total Receipts (desc),
    same as department_analysis.head(10) shown in Figure 4 of the report."""
    department_analysis = df[[COL_NAME, COL_RECEIVED, COL_DISPOSED, COL_PENDING]].sort_values(
        by=COL_RECEIVED, ascending=False
    )
    return department_analysis


def plot_received_vs_disposed(df, output_path="outputs/received_vs_disposed.png", top_n=10):
    """Figure 5 (Activity 2) / Figure 3 (Activity 3): Top 10 Departments - Received vs Disposed."""
    top = df.sort_values(by=COL_RECEIVED, ascending=False).head(top_n)

    plt.figure(figsize=(10, 6))
    plt.bar(top[COL_NAME], top[COL_RECEIVED], color="tab:blue", label="Total Received")
    plt.bar(top[COL_NAME], top[COL_DISPOSED], color="tab:orange", label="Total Disposed")
    plt.title("Top 10 Departments: Received vs Disposed Grievances")
    plt.xlabel("Ministry / Department / State")
    plt.ylabel("Number of Grievances")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")
