# This is Rebecca Hull's test script for PyMC which will be used for logistic regression

# I had to use Anacdona Prompt to install PyMC. I did conda activate pymc_env
# Make sure to use the Python Interpreter of pymc_env that I made

# This code is an example from ChatGPT

# From studying logistic regression, it seems that we need to set up prior distributions

import pymc as pm
import numpy as np
import matplotlib.pyplot as plt

# Simulated data
np.random.seed(42)
n_samples = 100
X = np.random.randn(n_samples)  # Predictor variable
true_intercept = -1.0
true_slope = 2.5
p = 1 / (1 + np.exp(-(true_intercept + true_slope * X)))  # Logistic function
y = np.random.binomial(1, p)  # Binary target variable

# Visualize the data
plt.scatter(X, y, label="Data")
plt.xlabel("X (Predictor)")
plt.ylabel("y (Binary Target)")
plt.legend()
plt.show()

# PyMC model
with pm.Model() as logistic_model:
    # Priors for intercept and slope
    intercept = pm.Normal("Intercept", mu=0, sigma=10)
    slope = pm.Normal("Slope", mu=0, sigma=10)
    
    # Logistic regression equation
    p = pm.math.sigmoid(intercept + slope * X)
    
    # Likelihood
    y_obs = pm.Bernoulli("y_obs", p=p, observed=y)
    
    # Inference
    trace = pm.sample(1000, return_inferencedata=True)

# Visualize posterior distributions
with logistic_model:
    pm.plot_posterior(trace)
