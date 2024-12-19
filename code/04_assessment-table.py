# The code will output one data file: assessment_data.csv

import pandas as pd
import numpy as np

# Data sheets
assessment = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Transcript Assessments')

# Rename 'StudentNumber' to 'student_number'
assessment = assessment.rename(columns={'StudentNumber': 'student_number'})

# Import student_table and high_school_student (for now)
student_table = pd.read_csv('data/student_table.csv')
high_school_students = pd.read_csv('data/high_school_students.csv')

####################################################################
# Only one file will be exported, so df will represent the exploratory and modeling data.
# If we decided to filter at the end, all we need to do is change high_school_students to student_table 
# when creating the df below. The next line is the only line that needs to be adjusted.
####################################################################

# Create the df from the high_school_student student_numbers
df = high_school_students[['student_number']].copy()

######################################################################################################################################################
# Add the transcript assessment data to the df
# We want to start with student_numbers that are included in the df
assessment_table = df[['student_number']].copy()

# Merge the assessment table with the df to return student_numbers from the df
assessment_table = pd.merge(assessment_table, assessment, on='student_number', how='left')

# Drop LEANumber from the assessment_table. All values are the same making it useless.
assessment_table = assessment_table.drop(columns='LEANumber', errors='ignore')

# Drop all rows where TestName does not begin with ACT. This will filter out SAT scores
assessment_table = assessment_table[assessment_table['TestName'].str.startswith('ACT', na=False)]

# Rename columns for consistency
assessment_table = assessment_table.rename(columns={
    'TestName': 'test_name',
    'TestDate': 'test_date',
    'Subtest': 'subtest',
    'TestScore': 'test_score'
})

# Ensure test_score is numeric to avoid aggregation issues
assessment_table['test_score'] = pd.to_numeric(assessment_table['test_score'], errors='coerce')

# Convert test_date to datetime format (not critical)
assessment_table['test_date'] = pd.to_datetime(assessment_table['test_date'], errors='coerce')

# Pivot table to turn subtest values into columns and fill with test scores
# Include student_number, test_name and test_date in the pivot index since there is 
# only one test_name and test_date per test, it does not matter which one we use.
assessment_grid = assessment_table.pivot_table(
    index=['student_number', 'test_name', 'test_date'],
    columns='subtest',
    values='test_score',
)

# Rename new columns created from the pivot for consistency
assessment_grid = assessment_grid.rename(columns={
    'Composite': 'composite_score',
    'English': 'english_score',
    'Math': 'math_score',
    'Reading': 'reading_score',
    'Science': 'science_score',
    'Writing': 'writing_score'
})

# Reset the index to make student_number a column again
assessment_grid = assessment_grid.reset_index()

# Drop the test_name column as all values are the same
assessment_grid.drop(columns='test_name', inplace=True, errors='ignore')

# Make sure student_number is a string
assessment_grid['student_number'] = assessment_grid['student_number'].astype(str)
df['student_number'] = df['student_number'].astype(str)

# Merge assessment_grid into the df
df = pd.merge(df, assessment_grid, on='student_number', how='left')

# Some students have taken the ACT multiple times. We want to keep the row with the highest composite score.
# Create a list of students with multiple test enteries
duplicates = df[df.duplicated(subset='student_number', keep=False)]

# Sort duplicates by highest composite_score
duplicates = duplicates.sort_values(by='composite_score', ascending=False)

# Drop all but the row with the highest composite score per student_number
duplicates = duplicates.drop_duplicates(subset='student_number', keep='first')

# Drop all duplicate rows from the df
df = df[~df.duplicated(subset='student_number', keep=False)].reset_index(drop=True)

# Add cleaned duplicates back to the df
df = pd.concat([df, duplicates], ignore_index=True).reset_index(drop=True)

df.head()


######################################################################################################################################################
# Export the data
df.to_csv('./data/assessment_data.csv', index=False)

print("Assessment data exported successfully!")