# Import libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import ast
import pickle
# from scipy.stats import gaussian_kde

# Set warnings to ignore
warnings.filterwarnings("ignore")
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: f'{x:.2f}')

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

##########################################################################
# PHASE ONE - Exploratory Data Visualizations
# Load the data from CSV files
data = pd.read_csv("data/exploratory_data.csv")

# Title
print("\033[1m" + "=" * 75)
print("CCSDUT Powerschool Exploratory Data Analysis")
print("=" * 75 + "\033[0m")

# === Utility Functions ===
def print_section_header(title):
    """Utility function to print section headers."""
    print("\n" + title)
    print("=" * 50)

def plot_ac_courses_and_students(data, post_covid_years=None):
    """Plot AC courses and AC students by school."""
    if post_covid_years:
        data = data[data['year'].isin(post_covid_years)]
        title_suffix = " (Post-COVID)"
    else:
        title_suffix = ""

    # Group data by school
    ac_courses_by_school = data.groupby('current_school')['ac_count'].sum().sort_values(ascending=False)
    ac_students_by_school = data[data['ac_ind'] == 1].groupby('current_school').size().sort_values(ascending=False)

    # Plot AC courses and students
    fig, ax = plt.subplots(figsize=(8, 6))
    ac_courses_by_school.plot(kind='bar', color='blue', edgecolor='black', ax=ax, label='AC Courses', position=0, width=0.4)
    ac_students_by_school.plot(kind='bar', color='steelblue', edgecolor='black', ax=ax, label='AC Students', position=1, width=0.4)

    ax.set_title(f'AC Count and Number of AC Students by School{title_suffix}')
    ax.set_ylabel('Count')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.legend()
    plt.tight_layout()
    plt.show()

def plot_ac_vs_non_ac_distribution(data):
    """Plot the distribution of AC vs Non-AC students."""
    plt.figure(figsize=(8, 6))
    ac_counts = data['ac_ind'].value_counts()
    labels = ['Non-AC', 'AC']
    sizes = [ac_counts[0], ac_counts[1]]
    colors = ['#8B0000', 'steelblue']
    plt.pie(sizes, labels=labels, colors=colors, wedgeprops=dict(edgecolor='black'), autopct='%1.1f%%', startangle=90)
    plt.title('Distribution of AC and Non-AC Students')
    plt.axis('equal')
    plt.show()

def plot_ac_gpa_distribution(data):
    """Plot the distribution of AC GPA."""
    filtered_ac_gpa = data['ac_gpa'][data['ac_gpa'] > 0]
    plt.figure(figsize=(8, 6))
    plt.hist(filtered_ac_gpa, bins=np.arange(0.0, 4.0, 0.5), color='steelblue', edgecolor='black')
    plt.title('AC GPA Distribution')
    plt.xlabel('Advanced Course GPA')
    plt.ylabel('Number of Students')
    plt.tight_layout()
    plt.show()

def plot_ac_gpa_by_school(data):
    """Plot the AC GPA distribution by school."""
    plt.figure(figsize=(6, 12))
    sns.boxplot(
        x='ac_gpa', y='current_school',
        data=data[data['ac_gpa'] > 0],
        showfliers=False, palette='Blues', orient='h'
    )
    plt.title('AC GPA Distribution by School')
    plt.xlabel('AC GPA')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()

def plot_gpa_density(data):
    """Plot GPA density for AC and Non-AC students."""
    plt.figure(figsize=(10, 6))
    sns.kdeplot(data[data['ac_ind'] == 1]['overall_gpa'], label='AC Students', shade=True, color='steelblue')
    sns.kdeplot(data[data['ac_ind'] == 0]['overall_gpa'], label='Non-AC Students', shade=True, color='red')

    # Calculate mean and median for both groups
    ac_mean = data[data['ac_ind'] == 1]['overall_gpa'].mean()
    ac_median = data[data['ac_ind'] == 1]['overall_gpa'].median()
    non_ac_mean = data[data['ac_ind'] == 0]['overall_gpa'].mean()
    non_ac_median = data[data['ac_ind'] == 0]['overall_gpa'].median()

    # Add legend for mean and median
    plt.legend([
        f'AC Mean: {ac_mean:.2f}', f'AC Median: {ac_median:.2f}',
        f'Non-AC Mean: {non_ac_mean:.2f}', f'Non-AC Median: {non_ac_median:.2f}'
    ], loc='upper right')

    plt.title('Comparison of GPA Distributions: AC vs Non-AC Students')
    plt.xlabel('GPA')
    plt.ylabel('Density')
    plt.tight_layout()
    plt.show()

