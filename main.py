# ==========================================
# 1. IMPORT LIBRARIES
# ==========================================
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# ==========================================
# 2. LOAD AND PROFILE RAW DATA
# ==========================================
df = pd.read_csv("data/community_program.csv")

financial_df = pd.read_csv(
    "data/program_financials.csv"
)

print("=== DATASET OVERVIEW ===")
print(df.head())

print("\n=== DATASET INFORMATION ===")
df.info()

print("\n=== MISSING VALUES ===")
print(df.isnull().sum())

print("\n=== DUPLICATE ROWS ===")
print(df.duplicated().sum())

print("\n=== DESCRIPTIVE STATISTICS ===")
print(df.describe())

print("\n=== FINANCIAL DATASET OVERVIEW ===")
print(financial_df.head())

print("\n=== FINANCIAL DATASET INFORMATION ===")
financial_df.info()

print("\n=== FINANCIAL DATA MISSING VALUES ===")
print(financial_df.isnull().sum())

print("\n=== FINANCIAL DATA DUPLICATES ===")
print(financial_df.duplicated().sum())

# ==========================================
# 3. DATA CLEANING AND PREPARATION
# ==========================================
clean_df = df.copy()
clean_financial_df = financial_df.copy()

print("\n=== STARTING DATA CLEANING ===")

# Standardise categorical values
clean_df["program_type"] = (
    clean_df["program_type"].str.strip().str.title()
)

clean_df["region"] = (
    clean_df["region"].str.strip().str.title()
)

clean_df["age_group"] = (
    clean_df["age_group"].str.strip()
)

clean_df["program_completed"] = (
    clean_df["program_completed"].str.strip().str.title()
)

clean_df["feedback_category"] = (
    clean_df["feedback_category"].str.strip().str.title()
)

# Convert reporting date to datetime
clean_df["reporting_date"] = pd.to_datetime(
    clean_df["reporting_date"],
    errors="coerce"
)

# Validate satisfaction scores
invalid_satisfaction = ~clean_df["satisfaction_score"].between(1, 5)

print(
    "\nInvalid satisfaction scores:",
    invalid_satisfaction.sum()
)


# Validate outcome scores
invalid_outcomes = (
    ~clean_df["outcome_before"].between(0, 100)
    | ~clean_df["outcome_after"].between(0, 100)
)

print(
    "Invalid outcome scores:",
    invalid_outcomes.sum()
)


# Remove exact duplicate rows
before_duplicates = len(clean_df)

clean_df = clean_df.drop_duplicates()

after_duplicates = len(clean_df)

print("\nDuplicates removed:")
print(before_duplicates - after_duplicates)

# ==========================================
# CLEAN FINANCIAL DATA
# ==========================================

clean_financial_df["program_type"] = (
    clean_financial_df["program_type"]
    .str.strip()
    .str.title()
)

clean_financial_df = (
    clean_financial_df.drop_duplicates()
)

invalid_financial = (
    (clean_financial_df["program_budget"] < 0)
    | (clean_financial_df["actual_expenditure"] < 0)
)

print(
    "\nInvalid financial values:",
    invalid_financial.sum()
)

clean_financial_df["calculated_variance"] = (
    clean_financial_df["program_budget"]
    - clean_financial_df["actual_expenditure"]
)

variance_mismatch = (
    clean_financial_df["budget_variance"]
    != clean_financial_df["calculated_variance"]
)

print(
    "Budget variance mismatches:",
    variance_mismatch.sum()
)


# ==========================================
# 4. PROGRAM EVALUATION
# ==========================================

# Calculate change between before and after outcome scores
clean_df["outcome_change"] = (
    clean_df["outcome_after"]
    - clean_df["outcome_before"]
)

# Extract reporting year and quarter
clean_df["reporting_year"] = (
    clean_df["reporting_date"].dt.year
)

clean_df["reporting_quarter"] = (
    clean_df["reporting_date"].dt.quarter
)

print("\n=== OUTCOME CHANGES ===")
print(
    clean_df[
        [
            "participant_id",
            "program_type",
            "outcome_before",
            "outcome_after",
            "outcome_change"
        ]
    ]
)

print("\n=== CLEAN DATA SUMMARY ===")
print(clean_df)

print("\nMissing values after cleaning:")
print(clean_df.isnull().sum())

print("\nDuplicate rows after cleaning:")
print(clean_df.duplicated().sum())

clean_df.to_csv(
    "data/community_program_clean.csv",
    index=False
)

