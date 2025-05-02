# Import libraries
import pandas as pd
import warnings

# Suppress warnings and set display options
warnings.filterwarnings("ignore")
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: f'{x:.2f}')

# Load dataset
data = pd.read_csv("../data/exploratory_data.csv")

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

def calculate_academic_statistics(data):
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

    # Post-COVID statistics (2022, 2023, 2024)
    post_covid_years = [2022, 2023, 2024]
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

def analyze_school_data(data):
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
    post_covid_years = [2022, 2023, 2024]
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
    calculate_academic_statistics(data)

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
    analyze_school_data(data)