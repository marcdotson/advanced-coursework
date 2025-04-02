# This script outputs four data files:
# - hs_teacher_data.csv: matrix showing which high schools each teacher taught at (all years)
# - ms_teacher_data.csv: matrix showing which middle schools each teacher taught at (all years)
# - hs_post_covid_teacher_data.csv: Same as above, but for post-covid years (2022–2024) at high schools
# - ms_post_covid_teacher_data.csv: Same as above, but for post-covid years (2022–2024) at middle schools

import pandas as pd

######################################################################################################################################################
# Load and combine data

# All data comes from the Course Master table and the Course Membership table
# - Course Master contains: Teacher1ID, SchoolNumber, CourseRecordID
# - Course Membership contains: CourseRecordID, CourseEntryDate
#         - CourseEntryDate, which includes the year used for filtering
# - The tables are joined using CourseRecordID

# Create lists to collect data across years
all_membership = []
all_master = []

years = [2017, 2018, 2022, 2023, 2024]

for year in years:
    # Load Course Master and Course Membership data for the year
    master_table = pd.read_excel(f'data/{year} EOY Data - USU.xlsx', sheet_name= 'Course Master').drop_duplicates(keep='first')
    membership_table = pd.read_excel(f'data/{year} EOY Data - USU.xlsx', sheet_name= 'Course Membership').drop_duplicates(keep='first')

    # Extract relevant columns and append to lists
    all_master.append(master_table[['Teacher1ID', 'SchoolNumber', 'CourseRecordID']])
    all_membership.append(membership_table[['CourseRecordID', 'CourseEntryDate']])

# Combine all years into single DataFrames
master = pd.concat(all_master, ignore_index=True)
membership = pd.concat(all_membership, ignore_index=True)


######################################################################################################################################################
# Process and merge data
# Create a column named year that contains the year value from CourseEntryDate
membership['CourseEntryDate'] = pd.to_datetime(membership['CourseEntryDate'].astype(str), format='%Y%m%d', errors='coerce')
membership['year'] = membership['CourseEntryDate'].dt.year

# Drop CourseEntryDate as it is not needed anymore
membership = membership.drop(columns=['CourseEntryDate'])

# Drop duplicates to speed up the merge
master = master.drop_duplicates(keep='first')
membership = membership.drop_duplicates(keep='first')

# Merge the data using CourseRecordID
df = pd.merge(master, membership, on='CourseRecordID', how='left')

# Rename columns and drop CourseRecordID as it was only needed for the merge
df = df.rename(columns={'Teacher1ID': 'teacher_id', 'SchoolNumber': 'school_number'})
df = df.drop(columns=['CourseRecordID'])


######################################################################################################################################################
# Filter and prep data
# Create a list of secondary school numbers
secondary_school_ids = [330, 406, 410, 710, 706, 705, 703, 702]

# Keep records for secondary schools only
df = df[df['school_number'].isin(secondary_school_ids)]

# Keep one row per teacher per school
df = df.drop_duplicates(subset=['teacher_id', 'school_number'], keep='first')

# Remove teachers who did not teach in the years below
all_years = [2017, 2018, 2022, 2023, 2024]
df = df[df['year'].isin(all_years)]

# Map the school numbers to their names
school_name_map = {
    330: "Spring Creek Middle",
    406: "North Cache Middle",
    410: "South Cache Middle",
    702: "Mountain Crest",
    703: "Green Canyon",
    705: "Ridgeline",
    706: "Sky View",
    710: "Cache High"
}

# Create a new column with school names from the map
df['school_name'] = df['school_number'].map(school_name_map)


######################################################################################################################################################
# Split data by high school vs. middle school and by all years vs. post-covid years
# List of middle and high school ids
middle_school_ids = [330, 406, 410]
high_school_ids = [710, 706, 705, 703, 702]

# Create a dataframe to store high school and middle school data
high_school = df[df['school_number'].isin(high_school_ids)]
middle_school = df[df['school_number'].isin(middle_school_ids)]

