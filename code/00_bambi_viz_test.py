#########################################################################
#                          IMPORT LIBRARIES
#########################################################################
import arviz as az
import numpy as np
import matplotlib.pyplot as plt
import os 

#########################################################################
#             LOAD IN THE DATA AND ESTABLISH TRACE OBJECT
#########################################################################

# Define the folder path where the trace plots will be saved
folder_path = "figures/model-plots"

# Check if the folder exists, and create it if not
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Load trace data from NetCDF file
trace = az.from_netcdf("output/flat-model-output.nc")

# Extract posterior summary statistics
summary = az.summary(trace)

#########################################################################
#                           FOREST PLOTS
#########################################################################

# Rank predictors by mean effect size (most influential)
summary["abs_mean"] = summary["mean"].abs() # Use mean or median based on preference
top_10_predictors = summary.nlargest(10, "abs_mean").index.tolist()

# Plot only the top 10 influential predictors
az.plot_forest(trace, 
               var_names=top_10_predictors,  # Select only top 10 predictors
               combined=True, 
               hdi_prob=0.95,
               kind="ridgeplot",
               ridgeplot_quantiles=[0.25, 0.5, 0.75],
               ridgeplot_overlap=0.7)

plt.title("Top 10 Most Influential Predictors")
plt.subplots_adjust(left=0.2)  # Increase left margin
plt.savefig(f"{folder_path}/flat-model-forest-plot-top-10-predictors.png", format="png")
plt.close()
print("Forest plot for top 10 predictors saved successfully!")

########################################################################

# Sort predictors by the mean effect size (largest to smallest)
sorted_predictors = summary["mean"].sort_values(ascending=False).index.tolist()

# Plot only the sorted predictors
az.plot_forest(trace, 
               var_names=sorted_predictors,  # Order predictors by effect size
               combined=True, 
               hdi_prob=0.95,
               kind="ridgeplot",
               ridgeplot_quantiles=[0.25, 0.5, 0.75],
               ridgeplot_overlap=0.7)

plt.title("Posterior Distribution For All Predictors")
plt.subplots_adjust(left=0.2)  # Increase left margin
plt.savefig(f"{folder_path}/flat-model-forest-plot-all-predictors.png", format="png")

print("Forest plot all predictors saved successfully!")


#########################################################################
#                           TRACE PLOTS
#########################################################################

# Create and save a trace plot for the 'b' parameter overall (for all predictors)
az.plot_trace(trace
              ,combined=True)
plt.subplots_adjust(left=0.3)
plt.tight_layout()  # Automatically adjust layout to prevent overlap

# Save the trace plot as a PNG file
plt.savefig(f"{folder_path}/flat-model-trace-plot-all-predictors.png", format="png", bbox_inches="tight")
plt.close()


#########################################################################
#                           RANK PLOTS
#########################################################################


#It looks at how often different parameter values appear across all Markov Chain Monte Carlo (MCMC) samples.
#If sampling is fair and efficient, the ranks should be evenly distributed across the range of values.
#If ranks are skewed or clumped, it may mean the model has sampling bias or convergence issues.

#Look for:
# Even, flat bars → Good sampling, no bias.
# Uneven or clumped bars → Possible sampling bias or poor mixing, which might require tuning.

# Create and save rank plots for all parameters
az.plot_rank(trace)
plt.title("Rank Plots for All Parameters")
plt.savefig(f"{folder_path}/rank-plot.png", format="png")
plt.close()
print("Rank plot saved successfully!")

# Our rank plot looks good. We believe that the sampling is fair and efficient.


#########################################################################
#                           POSTERIOR DISTRIBUTIONS
#########################################################################

# Create and save posterior distributions for all parameters
az.plot_posterior(trace,
                  kind="kde", # Kernel Density Estimate for smoothness
                  hdi_prob=0.95,  # 95% Highest Density Interval
                  ref_val=0)  # Reference line at 0 for effect size interpretation

plt.title("Posterior Distributions for All Parameters")
plt.savefig(f"{folder_path}/flat-model-posterior-distributions.png", format="png")
plt.close()
print("Posterior distributions plot saved successfully!")