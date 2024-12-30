import pandas as pd
import numpy as np

# Data sheets
membership = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Course Membership')
master = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Course Master')
courses = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Transcript Courses')

# Rename 'StudentNumber' to 'student_number'
courses = courses.rename(columns={'StudentNumber': 'student_number'})
membership = membership.rename(columns={'StudentNumber': 'student_number'})

# Import student_table and high_school_student (for now)
student_table = pd.read_csv('data/student_table.csv')
high_school_students = pd.read_csv('data/high_school_students.csv')

# Create the df from the high_school_student student_numbers
df = high_school_students[['student_number']].copy()

# Create the model_df from the high_school_student student_numbers
model_df = high_school_students[['student_number']].copy()

###########################################################################


#------------------------------------------------------------------------------------------------------------------------------
# Get the current grade level and school for each student. Then dummy code school and grade columns

# Rename SchoolNumber to school_number on the membership table
membership = membership.rename(columns={'SchoolNumber': 'school_number', 'CourseNumber': 'course_number'})
courses = courses.rename(columns={'CourseNumber': 'course_number', 'GradeLevel': 'grade_level', 'SchoolYear': 'school_year'})
master = master.rename(columns={'CourseSection': 'course_number'})

membership.duplicated().sum()
master.duplicated().sum()
master = master.drop_duplicates(keep = 'first')

student_membership = membership[['student_number', 'school_number', 'CourseRecordID']].copy()
student_membership.duplicated().sum()
student_membership = student_membership.drop_duplicates(keep='first')

student_master = master[['course_number', 'CourseRecordID']].copy()
student_master.duplicated().sum()
student_master = student_master.drop_duplicates(keep='first')

student_master['CourseRecordID'] = student_master['CourseRecordID'].astype(str)
student_membership['CourseRecordID'] = student_membership['CourseRecordID'].astype(str)

student_school = pd.merge(student_master, student_membership, on='CourseRecordID', how='left')
student_school.head()
student_school.duplicated(subset=['student_number', 'school_number']).sum()
student_school = student_school.drop_duplicates(subset=['student_number', 'school_number'], keep= 'first')
student_school.duplicated(subset='student_number').sum()

student_school = student_school.drop(columns=['CourseRecordID', 'course_number'])
student_school['school_number'].value_counts()

# Pivot the table to create a grid of student_number by school_number
school_grid = student_school.pivot_table(
    index='student_number',
    columns='school_number',
    values='school_number',  # Use school_number to create binary attendance indicators
    aggfunc=lambda x: 1,     # Set 1 to indicate attendance
    fill_value=0             # Fill missing values with 0 to indicate no attendance
)

# Rename the columns to make them more descriptive
school_grid.columns = [f'school_{int(col)}' for col in school_grid.columns]

# Reset the index to include student_number as a column if needed
school_grid = school_grid.reset_index()

# View the resulting DataFrame
school_grid.head()

# Add a column to count the number of schools attended by each student
school_grid['school_count'] = school_grid.iloc[:, 1:].sum(axis=1)

# Filter for students who attended more than 1 school
students_with_multiple_schools = school_grid[school_grid['school_count'] > 2]

# View the results
print(students_with_multiple_schools)

school_grid['school_count'].value_counts()

school_grid.duplicated(subset='student_number').sum()


courses['school_year'].value_counts()
courses.columns