clean_financial_df.to_csv(
    "data/program_financials_clean.csv",
    index=False
)

print(
    "Clean financial dataset saved to "
    "data/program_financials_clean.csv"
)

print(
    "\nClean dataset saved to "
    "data/community_program_clean.csv"
)

# ==========================================
# 5. PREPARE RELATIONAL DATA
# ==========================================
print("\n=== PREPARING RELATIONAL DATA ===")

# Create a separate programs table
programs_df = (
    clean_df[["program_type"]]
    .drop_duplicates()
    .sort_values("program_type")
    .reset_index(drop=True)
)

programs_df["program_id"] = programs_df.index + 1

programs_df = programs_df.rename(
    columns={"program_type": "program_name"}
)

print("\n=== PROGRAMS TABLE ===")
print(programs_df)


# Add program_id to participant records
participants_db_df = clean_df.merge(
    programs_df,
    left_on="program_type",
    right_on="program_name"
)

print("\n=== PARTICIPANTS WITH PROGRAM ID ===")
print(
    participants_db_df[
        [
            "participant_id",
            "program_type",
            "program_id"
        ]
    ]
)

# Add program_id to financial records
financial_db_df = clean_financial_df.merge(
    programs_df,
    left_on="program_type",
    right_on="program_name"
)

print("\n=== FINANCIAL DATA WITH PROGRAM ID ===")
print(
    financial_db_df[
        [
            "program_type",
            "program_id",
            "reporting_year",
            "reporting_quarter",
            "program_budget",
            "actual_expenditure",
            "budget_variance"
        ]
    ]
)


# ==========================================
# 6. CREATE AND POPULATE SQLITE DATABASE
# ==========================================
print("\n=== CREATING DATABASE ===")

conn = sqlite3.connect(
    "database/community_program.db"
)

# Enable foreign key enforcement
conn.execute("PRAGMA foreign_keys = ON")

with open(
    "sql/create_tables.sql",
    "r"
) as sql_file:
    sql_script = sql_file.read()

conn.executescript(sql_script)

print("Database tables created successfully.")


# Select columns required by participants table
participants_db_df = participants_db_df[
    [
        "participant_id",
        "program_id",
        "region",
        "age_group",
        "sessions_attended",
        "program_completed",
        "satisfaction_score",
        "outcome_before",
        "outcome_after",
        "outcome_change",
        "feedback_category",
        "reporting_date"
    ]
].copy()

# Select columns required by program_financials table
financial_db_df = financial_db_df[
    [
        "program_id",
        "reporting_year",
        "reporting_quarter",
        "program_budget",
        "actual_expenditure",
        "budget_variance"
    ]
].copy()


# Create unique financial IDs
financial_db_df.insert(
    0,
    "financial_id",
    range(1, len(financial_db_df) + 1)
)


# Clear old data so the script can be run again
conn.execute("DELETE FROM program_financials")
conn.execute("DELETE FROM participants")
conn.execute("DELETE FROM programs")

# Insert program data
programs_df.to_sql(
    "programs",
    conn,
    if_exists="append",
    index=False
)


# Insert participant data
participants_db_df.to_sql(
    "participants",
    conn,
    if_exists="append",
    index=False
)

# Insert financial data
financial_db_df.to_sql(
    "program_financials",
    conn,
    if_exists="append",
    index=False
)

conn.commit()

print("\nData inserted into database successfully.")

# ==========================================
# 7. VERIFY DATABASE
# ==========================================
print("\n=== DATABASE VERIFICATION ===")

query = """
SELECT
    p.participant_id,
    pr.program_name,
    p.region,
    p.age_group,
    p.sessions_attended,
    p.program_completed,
    p.satisfaction_score,
    p.outcome_before,
    p.outcome_after,
    p.outcome_change,
    p.feedback_category
FROM participants AS p
JOIN programs AS pr
    ON p.program_id = pr.program_id
ORDER BY p.participant_id;
"""

result = pd.read_sql_query(query, conn)

print(result)

# ==========================================
# 8. SQL DATA ANALYSIS
# ==========================================
print("\n=== SQL DATA ANALYSIS ===")


# 1. Participants by program
query_participants = """
SELECT
    pr.program_name,
    COUNT(p.participant_id) AS total_participants
FROM participants AS p
JOIN programs AS pr
    ON p.program_id = pr.program_id
GROUP BY pr.program_name
ORDER BY total_participants DESC;
"""

participants_by_program = pd.read_sql_query(
    query_participants,
    conn
)

