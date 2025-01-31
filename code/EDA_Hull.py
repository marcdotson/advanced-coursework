# EDA on 08_combined_modeling_data.csv (has one row per student) by Rebecca Hull

import pandas as pd

# Read CSV file
df = pd.read_csv("../data/08_combined_modeling_data.csv")

# Display the first few rows
print(df.head())

# Dimensions are 18,474 rows x 1563 columns
df.shape

# How many nulls in each column
df.isnull().sum()
# Can't see the entire table but the first several columns
# have no nulls but there are nulls as we keep going across columns

# Numerical Summaries
df['ac_ind'].describe()
# The mean of ac_ind is 0.468 with sd of 0.499, meaning 46.8% of all students have taken at least one AC

df['overall_gpa'].describe()
# The mean of overall_gpa 3.16 with sd of .905

df['days_attended'].describe()
# Mean of 268.0 days attended with sd of 140.917

df['days_absent'].describe()
# Mean of days absent is 8.27 with sd of 26.715. However I'm suspicious because the min is -359.

df['school_membership'].describe()
# Mean of 276.29 TOTAL days attended of school with sd 146.7. Confused about how this is different from days attended

df['percent_days_attended'].describe()
# Percent days attended mean is 100% with sd of 258.3%.

df['is_one_percent_y'].describe()
# The mean is 0.005, or 0.5%, with sd of 0.076, or 7.6%. This is least serious disability.

df['extended_school_year_y'].describe()
# The mean is 0.003, or 0.3%, with sd of 0.058, or 5.8%.

df['regular_percent_1.0'].describe()
# The mean is 0.055, or 5.5%, with sd of 0.228, or 22.8%.

df['regular_percent_2.0'].describe()
# The mean is 0.035, or 3.5%, with sd of 0.185, or 18.5%.

df['regular_percent_3.0'].describe()
# The mean is 0.004, or 0.4%, with sd of 0.064, 6.4%.

df['school_count'].describe()
# The mean is 1.908 with an sd of 0.86. The max is 6 which is interesting!
# I believe this is how many schools the high schooler has been to which in HS.

(df['composite_score'].isna() | (df['composite_score'] == '')).sum()
# 8816 total NAs or blanks

df['composite_score'].describe()
# When doing numerical summaries, it ignores the 8816 blanks
# The mean composite score is 21.05 with sd of 5.8.

(df['english_score'].isna() | (df['english_score'] == '')).sum()
# 8807 total NAs or blanks

df['english_score'].describe()
#The mean english score is 19.866 with sd of 6.26.

(df['reading_score'].isna() | (df['reading_score'] == '')).sum()
# 8812 total NAs or blanks

df['reading_score'].describe()
#The mean english score is 21.73 with sd of 6.47.

(df['science_score'].isna() | (df['science_score'] == '')).sum()
# 8816 total NAs or blanks

df['science_score'].describe()
#The mean english score is 21.13 with sd of 6.47.

(df['writing_score'].isna() | (df['writing_score'] == '')).sum()
# 17228 total NAs or blanks

df['writing_score'].describe()
#The mean english score is 6.68 with sd of 2.53.




#~~~~~~
# Check the proportion of missing data for each score column
missing_percentage = df[['composite_score', 'english_score', 'reading_score', 'science_score', 'writing_score']].isna().mean()
print(missing_percentage)

#composite_score    0.477211
#english_score      0.476724
#reading_score      0.476995
#science_score      0.477211
#writing_score      0.932554

# Check if missing data in 'composite_score' correlates with other variables
missing_composite = df[df['composite_score'].isna()]
print(missing_composite[['school_count', 'days_attended', 'ac_ind']].describe())

#      school_count  days_attended       ac_ind
#count   8571.000000    8816.000000  8816.000000
#mean       2.076304     220.201225     0.123412
#std        0.889069     123.112491     0.328928
#min        1.000000       0.000000     0.000000
#25%        1.000000     168.000000     0.000000
#50%        2.000000     180.000000     0.000000
#75%        3.000000     345.000000     0.000000
#max        6.000000     851.000000     1.000000


# Compared to school_count mean of 1.908 for all the data, a mean of 2.07 is not much different.
# Compared to days_attended mean of 286 for all the data, a mean of 220 seems somewhat close.
# Compared to ac_ind mean of 46.8% for all the data, a mean of 12.3% is significantly lower.
# Does this imply that those who take AC are also more likely to take the ACT?





# Check correlation between missing data in score columns and other features
df['missing_composite'] = df['composite_score'].isna().astype(int)
df['missing_english'] = df['english_score'].isna().astype(int)
df['missing_reading'] = df['reading_score'].isna().astype(int)
df['missing_science'] = df['science_score'].isna().astype(int)
df['missing_writing'] = df['writing_score'].isna().astype(int)

# Calculate correlations between missingness and other columns
correlation_matrix = df[['school_count', 'days_attended', 'missing_composite', 'missing_english', 'missing_reading', 'missing_science', 'missing_writing']].corr()
print(correlation_matrix)


# Adjust Pandas display options to show more rows and columns
pd.set_option('display.max_rows', 50)  # Adjust as necessary
pd.set_option('display.max_columns', 50)  # Adjust as necessary

# Print the correlation matrix again
print(correlation_matrix)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# suspicious of days_absent. maybe even days attended (sd of 140 seems large).
# also max of days attended is 851?    is this because it's a total? 180 x 4 = 720. Still too high

# I'm questioning the data integrity I guess?

# little confused by school membership bec wouldnt this be the same from days attended??