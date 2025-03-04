import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from scipy.stats import norm

# Define the folder path where the output files will be saved
folder_path = "output/"

# Check if the folder exists, and create it if not
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Load the dataset
df = pd.read_csv('data\post_covid_modeling_data.csv', low_memory=False)

################################################################################################
# RUN THE FLAT MODEL USING SCIKIT-LEARN AND EXPORT DRAWS TO A FILE
################################################################################################

# Convert categorical variables into dummies
df = pd.get_dummies(df, drop_first =False)

# Define target and predictors
y = df['ac_ind']
X_drop = ['student_number', 'ac_ind', 'ell_disability_group_non_ell_without_disability']
X = df.drop(columns=X_drop, axis=1)

# Fit logistic regression model
log_reg = LogisticRegression(fit_intercept=True, max_iter=10000)
log_reg.fit(X, y)

# Extract feature names and coefficients
coef_df = pd.DataFrame({'Feature': X.columns, 'Coefficient': log_reg.coef_[0]})

# Sort by absolute coefficient value (most influential first)
coef_df = coef_df.sort_values(by='Coefficient', ascending=False)
print("Scikit Logistic regression coefficients saved successfully!")

################################################################################################
# CALCULATING CONFIDENCE INTERVALS IN BATCHES (HESSIAN COMPUTATION IN BATCHES)
################################################################################################

# Compute predicted probabilities
p = log_reg.predict_proba(X)[:, 1]

# Batch size for Hessian computation
batch_size = 3
num_features = X.shape[1]

# Prepare results dataframe
results = []

# Iterate through the features in batches
for i in range(0, num_features, batch_size):
    batch_features = X.iloc[:, i:i + batch_size]  # Select batch of features
    batch_X = np.column_stack((np.ones(X.shape[0]), batch_features))  # Add intercept
    
    # Compute Hessian for the batch
    V = np.diag(p * (1 - p))  # Variance matrix
    Hessian_batch = batch_X.T @ V @ batch_X  # Hessian for the batch

    # Compute inverse Hessian (covariance matrix) for the batch
    try:
        cov_matrix_batch = np.linalg.inv(Hessian_batch)
    except np.linalg.LinAlgError:
        print(f"Singular matrix encountered in batch {i // batch_size + 1}, skipping...")
        continue  # Skip if the matrix is singular

    # Compute standard errors for the batch
    standard_errors_batch = np.sqrt(np.diag(cov_matrix_batch)[1:])  # Skip intercept

    # Compute confidence intervals (95%)
    z_critical = norm.ppf(0.975)  # 1.96 for 95% confidence
    batch_coefs = coef_df.iloc[i:i + batch_size].copy()  # Select corresponding coefficients
    batch_coefs["conf_low"] = batch_coefs["Coefficient"] - z_critical * standard_errors_batch
    batch_coefs["conf_high"] = batch_coefs["Coefficient"] + z_critical * standard_errors_batch

    # Append batch results
    results.append(batch_coefs)

    # Save each batch progressively
    batch_coefs.to_csv(f"{folder_path}batch_{i // batch_size + 1}_coefficients_with_conf.csv", index=False)
    print(f"Batch {i // batch_size + 1} saved successfully!")

# Combine all batches into a single file
final_df = pd.concat(results, ignore_index=True)
final_df.to_csv(f"{folder_path}all_batches_coefficients_with_conf-post-covid.csv", index=False)

print("All batches processed and saved!")