def plot_ethnic_group_proportions(data, total_students):
    """Plot the proportion of ethnic groups in AC courses."""
    ethnic_counts = data[['amerindian_alaskan', 'asian', 'black_african_amer', 'hawaiian_pacific_isl', 'white', 'migrant', 'immigrant', 'refugee_student', 'ethnicity']].apply(pd.Series.value_counts).fillna(0)
    ethnic_proportions = (ethnic_counts.loc['Y'] / total_students) * 100
    plt.figure(figsize=(10, 6))
    ethnic_proportions.plot(kind='bar', color='steelblue', edgecolor='black')
    plt.title('Proportion of Students for Each Ethnic Group')
    plt.ylabel('Proportion')
    plt.xticks(rotation=45)
    for p in plt.gca().patches:
        plt.text(p.get_x() + (p.get_width() / 2), p.get_y() + (p.get_height() / 2), '{:.1f}%'.format(p.get_height()), ha='center')
    plt.tight_layout()
    plt.show()

def plot_ethnic_ac_participation(data):
    """Plot participation of ethnic groups in AC courses."""
    ethnic_counts_total = data[['amerindian_alaskan', 'asian', 'black_african_amer', 'hawaiian_pacific_isl', 'white', 'migrant', 'immigrant', 'refugee_student']].apply(pd.Series.value_counts).fillna(0).loc['Y']
    ethnic_counts_ac = data[data['ac_ind'] == 1][['amerindian_alaskan', 'asian', 'black_african_amer', 'hawaiian_pacific_isl', 'white', 'migrant', 'immigrant', 'refugee_student']].apply(pd.Series.value_counts).fillna(0).loc['Y']
    ethnic_proportions_ac = (ethnic_counts_ac / ethnic_counts_total) * 100
    plt.figure(figsize=(10, 6))
    ethnic_proportions_ac.plot(kind='bar', color='steelblue', edgecolor='black')
    plt.title('Proportion of Students in AC Courses by Ethnic Group')
    plt.ylabel('Proportion')
    plt.xticks(rotation=45)
    for p in plt.gca().patches:
        plt.text(p.get_x() + (p.get_width() / 2), p.get_y() + (p.get_height() / 2), '{:.1f}%'.format(p.get_height()), ha='center')
    plt.tight_layout()
    plt.show()

def plot_gpa_vs_ac_count(data):
    """Plot GPA vs AC course count."""
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='overall_gpa', y='ac_count', hue='ac_ind', data=data, palette={0: 'red', 1: 'steelblue'})
    plt.title('Relationship Between GPA and AC Course Count')
    plt.xlabel('GPA')
    plt.ylabel('Number of AC Courses')
    plt.legend(title='AC Status', loc='upper left')
    plt.tight_layout()
    plt.show()

def plot_ac_students_by_gender(data):
    """Plot AC enrollment by gender."""
    plt.figure(figsize=(10, 6))
    ac_enrollment_by_gender = data[data['ac_ind'] == 1].groupby('gender').size()
    ac_enrollment_by_gender.plot(kind='bar', color='steelblue', edgecolor='black')
    plt.title('AC Students By Gender')
    plt.xlabel('Gender')
    plt.ylabel('Student Count')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()

