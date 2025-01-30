###########################################################################
# The code will output a single pickle file containing all student tables: student_data.pkl
# This file includes two dictionaries:
# 1. student_tables:
#    - A dictionary where:
#      - Keys: Years (e.g., 2017, 2018, 2022, etc.).
#      - Values: DataFrames containing the full student table for each year.
#    - Example: student_tables[2017] provides the full student table for 2017.
# 2. high_school_students_tables:
#    - A dictionary where:
#      - Keys: Years (e.g., 2017, 2018, 2022, etc.).
#      - Values: DataFrames containing only high school students for each year.
#    - Example: high_school_students_tables[2017] provides the high school student table for 2017.
#############################################################################
# TODO: Decide on how to filter for high school students only at the end of the data
# The code currently uses high_school_students_tables for processing.
# If filtering is moved to the end instead of the beginning, only 1-2 lines of code per script would need to be adjusted.
#############################################################################

import pandas as pd
import pickle

##########################################################################################################################################################
# Columns to drop if they exist in the student_table. Some years are missing columns.
# Not all the columns below exist in every year
columns_to_drop = [
    "ExitDate", "ResidentStatus", "KindergartenType", "EarlyGrad", "ReadGradeLevelFall", 
    "ReadGradeLevelSpring", "Biliteracy1Level", "Biliteracy1Language", "Biliteracy2Level",
    "Biliteracy2Language", "EarlyNumeracyStatusBOY", "EarlyNumeracyStatusMOY", 
    "EarlyNumeracyStatusEOY", "EarlyNumeracyIntervention"
]

# List of years to process
years = [2017, 2018, 2022, 2023, 2024]

# Initialize dictionaries to store tables for all years
student_tables = {} # Stores all students for each year
high_school_students_tables = {} # Stores high school students for each year

# Start the for loop
for year in years:
    # Load the Excel file for the specific year
    file_path = f'data/{year} EOY Data - USU.xlsx'
    student = pd.read_excel(file_path, sheet_name='Student')

    # Rename 'StudentNumber' to 'student_number' in all tables that contain 'student_number'
    student = student.rename(columns={'StudentNumber': 'student_number'})


    ##########################################################################################################################################################
    # Filter the student table down to 1 row per student. This will make everything easier moving forward
    # This is handling one year of data at a time, so this is filtering to one student_number per year

    # Drop the columns from the list above. If the data does not contain that column ignore the error and continue.
    student_table = student.drop(columns=[col for col in columns_to_drop if col in student.columns], errors='ignore')

    # Drop rows with null or empty student_numbers
    student_table.dropna(subset=['student_number'], inplace=True)

    # Drop duplicate student_numbers but keep the row with the largest GradeLevel
    student_table = student_table.loc[student_table.groupby('student_number')['GradeLevel'].idxmax()].reset_index(drop=True)


    ##########################################################################################################################################################
    # Create a table that contains all the columns as the student_table but only includes student_numbers for high school students.
    # Ensure GradeLevel is numeric
    student_table['GradeLevel'] = pd.to_numeric(student_table['GradeLevel'], errors='coerce')

    # Filter the student_table to only include student_numbers for students in grades > 8
    high_school_students = student_table[student_table['GradeLevel'] > 8].copy()

    student_table.head()
    high_school_students.head()


    ##########################################################################################################################################################
    # Add the processed tables to their respective dictionaries
    student_tables[year] = student_table
    high_school_students_tables[year] = high_school_students


##########################################################################################################################################################
# Save the dictionaries into a single pickle file (student_data.pkl)
# 'wb' opens the file in binary write mode (required for pickle).
# 'as f' assigns the file object to 'f' for use within the block.
# pickle.dump((student_tables, high_school_students_tables), f) saves the two dictionaries 
with open('./data/student_data.pkl', 'wb') as f:
    pickle.dump((student_tables, high_school_students_tables), f)

print('===========================================')
print("Student tables exported successfully!")
print("Next, run: 02_academic-table.py")
print('===========================================')
