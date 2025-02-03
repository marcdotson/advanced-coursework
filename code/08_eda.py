import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings("ignore")

print("Cache County School District")
print("Powerschool Exploratory Data Analysis\n")

# Load the data from a CSV file
data = pd.read_csv("../data/exploratory_data.csv")
modeldata = pd.read_csv("../data/modeling_data.csv")

#****Waiting on current_year and current_school values to do more extensive analysis

# Summary Statistics
#######################################################
print("Summary Statistics:")

# print(data['year'].unique())

# print("model data")
# print(modeldata.columns)
# print(modeldata.head().to_string())

data.describe(include='all')

# Display the first few rows of the data
print("\nFirst few rows of data:")
print(data.head().to_string(), "\n")

# Display the column names
print("Columns in the data:")
print(data.columns)

# Display the count of missing values in each column
print("\nCount of missing values in each column:")
print(data.isna().sum())

# Missing value analysis
#plt.figure(figsize=(8, 6))
print("Missing values:", "\n")
sns.heatmap(data.isnull(), cbar=False)
plt.title('Missing Value Heatmap')
plt.show()

# Count total number of female and male students
gender_counts = data.filter(like='gender_').sum()
print("\nTotal number of female and male students:")
print(gender_counts)

#***Fix this later
# # Count total number of each ethnic group
# ethnic_counts = data.filter(like='ethnicity_').sum()
# ethnic_groups = ['amerindian_alaskan', 'asian', 'black_african_amer', 'hawaiian_pacific_isl', 'white']
# total_ethnic_counts = ethnic_counts[ethnic_groups].sum()
# print("\nTotal number of students in each ethnic group:")
# for group in ethnic_groups:
#     print(f"{group}: {total_ethnic_counts[group]}")
# print("\nTotal number of each ethnic group:")
# print(ethnic_counts)


#EDA Data Distributions
#District-Wide
###################################################################################################

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

# Calculate ac proportion values
ac_proportion = ac_counts[1] / data.shape[0]
print(f"The overall proportion of students who have taken advanced courses (AC) is {ac_proportion:.2%}.")

# Histogram - overall GPA
plt.figure(figsize=(8, 6))
plt.hist(data['overall_gpa'], bins=10, color='blue', edgecolor='black')
plt.title('Overall GPA Distribution')
plt.xlabel('Overall GPA')
plt.ylabel('Students')
plt.xlim(0, 4)  # Set x-axis range from 0 to 4
plt.show()

# Calculate average overall GPA (excluding 0s)
average_gpa = data['overall_gpa'][data['overall_gpa'] != 0].mean()
print(f"\nAverage overall GPA: {average_gpa:.2f}")

# Calculate median overall GPA (excluding 0s)
median_gpa = data['overall_gpa'][data['overall_gpa'] != 0].median()
print(f"Median overall GPA: {median_gpa:.2f}")

# Histogram - days attended
plt.figure(figsize=(8, 6))
plt.hist(data['days_attended'], bins=range(0, 190, 10), color='blue', edgecolor='black')
plt.title('Days Attended Distribution')
plt.xlabel('Days Attended')
plt.ylabel('Frequency')
plt.xlim(0, 180)
plt.show()

# Calculate average days attended
average_days_attended = data['days_attended'].mean()
print(f"\nAverage days attended: {average_days_attended:.2f}")

# Calculate median days attended
median_days_attended = data['days_attended'].median()
print(f"Median days attended: {median_days_attended:.2f}")

# Histogram - ac_gpa
# Drop all zeros in ac gpa (fail, pass, na)
filtered_ac_gpa = data['ac_gpa'][data['ac_gpa'] > 0]
plt.figure(figsize=(8, 6))
plt.hist(filtered_ac_gpa, bins=np.arange(0.0, 4.1, 0.5), color='blue', edgecolor='black')
plt.title('AC GPA Distribution')
plt.xlabel('AC GPA')
plt.ylabel('Frequency')
plt.show()

# Calculate average ac GPA
average_ac_gpa = filtered_ac_gpa.mean()
print(f"\nAverage AC GPA: {average_ac_gpa:.2f}")

# Calculate median ac GPA
median_ac_gpa = filtered_ac_gpa.median()
print(f"Median AC GPA: {median_ac_gpa:.2f}")

# Pair plot for selected numerical variables
numerical_vars = ['overall_gpa', 'days_attended', 'ac_gpa']
sns.pairplot(data[numerical_vars])
plt.suptitle('Pair Plot of Selected Numerical Variables', y=1.02)
plt.show()


#EDA Data Correlation Calculations
#District-Wide
###################################################################################################
print("Correlation Analysis")

#change date columns to numeric values so we can calculate correlation
reference_date = pd.to_datetime('2000-01-01')
data['ell_entry_date'] = pd.to_datetime(data['ell_entry_date'], errors='coerce')
data['first_enroll_us'] = pd.to_datetime(data['first_enroll_us'], errors='coerce')

data['ell_entry_date_num'] = (data['ell_entry_date'] - reference_date).dt.days
data['first_enroll_us_num'] = (data['first_enroll_us'] - reference_date).dt.days

# Drop columns we don't need
datacorr = data.drop(['student_number', 'teacher_count', 'school_count', 'ac_gpa'], axis=1)

# Rank each column against ac_ind and list the top correlated features
correlations = datacorr.select_dtypes(include=[np.number]).corrwith(datacorr['ac_ind']).sort_values(ascending=False)
print("\nTop correlated features with ac_ind:")
print(correlations)

# Extract teacher and school columns for correlation analysis
teacher_columns = [col for col in data.columns if col.startswith('teacher_')]
school_columns = [col for col in data.columns if col.startswith('school_')]

