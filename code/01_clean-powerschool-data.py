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
# Only include high school students in df
student['GradeLevel'] = pd.to_numeric(student['GradeLevel'], errors='coerce')
high_school_students = student[student['GradeLevel'] > 8]
df = high_school_students[['student_number']]
df = df.drop_duplicates()
df.head()


#------------------------------------------------------------------------------------
# Merge membership and master data
membership_filtered = membership[['student_number', 'CourseRecordID', 'ConcurrEnrolled', 'GradeEarned']]
master_filtered = master[['CourseTitle', 'CollegeGrantingCr', 'WhereTaughtCampus', 'CourseRecordID']]
advanced_courses = pd.merge(membership_filtered, master_filtered, on='CourseRecordID', how='left')

# Identify advanced courses
advanced_courses['advanced_course'] = (
    (advanced_courses['CollegeGrantingCr'].notnull()) |
    (advanced_courses['WhereTaughtCampus'].notnull()) |
    (advanced_courses['ConcurrEnrolled'] == 'Y') |
    (advanced_courses['CourseTitle'].str.startswith('AP', na=False)) |
    (advanced_courses['CourseTitle'].str.startswith('BTEC', na=False))
).astype(int)

# If CourseTitle is in the advanced_course list then add a 1 to the new column
advanced_summary = advanced_courses.groupby('student_number', as_index=False).agg(
    ac_ind=('advanced_course', lambda x: 1 if x.sum() > 0 else 0),  # Has at least one advanced course
    ac_count=('advanced_course', 'sum')  # Total advanced courses
)

cumulative_gpa = student[['student_number', 'CumulativeGPA']]
cumulative_gpa = cumulative_gpa.drop_duplicates()
df = pd.merge(df, cumulative_gpa, on='student_number', how='left')
df = df.rename(columns={'CumulativeGPA': 'overall_gpa'})

df = pd.merge(df, advanced_summary, on='student_number', how='left')
df[['overall_gpa','ac_ind', 'ac_count']] = df[['overall_gpa', 'ac_ind', 'ac_count']].fillna(0)
df.head()


#------------------------------------------------------------------------------------
# Calculate students gpa in advanced courses
# Filter for advanced courses only
ac_grade = advanced_courses[advanced_courses['advanced_course'] == 1][['student_number', 'GradeEarned']].copy()

# Replace 'P' and 'F' with numeric values
ac_grade['GradeEarned'] = ac_grade['GradeEarned'].replace({'P': 4.0, 'F': 0.0})

# Ensure GradeEarned is numeric
ac_grade['GradeEarned'] = pd.to_numeric(ac_grade['GradeEarned'], errors='coerce')

# Calculate the average grade for each student
avg_ac_grade = ac_grade.groupby('student_number', as_index=False)['GradeEarned'].mean()

# Rename the GradeEarned column to 'ac_gpa'
avg_ac_grade.rename(columns={'GradeEarned': 'ac_gpa'}, inplace=True)

df = pd.merge(df, avg_ac_grade, on='student_number', how='left')

df['ac_gpa'] = df['ac_gpa'].fillna(0)
df['ac_gpa'] = df['ac_gpa'].astype(float)

df.head()


#------------------------------------------------------------------------------------
# Student Attendance by School and Grade
course_year = courses[['student_number', 'GradeLevel']]
school_number = membership[['student_number', 'SchoolNumber']]

# Merge 'school_number' and 'course_year' on 'student_number'
school_data = pd.merge(school_number, course_year, on='student_number', how='left')

# Drop rows that have the same student_number, GradeLevel and SchoolNumber
school_data = school_data.drop_duplicates()

#Convert 'SchoolNumber' and 'GradeLevel' to strings
school_data['SchoolNumber'] = school_data['SchoolNumber'].astype(str)
school_data['GradeLevel'] = school_data['GradeLevel'].astype(str)

# Create the 'School_Grade' column with school and grade information, retaining NaNs
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


# Get a list of all student_numbers for students in high school
high_school_students = course_year[course_year['GradeLevel']>8]

# Make sure student_number is a string
high_school_students['student_number'] = high_school_students['student_number'].astype(str)
school_grid['student_number'] = school_grid['student_number'].astype(str)

# Filter school_grid to include only rows for students who are in high school
school_grid = school_grid[school_grid['student_number'].isin(high_school_students['student_number'])]

# Identify columns where all values are 0 after 8th graders are filtered out
school_grid_null_columns = school_grid.columns[(school_grid == 0).all()]

# Drop columns from school_grid where all values in the column are 0
school_grid = school_grid.drop(school_grid_null_columns, axis=1)

school_grid.head()


#------------------------------------------------------------------------------------
# Student's Teacher by TeacherID and Grade

course_data = courses[['student_number', 'GradeLevel']]
membership_data = membership[['student_number', 'CourseRecordID']]
master_data = master[['CourseRecordID', 'Teacher1ID']]

# Merge master and membership on 'CourseRecordID' to get Teacher1ID per student
teacher_membership = pd.merge(membership_data, master_data, on='CourseRecordID', how='left')

