# The code will output two data files: 02_academic_exploratory_data.csv and 02_academic_modeling_data.csv
# Exploratory data will have one row per student per year
# Modeling data will have one row per student

import pandas as pd
import numpy as np
import pickle

######################################################################################################################################################
# All of the data will be left joined with the df and model_df
# (if we don't want to filter before)

def process_numeric_student_columns(student_table, model_df, df, columns, rename_map):
    """
    Processes numeric columns from the student sheet, renames them, 
    and merges them into the model_df and df DataFrames.

    Parameters:
    - student_table (pd.DataFrame): DataFrame containing student data.
    - model_df (pd.DataFrame): DataFrame to merge the processed columns into.
    - df (pd.DataFrame): Another DataFrame to merge the processed columns into.
    - columns (list): List of columns to process and merge, including 'student_number'.
    - rename_map (dict): Dictionary mapping original column names to their new names.

    Returns:
    - model_df (pd.DataFrame): Updated model_df with the renamed columns merged.
    - df (pd.DataFrame): Updated df with the renamed columns merged.
    """
    
    # Ensure 'student_number' is in the list of columns
    if 'student_number' not in columns:
        columns.insert(0, 'student_number')
    
    # Copy the required columns
    selected_table = student_table[columns].copy()
    
    # Rename columns
    selected_table = selected_table.rename(columns=rename_map)
    
    # Ensure student_number is a string in all DataFrames
    selected_table['student_number'] = selected_table['student_number'].astype(str)
    model_df['student_number'] = model_df['student_number'].astype(str)
    df['student_number'] = df['student_number'].astype(str)
    
    # Merge into model_df
    model_df = pd.merge(model_df, selected_table, on='student_number', how='left')
    
    # Merge into df
    df = pd.merge(df, selected_table, on='student_number', how='left')
    
    return model_df, df


######################################################################################################################################################
# Define the list of years to process
years = [2017, 2018, 2022, 2023, 2024]

# Create two empty dictionaries to store df and model_df for each year: df_dict and model_dict
df_dict = {}
model_dict = {}

# Load the pickled data
# 'rb' opens the file in binary read mode (required for pickle).
# 'as f' assigns the file object to 'f' for use within the block.
# pickle.load(f) loads the saved Python objects (two dictionaries of DataFrames).
with open('./data/student_data.pkl', 'rb') as f:
    student_tables = pickle.load(f)

