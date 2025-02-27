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

    # Fill any remaining nulls in dummy variables with 0
    model_df[dummies.columns] = model_df[dummies.columns].fillna(0)

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

    # Fill any remaining nulls in dummy variable with 0
    model_df[f"{dummy_name}_y"] = model_df[f"{dummy_name}_y"].fillna(0)

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
    student_tables = pickle.load(f)

# Begin the for loop to process all the years of data
for year in years:
    ######################################################################################################################################################
    # Retrieve the data for the specified year from the student_tables dictionary
    student_table = student_tables[year]

    # df will represent the exploratory data, and model_df will represent the model data
    # Create the df from the student_table student_numbers
    df = student_table[['student_number']].copy()

    # Create the model_df from the student_table student_numbers
    model_df = student_table[['student_number']].copy()


    ######################################################################################################################################################
    # Define the list of categorical columns to process using the function above (process_categorical_column)
    categorical_columns = [
        ('Gender', 'gender'),
        ('LimitedEnglish', 'limited_english'),
        ('HighSchlComplStatus', 'hs_complete_status'),
        ('ExitCode', 'exit_code'),
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
        ('Services504', 'services_504'),
        ('MilitaryChild', 'military_child'),
        ('RefugeeStudent', 'refugee_student'),
        ('Immigrant', 'immigrant'),
        ('ReadingIntervention', 'reading_intervention'),
        ('PassedCivicsExam', 'passed_civics_exam'),
        ('ReadGradeLevel', 'read_grade_level'),
        ('Gifted', 'gifted')
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
    # TODO I am still unsure of the best way format the dates, possibly a count since a specific date or something else.
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
    # Add HomeStatus and PartTimeHomeSchool to the df and model_df
    # These columns will be grouped differently later in the script, so they are handled separately here.  
    
    # Create a DataFrame that only contains student_number from the student_table
    extra_columns = student_table[['student_number']].copy()

    # Check if HomeStatus is available for the current year and merge it. Print a message if it's missing.
    if 'HomeStatus' in student_table.columns:
        extra_columns = extra_columns.merge(student_table[['student_number', 'HomeStatus']], on='student_number', how='left')
    else:
        print(f"Column 'HomeStatus' not found in the '{year}' student_table. Skipping...")

    # Check if PartTimeHomeSchool is available for the current year and merge it. Print a message if it's missing.
    if 'PartTimeHomeSchool' in student_table.columns:
        extra_columns = extra_columns.merge(student_table[['student_number', 'PartTimeHomeSchool']], on='student_number', how='left')
    else:
        print(f"Column 'PartTimeHomeSchool' not found in the '{year}' student_table. Skipping...")

    # Rename columns for consistency
    extra_columns = extra_columns.rename(columns={
        'HomeStatus': 'home_status',
        'PartTimeHomeSchool': 'part_time_home_school'
    })

    # Make sure student_number is a string
    extra_columns['student_number'] = extra_columns['student_number'].astype(str)
    df['student_number'] = df['student_number'].astype(str)
    model_df['student_number'] = model_df['student_number'].astype(str)

    # Merge into df and model_df
    df = pd.merge(df, extra_columns, on='student_number', how='left')
    model_df = pd.merge(model_df, extra_columns, on='student_number', how='left')


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

earliest_dates.fillna(0, inplace=True)
earliest_dates.head()

# Merge the earliest dates into model_df
model_df = pd.merge(model_df, earliest_dates, on='student_number', how='left')

# Preview the updated model_df
model_df.head()


######################################################################################################################################################
# The following code processes the 'home_status' column to indicate student homelessness status.
#
# HomeStatus codes:
# 0 - Not homeless
# 1 - Living with family due to economic hardship
# 2 - Living in a motel or hotel
# 3 - Living in a shelter (emergency, transitional, or domestic violence)
# 4 - Living in a car, park, campground, or public place
# 5 - Without adequate facilities (running water, heat, electricity)
#
# Key tasks performed in this script:
# - Creates a binary indicator 'homeless_y' (1 if home_status was ever > 0, otherwise 0)
# - df retains 'homeless_y' for each specific year (multiple rows per student)
# - model_df retains 'homeless_y' if a student was ever homeless (one row per student)
#
# df and model_df both merge with home_status_df:
# - df merges **before** dropping duplicates (to retain yearly homeless status)
# - model_df merges **after** dropping duplicates (ensuring only one row per student)

# Extract relavant columns
home_status_df = concat_model[['student_number', 'home_status']].copy()

# Make sure home_status values are numbers and also fill null values with 0
home_status_df['home_status'] = pd.to_numeric(home_status_df['home_status'], errors='coerce').fillna(0)

# Create a column 'homeless_y'. If a student had a home_status that was not 0 homeless_y = 1
home_status_df['homeless_y'] = (home_status_df['home_status'] != 0).astype(int)

# Sort by home_status in descening order
home_status_df = home_status_df.sort_values(by='home_status', ascending=False)

# Drop home_status column as it is no longer needed
home_status_df = home_status_df.drop(columns=['home_status'])

# Make sure student_number is a string
home_status_df['student_number'] = home_status_df['student_number'].astype(str)
df['student_number'] = df['student_number'].astype(str)
model_df['student_number'] = model_df['student_number'].astype(str)

#=================================================================
# Before dropping duplicates, merge home_status_df with df
df = pd.merge(df, home_status_df, on='student_number', how='left')

# Drop home_status from the df
df = df.drop(columns=['home_status'])
#=================================================================

# Drop duplicates, keeping the first occurrence (which will be homeless if applicable)
home_status_df = home_status_df.drop_duplicates(subset=['student_number'], keep='first')

# home_status_df now only contains one row per student_number, so we can now merge with model_df
model_df = pd.merge(model_df, home_status_df, on='student_number', how='left')

model_df.head()
df.head()


######################################################################################################################################################
# Processing part_time_home_school column:
# - H = Home School
# - P = Private School
# - S = "Stable" (Part-time but not Home/Private School)
# - Creates 'part_time_home_school_y' (1 if a student was ever in part-time home school, else 0)
# - df retains part-time home school status per year (multiple rows per student)
# - model_df retains part-time home school status if a student was ever enrolled (one row per student)

# Extract only relevant columns and make a copy
part_time_home_df = concat_model[['student_number', 'part_time_home_school']].copy()

# Create part_time_home_school_y column (1 if part_time_home_school is not null, else 0)
part_time_home_df['part_time_home_school_y'] = part_time_home_df['part_time_home_school'].notna().astype(int)

# Sort by part_time_home_school_y in descending order to prioritize students with part-time home school history
part_time_home_df = part_time_home_df.sort_values(by='part_time_home_school_y', ascending=False)

# Drop home_status column as it is no longer needed
part_time_home_df = part_time_home_df.drop(columns=['part_time_home_school'])

# Convert student_number to string for consistency
part_time_home_df['student_number'] = part_time_home_df['student_number'].astype(str)

#=================================================================
# Before dropping duplicates, merge part_time_home_df with df
df = pd.merge(df, part_time_home_df[['student_number', 'part_time_home_school_y']], on='student_number', how='left')

# Drop part_time_home_school from the df
df = df.drop(columns=['part_time_home_school'])
#=================================================================

# Drop duplicates, keeping the first occurrence (which is sorted by part_time_home_school_y in descending order)
part_time_home_df = part_time_home_df.drop_duplicates(subset=['student_number'], keep='first')

# Merge part_time_home_df with model_df (after dropping duplicates)
model_df = pd.merge(model_df, part_time_home_df[['student_number', 'part_time_home_school_y']], on='student_number', how='left')

model_df.head()
df.head()


######################################################################################################################################################
# Categorizing students based on ELL status and disability.
# A student is considered to have a disability if regular_percent is 1, 2, or 3.
# A student is classified as ELL if limited_english is 'Y', 'O', or 'F'.
# This will create four distinct groups, stored in a single column (ell_disability_group): 
#   - ell_with_disability
#   - ell_without_disability
#   - non_ell_with_disability
#   - non_ell_without_disability
# This column will contain one of the four group labels.
# The exploratory data will follow the same process, but will assign a group for each year a student_number appears in the data.

#======================================================================================================================================
# The regular_percent columns were originally created in the 02_academic-table.py script.
# They could not be dropped there because they are needed in this script to classify disability status. 
# However, after this script, they are no longer needed and should be removed.

# To properly handle this:
# 1. Load 02_academic_exploratory.csv and 02_academic_modeling.csv, which contain the regular_percent columns.
# 2. Create copies: 
#       a. academic_exploratory_data and academic_modeling_data to retain the original CSV files
#       b. academic_df and academic_model_df to calculate disability_status
# 3. Remove the regular_percent columns from academic_exploratory_data and academic_modeling_data.
# 4. Export the updated academic_exploratory_data and academic_modeling_data files using the same file paths from the 02-script, 
#    ensuring 02_academic_exploratory.csv and 02_academic_modeling.csv no longer contain regular_percent columns.
#    This will be done at the end of the script to avoid any issues.

# Import the academic tables
academic_df = pd.read_csv('data/02_academic_exploratory.csv')
academic_model_df = pd.read_csv('data/02_academic_modeling.csv')

# Create dataframes to store the entire imported csv files
academic_exploratory_data = academic_df.copy()
academic_modeling_data = academic_model_df.copy()

# Drop the regular percent columns from the academic exploratory and modeling data
academic_exploratory_data = academic_exploratory_data.drop(columns=['regular_percent'], errors='ignore')

# Dynamically drop the regular_percent columns from the academic modeling data
academic_modeling_data = academic_modeling_data.drop(
    columns=[col for col in academic_model_df.columns if col.startswith('regular_percent_')], errors='ignore')

#======================================================================================================================================

# Keep only student_number and regular_percent columns
academic_df = academic_df[['student_number', 'regular_percent']].copy()
academic_model_df = academic_model_df[['student_number', 'regular_percent_1.0', 'regular_percent_2.0', 'regular_percent_3.0']].copy()

# Extract ELL status columns from model_df
ell_data = model_df[['student_number', 'limited_english_y', 'limited_english_o', 'limited_english_f']].copy()

# Determine if a student is classified as ELL (1 if 'Y', 'O', or 'F'; otherwise 0)
ell_data["ell_status"] = ell_data[["limited_english_y", "limited_english_o", "limited_english_f"]].max(axis=1)

# Keep only student_number and ell_status
ell_data = ell_data[['student_number', 'ell_status']]

# Extract disability-related columns from academic_model_df
disability_data = academic_model_df.copy()

# Determine if a student has a disability (1 if any of these columns = 1, 2, or 3; otherwise 0)
disability_data["disability_status"] = disability_data[['regular_percent_1.0', 'regular_percent_2.0', 'regular_percent_3.0']].max(axis=1)

# Keep only student_number and disability_status
disability_data = disability_data[['student_number', 'disability_status']]

# Make sure student_number is a string
ell_data['student_number'] = ell_data['student_number'].astype(str)
disability_data['student_number'] = disability_data['student_number'].astype(str)

# Merge ELL and disability data
ell_disability_data = pd.merge(ell_data, disability_data, on='student_number', how='left')

# Create a column to store classification label (ex. 1_0 means ell_without_disability)
ell_disability_data["ell_disability_group"] = (
    ell_disability_data["ell_status"].astype(str) + "_" + ell_disability_data["disability_status"].astype(str)
)

# Define the mapping for group labels (if ell_disability_group = 1_1 then ell_with_disability)
group_mapping = {
    "1_1": "ell_with_disability",
    "1_0": "ell_without_disability",
    "0_1": "non_ell_with_disability",
    "0_0": "non_ell_without_disability",
}

# Apply mapping
ell_disability_data["ell_disability_group"] = ell_disability_data["ell_disability_group"].map(group_mapping)

# Merge into model_df
model_df = pd.merge(model_df, ell_disability_data, on='student_number', how='left')

# ====== Processing Groups for Exploratory Data (row-level not student level) ======
# Process disability status in academic_df
academic_df["disability_status"] = academic_df["regular_percent"].apply(lambda x: 1 if x in [1, 2, 3] else 0)

# Only keep student_number and disability_status
academic_df = academic_df[['student_number', 'disability_status']].copy()

# Make sure student_number is a string
academic_df['student_number'] = academic_df['student_number'].astype(str)

# Merge disability_status from academic_df into df
df = pd.merge(df, academic_df, on='student_number', how='left')

# Process ELL status for exploratory data
# Convert limited_english to uppercase to ensure case consistency
df["limited_english"] = df["limited_english"].astype(str).str.upper()

# If limited_english is 'Y', 'O', or 'F', classify as ELL (1), otherwise (0)
df["ell_status"] = df["limited_english"].apply(lambda x: 1 if x in ['Y', 'O', 'F'] else 0)

# Create ell_disability_group column to store classification labels
df["ell_disability_group"] = df["ell_status"].astype(str) + "_" + df["disability_status"].astype(str)

# Apply mapping
df["ell_disability_group"] = df["ell_disability_group"].map(group_mapping)

model_df.head()
df.head()


######################################################################################################################################################
# Now that all data has been merged, null values need to be addressed.  
# These null values arise because the data comes from multiple years, and not every column exists in every year.  
# When categorical columns are dummy-encoded and merged across different years, some students may not have entries  
# for certain categories, resulting in null values.  
# To handle this, all columns except the date columns (defined below) will have missing values filled with 0.  
# Since date columns have a different format, they need to be handled separately.

# Define the date columns that should NOT be filled with 0
date_columns = ['ell_entry_date', 'entry_date', 'first_enroll_us']

# Identify all columns except date columns
non_date_model_cols = [col for col in model_df.columns if col not in date_columns]
non_date_df_cols = [col for col in df.columns if col not in date_columns]

# Fill NaNs with 0 for all non-date columns
model_df[non_date_model_cols] = model_df[non_date_model_cols].fillna(0)
df[non_date_df_cols] = df[non_date_df_cols].fillna(0)

# Fill NaNs in date columns with 'unknown'
model_df[date_columns] = model_df[date_columns].fillna('unknown')
df[date_columns] = df[date_columns].fillna('unknown')

# The columns below must be exported as strings to prevent them from being loaded as null values in the 07-script.
# These specific columns are the only ones causing issues.
# Ensure columns remain as strings to prevent unintended float conversions
columns_to_fix = ['tribal_affiliation', 'exit_code', 'hs_complete_status']

# Convert columns to strings and ensure missing values remain as '0'
df[columns_to_fix] = df[columns_to_fix].astype(str).replace('nan', '0')


######################################################################################################################################################
# Rename hs_complete_status_gc to hs_advanced_math_y in model_df
model_df = model_df.rename(columns={'hs_complete_status_gq': 'hs_advanced_math_y'})

# Specify the columns to be dropped from the model_df
model_columns_to_drop = ['enviroment_v', 'gender_f', 'ell_entry_date', 'entry_date', 'first_enroll_us', 'gifted_y', 'reading_intervention_y',  
    'tribal_affiliation_nan', 'exit_code_nan', 'read_grade_level_y']
model_columns_to_drop += [col for col in model_df.columns if col.startswith('hs_complete_status_')]

# Make sure the column exists before dropping
model_df = model_df.drop(columns=[col for col in model_columns_to_drop if col in model_df.columns], errors='ignore')

######################################################################################################################################################
# Prepare the data for export 

# Specify the column order for the df
df_columns = ['student_number', 'gender', 'ethnicity', 'amerindian_alaskan', 'asian', 'black_african_amer', 
            'hawaiian_pacific_isl', 'white', 'migrant', 'military_child', 'refugee_student',
            'services_504', 'immigrant', 'passed_civics_exam', 'reading_intervention', 'homeless_y', 'part_time_home_school_y', 'ell_disability_group',
            'hs_complete_status', 'tribal_affiliation', 'read_grade_level', 'exit_code', 
            'ell_entry_date', 'entry_date','first_enroll_us']

df = df[df_columns]

# Specify the column order for the model_df
model_columns = (
    ['student_number']+
    [col for col in model_df.columns if col.startswith('gender_')]
    +[
        'ethnicity_y', 'amerindian_alaskan_y', 'asian_y', 'black_african_amer_y', 
        'hawaiian_pacific_isl_y', 'white_y', 'migrant_y', 'military_child_y', 'refugee_student_y', 'homeless_y', 'part_time_home_school_y',
        'services_504_y', 'immigrant_y', 'passed_civics_exam_y', 'ell_disability_group', 'hs_advanced_math_y']
    + [col for col in model_df.columns if col.startswith('ell_with')]
    + [col for col in model_df.columns if col.startswith('tribal_affiliation_')]
    + [col for col in model_df.columns if col.startswith('read_grade_level_')]
    + [col for col in model_df.columns if col.startswith('exit_code_')])

model_df = model_df[model_columns]

model_df.head()
df.head()


######################################################################################################################################################
# Export the data

# Export the updated academic files using the same file paths from the 02-script
academic_exploratory_data.to_csv('data/02_academic_exploratory.csv', index=False)
academic_modeling_data.to_csv('data/02_academic_modeling.csv', index=False)

# Export both files
df.to_csv('./data/03_demographic_exploratory.csv', index=False)
model_df.to_csv('./data/03_demographic_modeling.csv', index=False)


print("Demographic data exported successfully!")
print("Next, run: 04_assessment-table.py")
print('===========================================')

