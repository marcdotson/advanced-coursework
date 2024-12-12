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
# High school student's unique teachers in 2022

master_teacher = master[['CourseRecordID', 'Teacher1ID']]
membership_teacher = membership[['CourseRecordID', 'student_number']]

# Drop duplicates from courses table to avoid repeated data,
# as the data is too generic to filter accurately using only the three selected columns below
school_year = courses.drop_duplicates()
school_year = school_year[['student_number', 'SchoolYear', 'GradeLevel']]

# Merge the data
# Use an outer join to include all courses and teachers, even if data is missing
teacher_year = pd.merge(master_teacher, membership_teacher, on='CourseRecordID', how='outer')

# Use an outer join to include all students and their related data, even if some records are incomplete
teacher_join = pd.merge(school_year, teacher_year, on='student_number', how='outer')

# Filter to only include high school students
teacher_join = teacher_join[teacher_join['GradeLevel'] > 8]

# Filter data to include only the year 2022
teacher_2022 = teacher_join[teacher_join['SchoolYear'] == 2022]

# Remove duplicate pairs of student_number and Teacher1ID
teacher_2022 = teacher_2022.drop_duplicates(subset=['student_number', 'Teacher1ID'])

# Count the number of unique teachers for each student
teacher_counts = teacher_2022.groupby('student_number')['Teacher1ID'].nunique()

# Create a list of unique teachers for each student
teacher_list = teacher_2022.groupby('student_number')['Teacher1ID'].apply(list)

# Determine the maximum number of unique teachers any student had in 2022
max_teachers = teacher_list.apply(len).max()

# Convert the teacher list into a DataFrame
teacher_df = pd.DataFrame(teacher_list.tolist(), index=teacher_list.index)

# Create column names based on the number of unique teachers
teacher_df.columns = [f'teacher_{i+1}' for i in range(teacher_df.shape[1])]

teacher_df.reset_index(inplace=True)

# Replace NaN values with 0
teacher_df = teacher_df.fillna(0)

# Make sure student_number is a string
teacher_df['student_number'] = teacher_df['student_number'].astype(str)
df['student_number'] = df['student_number'].astype(str)

# Add teacher_df to the df
df = pd.merge(df, teacher_df, on='student_number', how='left')
df.head()


#------------------------------------------------------------------------------------------------------------------------------
# Get the current grade level and school for each student. Then dummy code school and grade columns

student_school = pd.merge(membership[['student_number', 'SchoolNumber']],
                          courses[['student_number', 'GradeLevel']],
                          on='student_number',
                          how='left')

# Filter to only include high school students
student_school = student_school[student_school['GradeLevel'] > 8]

# Sort the data by 'student_number' and 'GradeLevel' to prepare for grouping
student_school = student_school.sort_values(by=['student_number', 'GradeLevel'])

# Group by 'student_number' to get the most recent grade level and school for each student
current_school_grade = student_school.groupby('student_number', as_index=False).agg({
    'GradeLevel': 'max',   # Get the maximum school year
    'SchoolNumber': 'last' # Get the school associated with the latest year
})

# Rename columns
current_school_grade = current_school_grade.rename(columns={'GradeLevel': 'current_grade', 'SchoolNumber': 'current_school'})

# Make sure student_number is a string
current_school_grade['student_number'] = current_school_grade['student_number'].astype(str)
df['student_number'] = df['student_number'].astype(str)

# Add current_grade and current_school to the df
df = pd.merge(df, current_school_grade, on='student_number', how='left')

# Create dummy variables for 'current_school' and 'current_grade'
school_dummies = pd.get_dummies(current_school_grade['current_school'], prefix='current_school', dtype=int)
grade_dummies = pd.get_dummies(current_school_grade['current_grade'], prefix='current_grade', dtype=int)

# Combine the dummy variables into a separate DataFrame, excluding current_school and current_grade
grade_school_dummies = pd.concat([school_dummies, grade_dummies], axis=1)

# Add student_number back to grade_school_dummies for reference
grade_school_dummies['student_number'] = current_school_grade['student_number']

# Reorder columns to ensure student_number is the first column
grade_school_dummies = grade_school_dummies[['student_number'] + [col for col in grade_school_dummies.columns if col != 'student_number']]

# Make sure student_number is a string
grade_school_dummies['student_number'] = grade_school_dummies['student_number'].astype(str)
model_df['student_number'] = model_df['student_number'].astype(str)

grade_school_dummies.head()

# Add grade_school_dummies to the model_df
model_df = pd.merge(model_df, grade_school_dummies, on='student_number', how='left')

model_df.head()