# Begin the for loop to process all the years of data
for year in years:
    # Reset the df and model_df after each iteration
    df = None
    model_df = None

    ######################################################################################################################################################
    # File Paths
    master_file = f'data/{year} EOY Data - USU.xlsx'
    membership_file = f'data/{year} EOY Data - USU.xlsx'
    scram_file = f'data/{year} EOY Data - USU.xlsx'

    # Load Data
    master = pd.read_excel(master_file, sheet_name='Course Master')
    membership = pd.read_excel(membership_file, sheet_name='Course Membership')
    scram = pd.read_excel(scram_file, sheet_name='SCRAM')

    # Retrieve the data for the specified year from the student_tables dictionary
    student_table = student_tables[year]

    # Rename 'StudentNumber' to 'student_number'
    membership = membership.rename(columns={'StudentNumber': 'student_number'})
    scram = scram.rename(columns={'StudentNumber': 'student_number'})

    ######################################################################################################################################################
    # df will represent the exploratory data, and model_df will represent the model data

    # Create the df from the student_table student_numbers
    df = student_table[['student_number']].copy()

    # Create the model_df from the student_table student_numbers
    model_df = student_table[['student_number']].copy()

    ######################################################################################################################################################
    # Determine if a class is an advanced course, determine if a student has taken an ac (ac_ind)
    # and count the number of ac classes a student has taken (ac_count).
    # df will include all new columns while model_df will only include ac_ind

    # Merge membership and master data on the CourseRecordID from the membership table
    membership_filtered = membership[['student_number', 'CourseRecordID', 'ConcurrEnrolled', 'GradeEarned']]
    master_filtered = master[['CourseTitle', 'CollegeGrantingCr', 'WhereTaughtCampus', 'CourseRecordID']]
    advanced_courses = pd.merge(membership_filtered, master_filtered, on='CourseRecordID', how='left')

    # Drop identical rows
    advanced_courses = advanced_courses.drop_duplicates()

    # Identify advanced courses
    # The result is converted to an integer type (1 for True, 0 for False)
    advanced_courses['advanced_course'] = (
        (advanced_courses['CollegeGrantingCr'].notnull()) | # Check for college credit
        (advanced_courses['WhereTaughtCampus'].notnull()) | # Check for campus location
        (advanced_courses['ConcurrEnrolled'] == 'Y') | # Check for concurrent enrollment
        (advanced_courses['CourseTitle'].str.startswith('AP', na=False)) | # Check for AP courses
        (advanced_courses['CourseTitle'].str.startswith('BTEC', na=False)) # Check for BTEC courses
    ).astype(int)

    # If CourseTitle is in the advanced_course list then add a 1 to the new column
    advanced_summary = advanced_courses.groupby('student_number', as_index=False).agg(
        ac_ind=('advanced_course', lambda x: 1 if x.sum() > 0 else 0),  # Has at least one advanced course
        ac_count=('advanced_course', 'sum')  # Total advanced courses
    )

    # Dropping any duplicate rows from advanced_summary just in case any remain.
    advanced_summary = advanced_summary.drop_duplicates()

    # Make sure student_number is a string
    advanced_summary['student_number'] = advanced_summary['student_number'].astype(str)
    df['student_number'] = df['student_number'].astype(str)
    model_df['student_number'] = model_df['student_number'].astype(str)

    # Add ac_ind to model_df
    model_df = pd.merge(model_df, advanced_summary[['student_number','ac_ind']], on='student_number', how='left')

    # Add the advanced_summary data to the df
    df = pd.merge(df, advanced_summary, on='student_number', how='left')

    # Fill null values with 0
    df[['ac_ind', 'ac_count']] = df[['ac_ind', 'ac_count']].fillna(0)
    model_df['ac_ind'] = model_df['ac_ind'].fillna(0)

    df.head()
    model_df.head()


    ######################################################################################################################################################
    # Calculate students gpa in advanced courses (ac_gpa)
    # Filter for advanced courses based on the advanced_courses list
    ac_grade = advanced_courses[advanced_courses['advanced_course'] == 1][['student_number', 'GradeEarned']].copy()

    # Exclude 'P' from the calculation as it does not get factored into the GPA and replace 'F' with 0.0
    ac_grade = ac_grade[ac_grade['GradeEarned'] != 'P']
    ac_grade['GradeEarned'] = ac_grade['GradeEarned'].replace({'F': 0.0})

    # Ensure GradeEarned is numeric
    ac_grade['GradeEarned'] = pd.to_numeric(ac_grade['GradeEarned'], errors='coerce')

    # Calculate the average grade for each student
    avg_ac_grade = ac_grade.groupby('student_number', as_index=False)['GradeEarned'].mean()

    # Rename the GradeEarned column to 'ac_gpa'
    avg_ac_grade.rename(columns={'GradeEarned': 'ac_gpa'}, inplace=True)

    # Make sure student_number is a string
    avg_ac_grade['student_number'] = avg_ac_grade['student_number'].astype(str)
    df['student_number'] = df['student_number'].astype(str)

    # Add avg_gpa to the df
    df = pd.merge(df, avg_ac_grade, on='student_number', how='left')

    # Fill null values with 0
    df['ac_gpa'] = df['ac_gpa'].fillna(0)

    # Convert ac_gpa to a float and round 3 decimal places
    df['ac_gpa'] = df['ac_gpa'].astype(float).round(3)

    df.head()


    ######################################################################################################################################################
    # Call the function above to process the numeric columns
    # Columns to process from the student_table
    columns_to_process = ['GradeLevel', 'DaysAttended', 'SchoolMembership', 'CumulativeGPA', 'ExcusedAbsences', 'UnexcusedAbsences', 'AbsencesDueToSuspension']

    # Specify the columns to process and rename
    rename_map = {
        'GradeLevel': 'current_grade',
        'DaysAttended': 'days_attended',
        'SchoolMembership': 'school_membership',
        'CumulativeGPA': 'overall_gpa',
        'ExcusedAbsences': 'excused_absences',
        'UnexcusedAbsences': 'unexcused_absences',
        'AbsencesDueToSuspension': 'absences_due_to_suspension'
    }
    # Filter columns_to_process based on their presence in the current student_table
    existing_columns = [col for col in columns_to_process if col in student_table.columns]

    # Include only the existing columns in the rename_map
    existing_rename_map = {key: rename_map[key] for key in existing_columns if key in rename_map}

    # Call the function with filtered columns and rename map
    model_df, df = process_numeric_student_columns(student_table, model_df, df, existing_columns, existing_rename_map)


    ######################################################################################################################################################
    # Add the scram data to df and model_df
    # We need to remove duplicate student_numbers by keeping the row with the max ScramMembership
    # Fill null ScramMembership values with 0
    scram['ScramMembership'] = scram['ScramMembership'].fillna(0)

    # We need to remove duplicate student_numbers by keeping the row with the max ScramMembership
    scram = scram.loc[scram.groupby('student_number')['ScramMembership'].idxmax()]
    scram.reset_index(drop=True, inplace=True)

    # Make sure student_number is a string
    scram['student_number'] = scram['student_number'].astype(str)

    # We will merge with df['student_number'] at the beginning to only work with the filtered student_numbers
    # This way we can adjust the student numbers at the top on the script once.
    scram = pd.merge(df['student_number'], scram, on='student_number', how='left')

    # Rename columns
    scram_columns = {
        'ScramMembership': 'scram_membership',
        'RegularPercent': 'regular_percent',
        'Environment': 'environment',
        'ExtendedSchoolYear': 'extended_school_year'
    }
    scram = scram.rename(columns=scram_columns)

    ################################################################
    # Dummy code the scram data (regular_percent, environment and extended_school_year)
    # Create a dataframe for dummy variables. scram_membership is a number from 0-180 so it doesn't need to be dummied.
    scram_dummies = scram[['student_number', 'scram_membership']].copy()

    ################################################################
    # Dummy code regular_percent (regular_percent_1.0, regular_percent_2.0, regular_percent_3.0 and regular_percent_nan)
    
    ################################################################
    # I'm not sure if or how the null values should be classified, therefore I have not dropped a column
    # TODO: Check with Jeremy
    ################################################################
    regular_percent_dummies = pd.get_dummies(scram['regular_percent'].astype(str), prefix='regular_percent').astype(int)

    # Concat with scram_dummies table
    scram_dummies = pd.concat([scram_dummies, regular_percent_dummies], axis=1)

    scram_dummies.head()

    ################################################################
    # Dummy code environment (environment_v = 1)
    # There are only two students in environment_h

    ################################################################
    # I'm assuming that null values would be classified as environment_v (regular school setting)
    # TODO: Check with Jeremy
    ################################################################

    environment_dummies = pd.get_dummies(scram['environment'].fillna('V').astype(str), prefix='environment').astype(int)

    # Lowercase column titles
    environment_dummies.columns = environment_dummies.columns.str.lower()

    # Concat with scram_dummies table
    scram_dummies = pd.concat([scram_dummies, environment_dummies], axis=1)

    scram_dummies.head()


    ################################################################
    # Dummy code extended_school_year (extended_school_year_y = 1)
    
    ################################################################
    # I'm assuming that null values would be classified as extended_school_year_n (No extended school year)
    # TODO: Check with Jeremy
    ################################################################
    # Dummy code extended_school_year (extended_school_year_y)
    extended_year_dummies = pd.get_dummies(scram['extended_school_year'].replace(0, 'n'), prefix='extended_school_year').astype(int)

    # Lowercase column titles
    extended_year_dummies.columns = extended_year_dummies.columns.str.lower()

    # Concat with scram_dummies table
    scram_dummies = pd.concat([scram_dummies, extended_year_dummies], axis=1)

    scram_dummies.head()

    ################################################################
    # Merge the scram data with the df and model_df
    # Make sure student_number is a string
    scram['student_number'] = scram['student_number'].astype(str)
    scram_dummies['student_number'] = scram_dummies['student_number'].astype(str)

    # Merge the non-dummied data with the df
    df = pd.merge(df, scram, on='student_number', how='left')

    # Merge the dummied data with the model_df
    model_df = pd.merge(model_df, scram_dummies, on='student_number', how='left')

    ######################################################################################################################################################
    # Store the resulting DataFrames in dictionaries (i.e. df_2017, model_df_2017)
    df_dict[f'df_{year}'] = df.copy()
    model_dict[f'model_df_{year}'] = model_df.copy()

    # Add a year column to df_dict. This may be important later
    df_dict[f'df_{year}']['year'] = year



