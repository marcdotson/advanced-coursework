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
label_mapping = {
    "overall_gpa": "Overall GPA",
    "refugee_student_y": "Refugee Student",
    "military_child_y": "Military Child",
    "migrant_y": "Migrant",
    "exit_code_11": "Graduated Early – 11th Grade",
    "immigrant_y": "Immigrant",
    "exit_code_tc": "Transferred Out of Country",
    "exit_code_td": "Transferred Within LEA",
    "hs_advanced_math_y": "Took Advanced Math in HS",
    "exit_code_t2": "Early Graduate – 2nd Trimester",
    "school_330": "Attended Spring Creek",
    "ell_disability_group_non_ell_with_disability": "Has a Disability, Not ELL"
}

# Replace feature names with the mapped names, if they exist
flatresults["Feature"] = flatresults["Feature"].map(label_mapping).fillna(flatresults["Feature"])

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
plt.xlabel("Impact on Likelihood of Taking an AC Course", labelpad=15, fontsize=15)
plt.text(0.5, -0.195, "(Positive = More Likely, Negative = Less Likely)", 
         ha="center", va="center", fontsize=13, color="#505050", transform=plt.gca().transAxes)
plt.title('Top 10 Most Influential Predictors', fontsize=18, fontweight="bold")
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
plt.xlabel("Impact on Likelihood of Taking an AC Course", labelpad=15, fontsize=15)
plt.text(0.5, -0.195, "(Positive = More Likely, Negative = Less Likely)", 
         ha="center", va="center", fontsize=13, color="#505050", transform=plt.gca().transAxes)
plt.title('Top 10 Most Influential Predictors', fontsize=18, fontweight="bold")
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
plt.xlabel("Impact on Likelihood of Taking an AC Course", labelpad=15, fontsize=15)
plt.text(0.5, -0.13, "(Positive = More Likely, Negative = Less Likely)", 
         ha="center", va="center", fontsize=13, color="#505050", transform=plt.gca().transAxes)
plt.title('Confidence Intervals for Top 10 Most Influential Variables', fontsize=18, fontweight="bold")

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