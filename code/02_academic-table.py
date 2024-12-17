import pandas as pd
import numpy as np

# Data sheets
master = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Course Master')
membership = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Course Membership')

# Rename 'StudentNumber' to 'student_number'
membership = membership.rename(columns={'StudentNumber': 'student_number'})

# Import student_table and high_school_student (for now)
student_table = pd.read_csv('data/student_table.csv')
high_school_students = pd.read_csv('data/high_school_students.csv')


###########################################################################
# df will represent the exploratory data, and model_df will represent the model data
# If we decided to filter at the end, all we need to do is change high_school_students to student_table when creating the df's below

# Create the df from the high_school_student student_numbers
df = high_school_students[['student_number']]

# Create the model_df from the high_school_student student_numbers
model_df = high_school_students[['student_number']]


######################################################################################################################################################
# Determine if a class is an advanced course, determine if a student has taken an ac (ac_ind)
# and count the number of ac classes a student has taken (ac_count).
# df will include all new columns while model_df will only include ac_ind

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

# Dropping any duplicate rows from advanced_summary just in case any remain.
advanced_summary = advanced_summary.drop_duplicates()

# Make sure student_number is a string
advanced_summary['student_number'] = advanced_summary['student_number'].astype(str)
df['student_number'] = df['student_number'].astype(str)
model_df['student_number'] = model_df['student_number'].astype(str)

# Add ac_ind to model_df
model_df = pd.merge(model_df, advanced_summary[['student_number','ac_ind']], on='student_number', how='left')

# Add the advanced_summary data to the df
df = pd.merge(df, advanced_summary, on='student_number', how='left')

# Fill null values with 0
df[['ac_ind', 'ac_count']] = df[['ac_ind', 'ac_count']].fillna(0)
model_df['ac_ind'] = model_df['ac_ind'].fillna(0)

df.head()
model_df.head()


######################################################################################################################################################
# Calculate students gpa in advanced courses (ac_gpa)
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


######################################################################################################################################################
# Function to process numeric and date columns from the student table
# SchoolMemebership tracks the number of days a student was enrolled in the school
# There are quite a few students with a student_membership of 0 but with good attendance.
# All of the data will be left joined with the df and model_df, therefore we can use the student_table

def process_numeric_student_columns(student_table, model_df, df, columns, rename_map):
    """
    Processes numeric columns from the student sheet, renames them, 
    and merges them into the model_df and df DataFrames.

    Parameters:
    - student_table (pd.DataFrame): DataFrame containing student data.
    - model_df (pd.DataFrame): DataFrame to merge the processed columns into.
    - df (pd.DataFrame): Another DataFrame to merge the processed columns into.
    - columns (list): List of columns to process and merge, including 'student_number'.
    - rename_map (dict): Dictionary mapping original column names to their new names.

    Returns:
    - model_df (pd.DataFrame): Updated model_df with the renamed columns merged.
    - df (pd.DataFrame): Updated df with the renamed columns merged.
    """
    # Ensure 'student_number' is in the list of columns
    if 'student_number' not in columns:
        columns.insert(0, 'student_number')
    
    # Copy the required columns
    selected_table = student_table[columns].copy()
    
    # Rename columns
    selected_table = selected_table.rename(columns=rename_map)
    
    # Ensure student_number is a string in all DataFrames
    selected_table['student_number'] = selected_table['student_number'].astype(str)
    model_df['student_number'] = model_df['student_number'].astype(str)
    df['student_number'] = df['student_number'].astype(str)
    
    # Merge into model_df
    model_df = pd.merge(model_df, selected_table, on='student_number', how='left')
    
    # Merge into df
    df = pd.merge(df, selected_table, on='student_number', how='left')
    
    return model_df, df

# Columns to process from the student_table
columns_to_process = ['DaysAttended', 'CumulativeGPA', 'SchoolMembership', 'ExcusedAbsences', 'UnexcusedAbsences', 'AbsencesDueToSuspension']

# Specify the columns to process and rename
rename_map = {
    'DaysAttended': 'days_attended',
    'CumulativeGPA': 'overall_gpa',
    'SchoolMembership': 'school_membership',
    'ExcusedAbsences': 'excused_absences',
    'UnexcusedAbsences': 'unexcused_absences',
    'AbsencesDueToSuspension': 'absences_due_to_suspension'
}
model_df, df = process_numeric_student_columns(student_table, model_df, df, columns_to_process, rename_map)


######################################################################################################################################################
# Prepare the data for export
# Specify the column order for the df
df_columns = ['student_number', 'ac_ind', 'ac_count', 'ac_gpa', 'overall_gpa', 'days_attended', 
            'excused_absences', 'unexcused_absences', 'absences_due_to_suspension', 'school_membership']

df = df[df_columns]

# Specify the column order for the model_df
model_columns = ['student_number', 'ac_ind', 'overall_gpa', 'days_attended', 
                'excused_absences', 'unexcused_absences', 'absences_due_to_suspension', 'school_membership']

model_df = model_df[model_columns]

df.head()
model_df.head()

# Export both files
df.to_csv('./data/academic_exploratory_data.csv', index=False)
model_df.to_csv('./data/academic_modeling_data.csv', index=False)