######################################################################################################################################################
# Not all years (2017 and 2018) contain the following columns: excused_absences, unexcused_absences, and absences_due_to_suspension
# These columns are important for calculating school membership and total absences for students
# For years where these columns are missing, the provided school_membership column seems to be more accurate
# The logic will calculate absences differently based on the availability of these columns:
# - If absence columns exist: Calculate school_membership as the sum of attendance and absence columns
# - If absence columns are missing: Use the existing school_membership column to calculate absences by subtracting days_attended from school_membership
# The days_absent column is created to standardize the representation of total absences across all years
# This will be done separately for df_dict and model_dict

for year in years:
    ################################################################
    # Process df_dict for the current year
    df_year = df_dict[f'df_{year}']

    # If the absence columns exist
    if {'excused_absences', 'unexcused_absences', 'absences_due_to_suspension'}.issubset(df_year.columns):
        
        # Sum the absence columns and days_attended to create the school_membership column
        df_year['school_membership'] = df_year[
            ['days_attended', 'excused_absences', 'unexcused_absences', 'absences_due_to_suspension']
        ].sum(axis=1)
        
        # Consolidate absence data into a single column days_absent
        df_year['days_absent'] = df_year[
            ['excused_absences', 'unexcused_absences', 'absences_due_to_suspension']
        ].sum(axis=1)

        # Drop the all absence columns other than days_absent from the dictionary as they are no longer needed
        df_year = df_year.drop(columns=['excused_absences', 'unexcused_absences', 'absences_due_to_suspension'])
    
    # If the absence columns do not exist
    else:
        # For years without detailed absence columns, absences are calculated as the difference between school_membership and days_attended
        df_year['days_absent'] = df_year['school_membership'] - df_year['days_attended']

    # Save the updated DataFrame back to the dictionary
    df_dict[f'df_{year}'] = df_year

    ################################################################
    # Process model_dict for the current year
    model_year = model_dict[f'model_df_{year}']

    # If the absence columns exist
    if {'excused_absences', 'unexcused_absences', 'absences_due_to_suspension'}.issubset(model_year.columns):
        
        # Sum the absence columns and days_attended to create the school_membership column
        model_year['school_membership'] = model_year[
            ['days_attended', 'excused_absences', 'unexcused_absences', 'absences_due_to_suspension']
        ].sum(axis=1)
        
        # Consolidate absence data into a single column `days_absent`
        model_year['days_absent'] = model_year[
            ['excused_absences', 'unexcused_absences', 'absences_due_to_suspension']
        ].sum(axis=1)

        # Drop the all absence columns other than days_absent from the dictionary as they are no longer needed
        model_year = model_year.drop(columns=['excused_absences', 'unexcused_absences', 'absences_due_to_suspension'])

    # If the absence columns do not exist
    else:
        # For years without detailed absence columns, absences are calculated as the difference between school_membership and days_attended
        model_year['days_absent'] = model_year['school_membership'] - model_year['days_attended']

    # Save the updated DataFrame back to the dictionary
    model_dict[f'model_df_{year}'] = model_year


