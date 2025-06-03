# Import libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from scipy.stats import gaussian_kde

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

# Load the data from CSV files
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