print("\nParticipants by program:")
print(participants_by_program)


# 2. Average outcome improvement by program
query_outcome = """
SELECT
    pr.program_name,
    ROUND(AVG(p.outcome_change), 2) AS average_outcome_change
FROM participants AS p
JOIN programs AS pr
    ON p.program_id = pr.program_id
GROUP BY pr.program_name
ORDER BY average_outcome_change DESC;
"""

outcome_by_program = pd.read_sql_query(
    query_outcome,
    conn
)

print("\nAverage outcome improvement by program:")
print(outcome_by_program)


# 3. Program completion rate
query_completion = """
SELECT
    pr.program_name,
    COUNT(p.participant_id) AS total_participants,
    SUM(
        CASE
            WHEN p.program_completed = 'Yes' THEN 1
            ELSE 0
        END
    ) AS completed_participants,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN p.program_completed = 'Yes' THEN 1
                ELSE 0
            END
        ) / COUNT(p.participant_id),
        2
    ) AS completion_rate
FROM participants AS p
JOIN programs AS pr
    ON p.program_id = pr.program_id
GROUP BY pr.program_name
ORDER BY completion_rate DESC;
"""

completion_by_program = pd.read_sql_query(
    query_completion,
    conn
)

print("\nCompletion rate by program:")
print(completion_by_program)


# 4. Average satisfaction by program
query_satisfaction = """
SELECT
    pr.program_name,
    ROUND(
        AVG(p.satisfaction_score),
        2
    ) AS average_satisfaction
FROM participants AS p
JOIN programs AS pr
    ON p.program_id = pr.program_id
GROUP BY pr.program_name
ORDER BY average_satisfaction DESC;
"""

satisfaction_by_program = pd.read_sql_query(
    query_satisfaction,
    conn
)

print("\nAverage satisfaction by program:")
print(satisfaction_by_program)


# 5. Feedback categories
query_feedback = """
SELECT
    feedback_category,
    COUNT(*) AS total_feedback
FROM participants
GROUP BY feedback_category
ORDER BY total_feedback DESC;
"""

feedback_summary = pd.read_sql_query(
    query_feedback,
    conn
)

print("\nFeedback summary:")
print(feedback_summary)

# ==========================================
# FINANCIAL PERFORMANCE ANALYSIS
# ==========================================

query_financial = """
SELECT
    pr.program_name,
    SUM(pf.program_budget) AS total_budget,
    SUM(pf.actual_expenditure) AS total_expenditure,
    SUM(pf.budget_variance) AS total_variance
FROM program_financials AS pf
JOIN programs AS pr
    ON pf.program_id = pr.program_id
GROUP BY pr.program_name
ORDER BY total_variance DESC;
"""

financial_by_program = pd.read_sql_query(
    query_financial,
    conn
)

print("\nFinancial performance by program:")
print(financial_by_program)

query_quarterly_financial = """
SELECT
    pr.program_name,
    pf.reporting_year,
    pf.reporting_quarter,
    pf.program_budget,
    pf.actual_expenditure,
    pf.budget_variance
FROM program_financials AS pf
JOIN programs AS pr
    ON pf.program_id = pr.program_id
ORDER BY
    pr.program_name,
    pf.reporting_year,
    pf.reporting_quarter;
"""

quarterly_financial = pd.read_sql_query(
    query_quarterly_financial,
    conn
)

print("\nQuarterly financial performance:")
print(quarterly_financial)

query_quarterly_performance = """
SELECT
    pr.program_name,
    CAST(strftime('%Y', p.reporting_date) AS INTEGER)
        AS reporting_year,
    ((CAST(strftime('%m', p.reporting_date) AS INTEGER) - 1) / 3) + 1
        AS reporting_quarter,
    COUNT(p.participant_id) AS total_participants,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN p.program_completed = 'Yes' THEN 1
                ELSE 0
            END
        ) / COUNT(p.participant_id),
        2
    ) AS completion_rate,
    ROUND(
        AVG(p.satisfaction_score),
        2
    ) AS average_satisfaction,
    ROUND(
        AVG(p.outcome_change),
        2
    ) AS average_outcome_change
FROM participants AS p
JOIN programs AS pr
    ON p.program_id = pr.program_id
GROUP BY
    pr.program_name,
    reporting_year,
    reporting_quarter
ORDER BY
    pr.program_name,
    reporting_year,
    reporting_quarter;
"""

quarterly_performance = pd.read_sql_query(
    query_quarterly_performance,
    conn
)

