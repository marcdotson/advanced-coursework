import pandas as pd
import bambi as bmb
import arviz as az
# import networkx as nx
import os
import matplotlib.pyplot as plt

# ################################################################################################
# #                            #CREATE A DAG TO JUSTIFY THE MODEL
# ################################################################################################
# G = nx.DiGraph()

# # Add edges based on the DAG structure
# edges = [
#     ("Teacher", "AC_Ind"),
#     ("Teacher", "Overall_GPA"),
#     ("Attendance", "Overall_GPA"),
#     ("School", "Teacher"),
#     ("School", "Overall_GPA"),
#     ("School", "AC_Ind"),
#     ("Disadvantage", "Overall_GPA"),
#     ("Disadvantage", "Attendance"),
#     ("Disadvantage", "AC_Ind"),
#     ("Overall_GPA", "AC_Ind")
# ]

# G.add_edges_from(edges)

# # Draw the DAG
# plt.figure(figsize=(10, 8))
# pos = nx.shell_layout(G)  # Trying a shell layout for better separation
# nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=3000, font_size=10)
# plt.title("DAG for Advanced Coursework ASC Project")
# plt.show()

################################################################################################
# Load in the dataset
df = pd.read_csv('data/modeling_data.csv', low_memory = False)

# Define the folder path where the trace plots will be saved
folder_path = "output/"

# Check if the folder exists, and create it if not
if not os.path.exists(folder_path):
    os.makedirs(folder_path)


##################################################################################################
# PREP THE MODEL AND SPECIFY COLUMNS TO DROP
##################################################################################################

# Columns to exclude from modeling 
col_drop = ['student_number']
for col in df.columns:
    if col.startswith('teacher') or col.startswith('exit'):
        col_drop.append(col)

# Define base dataframe after dropping columns
df_base = df.drop(columns=col_drop, axis=1)

# create a list of columns to include as random effects
rand_effects = []
for col in df_base.columns:
    if col.startswith('school'): # Just include schools as random effects
        rand_effects.append(col)

# Extract potential predictors (excluding the target 'ac_ind')
# all_predictors = " + ".join(df_base.columns.difference(["ac_ind", "ell_disability_group"]))
fixed_effects = (" + ".join(df_base.columns
    .difference(["ac_ind", "ell_disability_group"])
    .difference(rand_effects))
)

rand_effects = " + ".join(rand_effects)

#create the string formated model formula 
# model_formula = f"ac_ind ~ {all_predictors} + ({all_predictors} | ell_disability_group)"
# model_formula = f"ac_ind ~ ({all_predictors} | ell_disability_group)"
model_formula = f"ac_ind ~ {fixed_effects} + ({rand_effects} | ell_disability_group)"


################################################################################################
# RUN THE FLAT MODEL AND EXPORT DRAWS TO A FILE
################################################################################################

if __name__ == '__main__':
    print("Starting model setup...")

    #establish the flat Logistic Regression Model
    multilevel_model = bmb.Model(model_formula, df_base, family="bernoulli")
    # apply the .build() method prior to fitting the model
    multilevel_model.build() 

    # Run the sampling *******ADJUST THE AMOUNT OF SAMPLING (TUNE, DRAW, ETC.) HERE AS NEEDED ********
    try:
        print("Starting model sampling...")
        #fit the model with the the flat_model that was created prior
        multilevel_fitted = multilevel_model.fit(
            draws=2000, inference_method='mcmc', random_seed=42, target_accept = .9)
        print("Sampling complete.")

    except Exception as e:
        print(f"Sampling failed: {e}")
        multilevel_fitted = None  # Set output to None if sampling fails

    # Only try to export if it is not none
    if multilevel_fitted is not None:
        # Save trace to a NetCDF file
        print('Saving Model Trace to a File...')
        multilevel_fitted.to_netcdf(f"{folder_path}/multilevel-model-output.nc")
        print('Trace successfully saved, look for it in the data folder')

        # Extract posterior summary to save sorted predictors to a csv
        summary = az.summary(multilevel_fitted)
       # Sort predictors by mean effect size (largest to smallest)
        sorted_summary = summary.reindex(summary["mean"].abs().sort_values(ascending=False).index)

        # Save ordered model output to CSV
        sorted_summary.to_csv(f"{folder_path}/multilevel-model-output-ordered.csv")
        print("Ordered model output saved successfully!")

    else:
        print("Trace is None, cannot save trace to a file.")

