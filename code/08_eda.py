import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# Load the data from a CSV file
data = pd.read_csv("../data/exploratory_data.csv")
modeldata = pd.read_csv("../data/modeling_data.csv")

print("CCSD Powerschool Exploratory Data Analysis\n")

years = data['year'].unique()
print(f"Years in data set: {years}\n", sep=', ')

# Summary Statistics
print("##############################################################################################################")
print("Summary Statistics:")

data.info()
data.describe(include='all')

# # Display the count of missing values in each column
# print("\nCount of missing values in each column:")
# print(data.isna().sum())

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

# columns i still need to evaluate:
# current_grade
# scram_membership
    #days on disability list
# environment

# Count total number of students in data set
total_students = data.shape[0]
print(f"Total number of students: {total_students}")

# Count of students with ac_ind=1
ac_ind_count = data[data['ac_ind'] == 1].shape[0]
print(f"Number of students who have taken an AC course: {ac_ind_count} ( {ac_ind_count / total_students:.2f}% )")

 #Pie chart -  AC vs non-AC students
plt.figure(figsize=(8, 6))
ac_counts = data['ac_ind'].value_counts()
labels = ['Non-AC', 'AC']
sizes = [ac_counts[0], ac_counts[1]]
colors = ['blue', 'steelblue']
print("Distribution of Advanced Coursework Students in the District:")
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
plt.title('Distribution of AC and Non-AC Students')
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.show()

#Name this better****
# Count of how many AC courses a student has taken
avg_ac_count = round(data[data['ac_count'] > 0]['ac_count'].mean(), 2)
print(f"Average number of AC courses taken by students who took AC courses: {avg_ac_count}")

# Calculate average overall GPA (excluding 0s)
average_gpa = data['overall_gpa'][data['overall_gpa'] != 0].mean()
print(f"\nAverage overall GPA: {average_gpa:.2f}")

#Average overall GPA of students who have not taken an AC course
non_ac_overall_gpa = round(data[data['ac_ind'] == 0]['overall_gpa'].mean(), 2)
print(f"Average overall GPA for ac_ind = 0 students: {non_ac_overall_gpa}")

# Average overall GPA of students who have taken an AP course
ac_overall_gpa = round(data[data['ac_ind'] == 1]['overall_gpa'].mean(), 2)
print(f"Average overall GPA for ac_ind = 1 students: {ac_overall_gpa}")

# # Drop all zeros in ac gpa (fail, pass, na)
filtered_ac_gpa = data['ac_gpa'][data['ac_gpa'] > 0]
plt.figure(figsize=(8, 6))
plt.hist(filtered_ac_gpa, bins=np.arange(0.0, 4.1, 0.5), color='blue', edgecolor='black')
plt.title('AC GPA Distribution')
plt.xlabel('AC GPA')
plt.ylabel('Frequency')
plt.show()
# Box plot - overall GPA by ac_ind, excluding zero GPAs
plt.figure(figsize=(8, 6))
sns.boxplot(x="overall_gpa", y="ac_ind", data=data[(data['ac_ind'].isin([0, 1])) & (data['overall_gpa'] > 0)], palette=['skyblue', 'navy'], orient='h')
plt.title('Overall GPA Distribution by AC Course Status (Excluding Zero GPAs)')
plt.xlabel('Overall GPA')
plt.ylabel('AC Course Status')
plt.xlim(0, 4)  # Set x-axis range from 0 to 4
plt.yticks([0, 1], ['Non-AC', 'AC'])  # Set y-axis labels
plt.show()

# Scatter plot - overall GPA vs AC course status
plt.figure(figsize=(8, 6))
sns.scatterplot(x="overall_gpa", y="ac_count", data=data[data['ac_ind'].isin([0,1]) & (data['overall_gpa'] > 0)], hue="ac_ind", palette=['skyblue', 'navy'])
plt.title('Scatter Plot of Overall GPA vs AC Course Status')
plt.xlabel('Overall GPA')
plt.ylabel('AC Count')
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles=handles, title='AC Course Status', loc='upper right', labels=['Non-AC', 'AC'], facecolor='lightgrey', markerscale=1.5)
plt.show()

# Did not use model percent days attended because there were errors
# Establish variable
data['percent_days_attended'] = np.nan

# Perform the calculation only where school_membership is greater than zero
data.loc[data['school_membership'] > 0, 'percent_days_attended'] = \
    (data['days_attended'] / data['school_membership']) * 100