# Calculate correlations for teacher columns and ac_ind
teacher_correlations = data[teacher_columns + ['ac_ind']].corr()['ac_ind'].sort_values(ascending=False)
print("\nTop correlated teacher features with ac_ind:")
print(teacher_correlations)

# Calculate correlations for school columns and ac_ind  
school_correlations = data[school_columns + ['ac_ind']].corr()['ac_ind'].sort_values(ascending=False)
print("\nTop correlated school features with ac_ind:")
print(school_correlations)

# Display the top 5 correlated teacher features 
top_teacher_features = teacher_correlations.index[1:6]  # Exclude ac_ind itself
print("\nTop 5 correlated teacher features with ac_ind:")
print(data[top_teacher_features].head())

# Display the top 5 correlated school features
top_school_features = school_correlations.index[1:6]  # Exclude ac_ind itself
print("\nTop 5 correlated school features with ac_ind:")
print(data[top_school_features].head())

def correlation(data):
    """
    Calculate the correlation between overall_gpa and ac_ind
    """
    corr_coef = data['overall_gpa'].corr(data['ac_ind'])
    print(f"The correlation between overall_gpa and ac_ind is {corr_coef:.4f}")
    if corr_coef > 0.3:
        print("This indicates a moderate positive correlation.\n")
    elif corr_coef > 0.1:
        print("This indicates a weak positive correlation.\n")
    else:
        print("This indicates a very weak or no correlation.\n")

correlation(data)


#Modeling Data Correlation Calculations
###################################################################################################

# Rank each column against ac_ind and list the top correlated features
correlations = modeldata.select_dtypes(include=[np.number]).corrwith(modeldata['ac_ind']).sort_values(ascending=False)
print("\nTop correlated features with ac_ind from the modeling data:")
print(correlations.head(10))

# Display the top 5 correlated features
top_correlated_features = correlations.index[1:6]  # Exclude ac_ind itself
print("\nTop 5 correlated features with ac_ind:")
print(modeldata[top_correlated_features].columns.tolist())


#Correlation Visualizations
###################################################################################################

# Scatter plot - overall_gpa vs days_attended
plt.figure(figsize=(10, 6))
sns.scatterplot(data=data, x='overall_gpa', y='days_attended', hue='ac_ind', palette='viridis')
plt.title('Scatter Plot of Overall GPA vs Days Attended')
plt.xlabel('Overall GPA')
plt.ylabel('Days Attended')
plt.legend(title='AC Indicator', loc='upper right', labels=['Non-AC', 'AC'])
plt.show()

#Pairwise scatter plot matrix
plt.figure(figsize=(10, 8))
sns.pairplot(data[['overall_gpa', 'ac_gpa', 'days_attended', 'ac_ind']])
plt.suptitle('Pairwise Scatter Plot Matrix')
plt.show()

#***Fix this
#Is this useful?
# #Correlation heatmap
# plt.figure(figsize=(8, 6))
# sns.heatmap(data.corr(), annot=True, cmap='YlOrRd')
# plt.title('Correlation Heatmap')
# plt.show()


#School/Grade Specific Analysis
###################################################################################################
#****When we have the current_school data add:
    # How many AC classes each school offers???
    # How many teachers teach AC classes in each school???
    # Days attended distributions by school

#A lot of these calculations were used before we dropped current_grade
# # Number of students in each grade in the whole district and in each school
# grade_counts_district = df.filter(like='current_grade').sum().sort_values(ascending=False)
# grade_counts_school = df.filter(like='current_grade').groupby(df.filter(like='current_school').columns, axis=1).sum().T
# print("Number of students in the whole district:")
# print(grade_counts_district)
# print("\nNumber of students in each grade in each school:")
# print(grade_counts_school)

# # Count total number of students in each current school
# school_counts = df.filter(like='current_school').sum()
# print("\nTotal number of students in each school:")
# print(school_counts)

# # Count total number of students in each current grade
# grade_counts = df.filter(like='current_grade').sum()
# print("\nTotal number of students in each grade:")
# print(grade_counts)

# # Number of ac_ind in the whole district and in each school
# ac_ind_counts_district = df['ac_ind'].value_counts()
# ac_ind_counts_school = df.groupby(df.filter(like='current_school').columns.tolist())['ac_ind'].value_counts()
# print("\nNumber of ac_ind in the whole district:")
# print(ac_ind_counts_district)
# print("\nNumber of ac_ind in each school:")
# print(ac_ind_counts_school)

# # # Visualizations
# # plt.figure(figsize=(10, 6))
# # sns.countplot(data=df, x='grade', order=df['grade'].value_counts().index)
# # plt.title('Number of Students in Each Grade')
# # plt.show()

# # plt.figure(figsize=(10, 6))
# # sns.countplot(data=df, x='ac_ind', order=df['ac_ind'].value_counts().index)
# # plt.title('Number of Students with ac_ind')
# # plt.show()

# # plt.figure(figsize=(12, 8))
# # sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
# # plt.title('Correlation Matrix')
# # plt.show()

# # Pie chart for school distribution
# plt.figure(figsize=(8, 6))
# data['current_school'].value_counts().plot(kind='pie', autopct='%1.1f%%')
# plt.title('Distribution of Students by School')
# plt.axis('equal')
# plt.show()

# # Box plot of overall GPA by school
# plt.figure(figsize=(10, 6))
# sns.boxplot(x='current_school', y='overall_gpa', data=data)
# plt.title('Overall GPA Distribution by School')
# plt.xlabel('School')
# plt.ylabel('Overall GPA')
# plt.xticks(rotation=90)
# plt.show()