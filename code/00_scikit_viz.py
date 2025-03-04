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
#                           LOAD IN THE DATA 
#########################################################################
# Define the folder path where the trace plots will be saved
folder_path = "figures/model-plots"

# Check if the folder exists, and create it if not
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Load data from CSV file
data_path = os.path.join(os.path.dirname(__file__), "..", "output", "all_batches_coefficients_with_conf.csv")
flatresults = pd.read_csv(data_path, low_memory=False)

##########################################################################
#                   SEPERATE THE DATA INTO THE FOUR GROUPS
##########################################################################
academic_group = [
    'overall_gpa', 'days_attended', 'days_absent', 'school_membership',
                   'scram_membership', 'percent_days_attended', 
                   'environment_r', 'environment_h', 'extended_school_year_y']

# Define your initial list of demographic groups
demographic_group = [
    "ethnicity_y", "amerindian_alaskan_y", "asian_y", "black_african_amer_y",
    "hawaiian_pacific_isl_y", "white_y", "migrant_y", "military_child_y", "refugee_student_y",
    "gifted_y", "services_504_y", "immigrant_y", "passed_civics_exam_y", "reading_intervention_y",
    'gender_m', 'gender_u', 'homeless_y', 'hs_advanced_math_y', 'part_time_home_school_y', 
    'ell_disability_group_ell_without_disability', 'ell_disability_group_ell_with_disability', 
    'ell_disability_group_non_ell_with_disability', 'tribal_affiliation_u', 'tribal_affiliation_n', 
    'tribal_affiliation_g', 'tribal_affiliation_p', 'tribal_affiliation_s', 'tribal_affiliation_o',
    'exit_code_de', 'exit_code_t2', 'exit_code_tp', 'exit_code_ae', 'exit_code_he', 'exit_code_t1', 
    'exit_code_th', 'exit_code_tr', 'exit_code_og', 'exit_code_ge', 'exit_code_ex', 'exit_code_un', 
    'exit_code_do', 'exit_code_tn', 'exit_code_to', 'exit_code_wd', 'exit_code_wm', 'exit_code_fe', 
    'exit_code_ts', 'exit_code_td', 'exit_code_tc', 'exit_code_11'
]

# All the teachers
teacher_group = [feature for feature in flatresults['Feature'] if feature.startswith('teacher')]

#all the schools
school_group = [feature for feature in flatresults['Feature'] if feature.startswith('school')]


###########################################################################
#                   MAP THE DATA TO VISUALIZE WITH LABELS
###########################################################################


# Define label mappings for feature names
label_mapping = {
    "overall_gpa": "Overall GPA",
    "refugee_student_y": "Refugee Student",
    "military_child_y": "Military Child",
    "migrant_y": "Migrant",
    "immigrant_y": "Immigrant",
    "hs_advanced_math_y": "Took Advanced Math in HS",
    "ell_disability_group_non_ell_with_disability": "Has a Disability, Not ELL",
    'exit_code_11': 'Early Graduate – Eleventh grade',
    'exit_code_ae': 'Transferred to adult education',
    'exit_code_de': 'Exit_code_Died',
    'exit_code_do': 'Dropped out',
    'exit_code_fe': 'Foreign exchange',
    'exit_code_ge': 'Exited to take GED',
    'exit_code_og': 'Other Graduate (i.e. graduate early, military, certificate of graduation, etc.)',
    'exit_code_t1': 'Early Graduate – First trimester',
    'exit_code_t2': 'Early Graduate – Second trimester',
    'exit_code_tc': 'Transfer out of country',
    'exit_code_td': 'Transfer within LEA',
    'exit_code_th': 'Transfer to homeschool',
    'exit_code_tn': 'Transfer under NCLB',
    'exit_code_to': 'Transfer out of state (to another state)',
    'exit_code_tp': 'Transfer to private school',
    'exit_code_tr': 'Transfer to charter',
    'exit_code_ts': 'Transfer to another school (in state, different LEA)',
    'exit_code_un': 'Unknown but did dropout',
    'exit_code_wd': 'Withdrew',
    'exit_code_wm': 'Withdraw for medical',
    'exit_code_wp': 'Withdraw from Preschool',
    'services_504_y' : 'Disability Accomodations'

}

