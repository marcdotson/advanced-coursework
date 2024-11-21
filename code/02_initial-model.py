import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression

df = pd.read_csv('data/01_cleaned_powerschool_data.csv')

y = df['ac_ind']
X = df.drop(columns = ['student_number'])
X = sm.add_constant(X[['days_attended', 'current_grade']]) # Add variable names here...

########################################################
# Add overall_gpa
# Dummy current_school
# Dummy current_grade
# How to use a regexp to select column names?
########################################################

mod = sm.Logit(y, X)
res = mod.fit()
res.summary()

