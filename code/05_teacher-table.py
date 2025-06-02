"""
This script has two parts:

----------------------------------
PART 1: School-Level Teacher Grids
----------------------------------
- Combines Course Master and Course Membership data from 2017, 2018, 2022, 2023, and 2024.
- Builds matrices showing which teachers taught at which secondary schools.
- Splits the data into:
    - High schools vs. middle schools
    - All years vs. post-COVID years (2022–2024)
- Each matrix has schools as rows and teachers as columns (1 = taught at that school, 0 = did not).

Files Exported:
- ./data/hs_teacher_data.csv
- ./data/ms_teacher_data.csv
- ./data/hs_post_covid_teacher_data.csv
- ./data/ms_post_covid_teacher_data.csv

----------------------------------
PART 2: Student-Teacher Exposure Grids
----------------------------------
- Uses the same Course Master and Course Membership data as Part 1
- Adds student-level data (from pickled student_tables) to get accurate student_number information
- Also loads academic outcome data from 02_academic_modeling.csv to merge in each student's ac_ind
- Builds:
    - A grid of all students and all teachers
    - A grid of all students and only non-AC teachers
    - A grid for each school showing student exposure to non-AC teachers

Files Exported:
- ./data/all_teacher_grid.csv
- ./data/non_ac_teacher_grid.csv
- ./data/sky_view_non_ac_teacher_grid.csv
- ./data/green_canyon_non_ac_teacher_grid.csv
- ./data/ridgeline_non_ac_teacher_grid.csv
- ./data/mountain_crest_non_ac_teacher_grid.csv
- ./data/cache_high_non_ac_teacher_grid.csv
- ./data/spring_creek_middle_non_ac_teacher_grid.csv
- ./data/north_cache_middle_non_ac_teacher_grid.csv
- ./data/south_cache_middle_non_ac_teacher_grid.csv
"""


import pandas as pd
import pickle

######################################################################################################################################################
# ----------------------------------
# PART 1: School-Level Teacher Grids
# ----------------------------------

# Create lists to collect data across years
all_membership = []
all_master = []

years = [2017, 2018, 2022, 2023, 2024]

for year in years:
    # Load Course Master and Course Membership data for the year
    master_table = pd.read_excel(f'data/{year} EOY Data - USU.xlsx', sheet_name= 'Course Master').drop_duplicates(keep='first')
    membership_table = pd.read_excel(f'data/{year} EOY Data - USU.xlsx', sheet_name= 'Course Membership').drop_duplicates(keep='first')
    membership_table['year'] = year

    # Extract relevant columns and append to lists
    all_master.append(master_table[['Teacher1ID', 'SchoolNumber', 'CourseRecordID']])
    all_membership.append(membership_table[['CourseRecordID', 'year']])

# Combine all years into single DataFrames
master = pd.concat(all_master, ignore_index=True)
membership = pd.concat(all_membership, ignore_index=True)

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

# Number of Schools a Teacher Taught At
#                                 |   1 School  |  >1 School  |  >2 Schools  |  >3 Schools  |  >4 Schools
# --------------------------------|-------------|-------------|--------------|--------------|--------------
#     High School (All Years)     |     320     |     129     |      51      |      8       |      0
#     High School (Post-COVID)    |     143     |      54     |      22      |      1       |      0
#     Middle School (All Years)   |     108     |       6     |       1      |      0       |      0
#     Middle School (Post-COVID)  |      50     |       6     |       1      |      0       |      0



######################################################################################################################################################
# ----------------------------------
# PART 2: Student-Teacher Exposure Grids
# ----------------------------------
# This code creates:
# - A complete grid of all students and all teachers
# - A grid of all students and only non-AC (non-advanced course) teachers
# - Separate grids for each school showing student exposure to non-AC teachers

# Specify the columns and their corresponding data types for each dataset to speed up the concatenation
membership_columns = {'StudentNumber': 'int32', 'CourseRecordID': 'string', 'SchoolNumber': 'int32', 'ConcurrEnrolled': 'string'}
master_columns = {'Teacher1ID': 'int32', 'CourseRecordID': 'string', 'CollegeGrantingCr': 'string', 'WhereTaughtCampus': 'string', 'CourseTitle': 'string'}