# Define the new school name to school number mapping
# Updated school mapping with 'school_' prefix on the keys
school_mapping = {
    "school_710": "Cache High",
    "school_706": "Sky View",
    "school_705": "Ridgeline",
    "school_703": "Green Canyon",
    "school_702": "Mountain Crest",
    "school_410": "South Cache Middle",
    "school_406": "North Cache Middle",
    "school_330": "Spring Creek Middle",
    "school_170": "Wellesville Elem.",
    "school_166": "Sunrise Elem.",
    "school_164": "Summit Elem.",
    "school_160": "River Heights Elem.",
    "school_156": "Providence Elem.",
    "school_152": "White Pine Elem.",
    "school_144": "North Park Elem.",
    "school_140": "Nibley Elem.",
    "school_132": "Millville Elem.",
    "school_130": "Mountainside Elem.",
    "school_128": "Lincoln Elem.",
    "school_124": "Lewiston Elem.",
    "school_120": "Heritage Elem.",
    "school_118": "Greenville Elem.",
    "school_111": "Cedar Ridge Elem.",
    "school_109": "Canyon Elem.",
    "school_106": "Birch Creek Elem."
}



########################################################################
#               DEFINE A FUNCTION THAT PLOTS TOP 10 CI FOR EACH GROUP
#########################################################################

# Define the function that applies the label mapping only when plotting
def plot_confidence_intervals(data, title, filename, label_mapping, xlabel="Impact on Likelihood of Taking an AC Course"):
    sns.set_style("whitegrid")  
    plt.figure(figsize=(12, 7))

    primary_color = "#1f77b4"  
    secondary_color = "#aec7e8"  

    # Apply label mapping for the 'Feature' column for display purposes only
    data['Feature'] = data['Feature'].map(label_mapping).fillna(data['Feature'])  # Apply label mapping
    
    plt.errorbar(
        data['Coefficient'], data['Feature'],
        xerr=[data['Coefficient'] - data['conf_low'], 
              data['conf_high'] - data['Coefficient']],
        fmt='o', capsize=6, markersize=8, 
        color=primary_color, ecolor=secondary_color, label="Estimates"
    )
    plt.gca().invert_yaxis()
    plt.axvline(0, color="red", linestyle="--", linewidth=2, label="Zero Line")
    plt.xlabel(xlabel= xlabel, fontsize=16, fontweight="bold", color="#333333")
    plt.ylabel("Feature", fontsize=16, fontweight="bold", color="#333333")
    plt.title(title, fontsize=18, fontweight="bold", color="#333333")
    plt.yticks(fontsize=14)
    plt.subplots_adjust(left=0.3, right=0.95, top=0.9, bottom=0.1)
    plt.legend(fontsize=13, loc="best", frameon=True, facecolor="white", edgecolor="gray")

    plt.savefig(os.path.join(folder_path, filename), dpi=300, bbox_inches="tight")
    print(f"Confidence interval plot saved successfully: {filename}")

########################################################################################
# Apply the plot function for different groups (academic, demographic, etc.)
########################################################################################

# Academic Group
academic_df = flatresults[flatresults['Feature'].str.contains('|'.join(academic_group))]
# Sort by coefficient to pick top predictors
academic_df = academic_df.sort_values(by='Coefficient', ascending=False)[:10]
plot_confidence_intervals(academic_df, 'Top Predictors Across Academic Variables', 'academic-ci-plots-all-years.png', label_mapping)

# Demographic Group
demographic_df = flatresults[flatresults['Feature'].str.contains('|'.join(demographic_group))]
# Sort by coefficient to pick top predictors
demographic_df = demographic_df.sort_values(by='Coefficient', ascending=False)[:10]
plot_confidence_intervals(demographic_df, 'Top Predictors Across Demographic Variables', 'demographic-ci-plots-all-years.png', label_mapping)


# All the teacher-related features
teacher_df = flatresults[flatresults['Feature'].str.contains('|'.join(teacher_group))]
# Sort by coefficient to pick top predictors
teacher_df = teacher_df.sort_values(by='Coefficient', ascending=False)[:10]
plot_confidence_intervals(teacher_df, 'Top Predictors Across Teacher Variables', 'teacher-ci-plots-all-years.png', label_mapping)