# === Main Processing ===
if __name__ == "__main__":
    total_students = data.shape[0]

    print_section_header("EDA Visualizations")

    # Plot AC courses and students by school (total and post-COVID)
    plot_ac_courses_and_students(data)
    plot_ac_courses_and_students(data, post_covid_years=[2022, 2023, 2024])

    # Plot AC vs Non-AC distribution
    plot_ac_vs_non_ac_distribution(data)

    # Plot AC GPA distribution
    plot_ac_gpa_distribution(data)

    # Plot AC GPA by school
    plot_ac_gpa_by_school(data)

    # Plot GPA density
    plot_gpa_density(data)

    # Plot ethnic group proportions
    plot_ethnic_group_proportions(data, total_students)

    # Plot ethnic AC participation
    plot_ethnic_ac_participation(data)

    # Plot GPA vs AC course count
    plot_gpa_vs_ac_count(data)

    # Plot AC enrollment by gender
    plot_ac_students_by_gender(data)

##########################################################################
# PHASE TWO - Clearinghouse Exploratory Data Visualizations
# Load the df from CSV file
df = pd.read_csv("data/clearinghouse_exploratory_data.csv", low_memory=False)

print("Clearinghouse Exploratory Data Analysis\n")

# Display years in the dataset
years = df['year'].unique()
print(f"Years in data set: {', '.join(map(str, years))}\n")

print("\nOverall District Summary:\n")
def overall_enrollment_stats(df):
    """
    Generate and print an overall district summary based on the provided DataFrame.
    """
    total_students = df.shape[0]
    total_started_college = df[df['start_college_y'] == 1]['start_college_y'].sum()
    percent_started_college = (total_started_college / total_students) * 100
    college_grad_sum = df['college_grad_y'].sum()
    percent_grad_college = (college_grad_sum / total_students) * 100
    percent_grad_college_started = (college_grad_sum / total_started_college) * 100

    print(f"Total number of students in the dataset: {total_students}")
    print(f"Total number of students who started college: {total_started_college}")
    print(f"Percentage of all students who started college: {percent_started_college:.2f}%")
    print(f"Total number of students who graduated college: {college_grad_sum}")
    print(f"Percentage of all students who graduated college: {percent_grad_college:.2f}%")
    print(f"Percentage of students who started college that graduated college: {percent_grad_college_started:.2f}%\n")

# Call the function
overall_enrollment_stats(df)

