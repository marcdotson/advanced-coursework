# Import libraries
import pandas as pd
import warnings
import ast

# Specify all years
years = [2017, 2018, 2022, 2023, 2024, 2025]

# Suppress warnings and set display options
warnings.filterwarnings("ignore")
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: f'{x:.2f}')

##########################################################################
# PHASE ONE - Exploratory Data
# Load dataset
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

def summarize_dataset(data):
    """Display dataset structure and sample rows."""
    print_section_header("Summary Statistics")
    print(f"Years in dataset: {data['year'].unique()}\n")
    data.info()

def calculate_academic_statistics(data, years):
    """Calculate district-level academic stats."""
    # Overall statistics
    total = len(data)
    ac_students = data[data['ac_ind'] == 1].shape[0]
    avg_gpa = data[data['overall_gpa'] != 0]['overall_gpa'].mean()
    avg_gpa_non_ac = data[data['ac_ind'] == 0]['overall_gpa'].mean()
    avg_gpa_ac = data[data['ac_ind'] == 1]['overall_gpa'].mean()
    avg_ac_count = data[data['ac_count'] > 0]['ac_count'].mean()

    print("=== Overall Statistics ===")
    print(f"Total students: {total}")
    print(f"AC course takers: {ac_students} ({ac_students / total:.2%})")
    print(f"Avg GPA: {avg_gpa:.2f}")
    print(f"Avg GPA (Non-AC students): {avg_gpa_non_ac:.2f}")
    print(f"Avg GPA (AC students): {avg_gpa_ac:.2f}")
    print(f"Avg AC courses taken per AC student: {avg_ac_count:.2f}")

    # Post-COVID statistics
    years_temp = pd.Series(years)
    post_covid_years = years_temp[years_temp >= 2022].tolist()
    post_covid_data = data[data['year'].isin(post_covid_years)]
    total_post_covid = len(post_covid_data)
    ac_students_post_covid = post_covid_data[post_covid_data['ac_ind'] == 1].shape[0]
    avg_gpa_post_covid = post_covid_data[post_covid_data['overall_gpa'] != 0]['overall_gpa'].mean()
    avg_gpa_non_ac_post_covid = post_covid_data[post_covid_data['ac_ind'] == 0]['overall_gpa'].mean()
    avg_gpa_ac_post_covid = post_covid_data[post_covid_data['ac_ind'] == 1]['overall_gpa'].mean()
    avg_ac_count_post_covid = post_covid_data[post_covid_data['ac_count'] > 0]['ac_count'].mean()

    print("\n=== Post-COVID Statistics (2022-2024) ===")
    print(f"Total students: {total_post_covid}")
    print(f"AC course takers: {ac_students_post_covid} ({ac_students_post_covid / total_post_covid:.2%})")
    print(f"Avg GPA: {avg_gpa_post_covid:.2f}")
    print(f"Avg GPA (Non-AC students): {avg_gpa_non_ac_post_covid:.2f}")
    print(f"Avg GPA (AC students): {avg_gpa_ac_post_covid:.2f}")
    print(f"Avg AC courses taken per AC student: {avg_ac_count_post_covid:.2f}")

def analyze_demographics(data):
    """Analyze student demographics with 'Y' indicator only."""
    ethnic_cols = [
        'amerindian_alaskan', 'asian', 'black_african_amer',
        'hawaiian_pacific_isl', 'white', 'migrant', 'immigrant',
        'refugee_student', 'ethnicity'
    ]

    # Counts of 'Y' in ethnic and gender columns
    ethnic_counts = data[ethnic_cols].apply(lambda col: (col == 'Y').sum())
    ethnic_counts_ac = data[data['ac_ind'] == 1][ethnic_cols].apply(lambda col: (col == 'Y').sum())
    ethnic_proportion_ac = (ethnic_counts_ac / ethnic_counts_ac.sum()).map('{:.2%}'.format) 
    gender_counts = data['gender'].value_counts()
    gender_counts_ac = data[data['ac_ind'] == 1]['gender'].value_counts()
    gender_proportion_ac = (gender_counts_ac / gender_counts_ac.sum()).map('{:.2%}'.format)

    print(f"=== Total ethnic group counts ===\n{ethnic_counts}")
    print(f"\n=== Total ethnic group counts for AC students ===\n{ethnic_counts_ac}\n")
    print(f"\n=== Proportion of each ethnic group taking AC courses ===\n{ethnic_proportion_ac}")
    print(f"=== Gender counts ===\n{gender_counts}")
    print(f"\n=== AC enrollment counts by gender ===\n{gender_counts_ac}")
    print(f"\n=== Proportion of each gender taking AC courses ===\n{gender_proportion_ac}")

def analyze_indicators(data, indicators):
    """Compare total and AC students for each indicator."""
    print("\n=== AC enrollment rates across various indicators ===")
    for indicator in indicators:
        print(f"\n=== {indicator} ===")
        total_counts = data[indicator].value_counts()
        ac_counts = data[data['ac_ind'] == 1][indicator].value_counts()

        results = [
            (value, ac_counts.get(value, 0), total, ac_counts.get(value, 0) / total if total > 0 else 0)
            for value, total in total_counts.items()
        ]
        results.sort(key=lambda x: x[3], reverse=True)

        for value, ac, total, rate in results:
            print(f"{value}: {ac}/{total} ({rate:.2%})")