######################################################################################################################################################
# Concatenate data from multiple years into two main DataFrames:
# - df keeps one row per student per year, preserving yearly details
# - concat_model combines all years of model data to later aggregate to one row per student

df = pd.concat(df_dict.values(), ignore_index=True)
concat_model = pd.concat(model_dict.values(), ignore_index=True)

# Remove duplicate rows if there are any
df = df.drop_duplicates(keep='first')
concat_model = concat_model.drop_duplicates(keep='first')

df.head()
concat_model.head()

######################################################################################################################################################
# Create model_df as a base for aggregated data
# Extracts unique student numbers from concat_model
# model_df will contain one row per student, making it suitable for merging aggregated metrics

model_df = concat_model[['student_number']].copy()

# Make sure model_df has one row per student_number
model_df = model_df.drop_duplicates(keep='first')
model_df.head()


######################################################################################################################################################
# Compile all student attendance data from different years into one row per student
# Select the attendance columns we want from the concat_model
model_attendance = concat_model[['student_number', 'days_attended', 'days_absent', 'school_membership']].copy()

# Remove any duplicate rows, keeping only the first occurrence of each
model_attendance = model_attendance.drop_duplicates(keep='first')

# Sum the attendance data for each student_number to aggregate across years
model_attendance = model_attendance.groupby('student_number', as_index=False).sum()

