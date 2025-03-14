import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings

warnings.filterwarnings("ignore")

# Load the data from CSV files
data = pd.read_csv("../data/exploratory_data.csv")
modeldata = pd.read_csv("../data/modeling_data.csv")

print("CCSD Powerschool Exploratory Data Analysis\n")

# Display years in the dataset
years = data['year'].unique()
print(f"Years in data set: {years}\n")

# Display summary statistics
print("##############################################################################################################")
print("Summary Statistics:")
data.info()
data.describe(include='all')

# Display the count of missing values in each column
print("\nCount of missing values in each column:")
print(data.isna().sum())

# Display the first few rows of the data
print("\nFirst few rows of data:")
print(data.head().to_string(), "\n")

# Display the column names
print("Columns in the data:")
for column in data.columns:
    print(column, end=',\n ')

# District-Wide Analysis
print("##############################################################################################################")
print("District-Wide Analysis\n")

# Academic Data
print("##############################################################################################################")
print("Academic Data from 02_academic_table data\n")

# Count total number of students in data set
total_students = data.shape[0]
print(f"Total number of students: {total_students}")

# Count of students with ac_ind=1
ac_ind_count = data[data['ac_ind'] == 1].shape[0]
print(f"Number of students who have taken an AC course: {ac_ind_count} ({ac_ind_count / total_students:.2f}%)")

# Calculate average overall GPA (excluding 0s)
average_gpa = data['overall_gpa'][data['overall_gpa'] != 0].mean()
print(f"\nAverage overall GPA: {average_gpa:.2f}")

# Average overall GPA of students who have not taken an AC course
non_ac_overall_gpa = round(data[data['ac_ind'] == 0]['overall_gpa'].mean(), 2)
print(f"Average overall GPA for ac_ind = 0 students: {non_ac_overall_gpa}")

# Average overall GPA of students who have taken an AP course
ac_overall_gpa = round(data[data['ac_ind'] == 1]['overall_gpa'].mean(), 2)
print(f"Average overall GPA for ac_ind = 1 students: {ac_overall_gpa}")

# Count how many AC courses a student has taken
avg_ac_count = round(data[data['ac_count'] > 0]['ac_count'].mean(), 2)
print(f"Average number of AC courses taken by students who took AC courses: {avg_ac_count}")

# Extended school year
extended = data['extended_school_year'].value_counts()
print(extended)

# Demographic Data
print("\n##############################################################################################################")
print("Demographic Data from 03_demographic_table - EOY Student Table\n")

# Services 504
service_504 = data['services_504'].value_counts()
print(service_504)

# Count total number of each ethnic group
ethnic_counts = data[['amerindian_alaskan', 'asian', 'black_african_amer', 'hawaiian_pacific_isl', 'white', 'migrant', 'immigrant','refugee_student', 'ethnicity']].apply(pd.Series.value_counts).fillna(0)
print(f"\nTotal number of each ethnic group: {ethnic_counts}")

# Count total number of each ethnic group for students taking AP courses
ethnic_counts_ap = data[data['ac_ind'] == 1][['amerindian_alaskan', 'asian', 'black_african_amer', 'hawaiian_pacific_isl', 'white', 'migrant', 'immigrant', 'refugee_student', 'ethnicity']].apply(pd.Series.value_counts).fillna(0)
print("\nAC Count By Ethnicity:")
print(ethnic_counts_ap['amerindian_alaskan'])
print(ethnic_counts_ap['asian'])
print(ethnic_counts_ap['black_african_amer'])
print(ethnic_counts_ap['hawaiian_pacific_isl'])
print(ethnic_counts_ap['white'])
print(ethnic_counts_ap['migrant'])
print(ethnic_counts_ap['immigrant'])
print(ethnic_counts_ap['refugee_student'])
print(ethnic_counts_ap['ethnicity'])

# Count proportion of gender
print("\nTotal number of each gender:")
gender_counts = data.groupby('gender')['gender'].count()
print(gender_counts)

# Calculate AC enrollment rates by gender
ac_enrollment_by_gender = data[data['ac_ind'] == 1].groupby('gender')['ac_ind'].value_counts()
print("AC counts by gender: \n", ac_enrollment_by_gender)
gender_ac = data[data['ac_ind'] == 1]['gender'].value_counts().sum()
gender_proportion_ac = data[data['ac_ind'] == 1].groupby('gender')['ac_ind'].count() / gender_counts
print(f"\nProportion of each gender taking AC courses:\n{gender_proportion_ac.map('{:.2%}'.format)}")

# Indicators
indicators = [
    'military_child', 'passed_civics_exam', 'read_grade_level',
    'reading_intervention', 'hs_complete_status',
    'tribal_affiliation',
    'read_grade_level'
]

