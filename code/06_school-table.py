# The code will output two data files: 06_school_exploratory_data.csv and 06_school_modeling_data.csv

import pandas as pd

# Define the years to process
years = [2017, 2018, 2022, 2023, 2024]

# Specify the columns and their corresponding data types for each dataset to speed up the concatenation
membership_columns = {'StudentNumber': 'int32', 'SchoolNumber': 'int16'}
student_table_columns = {'student_number':'int32'}
hs_students_columns = {'student_number': 'int32'}

# Concatenate all years of data for each dataset into single DataFrames
# This combines data from all years to create a complete record of the schools attended by students

# Initialize empty lists to store year-specific DataFrames
all_membership = []
all_student_tables = []
all_hs_students = []

# Loop through each year and load the data and drop duplicates immediatly to clean the data and speed up the loop
for year in years:
    membership_year = pd.read_excel(
        f'data/{year} EOY Data - USU.xlsx', sheet_name='Course Membership', usecols=membership_columns.keys(), dtype=membership_columns
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
    all_student_tables.append(student_table_year[['student_number']])
    all_hs_students.append(hs_students_year[['student_number']])


######################################################################################################################################################
# Concatenate and clean the DataFrames for each dataset across all years
membership = pd.concat(all_membership, ignore_index=True)
student_table = pd.concat(all_student_tables, ignore_index=True)
hs_students = pd.concat(all_hs_students, ignore_index=True)

# Rename column names in membership table
membership = membership.rename(columns={'StudentNumber': 'student_number', 'SchoolNumber': 'school_number'})

# Remove all duplicates from the dataframes after the data is concatenated
membership = membership.drop_duplicates(keep='first')
student_table = student_table.drop_duplicates(keep='first')
hs_students = hs_students.drop_duplicates(keep='first')

####################################################################
# If we decided to filter at the end, all we need to do is change hs_students to student_table
# when creating the df below. The next line is the only line that needs to be adjusted.
####################################################################
# Create the df from the high_school_student student_numbers
# - df: exploratory data
# - model_df: model data
df = hs_students[['student_number']].copy()
model_df = hs_students[['student_number']].copy()

# Merge model_df and the membership table
student_school = pd.merge(model_df, membership, on='student_number', how='left')
student_school.head()


######################################################################################################################################################
# Pivot the merged table to create a grid of student_numbers by school_number
school_grid = student_school.pivot_table(
    index='student_number',
    columns='school_number',
    values='school_number',  # Use school_number to create binary attendance indicators
    aggfunc=lambda x: 1,     # Set 1 to indicate attendance
    fill_value=0             # Fill missing values with 0 to indicate no attendance
)

# Rename the columns to make them more descriptive (i.e. school_[x])
school_grid.columns = [f'school_{int(col)}' for col in school_grid.columns]

# Reset the index to include student_number as a column for merging
school_grid = school_grid.reset_index()

school_grid.head()

# Merge school_grid with the model_df
model_df = pd.merge(model_df, school_grid, on='student_number', how='left')

model_df.head()


######################################################################################################################################################
# Create a list of all the schools a student has attended for the exploratory data
# This will create a column named schools_attended with a list of all the schools students have attended for the exploratory data
student_school_list = (
    student_school.groupby('student_number')['school_number']
    .apply(list)  # Aggregate school_number as a list
    .reset_index()
    .rename(columns={'school_number': 'schools_attended'})
)

# Add a column to count the number of schools attended by each student
student_school_list['school_count'] = school_grid.iloc[:, 1:].sum(axis=1)

# Merge the student_school_list with the df
df = pd.merge(df, student_school_list, on='student_number', how='left')

df.head()


######################################################################################################################################################
# Export the data
df.to_csv('./data/06_school_exploratory_data.csv', index=False)
model_df.to_csv('./data/06_school_modeling_data.csv', index=False)

print('===========================================')
print('School data exported successfully!')
print("Next, run: 07_combine_data-table.py")
print('===========================================')