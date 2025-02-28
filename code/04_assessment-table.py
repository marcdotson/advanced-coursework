# The code will output one data file: 04_assessment_data.csv
import pandas as pd
import numpy as np
import pickle

# Define the list of years to process
# years = [2017, 2018, 2022, 2023, 2024]

# Post Covid years
years = [2022, 2023, 2024]

# Create an empty dictionary to store the df data for each year
# Only one file will be exported, so df will represent the exploratory and modeling data.
df_dict = {}

######################################################################################################################################################
# Begin the for loop:
# For each year, the logic will:
# 1. Take 'student_number' from the assessment table and perform a left join with 'student_number' 
#    from the corresponding 'student_table[year]' table.
# 2. Filter the data to retain only the highest 'composite_score' per student for that year.
# 3. Store the filtered data in the 'df_dict' dictionary with the key formatted as 'assessment_[year]'.
# 
# After the loop completes:
# - Concatenate the data from all years into a single DataFrame.
# - Further filter the combined data to include only the highest 'composite_score' per student across all years.

# Load the pickled data (student_tables)
with open('./data/student_data.pkl', 'rb') as f:
    student_tables = pickle.load(f)

for year in years:
    # File Paths
    assessment_file = f'data/{year} EOY Data - USU.xlsx'

    # Load Data
    assessment = pd.read_excel(assessment_file, sheet_name='Transcript Assessments')
    
    # Retrieve the data for the specified year from the student_tables dictionary
    student_table = student_tables[year]

    # Rename 'StudentNumber' to 'student_number' in the assessment table
    assessment = assessment.rename(columns={'StudentNumber': 'student_number'})

    df = student_table[['student_number']].copy()

    ######################################################################################################################################################
    # Add the transcript assessment data to the df
    # We only want to include student_numbers that are in the student_table table
    assessment_table = df[['student_number']].copy()

    # Merge the assessment table with the df to return student_numbers from the df
    assessment_table = pd.merge(assessment_table, assessment, on='student_number', how='left')

    # Drop LEANumber from the assessment_table. All values are the same making it useless.
    assessment_table = assessment_table.drop(columns='LEANumber', errors='ignore')

    # Drop all rows where TestName does not begin with ACT. This will filter out SAT scores
    assessment_table = assessment_table[assessment_table['TestName'].str.startswith('ACT', na=False)]

    # Drop the TestName column as all values are the same
    assessment_table.drop(columns='TestName', inplace=True, errors='ignore')

    # Rename columns for consistency
    assessment_table = assessment_table.rename(columns={
        'TestDate': 'test_date',
        'Subtest': 'subtest',
        'TestScore': 'test_score'
    })

    # Ensure test_score is numeric to avoid aggregation issues
    assessment_table['test_score'] = pd.to_numeric(assessment_table['test_score'], errors='coerce')

    # Convert test_date to datetime format (not critical)
    assessment_table['test_date'] = pd.to_datetime(assessment_table['test_date'], errors='coerce')

    # Pivot table to turn subtest values into columns and fill with test scores
    # Include 'test_date' in the pivot index because each test has the same 'test_date' across all its subtests. This means that regardless 
    # of which subtest we reference, the associated 'test_date' will always be the same.

    assessment_grid = assessment_table.pivot_table(
        index=['student_number', 'test_date'],
        columns='subtest',
        values='test_score',
    )

    # Rename new columns created from the pivot for consistency
    assessment_grid = assessment_grid.rename(columns={
        'Composite': 'composite_score',
        'English': 'english_score',
        'Math': 'math_score',
        'Reading': 'reading_score',
        'Science': 'science_score',
        'Writing': 'writing_score'
    })

    # Reset the index to make student_number a column again
    assessment_grid = assessment_grid.reset_index()

    # Make sure student_number is a string
    assessment_grid['student_number'] = assessment_grid['student_number'].astype(str)
    df['student_number'] = df['student_number'].astype(str)

    # Merge assessment_grid into the df
    df = pd.merge(df, assessment_grid, on='student_number', how='left')

    # Some students have taken the ACT multiple times. We only want to keep the row with the highest composite score.
    # Create a list of students with multiple test entries
    duplicates = df[df.duplicated(subset='student_number', keep=False)]

    # Sort the df by highest composite_score
    df = df.sort_values(by='composite_score', ascending=False)

    # Drop all but the row with the highest composite score per student_number
    # Because the df is ordered by composite_score in descending order, we can drop all duplicate rows while keeping the first instance
    df = df.drop_duplicates(subset='student_number', keep='first')

    # Store the resulting DataFrame in a dictionary
    # Results stored as assessment_[year]
    df_dict[f'assessment_{year}'] = df.copy()


######################################################################################################################################################
# Since students may have taken the test multiple times across different years, we will apply the same filtering process as above.
# Concatenate all data into df.
df = pd.concat(df_dict.values(), ignore_index=True)

# We only want to keep the row associated with the highest composite score per student
# Sort df by composite score descending
df = df.sort_values(by = 'composite_score', ascending=False)

# Drop all duplicate rows, and only keep the first instance of the duplicate
df = df.drop_duplicates(subset='student_number', keep = 'first')

# Fill the null values within each column with 0. 
# These null values exist because some students have not taken the ACT yet.
df.fillna(0, inplace=True)

df.head()

######################################################################################################################################################
# Drop test_date column
df = df.drop(columns='test_date')


######################################################################################################################################################
# Export the data
df.to_csv('./data/04_assessment_data.csv', index=False)

print('===========================================')
print("Assessment data exported successfully!")
print("Next, run: 05_teacher-table.py")
print('===========================================')