# Merge with courses on 'student_number' to add GradeLevel
teacher_data = pd.merge(teacher_membership, course_data, on='student_number', how='left')

# Drop rows that have the same student_number, GradeLevel, and Teacher1ID
teacher_data = teacher_data.drop_duplicates()

# Convert 'Teacher1ID' and 'GradeLevel' to strings
teacher_data['Teacher1ID'] = teacher_data['Teacher1ID'].astype(str)
teacher_data['GradeLevel'] = teacher_data['GradeLevel'].astype(str)

# Create the 'Teacher_Grade' column
teacher_data['Teacher_Grade'] = 'teacher_' + teacher_data['Teacher1ID'] + '_grade_' + teacher_data['GradeLevel']

# Pivot the data to create a grid for each student, indicating attendance with 1 and non-attendance with 0
teacher_grid = teacher_data.pivot_table(
    index='student_number',
    columns='Teacher_Grade',
    values='GradeLevel',
    aggfunc=lambda x: 1,    # Use 1 to indicate attendance
    fill_value=0            # Fill missing values with 0 to indicate no attendance
)

teacher_grid.columns = teacher_grid.columns.str.replace(r'\.0', '', regex=True)
teacher_grid.reset_index(inplace=True)

# Get a list of all student_numbers for students in high school
high_school_students = course_data[course_data['GradeLevel'] > 8]

# Make sure student_number is a string
high_school_students['student_number'] = high_school_students['student_number'].astype(str)
teacher_grid['student_number'] = teacher_grid['student_number'].astype(str)

# Filter teacher_grid to include only rows for students who are in high school
teacher_grid = teacher_grid[teacher_grid['student_number'].isin(high_school_students['student_number'])]

# Identify columns where all values are 0 after 8th graders are filtered out
teacher_grid_null_columns = teacher_grid.columns[(teacher_grid == 0).all()]

# Drop columns from teacher_grid where all values in the column are 0
teacher_grid = teacher_grid.drop(teacher_grid_null_columns, axis=1)

teacher_grid.head()



#------------------------------------------------------------------------------------
# High school student's unique teachers in 2022
master_teacher = master[['CourseRecordID', 'Teacher1ID']]
membership_teacher = membership[['CourseRecordID', 'student_number']]
school_year = courses.drop_duplicates()
school_year = school_year[['student_number', 'SchoolYear', 'GradeLevel']]

# Merge the data
teacher_year = pd.merge(master_teacher, membership_teacher, on='CourseRecordID', how='outer')
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
print(max_teachers)
# Convert the teacher list into a DataFrame
teacher_df = pd.DataFrame(teacher_list.tolist(), index=teacher_list.index)

# Create column names based on the number of unique teachers
teacher_df.columns = [f'teacher_{i+1}' for i in range(teacher_df.shape[1])]

teacher_df.reset_index(inplace=True)

# Replace NaN values with 0
teacher_df = teacher_df.fillna(0)

teacher_df['student_number'] = teacher_df['student_number'].astype(str)
df['student_number'] = df['student_number'].astype(str)

teacher_df.head()
df = pd.merge(df, teacher_df, on='student_number', how='left')
df.head()


#------------------------------------------------------------------------------------
# Get the current grade level and school for each student. Then dummy code school and grade columns
student_school = pd.merge(membership[['student_number', 'SchoolNumber']],
                          courses[['student_number', 'GradeLevel']],
                          on='student_number',
                          how='left')

student_school = student_school[student_school['GradeLevel'] > 8]
student_school = student_school.sort_values(by=['student_number', 'GradeLevel'])

current_school_grade = student_school.groupby('student_number', as_index=False).agg({
    'GradeLevel': 'max',   # Get the maximum school year
    'SchoolNumber': 'last' # Get the school associated with the latest year
})

current_school_grade = current_school_grade.rename(columns={'GradeLevel': 'current_grade', 'SchoolNumber': 'current_school'})
#current_school_grade = current_school_grade[current_school_grade['current_grade']>8] # Filter to grades > 8 so only grades 9 - 12 and highschools are returned

# Make sure student_number is a string
current_school_grade['student_number'] = current_school_grade['student_number'].astype(str)
df['student_number'] = df['student_number'].astype(str)

# Add current_grade and current_school to the main DataFrame (df)
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
# Get the current years attendance for each student
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

df = pd.merge(df, current_attendance, on='student_number', how='left')


#------------------------------------------------------------------------------------
# Make sure student_number is a string
df['student_number'] = df['student_number'].astype(str)
df = df.fillna(0)

# Define the desired column order
df_columns = [
    'student_number', 'ac_ind', 'ac_count', 'ac_gpa', 'overall_gpa', 
    'current_grade', 'current_school', 'days_attended'
] + [col for col in df.columns if col.startswith('teacher_')]

df = df[df_columns]

df = df.drop_duplicates()

df.head()

# ------------------------------------------------------------------------------------
# Prepare the modeling data by merging grids
# Start with a subset of df 
model_data = df[['student_number', 'ac_ind', 'overall_gpa', 'days_attended']]

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
