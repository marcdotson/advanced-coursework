import pandas as pd
import bambi as bmb
import arviz as az
import os
import glob


########################################################
# SPECIFY WHAT MODEL TO RUN
########################################################

# post_covid_data_ind = 0  # Only use the post-covid data
multilevel_model_ind = 0   # Run a multilevel model
college_grad_model_ind = 1 # Run a model for college graduation


########################################################
# LOAD IN THE DATASET AND ESTABLISH FOLDER PATH
########################################################

# Load in the data based on the indicators
# if post_covid_data_ind == 1:
#     df = pd.read_csv('data/post_covid_modeling_data.csv', low_memory = False)
# else:
df = pd.read_csv('data/clearinghouse_model_data.csv', low_memory = False)

# Define the folder path where the model output will be saved
folder_path = "output/"

# Check if the folder exists, and create it if not
if not os.path.exists(folder_path):
    os.makedirs(folder_path)


#######################################################
# PREP THE MODEL AND SPECIFY THE MODEL FORMULA
#######################################################

# Columns to exclude from modeling
col_drop = ['Unnamed: 0', 'student_number', 'hs_advanced_math_y', 'tribal_affiliation_g', 'year', 'passed_civics_exam_y']
for col in df.columns:
    if col.startswith('teacher') or col.startswith('exit') or col.startswith('envi'):
        col_drop.append(col)

# Filter students out from Cache High who have no high school assigned
df = df[~df['high_school'].isin(['Cache High', '0'])]

# Define base data frame after dropping columns and specify predictors
df_base = df.drop(columns = col_drop, axis=1)

# Specify the model formula
if multilevel_model_ind == 1:
    all_predictors = " + ".join(df_base.columns.difference(["start_college_y", "college_grad_y","high_school"]))
    if college_grad_model_ind == 1:
        model_formula = f"college_grad_y ~ ({all_predictors} | high_school)"
    else:
        model_formula = f"start_college_y ~ ({all_predictors} | high_school)"
else:
    all_predictors = " + ".join(df_base.columns.difference(["start_college_y", "college_grad_y"]))
    if college_grad_model_ind == 1:
        model_formula = f"college_grad_y ~ {all_predictors}"
    else:
        model_formula = f"start_college_y ~ {all_predictors}"


################################################
# RUN THE MODEL 
################################################

if __name__ == '__main__':
    print("Starting model setup...")

    # Specify the model
    if multilevel_model_ind == 1:
        effects_model = bmb.Model(model_formula, df_base, family = "bernoulli", noncentered = True)
    else:
        effects_model = bmb.Model(model_formula, df_base, family = "bernoulli")
        
    # Build the model
    effects_model.build()

    # Run the sampling (ADJUST THE AMOUNT OF SAMPLING (TUNE, DRAW, ETC.) HERE AS NEEDED)
    try:
        print("Starting model sampling...")
        
        if multilevel_model_ind == 1:
            model_fitted = effects_model.fit(tune=2000, draws=2000, idata_kwargs = {"log_likelihood": True})
        else:
            model_fitted = effects_model.fit(tune=3000, draws=3000, idata_kwargs = {"log_likelihood": True})

        print("Sampling complete.")

    except Exception as e:
        print(f"Sampling failed: {e}")
        model_fitted = None


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
if model_fitted is not None:
    print('Saving Model Output to a File...')

    # Generate incremented filenames
    if multilevel_model_ind == 1:
        filename_nc = "multilevel-model-output"
        filename_csv = "multilevel-model-output-ordered"
    else:
        filename_nc = "flat-model-output"
        filename_csv = "flat-model-output-ordered"
    
    netcdf_filename = get_next_filename(folder_path, filename_nc, "nc")
    csv_filename = get_next_filename(folder_path, filename_csv, "csv")

    # Save the NetCDF file
    model_fitted.to_netcdf(netcdf_filename)
    print(f'Output successfully saved as {netcdf_filename}')

    # Extract posterior summary
    summary = az.summary(model_fitted)

    # Sort predictors by absolute mean effect size
    sorted_summary = summary.reindex(summary["mean"].abs().sort_values(ascending=False).index)

    # Save ordered model output to CSV
    sorted_summary.to_csv(csv_filename)
    print(f"Ordered model output saved as {csv_filename}!")

else:
    print("Cannot save output to a file.")

# Flat Models:
# 03 - Original flat effects model.
# 04 - Flat model 03 run for longer.
# 08 - Flat model of start_college_y with advanced course categories.
# 09 - Flat model of college_grad_y with advanced course categories.
# 13 - Flat model of start_college_y with advanced course categories and passed_civics_exam_y removed.
# 14 - Flat model of college_grad_y with advanced course categories and passed_civics_exam_y removed.
# 15 - 2025 Update: Flat model of start_college_y with advanced course categories and passed_civics_exam_y removed.
# 16 - 2025 Update: Flat model of college_grad_y with advanced course categories and passed_civics_exam_y removed.

# Final Models:
# Full Dataset: Flat Models 13 and 14.
# 2025 Update: Full Dataset: Flat Models 15 and 16.

