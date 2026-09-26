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

# ==========================================
# 3. DATA CLEANING AND PREPARATION
# ==========================================
clean_df = df.copy()

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

# Remove exact duplicate rows
before_duplicates = len(clean_df)

clean_df = clean_df.drop_duplicates()

after_duplicates = len(clean_df)

print("\nDuplicates removed:")
print(before_duplicates - after_duplicates)


# ==========================================
# 4. PROGRAM EVALUATION
# ==========================================

# Calculate change between before and after outcome scores
clean_df["outcome_change"] = (
    clean_df["outcome_after"]
    - clean_df["outcome_before"]
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
        "feedback_category"
    ]
].copy()


# Clear old data so the script can be run again
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