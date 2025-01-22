import pandas as pd

# Load in the datasets that will be joined later
academic_table = pd.read_csv('data/academic_modeling_data.csv')
demographic_table = pd.read_csv('data/demographic_modeling_data.csv')
assessment_table = pd.read_csv('data/assessment_data.csv')


######################################################################################################################################################
# Initialize empty list to store the student_numbers from the for loop
all_students = []  # this will store the student_numbers from the student_tables
hs_students = []  # this will store the student_numbers from the high_school_students tables

# List of years for which we will process the data
years = [2017, 2018, 2022, 2023, 2024]

# Iterate through each of the student_tables and high_school_student_tables to make a list of all student_numbers across all years
for year in years:
    # Load the student_table_[year] and high_school_students_table_[year]
    # low_memory=False removes the warning for mixed data types
    student_table = pd.read_csv(f'data/student_table_{year}.csv', low_memory=False)
    high_school_student = pd.read_csv(f'data/high_school_students_{year}.csv')
    
    # Add the student_number to the all_students and hs_students list
    all_students.append(student_table[['student_number']])
    hs_students.append(high_school_student[['student_number']])


######################################################################################################################################################
# Concatinate all of the student_numbers from the high_school_students tables into df. Everything will be built by left joining with the df.
####################################################################
# If we decided to filter at the end, all we need to do is change hs_students to all_students 
# when creating the df below. The next line is the only line that needs to be adjusted.
####################################################################
df = pd.concat(hs_students, ignore_index=True)

# We do not want any duplicate student_numbers, so we will drop all duplicates while only keeping the first duplicate.
df = df.drop_duplicates(keep = 'first')

df.head()

# Left join the df with all the datasets from above
# Left join ensures that we keep all students in df, even if they have missing data in other tables.
df = pd.merge(df, academic_table, on='student_number', how='left')
df = pd.merge(df, demographic_table, on='student_number', how='left')
df = pd.merge(df, assessment_table, on='student_number', how='left')

df.head()



######################################################################################################################################################
# Export the data
# df.to_csv('/data/output/model_data.csv', index=False)

