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
    idata = az.from_netcdf("output\multilevel-model-output_05.nc")

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

#function to sort the data and remove the "other groups labeled with a 0"
def process_idata_groups(idata, var_list, group_dims=None):
    # Filter only relevant variables that match our list
    relevant_vars = [var for var in idata.data_vars if any(f"{v}" in f"{var}" for v in var_list)]
    
    if not relevant_vars:
        print("No matching variables found.")
        return None
    
 # Drop any data related to 'high_school[0]' for each dimension in group_dims
    for dimension in group_dims:
        try:
            idata = idata.drop_sel({dimension: '0'})
        except:
            print(f"{dimension} not present in the dataset, moving on.")

    # Compute medians across chains and draws
    medians = {
        var: idata[var].median(dim=("chain", "draw"), skipna=True)
        for var in relevant_vars}
    
    # Detect all extra grouping dimensions automatically
    all_group_dims = set()
    for var in relevant_vars:
        all_group_dims.update(set(medians[var].dims) - {"chain", "draw"})
    
    # Keep only the specified group dimensions (if provided), otherwise use all detected
    group_dims = group_dims or list(all_group_dims)

    # Compute overall median per variable, considering multiple grouping dimensions
    overall_medians = {}
    for var in relevant_vars:
        median_value = medians[var]

        # If there are grouping dimensions, compute the mean across them
        if group_dims and any(dim in median_value.dims for dim in group_dims):
            median_value = median_value.mean(dim=[dim for dim in group_dims if dim in median_value.dims], skipna=True)

        # Convert to a scalar safely
        overall_medians[var] = median_value.item() if median_value.size == 1 else float(median_value.mean().values)

    # Sort variables by median effect size (descending)
    sorted_vars = sorted(overall_medians, key=overall_medians.get, reverse=True)

    # Return the sorted subset of idata
    return idata[sorted_vars]

#funtion to get only the signficant vars if needed
def get_significant_vars_only(idata):

    hdi_dataset = az.hdi(idata, hdi_prob=0.95)  # Ensure you're using the correct HDI probability

    significant_vars = []

    # Loop through all data variables in the dataset
    for var_name in hdi_dataset.data_vars:
        var_data = hdi_dataset[var_name]

        # Determine the grouping structure from dimensions
        factor_dim = None
        for dim in var_data.dims:
            if "factor_dim" in dim:  # Identify the factor level for grouping variables
                factor_dim = dim
                break

        if factor_dim:
            # Loop over factor levels
            for i, level in enumerate(var_data[factor_dim].values):
                lower, upper = var_data[i].sel(hdi="lower").item(), var_data[i].sel(hdi="higher").item()
                
                # Check significance: exclude intervals containing 0
                if lower > 0 or upper < 0:
                    full_name = f"{var_name}[{level}]"  # Construct full variable name
                    significant_vars.append(var_name)
        else:
            # If no factor grouping, just check the single HDI range
            lower, upper = var_data.sel(hdi="lower").item(), var_data.sel(hdi="higher").item()
            if lower > 0 or upper < 0:
                significant_vars.append(var_name)
    return significant_vars

# Define groups
groups = {
    "Academic Performance": ["composite_score", "english_score", "math_score", "reading_score",
                             "science_score", "writing_score", "overall_gpa", "percent_days_attended",
                             "passed_civics_exam", "hs_advanced_math_y", "extracurricular_ind" "part_time_home_school_y"],

    "Environmental Factors": ["immigrant_y", "migrant_y",
                     "homeless_y", "military_child_y", "refugee_student_y"],

    "Disability & ELL Status": ["ell_with_disability", "ell_without_disability",
                                 "non_ell_with_disability", "services_504_y", "environment_h", 
                                 "environment_r", "scram_membership"],


    "Demograophic": ["tribal_affiliation_g", "tribal_affiliation_n", "tribal_affiliation_o",
                           "tribal_affiliation_p", "tribal_affiliation_s", "tribal_affiliation_u",
                           "amerindian_alaskan_y", "asian_y", "black_african_amer_y", "hawaiian_pacific_isl_y",
                     "white_y", "ethnicity_y", "gender_m", "gender_u"]
}

#create our sorted IDATA for all the vars in all the groups
sorted_all_variables_idata = process_idata_groups(filtered_idata, filtered_idata.data_vars, group_dims = ["high_school__factor_dim", 'middle_school__factor_dim'])

significant_vars = get_significant_vars_only(filtered_idata)
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
interval_plot_base_name = 'interval-plot-multilevel-model05'

# Loop over all the data in `all_idata`
# Loop through and plot each group
for group_name, base_names in groups.items():
    # Select variables that match the base names
    variables = [var for var in sorted_all_variables_idata if any(var.startswith(base) for base in base_names)
                 and var in significant_vars]

    print(f'Starting plot for {group_name}')
    # Generate the forest plot
    az.plot_forest(sorted_all_variables_idata,
        var_names=variables,  # Pass the final filtered list
        filter_vars="like", 
        combined=True, kind="ridgeplot",
        ridgeplot_truncate=True, ridgeplot_overlap=1, ridgeplot_quantiles=[0.5]
    )
    plt.title(group_name.capitalize())
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