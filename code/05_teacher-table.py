# The code will output two data files: 05_teacher_exploratory_data.csv and 05_teacher_modeling_data.csv

import pandas as pd

# Define the years to process
years = [2017, 2018, 2022, 2023, 2024]

# Specify the columns and their corresponding data types for each dataset to speed up the concatenation
membership_columns = {'StudentNumber': 'int32', 'CourseRecordID': 'string'}
master_columns = {'Teacher1ID': 'int32', 'CourseRecordID': 'string'}
student_table_columns = {'student_number':'int32'}
hs_students_columns = {'student_number': 'int32'}

# Concatenate all years of data for each dataset into single DataFrames
# This combines data from all years to create a complete record of the teachers had by students

# Initialize empty lists to store year-specific DataFrames
all_membership = []
all_master = []
all_student_tables = []
all_hs_students = []

# Loop through each year and load the data and drop duplicates immediatly to clean the data and speed up the loop
for year in years:
    membership_year = pd.read_excel(
        f'data/{year} EOY Data - USU.xlsx', sheet_name='Course Membership', usecols=membership_columns.keys(), dtype=membership_columns
        ).drop_duplicates()
    
    master_year = pd.read_excel(
    f'data/{year} EOY Data - USU.xlsx', sheet_name='Course Master', usecols=master_columns.keys(),dtype=master_columns
    ).drop_duplicates()

    # low_memory=False removes the warning for mixed data types
    student_table_year = pd.read_csv(
        f'data/01_student_table_{year}.csv', usecols=student_table_columns.keys(), dtype=student_table_columns, low_memory=False
        ).drop_duplicates()
    
    # low_memory=False removes the warning for mixed data types
    hs_students_year = pd.read_csv(
        f'data/01_high_school_students_{year}.csv', usecols=hs_students_columns.keys(), dtype=hs_students_columns, low_memory=False
        ).drop_duplicates()

    # Append year-specific data to the respective lists
    all_membership.append(membership_year)
    all_master.append(master_year)
    all_student_tables.append(student_table_year[['student_number']])
    all_hs_students.append(hs_students_year[['student_number']])


######################################################################################################################################################
# Concatenate and clean the DataFrames for each dataset across all years
membership = pd.concat(all_membership, ignore_index=True)
master = pd.concat(all_master, ignore_index=True)
student_table = pd.concat(all_student_tables, ignore_index=True)
hs_students = pd.concat(all_hs_students, ignore_index=True)

# Rename column names in membership table
membership = membership.rename(columns={'StudentNumber': 'student_number', 'CourseRecordID': 'course_record_id'})
master = master.rename(columns={'Teacher1ID': 'teacher_id', 'CourseRecordID': 'course_record_id'})


# Remove all duplicates from the dataframes after the data is concatinated
membership = membership.drop_duplicates(keep='first')
master = master.drop_duplicates(keep='first')
student_table = student_table.drop_duplicates(keep='first')
hs_students = hs_students.drop_duplicates(keep='first')


######################################################################################################################################################
# Merge the different tables to prepare for the pivot
teacher_student = pd.merge(membership, master, on='course_record_id', how='left')

####################################################################
# If we decided to filter at the end, all we need to do is change hs_students to student_table
# when creating the df below. The next line is the only line that needs to be adjusted.
####################################################################
# Create the df from the high_school_student student_numbers
# - df: exploratory data
# - model_df: model data
df = hs_students[['student_number']].copy()
model_df = hs_students[['student_number']].copy()

# Left join model_df and teacher_student so we only have student_numbers from the model_df
# Only include the student_number and teacher_id from the teacher_student table
teacher_student = pd.merge(model_df, teacher_student[['student_number', 'teacher_id']], on='student_number', how='left')


######################################################################################################################################################
# Pivot the merged table to create a grid of student_numbers by school_number
teacher_grid = teacher_student.pivot_table(
    index='student_number',
    columns='teacher_id',
    values='teacher_id',  # Use teacher_id to create binary attendance indicators
    aggfunc=lambda x: 1,     # Set 1 to indicate a student has taken a class from a teacher
    fill_value=0             # Fill missing values with 0 to indicate no attendance
)

# Rename the columns to make them more descriptive (i.e. school_[x])
teacher_grid.columns = [f'teacher_{int(col)}' for col in teacher_grid.columns]

# Reset the index to include student_number as a column for merging
teacher_grid = teacher_grid.reset_index()

teacher_grid.head()

# Add a column to count the number of teachers each student had
teacher_grid['teacher_count'] = teacher_grid.iloc[:, 1:].sum(axis=1)

# Merge teacher_grid with the model_df
model_df = pd.merge(model_df, teacher_grid, on='student_number', how='left')

model_df.head()


######################################################################################################################################################
# Create a list of all the teachers a student has had for the exploratory data
# This will create a column named teachers_had with a list of all the teachers a student has had for the exploratory data
student_teacher_list = (
    teacher_student.groupby('student_number')['teacher_id']
    .apply(list)  # Aggregate school_number as a list
    .reset_index()
    .rename(columns={'teacher_id': 'teachers_had'})
)

# Merge the school_count column into the exploratory data (student_teacher_list)
student_teacher_list = pd.merge(
    student_teacher_list, teacher_grid[['student_number', 'teacher_count']], on='student_number', how='left')

# Merge the student_school_list with the df
df = pd.merge(df, student_teacher_list, on='student_number', how='left')

df.head()


######################################################################################################################################################
# Export the data
df.to_csv('./data/05_teacher_exploratory_data.csv', index=False)
model_df.to_csv('./data/05_teacher_modeling_data.csv', index=False)

print('Teacher data exported successfully!')