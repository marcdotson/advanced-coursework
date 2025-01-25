###########################################################################
# Start here!
###########################################################################
# The code will output two data files per year: 01_student_table_[year].csv and 01_high_school_students_[year].csv

import pandas as pd
import numpy as np

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

# Start the for loop
for year in years:
    # Load the Excel file for the specific year
    file_path = f'data/{year} EOY Data - USU.xlsx'
    student = pd.read_excel(file_path, sheet_name='Student')

    # Rename 'StudentNumber' to 'student_number' in all tables that contain 'student_number'
    student = student.rename(columns={'StudentNumber': 'student_number'})

#############################################################################
# Filter at the end of all of the data wrangling?
#############################################################################

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
    # Export both tables for the specific year
    student_table.to_csv(f'./data/01_student_table_{year}.csv', index=False)
    high_school_students.to_csv(f'./data/01_high_school_students_{year}.csv', index=False)

print('===========================================')
print("Student tables exported successfully!")
print("Next, run: 02_academic-table.py")
print('===========================================')
