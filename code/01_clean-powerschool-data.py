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


# Merge student and course data
student_membership = pd.merge(student, membership, on='student_number', how='left')
full_join = pd.merge(student_membership, master, on='CourseRecordID', how='left')


# Identify advanced courses
advanced_course = full_join[(full_join['CollegeGrantingCr'].notnull()) |
                 (full_join['WhereTaughtCampus'].notnull()) |
                 (full_join['ConcurrEnrolled'] == 'Y') |
                 (full_join['CourseTitle'].str.startswith('AP')) |
                 (full_join['CourseTitle'].str.startswith('BTEC'))]

# if CourseTitle is in the advanced_course list then add a 1 to the new column
full_join['advanced_course'] = full_join['CourseTitle'].apply(lambda x: 1 if x in advanced_course['CourseTitle'].values else 0)
df = full_join[['student_number', 'advanced_course']].copy()


#------------------------------------------------------------------------------------
# Count the ac_ind and create column ac_count
df = full_join.groupby('student_number').agg(
    ac_ind=('advanced_course', lambda x: 1 if x.sum() > 0 else 0),  # if student has at least one '1', else 0
    ac_count=('advanced_course', 'sum')  # Sum of '1's for each student
).reset_index()


#------------------------------------------------------------------------------------
# Get the avg grade for students enrolled in ac and create ac_gpa column for exploratory analysis
ac_grade = advanced_course[['student_number', 'GradeEarned']].copy()
ac_grade['GradeEarned'] = ac_grade['GradeEarned'].replace({'P': 4.0, 'F': 0.0}) # replace P and F with numbers
ac_grade['GradeEarned'] = pd.to_numeric(ac_grade['GradeEarned'], errors='coerce') # make sure GradeEarned is a numeric value
avg_ac_grade = ac_grade.groupby('student_number')['GradeEarned'].mean().reset_index() # average the grades for each student number
avg_ac_grade.rename(columns={'GradeEarned': 'ac_gpa'}, inplace=True) 
df = pd.merge(df, avg_ac_grade, on='student_number', how='left')
df['ac_gpa'] = df['ac_gpa'].fillna(0)


#------------------------------------------------------------------------------------
# Student Attendance by School and Grade for the model
# 'nan' columns capture attendance when grade data is missing.

course_year = courses[['student_number', 'GradeLevel']]
school_number = membership[['student_number', 'SchoolNumber']]

# Merge 'school_number' and 'course_year' on 'student_number'
school_data = pd.merge(school_number, course_year, on='student_number', how='left')

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

# Drop 'School_Grade' now that it's captured in pivot columns
school_grid = school_grid.drop(columns=['School_Grade'], errors='ignore')

# Reorder the columns
grid_columns = [
    'student_number',
    'school_710_grade_8', 'school_710_grade_9', 'school_710_grade_10', 'school_710_grade_11', 'school_710_grade_12', 'school_710_grade_nan',
    'school_706_grade_8', 'school_706_grade_9', 'school_706_grade_10', 'school_706_grade_11', 'school_706_grade_12', 'school_706_grade_nan',
    'school_705_grade_9', 'school_705_grade_10', 'school_705_grade_11', 'school_705_grade_12', 'school_705_grade_nan',
    'school_703_grade_8', 'school_703_grade_9', 'school_703_grade_10', 'school_703_grade_11', 'school_703_grade_12', 'school_703_grade_nan',
    'school_702_grade_8', 'school_702_grade_9', 'school_702_grade_10', 'school_702_grade_11', 'school_702_grade_12', 'school_702_grade_nan',
    'school_330_grade_9', 'school_330_grade_nan', 
    'school_106_grade_nan', 'school_109_grade_nan', 'school_111_grade_nan', 'school_118_grade_nan', 
    'school_120_grade_nan', 'school_124_grade_nan', 'school_128_grade_nan', 'school_130_grade_nan', 
    'school_132_grade_nan', 'school_140_grade_nan', 'school_144_grade_nan', 'school_152_grade_nan', 
    'school_156_grade_nan', 'school_160_grade_nan', 'school_164_grade_nan', 'school_166_grade_nan', 
    'school_170_grade_nan', 'school_406_grade_nan', 'school_410_grade_nan', 'school_600_grade_nan'
]

school_grid = school_grid.reindex(columns=grid_columns)

school_grid.head()


#------------------------------------------------------------------------------------
# Student's Teacher by TeacherID and Grade for the model
# 'nan' columns capture attendance when grade data is missing.

