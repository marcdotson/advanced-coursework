# The code will output two data files: '07_clearinghouse_exploratory_data.csv' and '07_clearinghouse_model_data.csv'
import pandas as pd
import pickle

# Load the clearinghouse data. We have two files, so we will load both and combine them
clearing_old = pd.read_csv('data/Clearing House Data - USU Version.csv').drop_duplicates()
clearing_new = pd.read_csv('data/National Clearinghouse Data - Dec 2024.csv').drop_duplicates()
clearing_new.head()

# Standardize the student ID column name across both datasets for consistency
# - In clearing_old, rename 'Student Identifier' to 'student_number'
# - In clearing_new, rename 'Student Number' to 'student_number'
clearing_old = clearing_old.rename(columns={'Student Identifier': 'student_number'})
clearing_new = clearing_new.rename(columns={'Student Number': 'student_number'})

# Concat both files
clearing = pd.concat([clearing_old, clearing_new], ignore_index=True)

# Drop duplicate rows, to ensure only unique rows remain
clearing = clearing.drop_duplicates()


######################################################################################################################################################

# Load the pickled data (student_tables)
with open('./data/student_data.pkl', 'rb') as f:
    student_tables = pickle.load(f)
years = [2017, 2018, 2022, 2023, 2024, 2025]

# Create empty tables to store yearly data
all_membership = []
all_master = []
all_students = []
all_student_years = [] # This will be used to track years for post and pre-covid data

for year in years:
    master_year = pd.read_excel(f'data/{year} EOY Data - USU.xlsx', sheet_name='Course Master')
    membership_year = pd.read_excel(f'data/{year} EOY Data - USU.xlsx', sheet_name='Course Membership')
    student_year = student_tables[year]
    student_year['year'] = year # This will be used to track years for post and pre-covid data

    all_master.append(master_year[['CollegeGrantingCr', 'WhereTaughtCampus', 'CourseTitle', 'CourseRecordID']].drop_duplicates())
    all_membership.append(membership_year[['StudentNumber', 'ConcurrEnrolled', 'CourseRecordID']].drop_duplicates())
    all_students.append(student_year[['student_number']].drop_duplicates())
    all_student_years.append(student_year[['student_number', 'year']].drop_duplicates()) # This will be used to track years for post and pre-covid data

# Concat all the data from the for loop
master = pd.concat(all_master, ignore_index=True)
membership = pd.concat(all_membership, ignore_index=True)
student = pd.concat(all_students, ignore_index=True)
student_years = pd.concat(all_student_years, ignore_index=True) # This will be used to track years for post and pre-covid data

#==============================================================
# Clean up a few columns from membership table (this will be helpful later in the script)
# Rename StudentNumber to student_number
membership = membership.rename(columns={'StudentNumber': 'student_number'})
# Make sure student_number is a string
membership['student_number'] = membership['student_number'].astype(str)
#==============================================================

# Drop duplicate rows from each DataFrame
master = master.drop_duplicates()
membership = membership.drop_duplicates()
student = student.drop_duplicates()
student_years = student_years.drop_duplicates() # This will be used to track years for post and pre-covid data

#==============================================================
# Create a df named 'student_clearing' that only includes clearinghouse data for the student_numbers we have
# This df will be used throught the scrip
# Make sure student_number is a string
student['student_number'] = student['student_number'].astype(str)
clearing['student_number'] = clearing['student_number'].astype(str)

# Merge student table and clearning table
student_clearing = pd.merge(student, clearing, on='student_number', how='left')

# Convert all column names to lowercase
student_clearing.columns = student_clearing.columns.str.lower()

# Convert enrollment_begin to datetime (first remove the .0 and cast to int) This will be used throught the script
student_clearing['enrollment_begin'] = pd.to_datetime(student_clearing['enrollment_begin'].astype('Int64'), format='%Y%m%d')

# Create model_df and df to left join with at the end of each data engineering step
df = student.copy()
model_df = student.copy()


######################################################################################################################################################
# Create a binary indicator for whether the student started college, and one for if they graduated college
#     - 'start_college_y' will be 1 if 'College_Code/Branch' is not null, else 0
#     - 'college_grad_y' will be 1 if 'graduated' column equals 'Y', else 0

# Create a dataframe named start_college with the columns needed
# Note: 'College_Code/Branch', 'College_Name', and 'College_State' are always either all null or all filled — so we can use any of them to determine college enrollment status.
start_college = student_clearing[['student_number', 'college_code/branch']].copy()

# Create a binary indicator for whether the student started college
start_college['start_college_y'] = start_college['college_code/branch'].notna().astype(int)

# Drop college_code/branch as it is not needed and will create duplicates
start_college = start_college.drop(columns=['college_code/branch'])

# Drop rows where start_college_y is null or 0, keeping only students who attended college
start_college = start_college[start_college['start_college_y'] == 1]

# There are multiple rows per student so drop duplicates
start_college = start_college.drop_duplicates()

