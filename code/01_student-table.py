###########################################################################
# The code will output a single pickle file containing all student tables: student_data.pkl
# This file includes two dictionaries:
# 1. student_tables:
#    - A dictionary where:
#      - Keys: Years (e.g., 2017, 2018, 2022, etc.).
#      - Values: DataFrames containing the full student table for each year.
#    - Example: student_tables[2017] provides the full student table for 2017.

#======================================================
# Filtering has been moved back to the begining of the process
# IsOnePercent = Y has been filtered out of the data.
#======================================================

import pandas as pd
import pickle

# List of years to process
years = [2017, 2018, 2022, 2023, 2024, 2025]

##########################################################################################################################################################
# Columns to drop if they exist in the student_table. Some years are missing columns.
# Not all the columns below exist in every year
columns_to_drop = [
    "ExitDate", "ResidentStatus", "KindergartenType", "EarlyGrad", "ReadGradeLevelFall", 
    "ReadGradeLevelSpring", "Biliteracy1Level", "Biliteracy1Language", "Biliteracy2Level",
    "Biliteracy2Language", "EarlyNumeracyStatusBOY", "EarlyNumeracyStatusMOY", 
    "EarlyNumeracyStatusEOY", "EarlyNumeracyIntervention"
]

# Initialize dictionaries to store tables for all years
student_tables = {} # Stores all students for each year

# Start the for loop
for year in years:
    # Load the Excel file for the specific year
    file_path = f'data/{year} EOY Data - USU.xlsx'
    student = pd.read_excel(file_path, sheet_name='Student')
    # Load the scram data to filter out IsOnePercent = Y
    scram = pd.read_excel(file_path, sheet_name='SCRAM')
    
    # Rename 'StudentNumber' to 'student_number' in all tables that contain 'student_number'
    student = student.rename(columns={'StudentNumber': 'student_number'})
    scram = scram.rename(columns={'StudentNumber': 'student_number'})

    ##########################################################################################################################################################
    # Filter the student table down to 1 row per student. This will make everything easier moving forward
    # This is handling one year of data at a time, so this is filtering to one student_number per year

    # Drop the columns from the list above. If the data does not contain that column ignore the error and continue.
    student_table = student.drop(columns=[col for col in columns_to_drop if col in student.columns], errors='ignore')
    
    # Create a table with student_number and IsOnePercent from the scram data
    scram_filter = scram[['student_number', 'IsOnePercent']].copy()

    # Merge the student table and the scram_filter table
    student_table = pd.merge(student_table, scram_filter, on='student_number', how='left')
    
    # Drop rows from student_table where IsOnePercent is NOT null. 
    # This column contains only 'Y' or null, so removing all non-null values accounts for any potential data entry inconsistencies.
    student_table = student_table[student_table['IsOnePercent'].isna()]

    # Now that we have filtered out IsOnePercent we can drop this column from the student_table
    student_table = student_table.drop(columns=['IsOnePercent'])

    # Ensure GradeLevel is numeric
    student_table['GradeLevel'] = pd.to_numeric(student_table['GradeLevel'], errors='coerce')

    # Drop rows with null or empty student_numbers and GradeLevels
    student_table.dropna(subset=['student_number'], inplace=True)
    student_table = student_table.dropna(subset=['GradeLevel'])

    # Make sure GradeLevel is an int
    student_table['GradeLevel'] = student_table['GradeLevel'].astype(int)

    # Drop duplicate student_numbers but keep the row with the largest GradeLevel
    student_table = student_table.loc[student_table.groupby('student_number')['GradeLevel'].idxmax()].reset_index(drop=True)

    # Filter out students that are not in high school
    student_table = student_table[student_table['GradeLevel'] > 8]

    ##########################################################################################################################################################
    # Add the processed tables to their respective dictionaries
    student_tables[year] = student_table

##########################################################################################################################################################
# Save the dictionaries into a single pickle file (student_data.pkl)
# 'wb' opens the file in binary write mode (required for pickle)
# 'as f' assigns the file object to 'f' for use within the block
# pickle.dump((student_tables), f) saves the dictionary 
with open('./data/student_data.pkl', 'wb') as f:
    pickle.dump((student_tables), f)

print('===========================================')
print("Student tables exported successfully!")
print("Next, run: 02_academic-table.py")
print('===========================================')
