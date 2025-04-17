import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import ast
import matplotlib as mpl

warnings.filterwarnings("ignore")

# USU color palette
usu_colors = ["#00274C", "#9EA2A2", "#D6D6D6"]

# Set global font to Montserrat and apply USU colors
plt.rcParams.update({
    "font.family": "Montserrat",  # Global font
    "axes.titlesize": 16,         # Title font size
    "axes.labelsize": 12,         # Axis label size
    "axes.labelcolor": usu_colors[0],  # Axis label color
    "xtick.color": usu_colors[0],      # X-tick color
    "ytick.color": usu_colors[0],      # Y-tick color
    "text.color": usu_colors[0]        # General text color
})
sns.set_palette(usu_colors)  # Apply USU color palette to Seaborn globally
sns.set_style("whitegrid")  # Set Seaborn style

# Load the df from CSV file
df = pd.read_csv("../data/clearinghouse_exploratory_data.csv")

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


# Visualization Functions
def visualize_college_statistics_by_school(school_summary):
    """Visualize college start and graduation rates grouped by school."""
    school_summary = school_summary.sort_values(by='percent_started_college', ascending=True)
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=school_summary,
        x="schools_attended",
        y="percent_started_college",
        palette=usu_colors
    )
    plt.title("College Start Rates by School", fontsize=16)
    plt.xlabel("School")
    plt.ylabel("College Start Rate (%)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    school_summary = school_summary.sort_values(by='percent_graduated_college', ascending=True)

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=school_summary,
        x="schools_attended",
        y="percent_graduated_college",
        palette=usu_colors
    )
    plt.title("College Graduation Rates by School", fontsize=16)
    plt.xlabel("School")
    plt.ylabel("College Graduation Rate (%)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# Visualize college statistics
visualize_college_statistics_by_school(school_summary)


import pickle
# Most popular AC course visualization (until new eda data is updated)

# Load the clearinghouse data
clearing_old = pd.read_csv('../data/Clearing House Data - USU Version.csv').drop_duplicates()
clearing_new = pd.read_csv('../data/National Clearinghouse Data - Dec 2024.csv').drop_duplicates()

# Standardize student ID column for consistency
clearing_old = clearing_old.rename(columns={'Student Identifier': 'student_number'})
clearing_new = clearing_new.rename(columns={'Student Number': 'student_number'})

# Combine the datasets
clearing = pd.concat([clearing_old, clearing_new], ignore_index=True)
clearing = clearing.drop_duplicates()

# Load the pickled student data
with open('../data/student_data.pkl', 'rb') as f:
    student_tables = pickle.load(f)
years = [2017, 2018, 2022, 2023, 2024]

# Create empty tables to store yearly data
all_membership = []
all_master = []
all_students = []
all_student_years = []

for year in years:
    master_year = pd.read_excel(f'../data/{year} EOY Data - USU.xlsx', sheet_name='Course Master')
    membership_year = pd.read_excel(f'../data/{year} EOY Data - USU.xlsx', sheet_name='Course Membership')
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