# Merge with model_df and df
df = pd.merge(df, start_college, on='student_number', how='left')
model_df = pd.merge(model_df, start_college, on='student_number', how='left')

#=============================================================================
# Create a df to track students college graduation status ('college_grad')
college_grad = student_clearing[['student_number', 'graduated']].copy()

# Create a binary indicator for whether the student graduated from college
college_grad['college_grad_y'] = (college_grad['graduated'] == 'Y').astype(int)

# Drop graduated as it is not needed and will create duplicates
college_grad = college_grad.drop(columns=['graduated'])

# Drop rows where college_grad_y is null or 0, keeping only students who graduated college
college_grad = college_grad[college_grad['college_grad_y'] == 1]

# There are multiple rows per student so drop duplicates
college_grad = college_grad.drop_duplicates()

# Merge with model_df and df
df = pd.merge(df, college_grad, on='student_number', how='left')
model_df = pd.merge(model_df, college_grad, on='student_number', how='left')


######################################################################################################################################################
# Create a grid using student_number as rows and advanced courses course_titles as column headings
# Merge the master and membership table to get a list of advanced courses
ac_list = pd.merge(master, membership, on='CourseRecordID', how='left').drop_duplicates()

# Rename columns
ac_list = ac_list.rename(columns={'CourseTitle': 'course_title'})

# Filter down ac_list to only include advanced courses
ac_list = ac_list[
    (ac_list['CollegeGrantingCr'].notnull()) |
    (ac_list['WhereTaughtCampus'].notnull()) |
    (ac_list['ConcurrEnrolled'] == 'Y') |
    (ac_list['course_title'].str.startswith('AP', na=False)) |
    (ac_list['course_title'].str.startswith('BTEC', na=False))]

# I manually standardized the course_title values in a Excel file, since many entries represented the same course but were labeled slightly differently
# Load the manually cleaned mapping Excel file
mapping_df = pd.read_excel('data/Advanced Course Title Mapping.xlsx')

# Merge the mapping to assign cleaned course titles, this will add a column named clean_course_title to ac_list
ac_list = pd.merge(ac_list, mapping_df, on='course_title', how='left')

# Create a new dataframe that will be used to create a grid (student_number = rows, course_title = columns)
# Note: Using clean_course_title instead of course_number since course numbers can vary across schools
ac_grid = ac_list[['student_number', 'course_title', 'clean_course_title', 'course_subject', 'course_type']].copy()

# Replace spaces with underscores and remove special characters
ac_grid['clean_course_title'] = (
    ac_grid['clean_course_title']
    .str.replace('&', 'and', regex=False)         # Replace & with "and"
    .str.replace('/', '_', regex=False)           # Replace / with "_"
    .str.replace(' ', '_', regex=False)           # Replace spaces with "_"
    .str.replace(r'[^A-Za-z0-9_]', '', regex=True)  # Remove other special characters
)

ac_grid = ac_grid.drop_duplicates(subset=['student_number', 'course_title'])

# Create two grids, one for course_type(AP, BTECH, CE), and one for course_subject(math, science, arts, ect.)
ac_type = ac_grid[['student_number', 'course_type']].copy()
ac_subject = ac_grid[['student_number', 'course_subject']].copy()

# Create the grids (pivot table)
ac_type = ac_type.pivot_table(
    index='student_number',
    columns='course_type',
    aggfunc='size',
    fill_value=0
).astype(int)

ac_subject = ac_subject.pivot_table(
    index='student_number',
    columns='course_subject',
    aggfunc='size',
    fill_value=0
).astype(int)

# Reset the index so student_number becomes a column
ac_type = ac_type.reset_index()
ac_subject = ac_subject.reset_index()

# Remove the column axis name
ac_type.columns.name = None
ac_subject.columns.name = None

# Drop duplicates before the merge
ac_type = ac_type.drop_duplicates()
ac_subject = ac_subject.drop_duplicates()

# Make sure student_number is a string
ac_type['student_number'] = ac_type['student_number'].astype(str)
ac_subject['student_number'] = ac_subject['student_number'].astype(str)

# Join the grids with the student_table to include all student_numbers not just student_numbers for students who have taken an advanced Course
ac_type = pd.merge(student, ac_type, on='student_number', how='left')
ac_subject = pd.merge(student, ac_subject, on='student_number', how='left')

# Drop duplicate rows after the merge
ac_type = ac_type.drop_duplicates()
ac_subject = ac_subject.drop_duplicates()

# Make sure null values are filled with 0
ac_type = ac_type.fillna(0)
ac_subject = ac_subject.fillna(0)

# Merge with the model_df and df
df = pd.merge(df, ac_type, on='student_number', how='left')
df = pd.merge(df, ac_subject, on='student_number', how='left')

model_df = pd.merge(model_df, ac_type, on='student_number', how='left')
model_df = pd.merge(model_df, ac_subject, on='student_number', how='left')