# Create a dataframe to store post-covid data for high school and middle school
post_covid_years = [2022, 2023, 2024]
post_high = high_school[high_school['year'].isin(post_covid_years)]
post_middle = middle_school[middle_school['year'].isin(post_covid_years)]


######################################################################################################################################################
# Create grids
# Create a grid where school_name is the rows, and teacher_id is the columns
# All years
high_school_grid = pd.crosstab(high_school['school_name'], high_school['teacher_id'])
middle_school_grid = pd.crosstab(middle_school['school_name'], middle_school['teacher_id'])

# Post-covid years
post_high_grid = pd.crosstab(post_high['school_name'], post_high['teacher_id'])
post_middle_grid = pd.crosstab(post_middle['school_name'], post_middle['teacher_id'])

# Remove the index name from all grids
high_school_grid.index.name = None
middle_school_grid.index.name = None
post_high_grid.index.name = None
post_middle_grid.index.name = None

# Rename columns: teacher_[teacher_id]
high_school_grid.columns = [f'teacher_{int(c)}' for c in high_school_grid.columns]
middle_school_grid.columns = [f'teacher_{int(c)}' for c in middle_school_grid.columns]
post_high_grid.columns = [f'teacher_{int(c)}' for c in post_high_grid.columns]
post_middle_grid.columns = [f'teacher_{int(c)}' for c in post_middle_grid.columns]


######################################################################################################################################################
# Export Data
high_school_grid.to_csv('data/hs_teacher_data.csv')
middle_school_grid.to_csv('data/ms_teacher_data.csv')
post_high_grid.to_csv('data/hs_post_covid_teacher_data.csv')
post_middle_grid.to_csv('data/ms_post_covid_teacher_data.csv')

# Number of Schools a Teacher Taught At
#                                 |   1 School  |  >1 School  |  >2 Schools  |  >3 Schools  |  >4 Schools
# --------------------------------|-------------|-------------|--------------|--------------|--------------
#     High School (All Years)     |     320     |     129     |      51      |      8       |      0
#     High School (Post-COVID)    |     143     |      54     |      22      |      1       |      0
#     Middle School (All Years)   |     108     |       6     |       1      |      0       |      0
#     Middle School (Post-COVID)  |      50     |       6     |       1      |      0       |      0




######################################################################################################################################################
######################################################################################################################################################
# Old code
######################################################################################################################################################
######################################################################################################################################################
# # The code will output two data files: 05_teacher_exploratory_data.csv and 05_teacher_modeling_data.csv

# import pandas as pd
# import pickle

# # Define the years to process
# years = [2017, 2018, 2022, 2023, 2024]

# # Specify the columns and their corresponding data types for each dataset to speed up the concatenation
# membership_columns = {'StudentNumber': 'int32', 'CourseRecordID': 'string'}
# master_columns = {'Teacher1ID': 'int32', 'CourseRecordID': 'string'}

# # Load the pickled data (student_tables)
# with open('./data/student_data.pkl', 'rb') as f:
#     student_tables = pickle.load(f)

# # Concatenate all years of data for each dataset into single DataFrames
# # This combines data from all years to create a complete record of the teachers had by students

# # Initialize empty lists to store year-specific DataFrames
# all_membership = []
# all_master = []
# all_student_tables = []

# # Loop through each year and load the data and drop duplicates immediatly to clean the data and speed up the loop
# for year in years:
#     membership_year = pd.read_excel(
#         f'data/{year} EOY Data - USU.xlsx', sheet_name='Course Membership', usecols=membership_columns.keys(), dtype=membership_columns
#         ).drop_duplicates()
    
#     master_year = pd.read_excel(
#     f'data/{year} EOY Data - USU.xlsx', sheet_name='Course Master', usecols=master_columns.keys(),dtype=master_columns
#     ).drop_duplicates()