# All the school-related features
school_df = flatresults[flatresults['Feature'].str.contains('|'.join(school_group))]
# Sort by coefficient to pick top predictors
school_df = school_df.sort_values(by='Coefficient', ascending=False)[:10]
plot_confidence_intervals(school_df, 'Top Predictors Across School Variables', 'school-ci-plots-all-years.png',school_mapping)


# Combine both school_mapping and label_mapping dictionaries
combined_mapping = {**school_mapping, **label_mapping}
# Sort all results by 'Coefficient'
all_results = flatresults.sort_values(by='Coefficient', ascending=False)
# Call the plot function with the combined mapping
plot_confidence_intervals(all_results, 'Top Predictors Across School Variables', 'all-groups-ci-plots-all-years.png', combined_mapping)

# academic_df = flatresults[flatresults['Feature'].str.contains('|'.join(academic_group))]
# # Sort by coefficient to pick top predictors
# academic_df = academic_df.sort_values(by='Coefficient', ascending=True).head(10)
# plot_confidence_intervals(academic_df ,'Top Predictors Across Academic Variables' , 'academic-ci-plots-all-years.png')

# academic_df = flatresults[flatresults['Feature'].str.contains('|'.join(academic_group))]
# # Sort by coefficient to pick top predictors
# academic_df = academic_df.sort_values(by='Coefficient', ascending=True).head(10)
# plot_confidence_intervals(academic_df ,'Top Predictors Across Academic Variables' , 'academic-ci-plots-all-years.png')
# def plot_group_predictors_with_ci(coefficients_df, group_columns, title, file_name, xlabel="Impact on Likelihood of Taking an AC Course"):
#     """
#     Plots the top predictors with their coefficients and confidence intervals filtered by the group columns.
    
#     Parameters:
#     - coefficients_df: DataFrame with columns ['Feature', 'Coefficient', 'Coef_Lower', 'Coef_Upper']
#     - group_columns: List of column names or patterns to filter the predictors (list of strings)
#     - title: Title for the plot (string)
#     - file_name: Name of the file to save the plot (string)
#     - xlabel: Label for the x-axis (string, default="Impact on Likelihood of Taking an AC Course")
#     """
#     # Filter coefficients_df based on the group_columns (those that match the column names or patterns)
#     filtered_df = coefficients_df[coefficients_df['Feature'].str.contains('|'.join(group_columns))]

#     # Sort by coefficient to pick top predictors
#     filtered_df_sorted = filtered_df.sort_values(by='Coefficient', ascending=False).head(10)

#     # Create a figure and axis
#     plt.figure(figsize=(12, 8))
    
#     # Create a dark-to-light color palette for the filtered predictors
#     palette_top = sns.dark_palette("royalblue", as_cmap=False, n_colors=len(filtered_df_sorted))
    
#     # Plot the coefficients as horizontal bars
#     plt.barh(filtered_df_sorted["Feature"], filtered_df_sorted["Coefficient"], color=palette_top)
    
#     # Plot the confidence intervals as horizontal lines (whiskers)
#     for index, row in filtered_df_sorted.iterrows():
#         plt.plot([row["conf_low"], row["conf_high"]], [index, index], color='black', lw=2)
    
#     # Add the labels and title
#     plt.xlabel(xlabel, labelpad=15, fontsize=15)
#     plt.text(0.5, -0.195, "(Positive = More Likely, Negative = Less Likely)", 
#              ha="center", va="center", fontsize=13, color="#505050", transform=plt.gca().transAxes)
#     plt.title(title, fontsize=18, fontweight="bold")
    
#     # Invert y-axis to have the largest coefficient at the top
#     plt.gca().invert_yaxis()
    
#     # Light gridlines
#     plt.grid(axis='x', linestyle='--', alpha=0.5)
    
#     # Make the layout tight
#     plt.tight_layout()
    
#     # Save the plot to a file
#     plt.savefig(file_name, format="png")
#     plt.close()

#     print(f"Bar plot saved successfully as {file_name}!")


# plot_group_predictors_with_ci(flatresults, academic_group, ', )


# # #########################################################################
# # #              CONFIDENCE INTERVAL PLOT FOR ALL PREDICTORS
# # #########################################################################

