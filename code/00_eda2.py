import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import ast

warnings.filterwarnings("ignore")

# Load the df from CSV file
df = pd.read_csv("../data/clearinghouse_exploratory_data.csv")

print("Clearinghouse Exploratory Data Analysis\n")

# Display years in the dataset
years = df['year'].unique()
print(f"Years in data set: {', '.join(map(str, years))}\n")

# # Display column names
# print("Columns in the dataset:")
# for column in df.columns:
#     print(column, end=',\n')


print("\nOverall District Summary:\n")

def overall_enrollment_stats(df):
    """
    Generate and print an overall district summary based on the provided DataFrame.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the data.

    Returns:
    None
    """

    # Total number of students
    total_students = df.shape[0]
    print(f"Total number of students in the dataset: {total_students}")

    # Total number of students who started college
    total_started_college = df[df['start_college_y'] == 1]['start_college_y'].sum()
    print(f"Total number of students who started college: {total_started_college}")

    # Percentage of students who started college
    percent_started_college = (total_started_college / total_students) * 100
    print(f"Percentage of all students who started college: {percent_started_college:.2f}%")

    # Total number of students who graduated college
    college_grad_sum = df['college_grad_y'].sum()
    print(f"Total number of students who graduated college: {college_grad_sum}")

    # Percentage of students who graduated college
    percent_grad_college = (college_grad_sum / total_students) * 100
    print(f"Percentage of all students who graduated college: {percent_grad_college:.2f}%")

    # Percentage of students who started college that graduated college
    percent_grad_college_started = (college_grad_sum / total_started_college) * 100
    print(f"Percentage of students who started college that graduated college: {percent_grad_college_started:.2f}%\n")

# Call the function
overall_enrollment_stats(df)