######################################################################################################################################################
# Track postsecondary outcomes for each student which will be used in the df
# - We will create separate grids to capture degrees, majors, and colleges attended
# - Some students have multiple records for each category, so we'll create a grid  where each column (e.g., degree_1 through degree_5) reflects the sequence in which they 
#   earned degrees, declared majors, or attended colleges

#==============================================================
# Degree Grid: degree_1 - degree_5
#==============================================================
# Create a DataFrame to track degrees earned
student_degree = student_clearing[['student_number', 'degree_title', 'enrollment_begin']]

# Drop rows where degree_title is null
student_degree = student_degree[student_degree['degree_title'].notna()]

# Sort rows by enrollment_begin so we can track the order of degrees earned
student_degree = student_degree.sort_values(by='enrollment_begin')

# Drop duplicates before the pivot
student_degree = student_degree.drop_duplicates()

# Create a sequential order of degrees per student
student_degree['degree_sequence'] = student_degree.groupby('student_number').cumcount() + 1

# Pivot so each degree becomes its own column
degree_grid = student_degree.pivot_table(
    index='student_number',
    columns='degree_sequence',
    values='degree_title',
    aggfunc='first'
)

# Rename columns from numbers to 'degree_1', 'degree_2', etc.
degree_grid.columns = [f'degree_{int(col)}' for col in degree_grid.columns]

# Reset index for merging or export
degree_grid = degree_grid.reset_index()

# Make sure null values are filled with 0
degree_grid = degree_grid.fillna(0)

# Drop duplicates before the merge just in case
degree_grid = degree_grid.drop_duplicates()

# Drop duplicate rows just in case
df = pd.merge(df, degree_grid, on='student_number', how='left')

#==============================================================
# Major Grid: major_1 - major_6
#==============================================================
# Create a DataFrame to track majors earned
student_major = student_clearing[['student_number', 'major', 'enrollment_begin']]

# Drop rows where major is null
student_major = student_major[student_major['major'].notna()]

# Sort rows by enrollment_begin so we can track the order of majors declared
student_major = student_major.sort_values(by='enrollment_begin')

# Drop duplicates before the pivot
student_major = student_major.drop_duplicates()

# Create a sequential order of majors per student
student_major['major_sequence'] = student_major.groupby('student_number').cumcount() + 1

# Pivot so each major becomes its own column
major_grid = student_major.pivot_table(
    index='student_number',
    columns='major_sequence',
    values='major',
    aggfunc='first'
)

# Rename columns from numbers to 'major_1', 'major_2', etc.
major_grid.columns = [f'major_{int(col)}' for col in major_grid.columns]

# Reset index for merging or export
major_grid = major_grid.reset_index()

# Make sure null values are filled with 0
major_grid = major_grid.fillna(0)

# Drop duplicates before the merge just in case
major_grid = major_grid.drop_duplicates()

# Merge the major grid back into the main df
df = pd.merge(df, major_grid, on='student_number', how='left')

#==============================================================
# College Grid: college_1 - college_6
#==============================================================
# Create a DataFrame to track colleges attended
student_college = student_clearing[['student_number', 'college_name', 'enrollment_begin', 'college_sequence']].copy()

# Sort by enrollment_begin to ensure the sequence is chronological
student_college = student_college.sort_values(by='enrollment_begin')

# Drop duplicates before the pivot
student_college = student_college.drop_duplicates()

# Pivot the data so each college_sequence becomes its own column
college_grid = student_college.pivot_table(
    index='student_number',
    columns='college_sequence',
    values='college_name',
    aggfunc='first'  # In case of duplicates, just take the first
)

# Rename columns from sequence numbers to 'college_1', 'college_2', etc.
college_grid.columns = [f'college_{int(col)}' for col in college_grid.columns]

# Reset index for merging or export
college_grid = college_grid.reset_index()

# Make sure null values are filled with 0
college_grid = college_grid.fillna(0)

# Drop duplicates before the merge just in case
college_grid = college_grid.drop_duplicates()

# Merge the college grid back into the main df
df = pd.merge(df, college_grid, on='student_number', how='left')


######################################################################################################################################################
# Add logic to identify the most recent high school year per student
# (This will be important if we separate by pre- and post-COVID years in the combined script.)

# Get the most recent year per student from the student table
latest_year = student_years.copy()
latest_year = latest_year.sort_values(by='year', ascending=False)
latest_year = latest_year.drop_duplicates(subset=['student_number'], keep='first')
latest_year['student_number'] = latest_year['student_number'].astype(str)


# Merge with df and model_df
# df = pd.merge(df, latest_year, on='student_number', how='left')
model_df = pd.merge(model_df, latest_year, on='student_number', how='left')


######################################################################################################################################################
# Export data

df.to_csv('./data/07_clearinghouse_exploratory_data.csv', index=False)
model_df.to_csv('./data/07_clearinghouse_model_data.csv', index=False)

print('===========================================')
print('Clearinghouse data exported successfully!')
print("Next, run: 08_combine_data-table.py")
print('===========================================')

