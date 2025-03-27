import pandas as pd
import bambi as bmb
import arviz as az
# import networkx as nx
import os
import matplotlib.pyplot as plt
import glob

# ################################################
# #CREATE A DAG TO JUSTIFY THE MODEL
# ################################################
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


########################################################
# LOAD IN THE DATASET AND ESTABLISH FOLDER PATH
########################################################

df = pd.read_csv('data/modeling_data.csv', low_memory = False)

# Define the folder path where the trace plots will be saved
folder_path = "output/"

# Check if the folder exists, and create it if not
if not os.path.exists(folder_path):
    os.makedirs(folder_path)


#######################################################
# PREP THE MODEL AND SPECIFY THE MODEL FORMULA
#######################################################

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


################################################
# RUN THE MULTILEVEL MODEL 
################################################

if __name__ == '__main__':
    print("Starting model setup...")

    #establish the flat Logistic Regression Model
    multilevel_model = bmb.Model(model_formula, df_base, family="bernoulli",  noncentered=True)
    # apply the .build() method prior to fitting the model
    multilevel_model.build() 

    # Run the sampling *******ADJUST THE AMOUNT OF SAMPLING (TUNE, DRAW, ETC.) HERE AS NEEDED ********
    try:
        print("Starting model sampling...")
        #fit the model with the the flat_model that was created prior
        multilevel_fitted = multilevel_model.fit(
            draws=2000, inference_method='mcmc', random_seed=42, target_accept = .9, 
            idata_kwargs={"log_likelihood": True})
        print("Sampling complete.")

    except Exception as e:
        print(f"Sampling failed: {e}")
        multilevel_fitted = None  # Set output to None if sampling fails



###############################################################
# SAVE THE MODEL OUTPUT AND THE SORTED MODEL OUTPUT
###############################################################

# Function to find the next available output filename
def get_next_filename(folder_path, base_name, extension):
    """Finds the next available file number to avoid overwriting."""
    existing_files = glob.glob(f"{folder_path}/{base_name}_*.{extension}")
    existing_numbers = sorted(
        [int(f.split("_")[-1].split(".")[0]) for f in existing_files if f.split("_")[-1].split(".")[0].isdigit()]
    )

    next_number = existing_numbers[-1] + 1 if existing_numbers else 1
    return f"{folder_path}/{base_name}_{next_number:02d}.{extension}"


# Only try to export if the model is not None
if multilevel_fitted is not None:
    print('Saving Model Trace to a File...')

    # Generate incremented filenames
    netcdf_filename = get_next_filename(folder_path, "multilevel-model-output", "nc")
    csv_filename = get_next_filename(folder_path, "multilevel-model-output-ordered", "csv")

    # Save the NetCDF file
    multilevel_fitted.to_netcdf(netcdf_filename)
    print(f'Trace successfully saved as {netcdf_filename}')

    # Extract posterior summary
    summary = az.summary(multilevel_fitted)

    # Sort predictors by absolute mean effect size
    sorted_summary = summary.reindex(summary["mean"].abs().sort_values(ascending=False).index)

    # Save ordered model output to CSV
    sorted_summary.to_csv(csv_filename)
    print(f"Ordered model output saved as {csv_filename}!")

else:
    print("Trace is None, cannot save trace to a file.")

