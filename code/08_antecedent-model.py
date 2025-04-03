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

# df = pd.read_csv('data/modeling_data.csv', low_memory = False)
df = pd.read_csv('data/post_covid_modeling_data.csv', low_memory = False)


#######################################################
# import polars as pl

# df_pl = pl.DataFrame(df)

# df_pl.shape
# df_pl.columns

# df_pl.select(pl.col('student_number')).shape
# df_pl.select(pl.col('student_number')).unique().shape

# (df_pl
#     .group_by(pl.col('extracurricular_ind'))
#     .agg(n = pl.len())
# )

# (df_pl
#     .group_by(pl.col('high_school'))
#     .agg(n = pl.len())
# )

# (df_pl
#     .group_by(pl.col('middle_school'))
#     .agg(n = pl.len())
# )

# # # Automatically identify all binary columns (True/False or 0/1)
# # binary_cols = [
# #     col for col, dtype in zip(df_pl.columns, df_pl.dtypes)
# #     if (dtype in [pl.Boolean, pl.Int8, pl.Int16, pl.Int32, pl.Int64]) and col != 'ell_disability_group'
# # ]

# # # Compute counts of binary columns grouped by categorical variable
# # counts = (df_pl
# #     .group_by(pl.col('ell_disability_group'))
# #     .agg([
# #         pl.col(bin_col).sum().alias(f"{bin_col}_count") for bin_col in binary_cols
# #     ])
# #     .sort(pl.col('ell_disability_group'))
# # )
#######################################################

# Define the folder path where the model output will be saved
folder_path = "output/"

# Check if the folder exists, and create it if not
if not os.path.exists(folder_path):
    os.makedirs(folder_path)


#######################################################
# PREP THE MODEL AND SPECIFY THE MODEL FORMULA
#######################################################

# # Columns to exclude from modeling for model_data
# col_drop = ['student_number']
# for col in df.columns:
#     if col.startswith('teacher') or col.startswith('exit'):
#         col_drop.append(col)

# Columns to exclude from modeling for post_covid_modeling_data
col_drop = ['student_number']
for col in df.columns:
    if col.startswith('teacher') or col.startswith('exit') or col.startswith('envi') or col.startswith('tribal_affiliation_g'):
        col_drop.append(col)

# Define base dataframe after dropping columns
df_base = df.drop(columns=col_drop, axis=1)

# # # create a list of columns to include as random effects
# # rand_effects = []
# # for col in df_base.columns:
# #     if col.startswith('school'): # Just include schools as random effects
# #         rand_effects.append(col)
# fixed_effects = []
# for col in df_base.columns:
#     if col.startswith('school'): # Just include schools as random effects
#         fixed_effects.append(col)

# rand_effects = " + ".join(df_base.columns.difference(["ac_ind", "high_school", "middle_school"]))

# # Includes zero counts!
# zero_counts = ['migrant_y', 'military_child_y', 'refugee_student_y', 'homeless_y',
#     'part_time_home_school_y', 'services_504_y', 'immigrant_y',
#     'tribal_affiliation_n', 'tribal_affiliation_p']

# Extract potential predictors (excluding the target 'ac_ind')
# all_predictors = " + ".join(df_base.columns.difference(["ac_ind", "ell_disability_group"]))
all_predictors = " + ".join(df_base.columns.difference(["ac_ind", "high_school", "middle_school"]))

# # Include secondary schools as fixed effects.
# df_high_schools = pd.get_dummies(df_base['high_school'], dtype = float).rename(columns = {'0': 'Unknown_High', 'Cache High': 'Cache_High', 'Green Canyon': 'Green_Canyon', 'Mountain Crest': 'Mountain_Crest', 'Ridgeline': 'Ridgeline', 'Sky View': 'Sky_View'})
# df_middle_schools = pd.get_dummies(df_base['middle_school'], dtype = float).rename(columns = {'0': 'Unknown_Middle', 'North Cache Middle': 'North_Cache_Middle', 'South Cache Middle': 'South_Cache_Middle', 'Spring Creek Middle': 'Spring_Creek_Middle'})
# df_base = pd.concat([df_base, df_high_schools, df_middle_schools], axis = 1)
# # df_base = pd.concat([df_base, df_high_schools], axis = 1)

