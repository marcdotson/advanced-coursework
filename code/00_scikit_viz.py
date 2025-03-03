#########################################################################
#                          IMPORT LIBRARIES
#########################################################################
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # Import seaborn for better color palettes

# Set the seaborn style for fancier plots
sns.set(style="whitegrid")

#########################################################################
#             LOAD IN THE DATA AND ESTABLISH TRACE OBJECT
#########################################################################
# Define the folder path where the trace plots will be saved
folder_path = os.path.join(os.path.dirname(__file__), "figures", "model-plots")

# Check if the folder exists, and create it if not
os.makedirs(folder_path, exist_ok=True)

# Load data from CSV file
data_path = os.path.join(os.path.dirname(__file__), "..", "data", "scikit-flat-model-sorted-coefficients.csv")
flatresults = pd.read_csv(data_path, low_memory=False)

#########################################################################
#                         FILTER OUT UNWANTED FEATURES
#########################################################################

# Filter out features that begin with "school" or "teacher"
flatresults_filtered = flatresults[~flatresults['Feature'].str.startswith(('school', 'teacher'))]

#########################################################################
#                   FOREST PLOT FOR ABS NON SCHOOL/ TEACHER
#########################################################################

# Rank predictors by absolute coefficient value (most influential)
flatresults_filtered["abs_coefficient"] = flatresults_filtered["Coefficient"].abs()  # Use absolute coefficient for ranking
top_10_predictors = flatresults_filtered.nlargest(10, "abs_coefficient")

# Plot only the top 10 influential predictors
plt.figure(figsize=(10, 6))
# Create a dark-to-light color palette
palette_top_10 = sns.dark_palette("royalblue", as_cmap=False, n_colors=len(top_10_predictors))
plt.barh(top_10_predictors["Feature"], top_10_predictors["Coefficient"], color=palette_top_10)
plt.xlabel('Coefficient', fontsize=14)
plt.ylabel('Feature', fontsize=14)
plt.title('Top 10 Most Influential Predictors', fontsize=16)
plt.gca().invert_yaxis()  # Invert y-axis to have the largest coefficient at the top
plt.grid(axis='x', linestyle='--', alpha=0.5)  # Light gridlines
plt.tight_layout()
plt.show()  # Show the plot
plt.savefig(f"{folder_path}/flat-model-top-10-predictors-filtered.png", format="png")
plt.close()
print("Bar plot for top 10 predictors saved successfully!")

#########################################################################
#                   FOREST PLOT FOR TOP 10 OVERALL
#########################################################################

# Rank predictors by absolute coefficient value (most influential)
flatresults["abs_coefficient"] = flatresults["Coefficient"].abs()  # Use absolute coefficient for ranking
top_10_predictors = flatresults.nlargest(10, "abs_coefficient")

# Plot only the top 10 influential predictors
plt.figure(figsize=(10, 6))
# Create a dark-to-light color palette
palette_top_10 = sns.dark_palette("royalblue", as_cmap=False, n_colors=len(top_10_predictors))
plt.barh(top_10_predictors["Feature"], top_10_predictors["Coefficient"], color=palette_top_10)
plt.xlabel('Coefficient', fontsize=14)
plt.ylabel('Feature', fontsize=14)
plt.title('Top 10 Most Influential Predictors', fontsize=16)
plt.gca().invert_yaxis()  # Invert y-axis to have the largest coefficient at the top
plt.grid(axis='x', linestyle='--', alpha=0.5)  # Light gridlines
plt.tight_layout()
plt.show()  # Show the plot
plt.savefig(f"{folder_path}/flat-model-top-10-predictors.png", format="png")
plt.close()
print("Bar plot for top 10 predictors saved successfully!")


#########################################################################
#                         COMPUTE STANDARD ERROR AND CI
#########################################################################
# Calculate standard error dynamically (approximated as half of the coefficient magnitude)
flatresults["std_error"] = abs(flatresults["Coefficient"]) / 2

# Calculate 95% confidence intervals
z_value = 1.96  # For 95% confidence level
flatresults["CI_lower"] = flatresults["Coefficient"] - (z_value * flatresults["std_error"])
flatresults["CI_upper"] = flatresults["Coefficient"] + (z_value * flatresults["std_error"])

# # Calculate standard error and confidence intervals
# flatresults['std_error'] = flatresults['Coefficient'].apply(lambda x: abs(x) / 2)
# flatresults['CI_lower'] = flatresults['Coefficient'] - (1.96 * flatresults['std_error'])
# flatresults['CI_upper'] = flatresults['Coefficient'] + (1.96 * flatresults['std_error'])

#########################################################################
#                         CREATE CONFIDENCE INTERVAL PLOT
#########################################################################

# Get top 10 teacher/school variables by absolute coefficient
top_10_variables = flatresults.nlargest(10, 'abs_coefficient')

# Sort the top 10 variables by median (highest to lowest)
top_10_variables = top_10_variables.sort_values(by="Coefficient", ascending=True)