print("\nQuarterly program performance:")
print(quarterly_performance)

# ==========================================
# INTEGRATED MANAGEMENT REPORTING
# ==========================================

query_management_report = """
WITH performance AS (
    SELECT
        p.program_id,
        CAST(
            strftime('%Y', p.reporting_date)
            AS INTEGER
        ) AS reporting_year,
        (
            (
                CAST(
                    strftime('%m', p.reporting_date)
                    AS INTEGER
                ) - 1
            ) / 3
        ) + 1 AS reporting_quarter,

        COUNT(p.participant_id)
            AS total_participants,

        ROUND(
            100.0 * SUM(
                CASE
                    WHEN p.program_completed = 'Yes'
                    THEN 1
                    ELSE 0
                END
            ) / COUNT(p.participant_id),
            2
        ) AS completion_rate,

        ROUND(
            AVG(p.satisfaction_score),
            2
        ) AS average_satisfaction,

        ROUND(
            AVG(p.outcome_change),
            2
        ) AS average_outcome_change

    FROM participants AS p

    GROUP BY
        p.program_id,
        reporting_year,
        reporting_quarter
)

SELECT
    pr.program_name,
    pf.reporting_year,
    pf.reporting_quarter,

    perf.total_participants,
    perf.completion_rate,
    perf.average_satisfaction,
    perf.average_outcome_change,

    pf.program_budget,
    pf.actual_expenditure,
    pf.budget_variance

FROM program_financials AS pf

JOIN programs AS pr
    ON pf.program_id = pr.program_id

LEFT JOIN performance AS perf
    ON pf.program_id = perf.program_id
    AND pf.reporting_year = perf.reporting_year
    AND pf.reporting_quarter = perf.reporting_quarter

ORDER BY
    pr.program_name,
    pf.reporting_year,
    pf.reporting_quarter;
"""

management_report = pd.read_sql_query(
    query_management_report,
    conn
)

print("\n=== INTEGRATED MANAGEMENT REPORT ===")
print(management_report)

print(
    "\nManagement report missing values:"
)

print(
    management_report.isnull().sum()
)

management_report.to_csv(
    "output/management_report.csv",
    index=False
)

print(
    "\nCreated: output/management_report.csv"
)

# ==========================================
# 9. DATA VISUALISATION
# ==========================================
print("\n=== CREATING VISUALISATIONS ===")


# Chart 1: Average outcome improvement by program
plt.figure(figsize=(8, 5))

plt.bar(
    outcome_by_program["program_name"],
    outcome_by_program["average_outcome_change"]
)

plt.title("Average Outcome Improvement by Program")
plt.xlabel("Program")
plt.ylabel("Average Outcome Change")

plt.xticks(rotation=20)
plt.tight_layout()

plt.savefig(
    "output/average_outcome_improvement.png"
)

plt.close()

print("Created: output/average_outcome_improvement.png")


# Chart 2: Completion rate by program
plt.figure(figsize=(8, 5))

plt.bar(
    completion_by_program["program_name"],
    completion_by_program["completion_rate"]
)

plt.title("Program Completion Rate")
plt.xlabel("Program")
plt.ylabel("Completion Rate (%)")

plt.xticks(rotation=20)
plt.tight_layout()

plt.savefig(
    "output/program_completion_rate.png"
)

plt.close()

print("Created: output/program_completion_rate.png")


# Chart 3: Average satisfaction by program
plt.figure(figsize=(8, 5))

plt.bar(
    satisfaction_by_program["program_name"],
    satisfaction_by_program["average_satisfaction"]
)

plt.title("Average Satisfaction by Program")
plt.xlabel("Program")
plt.ylabel("Average Satisfaction Score")

plt.xticks(rotation=20)
plt.tight_layout()

plt.savefig(
    "output/average_satisfaction.png"
)

plt.close()

print("Created: output/average_satisfaction.png")


# Chart 4: Feedback categories
plt.figure(figsize=(8, 5))

plt.bar(
    feedback_summary["feedback_category"],
    feedback_summary["total_feedback"]
)

plt.title("Participant Feedback Summary")
plt.xlabel("Feedback Category")
plt.ylabel("Number of Participants")

plt.tight_layout()

plt.savefig(
    "output/feedback_summary.png"
)

plt.close()

print("Created: output/feedback_summary.png")


# ==========================================
# 10. CLOSE DATABASE CONNECTION
# ==========================================
conn.close()

print("\nAnalysis completed successfully.")