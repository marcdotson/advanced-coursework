import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings

warnings.filterwarnings("ignore")

# Load the data
data = pd.read_csv("../data/exploratory_data.csv")
modeldata = pd.read_csv("../data/modeling_data.csv")

# Standardize categorical values
data.columns = data.columns.str.lower().str.strip()
data['ethnicity'] = data['ethnicity'].str.lower().str.strip()
data['refugee_student'] = data['refugee_student'].str.lower().str.strip()

# School name mappings
school_name_map = {
    710: 'Cache High', 706: 'Sky View', 705: 'Ridgeline', 703: 'Green Canyon', 702: 'Mountain Crest',
    410: 'South Cache Middle', 406: 'North Cache Middle', 330: 'Spring Creek Middle'
}

hs_name_map = {710: 'Cache High', 706: 'Sky View', 705: 'Ridgeline', 703: 'Green Canyon', 702: 'Mountain Crest'}

# Ensure numeric GPA and filter out zero values
data['overall_gpa'] = pd.to_numeric(data['overall_gpa'], errors='coerce')
filtered_data = data[data['overall_gpa'] > 0]

# Compute district-wide statistics
total_students = len(data)
total_ac_students = data['ac_ind'].sum()
total_ac_courses = data['ac_count'].sum()

print(f"Total students in district: {total_students}")
print(f"Total AC students in district: {total_ac_students}")

# Function to compute AC statistics by school
def compute_ac_stats(df, schools):
    ac_students = df[df['ac_ind'] == 1].groupby('current_school').size()
    ac_courses = df.groupby('current_school')['ac_count'].sum()
    return ac_students.rename(index=schools), ac_courses.rename(index=schools)

# Function to create bar plots
def plot_bar_chart(data, title, ylabel, color='steelblue', rotation=45):
    plt.figure(figsize=(10, 6))
    data.sort_values(ascending=False).plot(kind='bar', color=color, edgecolor='black')
    plt.title(title, fontweight='bold', fontsize=18)
    plt.ylabel(ylabel, fontsize=14)
    plt.xticks(rotation=rotation, fontsize=12)
    plt.tight_layout()
    plt.show()

# Compute statistics for all years and 2022-2024
total_ac_students_by_school, total_ac_courses_by_school = compute_ac_stats(filtered_data, hs_name_map)
total_ac_students_by_school_22_24, total_ac_courses_by_school_22_24 = compute_ac_stats(
    data[data['year'].isin([2022, 2023, 2024])], hs_name_map)

# # Plot AC count and students per school
# plot_bar_chart(total_ac_courses_by_school, 'Total AC Count by School', 'Number of AC Courses')
# plot_bar_chart(total_ac_students_by_school, 'Total AC Students by School', 'Number of AC Students')
# plot_bar_chart(total_ac_courses_by_school_22_24, 'AC Courses by School (2022-2024)', 'Number of AC Courses')
# plot_bar_chart(total_ac_students_by_school_22_24, 'AC Students by School (2022-2024)', 'Number of AC Students')

# Create side-by-side bar charts for all years vs post-COVID (2022-2024)
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Plot AC courses and AC students for all years
total_ac_courses_by_school.sort_values(ascending=False).plot(
    kind='bar', color='blue', edgecolor='black', ax=axes[0], position=0, width=0.4, label='AC Courses'
)
total_ac_students_by_school.sort_values(ascending=False).plot(
    kind='bar', color='steelblue', edgecolor='black', ax=axes[0], position=1, width=0.4, label='AC Students'
)
axes[0].set_title('AC Courses & Students by School (All Years)', fontweight='bold', fontsize=14)
axes[0].set_ylabel('Count')
axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=45)
axes[0].legend()

# Plot AC courses and AC students for post-COVID (2022-2024)
total_ac_courses_by_school_22_24.sort_values(ascending=False).plot(
    kind='bar', color='blue', edgecolor='black', ax=axes[1], position=0, width=0.4, label='AC Courses (Post-COVID)'
)
total_ac_students_by_school_22_24.sort_values(ascending=False).plot(
    kind='bar', color='steelblue', edgecolor='black', ax=axes[1], position=1, width=0.4, label='AC Students (Post-COVID)'
)
axes[1].set_title('AC Courses & Students by School (Post-COVID)', fontweight='bold', fontsize=14)
axes[1].set_ylabel('Count')
axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=45)
axes[1].legend()

