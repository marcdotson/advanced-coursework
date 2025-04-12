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
    #Inerence data for all years
    idata_multi = az.from_netcdf("output\multilevel-model-output_08.nc")

    #inference data for multilevel model post covid
    idata_multi_pc = az.from_netcdf("output\multilevel-model-output_07.nc")

    #Inference Data for Flat model all Years
    idata_flat = az.from_netcdf("output/flat-model-output-all-years-secondary-schools.nc")

    #Inference Data for Flat model post covid
    idata_flat_pc = az.from_netcdf("output/flat-model-output-post-covid.nc")

    #store all inference data in a list to iterate through later
    all_idata = [idata_multi, idata_multi_pc, idata_flat, idata_flat_pc]
except Exception as e:
    print(f"Loading Data failed: {e}")


# Define the folder path where the trace plots will be saved
folder_path = "figures/model-plots"

#define file extension
extension = 'png'

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

##############################################################################
              #CREATE OUR GROUPIING STRUCTURES FOR THE VISUALS
##############################################################################

def process_filtered_idata(idata, var_list, group_dims=None):
    # Drop `_sigma` variables and Intercept from the posterior
    filtered = idata.posterior.drop_vars([var for var in idata.posterior.data_vars if '_sigma' in var or var == 'Intercept'])

    # Filter only relevant variables that match our list
    relevant_vars = [var for var in filtered.data_vars if any(f"{v}" in f"{var}" for v in var_list)]
    
    if not relevant_vars:
        print("No matching variables found.")
        return None
    
    # Drop any data related to 'high_school[0]' for each dimension in group_dims
    for dimension in group_dims:
        try:
            filtered = filtered.drop_sel({dimension: '0'})
        except:
            print(f"{dimension} not present in the dataset, moving on.")
    
    # Compute medians across chains and draws
    medians = {
        var: filtered[var].median(dim=("chain", "draw"), skipna=True)
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

    # Return the sorted subset of filtered idata
    return filtered[sorted_vars]

# #funtion to get only the signficant vars if needed
def get_significant_vars_only(all_idata):
    hdi_datasets = [az.hdi(idata, hdi_prob=0.95) for idata in all_idata]

    sig_multi = []
    sig_multi_pc = []
    sig_flat = []
    sig_flat_pc = []

    for idx, hdi_dataset in enumerate(hdi_datasets):  
        significant_vars = []
        
        for var_name in hdi_dataset.data_vars:
            var_data = hdi_dataset[var_name]

            # Determine if there's a factor grouping
            factor_dim = None
            for dim in var_data.dims:
                if "factor_dim" in dim:
                    factor_dim = dim
                    break

            if factor_dim:
                # Loop over factor levels
                for i, level in enumerate(var_data[factor_dim].values):
                    lower = var_data.sel({factor_dim: level, "hdi": "lower"}).values
                    upper = var_data.sel({factor_dim: level, "hdi": "higher"}).values

                    if lower.size == 1 and upper.size == 1:
                        lower, upper = lower.item(), upper.item()

                        if lower > 0 or upper < 0:
                            full_name = f"{var_name}[{level}]"
                            significant_vars.append(full_name)
            else:
                # If no factor grouping
                lower = var_data.sel(hdi="lower").values
                upper = var_data.sel(hdi="higher").values

                if lower.size == 1 and upper.size == 1:
                    lower, upper = lower.item(), upper.item()

                    if lower > 0 or upper < 0:
                        significant_vars.append(var_name)

        # Assign variables to respective lists
        if idx == 0:
            sig_multi = significant_vars
        elif idx == 1:
            sig_multi_pc = significant_vars
        elif idx == 2:
            sig_flat = significant_vars
        elif idx == 3:
            sig_flat_pc = significant_vars

    return sig_multi, sig_multi_pc, sig_flat, sig_flat_pc

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

# #create our sorted IDATA for all the vars in all the groups
sorted_multi = process_filtered_idata(idata_multi, idata_multi.posterior.data_vars, group_dims = ["high_school__factor_dim", 'middle_school__factor_dim'])
sorted_multi_pc = process_filtered_idata(idata_multi_pc, idata_multi_pc.posterior.data_vars, group_dims = ["high_school__factor_dim", 'middle_school__factor_dim'])

sig_multi, sig_multi_pc, sig_flat, sig_flat_pc = get_significant_vars_only(all_idata)

summary_flat = az.summary(idata_flat)
summary_flat_pc = az.summary(idata_flat_pc)

# ##############################################################################
#             # EXTACT OUR MOST INFLUENTIAL FACTORS FOR FLAT MODEL
# ##############################################################################
all_summaries = [summary_flat, summary_flat_pc]
summary_names = ["flat-model-all-years", "flat-model-post-covid"]  # Corresponding names for file output

for i, summary in enumerate(all_summaries):
    # Filter to exclude random effect standard deviations (_sigma), the Intercept, and the 'refugee_student_y' variable
    fixed_effects_summary = summary[
        (~summary.index.str.contains('_sigma')) & 
        (~summary.index.str.contains("Intercept")) & 
        (~summary.index.str.contains("refugee_student_y"))
    ]
    
    # Filter for significant effects (hdi_3% > 0 or hdi_97% < 0)
    significant_effects = fixed_effects_summary[
        (fixed_effects_summary["hdi_3%"] > 0) | (fixed_effects_summary["hdi_97%"] < 0)
    ]
    
    # Sort by absolute mean effect size (largest to smallest)
    sorted_fixed_effects = significant_effects.reindex(
        significant_effects["mean"].abs().sort_values(ascending=False).index
    )
    
    # Select the top 10 most influential fixed effects (excluding Intercept and 'refugee_student_y')
    top_10_fixed_effects = sorted_fixed_effects.head(10)
    
    # Plot absolute sorted values
    plt.figure(figsize=(10, 6))
    sns.barplot(
        x=top_10_fixed_effects["mean"], 
        y=top_10_fixed_effects.index, 
        palette=usu_palette
    )
    plt.axvline(x=0, color="black", linestyle="--", alpha=0.7)
    plt.xlabel("Effect Size (Mean)")
    plt.ylabel("Predictor")
    plt.title(f"Top 10 Most Influential Predictors ({summary_names[i]})")
    plt.subplots_adjust(left=0.4)
    plt.savefig(f"{folder_path}/top10-plot-{summary_names[i]}.png", format="png")
    plt.close()
    
    # Sort by raw mean effect size (largest to smallest)
    sorted_fixed_effects_not_abs = significant_effects.reindex(
        significant_effects["mean"].sort_values(ascending=False).index
    )
    
    # Select the top 10 most influential fixed effects (excluding Intercept and 'refugee_student_y')
    top_10_fixed_effects_non_abs = sorted_fixed_effects_not_abs.head(10)
    
    # Plot non-absolute sorted values
    plt.figure(figsize=(10, 6))
    sns.barplot(
        x=top_10_fixed_effects_non_abs["mean"], 
        y=top_10_fixed_effects_non_abs.index, 
        palette=usu_palette
    )
    plt.axvline(x=0, color="black", linestyle="--", alpha=0.7)
    plt.xlabel("Effect Size (Mean)")
    plt.ylabel("Predictor")
    plt.title(f"Top 10 Most Influential Predictors ({summary_names[i]})")
    plt.subplots_adjust(left=0.4)
    plt.savefig(f"{folder_path}/top10-plot-non-abs-{summary_names[i]}.png", format="png")
    plt.close()


# ###############################################################################
#                          # INTERVAL PLOTS
# ###############################################################################

# *******CHANGE THIS NAME HERE BASED ON HOW YOU WOULD LIKE IT TO SAVE***********
interval_plot_base_name = 'interval-plot-multilevel-model'

#Interval plot of sorted effects and to compare multiple models
def compare_group_effects(
    models,
    labels,
    var_name,
    filename,
    group_dim="high_school__factor_dim",
    hdi_prob=0.94,
    sort_by="mean"
):
    """
    Compare group-level effects across multiple models (e.g., pre/post-COVID) using forest plots.

    Parameters:
    - models: list of ArviZ InferenceData objects
    - labels: list of labels corresponding to each model
    - var_name: str, name of the variable to plot (must be present in each model)
    - group_dim: str, dimension that identifies the group (e.g., schools)
    - hdi_prob: float, HDI width (default: 0.94)
    - sort_by: str, "mean" or "median" (default: "mean")
    - filename: str, name of the file to save to under figures/model-plots/
    """

    # USU color palette
    colors = ["#00274C", "#9EA2A2", "#D6D6D6"]

    # Directory handling
    output_dir = "figures/model-plots"
    os.makedirs(output_dir, exist_ok=True)
    full_path = os.path.join(output_dir, filename)

    # Collect summaries
    summaries = []
    for i, model in enumerate(models):
        summary = az.summary(model, var_names=[var_name], hdi_prob=hdi_prob)
        group_labels = model[var_name].coords[group_dim].values
        summary["group"] = group_labels
        summary["model"] = labels[i]
        summaries.append(summary)

    # Merge summaries
    all_summary = summaries[0].copy()
    for s in summaries[1:]:
        all_summary = all_summary.merge(s, how="outer")

    # Use the first model's sorting logic
    sort_column = sort_by if sort_by in all_summary.columns else "mean"
    sorted_groups = summaries[0].sort_values(sort_column)["group"].values
    y_pos = np.arange(len(sorted_groups))

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, summary in enumerate(summaries):
        summary = summary.set_index("group").loc[sorted_groups].reset_index()
        offset = (i - len(summaries) / 2) * 0.2  # Adjust offset for overlapping points
        ax.errorbar(
            summary["mean"],
            y_pos + offset,
            xerr=[
                summary["mean"] - summary[f"hdi_{int((1 - hdi_prob)/2 * 100)}%"],
                summary[f"hdi_{int((1 + hdi_prob)/2 * 100)}%"] - summary["mean"]
            ],
            fmt='o',
            color=colors[i % len(colors)],
            label=labels[i],
            capsize=4
        )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_groups)
    ax.set_xlabel(f"Estimated Effect ({sort_by.title()} with {int(hdi_prob*100)}% HDI)")
    ax.set_title(f"Posterior Comparison: {var_name}")
    ax.legend()
    
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(full_path, dpi=300)
    plt.close()

    print(f"✅ Plot saved to: {full_path}")

#SAVE THE PLOT, First two parameters must be wrapped in a [] in order to treat like a list
compare_group_effects([sorted_multi, sorted_multi_pc], ['Model 08', 'Model 07'], 'non_ell_with_disability|high_school', interval_plot_base_name)