#     # Retrieve the data for the specified year from the student_tables dictionary
#     student_table_year = student_tables[year]
#     student_table_year['year'] = year

#     # Append year-specific data to the respective lists
#     all_membership.append(membership_year)
#     all_master.append(master_year)
#     all_student_tables.append(student_table_year[['student_number', 'year']])


# ######################################################################################################################################################
# # Concatenate and clean the DataFrames for each dataset across all years
# membership = pd.concat(all_membership, ignore_index=True)
# master = pd.concat(all_master, ignore_index=True)
# student_table = pd.concat(all_student_tables, ignore_index=True)

# # Rename column names in membership table
# membership = membership.rename(columns={'StudentNumber': 'student_number', 'CourseRecordID': 'course_record_id'})
# master = master.rename(columns={'Teacher1ID': 'teacher_id', 'CourseRecordID': 'course_record_id'})

# # Remove all duplicates from the dataframes after the data is concatenated
# membership = membership.drop_duplicates(keep='first')
# master = master.drop_duplicates(keep='first')
# student_table = student_table.drop_duplicates(keep='first')


# ######################################################################################################################################################
# # Merge the different tables to prepare for the pivot
# teacher_student = pd.merge(membership, master, on='course_record_id', how='left')

# # Create the df from the student_table student_numbers
# # - df: exploratory data
# # - model_df: model data
# df = student_table[['student_number', 'year']].copy()
# df = df.drop_duplicates(subset=['student_number', 'year'], keep='first')
# model_df = student_table[['student_number']].copy()
# model_df = model_df.drop_duplicates(keep='first')

# # Left join model_df and teacher_student so we only have student_numbers from the model_df
# # Only include the student_number and teacher_id from the teacher_student table
# teacher_student = pd.merge(model_df, teacher_student[['student_number', 'teacher_id']], on='student_number', how='left')


# ######################################################################################################################################################
# # Pivot the merged table to create a grid of student_numbers by school_number
# teacher_grid = teacher_student.pivot_table(
#     index='student_number',
#     columns='teacher_id',
#     values='teacher_id',  # Use teacher_id to create binary attendance indicators
#     aggfunc=lambda x: 1,     # Set 1 to indicate a student has taken a class from a teacher
#     fill_value=0             # Fill missing values with 0 to indicate no attendance
# )

# # Rename the columns to make them more descriptive (i.e. school_[x])
# teacher_grid.columns = [f'teacher_{int(col)}' for col in teacher_grid.columns]

# # Reset the index to include student_number as a column for merging
# teacher_grid = teacher_grid.reset_index()

# teacher_grid.head()

# # Merge teacher_grid with the model_df
# model_df = pd.merge(model_df, teacher_grid, on='student_number', how='left')

# model_df.head()


# ######################################################################################################################################################
# # Create a list of all the teachers a student has had for the exploratory data
# # This will create a column named teachers_had with a list of all the teachers a student has had for the exploratory data
# student_teacher_list = (
#     teacher_student.groupby('student_number')['teacher_id']
#     .apply(list)  # Aggregate school_number as a list
#     .reset_index()
#     .rename(columns={'teacher_id': 'teachers_had'})
# )

# # Add a column to count the number of teachers each student had
# student_teacher_list['teacher_count'] = teacher_grid.iloc[:, 1:].sum(axis=1)

# # Merge the student_school_list with the df
# df = pd.merge(df, student_teacher_list, on='student_number', how='left')

# df.head()

# # Fill all null values with 0.
# # The null values arise because there are some (290) students_numbers who do not have any recorded teachers.
# model_df.fillna(0, inplace=True)
# df.fillna(0, inplace=True)


# ######################################################################################################################################################
# # Export the data
# df.to_csv('./data/05_teacher_exploratory_data.csv', index=False)
# model_df.to_csv('./data/05_teacher_modeling_data.csv', index=False)

# print('===========================================')
# print('Teacher data exported successfully!')
# print("Next, run: 06_school-table.py")
# print('===========================================')
