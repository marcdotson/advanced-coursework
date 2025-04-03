import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

# Load the data from a CSV files
data = pd.read_csv("../data/exploratory_data.csv")
modeldata = pd.read_csv("../data/modeling_data.csv")
warnings.filterwarnings("ignore")

print("EDA visualizations\n")

#Clean up data and establish variables
# Ensure 'overall_gpa' is numeric and filter out zero GPAs
data['overall_gpa'] = pd.to_numeric(data['overall_gpa'], errors='coerce')
filtered_data = data[data['overall_gpa'] > 0]
# Total students in district
total_students = data.shape[0]
# Total students with ac_ind = 1
total_ac_students = data[data['ac_ind'] == 1].shape[0]
# Total AC courses in the district
total_ac_courses = data['ac_count'].sum()
# Calculate total students, total ac students, and total ac courses by school
total_students_by_school = filtered_data.groupby('current_school').size()
total_ac_students_by_school = filtered_data[filtered_data['ac_ind'] == 1].groupby('current_school').size()
total_ac_courses_by_school = filtered_data.groupby('current_school')['ac_count'].sum()

# Pie chart - AC vs non-AC students
plt.figure(figsize=(8, 6))
ac_counts = data['ac_ind'].value_counts()
labels = ['Non-AC', 'AC']
sizes = [ac_counts[0], ac_counts[1]]
colors = ['#8B0000', 'steelblue']  # Darker red
plt.pie(sizes, labels=labels, colors=colors, wedgeprops=dict(edgecolor='black'), autopct='%1.1f%%', startangle=90)
plt.title('Distribution of AC and Non-AC Students')
plt.axis('equal')
plt.show()

# Histogram = AC GPA Distribution
# # Drop all zeros in ac gpa (fail, pass, na)
filtered_ac_gpa = data['ac_gpa'][data['ac_gpa'] > 0]
plt.figure(figsize=(8, 6))
plt.hist(filtered_ac_gpa, bins=np.arange(0.0, 4.0, 0.5), color='steelblue', edgecolor='black')
plt.title('AC GPA Distribution')
plt.xlabel('Advanced Course GPA')
plt.ylabel('Number of students')
plt.show()

# GPA vs AC count scatter plot
plt.figure(figsize=(12, 6))
sns.scatterplot(x='overall_gpa', y='ac_count', hue='ac_ind', data=data, palette={0: 'red', 1: 'steelblue'})
plt.title('Relationship Between GPA and AC Course Count')
plt.xlabel('GPA')
plt.ylabel('Number of AC Courses')
plt.legend(title='AC Status', loc='upper left')
plt.show()

# Histogram = AC Status by gender
plt.figure(figsize=(10, 6))
ac_enrollment_by_gender = data[data['ac_ind'] == 1].groupby('gender')['ac_ind'].value_counts()
ac_enrollment_by_gender.plot(kind='bar', color='steelblue', edgecolor='black')
plt.title('AC Students By Gender')
plt.xlabel('Gender')
plt.ylabel('Student Count')
plt.xticks(rotation=45)
plt.xticks([0,1,2], ['Female', 'Male', 'Unknown'])
for p in plt.gca().patches:
    plt.text(p.get_x() + (p.get_width() / 2), p.get_y() + (p.get_height() / 2), '{:.0f}'.format(p.get_height()), ha='center')
plt.show()

### Density Plots ###

# Set figure size
plt.figure(figsize=(8, 6))
# Define color scheme
colors = {'AC Students': 'blue', 'Non-AC Students': 'red'}
# Plot KDE with transparency and smoothing
sns.kdeplot(data=data[data['ac_ind'] == 1]['overall_gpa'], shade=True, color=colors['AC Students'], 
            label='AC Students', bw_adjust=0.8, alpha=0.6)
sns.kdeplot(data=data[data['ac_ind'] == 0]['overall_gpa'], shade=True, color=colors['Non-AC Students'], 
            label='Non-AC Students', bw_adjust=0.8, alpha=0.6)
