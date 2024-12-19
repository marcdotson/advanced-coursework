# The code will output two data files: student_table.csv and high_school_students.csv

import pandas as pd
import numpy as np

# Data sheets
student = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Student')

# Rename 'StudentNumber' to 'student_number' in all tables that contain 'student_number'
student = student.rename(columns={'StudentNumber': 'student_number'})

#############################################################################
# Filter at the end of all of the data wrangling?
#############################################################################

##########################################################################################################################################################
# Filter the student table down to 1 row per student. This will make everything easier moving forward
# Drop columns that we do not need.
student_columns_to_drop = [
    "ExitDate", "ResidentStatus", "KindergartenType", "EarlyGrad", "ReadGradeLevelFall", 
    "ReadGradeLevelSpring", "Biliteracy1Level", "Biliteracy1Language", "Biliteracy2Level",
    "Biliteracy2Language", "EarlyNumeracyStatusBOY", "EarlyNumeracyStatusMOY", 
    "EarlyNumeracyStatusEOY", "EarlyNumeracyIntervention"
]

# Filter student_table to one row per student (Remove rows with null or empty student_numbers and duplicate rows)
student_table = student.drop(columns=student_columns_to_drop)
student_table.dropna(subset=['student_number'], inplace=True)

# Drop duplicate student_numbers but keep the row with the largest GradeLevel
student_table = student_table.loc[student_table.groupby('student_number')['GradeLevel'].idxmax()].reset_index(drop=True)


##########################################################################################################################################################
# Create a table that contains all the columns as the student_table but only inlcudes student_numbers for high school students.
# Ensure GradeLevel is numeric
student_table['GradeLevel'] = pd.to_numeric(student_table['GradeLevel'], errors='coerce')

# Filter the student_table to only include student_numbers for students in grades > 8
high_school_students = student_table[student_table['GradeLevel'] > 8].copy()

student_table.head()
high_school_students.head()


##########################################################################################################################################################
# Export both tables
student_table.to_csv('./data/student_table.csv', index=False)
high_school_students.to_csv('./data/high_school_students.csv', index=False)

print("Student data exported successfully!")