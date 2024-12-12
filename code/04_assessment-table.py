import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)

# Data sheets
# student = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Student')
# master = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Course Master')
# membership = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Course Membership')
# courses = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Transcript Courses')
assesment = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Transcript Assessments')

# Rename 'StudentNumber' to 'student_number'
courses = courses.rename(columns={'StudentNumber': 'student_number'})
membership = membership.rename(columns={'StudentNumber': 'student_number'})
student = student.rename(columns={'StudentNumber': 'student_number'})

# Import student_table and high_school_student (for now)
student_table = pd.read_csv('data/student_table.csv')
high_school_students = pd.read_csv('data/high_school_students.csv')

# Create the df from the high_school_student student_numbers
df = high_school_students[['student_number']]

# Create the model_df from the high_school_student student_numbers
model_df = high_school_students[['student_number']]

###########################################################################

#------------------------------------------------------------------------------------------------------------------------------
# Add the transcript assessment data to the model_df and the df

# Extract high school student_numbers and merge with assessment table (This way we only have student_numbers for hs students)
assessment_table = hs_student_table[['student_number']].copy()
assessment_table = pd.merge(assessment_table, assessment, on='student_number', how='left')

# Drop LEANumber from the assessment_table. All values are the same making it useless.
assessment_table = assessment_table.drop(columns='LEANumber', errors='ignore')

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
# only one test_name and test_date per student, it does not matter which one we use.
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

assessment_grid.head()

# Make sure student_number is a string
assessment_grid['student_number'] = assessment_grid['student_number'].astype(str)
df['student_number'] = df['student_number'].astype(str)
model_df['student_number'] = model_df['student_number'].astype(str)

# Merge into df
df = pd.merge(df, assessment_grid, on='student_number', how='left')

# Merge into model_df
model_df = pd.merge(model_df, assessment_grid, on='student_number', how='left')