print("\nHigh School Summary:\n")
def calculate_college_statistics_by_school(df):
    """
    Calculate and print college-related statistics grouped by high schools.
    """
    valid_high_schools = ['Green Canyon', 'Mountain Crest', 'Sky View', 'Ridgeline']
    df['schools_attended'] = df['schools_attended'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    df_exploded = df.explode('schools_attended')
    filtered_df = df_exploded[df_exploded['schools_attended'].isin(valid_high_schools)]
    
    school_summary = filtered_df.groupby('schools_attended').agg(
        total_students=('student_number', 'size'),
        total_started_college=('start_college_y', 'sum'),
        total_graduated_college=('college_grad_y', 'sum')
    ).reset_index()

    school_summary['percent_started_college'] = school_summary['total_started_college'] / school_summary['total_students'] * 100
    school_summary['percent_graduated_college'] = school_summary['total_graduated_college'] / school_summary['total_students'] * 100
    school_summary['percent_graduated_started'] = school_summary.apply(
        lambda row: (row['total_graduated_college'] / row['total_started_college'] * 100) if row['total_started_college'] > 0 else 0, axis=1
    )

    for _, row in school_summary.iterrows():
        print(f"--- {row['schools_attended']} ---")
        print(f"Total Students: {row['total_students']}")
        print(f"Started College: {row['total_started_college']} ({row['percent_started_college']:.2f}%)")
        print(f"Graduated College: {row['total_graduated_college']} ({row['percent_graduated_college']:.2f}%)")
        print(f"Graduated (of Started): {row['percent_graduated_started']:.2f}%\n")

    return school_summary

# Call the function
school_summary = calculate_college_statistics_by_school(df)

print("\nMetrics for AC and Non-AC Students:\n")
def calculate_ac_non_ac_metrics(df):
    """Calculate and display metrics for AC and Non-AC students."""
    ac_students = df[df['ac_count'] > 1]
    non_ac_students = df[df['ac_count'] == 0]
    total_ac_students = ac_students.shape[0]
    ac_started_college = ac_students['start_college_y'].sum()
    ac_graduated_college = ac_students['college_grad_y'].sum()
    total_non_ac_students = non_ac_students.shape[0]
    non_ac_started_college = non_ac_students['start_college_y'].sum()
    non_ac_graduated_college = non_ac_students['college_grad_y'].sum()

    print("=== Metrics for AC Students (ac_count > 1) ===")
    print(f"Total AC students: {total_ac_students}")
    print(f"AC students who started college: {ac_started_college}")
    print(f"AC students who graduated college: {ac_graduated_college}")
    print(f"Percentage of AC students who started college: {(ac_started_college / total_ac_students) * 100:.2f}%")
    print(f"Percentage of AC students who graduated college: {(ac_graduated_college / total_ac_students) * 100:.2f}%")
    print(f"Percentage of the AC students who started college that graduated: {(ac_graduated_college / ac_started_college) * 100:.2f}%\n")

    print("=== Metrics for Non-AC Students (ac_count == 0) ===")
    print(f"Total Non-AC students: {total_non_ac_students}")
    print(f"Non-AC students who started college: {non_ac_started_college}")
    print(f"Non-AC students who graduated college: {non_ac_graduated_college}")
    print(f"Percentage of Non-AC students who started college: {(non_ac_started_college / total_non_ac_students) * 100:.2f}%")
    print(f"Percentage of Non-AC students who graduated college: {(non_ac_graduated_college / total_non_ac_students) * 100:.2f}%")
    print(f"Percentage of the Non-AC students who started college that graduated: {(non_ac_graduated_college / non_ac_started_college) * 100:.2f}%\n")

# Call the function
calculate_ac_non_ac_metrics(df)

pre_covid_years = [2017, 2018, 2019]
post_covid_years = [2021, 2022, 2023, 2024]

# Filter data for pre- and post-COVID years
df_pre_covid = df[df['year'].isin(pre_covid_years)]
df_post_covid = df[df['year'].isin(post_covid_years)]

def calculate_college_statistics_by_school(df):
    """
    Calculate college-related statistics grouped by high schools.
    """
    valid_high_schools = ['Green Canyon', 'Mountain Crest', 'Sky View', 'Ridgeline']
    df['schools_attended'] = df['schools_attended'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    df_exploded = df.explode('schools_attended')
    filtered_df = df_exploded[df_exploded['schools_attended'].isin(valid_high_schools)]
    
    school_summary = filtered_df.groupby('schools_attended').agg(
        total_students=('student_number', 'size'),
        total_started_college=('start_college_y', 'sum'),
        total_graduated_college=('college_grad_y', 'sum')
    ).reset_index()

    school_summary['percent_started_college'] = school_summary['total_started_college'] / school_summary['total_students'] * 100
    school_summary['percent_graduated_college'] = school_summary['total_graduated_college'] / school_summary['total_students'] * 100
    school_summary['percent_graduated_started'] = school_summary.apply(
        lambda row: (row['total_graduated_college'] / row['total_started_college'] * 100) if row['total_started_college'] > 0 else 0, axis=1
    )

    return school_summary

# Calculate pre- and post-COVID summaries
school_summary_pre_covid = calculate_college_statistics_by_school(df_pre_covid)
school_summary_post_covid = calculate_college_statistics_by_school(df_post_covid)

def visualize_pre_post_statistics(pre_summary, post_summary, metric, title, ylabel):
    """
    Visualize pre- and post-COVID statistics for a given metric.
    """
    pre_summary['period'] = 'Pre-COVID'
    post_summary['period'] = 'Post-COVID'
    combined_summary = pd.concat([pre_summary, post_summary])
    
    # Sort by the metric values (post-COVID for consistency)
    combined_summary = combined_summary.sort_values(by=metric, ascending=False)

    plt.figure(figsize=(12, 6))
    ax = sns.barplot(
        data=combined_summary,
        x="schools_attended",
        y=metric,
        hue="period",
        palette=[gray, navy]  # Pre-COVID: gray, Post-COVID: navy
    )

    # Add labels to each bar with percent signs
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f%%", label_type="edge", color="black", fontsize=10)

    plt.title(title, fontsize=16)
    plt.xlabel("School")
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# Graph 1: Pre- and Post-COVID College Start Rates
visualize_pre_post_statistics(
    pre_summary=school_summary_pre_covid,
    post_summary=school_summary_post_covid,
    metric="percent_started_college",
    title="Pre- and Post-COVID College Start Rates by School",
    ylabel="College Start Rate (%)"
)

# Graph 2: Pre- and Post-COVID College Graduation Rates
visualize_pre_post_statistics(
    pre_summary=school_summary_pre_covid,
    post_summary=school_summary_post_covid,
    metric="percent_graduated_college",
    title="Pre- and Post-COVID College Graduation Rates by School",
    ylabel="College Graduation Rate (%)"
)

# Most popular AC course visualization

# Load the clearinghouse data
clearing_old = pd.read_csv('data/Clearing House Data - USU Version.csv').drop_duplicates()
clearing_new = pd.read_csv('data/National Clearinghouse Data - Dec 2024.csv').drop_duplicates()

# Standardize student ID column for consistency
clearing_old = clearing_old.rename(columns={'Student Identifier': 'student_number'})
clearing_new = clearing_new.rename(columns={'Student Number': 'student_number'})

# Combine the datasets
clearing = pd.concat([clearing_old, clearing_new], ignore_index=True)
clearing = clearing.drop_duplicates()

# Load the pickled student data
with open('data/student_data.pkl', 'rb') as f:
    student_tables = pickle.load(f)
years = [2017, 2018, 2022, 2023, 2024]

# Create empty tables to store yearly data
all_membership = []
all_master = []
all_students = []
all_student_years = []

for year in years:
    master_year = pd.read_excel(f'data/{year} EOY Data - USU.xlsx', sheet_name='Course Master')
    membership_year = pd.read_excel(f'data/{year} EOY Data - USU.xlsx', sheet_name='Course Membership')
    student_year = student_tables[year]
    student_year['year'] = year

    all_master.append(master_year[['CollegeGrantingCr', 'WhereTaughtCampus', 'CourseTitle', 'CourseRecordID']].drop_duplicates())
    all_membership.append(membership_year[['StudentNumber', 'ConcurrEnrolled', 'CourseRecordID']].drop_duplicates())
    all_students.append(student_year[['student_number']].drop_duplicates())
    all_student_years.append(student_year[['student_number', 'year']].drop_duplicates())

# Combine yearly data
master = pd.concat(all_master, ignore_index=True)
membership = pd.concat(all_membership, ignore_index=True)
student = pd.concat(all_students, ignore_index=True)
student_years = pd.concat(all_student_years, ignore_index=True)

# Standardize columns
membership = membership.rename(columns={'StudentNumber': 'student_number'})
membership['student_number'] = membership['student_number'].astype(str)

# Merge student table and clearing data
student['student_number'] = student['student_number'].astype(str)
clearing['student_number'] = clearing['student_number'].astype(str)
student_clearing = pd.merge(student, clearing, on='student_number', how='left')

# Create ac_list for advanced courses
ac_list = pd.merge(master, membership, on='CourseRecordID', how='left').drop_duplicates()
ac_list = ac_list.rename(columns={'CourseTitle': 'course_title'})
ac_list = ac_list[
    (ac_list['CollegeGrantingCr'].notnull()) |
    (ac_list['WhereTaughtCampus'].notnull()) |
    (ac_list['ConcurrEnrolled'] == 'Y') |
    (ac_list['course_title'].str.startswith('AP', na=False)) |
    (ac_list['course_title'].str.startswith('BTEC', na=False))
]

def visualize_most_popular_courses(ac_list):
    """
    Visualize the most popular courses (not categorized).
    """
    course_counts = ac_list['course_title'].value_counts().reset_index()
    course_counts.columns = ['course_title', 'count']
    top_courses = course_counts.head(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top_courses, x='count', y='course_title', palette=usu_colors)
    plt.title("Most Popular Advanced Courses", fontsize=16)
    plt.xlabel("Number of Students", fontsize=12)
    plt.ylabel("Course Title", fontsize=12)
    plt.tight_layout()
    plt.show()

visualize_most_popular_courses(ac_list)