# Load the pickled data (student_tables)
with open('./data/student_data.pkl', 'rb') as f:
    student_tables = pickle.load(f)

# Concatenate all years of data for each dataset into single DataFrames
# This combines data from all years to create a complete record of the teachers had by students

# Initialize empty lists to store year-specific DataFrames
all_membership = []
all_master = []
all_student_tables = []

# Loop through each year and load the data and drop duplicates immediatly to clean the data and speed up the loop
for year in years:
    membership_year = pd.read_excel(
        f'data/{year} EOY Data - USU.xlsx', sheet_name='Course Membership', usecols=membership_columns.keys(), dtype=membership_columns
        ).drop_duplicates()
    
    master_year = pd.read_excel(
    f'data/{year} EOY Data - USU.xlsx', sheet_name='Course Master', usecols=master_columns.keys(),dtype=master_columns
    ).drop_duplicates()

    # Retrieve the data for the specified year from the student_tables dictionary
    student_table_year = student_tables[year]
    student_table_year['year'] = year

    # Append year-specific data to the respective lists
    all_membership.append(membership_year)
    all_master.append(master_year)
    all_student_tables.append(student_table_year[['student_number', 'year']])

# Concatenate and clean the DataFrames for each dataset across all years
membership = pd.concat(all_membership, ignore_index=True)
master = pd.concat(all_master, ignore_index=True)
student_table = pd.concat(all_student_tables, ignore_index=True)

# Rename column names in membership table
membership = membership.rename(columns={'StudentNumber': 'student_number', 'CourseRecordID': 'course_record_id', 'SchoolNumber': 'school_number'})
master = master.rename(columns={'Teacher1ID': 'teacher_id', 'CourseRecordID': 'course_record_id'})


######################################################################################################################################################
# Create a master DataFrame named 'teacher_data' that will be used to generate various student–teacher grids.
# This table includes:
# - Whether a teacher is an AC teacher (teacher_ac_ind)
# - The most recent school each teacher taught at (school_name)
# - One row per unique student_number and teacher_id combination

# Create a dataframe that will store all of the information used to create the 'teacher_data' data frame
all_teacher_data = pd.merge(membership, master, on='course_record_id', how='inner')

# Merge with student_table to filter to only students in our dataset and to include the 'year' column
# This is necessary to determine each teacher's most recent school
all_teacher_data = pd.merge(all_teacher_data, student_table, on='student_number', how='inner')

# Create a flag for whether a course is considered an advanced course
all_teacher_data['advanced_course'] = (
    (all_teacher_data['CollegeGrantingCr'].notnull()) | # Check for college credit
    (all_teacher_data['WhereTaughtCampus'].notnull()) | # Check for campus location
    (all_teacher_data['ConcurrEnrolled'] == 'Y') | # Check for concurrent enrollment
    (all_teacher_data['CourseTitle'].str.startswith('AP', na=False)) | # Check for AP courses
    (all_teacher_data['CourseTitle'].str.startswith('BTEC', na=False)) # Check for BTEC courses
).fillna(False).astype(int)

# Group by teacher_id to determine which teachers taught at least one advanced course
teacher_data = all_teacher_data.groupby('teacher_id', as_index=False).agg(
    teacher_ac_ind=('advanced_course', lambda x: 1 if x.sum() > 0 else 0),  # Has at least one advanced course
)

#======================================================================================================================
# Extract relevant columns to determine the most recent school each teacher has taught at
teacher_school = all_teacher_data[['teacher_id', 'school_number', 'year']].copy()

# Sort by year in descending order so the most recent year comes first
teacher_school = teacher_school.sort_values(by='year', ascending=False)

# Keep the most recent school per teacher
teacher_school = teacher_school.drop_duplicates(subset = ['teacher_id'], keep='first')

# Drop the 'year' column since it's no longer needed
teacher_school = teacher_school.drop(columns='year')

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
teacher_school['school_name'] = teacher_school['school_number'].map(school_name_map)

# Now that we have the school name, we can drop the school_number column
teacher_school = teacher_school.drop(columns='school_number')

