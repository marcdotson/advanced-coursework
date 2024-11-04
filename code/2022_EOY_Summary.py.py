import pandas as pd

# Data sheets
student = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Student')
master = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Course Master')
membership = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Course Membership')

# Merge student and course data
student_membership = pd.merge(student, membership, on='StudentNumber', how='left')
full_join = pd.merge(student_membership, master, on='CourseRecordID', how='left')


# Identify advanced courses
advanced_course = full_join[(full_join['CollegeGrantingCr'].notnull()) |
                 (full_join['WhereTaughtCampus'].notnull()) |
                 (full_join['ConcurrEnrolled'] == 'Y') |
                 (full_join['CourseTitle'].str.startswith('AP')) |
                 (full_join['CourseTitle'].str.startswith('BTEC'))]

# if CourseTitle is in the advanced_course list then add a 1 to the new column
full_join['advanced_course'] = full_join['CourseTitle'].apply(lambda x: 1 if x in advanced_course['CourseTitle'].values else 0)
df = full_join[['StudentNumber', 'advanced_course']].copy()


#------------------------------------------------------------------------------------
# Count the ac_ind and create column ac_count
df = full_join.groupby('StudentNumber').agg(
    ac_ind=('advanced_course', lambda x: 1 if x.sum() > 0 else 0),  # if student has at least one '1', else 0
    ac_count=('advanced_course', 'sum')  # Sum of '1's for each student
).reset_index()


#------------------------------------------------------------------------------------
# Get the avg grade for students enrolled in ac and create ac_gpa column
ac_grade = advanced_course[['StudentNumber', 'GradeEarned']].copy()
ac_grade['GradeEarned'] = ac_grade['GradeEarned'].replace({'P': 4.0, 'F': 0.0}) # replace P and F with numbers
ac_grade['GradeEarned'] = pd.to_numeric(ac_grade['GradeEarned'], errors='coerce') # make sure GradeEarned is a numeric value
avg_ac_grade = ac_grade.groupby('StudentNumber')['GradeEarned'].mean().reset_index() # average the grades for each student number
avg_ac_grade.rename(columns={'GradeEarned': 'ac_gpa'}, inplace=True) 
df = pd.merge(df, avg_ac_grade, on='StudentNumber', how='left')
df['ac_gpa'] = df['ac_gpa'].fillna(0)


#------------------------------------------------------------------------------------
# Student Attendance by School and Grade
# 'nan' columns capture attendance when grade data is missing.

courses = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Transcript Courses')
course_year = courses[['StudentNumber', 'GradeLevel']]
school_number = membership[['StudentNumber', 'SchoolNumber']]

# Merge 'school_number' and 'course_year' on 'StudentNumber'
school_data = pd.merge(school_number, course_year, on='StudentNumber', how='left')

#Convert 'SchoolNumber' and 'GradeLevel' to strings
school_data['SchoolNumber'] = school_data['SchoolNumber'].astype(str)
school_data['GradeLevel'] = school_data['GradeLevel'].astype(str)

# Create the 'School_Grade' column with school and grade information, retaining NaNs
school_data['School_Grade'] = 'school_' + school_data['SchoolNumber'] + '_grade_' + school_data['GradeLevel']

# Pivot the data to create a grid for each student, indicating attendance with 1 and non-attendance with 0
school_grid = school_data.pivot_table(
    index='StudentNumber',
    columns='School_Grade',
    values='GradeLevel',
    aggfunc=lambda x: 1,    # Use 1 to indicate attendance
    fill_value=0            # Fill missing values with 0 to indicate no attendance
)

school_grid.columns = school_grid.columns.str.replace(r'\.0', '', regex=True)
school_grid.reset_index(inplace=True)
school_grid = school_grid.drop(columns=['School_Grade'], errors='ignore')

# Merge the school grid with the main DataFrame 'df' on 'StudentNumber'
df = pd.merge(df, school_grid, on='StudentNumber', how='left')


#------------------------------------------------------------------------------------
# Student's Unique Teachers in 2022
# This script provides options for including all students or only those in grades > 8.
# It also allows adjustment to display either the maximum number of unique teachers per student or limit to 14 teachers. 
teacher_year = full_join[['StudentNumber', 'Teacher1ID']]
school_year = courses[['StudentNumber', 'SchoolYear']]
teacher_join = pd.merge(school_year, teacher_year, on='StudentNumber', how='left')
teacher_2022 = teacher_join[teacher_join['SchoolYear'] == 2022]

# Optional filter to include only students in grades above 8
#teacher_2022 = teacher_join[teacher_join['GradeLevel'] > 8]

teacher_2022 = teacher_2022.drop_duplicates(subset=['StudentNumber', 'Teacher1ID'])
teacher_counts = teacher_2022.groupby('StudentNumber')['Teacher1ID'].nunique()
teacher_list = teacher_2022.groupby('StudentNumber')['Teacher1ID'].apply(list)

# Determine the maximum number of unique teachers any student had in 2022
# max_teachers = 22
max_teachers = teacher_counts.max()
teacher_df = pd.DataFrame(teacher_list.tolist(), index=teacher_list.index)

# Adjust the number of teacher columns per student:
teacher_df.columns = [f'teacher_{i+1}' for i in range(max_teachers)] # Includes all unique teachers per student
#teacher_df.columns = [f'Teacher{i+1}' for i in range(14)] # Limit to 14 teachers per student
teacher_df.reset_index(inplace=True)

df = pd.merge(df, teacher_df, on='StudentNumber', how='left')


#------------------------------------------------------------------------------------
# Get the current grade level and school for each student
student_school = pd.merge(membership[['StudentNumber', 'SchoolNumber']], 
                          courses[['StudentNumber', 'SchoolYear']], 
                          on='StudentNumber', 
                          how='left')

current_school_grade = student_school.groupby('StudentNumber', as_index=False).agg({
    'SchoolYear': 'max',           # Get the maximum school year
    'SchoolNumber': 'last'         # Get the school associated with the latest year
})
current_school_grade = current_school_grade.rename(columns={'SchoolYear': 'current_grade', 'SchoolNumber': 'current_school'})

current_school_grade.head()
df = pd.merge(df, current_school_grade[['StudentNumber', 'current_grade', 'current_school']], on='StudentNumber', how='left')


#------------------------------------------------------------------------------------
# Get the current years attendance for each student
student_attendance = student[['StudentNumber', 'GradeLevel', 'DaysAttended']]

# Group by 'StudentNumber' to get the maximum 'GradeLevel' and corresponding 'DaysAttended'
current_attendance = student_attendance.groupby('StudentNumber', as_index=False).agg({
    'GradeLevel': 'max',           # Get the maximum GradeLevel
    'DaysAttended': 'last'         # Get the days attended associated with the max GradeLevel
})

current_attendance = current_attendance.rename(columns={'DaysAttended': 'days_attended'})

current_attendance = current_attendance[['StudentNumber', 'days_attended']]

df = pd.merge(df, current_attendance, on='StudentNumber', how='left')


#------------------------------------------------------------------------------------
# Reorder columns in df
final_columns = [
    'StudentNumber', 'ac_ind', 'ac_count', 'ac_gpa', 'current_grade', 'current_school', 'days_attended', 
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
] + [col for col in df.columns if col.startswith('teacher_')]

df = df.reindex(columns=final_columns)
df=df.fillna(0)


df.to_csv('2022_EOY_Summary.csv', index=False)