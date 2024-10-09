import pandas as pd
import numpy as np
import os

#Read in data
df = pd.read_csv('data/Clearing House Data - USU Version.csv')
#Remove rows that don't have data
df = df[df['Record_Found_Y/N'] != 'N']

#Condense the graduation date to only the year
df['High_School_Grad_Date'] = df['High_School_Grad_Date'].astype(str).str[:4].astype(int)

# Map the school codes to the school names
school_name = {
    450408: 'Sky View',
    450196: 'Ridgeline',
    450138: 'Mountain Crest',
    450017: 'Green Canyon',
    450168: 'Cache High'
}
# Rename the column to 'high_school'
df.rename(columns={'High_School_Code': 'High_School'}, inplace=True)

# Replace values in the renamed column
df['High_School'] = df['High_School'].replace(school_name)

# Rename the graduation_date column to college_grad_date'
df.rename(columns={'Graduation_Date': 'College_Grad_Date'}, inplace=True)

# Rename the high_school_grad_date column to 'high_school_grad_year'
df.rename(columns={'High_School_Grad_Date': 'High_School_Grad_Year'}, inplace=True)

#shorten column name
df.rename(columns={'Final_Graduation_Date': 'Final_Grad_Date'}, inplace=True)

# shortern column name
df.rename(columns={'College_Code/Branch': 'College_Code'}, inplace=True)

# shorten column name
df.rename(columns={'Student Identifier': 'Student_ID'}, inplace=True)

# Sort the dataframe by Student ID and Enrollment_Begin to ensure chronological order
df = df.sort_values(['Student_ID', 'Enrollment_Begin'])

# Add new column to count the number of semesters
df['Semester_Count'] = df.groupby('Student_ID')['Student_ID'].transform('count')
# If someone has graduated they have two additional rows, therefore we need to remove 2 from the count
df.loc[df['Graduated'] == 'Y', 'Semester_Count'] = df['Semester_Count'] - 2

max_instances = 10

# Calculate the duration in days between two dates
# Ensure date columns are in datetime format
df['Enrollment_End'] = pd.to_datetime(df['Enrollment_End'], format='%Y%m%d', errors='coerce')
df['Enrollment_Begin'] = pd.to_datetime(df['Enrollment_Begin'], format='%Y%m%d', errors='coerce')

# Function to create sequenced column names
def make_col_name(col, n):
    return f"{col}_{n+1}"

# Group by Student Identifier and create new columns
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
    
    #Multi-value columns
    for col in ['College_Code', 'College_Name', 'Major', 'Degree_Title', 'Program_Code', 'College_State', '2-Year/4-Year', 'Public/Private']:
        # Get the maximum number of instances for the current column from the dictionary
        values = student_data[col].dropna().tolist()
        for i in range(min(len(values), max_instances)):
            result[make_col_name(col, i)] = values[i]
        # Fill remaining columns with NaN if fewer than max_instances
        for i in range(len(values), max_instances):
            result[make_col_name(col, i)] = np.nan
    
    return pd.Series(result)

# Put date columns in the correct format
df['College_Grad_Date'] = pd.to_datetime(df['College_Grad_Date'], format='%Y%m%d')
df['Enrollment_Begin'] = pd.to_datetime(df['Enrollment_Begin'], format='%Y%m%d')
df['Enrollment_End'] = pd.to_datetime(df['Enrollment_End'], format='%Y%m%d')

# Apply the aggregation
grouped_df = df.groupby('Student_ID').apply(aggregate_student_data).reset_index()

# Drop columns with all null values
grouped_df = grouped_df.dropna(axis=1, how='all')

# Print confirmation and remaining columns
print("Columns after dropping null columns:")
print(grouped_df.columns)

# Define the output path relative to the current file's location
output_path = os.path.join("data", "cleaned_data.csv")

print(f"File saved successfully at: {output_path}")

# Print the first few rows and columns
print(grouped_df.head())
print(grouped_df.columns)