# Calculate and plot mean GPAs as vertical dashed lines
mean_ac = data[data['ac_ind'] == 1]['overall_gpa'].mean()
mean_non_ac = data[data['ac_ind'] == 0]['overall_gpa'].mean()
plt.axvline(mean_ac, color=colors['AC Students'], linestyle='dashed', alpha=0.8, label=f'AC Mean: {mean_ac:.2f}')
plt.axvline(mean_non_ac, color=colors['Non-AC Students'], linestyle='dashed', alpha=0.8, label=f'Non-AC Mean: {mean_non_ac:.2f}')
# Titles and labels
plt.title('Distribution of Overall GPA: AC vs. Non-AC Students', fontsize=14, fontweight='bold')
plt.xlabel('Overall GPA', fontsize=12)
plt.ylabel('Probability Density', fontsize=12)
# Set GPA limits
plt.xlim(0, 4)
# Add a grid for better readability
plt.grid(True, linestyle='--', alpha=0.5)
# Show legend
plt.legend()
# Display plot
plt.show()

# Ensure 'ac_ind' is treated as a category
data['ac_ind'] = data['ac_ind'].astype(str)
# Create a density contour plot
fig1 = px.density_contour(data, x="overall_gpa", color="ac_ind", 
                          marginal_x="histogram", 
                          title="GPA Density Plot: AC vs Non-AC Students")
# Set axis limits
fig1.update_xaxes(range=[0, 4])
# Show plot
fig1.show()

# Create a density heatmap
fig2 = px.density_heatmap(data, x="overall_gpa", color_continuous_scale="Blues",
                          facet_col="ac_ind",  # Separate AC and Non-AC
                          title="GPA Density Heatmap: AC vs Non-AC")
fig2.update_xaxes(range=[0, 4])
# Show plot
fig2.show()


# Visualize the proportion of 'Y' for each ethnic group
plt.figure(figsize=(10, 6))
ethnic_counts = data[['amerindian_alaskan', 'asian', 'black_african_amer', 'hawaiian_pacific_isl', 'white', 'migrant', 'immigrant', 'refugee_student', 'ethnicity']].apply(pd.Series.value_counts).fillna(0)
ethnic_proportions = (ethnic_counts.loc['Y'] / total_students) * 100
ethnic_proportions.plot(kind='bar', color='steelblue', edgecolor='black')
plt.title('Proportion of Students for Each Ethnic Group')
plt.ylabel('Proportion')
plt.xticks(rotation=45)
for p in plt.gca().patches:
    plt.text(p.get_x() + (p.get_width() / 2), p.get_y() + (p.get_height() / 2), '{:.1f}%'.format(p.get_height()), ha='center')
plt.ylim(0, 4)  # Set y-axis limits to stay within 0 and 4
plt.show()

# Total count of each ethnic group
ethnic_counts_total = data[['amerindian_alaskan', 'asian', 'black_african_amer', 'hawaiian_pacific_isl', 'white', 'migrant', 'immigrant', 'refugee_student']].apply(pd.Series.value_counts).fillna(0)

# Count of AC enrollments for each ethnic group
ethnic_counts_ac = data[data['ac_ind'] == 1][['amerindian_alaskan', 'asian', 'black_african_amer', 'hawaiian_pacific_isl', 'white', 'migrant', 'immigrant', 'refugee_student']].apply(pd.Series.value_counts).fillna(0)
ehtnic_counts_ac = (ethnic_counts_ac.loc['Y'] / ethnic_counts_total) * 100

# Calculate proportions of AC participation
ethnic_proportions_ac = (ethnic_counts_ac / ethnic_counts_total) * 100

# Visualize the proportions
plt.figure(figsize=(10, 6))
ethnic_proportions_ac.plot(kind='bar', color='steelblue', edgecolor='black')
plt.title('Proportion of Students in AC Courses by Ethnic Group')
plt.ylabel('Proportion')
plt.xticks(rotation=45)
for p in plt.gca().patches:
    plt.text(p.get_x() + (p.get_width() / 2), p.get_y() + (p.get_height() / 2), '{:.1f}%'.format(p.get_height()), ha='center')
plt.tight_layout()
plt.show()

