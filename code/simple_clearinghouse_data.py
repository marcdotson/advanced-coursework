
import pandas as pd

csv_path = 'data/Clearing House Data - USU Version.csv'
df = pd.read_csv(csv_path)
#Remove rows that don't have data
df = df[df['Record_Found_Y/N'] != 'N']
#Condence the graduation date to only the year
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

#Sort the columns by SI and Enrollment_Begin
df = df.sort_values(by=['Student Identifier', 'Enrollment_Begin'])
#Create New Column Semester_Count
df['Semester_Count'] = df.groupby('Student Identifier')['Student Identifier'].transform('count')
#If someone has graduated they have two additional rows, therefore we need to remove 2 from the count
df.loc[df['Graduated'] == 'Y', 'Semester_Count'] = df['Semester_Count'] - 2

#Rename Columns
df = df.rename(columns={
    'High_School_Code': 'High_School',
    'High_School_Grad_Date': 'High_School_Grad_Year',
    'Graduation_Date': 'College_Grad_Date'
})

#Change College_grad_Date to 'year-month' format
df['College_Grad_Date'] = pd.to_datetime(df['College_Grad_Date'], format='%Y%m%d', errors='coerce')
df['College_Grad_Date'] = df['College_Grad_Date'].dt.strftime('%Y-%m')

#If someone has graduated change all values in Graduation column to Y else N
df['Graduated'] = df.groupby('Student Identifier')['Graduated'].transform(lambda x: 'Y' if 'Y' in x.values else 'N')

# We want 1 row of data per student. If the person has not graduated, we want their last row of data.
# If they have graduated, we want the row of data with thier Major and Degree information.
# We need to split the date into seperate dataframes based on their graduation status.
df_not_graduated = df[df['Graduated'] == 'N']
df_graduated = df[df['Graduated'] == 'Y']

# If Graduation is 'N', keep the last row per student, and drop the duplicates
df_not_graduated_last = df_not_graduated.drop_duplicates(subset='Student Identifier', keep='last')

# If Graduation is 'Y', keep the row where 'Major' is not null, and then drop duplicates
df_graduated_not_null_major = df_graduated[df_graduated['Major'].notnull()]
df_graduated_not_null_major = df_graduated_not_null_major.drop_duplicates(subset='Student Identifier', keep='first')

# Combine both DataFrames
df_combined = pd.concat([df_not_graduated_last, df_graduated_not_null_major])

# Reset the index for the final combined DataFrame
df_combined = df_combined.reset_index(drop=True)
df_combined = df_combined.sort_values(by=['Student Identifier'])

# Drop the empty or useless columns
df_combined = df_combined.drop(['Record_Found_Y/N', 'Program_Code', 'Enrollment_Status',
        'Enrollment_Begin', 'Enrollment_End', 'College_Code/Branch'],axis=1)

#Reorder the columns
new_column_order = [
    'Student Identifier', 
    'High_School', 
    'High_School_Grad_Year',
    'College_Name',
    'College_State',
    '2-Year/4-Year',
    'Public/Private',
    'Graduated',
    'Semester_Count',    # Move 'Semester_Count' after 'Graduated'
    'College_Grad_Date', # Before 'College_Grad_Date'
    'Degree_Title',
    'Major',
    'College_Sequence'
]
df_combined = df_combined[new_column_order]

df_combined.to_csv('simple_clearinghouse_data.csv', index=False)