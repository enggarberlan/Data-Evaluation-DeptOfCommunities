import pandas as pd
import random
from datetime import datetime, timedelta


# ==========================================
# CONFIGURATION
# ==========================================

random.seed(42)

number_of_records = 100

programs = [
    "Family Support",
    "Youth Support",
    "Community Support"
]

regions = [
    "Perth",
    "Fremantle",
    "Joondalup",
    "Rockingham"
]

age_groups = [
    "18-24",
    "25-34",
    "35-44",
    "45-54",
    "55+"
]

feedback_categories = [
    "Positive",
    "Neutral",
    "Negative"
]


# ==========================================
# GENERATE SYNTHETIC DATA
# ==========================================

records = []

start_date = datetime(2025, 1, 1)

for participant_id in range(1, number_of_records + 1):

    program_type = random.choice(programs)
    region = random.choice(regions)
    age_group = random.choice(age_groups)

    reporting_date = (
        start_date
        + timedelta(days=random.randint(0, 364))
    )

    sessions_attended = random.randint(1, 12)

    program_completed = random.choices(
        ["Yes", "No"],
        weights=[75, 25]
    )[0]

    satisfaction_score = random.randint(1, 5)

    outcome_before = random.randint(30, 70)

    improvement = random.randint(-5, 30)

    outcome_after = max(
        0,
        min(100, outcome_before + improvement)
    )

    feedback_category = random.choices(
        feedback_categories,
        weights=[65, 25, 10]
    )[0]

    records.append(
        {
            "participant_id": participant_id,
            "program_type": program_type,
            "region": region,
            "age_group": age_group,
            "reporting_date": reporting_date.strftime(
                "%Y-%m-%d"
            ),
            "sessions_attended": sessions_attended,
            "program_completed": program_completed,
            "satisfaction_score": satisfaction_score,
            "outcome_before": outcome_before,
            "outcome_after": outcome_after,
            "feedback_category": feedback_category,
        }
    )


# ==========================================
# CREATE DATAFRAME
# ==========================================

df = pd.DataFrame(records)


# ==========================================
# SAVE RAW PARTICIPANT DATA
# ==========================================

df.to_csv(
    "data/community_program.csv",
    index=False
)

print("Synthetic participant dataset created successfully.")
print()
print(df.head())
print()
print("Total participant records:", len(df))


# ==========================================
# GENERATE PROGRAM FINANCIAL DATA
# ==========================================

financial_records = []

for program in programs:

    for quarter in range(1, 5):

        program_budget = random.randint(
            80000,
            150000
        )

        # Actual expenditure varies around budget
        expenditure_variation = random.randint(
            -20000,
            20000
        )

        actual_expenditure = (
            program_budget + expenditure_variation
        )

        budget_variance = (
            program_budget - actual_expenditure
        )

        financial_records.append(
            {
                "program_type": program,
                "reporting_year": 2025,
                "reporting_quarter": quarter,
                "program_budget": program_budget,
                "actual_expenditure": actual_expenditure,
                "budget_variance": budget_variance
            }
        )


financial_df = pd.DataFrame(
    financial_records
)


# ==========================================
# SAVE FINANCIAL DATA
# ==========================================

financial_df.to_csv(
    "data/program_financials.csv",
    index=False
)

print()
print("Program financial dataset created successfully.")
print()
print(financial_df)
print()
print(
    "Total financial records:",
    len(financial_df)
)