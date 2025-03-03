import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from scipy.stats import norm

# Define the folder path where the confidence interval plot will be saved
output_folder = "output/"
figure_folder = "figures/"

# Ensure directories exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs(figure_folder, exist_ok=True)

# Load dataset
df = pd.read_csv('data/modeling_data.csv', low_memory=False)

################################################################################################
# RUN THE FLAT MODEL USING SCIKIT-LEARN AND EXPORT DRAWS TO A FILE
################################################################################################

# Convert categorical variables into dummies
df = pd.get_dummies(df, drop_first=False)

# Define target and predictors
y = df['ac_ind']
X_drop = ['student_number', 'ac_ind', 'ell_disability_group_non_ell_without_disability']
X = df.drop(columns=X_drop, axis=1)

# Fit logistic regression model
log_reg = LogisticRegression(fit_intercept=True, max_iter=10000)
log_reg.fit(X, y)

# Extract feature names and coefficients
coef_df = pd.DataFrame({'Feature': X.columns, 'Coefficient': log_reg.coef_[0]})

# Select the top 10 most influential variables (absolute value)
coef_df['Abs_Coefficient'] = coef_df['Coefficient'].abs()
top_10_coef_df = coef_df.nlargest(10, 'Abs_Coefficient').drop(columns=['Abs_Coefficient'])
top_10_features = top_10_coef_df["Feature"].values

################################################################################################
# OPTIMIZED CONFIDENCE INTERVAL CALCULATION (ONLY FOR TOP 10 VARIABLES)
################################################################################################

# Filter X to only include the top 10 features
X_top10 = X[top_10_features]

# Compute Hessian for only the top 10 variables
X_with_intercept = np.column_stack((np.ones(X.shape[0]), X_top10))  # Add intercept manually
p = log_reg.predict_proba(X)[:, 1]  # Predicted probabilities
V = np.diag(p * (1 - p))  # Variance matrix (diagonal)
Hessian = X_with_intercept.T @ V @ X_with_intercept  # Hessian for top 10
cov_matrix = np.linalg.inv(Hessian)  # Covariance matrix
standard_errors = np.sqrt(np.diag(cov_matrix)[1:])  # Extract standard errors (excluding intercept)

# Compute confidence intervals (95%)
z_critical = norm.ppf(0.975)  # 1.96 for 95% confidence
top_10_coef_df["conf_low"] = top_10_coef_df["Coefficient"] - z_critical * standard_errors
top_10_coef_df["conf_high"] = top_10_coef_df["Coefficient"] + z_critical * standard_errors

################################################################################################
# SORT COEFFICIENTS IN DESCENDING ORDER FOR PLOTTING
################################################################################################
# Sort by coefficient values in descending order for clear visualization
top_10_coef_df = top_10_coef_df.sort_values(by="Coefficient", ascending=False).reset_index(drop=True)

print(top_10_coef_df[['Feature', 'Coefficient']])
# Reverse the order of rows for correct plotting
top_10_coef_df = top_10_coef_df[::-1].reset_index(drop=True)


################################################################################################
# PLOT CONFIDENCE INTERVALS FOR TOP 10 VARIABLES
################################################################################################
plt.figure(figsize=(10, 10))
plt.errorbar(top_10_coef_df['Coefficient'], top_10_coef_df['Feature'],
             xerr=[top_10_coef_df['Coefficient'] - top_10_coef_df['conf_low'], 
                   top_10_coef_df['conf_high'] - top_10_coef_df['Coefficient']], 
             fmt='o', capsize=5, label='Estimates')

plt.axvline(0, color='red', linestyle='--', label='Zero Line')
plt.xlabel("Coefficient Estimate")
plt.ylabel("Feature")
plt.title("Confidence Intervals for Top 10 Most Influential Variables (Sorted)")
plt.subplots_adjust(left=0.3)  # Increase left margin for long labels
plt.legend()

# Save the plot
plt.savefig(os.path.join(figure_folder, "flat-model-confidence-interval-sorted.png"), format="png")
print("Sorted confidence interval plot saved successfully!")
