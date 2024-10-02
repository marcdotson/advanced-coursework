import pandas as pd
import numpy as np

df = pd.read_csv('C:/Users/brook/OneDrive/Documents/ACP/Clearing House Data - USU Version.csv')

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
df['High_School_Code'] = df['High_School_Code'].replace(school_name)

# Sort the dataframe by Student Identifier and Enrollment_Begin to ensure chronological order
df = df.sort_values(['Student Identifier', 'Enrollment_Begin'])

# Define the maximum number of instances to track for repeated measures
max_instances = 10  # Adjust this based on your data and needs

# Function to create sequenced column names
def make_col_name(col, n):
    return f"{col}_{n+1}"

# Group by Student Identifier and create new columns
def aggregate_student_data(student_data):
    result = {
        'High_School_Code': student_data['High_School_Code'].iloc[0],
        'High_School_Grad_Date': student_data['High_School_Grad_Date'].iloc[0],
        'Graduated': student_data['Graduated'].iloc[-1],
        'Final_Graduation_Date': student_data['Graduation_Date'].dropna().iloc[-1] if not student_data['Graduation_Date'].dropna().empty else np.nan,
        'Total_Enrollments': len(student_data),
        'First_Enrollment': student_data['Enrollment_Begin'].iloc[0],
        'Last_Enrollment': student_data['Enrollment_End'].iloc[-1]
    }
    
    # Multi-value columns
    for col in ['College_Code/Branch', 'College_Name', 'Major', 'Degree_Title', 'Program_Code', 'College_State', '2-Year/4-Year', 'Public/Private']:
        values = student_data[col].dropna().tolist()
        for i in range(min(len(values), max_instances)):
            result[make_col_name(col, i)] = values[i]
        # Fill remaining columns with NaN if fewer than max_instances
        for i in range(len(values), max_instances):
            result[make_col_name(col, i)] = np.nan
    
    return pd.Series(result)

# Apply the aggregation
grouped_df = df.groupby('Student Identifier').apply(aggregate_student_data).reset_index()

# Drop columns with all null values
grouped_df = grouped_df.dropna(axis=1, how='all')

# Save the final DataFrame to CSV
output_path = r"C:/Users/brook/OneDrive/Documents/ACP/cleaned_data.csv"
grouped_df.to_csv(output_path, index=False)

print(f"File saved successfully at: {output_path}")

# Print the first few rows and columns
print(grouped_df.head())
print(grouped_df.columns)