# # # Rank predictors by absolute coefficient value (most influential)
# # flatresults["abs_coefficient"] = flatresults["Coefficient"].abs()  # Use absolute coefficient for ranking
# # top_10_predictors = flatresults.nlargest(10, "abs_coefficient")

# # # Plot only the top 10 influential predictors
# # plt.figure(figsize=(10, 6))
# # # Create a dark-to-light color palette
# # palette_top_10 = sns.dark_palette("royalblue", as_cmap=False, n_colors=len(top_10_predictors))
# # plt.barh(top_10_predictors["Feature"], top_10_predictors["Coefficient"], color=palette_top_10)
# # plt.xlabel("Impact on Likelihood of Taking an AC Course", labelpad=15, fontsize=15)
# # plt.text(0.5, -0.195, "(Positive = More Likely, Negative = Less Likely)", 
# #          ha="center", va="center", fontsize=13, color="#505050", transform=plt.gca().transAxes)
# # plt.title('Top 10 Most Influential Predictors', fontsize=18, fontweight="bold")
# plt.gca().invert_yaxis()  # Invert y-axis to have the largest coefficient at the top
# plt.grid(axis='x', linestyle='--', alpha=0.5)  # Light gridlines
# plt.tight_layout()
# plt.show()  # Show the plot
# plt.savefig(f"{folder_path}/flat-model-top-10-predictors.png", format="png")
# plt.close()
# print("Bar plot for top 10 predictors saved successfully!")


# #########################################################################
# #                CONFIDENCE INTERVAL PLOT FOR TOP 10 OVERALL
# #########################################################################
# # Calculate standard error dynamically (approximated as half of the coefficient magnitude)
# flatresults["std_error"] = abs(flatresults["Coefficient"]) / 2

# # Calculate 95% confidence intervals
# z_value = 1.96  # For 95% confidence level
# flatresults["CI_lower"] = flatresults["Coefficient"] - (z_value * flatresults["std_error"])
# flatresults["CI_upper"] = flatresults["Coefficient"] + (z_value * flatresults["std_error"])

# #########################################################################
# #                         CREATE CONFIDENCE INTERVAL PLOT
# #########################################################################

# # Get top 10 teacher/school variables by absolute coefficient
# top_10_variables = flatresults.nlargest(10, 'abs_coefficient')

# # Sort the top 10 variables by median (highest to lowest)
# top_10_variables = top_10_variables.sort_values(by="Coefficient", ascending=True)

# # Create the plot with specific dimensions to match the reference
# plt.figure(figsize=(10, 8))

# # Plot the confidence intervals with specific styling
# plt.errorbar(
#     top_10_variables['Coefficient'],
#     range(len(top_10_variables)),
#     xerr=[
#         top_10_variables['Coefficient'] - top_10_variables['CI_lower'],
#         top_10_variables['CI_upper'] - top_10_variables['Coefficient']
#     ],
#     fmt='o',  # Circle markers
#     color='royalblue',  # Blue color to match
#     capsize=5,  # Add caps to error bars
#     label='Estimates',
#     markersize=6  # Adjust marker size
# )

# # Add the zero reference line with specific styling
# plt.axvline(x=0, color='red', linestyle='--', label='Zero Line')

# # Customize the plot
# plt.yticks(range(len(top_10_variables)), top_10_variables['Feature'])
# plt.xlabel("Impact on Likelihood of Taking an AC Course", labelpad=15, fontsize=15)
# plt.text(0.5, -0.13, "(Positive = More Likely, Negative = Less Likely)", 
#          ha="center", va="center", fontsize=13, color="#505050", transform=plt.gca().transAxes)
# plt.title('Confidence Intervals for Top 10 Most Influential Variables', fontsize=18, fontweight="bold")

# # Add legend with specific placement
# plt.legend(loc='upper left')

# # Set x-axis limits to match reference
# plt.xlim(-2.5, 4.5)

# # Add grid for x-axis only
# plt.grid(axis='x', linestyle='-', alpha=0.2)

# # Adjust layout
# plt.tight_layout()

# # Save and show the plot
# plt.savefig(f"{folder_path}/teacher-confidence-intervals.png", format="png", dpi=300)
# plt.show()
# plt.close()

# print("Confidence interval plot saved successfully!")










