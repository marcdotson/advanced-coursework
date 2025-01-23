df = pd.read_csv('data/01_modeling_powerschool_data.csv')

import pandas as pd

print(df.columns)

'''
Index(['student_number', 'ac_ind', 'overall_gpa', 'days_attended',
       'ethnicity_y', 'amerindian_alaskan_y', 'asian_y',
       'black_african_amer_y', 'hawaiian_pacific_isl_y', 'white_y',
       ...
       'teacher_99561_grade_12', 'teacher_99561_grade_9',
       'teacher_99561_grade_nan', 'teacher_99615_grade_nan',
       'teacher_99679_grade_nan', 'teacher_99736_grade_10',
       'teacher_99736_grade_11', 'teacher_99736_grade_12',
       'teacher_99736_grade_9', 'teacher_99802_grade_nan'],
      dtype='object', length=2242)'

'''


# Basic Information
print("Shape of the dataset:")
print(df.shape)  # Rows and columns

#7277 rows, 2242 columns

print("\nData types of each column:")
print(df.dtypes)  # Data types

'''
student_number               int64
ac_ind                     float64
overall_gpa                float64
days_attended                int64
ethnicity_y                  int64
                            ...   
teacher_99736_grade_10     float64
teacher_99736_grade_11     float64
teacher_99736_grade_12     float64
teacher_99736_grade_9      float64
teacher_99802_grade_nan    float64
Length: 2242, dtype: object
'''

print("\nSample of the dataset:")
print(df.head())  # First 5 rows

print("\nSummary statistics:")
print(df.describe(include='all'))  # Summary statistics for numeric and categorical columns

#overall gpa summary statistics
print(df['overall_gpa'].describe())
# mean = 2.1, std = 1.68

#overall days attended statistics
print(df['days_attended'].describe())
# mean = 156.66, std = 42.1

print("\nNull values in each column:")
print(df.isnull().sum())  # Count of missing values in each column

'''
student_number               0
ac_ind                       0
overall_gpa                  0
days_attended                0
ethnicity_y                  0
                          ... 
teacher_99736_grade_10     175
teacher_99736_grade_11     175
teacher_99736_grade_12     175
teacher_99736_grade_9      175
teacher_99802_grade_nan    175
'''


# Column Names
print("\nColumn Names:")
print(df.columns.tolist())  # List all column names


# Correlation Matrix for Numeric Columns
numeric_columns = df.select_dtypes(include=['number']).columns
print("\nCorrelation Matrix for Numeric Columns:")
print(df[numeric_columns].corr())



####If I want a correlation matrix of a subset of variables
subset_df = df.iloc[:, :7]  # Slice the first 7 columns

# Identify numeric columns in the subset
numeric_columns = subset_df.select_dtypes(include=['number']).columns

# Calculate and print the correlation matrix for numeric columns
print("\nCorrelation Matrix for the First 21 Numeric Columns:")
correlation_matrix = subset_df[numeric_columns].corr()
print(correlation_matrix)





###########################################
# making charts


import matplotlib.pyplot as plt

subset_df = df.iloc[:, :21]

# Histograms for Numeric Columns
plt.hist(subset_df['overall_gpa'].dropna(), bins=30); plt.show()

plt.hist(subset_df['days_attended'].dropna(), bins=30); plt.show()








# Select columns related to current grades
current_grade_cols = [col for col in df.columns if col.startswith("current_grade_")]

# Sum up the values in each grade column to get the count of students
grade_counts = df[current_grade_cols].sum()

# Create a bar chart
plt.figure(figsize=(8, 5))
grade_counts.plot(kind='bar', color='skyblue', edgecolor='black')

# Customize the plot
plt.title("Number of Students in Each Current Grade", fontsize=14)
plt.xlabel("Grade", fontsize=12)
plt.ylabel("Number of Students", fontsize=12)
plt.xticks(ticks=range(len(current_grade_cols)), labels=[col.replace("current_grade_", "Grade ") for col in current_grade_cols], rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Show the plot
plt.show()
###########################################

# Select columns related to current grades
current_grade_cols = [col for col in df.columns if col.startswith("current_grade_")]

# Sum up the values in each grade column to get the count of students
grade_counts = df[current_grade_cols].sum()

# Create a bar chart
plt.figure(figsize=(8, 5))
bars = plt.bar(
    x=range(len(current_grade_cols)),
    height=grade_counts,
    color='skyblue',
    edgecolor='black'
)

# Add labels on top of each bar
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,  # Position at the center of the bar
        height + 0.5,  # Slightly above the bar
        f'{int(height)}',  # Label as an integer
        ha='center',
        fontsize=10
    )

# Customize the plot
plt.title("Number of Students in Each Current Grade", fontsize=14)
plt.xlabel("Grade", fontsize=12)
plt.ylabel("Number of Students", fontsize=12)
plt.xticks(
    ticks=range(len(current_grade_cols)),
    labels=[col.replace("current_grade_", "Grade ") for col in current_grade_cols],
    rotation=45
)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Show the plot
plt.show()