# Merge with teacher_data table
teacher_data = pd.merge(teacher_data, teacher_school, on='teacher_id', how='left')

# Drop any teachers who don't belong to one of the mapped schools (i.e., those with missing school_name)
teacher_data = teacher_data.dropna(subset='school_name')

#======================================================================================================================
# Create a new DataFrame with only the student–teacher relationships (one row per course/student/teacher)
student_teacher = all_teacher_data[['student_number', 'teacher_id']].copy()

# Filter to keep only those teachers who appear in the cleaned teacher_data (i.e., valid school)
student_teacher = student_teacher[student_teacher['teacher_id'].isin(teacher_data['teacher_id'])]

# Remove duplicate combinations of student_number and teacher_id
student_teacher = student_teacher.drop_duplicates()

# Add a column that indicates if a student has had a teacher (this will help when creating the different grids)
teacher_data['had_teacher'] = 1

# Merge the filtered student_teacher pairs with teacher_data to attach school_name and ac_ind
teacher_data = pd.merge(student_teacher, teacher_data, on='teacher_id', how='left')

#================================================
                # Summary of teacher data
# We have 166 ac teachers and 766 non-ac teachers
# Teacher counts by school:
#         school_name  total_teachers  ac_teachers  non_ac_teachers
#           Ridgeline             198           35              163
#        Green Canyon             164           46              118
#            Sky View             163           43              120
#      Mountain Crest             130           33               97
#  South Cache Middle              98            3               95
#  North Cache Middle              92            4               88
# Spring Creek Middle              67            2               65
#          Cache High              20            0               20


######################################################################################################################################################
# Create student–teacher grids to analyze the relationship between teacher exposure and students' advanced coursework (ac_ind)
# - Grid 1: All teachers and students
# - Grid 2: Non-AC teachers and all students
# - Grids 3–10: Non-AC teachers at each school and all students

# After each grid is created, we will merge in the ac_ind indicator from the academic dataset
# This helps us see how having certain teachers connects to whether students took an ac_course
# Read in the academic data
academic_table = pd.read_csv('data/02_academic_modeling.csv')

# We only want the student_number and ac_ind from this table
ac_ind_table = academic_table[['student_number', 'ac_ind']].copy()

#======================================================================================================================
# Grid creation will be the same for all tables, it will only differ when filtering
# Grid: All teachers and all students
all_teacher_grid = teacher_data[['student_number', 'teacher_id', 'had_teacher']].copy()

all_teacher_grid = all_teacher_grid.pivot_table(
    index='student_number',
    columns='teacher_id',
    values='had_teacher',
    aggfunc='max',      # If multiple matches, take the max (ensures value is 1)
    fill_value=0        # Fill missing entries with 0 (means student didn’t have that teacher)
)
# Rename the columns to make them more descriptive (i.e. teacher_[x])
all_teacher_grid.columns = [f'teacher_{int(col)}' for col in all_teacher_grid.columns]

# Reset the index to include student_number as a column for merging
all_teacher_grid = all_teacher_grid.reset_index()

# Add students ac_ind to the grid
all_teacher_grid = pd.merge(all_teacher_grid, ac_ind_table, on='student_number', how='left')

# Reorder columns: student_number, ac_ind, then everything else
cols = ['student_number', 'ac_ind'] + [col for col in all_teacher_grid.columns if col not in ['student_number', 'ac_ind']]
all_teacher_grid = all_teacher_grid[cols]

all_teacher_grid.head()

#======================================================================================================================
# Grid: Non-AC teachers and all students
non_ac_teacher_data = teacher_data[teacher_data['teacher_ac_ind'] == 0]

non_ac_teacher_grid = non_ac_teacher_data[['student_number', 'teacher_id', 'had_teacher']].copy()

non_ac_teacher_grid = non_ac_teacher_grid.pivot_table(
    index='student_number',
    columns='teacher_id',
    values='had_teacher',
    aggfunc='max',      # If multiple matches, take the max (ensures value is 1)
    fill_value=0        # Fill missing entries with 0 (means student didn’t have that teacher)
)

non_ac_teacher_grid.columns = [f'teacher_{int(col)}' for col in non_ac_teacher_grid.columns]