# Convert to numeric and round to 2 decimal places
data['percent_days_attended'] = pd.to_numeric(data['percent_days_attended'], errors='coerce')
data['percent_days_attended'] = data['percent_days_attended'].round(2)

# Average percent days attended in district
avg_percent_days_attended = round(data['percent_days_attended'].mean(), 2)
print(f"\nAverage percent days attended in district: {avg_percent_days_attended:.2f}%")

# Average percent days attended for students who have taken an AC course
avg_ac_percent_days_attended = round(data[data['ac_ind'] == 1]['percent_days_attended'].mean(), 2)
print(f"Average percent days attended for AC students: {avg_ac_percent_days_attended:.2f}%")

# regular_percent
regularpercent_3 = data[(data['regular_percent'] == 3) & (data['ac_ind'] == 1)].shape[0]
regularpercent_2 = data[(data['regular_percent'] == 2) & (data['ac_ind'] == 1)].shape[0]
regularpercent_1 = data[(data['regular_percent'] == 1) & (data['ac_ind'] == 1)].shape[0]
print(f"Number of students in each regularpercent category with ac_ind=1:\n1: ", regularpercent_1, "\n2: ", regularpercent_2, "\n3: ", regularpercent_3)

is_one_percent = data['is_one_percent'].value_counts()
print(is_one_percent)

extended = data['extended_school_year'].value_counts()
print(extended)


# Demographic Data
print("\n##############################################################################################################")
print("Demographic Data from 03_demographic_table - EOY Student Table\n")

# still need to evaluate these columns:
# ell_instruction_type
# ell_entry_date
    # how could we even use this??? maybe calculate diff between us enrollment and current year?
# first_enroll_us

# gifted
gifted = data['gifted'].value_counts()
print(gifted)
#print(f"\nNumber of gifted students: {gifted}, proportion: {gifted / total_students:.2f}")

# services_504
service_504 = data['services_504'].value_counts()
print(service_504)
#print(f"Number of services_504 students: {service_504}, proportion: {service_504 / total_students:.2f}")

#Count total number of each ethnic group in district, ethnicity column represents hispanic
#ethnic_counts = data[['amerindian_alaskan', 'asian', 'black_african_amer', 'hawaiian_pacific_isl', 'white', 'migrant', 'immigrant','refugee_student', 'ethnicity']].apply(pd.Series.value_counts).fillna(0)
#print(f"\nTotal number of each ethnic group: {ethnic_counts}")
# Visualize the amount of 'Y' for each ethnic group
plt.figure(figsize=(10, 6))
ethnic_counts = data[['amerindian_alaskan', 'asian', 'black_african_amer', 'hawaiian_pacific_isl', 'white', 'migrant', 'immigrant', 'refugee_student', 'ethnicity']].apply(pd.Series.value_counts).fillna(0)
ethnic_counts.loc['Y'].plot(kind='bar', color='steelblue')
plt.title('Amount of Students for Each Ethnic Group')
plt.xlabel('Ethnic Group')
plt.ylabel('Count of Ethnicity')
plt.xticks(rotation=45)
for p in plt.gca().patches:
    plt.text(p.get_x() + (p.get_width() / 2), p.get_y() + (p.get_height() / 2), '{:.0f}'.format(p.get_height()), ha='center')
plt.show()

# Count total number of each ethnic group for students taking AP courses
ethnic_counts_ap = data[data['ac_ind'] == 1][['amerindian_alaskan', 'asian', 'black_african_amer', 'hawaiian_pacific_isl', 'white', 'migrant', 'immigrant', 'refugee_student', 'ethnicity']].apply(pd.Series.value_counts).fillna(0)
# print("\nAC Count By Ethnicity:")
# print(ethnic_counts_ap['amerindian_alaskan'])
# print(ethnic_counts_ap['asian'])
# print(ethnic_counts_ap['black_african_amer'])
# print(ethnic_counts_ap['hawaiian_pacific_isl'])
# print(ethnic_counts_ap['white'])
# print(ethnic_counts_ap['migrant'])
# print(ethnic_counts_ap['immigrant'])
# print(ethnic_counts_ap['refugee_student'])
# print(ethnic_counts_ap['ethnicity'])
# Visualize the amount of 'Y' for each ethnic group taking an AC course
plt.figure(figsize=(10, 6))
ethnic_counts_ap.loc['Y'].plot(kind='bar', color='steelblue')
plt.title('AC Count By Ethnicity')
plt.xlabel('Ethnic Group')
plt.ylabel('Count of Ethnicity')
plt.xticks(rotation=45)
for p in plt.gca().patches:
    plt.text(p.get_x() + (p.get_width() / 2), p.get_y() + (p.get_height() / 2), '{:.0f}'.format(p.get_height()), ha='center')