# Create percent_days_attended to calculate overall attendance percentage: days_attended divided by school_membership
# If school_membership is 0 it is replaced with NA to avoid division issues.
# This might be pointless.
# If school_membership = 0 then percent_days_attended = 0 (avoid dividing by 0)
model_attendance.loc[model_attendance['school_membership'] == 0, 'percent_days_attended'] = np.nan

# Perform the calculation
model_attendance['percent_days_attended'] = (model_attendance['days_attended'] / model_attendance['school_membership']) * 100

# Round the result to two decimal places
model_attendance['percent_days_attended'] = model_attendance['percent_days_attended'].round(2)

model_attendance.head()

# Make sure student number is a string
model_attendance['student_number'] = model_attendance['student_number'].astype(str)
model_df['student_number'] = model_df['student_number'].astype(str)

# Merge student_attendance with model_df
model_df = pd.merge(model_df, model_attendance, on='student_number', how='left')

model_df.head()


######################################################################################################################################################
# Calculate the percent_days_attended column for the df. This will be the percentage of days each student attended each year.
# If school_membership is 0 it is replaced with NA to avoid division issues.
# This might be pointless.
# If school_membership = 0 then percent_days_attended = 0 (avoid dividing by 0)
df.loc[df['school_membership'] == 0, 'percent_days_attended'] = np.nan  # Avoid division by zero

# Perform the calculation
df['percent_days_attended'] = (df['days_attended'] / df['school_membership']) * 100

# Round the result to two decimal places
df['percent_days_attended'] = df['percent_days_attended'].round(2) 

# Round percent_days_attended to two decimal places
df['percent_days_attended'] = pd.to_numeric(df['percent_days_attended'], errors='coerce')
df['percent_days_attended'] = df['percent_days_attended'].round(2)

df.head()


######################################################################################################################################################
# Filter the ac_ind column for the model_df. ac_ind can only be a 1 or 0 so we will return the max value for each student_number
advanced_course_indicator = concat_model[['student_number', 'ac_ind']].copy()

# Group by student_number and the row with the max ac_ind
advanced_course_indicator = advanced_course_indicator.groupby('student_number', as_index=False)['ac_ind'].max()

# Make sure student number is a string
advanced_course_indicator['student_number'] = advanced_course_indicator['student_number'].astype(str)

advanced_course_indicator.head()

# Merge with model_df
model_df = pd.merge(model_df, advanced_course_indicator, on='student_number', how='left')

model_df.head()


######################################################################################################################################################
# Add the most recent overall_gpa per student to the model_df
combined_overall_gpa = concat_model[['student_number', 'overall_gpa', 'current_grade']].copy()

