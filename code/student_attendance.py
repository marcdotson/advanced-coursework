import pandas as pd
import numpy as np

# Data sheets
student_2017 = pd.read_excel('data/2017 EOY Data - USU.xlsx', sheet_name='Student')
student_2018 = pd.read_excel('data/2018 EOY Data - USU.xlsx', sheet_name='Student')
student_2022 = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Student')
student_2023 = pd.read_excel('data/2023 EOY Data - USU.xlsx', sheet_name='Student')
student_2024 = pd.read_excel('data/2024 EOY Data - USU.xlsx', sheet_name='Student')

student = pd.concat([student_2017, student_2018, student_2022, student_2023, student_2024], ignore_index=True)

# Rename 'StudentNumber' to 'student_number' in all tables that contain 'student_number'
student = student.rename(columns={'StudentNumber': 'student_number'})

student_columns_to_drop = [
    "ExitDate", "ResidentStatus", "KindergartenType", "EarlyGrad", "ReadGradeLevelFall", 
    "ReadGradeLevelSpring", "Biliteracy1Level", "Biliteracy1Language", "Biliteracy2Level",
    "Biliteracy2Language", "EarlyNumeracyStatusBOY", "EarlyNumeracyStatusMOY", 
    "EarlyNumeracyStatusEOY", "EarlyNumeracyIntervention"
]

# Filter student_table to one row per student (Remove rows with null or empty student_numbers and duplicate rows)
student_table = student.drop(columns=student_columns_to_drop)
student_table.dropna(subset=['student_number'], inplace=True)

student_table.duplicated(subset='student_number').sum()

student_attendance = student_table[['student_number', 'DaysAttended', 'ExcusedAbsences', 'UnexcusedAbsences', 'AbsencesDueToSuspension']]
student_attendance = student_attendance.rename(columns={
                'StudentNumber': 'student_number', 'DaysAttended': 'days_attended',
                'ExcusedAbsences': 'excused_absences', 'UnexcusedAbsences': 'unexcused_absences',
                'AbsencesDueToSuspension': 'absences_due_to_suspension'})

student_attendance = student_attendance.drop_duplicates(keep='first')

student_attendance = student_attendance.groupby('student_number', as_index=False).sum()

student_attendance.duplicated(subset='student_number').sum()

student_attendance['school_membership'] = student_attendance[
    ['days_attended', 'excused_absences', 'unexcused_absences', 'absences_due_to_suspension']
].sum(axis=1)

student_attendance['percent_days_attended'] = (
    student_attendance['days_attended'] / student_attendance['school_membership'].replace(0, pd.NA)
) * 100

student_attendance['percent_days_attended'] = student_attendance['percent_days_attended'].round(2)

student_attendance.head()
student_attendance['excused_absences'].value_counts()
student_attendance['unexcused_absences'].value_counts()
student_attendance['absences_due_to_suspension'].value_counts()
student_attendance['school_membership'].value_counts()
student_attendance['percent_days_attended'].value_counts()