plt.show()

# Count total number of each gender in district
print("\nTotal number of each gender:")
gender_counts = data.groupby('gender')['gender'].count()
print(gender_counts)
# Examine AC enrollment rates by gender
ac_enrollment_by_gender = data[data['ac_ind'] == 1].groupby('gender')['ac_ind'].value_counts()
print("AC counts by gender: \n", ac_enrollment_by_gender)
gender_ac = data[data['ac_ind'] == 1]['gender'].value_counts().sum()
gender_proportion_ac = data[data['ac_ind'] == 1].groupby('gender')['ac_ind'].count() / gender_counts
print(f"\nProportion of each gender taking AC courses:\n{gender_proportion_ac.map('{:.2%}'.format)}")

# # Histogram = AC by gender
# plt.figure(figsize=(10, 6))
# ac_enrollment_by_gender = data[data['ac_ind'] == 1].groupby('gender')['ac_ind'].value_counts()
# ac_enrollment_by_gender.plot(kind='bar', color='steelblue')
# plt.title('AC Count By Gender')
# plt.xlabel('Gender')
# plt.ylabel('Count of Gender')
# plt.xticks(rotation=45)
# plt.xticks([0,1,2], ['Female', 'Male', 'Unknown'])
# for p in plt.gca().patches:
#     plt.text(p.get_x() + (p.get_width() / 2), p.get_y() + (p.get_height() / 2), '{:.0f}'.format(p.get_height()), ha='center')
# plt.show()

indicators = [
    'military_child', 'passed_civics_exam', 'read_grade_level',
    'reading_intervention', 'home_status', 'hs_complete_status', 'part_time_home_school',
    'tribal_affiliation', 'limited_english', 'ell_native_language', 'ell_parent_language',
    'read_grade_level'
]

#data[indicators] = data[indicators].astype
#indicator_counts = data[indicators].apply(pd.Series.value_counts).sum(axis=1)
for indicator in indicators:
    print(f"\nCount of each category in {indicator}:")
    print(data[indicator].value_counts())
    #print(f"\nPercentage of {indicator} that have taken an AC course:")
    #print(data[data['ac_ind'] == 1][indicator].value_counts() / (data[indicator].value_counts()) * 100)

# Transcript Data
print("##############################################################################################################")
print("Assessment Data from 04_assessment-table script\n")

# Calculate average test composite scores for both groups
data['composite_score'] = data['composite_score'] != 0
avg_composite_score = data['composite_score'].mean()

print(f"Average composite score in the district: {avg_composite_score:.2f}")
#print(f"Average composite score for students with ac ind =1: {data[data['ac_ind'] == 1]['composite_score'].mean(): .2f}")
#print(f"Average composite score for students with ac ind =0: {data[data['ac_ind'] == 0]['composite_score'].mean(): .2f}")


# Course Master Data
print("\n##############################################################################################################")
print("Teacher Data from 05_teacher-table script\n")

teacher_columns = [col for col in modeldata.columns if col.startswith('teacher_')]
# Remove 'teachers_had' and 'teacher_count' from the teacher_columns list
teacher_columns = [col for col in teacher_columns if col not in ['teachers_had', 'teacher_count']]

#so lost lol
# # Calculate correlations for teacher columns with ac_ind = 1
# teacher_correlations = data[data['ac_ind'] == 1][teacher_columns].corrwith(data[data['ac_ind'] == 1]['ac_ind']).sort_values(ascending=False)
# # Display the top 5 correlated teacher features
# top_teacher_features = teacher_correlations.index[:5]  # Get the top 5 features
# print("\nTop 5 correlated teacher features with ac_ind = 1:")
# print(data[top_teacher_features].columns, sep=', ')
 
# Calculate correlations for teacher columns with ac_ind = 1
teacher_correlations = modeldata[modeldata['ac_ind'] == 1][teacher_columns].corrwith(modeldata[modeldata['ac_ind'] == 1]['ac_ind']).sort_values(ascending=False)
# Display the top 5 correlated teacher features
top_teacher_features = teacher_correlations.index[:5]  # Get the top 5 features
print("\nTop 5 correlated teacher features with ac_ind = 1:")
print(modeldata[top_teacher_features].columns, sep=', ')

 # Course Membership Data
