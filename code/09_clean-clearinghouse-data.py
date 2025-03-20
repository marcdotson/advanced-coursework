import pandas as pd
import numpy as np
import os

# TODO : figure out how to add a highest degree column
# FIXME : fix all the NaT values
# FIXME : standardize the values (Public vs public)
# FIXME : why are the high school codes messed up, standardize them with eda data

# Define the file path
csv_path = '../data/Clearing House Data - USU Version.csv'

# Read in data
df = pd.read_csv(csv_path)

# Remove rows that don't have data
df = df[df['Record_Found_Y/N'] != 'N']

# Condense the graduation date to only the year
df['High_School_Grad_Date'] = df['High_School_Grad_Date'].astype(str).str[:4].astype(int)

# Rename columns
df.rename(columns={
    'Graduation_Date': 'college_grad_date',
    'High_School_Grad_Date': 'high_school_grad_year',
    'Final_Graduation_Date': 'final_grad_date',
    'College_Code/Branch': 'college_code',
    'Student Identifier': 'student_number'
}, inplace=True)

df = df.rename(columns=str.lower)

# Sort the dataframe
df = df.sort_values(by=['student_number', 'enrollment_begin'])

# Add new column to count the number of semesters
df['semester_count'] = df.groupby('student_number')['student_number'].transform('count')
df.loc[df['graduated'] == 'Y', 'semester_count'] -= 2

# Ensure date columns are in datetime format
date_columns = ['enrollment_end', 'enrollment_begin', 'college_grad_date']
for col in date_columns:
    df[col] = pd.to_datetime(df[col], format='%Y%m%d', errors='coerce')

# Aggregate student data
def aggregate_student_data(student_data):
    result = {
        'high_school_code': student_data['high_school_code'].iloc[0],
        'high_school_grad_year': student_data['high_school_grad_year'].iloc[0],
        'graduated': student_data['graduated'].iloc[-1],
        'final_grad_date': student_data['college_grad_date'].max() if not student_data['college_grad_date'].dropna().empty else np.nan,
        'total_enrollments': len(student_data),
        'first_enrollment': student_data['enrollment_begin'].min(),
        'last_enrollment': student_data['enrollment_end'].max()
    }

    # Multi-value columns
    max_instances = 10
    for col in ['college_code', 'college_name', 'major', 'degree_title', 'program_code', 'college_state', '2-year/4-year', 'public/private']:
        values = student_data[col].dropna().tolist()
        for i in range(min(len(values), max_instances)):
            result[f"{col}_{i+1}"] = values[i]
        for i in range(len(values), max_instances):
            result[f"{col}_{i+1}"] = np.nan

    return pd.Series(result)

# Apply the aggregation
grouped_df = df.groupby('student_number').apply(aggregate_student_data).reset_index()

# Drop columns with all null values
grouped_df = grouped_df.dropna(axis=1, how='all')

# Define the output paths
cleaned_data_path = os.path.join("../data", "cleaned-clearinghouse-data.csv")
modeling_data_path = os.path.join("../data", "modeling-clearinghouse-data.csv")

# Save the cleaned data to a CSV file
grouped_df.to_csv(cleaned_data_path, index=False)
print(f"Cleaned data saved successfully at: {cleaned_data_path}")

# Feature Engineering for Modeling
df_modeling = grouped_df.copy()
df_modeling['time_to_enrollment'] = (df_modeling['first_enrollment'] - pd.to_datetime(df_modeling['high_school_grad_year'], format='%Y')).dt.days
df_modeling['total_college_time'] = (df_modeling['last_enrollment'] - df_modeling['first_enrollment']).dt.days
df_modeling['unique_colleges'] = df_modeling[['college_code_1', 'college_code_2', 'college_code_3', 'college_code_4', 'college_code_5',
                                             'college_code_6', 'college_code_7', 'college_code_8', 'college_code_9', 'college_code_10']].notnull().sum(axis=1)
df_modeling['institution_type'] = df_modeling[['2-year/4-year_1', '2-year/4-year_2', '2-year/4-year_3', '2-year/4-year_4', '2-year/4-year_5',
                                              '2-year/4-year_6', '2-year/4-year_7', '2-year/4-year_8', '2-year/4-year_9', '2-year/4-year_10']].apply(lambda x: '4-year' if '4-year' in x.values else '2-year', axis=1)
df_modeling['college_type'] = df_modeling[['public/private_1', 'public/private_2', 'public/private_3', 'public/private_4', 'public/private_5',
                                          'public/private_6', 'public/private_7', 'public/private_8', 'public/private_9', 'public/private_10']].apply(lambda x: 'Public' if 'Public' in x.values else 'Private', axis=1)

# Dummy Coding for Modeling
df_modeling = pd.get_dummies(df_modeling, columns=['high_school_code', 'institution_type', 'college_type'])

# Save the modeling data to a CSV file
df_modeling.to_csv(modeling_data_path, index=False)
print(f"Modeling data saved successfully at: {modeling_data_path}")

# Print the first few rows and columns
print(grouped_df.head())
print("Columns after processing:")
print(grouped_df.columns)