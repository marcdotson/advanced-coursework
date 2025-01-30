# The code will output two data files: 03_demographic_exploratory_data.csv and 03_demographic_modeling_data.csv

import pandas as pd
import pickle

####################################################################
# TODO: I have not dropped any categorical columns from the dummied data. I need to make sure the 
# column I drop is a column in every year of the data.
####################################################################

######################################################################################################################################################
# Function to process categorical variables. Add non-dummied columns to df and dummy-coded columns to model_df
def process_categorical_column(df, model_df, reference_table, column_name, dummy_name, key_column='student_number'):
    """
    Processes a categorical column by adding the non-dummied column to df and dummy-coded columns to model_df.

    Parameters:
        df (pd.DataFrame): DataFrame where the non-dummied column will be added.
        model_df (pd.DataFrame): DataFrame where dummy-coded columns will be added.
        reference_table (pd.DataFrame): The table containing the column to be processed.
        column_name (str): The original name of the column in the reference table.
        dummy_name (str): The desired name for the column in the df and model_df.
        key_column (str): The column to use as the primary key for merging (default is 'student_number').

    Returns:
        pd.DataFrame, pd.DataFrame: Updated df and model_df DataFrames.
    """
    # Extract and rename the column
    temp_table = reference_table[[key_column, column_name]].rename(columns={column_name: dummy_name})

    # Handle null values by filling with 'nan'
    temp_table[dummy_name] = temp_table[dummy_name].fillna('nan')

    # Ensure the key column is a string in all DataFrames
    temp_table[key_column] = temp_table[key_column].astype(str)
    df[key_column] = df[key_column].astype(str)
    model_df[key_column] = model_df[key_column].astype(str)

    # Add the non-dummied column to df
    df = pd.merge(df, temp_table, on=key_column, how='left')

    # Generate dummy variables
    dummies = pd.get_dummies(temp_table[dummy_name], prefix=dummy_name, dtype=int)

    # Rename dummy columns to lowercase
    dummies.columns = dummies.columns.str.lower()

    # Merge dummy variables into model_df
    model_df = pd.merge(model_df, pd.concat([temp_table[key_column], dummies], axis=1), on=key_column, how='left')

    return df, model_df


######################################################################################################################################################
# Function to process binary columns: add to df, replace nulls, and dummy code
def student_binary_columns(df, model_df, reference_table, column_name, dummy_name, key_column='student_number'):
    """
    Processes a binary column from a reference DataFrame (student_table) by adding the non-dummy column to df
    and dummy-coded columns to model_df.

    Parameters:
        df (pd.DataFrame): DataFrame where the non-dummy column will be added.
        model_df (pd.DataFrame): DataFrame where dummy-coded columns will be added.
        reference_table (pd.DataFrame): The table containing the column to be processed.
        column_name (str): The original name of the column in the reference table.
        dummy_name (str): The desired name for the column in the df and model_df.
        key_column (str): The column to use as the primary key for merging (default is 'student_number').

    Returns:
        pd.DataFrame, pd.DataFrame: Updated df and model_df DataFrames.
    """
    # Extract and rename the target column
    temp_table = reference_table[[key_column, column_name]].rename(columns={column_name: dummy_name})

    # Fill null values with 'N'
    temp_table[dummy_name] = temp_table[dummy_name].fillna('N')

    # Ensure the key column is a string in all DataFrames
    temp_table[key_column] = temp_table[key_column].astype(str)
    df[key_column] = df[key_column].astype(str)
    model_df[key_column] = model_df[key_column].astype(str)

    # Add the non-dummied column to df
    df = pd.merge(df, temp_table, on=key_column, how='left')

    # Create a binary dummy variable (Y=1, N=0)
    temp_table[f"{dummy_name}_y"] = temp_table[dummy_name].map({'Y': 1, 'N': 0})

    # Create a DataFrame containing only key_column and the dummy variable
    dummy_table = temp_table[[key_column, f"{dummy_name}_y"]]

    # Merge the dummy variable into model_df
    model_df = pd.merge(model_df, dummy_table, on=key_column, how='left')

    return df, model_df

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
    student_tables, high_school_students_tables = pickle.load(f)

