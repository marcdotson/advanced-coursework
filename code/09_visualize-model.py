##############################################################################
                             #IMPORT LIBRARIES
############################################################################## 
import arviz as az
import numpy as np
import matplotlib.pyplot as plt
import os 
import glob
import seaborn as sns


#############################################################################
                        #  PREP FOR MODEL VISUALS
############################################################################## 

# Load trace from the NetCDF file saved from model output and the dataset file
try:
    idata = az.from_netcdf("output\multilevel-model-output_01.nc")

except Exception as e:
    print(f"Loading Data failed: {e}")

# Define the folder path where the trace plots will be saved
folder_path = "figures/model-plots"

#define file extension
extension = 'png'

# Define the group names 
group_names = ["school", "academic", "demographic"]

# Check if the folder exists, and create it if not
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

#Finds the next available file number to avoid overwriting
def get_next_filename(folder_path, base_name, extension, group=None):
  
    # Ensure the extension is in lowercase for consistency
    extension = extension.lower()
    
    # Create the glob pattern for file search
    if group:
        search_pattern = f"{folder_path}/{base_name}-{group}-*.{extension}"
    else:
        search_pattern = f"{folder_path}/{base_name}-*.{extension}"

    # Search for existing files using the pattern
    existing_files = glob.glob(search_pattern)
    
    # Check if files exist and print for debugging
    if not existing_files:
        print("No existing files found. Starting from 1.")
    else:
        print(f"Found existing files: {existing_files}")

    # Extract numbers from filenames, sort them and find the next available number
    existing_numbers = sorted(
        [int(f.split("-")[-1].split(".")[0]) for f in existing_files if f.split("-")[-1].split(".")[0].isdigit()]
    )
    
    if existing_numbers:
        next_number = existing_numbers[-1] + 1
    else:
        next_number = 1

    # Return the next available filename
    if group:
        return f"{folder_path}/{base_name}-{group}-{next_number:02d}.{extension}"
    else:
        return f"{folder_path}/{base_name}-{next_number:02d}.{extension}"


#create a USU color pallete for our visuals
usu_palette = ["#0F2439", "#1D3F6E", "#A7A8AA"]  # Navy, Aggie Blue, and Gray

# Extract posterior summary
summary = az.summary(idata)


##############################################################################
              #CREATE OUR GROUPIING STRUCTURES FOR THE VISUALS
##############################################################################

# Drop `_sigma` variables and Intercept
filtered_idata = idata.posterior.drop_vars([var for var in idata.posterior.data_vars if '_sigma' in var or var == 'Intercept'])

#function to sort and filter our inference data object from the model
def process_idata_groups(idata, var_list, group_dim=None):

    # Filter only the relevant variables
    relevant_vars = [var for var in idata.data_vars if var in var_list]

    # Compute medians across chains and draws
    medians = {
        var: idata[var].median(dim=("chain", "draw"))
        for var in relevant_vars
    }

    # If there's a grouping dimension, compute overall median per variable
    if group_dim:
        overall_medians = {
            var: medians[var].mean(dim=group_dim).item()
            for var in relevant_vars
        }
    else:
        overall_medians = {
            var: medians[var].item()
            for var in relevant_vars
        }

    # Sort variables by median effect size (descending)
    sorted_vars = sorted(overall_medians, key=overall_medians.get, reverse=True)

    # Return the sorted dataset
    return idata[sorted_vars]

#all the schools
school_vars = [var for var in filtered_idata.data_vars if 'school_' in var and 'part_time' not in var]

#list of all academic collumns
academic_vars = ['overall_gpa', 'scram_membership', 'percent_days_attended', 
                'composite_score', 'english_score', 'hs_advanced_math_y', 'math_score', 
                'reading_score', 'science_score', 'writing_score' ]

#list of all demographic vars
demographic_vars = [
    "ethnicity_y", "amerindian_alaskan_y", "asian_y", "black_african_amer_y",
    "hawaiian_pacific_isl_y", "white_y", "migrant_y", "military_child_y",
     "services_504_y", "immigrant_y", "passed_civics_exam_y",
    'gender_m', 'gender_u', 'homeless_y', 'hs_advanced_math_y', 'part_time_home_school_y', 'tribal_affiliation_u', 'tribal_affiliation_n', 
     'tribal_affiliation_p', 'tribal_affiliation_s', 'tribal_affiliation_o']

