# Core libraries
import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_auc_score, roc_curve



#----------------------------------------------------------------------------------------------------------
                                   #Generate Random data to test the models
#----------------------------------------------------------------------------------------------------------

# Set random seed for reproducibility
np.random.seed(42)

# Generate random data
n_samples = 200
X1 = np.random.normal(loc=0, scale=1, size=n_samples)  # Feature 1
X2 = np.random.normal(loc=2, scale=1.5, size=n_samples)  # Feature 2

# Create a simple rule for the target variable
Y = (X1 + X2 + np.random.normal(scale=0.5, size=n_samples) > 2).astype(int)

# Create a DataFrame
df = pd.DataFrame({'X1': X1, 'X2': X2, 'Y': Y})

print(df.head())



#----------------------------------------------------------------------------------------------------------
                                   #Logistic Regression using Scikit-learn
#----------------------------------------------------------------------------------------------------------


# Split the data into train and test sets
X = df[['X1', 'X2']]
y = df['Y']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Logistic Regression Model with Scikit-learn
log_reg = LogisticRegression()
log_reg.fit(X_train, y_train)

# Make predictions
y_pred = log_reg.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")
print(classification_report(y_test, y_pred))

# Plotting the decision boundary
plt.figure(figsize=(8, 6))
plt.scatter(X_test['X1'], X_test['X2'], c=y_test, cmap='coolwarm', s=50, edgecolor='k', alpha=0.7)
plt.title('Logistic Regression Decision Boundary')
plt.xlabel('X1')
plt.ylabel('X2')

# Plot the decision boundary
xx, yy = np.meshgrid(np.linspace(X_test['X1'].min(), X_test['X1'].max(), 100),
                     np.linspace(X_test['X2'].min(), X_test['X2'].max(), 100))
Z = log_reg.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
plt.contourf(xx, yy, Z, alpha=0.2, cmap='coolwarm')

plt.show()





#----------------------------------------------------------------------------------------------------------
                                        #Logistic Regression using PyMc
#----------------------------------------------------------------------------------------------------------


# Your data generation code here (or loading from a file)
np.random.seed(42)
X1 = np.random.normal(0, 1, 100)
X2 = np.random.normal(0, 1, 100)
y = (1 / (1 + np.exp(-(1 + 2 * X1 - 3 * X2)))) > 0.5
y = y.astype(int)

data = pd.DataFrame({'X1': X1, 'X2': X2, 'y': y})

def run_logistic_regression():
    # Define the model
    with pm.Model() as logistic_model:
        intercept = pm.Normal('intercept', mu=0, sigma=10)
        coef_X1 = pm.Normal('coef_X1', mu=0, sigma=10)
        coef_X2 = pm.Normal('coef_X2', mu=0, sigma=10)

        linear_model = intercept + coef_X1 * data['X1'] + coef_X2 * data['X2']

        p = pm.math.sigmoid(linear_model)
        likelihood = pm.Bernoulli('likelihood', p=p, observed=data['y'])

        trace = pm.sample(2000, return_inferencedata=True)

    # Traceplot and summary
    az.plot_trace(trace)
    print(az.summary(trace))

if __name__ == '__main__':
    run_logistic_regression()


