#____________________________________________________________________________
                             #IMPORT LIBRARIES
#____________________________________________________________________________ 
import arviz as az
import numpy as np
import matplotlib.pyplot as plt
import os 


# Define the folder path where the trace plots will be saved
folder_path = "figures/model-plots"

# Check if the folder exists, and create it if not
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
#____________________________________________________________________________ 
                     #LOAD IN THE MODEL OUTPUT/ DATASET
#____________________________________________________________________________ 

# Load trace from the NetCDF file saved from model output and the dataset file
try:
    trace = az.from_netcdf("data/trace_output.nc")
except Exception as e:
    print(f"Loading Data failed: {e}")

#____________________________________________________________________________
               #FOREST PLOTS FOR POSTERIOR DISTRIBUTION
#____________________________________________________________________________

#forest plot for all predictors and for all predictors and all groups
az.plot_forest(trace, var_names=["b"], 
               combined=True, 
               hdi_prob=0.95,
               kind = 'ridgeplot',
               ridgeplot_quantiles=[.25, .5, .75],
               ridgeplot_overlap=0.7,
               figsize=(12, 9))
plt.title("Posterior Distributions of Each Predictor Across Each Group")
plt.subplots_adjust(left=0.3)  # Increase left margin
plt.savefig(f"{folder_path}/forest-plot-all-predictors-all-groups.png", format="png")




# Get the group names (adjust this based on your trace structure)
groups = trace.posterior["group"].values

# Iterate over each unique group
for group in np.unique(groups):
    print(f"Plotting top predictors for group: {group}")
    
    # Extract data for the specific group
    group_b = trace.posterior["b"].sel(group=group)  # Extract the coefficients for this group
    
    # Compute the mean effect size (average over chains and draws)
    b_means = group_b.mean(dim=["chain", "draw"])  # Mean over chains and draws
    
    
    # Sort predictors by effect size (descending order)
    sorted_indices = np.argsort(-b_means.values)[:10]  # Top 10 predictors
    predictor_names = group_b.coords["predictor"].values
    top_10_predictors = predictor_names[sorted_indices]
    
    # Subset the trace to include only the top 10 predictors for this group
    subset_trace = trace.sel(group=group, predictor=top_10_predictors)
    
    # Create a separate forest plot for each group
    az.plot_forest(
        subset_trace,
        var_names=["b"], 
        coords={"predictor": top_10_predictors.tolist()},  # Use list to preserve order
        combined=True,
        hdi_prob=0.95,
        kind = 'ridgeplot',
        ridgeplot_quantiles=[.25, .5, .75],
        ridgeplot_overlap=0.7,
        figsize=(12, 9)
    )
    plt.title(f"Top 10 Predictors for Group: {group}")
    plt.subplots_adjust(left=0.3)
    plt.savefig(f"{folder_path}/forest-plot-top-10-predictors-{group}.png", format="png")
    plt.close()


#____________________________________________________________________________
                         # TRACE PLOTS
#____________________________________________________________________________
# Create and save a trace plot for the 'b' parameter overall (for all predictors)
plt.figure(figsize=(9, 7))
az.plot_trace(trace, var_names=["b"], combined=True)
plt.title("Trace Plot for All Predictors")
plt.subplots_adjust(left=0.3)

# Save the trace plot as a PNG file
plt.savefig(f"{folder_path}/trace-plot-all-predictors.png", format="png")
plt.close()



# Iterate over each unique group
for group in np.unique(groups):
    print(f"Plotting trace plot for group: {group}")
    
    # Extract data for the specific group
    group_b = trace.posterior["b"].sel(group=group)  # Extract the coefficients for this group
    
    # Create and save the trace plot for this group
    plt.figure(figsize=(9, 7))
    az.plot_trace(
        group_b,  # Select data for this group
        var_names=["b"],  # Use 'b' or other relevant variables
        combined=True,
    )
    plt.title(f"Trace Plot for Group: {group}")
    plt.subplots_adjust(left=0.3)

    # Save the trace plot as a PNG file
    plt.savefig(f"{folder_path}/trace-plot-group-{group}.png", format="png")
    plt.close()