# Map school numbers to school names
school_name_map = {
    710: 'Cache High',
    706: 'Sky View',
    705: 'Ridgeline',
    703: 'Green Canyon',
    702: 'Mountain Crest',
    410: 'South Cache Middle',
    406: 'North Cache Middle',
    330: 'Spring Creek Middle',
    170: 'Wellesville Elem.',
    166: 'Summit Elem.',
    164: 'River Heights Elem.',
    160: 'Providence Elem.',
    156: 'White Pine Elem.',
    152: 'North Park Elem.',
    144: 'Nibley Elem.',
    140: 'Millville Elem.',
    132: 'Mountainside Elem.',
    130: 'Lincoln Elem.',
    128: 'Lewiston Elem.',
    124: 'Heritage Elem.',
    120: 'Greenville Elem.',
    118: 'Cedar Ridge Elem.',
    111: 'Canyon Elem.',
    109: 'Birch Creek Elem.',
    106: ''
}

hs_name_map = {
    710: 'Cache High',
    706: 'Sky View',
    705: 'Ridgeline',
    703: 'Green Canyon',
    702: 'Mountain Crest',
}

# Plot AC courses by school
# Create subplots for combined plots
fig, ax = plt.subplots(1, 1, figsize=(8, 6))
total_ac_courses_by_school[total_ac_courses_by_school.index.map(hs_name_map).notnull()].sort_values(ascending=False).rename(index=hs_name_map).plot(kind='bar', color='blue', edgecolor='black', ax=ax, position=0, width=0.4, label='AC Courses')
# Plot the proportion of AC students by school
total_ac_students_by_school[total_ac_students_by_school.index.map(hs_name_map).notnull()].sort_values(ascending=False).rename(index=hs_name_map).plot(kind='bar', color='steelblue', edgecolor='black', ax=ax, position=1, width=0.4, label='AC Students')
ax.set_title('AC Count and Number of AC Students by School')
ax.set_ylabel('Count')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
ax.legend()
plt.tight_layout()
plt.show()

# Plot AC courses by school (2022-2024)
# Create subplots for combined plots (2022-2024)
fig, ax = plt.subplots(1, 1, figsize=(8, 6))
# Plot AC courses by school (2022-2024)
total_ac_courses_by_school_22_24 = data[(data['year'].isin([2022, 2023, 2024])) & (data['current_school'].isin(hs_name_map.keys()))].groupby('current_school')['ac_count'].sum().rename(index=hs_name_map)
total_ac_courses_by_school_22_24.sort_values(ascending=False).plot(kind='bar', color='blue', edgecolor='black', ax=ax, position=0, width=0.4, label='AC Courses (2022-2024)')
# Plot the proportion of AC students by school (2022-2024)
total_ac_students_by_school_22_24 = data[(data['year'].isin([2022, 2023, 2024])) & (data['current_school'].isin(hs_name_map.keys()))].groupby('current_school').size().rename(index=hs_name_map)
total_ac_students_by_school_22_24.sort_values(ascending=False).plot(kind='bar', color='steelblue', edgecolor='black', ax=ax, position=1, width=0.4, label='AC Students (2022-2024)')
ax.set_title('AC Count and Number of AC Students by School (2022-2024)')
ax.set_ylabel('Count')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
ax.legend()
plt.tight_layout()
plt.show()

# Combined plots for AC courses and students by school Total and Post-Covid
# Create subplots for combined plots
fig, ax = plt.subplots(1, 1, figsize=(8, 6))
ax.set_title('AC Count by School Total and Post-Covid')
ax.set_ylabel('Count')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
ax.legend()
plt.tight_layout()
plt.show()

# Filter to only include schools that begin with 7 and map school numbers to names
data_schools_hs = data[data['current_school'].astype(str).str.startswith('7')]
data_schools_hs['hs_name_map'] = data_schools_hs['current_school'].map(hs_name_map)
# AC GPA by School (only schools that are in the specified list)
plt.figure(figsize=(6, 12))
data_schools_hs_mean_gpa = data_schools_hs[data_schools_hs['ac_gpa'] > 0].groupby('current_school')['ac_gpa'].mean().sort_values(ascending=False)
sns.boxplot(x='ac_gpa', y='current_school', data=data_schools_hs[data_schools_hs['ac_gpa'] > 0][data_schools_hs['hs_name_map'].isin(data_schools_hs_mean_gpa.index)], showfliers=False, palette='Blues', orient='h')
plt.title('AC GPA Distribution by School')
plt.xlabel('AC GPA')
plt.xticks(rotation=0)
plt.show()
