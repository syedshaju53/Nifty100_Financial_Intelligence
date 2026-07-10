import pandas as pd


def validate_dataframe(df):

    issues = []

    # ---------------- DQ-01 ----------------
    if df.empty:
        issues.append({
            "Rule": "DQ-01",
            "Issue": "Dataset is empty",
            "Severity": "CRITICAL"
        })

    # ---------------- DQ-02 ----------------
    if df.duplicated().sum() > 0:
        issues.append({
            "Rule": "DQ-02",
            "Issue": f"{df.duplicated().sum()} duplicate rows",
            "Severity": "WARNING"
        })

    # ---------------- DQ-03 ----------------
    if df.isnull().sum().sum() > 0:
        issues.append({
            "Rule": "DQ-03",
            "Issue": f"{df.isnull().sum().sum()} missing values",
            "Severity": "WARNING"
        })

    # ---------------- DQ-04 ----------------
    if "id" in df.columns:
        if df["id"].duplicated().sum() > 0:
            issues.append({
                "Rule": "DQ-04",
                "Issue": "Duplicate IDs found",
                "Severity": "CRITICAL"
            })

    # ---------------- DQ-05 ----------------
    if "id" in df.columns:
        if df["id"].isnull().sum() > 0:
            issues.append({
                "Rule": "DQ-05",
                "Issue": "Null IDs found",
                "Severity": "CRITICAL"
            })

    # ---------------- DQ-06 ----------------
    if "company_name" in df.columns:
        if df["company_name"].isnull().sum() > 0:
            issues.append({
                "Rule": "DQ-06",
                "Issue": "Company name missing",
                "Severity": "WARNING"
            })

    # ---------------- DQ-07 ----------------
    if "website" in df.columns:
        if df["website"].duplicated().sum() > 0:
            issues.append({
                "Rule": "DQ-07",
                "Issue": "Duplicate website URLs",
                "Severity": "INFO"
            })

    # ---------------- DQ-08 ----------------
    numeric_columns = ["face_value", "book_value", "roce_percentage", "roe_percentage"]

    for col in numeric_columns:
        if col in df.columns:
            if (df[col] < 0).any():
                issues.append({
                    "Rule": "DQ-08",
                    "Issue": f"{col} contains negative values",
                    "Severity": "WARNING"
                })

    # ---------------- DQ-09 ----------------
    for col in df.columns:
        if df[col].dtype == object:
            issues.append({
                "Rule": "DQ-09",
                "Issue": f"{col} is object datatype",
                "Severity": "INFO"
            })

    # ---------------- DQ-10 ----------------
    if len(df.columns) < 5:
        issues.append({
            "Rule": "DQ-10",
            "Issue": "Too few columns",
            "Severity": "WARNING"
        })

    # ---------------- DQ-11 ----------------
    if len(df.columns) > 30:
        issues.append({
            "Rule": "DQ-11",
            "Issue": "Too many columns",
            "Severity": "INFO"
        })

    # ---------------- DQ-12 ----------------
    if df.shape[0] < 1:
        issues.append({
            "Rule": "DQ-12",
            "Issue": "No records found",
            "Severity": "CRITICAL"
        })

    # ---------------- DQ-13 ----------------
    if df.columns.duplicated().sum() > 0:
        issues.append({
            "Rule": "DQ-13",
            "Issue": "Duplicate column names",
            "Severity": "CRITICAL"
        })

    # ---------------- DQ-14 ----------------
    issues.append({
        "Rule": "DQ-14",
        "Issue": "Foreign key validation will run after SQLite loading",
        "Severity": "INFO"
    })

    # ---------------- DQ-15 ----------------
    if "company_logo" in df.columns:
        if df["company_logo"].isnull().sum() > 0:
            issues.append({
                "Rule": "DQ-15",
                "Issue": "Missing company logos",
                "Severity": "INFO"
            })

    # ---------------- DQ-16 ----------------
    required_columns = [
        "id",
        "company_name",
        "company_logo",
        "website"
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        issues.append({
            "Rule": "DQ-16",
            "Issue": f"Missing required columns: {missing}",
            "Severity": "CRITICAL"
        })

    return pd.DataFrame(issues)