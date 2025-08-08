##############################################################################
# IMPORT LIBRARIES
############################################################################## 
import arviz as az
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os 
import glob
import seaborn as sns
import itertools
from matplotlib.colors import ListedColormap, BoundaryNorm

#############################################################################
# PREP FOR PHASE 1 MODEL VISUALS
##############################################################################
# Load trace from the NetCDF file saved from model output and the dataset file
try:
    #Inference data for all years
    idata_multi = az.from_netcdf("output/multilevel-model-output_12.nc")

    #inference data for multilevel model post covid
    idata_multi_pc = az.from_netcdf("output/multilevel-model-output_13.nc")

    #Inference Data for Flat model all Years
    idata_flat = az.from_netcdf("output/flat-model-output_12.nc")

    #Inference Data for Flat model post covid
    idata_flat_pc = az.from_netcdf("output/flat-model-output_10.nc")

    #store all inference data in a list to iterate through later
    
    all_idata = [idata_multi, idata_multi_pc, idata_flat, idata_flat_pc]
except Exception as e:
    print(f"Loading Data failed: {e}")

# Define the folder path where the trace plots will be saved
folder_path = "figures"
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
# CREATE OUR GROUPIING STRUCTURES FOR THE VISUALS
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
sorted_multi = process_filtered_idata(idata_multi, idata_multi.posterior.data_vars, group_dims = ["high_school__factor_dim", 'middle_school__expr_dim'])
sorted_multi_pc = process_filtered_idata(idata_multi_pc, idata_multi_pc.posterior.data_vars, group_dims = ["high_school__factor_dim", 'middle_school__expr_dim'])

sig_multi, sig_multi_pc, sig_flat, sig_flat_pc = get_significant_vars_only(all_idata)

summary_flat = az.summary(idata_flat)
summary_flat_pc = az.summary(idata_flat_pc)

##############################################################################
# EXTACT OUR MOST INFLUENTIAL FACTORS FOR FLAT MODEL
##############################################################################
all_summaries = [summary_flat, summary_flat_pc]
summary_names = ["Average Effects Across All Years", "Average Effects Post-Covid"]  # Corresponding names for file output

