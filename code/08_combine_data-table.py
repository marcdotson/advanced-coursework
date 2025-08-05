# This script has two parts:

# ----------------------------------
# PART 1: Phase One Combine Data
# ----------------------------------
# This code compiles all modeling and exploratory data into four CSV files: 
# 'model_data.csv', 'exploratory_data.csv' for full historical data 
# and 'post_covid_model_data.csv', 'post_covid_exploratory_data.csv' for post-COVID data

# ----------------------------------
# PART 2: Phase Two Combine Data with Clearinghouse Data
# ----------------------------------
# This code compiles all modeling and exploratory data into two CSV files: 
# 'clearinghouse_model_data.csv', 'clearinghouse_explore_data.csv'

import pandas as pd
import pickle

# Define the years to process
years = [2017, 2018, 2022, 2023, 2024, 2025]

# Post Covid years
years_temp = pd.Series(years)
post_covid_years = years_temp[years_temp >= 2022].tolist()

######################################################################################################################################################
# ----------------------------------
# PART 1: Phase One Combine Data
# ----------------------------------

# Load in the modeling datasets that will be joined later
# []_model represents modeling files
academic_model = pd.read_csv('data/02_academic_modeling.csv')
demographic_model = pd.read_csv('data/03_demographic_modeling.csv')
assessment_model = pd.read_csv('data/04_assessment_data.csv')
# teacher_model = pd.read_csv('data/05_teacher_modeling_data.csv')
school_model = pd.read_csv('data/06_school_modeling_data.csv')

# Load in the exploratory datasets that will be joined later
# []_df represents exploratory files
academic_df = pd.read_csv('data/02_academic_exploratory.csv')
demographic_df = pd.read_csv('data/03_demographic_exploratory.csv')
assessment_df = pd.read_csv('data/04_assessment_data.csv')
# teacher_df = pd.read_csv('data/05_teacher_exploratory_data.csv')
school_df = pd.read_csv('data/06_school_exploratory_data.csv')

# Load the pickled data (student_tables)
with open('./data/student_data.pkl', 'rb') as f:
    student_tables = pickle.load(f)

# Function to process student data for given years (so post_covid years and all years can be processed at the same time)
def process_student_data(years, prefix=""):
    """
    Processes student data for the specified years and exports both exploratory and modeling datasets.
    Parameters:
    - years (list): The list of years to process.
    - prefix (str): Optional prefix for output file names (e.g., "post_covid_").
    """

    all_students = []

    for year in years:
        student_table = student_tables[year]
        student_table['year'] = year
        all_students.append(student_table[['student_number', 'year']])

    df = pd.concat(all_students, ignore_index=True).drop_duplicates(subset=['student_number', 'year'], keep='first')
    model_df = df.copy()
    model_df = model_df.drop(columns='year')
    model_df = model_df.drop_duplicates(keep='first')

    # Merge model_df with all modeling datasets
    model_df = pd.merge(model_df, academic_model, on='student_number', how='left')
    model_df = pd.merge(model_df, demographic_model, on='student_number', how='left')
    model_df = pd.merge(model_df, assessment_model, on='student_number', how='left')
    # model_df = pd.merge(model_df, teacher_model, on='student_number', how='left')
    model_df = pd.merge(model_df, school_model, on='student_number', how='left')

    # Merge df with all exploratory datasets
    df = pd.merge(df, academic_df, on=['student_number', 'year'], how='left')
    df = pd.merge(df, demographic_df, on=['student_number', 'year'], how='left')
    df = pd.merge(df, assessment_df, on=['student_number'], how='left')
    # df = pd.merge(df, teacher_df, on=['student_number', 'year'], how='left')
    df = pd.merge(df, school_df, on=['student_number', 'year'], how='left')

    df = df.drop_duplicates(keep='first')
    df.to_csv(f'./data/{prefix}exploratory_data.csv', index=False)
    model_df.to_csv(f'./data/{prefix}modeling_data.csv', index=False)

# Process full historical data
process_student_data(years, prefix="")

# Process post-COVID data
process_student_data(post_covid_years, prefix="post_covid_")

print('===========================================')
print('Data exported successfully!')
print("Part one workflow is complete!")
print('===========================================')

######################################################################################################################################################
# ----------------------------------
# PART 2: Phase Two Combine Data with Clearinghouse Data
# ----------------------------------

