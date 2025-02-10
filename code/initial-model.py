import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

# =================================================
# Function: Remove Highly Correlated Features
# =================================================
# Identifies and drops features with a correlation above the given threshold
def remove_highly_correlated_features(df, threshold=0.95):
    # Compute correlation matrix
    corr_matrix = df.corr().abs()  # Compute absolute correlation matrix
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
    return df.drop(columns=to_drop), to_drop

# =================================================
# Step 1: Load and Prepare the Data
# =================================================
# Load dataset and handle missing/invalid values
df = pd.read_csv('data/modeling_data.csv', low_memory=False)
df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

# Display original column names for reference
print("Original Columns in Dataset:\n", df.columns.tolist())

# Define target variable (y) and feature set (X)
y = df['ac_ind']  # Target variable: academic indicator

# # List of required columns for modeling
# required_columns = [
#     'overall_gpa', 'days_attended', 'ethnicity_y', 'amerindian_alaskan_y', 'asian_y', 
#     'black_african_amer_y', 'hawaiian_pacific_isl_y', 'white_y', 'migrant_y', 'gifted_y', 
#     'services_504_y', 'military_child_y', 'refugee_student_y', 'immigrant_y', 
#     'reading_intervention_y', 'passed_civics_exam_y', 'gender_f', 'gender_m', 'gender_u'
# ]

# Select only the required columns for the feature set
X = df.drop(columns=['ac_ind'])
print("\nSelected Features for Initial Model:\n", X.columns.tolist())

# =================================================
# Step 2: Remove Highly Correlated Features
# =================================================
# Drop features with a high correlation threshold (default: 0.95)
# X, dropped_columns = remove_highly_correlated_features(X)S
# print("\nDropped Model Columns Due to High Correlation:\n", dropped_columns)

# =================================================
# Step 3: Standardize Features
# =================================================
# Standardize the feature values to ensure they are on the same scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# =================================================
# Step 4: Train-Test Split
# =================================================
# Split the dataset into training (80%) and testing (20%) sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# =================================================
# Step 5: Train Logistic Regression Model
# =================================================
# Initialize and train a logistic regression model with default regularization
model = LogisticRegression(max_iter=1000, solver='lbfgs')
model.fit(X_train, y_train)

# =================================================
# Step 6: Model Performance Evaluation
# =================================================
# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate and print key performance metrics
print("\nModel Performance Metrics:")
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])

print(f"- Accuracy: {accuracy:.4f}")
print(f"- Precision: {precision:.4f}")
print(f"- Recall: {recall:.4f}")
print(f"- F1-score: {f1:.4f}")
print(f"- ROC-AUC: {roc_auc:.4f}")

# =================================================
# Step 7: Feature Importance Interpretation
# =================================================
# Extract feature coefficients from the logistic regression model
coefficients = model.coef_[0]

# Create a DataFrame to store feature names and their corresponding coefficients
df_coefficients = pd.DataFrame({'feature': X.columns, 'coefficient': coefficients})

# Scale coefficients for readability and sort them by absolute importance
df_coefficients['coefficient'] *= 1e17  # Optional scaling for interpretability
df_coefficients = df_coefficients.sort_values(by='coefficient', ascending=False)

# Display the top 10 most important features
print("\nTop 10 Most Important Features:\n")
df_top10 = df_coefficients.reset_index(drop=True).assign(rank=lambda x: x.index + 1)[['rank', 'feature', 'coefficient']]
df_top10['coefficient'] = df_top10['coefficient'].apply(lambda x: f"{x:.2e}")
print(df_top10[0:10])



df_top10.to_csv("data/log_reg_initial_results_all_columns.csv", index=False)
