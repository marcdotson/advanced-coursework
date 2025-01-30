# This code compiles all of the modeling and exploratory data into two tables: '07_model_data.csv', '07_exploratory_data.csv'

import pandas as pd
import pickle

# Load in the modeling datasets that will be joined later
# []_model represents modeling files
academic_model = pd.read_csv('data/02_academic_modeling.csv')
demographic_model = pd.read_csv('data/03_demographic_modeling.csv')
assessment_model = pd.read_csv('data/04_assessment_data.csv')
teacher_model = pd.read_csv('data/05_teacher_modeling_data.csv')
school_model = pd.read_csv('data/06_school_modeling_data.csv')

# Load in the exploratory datasets that will be joined later
# []_df represents exploratory files
academic_df = pd.read_csv('data/02_academic_exploratory.csv')
demographic_df = pd.read_csv('data/03_demographic_exploratory.csv')
assessment_df = pd.read_csv('data/04_assessment_data.csv')
teacher_df = pd.read_csv('data/05_teacher_exploratory_data.csv')
school_df = pd.read_csv('data/06_school_exploratory_data.csv')

# Load the pickled data (student_tables)
with open('./data/student_data.pkl', 'rb') as f:
    student_tables, high_school_students_tables = pickle.load(f)

######################################################################################################################################################
# Initialize empty list to store the student_numbers from the for loop
all_students = []  # this will store the student_numbers from the student_tables
hs_students = []  # this will store the student_numbers from the high_school_students tables

# List of years for which we will process the data
years = [2017, 2018, 2022, 2023, 2024]

# Iterate through each of the student_tables and high_school_student_tables to make a list of all student_numbers across all years
for year in years:
    # Load the student_table and high_school_students for the specific year from the pickle data
    student_table = student_tables[year]  # Use the student_tables dictionary
    high_school_student = high_school_students_tables[year]  # Use the high_school_students_tables dictionary
    
    
    # Add the student_number to the all_students and hs_students list
    all_students.append(student_table[['student_number']])
    hs_students.append(high_school_student[['student_number']])


######################################################################################################################################################
# Concatenate all of the student_numbers from the high_school_students tables into the df and model_df. 
# Everything will be built by left joining with the df and model_df.
####################################################################
# If we decided to filter at the end, all we need to do is change hs_students to all_students 
# when creating the df and model_df below. The next two lines are the only lines that needs to be adjusted.
####################################################################
df = pd.concat(hs_students, ignore_index=True)
model_df = pd.concat(hs_students, ignore_index=True)

# We do not want any duplicate student_numbers, so we will drop all duplicates while only keeping the first duplicate.
df = df.drop_duplicates(keep = 'first')
model_df = model_df.drop_duplicates(keep = 'first')

df.head()
model_df.head()

# Left join the model_df with all the datasets from above
# Left join ensures that we keep all students in model_df, even if they have missing data in other tables.
model_df = pd.merge(model_df, academic_model, on='student_number', how='left')
model_df = pd.merge(model_df, demographic_model, on='student_number', how='left')
model_df = pd.merge(model_df, assessment_model, on='student_number', how='left')
model_df = pd.merge(model_df, teacher_model, on='student_number', how='left')
model_df = pd.merge(model_df, school_model, on='student_number', how='left')

model_df.head()

# Left join the df with all the datasets from above
# Left join ensures that we keep all students in df, even if they have missing data in other tables.
df = pd.merge(df, academic_df, on='student_number', how='left')
df = pd.merge(df, demographic_df, on='student_number', how='left')
df = pd.merge(df, assessment_df, on='student_number', how='left')
df = pd.merge(df, teacher_df, on='student_number', how='left')
df = pd.merge(df, school_df, on='student_number', how='left')

# Since df has multiple rows per student, there might be some duplicate rows after all the merges
# Therefore we want to drop duplicate rows and keep the first instance of the duplicate
df = df.drop_duplicates(keep = 'first')

df.head()


######################################################################################################################################################

# TODO: This is where I will add the code to remove columns from the data.

######################################################################################################################################################

# Export the data
df.to_csv('./data/exploratory_data.csv', index=False)
model_df.to_csv('./data/modeling_data.csv', index=False)

print('===========================================')
print('Modeling data exported successfully!')
print('Exploratory data exported successfully!')
print("The workflow is complete!")
print('===========================================')