non_ac_teacher_grid = non_ac_teacher_grid.reset_index()

non_ac_teacher_grid = pd.merge(non_ac_teacher_grid, ac_ind_table, on='student_number', how='left')

cols = ['student_number', 'ac_ind'] + [col for col in non_ac_teacher_grid.columns if col not in ['student_number', 'ac_ind']]
non_ac_teacher_grid = non_ac_teacher_grid[cols]

non_ac_teacher_grid.head()

#======================================================================================================================
# Grids: Non-AC teachers at each school and all students

# List of schools to process
schools = [
    'Sky View',
    'Green Canyon',
    'Ridgeline',
    'Mountain Crest',
    'Cache High',
    'Spring Creek Middle',
    'North Cache Middle',
    'South Cache Middle'
]

# Dictionary to store resulting DataFrames
school_grids = {}

# Loop through each school and create the non-ac teacher grid
for school in schools:
    # Filter to non-AC teachers at the current school
    df = teacher_data[
        (teacher_data['teacher_ac_ind'] == 0) &
        (teacher_data['school_name'] == school)
    ][['student_number', 'teacher_id', 'had_teacher']].copy()

    # Pivot to student × teacher grid
    df = df.pivot_table(
        index='student_number',
        columns='teacher_id',
        values='had_teacher',
        aggfunc='max',
        fill_value=0
    )

    # Rename teacher columns
    df.columns = [f'teacher_{int(col)}' for col in df.columns]

    # Add student_number as a column
    df = df.reset_index()

    # Merge with ac_ind_table
    df = pd.merge(df, ac_ind_table, on='student_number', how='left')

    # Reorder columns
    cols = ['student_number', 'ac_ind'] + [col for col in df.columns if col not in ['student_number', 'ac_ind']]
    df = df[cols]

    # Store the result
    var_name = f"{school.lower().replace(' ', '_')}_grid"
    school_grids[var_name] = df

school_grids['sky_view_grid'].head()
school_grids['green_canyon_grid'].head()
school_grids['ridgeline_grid'].head()
school_grids['mountain_crest_grid'].head()
school_grids['cache_high_grid'].head()
school_grids['spring_creek_middle_grid'].head()
school_grids['north_cache_middle_grid'].head()
school_grids['south_cache_middle_grid'].head()


######################################################################################################################################################
# Export data

# ----------------------------------
# PART 1: School-Level Teacher Grids
# ----------------------------------
high_school_grid.to_csv('data/hs_teacher_data.csv')
middle_school_grid.to_csv('data/ms_teacher_data.csv')
post_high_grid.to_csv('data/hs_post_covid_teacher_data.csv')
post_middle_grid.to_csv('data/ms_post_covid_teacher_data.csv')

# ----------------------------------
# PART 2: Student–Teacher Exposure Grids
# ----------------------------------
all_teacher_grid.to_csv('./data/all_teacher_grid.csv', index=False)
non_ac_teacher_grid.to_csv('./data/non_ac_teacher_grid.csv', index=False)

school_grids['sky_view_grid'].to_csv('./data/sky_view_non_ac_teacher_grid.csv', index=False)
school_grids['green_canyon_grid'].to_csv('./data/green_canyon_non_ac_teacher_grid.csv', index=False)
school_grids['ridgeline_grid'].to_csv('./data/ridgeline_non_ac_teacher_grid.csv', index=False)
school_grids['mountain_crest_grid'].to_csv('./data/mountain_crest_non_ac_teacher_grid.csv', index=False)
school_grids['cache_high_grid'].to_csv('./data/cache_high_non_ac_teacher_grid.csv', index=False)
school_grids['spring_creek_middle_grid'].to_csv('./data/spring_creek_middle_non_ac_teacher_grid.csv', index=False)
school_grids['north_cache_middle_grid'].to_csv('./data/north_cache_middle_non_ac_teacher_grid.csv', index=False)
school_grids['south_cache_middle_grid'].to_csv('./data/south_cache_middle_non_ac_teacher_grid.csv', index=False)

print('===========================================')
print('Teacher data exported successfully!')
print("Next, run: 06_school-table.py")
print('===========================================')