#create the seperated and filtered inference data objects
sorted_school_idata = process_idata_groups(filtered_idata, school_vars, group_dim="ell_disability_group__factor_dim")
sorted_academic_idata = process_idata_groups(filtered_idata, academic_vars)
sorted_demographic_idata = process_idata_groups(filtered_idata, demographic_vars)

#Store all the filter idata in a list to run in a for loop for our visuals
all_idata = [sorted_school_idata, sorted_academic_idata, sorted_demographic_idata]

# ##############################################################################
#                     # EXTACT OUR MOST INFLUENTIAL FACTORS
# ##############################################################################

# # Filter to exclude random effect standard deviations (_sigma) and the Intercept
# fixed_effects_summary = summary[
#     (~summary.index.str.contains('_sigma')) & (summary.index != "Intercept")
# ]

# # Sort by absolute mean effect size (largest to smallest)
# sorted_fixed_effects = fixed_effects_summary.reindex(
#     fixed_effects_summary["mean"].abs().sort_values(ascending=False).index
# )

# # Select the top 10 most influential fixed effects (excluding Intercept)
# top_10_fixed_effects = sorted_fixed_effects.head(10)

# # Plot
# plt.figure(figsize=(10, 6))
# sns.barplot(
#     x=top_10_fixed_effects["mean"], 
#     y=top_10_fixed_effects.index, 
#     palette = usu_palette
# )
# plt.axvline(x=0, color="black", linestyle="--", alpha=0.7)
# plt.xlabel("Effect Size (Mean)")
# plt.ylabel("Predictor")
# plt.title("Top 10 Most Influential Predictors")

# plt.subplots_adjust(left=0.4)
# plt.savefig(f"{folder_path}/top10-plot.png", format="png")
# plt.close()

# # Sort by absolute mean effect size (largest to smallest)
# sorted_fixed_effects_not_abs = fixed_effects_summary.reindex(
#     fixed_effects_summary["mean"].sort_values(ascending=False).index
# )

# # Select the top 10 most influential fixed effects (excluding Intercept)
# top_10_fixed_effects_non_abs = sorted_fixed_effects_not_abs.head(10)

# # Plot
# plt.figure(figsize=(10, 6))
# sns.barplot(
#     x=top_10_fixed_effects_non_abs["mean"], 
#     y=top_10_fixed_effects_non_abs.index, 
#     palette = usu_palette
# )
# plt.axvline(x=0, color="black", linestyle="--", alpha=0.7)
# plt.xlabel("Effect Size (Mean)")
# plt.ylabel("Predictor")
# plt.title("Top 10 Most Influential Predictors")

# plt.subplots_adjust(left=0.4)
# plt.savefig(f"{folder_path}/top10-plot-non-abs.png", format="png")
# plt.close()

# ###############################################################################
#                          # INTERVAL PLOTS
# ###############################################################################

# *******CHANGE THIS NAME HERE BASED ON HOW YOU WOULD LIKE IT TO SAVE***********
interval_plot_base_name = 'interval-plot-multilevel'

# Loop over all the data in `all_idata`
for idx, (data, group_name) in enumerate(zip(all_idata, group_names)):
    print(f'Starting plot for {group_name} group ({idx + 1})')

    # Generate the forest plot
    az.plot_forest(data, combined=True)

     # Set title and labels
    plt.title(f"Forest Plot for {group_name.capitalize()} Group")
    plt.xlabel("Effect Size")  # Label for the x-axis (you can adjust as needed)
    plt.ylabel("Variables")  # Label for the y-axis (you can adjust as needed)

    plt.axvline(0, color='black', linewidth=1, linestyle='--') 
    plt.tight_layout()

    # Generate the next available filename
    plot_filename = get_next_filename(folder_path, interval_plot_base_name, extension, group = group_name )
    
    # Save the plot
    plt.savefig(plot_filename)
    print(f"Plot saved as: {plot_filename}")
    plt.close()  # Close the current plot to avoid overlapping in the next iteration