for indicator in indicators:
    print(f"\nCount of each category in {indicator}:")
    print(data[indicator].value_counts())

# Transcript Data
print("##############################################################################################################")
print("Assessment Data from 04_assessment-table script\n")

composite = data['composite_score'].value_counts()
composite = composite[composite.index != 0]
composite.describe()

# Calculate average test composite score in district (excluding zeros)
avg_composite_score = data[data['composite_score'] != 0]['composite_score'].mean()
print(f"Average composite score in the district: {avg_composite_score:.2f}")

# Average test score by AC Status (excluding zeros)
avg_composite_score_ac_1 = data[(data['ac_ind'] == 1) & (data['composite_score'] != 0)]['composite_score'].mean()
avg_composite_score_ac_0 = data[(data['ac_ind'] == 0) & (data['composite_score'] != 0)]['composite_score'].mean()
print(f"Average composite score for students with ac ind =1: {avg_composite_score_ac_1:.2f}")
print(f"Average composite score for students with ac ind =0: {avg_composite_score_ac_0:.2f}")

# Course Master Data
print("\n##############################################################################################################")
print("Teacher Data from 05_teacher-table script\n")

# Not sure that this is accurate*** come back to this
# teacher_columns = [col for col in modeldata.columns if col.startswith('teacher_')]
# # Remove 'teachers_had' and 'teacher_count' from the teacher_columns list
# teacher_columns = [col for col in teacher_columns if col not in ['teachers_had', 'teacher_count']]

# # Calculate correlations for teacher columns with ac_ind = 1
# teacher_correlations = modeldata[modeldata['ac_ind'] == 1][teacher_columns].corrwith(modeldata[modeldata['ac_ind'] == 1]['ac_ind']).sort_values(ascending=False)
# # Display the top 5 correlated teacher features
# top_teacher_features = teacher_correlations.index[:5]  # Get the top 5 features
# print("\nTop 5 correlated teacher features with ac_ind = 1:")
# print(modeldata[top_teacher_features].columns, sep=', ')

# Course Membership Data
print("\n##############################################################################################################")
print("School Data from 06_school-table script")

# Calculate average GPA by school
school_gpa = data.groupby('current_school')['overall_gpa'].mean()
print("\nAverage Overall GPA by school:")

# Calculate average GPA for students taking AC courses by school
print("\nAverage GPA for students taking AC courses by school:")
average_ac_gpa_by_school = data[(data['ac_ind'] == 1) & (data['overall_gpa'] != 0)].groupby('current_school')['overall_gpa'].mean()
print(average_ac_gpa_by_school)

# Total number of AC courses taken in the district
ac_count_district_total = data['ac_count'].sum()
# Number of AC courses taken in each school
school_ac_count = data.groupby('current_school')['ac_count'].sum()
print(f"Number of AC classes in the district: {ac_count_district_total}")
print(f"Number of AC classes in each school:\n{school_ac_count}")
# Total number of AC students in the district
school_ac_students = data[data['ac_ind'] == 1].groupby('current_school')['ac_ind'].count()
# Total number of AC students in the district
district_ac_students = data['ac_ind'].sum()
print(f"Number of AC students in each school:\n{school_ac_students}")
print(f"Number of AC students in the district: {district_ac_students}")

# Calculate the average number of AC students to each non-AC student at each school
average_ac_to_nonac_by_school = (school_ac_students / (school_ac_count - school_ac_students)).sort_values(ascending=False)
print("\nAverage number of AC students to each non-AC student at each school:")

# Filter for specific high schools
high_schools = [706, 705, 703, 702]
average_ac_to_nonac_by_school = average_ac_to_nonac_by_school.loc[high_schools]
print(average_ac_to_nonac_by_school)

# Calculate the average AC classes per AP student by school
average_ac_classes_per_ap_student_by_school = (school_ac_count / school_ac_students).sort_values(ascending=False)
# Filter the average AC classes per AP student by school for specific high schools
average_ac_classes_per_ap_student_by_school = average_ac_classes_per_ap_student_by_school.loc[high_schools]

# Print results
print("\nAverage AC classes per AP student by school:")
print(average_ac_classes_per_ap_student_by_school.sort_values(ascending=False))

# Overall Correlations
print("\n##############################################################################################################")
print("Overall Correlations")

# Drop test scores from modeldata, except for cumulative score
# Rank each column against ac_ind and list the top correlated features
modeldata = modeldata.drop(['english_score', 'reading_score', 'math_score', 'science_score'], axis=1)
modelcorrelations = modeldata.select_dtypes(include=[np.number]).corrwith(modeldata['ac_ind'] == 1).sort_values(ascending=False)
print("\nTop correlated features with ac_ind == 1 from the modeling data:")
print(modelcorrelations.iloc[:10])