plt.tight_layout()
plt.show()


# Pie chart - AC vs non-AC students
plt.figure(figsize=(8, 8))
ac_counts = data['ac_ind'].value_counts()
sizes = [ac_counts.get(0, 0), ac_counts.get(1, 0)]
labels = ['Non-AC', 'AC']
colors = ['#8B0000', 'steelblue']
plt.pie(sizes, labels=labels, colors=colors, wedgeprops=dict(edgecolor='black'), autopct='%1.1f%%', startangle=90)
plt.title('Distribution of AC and Non-AC Students', fontsize=18)
plt.axis('equal')
plt.show()

# Histogram - AC GPA Distribution
filtered_ac_gpa = data['ac_gpa'][data['ac_gpa'] > 0]
plt.figure(figsize=(8, 6))
sns.histplot(filtered_ac_gpa, bins=8, kde=True, color='steelblue', edgecolor='black')
plt.title('AC GPA Distribution')
plt.xlabel('Advanced Course GPA')
plt.ylabel('Number of Students')
plt.show()

# GPA Density Plot with Mean and Median
plt.figure(figsize=(10, 6))
sns.kdeplot(data[data['ac_ind'] == 1]['overall_gpa'], label='AC Students', shade=True, color='steelblue')
sns.kdeplot(data[data['ac_ind'] == 0]['overall_gpa'], label='Non-AC Students', shade=True, color='red')

ac_mean = data[data['ac_ind'] == 1]['overall_gpa'].mean()
ac_median = data[data['ac_ind'] == 1]['overall_gpa'].median()
non_ac_mean = data[data['ac_ind'] == 0]['overall_gpa'].mean()
non_ac_median = data[data['ac_ind'] == 0]['overall_gpa'].median()

plt.legend([f'AC Mean: {ac_mean:.2f}', f'AC Median: {ac_median:.2f}', 
            f'Non-AC Mean: {non_ac_mean:.2f}', f'Non-AC Median: {non_ac_median:.2f}'])
plt.title('Comparison of GPA Distributions: AC vs Non-AC Students')
plt.xlabel('GPA')
plt.ylabel('Density')
plt.show()

# Ethnicity Proportions
ethnic_counts = data[['amerindian_alaskan', 'asian', 'black_african_amer', 'hawaiian_pacific_isl', 
                      'white', 'migrant', 'immigrant', 'refugee_student', 'ethnicity']].apply(pd.Series.value_counts).fillna(0)
ethnic_proportions = (ethnic_counts.get('Y', pd.Series(0)) / total_students) * 100
plot_bar_chart(ethnic_proportions, 'Proportion of Students for Each Ethnic Group', 'Proportion (%)')

# Proportion of students in AC courses by ethnicity
ethnic_counts_total = ethnic_counts.get('Y', pd.Series(0))
ethnic_counts_ac = data[data['ac_ind'] == 1][['amerindian_alaskan', 'asian', 'black_african_amer', 
                                              'hawaiian_pacific_isl', 'white', 'migrant', 'immigrant', 
                                              'refugee_student', 'ethnicity']].apply(pd.Series.value_counts).fillna(0).get('Y', pd.Series(0))
ethnic_proportions_ac = (ethnic_counts_ac / ethnic_counts_total) * 100
plot_bar_chart(ethnic_proportions_ac, 'Proportion of Students in AC Courses by Ethnic Group', 'Proportion (%)')

# GPA vs AC count scatter plot
plt.figure(figsize=(10, 6))
sns.scatterplot(x='overall_gpa', y='ac_count', hue='ac_ind', data=data, palette=['red', 'steelblue'])
plt.title('Relationship Between GPA and AC Course Count')
plt.xlabel('GPA')
plt.ylabel('Number of AC Courses')
plt.legend(title='AC Status', loc='upper left')
plt.show()

# Histogram - AC Status by gender
plt.figure(figsize=(10, 6))
ac_enrollment_by_gender = data[data['ac_ind'] == 1].groupby('gender')['ac_ind'].value_counts()
ac_enrollment_by_gender.plot(kind='bar', color='steelblue', edgecolor='black')
plt.title('AC Students By Gender')
plt.xlabel('Gender')
plt.ylabel('Student Count')
plt.xticks([0,1,2], ['Female', 'Male', 'Unknown'])
plt.show()
