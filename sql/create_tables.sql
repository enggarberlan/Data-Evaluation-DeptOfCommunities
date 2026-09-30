CREATE TABLE IF NOT EXISTS programs (
    program_id INTEGER PRIMARY KEY,
    program_name TEXT NOT NULL UNIQUE
);


CREATE TABLE IF NOT EXISTS participants (
    participant_id INTEGER PRIMARY KEY,
    program_id INTEGER NOT NULL,
    region TEXT NOT NULL,
    age_group TEXT NOT NULL,
    sessions_attended INTEGER NOT NULL,
    program_completed TEXT NOT NULL,
    satisfaction_score INTEGER,
    outcome_before INTEGER,
    outcome_after INTEGER,
    outcome_change INTEGER,
    feedback_category TEXT,
    reporting_date TEXT NOT NULL,

    FOREIGN KEY (program_id)
        REFERENCES programs(program_id)
);


CREATE TABLE IF NOT EXISTS program_financials (
    financial_id INTEGER PRIMARY KEY,
    program_id INTEGER NOT NULL,
    reporting_year INTEGER NOT NULL,
    reporting_quarter INTEGER NOT NULL,
    program_budget REAL NOT NULL,
    actual_expenditure REAL NOT NULL,
    budget_variance REAL NOT NULL,

    FOREIGN KEY (program_id)
        REFERENCES programs(program_id)
);