print("\n##############################################################################################################")
print("School Data from 06_school-table script\n")

# still need to evaluate these columns:
# schools attended
# current_school

# Extract teacher and school columns for correlation analysis
school_columns = [col for col in modeldata.columns if col.startswith('school_') and col != 'school_membership']

# Calculate correlations for school columns and ac_ind  
school_correlations = modeldata[modeldata['ac_ind'] == 1][school_columns + ['ac_ind']].corr()['ac_ind'].sort_values(ascending=False)
top_school_features = school_correlations.index[:5]  # Get the top 5 features
print("\nTop 5 correlated school features with ac_ind = 1:")
print(modeldata[top_school_features].columns, sep=', ')

# Overall Correlations
print("\n##############################################################################################################")
print("Overall Correlations\n")

# Drop test scores from modeldata, excep tof rcumulative score
# Rank each column against ac_ind and list the top correlated features
modeldata = modeldata.drop(['english_score', 'reading_score', 'math_score', 'science_score'], axis=1)
modelcorrelations = modeldata.select_dtypes(include=[np.number]).corrwith(modeldata['ac_ind'] == 1).sort_values(ascending=False)
print("\nTop correlated features with ac_ind == 1 from the modeling data:")
print(modelcorrelations.iloc[:10])

# # School Analysis
# print("##############################################################################################################")
# print("School Analysis\n")

# Other things to look at:
# How many AC classes each school offers???
    # How many teachers teach AC classes in each school???
    # Days attended distributions by school

# #Count total number of students in each current school
# school_counts = df.filter(like='current_school').sum()
# print("\nTotal number of students in each school:")
# print(school_counts)

# Calculate average GPA by school
school_gpa = data.groupby('current_school')['overall_gpa'].mean()
print("\nAverage Overall GPA by school:")

# Box plot of overall GPA by school
plt.figure(figsize=(10, 6))
sns.boxplot(x='current_school', y='ac_gpa', data=data)
plt.title('AC GPA by School')
plt.xlabel('School')
plt.ylabel('AC GPA')
plt.xticks(rotation=90)
plt.show()


#not sure why it is not working
# # Calculate average GPA for students taking AC courses by school
# print("\nAverage GPA for students taking AC courses by school:")
# average_ac_gpa_by_school = data[(data['ac_ind'] == 1) & (data['overall_gpa'] != 0)].groupby('current_school')['overall_gpa'].mean()
# print(average_ac_gpa_by_school)

# # Visualize the average GPA for students taking AC courses by school
# plt.figure(figsize=(12, 6))
# average_ac_gpa_by_school.plot(kind='bar', color='seagreen')
# plt.title('Average GPA for Students Taking AC Courses by School')
# plt.xlabel('School')
# plt.ylabel('Average GPA')
# plt.xticks(rotation=45)
# plt.show()

#Why is this output confusing???***
# Calculate AC GPA by school and plot
# plt.figure(figsize=(10, 6))
# ac_gpa_by_school = data.groupby('current_school')['ac_gpa'].mean()
# print(ac_gpa_by_school)
# ac_gpa_by_school.plot(kind='bar', color='skyblue')
# plt.title('AC GPA by School')
# plt.xlabel('School')
# plt.ylabel('AC GPA')
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()

#fix the ac count by school vs the ac students by school

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

# Plot the proportion of AC enrollments by school
plt.figure(figsize=(12, 6))
school_ac_count.sort_values(ascending=False).plot(kind='bar', color='seagreen')
plt.title('AC Count by School')
plt.xlabel('School')
plt.ylabel('Number of AC Students')
plt.xticks(rotation=45)
plt.show()

# Plot the proportion of AC enrollments by school
plt.figure(figsize=(12, 6))
school_ac_students.sort_values(ascending=False).plot(kind='bar', color='skyblue')
plt.title('Number of AC Students by School')
plt.xlabel('School')
plt.ylabel('Number of AC Students')
plt.xticks(rotation=45)
plt.show()


# Compute the average AC classes per AP student per school
average_ac_classes_per_ap_student_by_school = school_ac_count / school_ac_students

# Print results
print("\nAverage AC classes per AP student by school:")
print(average_ac_classes_per_ap_student_by_school.sort_values(ascending=False))