def analyze_school_data(data, years):
    """Analyze AC course and student data across the district and schools, including post-COVID analysis."""
    # Define high schools
    high_schools = ['Green Canyon', 'Sky View', 'Mountain Crest', 'Ridgeline']

    # Mean GPA of AC courses by school
    school_mean_gpa = data[(data['ac_gpa'] > 0) & (data['current_school'].isin(high_schools))].groupby('current_school')['ac_gpa'].mean().sort_values(ascending=False)
    print(f"\nMean GPA of AC courses by school:\n{school_mean_gpa}\n")

    # Total AC courses in the district
    ac_count_district_total = data['ac_count'].sum()
    print(f"Number of AC classes in the district: {ac_count_district_total}")

    # Post-COVID AC courses in the district
    years_temp = pd.Series(years)
    post_covid_years = years_temp[years_temp >= 2022].tolist()
    ac_count_district_total_post_covid = data[data['year'].isin(post_covid_years)]['ac_count'].sum()
    print(f"Number of AC classes in the district post-covid: {ac_count_district_total_post_covid}\n")

    # AC courses by school
    school_ac_count = data[data['current_school'].isin(high_schools)].groupby('current_school')['ac_count'].sum().sort_values(ascending=False)
    print(f"Number of total AC courses taken in each school:\n{school_ac_count}\n")

    # Post-COVID AC courses by school
    school_ac_count_post_covid = data[data['year'].isin(post_covid_years) & data['current_school'].isin(high_schools)].groupby('current_school')['ac_count'].sum().sort_values(ascending=False)
    print(f"Number of AC courses taken in each school post-COVID:\n{school_ac_count_post_covid}\n")

    # Total AC students in the district
    district_ac_students = len(data[(data['ac_ind'] == 1) & (data['current_school'].isin(high_schools))])
    print(f"Number of AC students in the district: {district_ac_students}")

    # Post-COVID AC students in the district
    district_ac_students_post_covid = len(data[(data['year'].isin(post_covid_years)) & (data['ac_ind'] == 1) & (data['current_school'].isin(high_schools))])
    print(f"Number of AC students in the district post-covid: {district_ac_students_post_covid}")
    print(f"Proportion of AC students in the data that are post-covid: {district_ac_students_post_covid / district_ac_students:.2%}\n")

    # AC students by school
    school_ac_students = data[(data['ac_ind'] == 1) & (data['current_school'].isin(high_schools))].groupby('current_school')['ac_ind'].count().sort_values(ascending=False)
    print(f"Number of AC students in each school:\n{school_ac_students}\n")

    # Post-COVID AC students by school
    school_ac_students_post_covid = data[(data['year'].isin(post_covid_years)) & (data['ac_ind'] == 1) & (data['current_school'].isin(high_schools))].groupby('current_school')['ac_ind'].count().sort_values(ascending=False)
    print(f"Number of AC students in each school post-covid:\n{school_ac_students_post_covid}")

    # Average AC students to non-AC students by school
    average_ac_to_nonac_by_school = (school_ac_students / (school_ac_count - school_ac_students)).sort_values(ascending=False)
    print(f"\nAverage number of AC students to each non-AC student at each school:\n{average_ac_to_nonac_by_school}")

    # Post-COVID average AC students to non-AC students by school
    average_ac_to_nonac_by_school_postcovid = (school_ac_students_post_covid / (school_ac_count_post_covid - school_ac_students_post_covid)).sort_values(ascending=False)
    print(f"\nAverage number of AC students to each non-AC student at each school post-COVID:\n{average_ac_to_nonac_by_school_postcovid}")

    # Average AC classes per AC student by school
    average_ac_classes_per_ac_student_by_school = (school_ac_count / school_ac_students).sort_values(ascending=False)
    print(f"\nAverage AC classes per AC student by school:\n{average_ac_classes_per_ac_student_by_school}")

    # Post-COVID average AC classes per AC student by school
    average_ac_classes_per_ac_student_by_school_postcovid = (school_ac_count_post_covid / school_ac_students_post_covid).sort_values(ascending=False)
    print(f"\nAverage AC classes per AC student by school post-COVID:\n{average_ac_classes_per_ac_student_by_school_postcovid}")

# === Main Processing ===
if __name__ == "__main__":
    summarize_dataset(data)

    print_section_header("District-Wide Analysis")
    calculate_academic_statistics(data, years)

    print_section_header("Demographic Data Analysis")
    analyze_demographics(data)

    indicators = [
        'military_child', 'passed_civics_exam', 'reading_intervention',
        'hs_complete_status', 'tribal_affiliation', 'services_504',
        'homeless_y', 'environment',
        'part_time_home_school_y', 'ell_disability_group'
    ]
    analyze_indicators(data, indicators)

    print_section_header("School Analysis")
    analyze_school_data(data, years)

##########################################################################
# PHASE TWO - Clearinghouse Exploratory Data
# Load the df from CSV file
df = pd.read_csv("data/clearinghouse_exploratory_data.csv")

print("Clearinghouse Exploratory Data Analysis\n")

# Display years in the dataset
years = df['year'].unique()
print(f"Years in data set: {', '.join(map(str, years))}\n")

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