# Begin the for loop to process all the years of data
for year in years:
    ######################################################################################################################################################
    # Retrieve the data for the specified year from the student_tables and high_school_students_tables dictionaries
    student_table = student_tables[year]
    high_school_students = high_school_students_tables[year]

    ######################################################################################################################################################
    # df will represent the exploratory data, and model_df will represent the model data
    ####################################################################
    # If we decided to filter at the end, all we need to do is change high_school_students to student_table when creating the df and model_df below
    ####################################################################

    # Create the df from the high_school_student student_numbers
    df = high_school_students[['student_number']].copy()

    # Create the model_df from the high_school_student student_numbers
    model_df = high_school_students[['student_number']].copy()


    ######################################################################################################################################################
    # Define the list of categorical columns to process using the function above (process_categorical_column)
    categorical_columns = [
        ('Gender', 'gender'),
        ('LimitedEnglish', 'limited_english'),
        ('PartTimeHomeSchool', 'part_time_home_school'),
        ('HighSchlComplStatus', 'hs_complete_status'),
        ('ExitCode', 'exit_code'),
        ('HomeStatus', 'home_status'),
        ('TribalAffiliation', 'tribal_affiliation'),
        ('EllNativeLanguage', 'ell_native_language'),
        ('EllParentLanguage', 'ell_parent_language'),
        ('EllInstructionType', 'ell_instruction_type')
    ]

    # Apply the function to each column in the list if the column exists
    for original_col, new_col in categorical_columns:
        if original_col in student_table.columns:
            df, model_df = process_categorical_column(df, model_df, student_table.copy(), original_col, new_col)
        
        # If the column does not exist, print which column is missing for what year
        else:
            print(f"Column '{original_col}' not found in the '{year}' student_table. Skipping...")



    ######################################################################################################################################################
    # Define the list of binary columns to process using the function above (student_binary_columns)
    columns_to_process = [
        ('Ethnicity', 'ethnicity'),
        ('AmerIndianAlaskan', 'amerindian_alaskan'),
        ('Asian', 'asian'),
        ('BlackAfricanAmer', 'black_african_amer'),
        ('HawaiianPacificIsl', 'hawaiian_pacific_isl'),
        ('White', 'white'),
        ('Migrant', 'migrant'),
        ('Gifted', 'gifted'),
        ('Services504', 'services_504'),
        ('MilitaryChild', 'military_child'),
        ('RefugeeStudent', 'refugee_student'),
        ('Immigrant', 'immigrant'),
        ('ReadingIntervention', 'reading_intervention'),
        ('PassedCivicsExam', 'passed_civics_exam'),
        ('ReadGradeLevel', 'read_grade_level')
    ]

    # Apply the function to each column in the list if the column exists
    for original_col, new_col in columns_to_process:
        if original_col in student_table.columns:
            df, model_df = student_binary_columns(df, model_df, student_table, original_col, new_col)
        
        # If the column does not exist, print which column is missing for what year
        else:
            print(f"Column '{original_col}' not found in the '{year}' student_table. Skipping...")


    ######################################################################################################################################################
    # Add the date columns from the student table to the model_df and the df (entry_date, first_enroll_us....)
    # I am still unsure of the best way format the dates, possibly a count since a specific date or something else.
    # Only use student_numbers of high school students
    student_dates = student_table[['student_number', 'EntryDate', 'FirstEnrollInUS', 'EllMonitoredEntryDate']]

    # Rename the following columns for consistency
    student_dates = student_dates.rename(columns={
        'EntryDate': 'entry_date',
        'FirstEnrollInUS': 'first_enroll_us',
        'EllMonitoredEntryDate': 'ell_entry_date'
    })

    date_columns = ['entry_date', 'first_enroll_us', 'ell_entry_date']

    # Convert date columns into datetime format
    student_dates[date_columns] = student_dates[date_columns].apply(
        lambda col: pd.to_datetime(col.astype(str).str.replace('-', ''), format='%Y%m%d', errors='coerce')
    )

    # Make sure student_number is a string
    student_dates['student_number'] = student_dates['student_number'].astype(str)
    df['student_number'] = df['student_number'].astype(str)
    model_df['student_number'] = model_df['student_number'].astype(str)

    # Merge into df
    df = pd.merge(df, student_dates, on='student_number', how='left')

    # Merge into model_df
    model_df = pd.merge(model_df, student_dates, on='student_number', how='left')


    ######################################################################################################################################################
    # Store the resulting DataFrames in dictionaries (i.e. df_2017, model_df_2017)
    df_dict[f'df_{year}'] = df.copy()
    model_dict[f'model_df_{year}'] = model_df.copy()

    # Add a year column to df_dict. This may be important later
    df_dict[f'df_{year}']['year'] = year
    model_dict[f'model_df_{year}']['year'] = year


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
# Retrieve the binary and categorical data associated with the students' most recent year they attended school for the model_df
# Specify the columns to exclude from this step
exclude_columns = ['ell_entry_date', 'entry_date', 'first_enroll_us']

# Create a copy of concat_model to work with
binary_categorical_data = concat_model.copy()

