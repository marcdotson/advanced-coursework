import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
from scipy.stats import gaussian_kde

# Set warnings to ignore
warnings.filterwarnings("ignore")

# USU color palette
navy = "#00274C"
gray = "#9EA2A2"
usu_colors = [navy, gray]
darker_red = "#8B0000"

# Set global font to Montserrat and apply USU colors
plt.rcParams.update({
    "font.family": "Montserrat",  # Global font
    "axes.titlesize": 16,         # Title font size
    "axes.labelsize": 12,         # Axis label size
    "axes.labelcolor": navy,      # Axis label color
    "xtick.color": navy,          # X-tick color
    "ytick.color": navy,          # Y-tick color
    "text.color": navy            # General text color
})
sns.set_palette(usu_colors)  # Apply USU color palette to Seaborn globally
sns.set_style("whitegrid")  # Set Seaborn style

# Load the data from CSV files
data = pd.read_csv("../data/exploratory_data.csv")
modeldata = pd.read_csv("../data/modeling_data.csv")

print("EDA Visualizations\n")

### Clean up data and establish variables ###
data['overall_gpa'] = pd.to_numeric(data['overall_gpa'], errors='coerce')
filtered_data = data[data['overall_gpa'] > 0]  # Filter out zero GPAs
total_students = data.shape[0]
total_ac_students = data[data['ac_ind'] == 1].shape[0]
total_ac_courses = data['ac_count'].sum()
total_students_by_school = filtered_data.groupby('current_school').size()
total_ac_students_by_school = filtered_data[filtered_data['ac_ind'] == 1].groupby('current_school').size()
total_ac_courses_by_school = filtered_data.groupby('current_school')['ac_count'].sum()
# Create high school name list to filter by
high_schools = ['Green Canyon', 'Mountain Crest', 'Sky View', 'Ridgeline']





### Visualization 1: Pie Chart - AC vs Non-AC Students ###
plt.figure(figsize=(12, 6))
ac_counts = data['ac_ind'].value_counts()
labels = ['Non-AC', 'AC']
sizes = [ac_counts[0], ac_counts[1]]
plt.pie(
    sizes,
    labels=labels,
    colors=[darker_red, navy],
    wedgeprops=dict(edgecolor='black'),
    autopct='%1.1f%%',
    startangle=90,
    textprops={'color': 'white', 'fontsize': 20},  # White text for percentages inside the pie chart
    pctdistance=0.7  # Adjusts the position of the percentages closer to the center
)
# Make labels outside the chart larger and more visible
plt.gca().legend(labels, loc="upper left", fontsize=20)  # Moves legend outside the chart
plt.title('Distribution of AC and Non-AC Students', fontsize=22)
plt.axis('equal')  # Ensure the pie chart is a circle
plt.tight_layout()  # Prevents clipping
plt.show()

### Visualization 2: Histogram - AC GPA Distribution ###
filtered_ac_gpa = data['ac_gpa'][data['ac_gpa'] > 0]
plt.figure(figsize=(12, 6))
plt.hist(filtered_ac_gpa, bins=np.arange(0.0, 4.0, 0.5), color=navy, edgecolor='black')
plt.title('AC GPA Distribution', fontsize=16)
plt.xlabel('Advanced Course GPA', fontsize=12)
plt.ylabel('Number of Students', fontsize=12)
plt.show()

### Visualization 3: GPA vs AC Count Scatter Plot ###
plt.figure(figsize=(12, 6))
sns.scatterplot(x='overall_gpa', y='ac_count', hue='ac_ind', data=data, palette={0: darker_red, 1: navy})
plt.title('Relationship Between GPA and AC Course Count', fontsize=16)
plt.xlabel('GPA', fontsize=12)
plt.ylabel('Number of AC Courses', fontsize=12)
plt.legend(title='AC Status', loc='upper left')
plt.show()

### Visualization 4: Histogram - AC Status by Gender ###
plt.figure(figsize=(12, 6))
ac_enrollment_by_gender = data[data['ac_ind'] == 1].groupby('gender')['ac_ind'].value_counts()
ac_enrollment_by_gender.plot(kind='bar', color=navy, edgecolor='black')
plt.title('AC Students By Gender', fontsize=16)
plt.xlabel('Gender', fontsize=12)
plt.ylabel('Student Count', fontsize=12)
plt.xticks(rotation=45, fontsize=12)
plt.show()

