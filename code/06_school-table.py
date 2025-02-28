# The code will output two data files: 06_school_exploratory_data.csv and 06_school_modeling_data.csv

import pandas as pd
import pickle

# Define the years to process
# years = [2017, 2018, 2022, 2023, 2024]

# Post Covid years
years = [2022, 2023, 2024]

# Specify the columns and their corresponding data types for each dataset to speed up the concatenation
membership_columns = {'StudentNumber': 'int32', 'SchoolNumber': 'int16'}

# Load the pickled data (student_tables)
with open('./data/student_data.pkl', 'rb') as f:
    student_tables = pickle.load(f)

# Concatenate all years of data for each dataset into single DataFrames
# This combines data from all years to create a complete record of the schools attended by students

# Initialize empty lists to store year-specific DataFrames
all_membership = []
all_student_tables = []

# Loop through each year and load the data and drop duplicates immediatly to clean the data and speed up the loop
for year in years:
    membership_year = pd.read_excel(
        f'data/{year} EOY Data - USU.xlsx', sheet_name='Course Membership', usecols=membership_columns.keys(), dtype=membership_columns
        ).drop_duplicates()
    
    # Retrieve the data for the specified year from the student_tables dictionary
    student_table_year = student_tables[year]

    # Assign the year to student_table_year table
    # I will later use this to join with students current school, to make sure data is accurate on yearly basis
    student_table_year['year'] = year  
    membership_year['year'] = year

    # Ensure year is an integer
    student_table_year['year'] = student_table_year['year'].astype(int)
    membership_year['year'] = membership_year['year'].astype(int)

    # Append year-specific data to the respective lists
    all_membership.append(membership_year)
    all_student_tables.append(student_table_year[['student_number', 'year']])


######################################################################################################################################################
# Concatenate and clean the DataFrames for each dataset across all years
membership = pd.concat(all_membership, ignore_index=True)
student_table = pd.concat(all_student_tables, ignore_index=True)
student_current_school = pd.concat(all_student_tables, ignore_index=True) # I will use this to create the df

# Rename column names in membership table
membership = membership.rename(columns={'StudentNumber': 'student_number', 'SchoolNumber': 'school_number'})

# We can drop the year column from the student_table as it is not needed in the modeling data
student_table = student_table.drop(columns=['year'])

# Remove all duplicates from the dataframes after the data is concatenated
membership = membership.drop_duplicates(keep='first')
student_table = student_table.drop_duplicates(keep='first')

# I want to keep one student_number per year so we can track students current_school
student_current_school = student_current_school.drop_duplicates(subset=['student_number', 'year'], keep='first')

# Create the df from the student_table and student_current_school student_numbers
# - df: exploratory data (created from the student_current_school)
# - model_df: model data (created from student_table)
df = student_current_school[['student_number', 'year']].copy()
model_df = student_table[['student_number']].copy()

# Merge model_df and the membership table
student_school = pd.merge(model_df, membership, on='student_number', how='left')

student_school.head()


######################################################################################################################################################
# Count the number of times each school is attended per student per year
# Because the data might indicate that a student attended multiple schools per year (if they took a course at another school)
# I will count the number of times a student 
# attended a school for each year, then I will keep the row with the max 'school_count' per year.
school_counts = (
    membership.groupby(['student_number', 'year', 'school_number'])
    .size()  # Count occurrences
    .reset_index(name='school_count')  # Rename the count column
)

# Rename school_number to current_school
school_counts = school_counts.rename(columns={'school_number': 'current_school'})

# Find the school with the maximum count per student per year
max_school_count = school_counts.loc[
    school_counts.groupby(['student_number', 'year'])['school_count'].idxmax()
]

# Drop the school_count column as it counts schools by students per year. 
# Later I will calculate the number of schools a student has attended in ccsd(not by year).
max_school_count.drop(columns=['school_count'], inplace=True)

# Merge max_school_count with the df
df = pd.merge(df, max_school_count, on=['student_number', 'year'], how='left')

df.head()

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

# Fill all null values with 0.
# The null values arise because there are some (290) students_numbers who do not have any recorded school_numbers in the membership table.
model_df.fillna(0, inplace=True)
df.fillna(0, inplace=True)


######################################################################################################################################################
# Export the data
df.to_csv('./data/06_school_exploratory_data.csv', index=False)
model_df.to_csv('./data/06_school_modeling_data.csv', index=False)

print('===========================================')
print('School data exported successfully!')
print("Next, run: 07_combine_data-table.py")
print('===========================================')
