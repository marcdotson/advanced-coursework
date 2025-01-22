import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)

# Load data sheets
student = pd.read_excel('../data/2022 EOY Data - USU.xlsx', sheet_name='Student') 
master = pd.read_excel('../data/2022 EOY Data - USU.xlsx', sheet_name='Course Master')
membership = pd.read_excel('../data/2022 EOY Data - USU.xlsx', sheet_name='Course Membership')
courses = pd.read_excel('../data/2022 EOY Data - USU.xlsx', sheet_name='Transcript Courses')

# Rename 'StudentNumber' to 'student_number' for consistency
courses = courses.rename(columns={'StudentNumber': 'student_number'})
membership = membership.rename(columns={'StudentNumber': 'student_number'})
student = student.rename(columns={'StudentNumber': 'student_number'})

# Import student_table and high_school_student (for now)
student_table = pd.read_csv('../data/student_table.csv')
high_school_students = pd.read_csv('../data/high_school_students.csv')

# Create the df from the high_school_student student_numbers
df = high_school_students[['student_number']]

# Create the model_df from the high_school_student student_numbers
model_df = high_school_students[['student_number']]

###########################################################################

#------------------------------------------------------------------------------------------------------------------------------
# Student's Teacher by TeacherID and Grade for the model (which teachers students had and in what grade)

course_data = courses[['student_number', 'GradeLevel']]
membership_data = membership[['student_number', 'CourseRecordID']]
master_data = master[['CourseRecordID', 'Teacher1ID']]

# Merge master and membership on 'CourseRecordID' to get Teacher1ID per student
teacher_membership = pd.merge(membership_data, master_data, on='CourseRecordID', how='left')

# Merge with courses on 'student_number' to add GradeLevel
teacher_data = pd.merge(teacher_membership, course_data, on='student_number', how='left')

# Drop rows that have the same combination of student_number, GradeLevel, and Teacher1ID
# This removes exact duplicates while still allowing duplicate student_numbers to remain
# The goal is to retain a list of all unique teachers that each student has had
teacher_data = teacher_data.drop_duplicates()

# Convert 'Teacher1ID' to strings
teacher_data['Teacher1ID'] = teacher_data['Teacher1ID'].astype(str)

# Create the 'Teacher_Grade' column
teacher_data['Teacher_Grade'] = 'teacher_' + teacher_data['Teacher1ID']

# Create dummy variables for 'Teacher_Grade'
teacher_dummies = pd.get_dummies(teacher_data['Teacher_Grade'], prefix='', prefix_sep='')

# Add 'student_number' back to the dummy DataFrame
teacher_dummies['student_number'] = teacher_data['student_number']

# Group by 'student_number' and sum the dummy variables to get the final DataFrame
teacher_dummies = teacher_dummies.groupby('student_number').sum().reset_index()

# Make sure student_number is a string
teacher_dummies['student_number'] = teacher_dummies['student_number'].astype(str)
model_df['student_number'] = model_df['student_number'].astype(str)

# Add teacher_dummies to the model_df
model_df = pd.merge(model_df, teacher_dummies, on='student_number', how='left')

# Save the model_df to a CSV file in the data folder
model_df.to_csv('../data/teacher_2022.csv', index=False)

model_df.head()