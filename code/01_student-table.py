import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)

# Data sheets
student = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Student')
master = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Course Master')
membership = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Course Membership')
courses = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Transcript Courses')


# Rename 'StudentNumber' to 'student_number'
courses = courses.rename(columns={'StudentNumber': 'student_number'})
membership = membership.rename(columns={'StudentNumber': 'student_number'})
student = student.rename(columns={'StudentNumber': 'student_number'})

# Create the df
df = pd.DataFrame()

# Create the model_df
model_df = pd.DataFrame()

#------------------------------------------------------------------------------------------------------------------------------
# Filter the student table down to 1 row per student. This will make everything easier moving forward
student_columns_to_drop = [
    "ExitDate", "ResidentStatus", "KindergartenType", "EarlyGrad", "ReadGradeLevelFall", 
    "ReadGradeLevelSpring", "Biliteracy1Level", "Biliteracy1Language", "Biliteracy2Level",
    "Biliteracy2Language", "EarlyNumeracyStatusBOY", "EarlyNumeracyStatusMOY", 
    "EarlyNumeracyStatusEOY", "EarlyNumeracyIntervention"
]

# Create the table student_table
student_table = student

# Drop the columns we do not want
student_table = student_table.drop(columns = student_columns_to_drop)

# Drop rows where student_number is null
student_table = student_table.dropna(subset=['student_number'])
student_table = student_table[student_table['student_number'] != '']

# Drop duplicate student_numbers but keep the row with the largest GradeLevel
student_table = student_table.loc[
    student_table.groupby('student_number')['GradeLevel'].idxmax()
]

# Reset index
student_table.reset_index(drop=True, inplace=True)

student_table.head()

#############################################################################
# Filter at the end of all of the data wrangling?

#------------------------------------------------------------------------------------------------------------------------------
# Start by building the df, and model_df with high school student_numbers from the student_table
student_table['GradeLevel'] = pd.to_numeric(student['GradeLevel'], errors='coerce')

# Filter the student table to include only high school students
high_school_students = student_table[student_table['GradeLevel'] > 8][['student_number', 'GradeLevel']].copy()
high_school_students['student_number'] = high_school_students['student_number'].astype(str)

# Create the df from the high_school_student student_numbers
df = high_school_students[['student_number']]

# Create the model_df from the high_school_student student_numbers
model_df = high_school_students[['student_number']]

df.head()

#############################################################################
# Export student_table.
student_table.to_csv('./data/student_table.csv')

# Export student_table.
high_school_students.to_csv('./data/high_school_students.csv')
