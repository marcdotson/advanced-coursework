import pandas as pd
import numpy as np
import os

# Define the file path
csv_path = 'data/Clearing House Data - USU Version.csv'

# Read in data
df = pd.read_csv(csv_path)

# Remove rows that don't have data
df = df[df['Record_Found_Y/N'] != 'N']

# Condense the graduation date to only the year
df['High_School_Grad_Date'] = df['High_School_Grad_Date'].astype(str).str[:4].astype(int)

# Map the school codes to the school names
school_name = {
    450408: 'Sky View',
    450196: 'Ridgeline',
    450138: 'Mountain Crest',
    450017: 'Green Canyon',
    450168: 'Cache High'
}
# Rename the column to 'High_School' and replace values
df.rename(columns={'High_School_Code': 'High_School'}, inplace=True)
df['High_School'] = df['High_School'].replace(school_name)

# Rename columns
df.rename(columns={
    'Graduation_Date': 'College_Grad_Date',
    'High_School_Grad_Date': 'High_School_Grad_Year',
    'Final_Graduation_Date': 'Final_Grad_Date',
    'College_Code/Branch': 'College_Code',
    'Student Identifier': 'Student_ID'
}, inplace=True)

# Sort the dataframe by Student ID and Enrollment_Begin
df = df.sort_values(by=['Student_ID', 'Enrollment_Begin'])

# Add new column to count the number of semesters
df['Semester_Count'] = df.groupby('Student_ID')['Student_ID'].transform('count')
df.loc[df['Graduated'] == 'Y', 'Semester_Count'] -= 2

# Ensure date columns are in datetime format
date_columns = ['Enrollment_End', 'Enrollment_Begin', 'College_Grad_Date']
for col in date_columns:
    df[col] = pd.to_datetime(df[col], format='%Y%m%d', errors='coerce')

# Aggregate student data
def aggregate_student_data(student_data):
    result = {
        'High_School': student_data['High_School'].iloc[0],
        'High_School_Grad_Year': student_data['High_School_Grad_Year'].iloc[0],
        'Graduated': student_data['Graduated'].iloc[-1],
        'Final_Grad_Date': student_data['College_Grad_Date'].max() if not student_data['College_Grad_Date'].dropna().empty else np.nan,
        'Total_Enrollments': len(student_data),
        'First_Enrollment': student_data['Enrollment_Begin'].min(),
        'Last_Enrollment': student_data['Enrollment_End'].max()
    }

    # Multi-value columns
    max_instances = 10
    for col in ['College_Code', 'College_Name', 'Major', 'Degree_Title', 'Program_Code', 'College_State', '2-Year/4-Year', 'Public/Private']:
        values = student_data[col].dropna().tolist()
        for i in range(min(len(values), max_instances)):
            result[f"{col}_{i+1}"] = values[i]
        for i in range(len(values), max_instances):
            result[f"{col}_{i+1}"] = np.nan

    return pd.Series(result)

# Apply the aggregation
grouped_df = df.groupby('Student_ID').apply(aggregate_student_data).reset_index()

# Drop columns with all null values
grouped_df = grouped_df.dropna(axis=1, how='all')

# Define the output path
output_path = os.path.join("data", "cleaned-clearinghouse-data.csv.")

# Save the cleaned data to a CSV file
grouped_df.to_csv(output_path, index=False)
print(f"File saved successfully at: {output_path}")

# Print the first few rows and columns
print(grouped_df.head())
print("Columns after processing:")
print(grouped_df.columns)
