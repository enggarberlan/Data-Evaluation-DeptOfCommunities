# Community Program Data & Evaluation Analysis

A portfolio project demonstrating data analysis, evaluation, SQL, Python, and reporting skills using a simulated community services dataset.

The project was designed to reflect the types of analytical tasks involved in monitoring and evaluating community programs, including data cleaning, database design, SQL analysis, performance measurement, and data visualisation.

## Project Objectives

The analysis aims to:

- assess participation and program completion
- measure changes in participant outcomes
- analyse participant satisfaction
- identify patterns across programs and regions
- summarise participant feedback
- demonstrate how data can support program monitoring and evaluation

## Tools & Technologies

- **Python**
  - pandas
  - matplotlib
  - sqlite3
- **SQL**
- **SQLite**
- **Microsoft Excel / CSV**
- **Visual Studio Code**
- **Git & GitHub**

## Project Structure

```text
├── data/
│   ├── community_program.csv
│   └── community_program_clean.csv
│
├── sql/
│   ├── create_tables.sql
│   └── analysis.sql
│
├── output/
│   ├── average_outcome_improvement.png
│   ├── average_satisfaction.png
│   ├── feedback_summary.png
│   └── program_completion_rate.png
│
├── main.py
└── README.md
```

## Analysis Workflow

### 1. Data Cleaning

Python is used to prepare the dataset for analysis, including checking data quality, handling missing or inconsistent values, and creating a clean dataset.

### 2. Database Creation

The cleaned data is loaded into a relational SQLite database.

SQL tables are created to organise participant and program information and support structured analysis.

### 3. SQL Analysis

SQL queries are used to investigate key program measures, including:

- participants by program
- program completion rates
- participant satisfaction
- changes in participant outcomes
- feedback categories
- differences across programs and regions

### 4. Evaluation

The analysis examines whether participants experienced improvements following program participation and identifies differences in outcomes and satisfaction across programs.

### 5. Data Visualisation

Python and Matplotlib are used to produce visual summaries of key findings, including:

- average outcome improvement (output/average_outcome_improvement.png)
- average satisfaction (output/average_satisfaction.png)
- program completion rates (output/feedback_summary.png)
- participant feedback (output/program_completion_rate.png)

## Skills Demonstrated

This project demonstrates practical experience in:

- quantitative data analysis
- data cleaning and validation
- SQL querying
- relational database design
- program monitoring and evaluation
- performance indicator analysis
- data visualisation
- analytical problem solving
- communicating findings through clear outputs
- reproducible analysis workflows

## Context

This is an independent portfolio project using simulated data. It is not affiliated with, commissioned by, or based on confidential data from the Western Australian Department of Communities.

The project was developed to demonstrate transferable data and evaluation skills relevant to public-sector and community-service environments.