for i, summary in enumerate(all_summaries):
    fixed_effects_summary = summary[
        (~summary.index.str.contains('_sigma')) & 
        (~summary.index.str.contains("Intercept")) & 
        (~summary.index.str.contains("homeless_y")) &
        (~summary.index.str.contains("refugee_student_y"))
    ]
    
    significant_effects = fixed_effects_summary[
        (fixed_effects_summary["hdi_3%"] > 0) | (fixed_effects_summary["hdi_97%"] < 0)
    ]
    
    sorted_fixed_effects = significant_effects.reindex(
        significant_effects["mean"].abs().sort_values(ascending=False).index
    )
    
    top_10_fixed_effects = sorted_fixed_effects.head(10)
    
    # --- First Plot (Absolute values) ---
    plt.figure(figsize=(12, 7), facecolor='white')
    sns.barplot(
        x=top_10_fixed_effects["mean"], 
        y=top_10_fixed_effects.index, 
        palette=usu_palette
    )
    
    plt.axvline(x=0, color="black", linestyle="--", alpha=0.6)
    plt.xlabel("Impact On Likelihood of Taking AC Courses\nPositive = More Likely | Negative = Less Likely", fontsize=14)
    plt.ylabel("Predictor", fontsize=13)
    plt.title(f"{summary_names[i]}", fontsize=16, pad=15)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(True, axis='x', linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(f"{folder_path}/flat-phase-1-plot-{summary_names[i]}.png", format="png", dpi=300, bbox_inches='tight')
    plt.close()

    sorted_fixed_effects_not_abs = significant_effects.reindex(
    significant_effects["mean"].sort_values(ascending=False).index
    )
    
    top_10_fixed_effects_non_abs = sorted_fixed_effects_not_abs.head(10)
    
    # --- Second Plot (Raw values) ---
    plt.figure(figsize=(12, 7), facecolor='white')
    sns.barplot(
        x=top_10_fixed_effects_non_abs["mean"], 
        y=top_10_fixed_effects_non_abs.index, 
        palette=usu_palette
    )
    
    plt.axvline(x=0, color="black", linestyle="--", alpha=0.6)
    plt.xlabel("Effect Size (Mean)\nPositive = More Likely | Negative = Less Likely", fontsize=14)
    plt.ylabel("Predictor", fontsize=13)
    plt.title(f"{summary_names[i]}", fontsize=16, pad=15)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(True, axis='x', linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(f"{folder_path}/flat-phase-1-plot-non-abs-{summary_names[i]}.png", format="png", dpi=300, bbox_inches='tight')

    plt.close()

# ###############################################################################
# INTERVAL PLOTS
# ###############################################################################
def compare_group_effects(
    models,
    labels,
    var_name,
    filename,
    cleaned_var_name,
    group_dims= ["high_school__factor_dim", 'middle_school__expr_dim'],  # Can now be a list of dimensions or None
    hdi_prob=0.94,
    sort_by="mean"
):

    # USU color palette
    colors = ["#00274C", "#9EA2A2", "#D6D6D6"]

    # Directory handling
    output_dir = "figures"
    os.makedirs(output_dir, exist_ok=True)
    full_path = os.path.join(output_dir, filename)

    # Collect summaries
    summaries = []
    for i, model in enumerate(models):
        summary = az.summary(model, var_names=[var_name], hdi_prob=hdi_prob)

        # If group_dims not provided, try to infer it
        if group_dims is None:
            group_dims = list(model[var_name].dims)
        elif isinstance(group_dims, str):
            group_dims = [group_dims]

            # Filter to only the dimensions that exist in the model
        present_dims = [dim for dim in group_dims if dim in model[var_name].coords]
        if not present_dims:
            raise ValueError(
                f"None of the provided dimensions {group_dims} are found in model variable '{var_name}'."
            )

        # Get coordinate combinations across all present dimensions
        
        dim_values = [model[var_name].coords[dim].values for dim in present_dims]
        group_labels = [' | '.join(map(str, comb)) for comb in itertools.product(*dim_values)]

        # Check match
        if len(group_labels) != len(summary):
            raise ValueError(
                f"Group labels length ({len(group_labels)}) does not match summary rows ({len(summary)}). "
                f"Check if the correct var_name and group_dims are used."
            )

        summary = summary.reset_index(drop=True)
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
    ax.set_xlabel(f"Estimated Effect ({sort_by.title()})")
    ax.set_title(f"Posterior Comparison: {cleaned_var_name}")
    ax.legend()
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(full_path, dpi=300)
    plt.close()

    print(f"✅ Plot saved to: {full_path}")

# *******CHANGE THIS NAME HERE BASED ON HOW YOU WOULD LIKE IT TO SAVE***********
interval_plot_base_name = 'interval-comparisons-gender'

#SAVE THE PLOT, First two parameters must be wrapped in a [] in order to treat like a list
compare_group_effects([sorted_multi, sorted_multi_pc], ['All Years', 'Post-Covid'], 'gender_m|high_school', interval_plot_base_name, 'Effect of Being Male Across Schools' )

###############################################################################
# HEAT MAP HIGH LEVEL
###############################################################################
# Access the posterior dataset
posterior = idata_multi.posterior
flat_posterior = idata_flat.posterior

# Step 1: Extract all high school-specific predictors
predictor_vars = [
    var for var in posterior.data_vars
    if "|high_school" in var and "middle_school|high_school" not in var and "sigma" not in var and '1' not in var
]

high_schools = posterior.coords["high_school__factor_dim"].values

# Step 2: Classify each predictor-high school pair
def classify_effect(varname):
    values = posterior[varname]  # shape: (chain, draw, high_school)
    summary = az.summary(values, hdi_prob=0.95)
    summary["high_school"] = high_schools
    summary["predictor"] = varname.split("|")[0]

    def classify(row):
        if row["hdi_2.5%"] > 0:
            return 1  # significantly positive
        elif row["hdi_97.5%"] < 0:
            return -1  # significantly negative
        else:
            return 0  # not significant

    summary["classification"] = summary.apply(classify, axis=1)
    return summary[["predictor", "high_school", "classification"]]

# Step 3: Concatenate all results
classification_df = pd.concat([classify_effect(var) for var in predictor_vars])

# --- New Step: Add fixed effect classifications for each predictor (same y-axis as heatmap) ---

# Step A: Extract flat predictors (only ones that match multilevel predictors)
flat_predictor_vars = [
    var for var in flat_posterior.data_vars
    if "high_school" not in var and "Intercept" not in var and "sigma" not in var and '1' not in var
]

# Step B: Classification function for fixed effects
def classify_fixed_effect(varname):
    values = flat_posterior[varname]
    summary = az.summary(values, hdi_prob=0.95)
    summary["predictor"] = varname

    def classify(row):
        if row["hdi_2.5%"] > 0:
            return 1
        elif row["hdi_97.5%"] < 0:
            return -1
        else:
            return 0

    summary["classification"] = summary.apply(classify, axis=1)
    return summary[["predictor", "classification"]]

# Step C: Concatenate fixed effects into a single DataFrame
fixed_effects_df = pd.concat([classify_fixed_effect(var) for var in flat_predictor_vars])
fixed_effects_df = fixed_effects_df.drop_duplicates(subset=["predictor"])

# Step D: Remove duplicates from the multilevel classification if needed
classification_df = classification_df.drop_duplicates(subset=["predictor", "high_school"])

# Step E: Map fixed effect classifications to each predictor
classification_df["Fixed Effects"] = classification_df["predictor"].map(
    fixed_effects_df.set_index("predictor")["classification"]
)

# Step 4: Pivot to matrix form for heatmap
heatmap_matrix = classification_df.pivot(
    index="predictor", columns="high_school", values="classification"
)

# ✅ Add the fixed effects classification column
heatmap_matrix["Average Effects"] = classification_df.drop_duplicates("predictor").set_index("predictor")["Fixed Effects"]

# ✅ Ensure predictor order is preserved
heatmap_matrix = heatmap_matrix.loc[sorted(heatmap_matrix.index)]

# Step 5: Define USU color palette
usu_colors = [ "#9EA2A2", "#D6D6D6", "#00274C"]
cmap = ListedColormap(usu_colors)
bounds = [-1.5, -0.5, 0.5, 1.5]
norm = BoundaryNorm(bounds, cmap.N)

# Step 6: Plot (PowerPoint-optimized: square layout for better y-label visibility)
num_predictors = len(heatmap_matrix)

# Increase height for more vertical room
height = max(12, num_predictors * 0.6)
plt.figure(figsize=(14, 8))  # Adjust height dynamically

sns.set(font_scale=1.3)  # Slight bump for clarity on PPT
sns.set_style("white")

ax = sns.heatmap(
    heatmap_matrix,
    cmap=cmap,
    norm=norm,
    linewidths=0.5,
    linecolor='white',
    cbar_kws={"ticks": [-1, 0, 1]},
    vmin=-1.5,
    vmax=1.5,
    xticklabels=True,
    yticklabels=True,
    square=False  # Set to True if you want perfect square cells (optional)
)

# Custom colorbar labels
colorbar = ax.collections[0].colorbar
colorbar.set_ticks([-1, 0, 1])
colorbar.set_ticklabels(["Negative", "Not Significant", "Positive"])

# Make axis labels larger and bolder
ax.set_xticklabels(ax.get_xticklabels(), ha="center", fontsize=14, weight='bold')
ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=16, weight='bold')  # Bigger y labels

# Clean labels
plt.xlabel("")
plt.ylabel("")
plt.tight_layout()

# Save for PowerPoint
full_path = 'figures/heat-map-high-level-fixed-effects.png'
plt.savefig(full_path, dpi=300)
plt.show()

#############################################################################
# PREP FOR PHASE 2 MODEL VISUALS
##############################################################################
# Load trace from the NetCDF file saved from model output and the dataset file
try:
    # Inference data for enrollment model
    # idata_enroll = az.from_netcdf("output/flat-model-output_13.nc")
    idata_enroll = az.from_netcdf("output/flat-model-output_15.nc")
    # Inference data for graduation model
    # idata_grad = az.from_netcdf("output/flat-model-output_14.nc")
    idata_grad = az.from_netcdf("output/flat-model-output_16.nc")
except Exception as e:
    print(f"Loading Data failed: {e}")

all_idata = [ idata_enroll, idata_grad ]

#all groups from phase 2, for easier sorted plotting
groups = {
    "Academic Performance": [
        "composite_score", "english_score", "math_score", "reading_score",
        "science_score", "writing_score", "overall_gpa", "percent_days_attended",
        "passed_civics_exam", "hs_advanced_math_y", "extracurricular_ind",
        "part_time_home_school_y"
    ],

    "Environmental Factors": [
        "immigrant_y", "migrant_y", "homeless_y", "military_child_y", "refugee_student_y"
    ],

    "Disability & ELL Status": [
        "ell_with_disability", "ell_without_disability",
        "non_ell_with_disability", "services_504_y",
        "environment_h", "environment_r", "scram_membership"
    ],

    "Demographic": [
        "tribal_affiliation_g", "tribal_affiliation_n", "tribal_affiliation_o",
        "tribal_affiliation_p", "tribal_affiliation_s", "tribal_affiliation_u",
        "amerindian_alaskan_y", "asian_y", "black_african_amer_y",
        "hawaiian_pacific_isl_y", "white_y", "ethnicity_y",
        "gender_m", "gender_u"
    ],

    "Classes": [
         "arts", "business", "math", "science", "social_studies", "technology", "language", "medical"
    ],

    "Course Types": [
        "ap_course", "btech_course", "ce_course",
    ],

    "School": [
        "high_school[Mountain Crest]", "high_school[Ridgeline]", "high_school[Sky View]",
        "middle_school[North Cache Middle]", "middle_school[South Cache Middle]",
        "middle_school[Spring Creek Middle]"
    ]
}

# USU color palette
colors = ["#00274C", "#9EA2A2", "#D6D6D6"]

#####################################################################
# INTERVAL PLOT FUNCTION FOR PHASE 2 MODELS
#####################################################################
def plot_summary_intervals(group_vars, labels, models, file_path, hdi_prob=0.94, sort_by_model=0):
    # Collect summaries
    summaries = []
    for model in models:
        summary = az.summary(model, hdi_prob=hdi_prob)
        filtered_summary = summary.loc[summary.index.intersection(group_vars)]
        summaries.append(filtered_summary)

    # Sort by the specified model's means
    sorted_groups = summaries[sort_by_model]["mean"].sort_values(ascending=True).index.tolist()

    # Positions for y-axis
    y_pos = np.arange(len(sorted_groups))

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, summary in enumerate(summaries):
        summary = summary.loc[sorted_groups] 
        offset = (i - (len(summaries) - 1) / 2) * 0.15  # space between points

        ax.errorbar(
            summary["mean"],
            y_pos + offset * 2,
            xerr=[
                summary["mean"] - summary[f"hdi_{int((1 - hdi_prob)/2 * 100)}%"],
                summary[f"hdi_{int((1 + hdi_prob)/2 * 100)}%"] - summary["mean"]
            ],
            fmt='o',
            color=colors[i % len(colors)],
            label=labels[i],
            capsize=4,
            markersize=6,
            alpha=0.9
        )

    # Clean up label formatting (replace underscores, title case)
    clean_labels = [label.replace("_", " ").title() for label in sorted_groups]

    ax.set_yticks(y_pos)
    ax.set_yticklabels(clean_labels)
    ax.set_xlabel("Impact On Likelihood\nPositive = More Likely | Negative = Less Likely")
    ax.set_title("Advanced Course Categories\nPosterior Effects")
    ax.legend()
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(file_path, dpi=300)
    plt.close()

    print(f"Plot saved to: {file_path}")

#ALTER FILE PATH AS NEEDED
file_path = "figures/2025-update_phase-02_comparison-college-enrollment-by-advanced-course-category.png"
# file_path = "figures/phase-02_comparison-college-enrollment-by-advanced-course-category.png"

#Plot whichever groups you want to visualize for phase 2 models
plot_summary_intervals(groups["Classes"], ["College Enrollment", "College Graduation"], all_idata, file_path)

