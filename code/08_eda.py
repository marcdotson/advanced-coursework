import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#This is a very rough start to the EDA

print("Cache County School District")
print("Powerschool Exploratory Data Analysis\n")

# Load the data from a CSV file
data = pd.read_csv("./data/exploratory_data.csv")

#we need year values before we can do this
#We also need them to show the ac trend from year to year, or if we want any year specific evaluations
# print(data['year'].unique())

data.describe(include='all')
print(data.head().to_string(), "\n")
print("Columns:\n", data.columns)
data.isna().sum()

#Not sure if we need this
# # Missing value analysis
# #plt.figure(figsize=(8, 6))
# sns.heatmap(data.isnull(), cbar=False)
# plt.title('Missing Value Heatmap')
# plt.show()

# Create a pie chart for AC vs non-AC students
plt.figure(figsize=(8, 6))
ac_counts = data['ac_ind'].value_counts()
labels = ['Non-AC', 'AC']
sizes = [ac_counts[0], ac_counts[1]]
colors = ['blue', 'steelblue']

plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
plt.title('Distribution of AC and Non-AC Students')
plt.axis('equal')  # Equal aspect ratio ensures that pie is circular.
plt.show()


# Print the overall proportion of AC students
ac_proportion = ac_counts[1] / data.shape[0]
print(f"The overall proportion of students who have taken advanced courses (AC) is {ac_proportion:.2%}.")
print("###################################################################################################\n")

# Histogram for overall GPA distribution
plt.figure(figsize=(8, 6))
plt.hist(data['overall_gpa'], bins=10, color='blue', edgecolor='black')
plt.title('Overall GPA Distribution')
plt.xlabel('Overall GPA')
plt.ylabel('Students')
plt.xlim(0, 4)  # Set x-axis range from 0 to 4
plt.show()

# Average overall GPA (excluding 0s)
average_gpa = data['overall_gpa'][data['overall_gpa'] != 0].mean()
print(f"\nAverage overall GPA: {average_gpa:.2f}")

# Median overall GPA (excluding 0s)
median_gpa = data['overall_gpa'][data['overall_gpa'] != 0].median()
print(f"Median overall GPA: {median_gpa:.2f}")

# Standard deviation of overall GPA (excluding 0s)
sd_gpa = data['overall_gpa'][data['overall_gpa'] != 0].std()
print(f"Standard deviation of overall GPA: {sd_gpa:.2f}")
print("###################################################################################################\n")
#should i do grade distributions by school? Bar chart?


# Boxplot of days attended with flipped axes
plt.figure(figsize=(8, 6))
plt.boxplot(data['days_attended'], vert=False)
plt.title('Days Attended')
plt.xlabel('Days Attended')
plt.show()

# Histogram for days attended distribution
plt.figure(figsize=(8, 6))
plt.hist(data['days_attended'], bins=range(0, 190, 10), color='blue', edgecolor='black')
plt.title('Days Attended Distribution')
plt.xlabel('Days Attended')
plt.ylabel('Frequency')
plt.xlim(0, 180)
plt.show()

# Average days attended
average_days_attended = data['days_attended'].mean()
print(f"\nAverage days attended: {average_days_attended:.2f}")

# Median days attended
median_days_attended = data['days_attended'].median()
print(f"Median days attended: {median_days_attended:.2f}")

# Standard deviation of days attended
sd_days_attended = data['days_attended'].std()
print(f"Standard deviation of days attended: {sd_days_attended:.2f}")
print("###################################################################################################\n")

# # Add counts on top of each bar
# counts, bins, patches = plt.hist(data['days_attended'], bins=range(0, 190, 10), color='lightblue', edgecolor='black')
# for count, patch in zip(counts, patches):
#     plt.text(patch.get_x() + patch.get_width() / 2, count, int(count), ha='center', va='bottom', color='black', fontsize=8)


#This is all from my first eda version, need to go through and see which ones to keep
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from sklearn.decomposition import PCA
# from sklearn.cluster import KMeans

# # Load the dataset
# df = pd.read_csv('./data/01_exploratory_powerschool_data.csv')

# # Drop rows with null values
# print(df.head().to_string())

# # Data summary
# print(df.info())
# print(df.describe())

# corr_coef = df['overall_gpa'].corr(df['ac_ind'].astype(float))
# print(corr_coef)

# ################################################
# # Number of students in each grade in the whole district and in each school
# grade_counts_district = df.filter(like='current_grade').sum().sort_values(ascending=False)
# grade_counts_school = df.filter(like='current_grade').groupby(df.filter(like='current_school').columns, axis=1).sum().T

# print("Number of students in the whole district:")
# print(grade_counts_district)
# print("\nNumber of students in each grade in each school:")
# print(grade_counts_school)

# # Count total number of each ethnic group
# ethnic_counts = df.filter(like='ethnicity_').sum()
# ethnic_groups = ['amerindian_alaskan', 'asian', 'black_african_amer', 'hawaiian_pacific_isl', 'white']
# total_ethnic_counts = ethnic_counts[ethnic_groups].sum()
# print("\nTotal number of students in each ethnic group:")
# for group in ethnic_groups:
#     print(f"{group}: {total_ethnic_counts[group]}")
# print("\nTotal number of each ethnic group:")
# print(ethnic_counts)

# # Count total number of female and male students
# gender_counts = df.filter(like='gender_').sum()
# print("\nTotal number of female and male students:")
# print(gender_counts)

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




#Need more info##

###I can't do this part until I have current_school data info

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

# # Scatter plot with regression line for overall GPA vs. days attended
# plt.figure(figsize=(8, 6))
# sns.regplot(x='days_attended', y='overall_gpa', data=data)
# plt.title('Overall GPA vs. Days Attended')
# plt.xlabel('Days Attended')
# plt.ylabel('Overall GPA')
# plt.show()

# # Correlation heatmap
# #plt.figure(figsize=(8, 6))
# #sns.heatmap(data.corr(), annot=True, cmap='YlOrRd')
# #plt.title('Correlation Heatmap')
# #plt.show()

# # Pairwise scatter plot matrix
# #plt.figure(figsize=(10, 8))
# #sns.pairplot(data[['overall_gpa', 'ac_gpa', 'days_attended', 'ac_ind']])
# #plt.suptitle('Pairwise Scatter Plot Matrix')
# #plt.show()