"""
Module 1 - Dashboard
Displays overall grievance summary: Total Received, Total Disposed,
Total Pending and Overall Disposal Rate.

Disposal Rate = (Total Disposed / Total Received) x 100
"""

COL_RECEIVED = "Total Receipts (01.01.2016 to 01.11.2019)"
COL_DISPOSED = "Total Disposal (01.01.2016 to 01.11.2019)"
COL_PENDING = "Total Pending as on 01.11.2019"


def get_dashboard_summary(df):
    """Return a dict with total received, disposed, pending and disposal rate."""
    total_received = int(df[COL_RECEIVED].sum())
    total_disposed = int(df[COL_DISPOSED].sum())
    total_pending = int(df[COL_PENDING].sum())
    disposal_rate = ((total_disposed / total_received) * 100) if total_received > 0 else 0.0

    return {
        "Total Received": total_received,
        "Total Disposed": total_disposed,
        "Total Pending": total_pending,
        "Disposal Rate": round(disposal_rate, 2),
    }


def print_dashboard(df):
    """Print the dashboard exactly like Figure 3 / Figure 1 (Final System Dashboard)."""
    summary = get_dashboard_summary(df)

    print("\n" + "=" * 70)
    print("          PUBLIC GRIEVANCE RESOLUTION ANALYSIS SYSTEM")
    print("                   Overall Grievance Dashboard")
    print("=" * 70)
    print(f"  Total Received   : {summary['Total Received']:,}")
    print(f"  Total Disposed   : {summary['Total Disposed']:,}")
    print(f"  Total Pending    : {summary['Total Pending']:,}")
    print(f"  Disposal Rate    : {summary['Disposal Rate']}%")
    print("=" * 70 + "\n")

    return summary
