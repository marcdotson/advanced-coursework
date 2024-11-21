import pandas as pd

# Data sheets
student = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Student')
master = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Course Master')
membership = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Course Membership')
courses = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Transcript Courses')


# Rename 'StudentNumber' to 'student_number'
courses = courses.rename(columns={'StudentNumber': 'student_number'})
membership = membership.rename(columns={'StudentNumber': 'student_number'})
student = student.rename(columns={'StudentNumber': 'student_number'})


#------------------------------------------------------------------------------------
# Start by building the df with high school student_numbers from the student table
student['GradeLevel'] = pd.to_numeric(student['GradeLevel'], errors='coerce')

# Filter the student table to include only high school students (This variable will be used throughout the script)
#high_school_students = student[student['GradeLevel'] > 8]
#high_school_students['student_number'] = high_school_students['student_number'].astype(str)
high_school_students = student[student['GradeLevel'] > 8][['student_number']].copy()
high_school_students['student_number'] = high_school_students['student_number'].astype(str)

# Create the df from the high_school_student student_numbers
df = high_school_students[['student_number']]

# Remove duplicate rows based on 'student_number' to ensure each student is included only once
df = df.drop_duplicates()

df.head()


#------------------------------------------------------------------------------------
# Merge membership and master data on the CourseRecordID from the membership table
membership_filtered = membership[['student_number', 'CourseRecordID', 'ConcurrEnrolled', 'GradeEarned']]
master_filtered = master[['CourseTitle', 'CollegeGrantingCr', 'WhereTaughtCampus', 'CourseRecordID']]
advanced_courses = pd.merge(membership_filtered, master_filtered, on='CourseRecordID', how='left')

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


# Add CumulativeGPA from the student table to the df
cumulative_gpa = student[['student_number', 'CumulativeGPA']]
cumulative_gpa = cumulative_gpa.drop_duplicates()

# Make sure student_number is a string
cumulative_gpa['student_number'] = cumulative_gpa['student_number'].astype(str)
df['student_number'] = df['student_number'].astype(str)

df = pd.merge(df, cumulative_gpa, on='student_number', how='left')
df = df.rename(columns={'CumulativeGPA': 'overall_gpa'})

# Make sure student_number is a string
advanced_summary['student_number'] = advanced_summary['student_number'].astype(str)
df['student_number'] = df['student_number'].astype(str)

# Add the advanced_summary data to the df
df = pd.merge(df, advanced_summary, on='student_number', how='left')

# Fill null values with 0
df[['overall_gpa','ac_ind', 'ac_count']] = df[['overall_gpa', 'ac_ind', 'ac_count']].fillna(0)
df.head()


#------------------------------------------------------------------------------------
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
df['student_number'] = avg_ac_grade['student_number'].astype(str)

# Add avg_gpa to the df
df = pd.merge(df, avg_ac_grade, on='student_number', how='left')

# Fill null values with 0
df['ac_gpa'] = df['ac_gpa'].fillna(0)

# Convert ac_gpa to a float and round 3 decimal places
df['ac_gpa'] = df['ac_gpa'].astype(float).round(3)

df.head()


#------------------------------------------------------------------------------------
# Student Attendance by School and Grade (which schools students attended and in what grade)
course_year = courses[['student_number', 'GradeLevel']]
school_number = membership[['student_number', 'SchoolNumber']]

# Merge 'school_number' and 'course_year' on 'student_number'
school_data = pd.merge(school_number, course_year, on='student_number', how='left')

# Drop rows that have the same combination of student_number, GradeLevel, and SchoolNumber
# This removes exact duplicates while still allowing duplicate student_numbers to remain
# The goal is to retain a list of all unique courses that each student has taken
school_data = school_data.drop_duplicates()

#Convert 'SchoolNumber' and 'GradeLevel' to strings
school_data['SchoolNumber'] = school_data['SchoolNumber'].astype(str)
school_data['GradeLevel'] = school_data['GradeLevel'].astype(str)

# Create the 'School_Grade' column with school and grade information
school_data['School_Grade'] = 'school_' + school_data['SchoolNumber'] + '_grade_' + school_data['GradeLevel']

# Pivot the data to create a grid for each student, indicating attendance with 1 and non-attendance with 0
school_grid = school_data.pivot_table(
    index='student_number',
    columns='School_Grade',
    values='GradeLevel',
    aggfunc=lambda x: 1,    # Use 1 to indicate attendance
    fill_value=0            # Fill missing values with 0 to indicate no attendance
)

school_grid.columns = school_grid.columns.str.replace(r'\.0', '', regex=True)
school_grid.reset_index(inplace=True)

# Reorder the school_grid columns dynamically
school_columns = sorted([col for col in school_grid.columns if col.startswith('school_')], reverse=True)

# Ensure 'student_number' is the first column, followed by the school columns
grid_columns = ['student_number'] + school_columns

school_grid = school_grid.reindex(columns=grid_columns)

