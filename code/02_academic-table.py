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

# Import student_table and high_school_student (for now)
student_table = pd.read_csv('data/student_table.csv')
high_school_students = pd.read_csv('data/high_school_students.csv')

# Create the df from the high_school_student student_numbers
df = high_school_students[['student_number']]

# Create the model_df from the high_school_student student_numbers
model_df = high_school_students[['student_number']]

###########################################################################

# Add CumulativeGPA from the student table to the df
cumulative_gpa = student_table[['student_number', 'CumulativeGPA']]

# Make sure student_number is a string
cumulative_gpa['student_number'] = cumulative_gpa['student_number'].astype(str)
df['student_number'] = df['student_number'].astype(str)

df = pd.merge(df, cumulative_gpa, on='student_number', how='left')
df = df.rename(columns={'CumulativeGPA': 'overall_gpa'})

df.head()

#------------------------------------------------------------------------------------------------------------------------------
# Merge membership and master data on the CourseRecordID from the membership table
membership_filtered = membership[['student_number', 'CourseRecordID', 'ConcurrEnrolled', 'GradeEarned']]
master_filtered = master[['CourseTitle', 'CollegeGrantingCr', 'WhereTaughtCampus', 'CourseRecordID']]
advanced_courses = pd.merge(membership_filtered, master_filtered, on='CourseRecordID', how='left')

# Drop identical rows
advanced_courses = advanced_courses.drop_duplicates()

# Identify advanced courses
# The result is converted to an integer type (1 for True, 0 for False)
advanced_courses['advanced_course'] = (
    (advanced_courses['CollegeGrantingCr'].notnull()) | # Check for college credit
    (advanced_courses['WhereTaughtCampus'].notnull()) | # Check for campus location
    (advanced_courses['ConcurrEnrolled'] == 'Y') | # Check for concurrent enrollment
    (advanced_courses['CourseTitle'].str.startswith('AP', na=False)) | # Check for AP courses
    (advanced_courses['CourseTitle'].str.startswith('BTEC', na=False)) # Check for BTEC courses
).astype(int)

# If CourseTitle is in the advanced_course list then add a 1 to the new column
advanced_summary = advanced_courses.groupby('student_number', as_index=False).agg(
    ac_ind=('advanced_course', lambda x: 1 if x.sum() > 0 else 0),  # Has at least one advanced course
    ac_count=('advanced_course', 'sum')  # Total advanced courses
)

# Make sure student_number is a string
advanced_summary['student_number'] = advanced_summary['student_number'].astype(str)
df['student_number'] = df['student_number'].astype(str)

# Add the advanced_summary data to the df
df = pd.merge(df, advanced_summary, on='student_number', how='left')

# Fill null values with 0
df[['overall_gpa','ac_ind', 'ac_count']] = df[['overall_gpa', 'ac_ind', 'ac_count']].fillna(0)
df.head()


#------------------------------------------------------------------------------------------------------------------------------
# Calculate students gpa in advanced courses
# Filter for advanced courses based on the advanced_courses list
ac_grade = advanced_courses[advanced_courses['advanced_course'] == 1][['student_number', 'GradeEarned']].copy()

# Replace 'P' and 'F' with numeric values
ac_grade['GradeEarned'] = ac_grade['GradeEarned'].replace({'P': 4.0, 'F': 0.0})

# Ensure GradeEarned is numeric
ac_grade['GradeEarned'] = pd.to_numeric(ac_grade['GradeEarned'], errors='coerce')

# Calculate the average grade for each student
avg_ac_grade = ac_grade.groupby('student_number', as_index=False)['GradeEarned'].mean()

# Rename the GradeEarned column to 'ac_gpa'
avg_ac_grade.rename(columns={'GradeEarned': 'ac_gpa'}, inplace=True)

# Make sure student_number is a string
avg_ac_grade['student_number'] = avg_ac_grade['student_number'].astype(str)
df['student_number'] = df['student_number'].astype(str)

# Add avg_gpa to the df
df = pd.merge(df, avg_ac_grade, on='student_number', how='left')

# Fill null values with 0
df['ac_gpa'] = df['ac_gpa'].fillna(0)

# Convert ac_gpa to a float and round 3 decimal places
df['ac_gpa'] = df['ac_gpa'].astype(float).round(3)

df.head()
