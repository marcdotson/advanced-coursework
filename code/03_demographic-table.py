import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)

# Data sheets
student = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Student')
master = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Course Master')
membership = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Course Membership')
courses = pd.read_excel('data/2022 EOY Data - USU.xlsx', sheet_name='Transcript Courses')

# Rename 'StudentNumber' to 'student_number'
courses = courses.rename(columns={'StudentNumber': 'student_number'})
membership = membership.rename(columns={'StudentNumber': 'student_number'})
student = student.rename(columns={'StudentNumber': 'student_number'})

# Import student_table and high_school_student (for now)
student_table = pd.read_csv('data/student_table.csv')
high_school_students = pd.read_csv('data/high_school_students.csv')

# Create the df from the high_school_student student_numbers
df = high_school_students[['student_number']]

# Create the model_df from the high_school_student student_numbers
model_df = high_school_students[['student_number']]

###########################################################################

#------------------------------------------------------------------------------------------------------------------------------
# Function to process categorical variable. Add non-dummied columns to df and dummy-coded columns to model_df

# Create a table based on the student_table but that only includes high school students
hs_student_table = student_table[student_table['GradeLevel'] > 8].copy()

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

# Define the list of categorical columns to process
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
    ('EllInstructionType', 'ell_instruction_type'),
    ('ReadGradeLevel', 'read_grade_level')
]

# Process each categorical column using the function
for original_col, new_col in categorical_columns:
    df, model_df = process_categorical_column(df, model_df, hs_student_table, original_col, new_col)

df.head()
model_df.head()


#------------------------------------------------------------------------------------------------------------------------------
# Function to process a column: add to df, replace nulls, and dummy code
def student_binary_columns(df, model_df, reference_table, column_name, dummy_name, key_column='student_number'):
    """
    Processes a binary column from a reference DataFrame by adding the non-dummy column to df
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

# Apply the function to each column
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
    ('PassedCivicsExam', 'passed_civics_exam')
]

# Apply the function to each column in the list
for col, dummy in columns_to_process:
    df, model_df = student_binary_columns(df, model_df, hs_student_table, col, dummy)

# Display the updated model DataFrame
model_df.head()

#------------------------------------------------------------------------------------------------------------------------------
# Add the date columns from the student table to the model_df and the df
# Only use student_numbers of high school students
student_dates = hs_student_table[['student_number', 'EntryDate', 'FirstEnrollInUS', 'EllMonitoredEntryDate']]

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