# fixed_effects = []
# for col in df_high_schools.columns.difference(['Unknown_High']):
#     fixed_effects.append(col)
# for col in df_middle_schools.columns.difference(['Unknown_Middle']):
#     fixed_effects.append(col)

# fixed_effects = " + ".join(fixed_effects)

# # fixed_effects = (" + ".join(df_base.columns
# #     .difference(["ac_ind", "ell_disability_group"])
# #     .difference(rand_effects))
# # )
# rand_effects = (" + ".join(df_base.columns
#     .difference(["ac_ind", "ell_disability_group"])
#     # .difference(fixed_effects))
#     .difference(fixed_effects)
#     .difference(zero_counts))
# )

# # rand_effects = " + ".join(rand_effects)
# fixed_effects_01 = " + ".join(fixed_effects)
# fixed_effects_02 = " + ".join(zero_counts)

#create the string formated model formula 
# model_formula = f"ac_ind ~ {all_predictors} + ({all_predictors} | ell_disability_group)"

# model_formula = f"ac_ind ~ ({all_predictors} | high_school)"
model_formula = f"ac_ind ~ ({all_predictors} | middle_school) + ({all_predictors} | high_school)"

# model_formula = f"ac_ind ~ {fixed_effects} + ({rand_effects} | high_school)"
# model_formula = f"ac_ind ~ {fixed_effects} + ({rand_effects} | ell_disability_group)"
# model_formula = f"ac_ind ~ {fixed_effects_01} + {fixed_effects_02} + ({rand_effects} | ell_disability_group)"


################################################
# RUN THE MULTILEVEL MODEL 
################################################

if __name__ == '__main__':
    print("Starting model setup...")

    #establish the flat Logistic Regression Model
    multilevel_model = bmb.Model(model_formula, df_base, family = "bernoulli", noncentered = True)
    # apply the .build() method prior to fitting the model
    multilevel_model.build() 

    # Run the sampling *******ADJUST THE AMOUNT OF SAMPLING (TUNE, DRAW, ETC.) HERE AS NEEDED ********
    try:
        print("Starting model sampling...")
        #fit the model with the the flat_model that was created prior
        # multilevel_fitted = multilevel_model.fit(
        #     draws=2000, inference_method='mcmc', random_seed=42, target_accept = .9, 
        #     idata_kwargs={"log_likelihood": True})
        # multilevel_fitted = multilevel_model.fit(idata_kwargs = {"log_likelihood": True})
        multilevel_fitted = multilevel_model.fit(draws=2000, idata_kwargs = {"log_likelihood": True})
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
    print('Saving Model Output to a File...')

    # Generate incremented filenames
    netcdf_filename = get_next_filename(folder_path, "multilevel-model-output", "nc")
    csv_filename = get_next_filename(folder_path, "multilevel-model-output-ordered", "csv")

    # Save the NetCDF file
    multilevel_fitted.to_netcdf(netcdf_filename)
    print(f'Output successfully saved as {netcdf_filename}')

    # Extract posterior summary
    summary = az.summary(multilevel_fitted)

    # Sort predictors by absolute mean effect size
    sorted_summary = summary.reindex(summary["mean"].abs().sort_values(ascending=False).index)

    # Save ordered model output to CSV
    sorted_summary.to_csv(csv_filename)
    print(f"Ordered model output saved as {csv_filename}!")

else:
    print("Cannot save output to a file.")

# 01 - All schools as random effects | ell_disability_group, otherwise fixed effects.
# 02 - Everything but school as random effects | ell_disability_group, otherwise fixed effects.
# 03 - Everything as random effects | high_school (including the intercept), no other schools.
# 04 - Everything as random effects | both high_school and middle_school (including the intercept).
# 05 - Model 04, run for twice as long.
# 06 - Model 03, run on the post-COVID data.
# 07 - Model 04, run for twice as long on the post-COVID data.