course_data = courses[['student_number', 'GradeLevel']]
membership_data = membership[['student_number', 'CourseRecordID']]
master_data = master[['CourseRecordID', 'Teacher1ID']]

# Merge master and membership on 'CourseRecordID' to get Teacher1ID per student
teacher_membership = pd.merge(membership_data, master_data, on='CourseRecordID', how='left')

# Merge with courses on 'student_number' to add GradeLevel
teacher_data = pd.merge(teacher_membership, course_data, on='student_number', how='left')

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

# Drop 'Teacher_Grade' now that it's captured in pivot columns
teacher_grid = teacher_grid.drop(columns=['Teacher_Grade'], errors='ignore')

# Display the resulting teacher grid
teacher_grid.head()


#------------------------------------------------------------------------------------
# Student's Unique Teachers in 2022
# This script provides options for including all students or only those in grades > 8.
# It also allows adjustment to display either the maximum number of unique teachers per student or limit to 14 teachers. 
teacher_year = full_join[['student_number', 'Teacher1ID']]
school_year = courses[['student_number', 'SchoolYear', 'GradeLevel']]
teacher_join = pd.merge(school_year, teacher_year, on='student_number', how='left')
teacher_2022 = teacher_join[teacher_join['SchoolYear'] == 2022]

teacher_2022 = teacher_2022.drop_duplicates(subset=['student_number', 'Teacher1ID'])
teacher_counts = teacher_2022.groupby('student_number')['Teacher1ID'].nunique()
teacher_list = teacher_2022.groupby('student_number')['Teacher1ID'].apply(list)

# Determine the maximum number of unique teachers any student had in 2022
# max_teachers = 22
max_teachers = teacher_counts.max()
teacher_df = pd.DataFrame(teacher_list.tolist(), index=teacher_list.index)

# Adjust the number of teacher columns per student:
teacher_df.columns = [f'teacher_{i+1}' for i in range(max_teachers)] # Includes all unique teachers per student
#teacher_df.columns = [f'Teacher{i+1}' for i in range(14)] # Limit to 14 teachers per student
teacher_df.reset_index(inplace=True)

df = pd.merge(df, teacher_df, on='student_number', how='left')


#------------------------------------------------------------------------------------
# Get the current grade level and school for each student
student_school = pd.merge(membership[['student_number', 'SchoolNumber']], 
                          courses[['student_number', 'GradeLevel']], 
                          on='student_number', 
                          how='left')

current_school_grade = student_school.groupby('student_number', as_index=False).agg({
    'GradeLevel': 'max',           # Get the maximum school year
    'SchoolNumber': 'last'         # Get the school associated with the latest year
})
current_school_grade = current_school_grade.rename(columns={'GradeLevel': 'current_grade', 'SchoolNumber': 'current_school'})

df = pd.merge(df, current_school_grade, on='student_number', how='left')


#------------------------------------------------------------------------------------
# Get the current years attendance for each student
student_attendance = student[['student_number', 'GradeLevel', 'DaysAttended']]

# Group by 'student_number' to get the maximum 'GradeLevel' and corresponding 'DaysAttended'
current_attendance = student_attendance.groupby('student_number', as_index=False).agg({
    'GradeLevel': 'max',           # Get the maximum GradeLevel
    'DaysAttended': 'last'         # Get the days attended associated with the max GradeLevel
})

current_attendance = current_attendance.rename(columns={'DaysAttended': 'days_attended'})

current_attendance = current_attendance[['student_number', 'days_attended']]

df = pd.merge(df, current_attendance, on='student_number', how='left')


#------------------------------------------------------------------------------------
# Order df columns and merge school_grid, and teacher_grid 
df_columns = [
    'student_number', 'ac_ind', 'ac_count', 'ac_gpa', 'current_grade', 'current_school', 'days_attended'
] + [col for col in df.columns if col.startswith('teacher_')]
df = df[df_columns]
df.head()
df = pd.merge(df, school_grid, on='student_number', how='left')
df = pd.merge(df, teacher_grid, on='student_number', how='left')

# Filter to include only students in grades above 8
teacher_2022 = teacher_join[teacher_join['GradeLevel'] > 8]
df = df[df['current_grade']>8]
df = df.fillna(0)
df.head()

#------------------------------------------------------------------------------------
#Export dataframe to CSV
df.to_csv('./data/01_cleaned_powerschool_data.csv', index=False)
