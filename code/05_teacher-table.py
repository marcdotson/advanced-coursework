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

# Convert 'Teacher1ID' and 'GradeLevel' to strings
teacher_data['Teacher1ID'] = teacher_data['Teacher1ID'].astype(str)
teacher_data['GradeLevel'] = teacher_data['GradeLevel'].astype(str)

# Create the 'Teacher_Grade' column
teacher_data['Teacher_Grade'] = 'teacher_' + teacher_data['Teacher1ID'] + '_grade_' + teacher_data['GradeLevel']

# Pivot the data to create a grid for each student, indicating if a student has had a teacher with 1 and not had with 0
teacher_grid = teacher_data.pivot_table(
    index='student_number',
    columns='Teacher_Grade',
    values='GradeLevel',
    aggfunc=lambda x: 1,    # Use 1 to indicate if a student has had a teacher
    fill_value=0            # Fill missing values with 0 to indicate if a student has not had a teacher
)

teacher_grid.columns = teacher_grid.columns.str.replace(r'\.0', '', regex=True)
teacher_grid.reset_index(inplace=True)

# Retrieve a list of all student_numbers for students currently in high school (high_school_students_teacher_grid)
# This is done after pivoting the data to retain information about the teachers students had before high school
# Students who are not currently in high school are excluded from this list
high_school_students_teacher_grid = student_table[['student_number','GradeLevel']]
high_school_students_teacher_grid = high_school_students_teacher_grid[high_school_students_teacher_grid['GradeLevel']>8]

# Make sure student_number is a string
high_school_students_teacher_grid['student_number'] = high_school_students_teacher_grid['student_number'].astype(str)
teacher_grid['student_number'] = teacher_grid['student_number'].astype(str)

# Filter teacher_grid to include only rows for students who are in high school
teacher_grid = teacher_grid[teacher_grid['student_number'].isin(high_school_students_teacher_grid['student_number'])].copy()

# Identify columns where all values are 0 after 8th graders are filtered out
teacher_grid_null_columns = teacher_grid.columns[(teacher_grid == 0).all()]

# Drop columns from teacher_grid where all values in the column are 0
teacher_grid = teacher_grid.drop(teacher_grid_null_columns, axis=1)

# Make sure student_number is a string
teacher_grid['student_number'] = teacher_grid['student_number'].astype(str)
model_df['student_number'] = model_df['student_number'].astype(str)

teacher_grid.head()

# Add teacher_grid to the model_df
model_df = pd.merge(model_df, teacher_grid, on='student_number', how='left')

model_df.head()