### Visualization 5: Density Plot - Overall GPA (AC vs Non-AC Students) ###
plt.figure(figsize=(12, 6))
sns.kdeplot(data=data[data['ac_ind'] == 1]['overall_gpa'], shade=True, color=navy, label='AC Students', bw_adjust=0.8, alpha=0.6)
sns.kdeplot(data=data[data['ac_ind'] == 0]['overall_gpa'], shade=True, color=darker_red, label='Non-AC Students', bw_adjust=0.8, alpha=0.6)
mean_ac = data[data['ac_ind'] == 1]['overall_gpa'].mean()
mean_non_ac = data[data['ac_ind'] == 0]['overall_gpa'].mean()
plt.axvline(mean_ac, color=navy, linestyle='dashed', alpha=0.8, label=f'AC Mean: {mean_ac:.2f}')
plt.axvline(mean_non_ac, color=darker_red, linestyle='dashed', alpha=0.8, label=f'Non-AC Mean: {mean_non_ac:.2f}')
plt.title('Distribution of Overall GPA: AC vs. Non-AC Students', fontsize=16)
plt.xlabel('Overall GPA', fontsize=12)
plt.ylabel('Probability Density', fontsize=12)
plt.xlim(0, 4)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
plt.show()

### Visualization 6: Proportion of Students for Each Ethnic Group ###
plt.figure(figsize=(12, 6))
ethnic_columns = ['amerindian_alaskan', 'asian', 'black_african_amer', 'hawaiian_pacific_isl', 'white', 'migrant', 'immigrant', 'refugee_student']
ethnic_counts = data[ethnic_columns].apply(lambda col: (col == 'Y').sum())
ethnic_proportions = (ethnic_counts / total_students) * 100
ethnic_proportions.plot(kind='bar', color=navy, edgecolor='black')
plt.title('Proportion of Students for Each Ethnic Group', fontsize=16)
plt.ylabel('Proportion (%)', fontsize=12)
plt.xlabel('Ethnic Group', fontsize=12)
plt.xticks(rotation=45, fontsize=12)
plt.tight_layout()
plt.show()

### Visualization 7: Proportion of AC Participation by Ethnic Group ###
plt.figure(figsize=(12, 6))
ethnic_counts_ac = data[data['ac_ind'] == 1][ethnic_columns].apply(lambda col: (col == 'Y').sum())
ethnic_proportions_ac = (ethnic_counts_ac / ethnic_counts) * 100
ethnic_proportions_ac = ethnic_proportions_ac.fillna(0)  # Replace NaN with 0 for missing data
ethnic_proportions_ac.plot(kind='bar', color=navy, edgecolor='black')
plt.title('Proportion of Students in AC Courses by Ethnic Group', fontsize=16)
plt.ylabel('Proportion (%)', fontsize=12)
plt.xlabel('Ethnic Group', fontsize=12)
plt.xticks(rotation=45, fontsize=12)
plt.tight_layout()
plt.show()

### Visualization 7: Proportion of AC Students and Courses for High School ###

# Plot AC courses and students by school side by side
fig, ax = plt.subplots(1, 1, figsize=(10, 6))  # Adjusted figure size for better readability
width = 0.4  # Width of each bar
x = np.arange(len(total_ac_courses_by_school))  # X positions for bars

# Plot the bars side by side
ax.bar(
    x - width / 2, 
    total_ac_courses_by_school.sort_values(ascending=False), 
    width, 
    color=navy, 
    edgecolor='black', 
    label='AC Courses'
)
ax.bar(
    x + width / 2, 
    total_ac_students_by_school.sort_values(ascending=False), 
    width, 
    color=gray, 
    edgecolor='black', 
    label='AC Students'
)

# Customize the plot
ax.set_ylabel('Count', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(total_ac_courses_by_school.sort_values(ascending=False).index, rotation=45, fontsize=12)
ax.legend(fontsize=12)
ax.set_title('AC Courses and Students by School (All Years)', fontsize=16)
plt.tight_layout()
plt.show()

# Plot AC courses and students by school (2022-2024) side by side
fig, ax = plt.subplots(1, 1, figsize=(10, 6))  # Adjusted figure size for better readability
# Filter data for years 2022-2024 and valid high schools
data_22_24 = data[(data['year'].isin([2022, 2023, 2024])) & (data['current_school'].isin(high_schools))]
total_ac_courses_by_school_22_24 = data_22_24.groupby('current_school')['ac_count'].sum()
total_ac_students_by_school_22_24 = data_22_24.groupby('current_school').size()

# X positions for the new plot
x = np.arange(len(total_ac_courses_by_school_22_24))

# Plot the bars side by side
ax.bar(
    x - width / 2, 
    total_ac_courses_by_school_22_24.sort_values(ascending=False), 
    width, 
    color=navy, 
    edgecolor='black', 
    label='AC Courses (2022-2024)'
)
ax.bar(
    x + width / 2, 
    total_ac_students_by_school_22_24.sort_values(ascending=False), 
    width, 
    color=gray, 
    edgecolor='black', 
    label='AC Students (2022-2024)'
)

# Customize the plot
ax.set_ylabel('Count', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(total_ac_courses_by_school_22_24.sort_values(ascending=False).index, rotation=45, fontsize=12)
ax.legend(fontsize=12)
ax.set_title('AC Courses and Students by School (2022-2024)', fontsize=16)
plt.tight_layout()
plt.show()