print("\nHigh School Summary:\n")
def calculate_college_statistics_by_school(df):
    """
    Calculate and print college-related statistics (e.g., enrollment and graduation rates) grouped by specific high schools.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the dataset.

    Returns:
    - pd.DataFrame: A summary DataFrame with college statistics for each specified high school.
    """
    # Define the high schools to include
    valid_high_schools = ['Green Canyon', 'Mountain Crest', 'Sky View', 'Ridgeline']
    
    # Convert the `schools_attended` column from strings to actual lists
    df['schools_attended'] = df['schools_attended'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # Explode the `schools_attended` column to handle students in multiple schools
    df_exploded = df.explode('schools_attended')
    
    # Filter for the specified high schools
    filtered_df = df_exploded[df_exploded['schools_attended'].isin(valid_high_schools)]
    
    # Group by 'schools_attended' and calculate statistics
    school_summary = filtered_df.groupby('schools_attended').agg(
        total_students=('student_number', 'size'),
        total_started_college=('start_college_y', 'sum'),
        total_graduated_college=('college_grad_y', 'sum')
    ).reset_index()

    # Add percentage calculations with safeguards against division by zero
    school_summary['percent_started_college'] = school_summary['total_started_college'] / school_summary['total_students'] * 100
    school_summary['percent_graduated_college'] = school_summary['total_graduated_college'] / school_summary['total_students'] * 100
    school_summary['percent_graduated_started'] = school_summary.apply(
        lambda row: (row['total_graduated_college'] / row['total_started_college'] * 100) if row['total_started_college'] > 0 else 0, axis=1
    )

    # Print statistics for each school
    for _, row in school_summary.iterrows():
        print(f"--- {row['schools_attended']} ---")
        print(f"Total Students: {row['total_students']}")
        print(f"Started College: {row['total_started_college']} ({row['percent_started_college']:.2f}%)")
        print(f"Graduated College: {row['total_graduated_college']} ({row['percent_graduated_college']:.2f}%)")
        print(f"Graduated (of Started): {row['percent_graduated_started']:.2f}%\n")

    return school_summary
# Call the function
calculate_college_statistics_by_school(df)


print("\nMetrics for AC and Non-AC Students:\n")
# Metrics for AC and Non-AC students
def calculate_ac_non_ac_metrics(df):
    """Calculate and display metrics for AC and Non-AC students."""
    # Filter AC students (ac_count > 1)
    ac_students = df[df['ac_count'] > 1]
    total_ac_students = ac_students.shape[0]
    ac_started_college = ac_students['start_college_y'].sum()
    ac_graduated_college = ac_students['college_grad_y'].sum()
    
    # Filter Non-AC students (ac_count == 0)
    non_ac_students = df[df['ac_count'] == 0]
    total_non_ac_students = non_ac_students.shape[0]
    non_ac_started_college = non_ac_students['start_college_y'].sum()
    non_ac_graduated_college = non_ac_students['college_grad_y'].sum()
    
    # Display metrics
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


print("\nDemographic Analysis:\n")
# Demographic Analysis for AC and Non-AC Students
def analyze_demographics_effect_ac_students(df, demographic_col):
    """
    Analyze AC students (ac_count > 1) by demographic column.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the dataset.
    - demographic_col (str): The demographic column to analyze.

    Returns:
    - pd.DataFrame: A summary DataFrame with metrics for AC students.
    """
    # Filter for AC students
    ac_students_df = df[df['ac_count'] > 1]
    
    # Check if the demographic column exists
    if demographic_col not in ac_students_df.columns:
        print(f"Column '{demographic_col}' not found in the DataFrame.")
        return None

    # Group by demographic column and calculate metrics
    summary = ac_students_df.groupby(demographic_col).agg(
        total_students=('student_number', 'size'),
        avg_ac_count=('ac_count', 'mean'),
        percent_started_college=('start_college_y', lambda x: (x.sum() / len(x)) * 100),
        percent_graduated_college=('college_grad_y', lambda x: (x.sum() / len(x)) * 100)
    ).reset_index()

    # Rename the columns for readability
    summary.columns = [
        demographic_col, 
        'Total AC Students', 
        'Avg AC Classes', 
        '% Started College', 
        '% Graduated College', 
    ]
    return summary
def analyze_demographics_effect_non_ac_students(df, demographic_col):
    """
    Analyze Non-AC students (ac_count == 0) by demographic column.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the dataset.
    - demographic_col (str): The demographic column to analyze.

    Returns:
    - pd.DataFrame: A summary DataFrame with metrics for Non-AC students.
    """
    # Filter for Non-AC students
    non_ac_students_df = df[df['ac_count'] == 0]
    
    # Check if the demographic column exists
    if demographic_col not in non_ac_students_df.columns:
        print(f"Column '{demographic_col}' not found in the DataFrame.")
        return None

    # Group by demographic column and calculate metrics
    summary = non_ac_students_df.groupby(demographic_col).agg(
        total_students=('student_number', 'size'),
        avg_ac_count=('ac_count', 'mean'),
        percent_started_college=('start_college_y', lambda x: (x.sum() / len(x)) * 100),
        percent_graduated_college=('college_grad_y', lambda x: (x.sum() / len(x)) * 100)
    ).reset_index()

    summary.columns = [
        demographic_col, 
        'Total Non-AC Students', 
        'Avg AC Classes', 
        '% Started College', 
        '% Graduated College', 
    ]
    return summary

# Establish variables
demographic_variables = [
    'gender', 'ethnicity', 'environment', 'extended_school_year', 
    'amerindian_alaskan', 'asian', 'black_african_amer', 
    'hawaiian_pacific_isl', 'white', 'migrant', 'military_child', 
    'refugee_student', 'services_504', 'immigrant', 'passed_civics_exam',
    'homeless_y', 'part_time_home_school_y', 'ell_disability_group', 
    'hs_complete_status', 'tribal_affiliation'
]

# Loop through demographics and analyze
for var in demographic_variables:
    print(f"\n=== Analysis for {var} (AC Students Only) ===")
    ac_summary = analyze_demographics_effect_ac_students(df, var)
    if ac_summary is not None:
        print(ac_summary)

    print(f"\n=== Analysis for {var} (Non-AC Students Only) ===")
    non_ac_summary = analyze_demographics_effect_non_ac_students(df, var)
    if non_ac_summary is not None:
        print(non_ac_summary)


def analyze_ap_courses(df):
    """
    Analyze AP course data by valid high schools (Green Canyon, Mountain Crest, Sky View, Ridgeline).

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the dataset.

    Returns:
    - dict: A dictionary containing:
        - Number of AP courses offered per school.
        - Types of AP courses available per school.
        - Percentage of the student body enrolled in AP courses by school.
        - Distribution of AP courses across grade levels by school.
    """
    # Define the valid high schools to include
    valid_high_schools = ["Green Canyon", "Mountain Crest", "Sky View", "Ridgeline"]

    # Convert the `schools_attended` column from strings to actual lists
    df['schools_attended'] = df['schools_attended'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # Explode the `schools_attended` column to handle students in multiple schools
    df_exploded = df.explode('schools_attended')

    # Filter for rows where `schools_attended` contains valid high schools
    df_filtered = df_exploded[df_exploded['schools_attended'].isin(valid_high_schools)]

    # Ensure AP course columns are identified
    ap_course_columns = [col for col in df_filtered.columns if "AP" in col and "Course" in col]

    # Check for necessary columns
    required_columns = ["schools_attended", "current_grade", "student_number"]
    for col in required_columns:
        if col not in df_filtered.columns:
            raise ValueError(f"Missing required column: {col}")

    # Analyze AP courses per school
    school_summary = df_filtered.groupby('schools_attended')

    # 1. Number of AP courses offered per school
    ap_courses_per_school = school_summary[ap_course_columns].sum()

    # 3. Percentage of the student body enrolled in AP courses by school
    def calculate_ap_enrollment(row):
        return row[ap_course_columns].sum() > 0

    df_filtered['enrolled_in_ap'] = df_filtered.apply(calculate_ap_enrollment, axis=1)
    ap_enrollment_rate = school_summary['enrolled_in_ap'].mean() * 100

    # 4. Distribution of AP courses across grade levels by school
    ap_courses_by_grade = df_filtered.groupby(['schools_attended', 'current_grade'])[ap_course_columns].sum()

    # Compile the results into a dictionary
    results = {
        "ap_courses_per_school": ap_courses_per_school,
        "ap_enrollment_rate": ap_enrollment_rate,
        "ap_courses_by_grade": ap_courses_by_grade,
    }

    return results

# Call the function
results = analyze_ap_courses(df)

# Printing results
print("Number of AP courses offered per school:")
print(results['ap_courses_per_school'])

print("\nTypes of AP courses available per school:")
for school, courses in results['ap_types_per_school'].items():
    print(f"{school}: {courses}")

print("\nPercentage of the student body enrolled in AP courses by school:")
print(results['ap_enrollment_rate'])

print("\nDistribution of AP courses across grade levels by school:")
print(results['ap_courses_by_grade'])


import pandas as pd
import ast

def analyze_course_popularity(df):
    """
    Analyze the popularity of course categories on a school-by-school basis.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the dataset.

    Returns:
    - pd.DataFrame: A DataFrame showing the most popular course categories for each school.
    """
    # Define the valid high schools to include
    valid_high_schools = ["Green Canyon", "Mountain Crest", "Sky View", "Ridgeline"]

    # Define the course categories
    course_categories = [
        "Agriculture & Horticulture",
        "Arts & Design",
        "BTECH Courses",
        "Business",
        "Concurrent Courses",
        "Health & Medical Sciences",
        "Humanities & Social Sciences",
        "Languages",
        "Other",
        "Science & Math",
        "Technology"
    ]

    # Convert the `schools_attended` column from strings to actual lists
    df['schools_attended'] = df['schools_attended'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # Explode the `schools_attended` column to handle students in multiple schools
    df_exploded = df.explode('schools_attended')

    # Filter for rows where `schools_attended` contains valid high schools
    df_filtered = df_exploded[df_exploded['schools_attended'].isin(valid_high_schools)]

    # Group by school and sum the counts for each course category
    course_popularity = df_filtered.groupby('schools_attended')[course_categories].sum()

    # Add a column for the most popular course category in each school
    course_popularity['Most Popular Category'] = course_popularity.idxmax(axis=1)
    course_popularity['Most Popular Count'] = course_popularity.max(axis=1)

    # Sort results by most popular count for better readability
    sorted_popularity = course_popularity.sort_values(by='Most Popular Count', ascending=False)

    return sorted_popularity

# Call the function
results = analyze_course_popularity(df)

# Printing results
print("Course Popularity by School:")
print(results)


# # Visualization Example for Gender
# gender_ac = analyze_demographics_effect_ac_students(df, 'gender')
# gender_non_ac = analyze_demographics_effect_non_ac_students(df, 'gender')

# # Bar plot for % Started College by Gender
# sns.barplot(x='gender', y='% Started College', data=gender_ac)
# plt.title('College Start Rates by Gender (AC Students Only)')
# plt.show()

# sns.barplot(x='gender', y='% Started College', data=gender_non_ac)
# plt.title('College Start Rates by Gender (Non-AC Students Only)')
# plt.show()

# # Bar plot for % Graduated College by Gender
# sns.barplot(x='gender', y='% Graduated College', data=gender_ac)
# plt.title('College Graduation Rates by Gender (AC Students Only)')
# plt.show()

# sns.barplot(x='gender', y='% Graduated College', data=gender_non_ac)
# plt.title('College Graduation Rates by Gender (Non-AC Students Only)')
# plt.show()