# Retrieve a list of all student_numbers for students currently in high school (high_school_students_school_grid)
# This is done after pivoting the data to retain information about the schools students attended before high school
# Students who are not currently in high school are excluded from this list
high_school_students_school_grid = student[['student_number', 'GradeLevel']]
high_school_students_school_grid = high_school_students_school_grid[high_school_students_school_grid['GradeLevel']>8]

# The data from the student table contains duplicates that need to be dropped
high_school_students_school_grid = high_school_students_school_grid.drop_duplicates()

# Make sure student_number is a string
high_school_students_school_grid['student_number'] = high_school_students_school_grid['student_number'].astype(str)
school_grid['student_number'] = school_grid['student_number'].astype(str)

# Filter school_grid to include only rows for students who are in high school
#school_grid = school_grid[school_grid['student_number'].isin(high_school_students['student_number'])]
school_grid = school_grid[school_grid['student_number'].isin(high_school_students_school_grid['student_number'])].copy()


# Identify columns where all values are 0 after 8th graders are filtered out
school_grid_null_columns = school_grid.columns[(school_grid == 0).all()]

# Drop columns from school_grid where all values in the column are 0
school_grid = school_grid.drop(school_grid_null_columns, axis=1)

school_grid.head()
# This is not added to the df, because we only want to include the grid into the modeling data


#------------------------------------------------------------------------------------
# Student's Teacher by TeacherID and Grade (which teachers students had and in what grade)

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
high_school_students_teacher_grid = student[['student_number','GradeLevel']]
high_school_students_teacher_grid = high_school_students_teacher_grid[high_school_students_teacher_grid['GradeLevel']>8]

# The data from the student table contains duplicates that need to be dropped
high_school_students_teacher_grid = high_school_students_teacher_grid.drop_duplicates()

# Make sure student_number is a string
high_school_students_teacher_grid['student_number'] = high_school_students_teacher_grid['student_number'].astype(str)
teacher_grid['student_number'] = teacher_grid['student_number'].astype(str)

# Filter teacher_grid to include only rows for students who are in high school
#teacher_grid = teacher_grid[teacher_grid['student_number'].isin(high_school_students['student_number'])]
teacher_grid = teacher_grid[teacher_grid['student_number'].isin(high_school_students_teacher_grid['student_number'])].copy()

# Identify columns where all values are 0 after 8th graders are filtered out
teacher_grid_null_columns = teacher_grid.columns[(teacher_grid == 0).all()]

# Drop columns from teacher_grid where all values in the column are 0
teacher_grid = teacher_grid.drop(teacher_grid_null_columns, axis=1)

teacher_grid.head()
# This is not added to the df, because we only want to include the grid into the modeling data


#------------------------------------------------------------------------------------
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


#------------------------------------------------------------------------------------
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

grade_school_dummies.head()

#------------------------------------------------------------------------------------
# Get the current years attendance for each student (Out of 180 days)
student_attendance = student[['student_number', 'GradeLevel', 'DaysAttended']]

# Group by 'student_number' to get the maximum 'GradeLevel' and corresponding 'DaysAttended'
current_attendance = student_attendance.groupby('student_number', as_index=False).agg({
    'GradeLevel': 'max',           # Get the maximum GradeLevel
    'DaysAttended': 'last'         # Get the days attended associated with the max GradeLevel
})

# Rename columns
current_attendance = current_attendance.rename(columns={'DaysAttended': 'days_attended'})
current_attendance = current_attendance[['student_number', 'days_attended']]

# Make sure student_number is a string
current_attendance['student_number'] = current_attendance['student_number'].astype(str)
df['student_number'] = df['student_number'].astype(str)

# Add current_attendance to the df
df = pd.merge(df, current_attendance, on='student_number', how='left')


#------------------------------------------------------------------------------------
# Make sure student_number is a string
df['student_number'] = df['student_number'].astype(str)

# Fill any null values with 0
df = df.fillna(0)

# Define the desired column order for df
df_columns = [
    'student_number', 'ac_ind', 'ac_count', 'ac_gpa', 'overall_gpa', 
    'current_grade', 'current_school', 'days_attended'
] + [col for col in df.columns if col.startswith('teacher_')]

df = df[df_columns]

# This is a check to make sure no duplicate rows are included
df = df.drop_duplicates()

df.head()

# ------------------------------------------------------------------------------------
# Prepare the modeling data by joining data from df and the grids

# Get the columns we want from df
model_data = df[['student_number', 'ac_ind', 'overall_gpa', 'days_attended']]

# grade_school_dummies, teacher_grid, and school_grid were not added to the df
model_data = pd.merge(model_data, grade_school_dummies, on='student_number', how='left')
model_data = pd.merge(model_data, teacher_grid, on='student_number', how='left')
model_data = pd.merge(model_data, school_grid, on='student_number', how='left')

model_data.head()

df.head()

# ------------------------------------------------------------------------------------
# Export the exploratory data
df.to_csv('./data/01_exploratory_powerschool_data.csv', index=False)

# Export the modeling data
model_data.to_csv('./data/01_modeling_powerschool_data.csv', index=False)

print("Data exported successfully!")