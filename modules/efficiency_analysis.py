"""
Module 4 - Efficiency and Insights
Analyzes grievance disposal performance using the Disposal Rate.

Formula: Disposal Rate = (Total Disposed / Total Received) x 100
"""

import matplotlib.pyplot as plt

COL_NAME = "Ministry/Department/State"
COL_RECEIVED = "Total Receipts (01.01.2016 to 01.11.2019)"
COL_DISPOSED = "Total Disposal (01.01.2016 to 01.11.2019)"
COL_RATE = "Disposal Rate (%)"


def get_efficiency_table(df):
    """Same as the Efficiency Table shown in Figure 9 of the report."""
    efficiency_table = df[[COL_NAME, COL_RECEIVED, COL_DISPOSED]].copy()
    efficiency_table[COL_RATE] = (
        (efficiency_table[COL_DISPOSED] / efficiency_table[COL_RECEIVED].replace(0, float("nan"))) * 100
    ).fillna(0.0)
    return efficiency_table


def plot_disposal_rate(efficiency_table, output_path="outputs/disposal_rate.png", top_n=10):
    """Figure 10 (Activity 2) / Figure 6 (Activity 3): Top 10 Departments by Disposal Rate."""
    top = efficiency_table.sort_values(by=COL_RATE, ascending=False).head(top_n)

    plt.figure(figsize=(10, 6))
    plt.bar(top[COL_NAME], top[COL_RATE], color="tab:blue")
    plt.title("Top 10 Departments by Disposal Rate")
    plt.xlabel("Ministry / Department / State")
    plt.ylabel("Disposal Rate (%)")
    plt.ylim(0, 110)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def print_insights(summary):
    """Grievance Management Insights (page 14 of Activity 2 report)."""
    print("\nGRIEVANCE MANAGEMENT INSIGHTS")
    print("-" * 70)
    print("- The system provides an overall view of grievance receipt, disposal and pending status.")
    print("- Department-wise analysis helps compare grievance handling across departments.")
    print("- Pending analysis shows the number of unresolved grievances.")
    print("- Pending duration analysis shows how long grievances remain unresolved.")
    print("- Disposal rate analysis helps compare grievance disposal performance.")
    print("- The analysis supports data-based grievance monitoring and management.")
    print("-" * 70 + "\n")