# Sort by grade level in descending order
combined_overall_gpa = combined_overall_gpa.sort_values(by='current_grade', ascending=False)

# Remove duplicates, keeping the row with the largest current_grade
combined_overall_gpa = combined_overall_gpa.drop_duplicates(subset='student_number', keep='first')

# Make sure student number is a string
combined_overall_gpa['student_number'] = combined_overall_gpa['student_number'].astype(str)

combined_overall_gpa.head()

# Merge with model_df
model_df = pd.merge(model_df, combined_overall_gpa[['student_number', 'overall_gpa']], on='student_number', how='left')

model_df.head()


######################################################################################################################################################
# Sum the scram_membership for each year per student and add to model_df
scram_membership_sum = concat_model[['student_number', 'scram_membership']].copy()

# Sum the scram_membership data for each student_number to aggregate across years
scram_membership_sum = scram_membership_sum.groupby('student_number', as_index=False).sum()

# Make sure student number is a string
scram_membership_sum['student_number'] = scram_membership_sum['student_number'].astype(str)

scram_membership_sum.head()

# Merge with model_df
model_df = pd.merge(model_df, scram_membership_sum, on='student_number', how='left')

model_df.head()


######################################################################################################################################################
# Return the rest of Scram data for the most recent year of data per student
concat_scram_colums = [
    'student_number', 'regular_percent_1.0', 'regular_percent_2.0', 'regular_percent_3.0', 'regular_percent_nan', 
    'environment_h', 'environment_r', 'environment_v', 'extended_school_year_y', 'current_grade'
]

# Filter the DataFrame for the specified columns
combined_scram = concat_model[concat_scram_colums]

# Sort by grade level in descending order
combined_scram = combined_scram.sort_values(by='current_grade', ascending=False)

# Remove duplicates, keeping the row with the largest current_grade
combined_scram = combined_scram.drop_duplicates(subset='student_number', keep='first')

# Drop current_grade from the Data Frame as it is not needed in the model_df
#combined_scram = combined_scram.drop(columns='current_grade')

###################################
# TODO: I am assuming that regular_percent_nan does not need to be reclassified, therefore I will drop this column
###################################
# Drop the regular_percent_nan column
combined_scram = combined_scram.drop(columns='regular_percent_nan')

###################################
# A environment column needs to be dropped, but some years have v, h, and r, while others only have v so I do not know which column to drop
###################################

# Make sure student number is a string
combined_scram['student_number'] = combined_scram['student_number'].astype(str)

combined_scram.head()

# Merge with model_df
model_df = pd.merge(model_df, combined_scram, on='student_number', how='left')

model_df.head()

df.duplicated(subset=['student_number', 'current_grade']).sum()
df.duplicated().sum()


######################################################################################################################################################
# Prepare the data for export
# Columns not included in both df and model_df: home_status, limited_english, ell_instruction_type, ell_native_language and ell_parent_language

# Specify the column order for the df
df_columns = ['student_number', 'ac_ind', 'ac_count', 'ac_gpa', 'overall_gpa', 'days_attended',
            'days_absent', 'school_membership', 'percent_days_attended',  'current_grade',
            'scram_membership', 'regular_percent', 'environment', 'extended_school_year']

df = df[df_columns]

# Specify the column order for the model_df
model_columns = (['student_number', 'ac_ind', 'overall_gpa', 'days_attended', 'days_absent', 
                'school_membership', 'percent_days_attended', 'extended_school_year_y']
 + [col for col in model_df.columns if col.startswith('regular_percent')]
 + [col for col in model_df.columns if col.startswith('environment_')])

model_df = model_df[model_columns]

df.head()
model_df.head()

# Export both files
df.to_csv('./data/02_academic_exploratory.csv', index=False)
model_df.to_csv('./data/02_academic_modeling.csv', index=False)

print('===========================================')
print("Academic data exported successfully!")
print("Next, run: 03_demographic-table.py")
print('===========================================')