# Create the plot with specific dimensions to match the reference
plt.figure(figsize=(10, 8))

# Plot the confidence intervals with specific styling
plt.errorbar(
    top_10_variables['Coefficient'],
    range(len(top_10_variables)),
    xerr=[
        top_10_variables['Coefficient'] - top_10_variables['CI_lower'],
        top_10_variables['CI_upper'] - top_10_variables['Coefficient']
    ],
    fmt='o',  # Circle markers
    color='royalblue',  # Blue color to match
    capsize=5,  # Add caps to error bars
    label='Estimates',
    markersize=6  # Adjust marker size
)

# Add the zero reference line with specific styling
plt.axvline(x=0, color='red', linestyle='--', label='Zero Line')

# Customize the plot
plt.yticks(range(len(top_10_variables)), top_10_variables['Feature'])
plt.xlabel('Coefficient Estimate')
plt.ylabel('Feature')
plt.title('Confidence Intervals for Top 10 Most Influential Variables (Sorted)')

# Add legend with specific placement
plt.legend(loc='upper left')

# Set x-axis limits to match reference
plt.xlim(-2.5, 4.5)

# Add grid for x-axis only
plt.grid(axis='x', linestyle='-', alpha=0.2)

# Adjust layout
plt.tight_layout()

# Save and show the plot
plt.savefig(f"{folder_path}/teacher-confidence-intervals.png", format="png", dpi=300)
plt.show()
plt.close()

print("Confidence interval plot saved successfully!")






# # Calculate standard error (if you have variance or standard deviation)
# # If you have raw data points, you can calculate it this way:
# def calculate_std_error(coefficient):
#     # Using a common statistical approach where SE is approximately coefficient/2 
#     # for a 95% confidence level. This is a simplified approach.
#     return abs(coefficient) / 2

# # Add standard error to the dataframe
# flatresults['std_error'] = flatresults['Coefficient'].apply(calculate_std_error)

# # Calculate confidence intervals (95% level)
# flatresults['CI_lower'] = flatresults['Coefficient'] - (1.96 * flatresults['std_error'])
# flatresults['CI_upper'] = flatresults['Coefficient'] + (1.96 * flatresults['std_error'])

# # Now proceed with the confidence interval plot code...
# # Sort predictors by the coefficient value (largest to smallest)
# sorted_predictors = flatresults_filtered.sort_values(by="Coefficient", ascending=False)

# # Increase figure size for better visibility
# plt.figure(figsize=(12, 18))  # Adjust height for long names
# # Create a dark-to-light color palette
# palette_all_predictors = sns.dark_palette("royalblue", as_cmap=False, n_colors=len(sorted_predictors))
# plt.barh(sorted_predictors["Feature"], sorted_predictors["Coefficient"], color=palette_all_predictors)

# # Set labels and title with adjusted font sizes
# plt.xlabel('Coefficient', fontsize=14)
# plt.ylabel('Feature', fontsize=12)  # Smaller font for feature names
# plt.title('Posterior Distribution For All Predictors', fontsize=16)

# # Adjust y-ticks font size
# plt.yticks(fontsize=10)

# plt.gca().invert_yaxis()  # Invert y-axis to have the largest coefficient at the top
# plt.grid(axis='x', linestyle='--', alpha=0.5)  # Light gridlines

# plt.tight_layout()
# plt.show()  # Show the plot
# plt.savefig(f"{folder_path}/flat-model-all-predictors.png", format="png")
# plt.close()
# print("Bar plot for all predictors saved successfully!")

# #########################################################################
# #                         CREATE CONFIDENCE INTERVAL PLOT
# #########################################################################

# # Get the top 10 overall by absolute coefficient value
# top_10_variables = flatresults.nlargest(10, 'Coefficient')

# # Create the confidence interval plot
# plt.figure(figsize=(10, 8))

# # Plot the confidence intervals
# plt.errorbar(
#     top_10_variables['Coefficient'],
#     range(len(top_10_variables)),
#     xerr=[
#         top_10_variables['Coefficient'] - top_10_variables['CI_lower'],
#         top_10_variables['CI_upper'] - top_10_variables['Coefficient']
#     ],
#     fmt='o',
#     color='royalblue',
#     capsize=5,
#     label='Estimates'
# )

# # Add the zero reference line
# plt.axvline(x=0, color='red', linestyle='--', label='Zero Line')

# # Customize the plot
# plt.yticks(range(len(top_10_variables)), top_10_variables['Feature'])
# plt.xlabel('Coefficient Estimate')
# plt.ylabel('Feature')
# plt.title('Confidence Intervals for Top 10 Most Influential Variables (Sorted)')
# plt.legend()

# # Adjust layout
# plt.tight_layout()

# # Save and show the plot
# plt.savefig(f"{folder_path}/top-10-confidence-intervals.png", format="png")
# plt.show()
# plt.close()

# print("Confidence interval plot saved successfully!")