# Load in the modeling datasets that will be joined later
# []_model represents modeling files
academic_model = pd.read_csv('data/02_academic_modeling.csv')
demographic_model = pd.read_csv('data/03_demographic_modeling.csv')
assessment_model = pd.read_csv('data/04_assessment_data.csv')
# teacher_model = pd.read_csv('data/05_teacher_modeling_data.csv')
school_model = pd.read_csv('data/06_school_modeling_data.csv')
clearinghouse_model = pd.read_csv('data/07_clearinghouse_model_data.csv')

# Load in the exploratory datasets that will be joined later
# []_df represents exploratory files
academic_df = pd.read_csv('data/02_academic_exploratory.csv')
demographic_df = pd.read_csv('data/03_demographic_exploratory.csv')
assessment_df = pd.read_csv('data/04_assessment_data.csv')
# teacher_df = pd.read_csv('data/05_teacher_exploratory_data.csv')
school_df = pd.read_csv('data/06_school_exploratory_data.csv')
clearinghouse_df = pd.read_csv('data/07_clearinghouse_exploratory_data.csv')

# Load the pickled data (student_tables)
with open('./data/student_data.pkl', 'rb') as f:
    student_tables = pickle.load(f)

# Drop ac_ind from academic_model and academic_df
academic_df = academic_df.drop(columns='ac_ind')
academic_model = academic_model.drop(columns='ac_ind')

all_students = []

for year in years:
    student_table = student_tables[year]
    student_table['year'] = year
    all_students.append(student_table[['student_number', 'year']])

df = pd.concat(all_students, ignore_index=True).drop_duplicates(subset=['student_number', 'year'], keep='first')
model_df = df.copy()
model_df = model_df.drop(columns='year')
model_df = model_df.drop_duplicates(keep='first')

# Merge model_df with all modeling datasets
model_df = pd.merge(model_df, academic_model, on='student_number', how='left')
model_df = pd.merge(model_df, demographic_model, on='student_number', how='left')
model_df = pd.merge(model_df, assessment_model, on='student_number', how='left')
# model_df = pd.merge(model_df, teacher_model, on='student_number', how='left')
model_df = pd.merge(model_df, school_model, on='student_number', how='left')
model_df = pd.merge(model_df, clearinghouse_model, on='student_number', how='left')

# Merge df with all exploratory datasets
df = pd.merge(df, academic_df, on=['student_number', 'year'], how='left')
df = pd.merge(df, demographic_df, on=['student_number', 'year'], how='left')
df = pd.merge(df, assessment_df, on=['student_number'], how='left')
# df = pd.merge(df, teacher_df, on=['student_number', 'year'], how='left')
df = pd.merge(df, school_df, on=['student_number', 'year'], how='left')
df = pd.merge(df, clearinghouse_df, on=['student_number'], how='left')

df = df.drop_duplicates(keep='first')
df = df.fillna(0)
model_df = model_df.fillna(0)

######################################################################################################################################################
# Process pre-covid years for modeling data
# pre_covid_model = model_df[model_df['year'] < 2020].copy()

# # The target variable for pre-covid data is 'graduated_college_y', so drop 'start_college_y'
# # The 'year' column in the modeling data was only needed to filter between pre and post-covid, so it can be dropped
# pre_covid_model = pre_covid_model.drop(columns=['start_college_y', 'year'])

# # Check for columns with all null values after rows have been filtered
# null_cols_pre = pre_covid_model.columns[pre_covid_model.isnull().all()]

# # If there are null columns, print which columns are null
# if not null_cols_pre.empty:
#     print("Null columns in pre-covid modeling data:", list(null_cols_pre))

# Export post-covid model data
# pre_covid_model.to_csv('/data/pre_covid_clearinghouse_model_data.csv')

######################################################################################################################################################
# Process post-covid years for modeling data
# post_covid_model = model_df[model_df['year'] >= 2020].copy()

# # The target variable for post-covid data is 'start_college_y', so drop 'college_grad_y'
# # The 'year' column in the modeling data was only needed to filter between pre and post-covid, so it can be dropped
# post_covid_model = post_covid_model.drop(columns=['college_grad_y', 'year'])

# # Check for columns with all null values after rows have been filtered
# null_cols_post = post_covid_model.columns[post_covid_model.isnull().all()]

# # If there are null columns, print which columns are null
# if not null_cols_post.empty:
#     print("Null columns in post-covid modeling data:", list(null_cols_post))

# Export post-covid model data
# post_covid_model.to_csv('/data/post_covid_clearinghouse_model_data.csv')

######################################################################################################################################################
# Export the data that includes all years

df.to_csv('data/clearinghouse_exploratory_data.csv')
model_df.to_csv('data/clearinghouse_model_data.csv')

print('===========================================')
print('Data exported successfully!')
print("Part two workflow is complete!")
print('===========================================')