# Drop the excluded columns from the data
binary_categorical_data = binary_categorical_data.drop(columns= exclude_columns)

# Sort the data by the year column in descending order
binary_categorical_data = binary_categorical_data.sort_values(by='year', ascending=False)

# Remove duplicate rows based on the 'student_number' column to keep the row with the most recent year
binary_categorical_data = binary_categorical_data.drop_duplicates(subset='student_number', keep='first')

# Drop the year column from the data
binary_categorical_data = binary_categorical_data.drop(columns='year')

# Make sure student_number is a string
binary_categorical_data['student_number'] = binary_categorical_data['student_number'].astype(str)
model_df['student_number'] = model_df['student_number'].astype(str)

binary_categorical_data.head()

# Merge the binary and categorical data with the model_df
model_df = pd.merge(model_df, binary_categorical_data, on='student_number', how='left')

model_df.head()


######################################################################################################################################################
# Add the date columns to the model_df keeping the oldest (earliest) date for each student
# Retain the oldest (earliest) date for each student in the specified columns
# Columns to process
date_columns = ['ell_entry_date', 'entry_date', 'first_enroll_us']

# Create a DataFrame to hold the results
earliest_dates = model_df[['student_number']].copy()

# Ensure the date columns are in datetime format and process each column separately
for col in date_columns:
    # Create a DataFrame with student_number and the current date column
    temp_date = concat_model[['student_number', col]].copy()
    
    # Ensure the column is in datetime format
    temp_date[col] = pd.to_datetime(temp_date[col], errors='coerce')
    
    # Sort by student_number and the date column in ascending order
    temp_date = temp_date.sort_values(by=['student_number', col], ascending=[True, True])
    
    # Drop duplicates to keep the earliest date for each student
    temp_date = temp_date.drop_duplicates(subset='student_number', keep='first')
    
    # Merge the earliest date back into the results DataFrame
    earliest_dates = pd.merge(earliest_dates, temp_date, on='student_number', how='left')

# Ensure student_number is a string
earliest_dates['student_number'] = earliest_dates['student_number'].astype(str)

earliest_dates.head()

# Merge the earliest dates into model_df
model_df = pd.merge(model_df, earliest_dates, on='student_number', how='left')

# Preview the updated model_df
model_df.head()


######################################################################################################################################################
# Prepare the data for export

# Specify the column order for the df
df_columns = ['student_number', 'gender', 'ethnicity', 'amerindian_alaskan', 'asian', 'black_african_amer', 
            'hawaiian_pacific_isl', 'white', 'migrant', 'military_child', 'refugee_student', 'gifted',
            'services_504', 'immigrant', 'passed_civics_exam', 'reading_intervention', 'home_status',
            'hs_complete_status', 'part_time_home_school', 'tribal_affiliation', 'limited_english', 
            'ell_instruction_type', 'ell_native_language', 'ell_parent_language', 'read_grade_level', 'exit_code', 
            'ell_entry_date', 'entry_date','first_enroll_us']

df = df[df_columns]

# Specify the column order for the model_df
model_columns = (
    ['student_number']+
    [col for col in model_df.columns if col.startswith('gender_')]
    +[
        'ethnicity_y', 'amerindian_alaskan_y', 'asian_y', 'black_african_amer_y', 
        'hawaiian_pacific_isl_y', 'white_y', 'migrant_y', 'military_child_y', 'refugee_student_y', 'gifted_y',
        'services_504_y', 'immigrant_y', 'passed_civics_exam_y', 'reading_intervention_y',]
    + [col for col in model_df.columns if col.startswith('home_status_')]
    + [col for col in model_df.columns if col.startswith('hs_complete_status_')]
    + [col for col in model_df.columns if col.startswith('part_time_home_school_')]
    + [col for col in model_df.columns if col.startswith('tribal_affiliation_')]
    + [col for col in model_df.columns if col.startswith('limited_english_')]
    + [col for col in model_df.columns if col.startswith('ell_instruction_type_')]
    + [col for col in model_df.columns if col.startswith('ell_native_language_')]
    + [col for col in model_df.columns if col.startswith('ell_parent_language_')]
    + [col for col in model_df.columns if col.startswith('read_grade_level_')]
    + [col for col in model_df.columns if col.startswith('exit_code_')]
    + ['ell_entry_date', 'entry_date', 'first_enroll_us'])

model_df = model_df[model_columns]

model_df.head()
df.head()

# Export both files
df.to_csv('./data/03_demographic_exploratory.csv', index=False)
model_df.to_csv('./data/03_demographic_modeling.csv', index=False)


print("Demographic data exported successfully!")
print("Next, run: 04_assessment-table.py")
print('===========================================')
