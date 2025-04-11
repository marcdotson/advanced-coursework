import pandas as pd
import bambi as bmb
import arviz as az
import os
import glob


########################################################
# SPECIFY WHAT MODEL TO RUN
########################################################

data_model_ind = 1          # Use the entire modeling data
data_post_covid_ind = 0     # Use the post-covid modeling data
group_high_school_ind = 1   # Group by high schools
group_middle_school_ind = 1 # Group by middle schools


########################################################
# LOAD IN THE DATASET AND ESTABLISH FOLDER PATH
########################################################

# Load in the data based on the indicators
if data_model_ind == 1:
    df = pd.read_csv('data/modeling_data.csv', low_memory = False)

if data_post_covid_ind == 1:
    df = pd.read_csv('data/post_covid_modeling_data.csv', low_memory = False)

# Define the folder path where the model output will be saved
folder_path = "output/"

# Check if the folder exists, and create it if not
if not os.path.exists(folder_path):
    os.makedirs(folder_path)


#######################################################
# PREP THE MODEL AND SPECIFY THE MODEL FORMULA
#######################################################

# Columns to exclude from modeling
col_drop = ['student_number', 'hs_advanced_math_y', 'tribal_affiliation_g']
for col in df.columns:
    if col.startswith('teacher') or col.startswith('exit') or col.startswith('envi'):
        col_drop.append(col)

# Filter students out from Cache High who have no high school assigned
# if group_high_school_ind == 1:
df = df[~df['high_school'].isin(['Cache High', '0'])]

# # Filter students who have no middle school assigned and drop more columns
# if group_middle_school_ind == 1:
#     df = df[~df['middle_school'].isin(['0'])]
# 
#     more_col_drop = ['gender_u', 'migrant_y', 'military_child_y', 
#         'refugee_student_y', 'homeless_y', 'part_time_home_school_y', 
#         'immigrant_y', 'tribal_affiliation_n', 'tribal_affiliation_p', 
#         'tribal_affiliation_s', 'tribal_affiliation_u']
# 
#     col_drop = col_drop + more_col_drop

# Define base data frame after dropping columns and specify predictors
df_base = df.drop(columns = col_drop, axis=1)
all_predictors = " + ".join(df_base.columns.difference(["ac_ind", "high_school", "middle_school"]))

# Specify the model formula
if group_high_school_ind == 1:
    model_formula = f"ac_ind ~ ({all_predictors} | high_school)"

if group_middle_school_ind == 1:
    model_formula = f"ac_ind ~ ({all_predictors} | middle_school) + ({all_predictors} | high_school)"


################################################
# RUN THE MULTILEVEL MODEL 
################################################

if __name__ == '__main__':
    print("Starting model setup...")

    # Establish the Multilevel Logistic Regression Model
    multilevel_model = bmb.Model(model_formula, df_base, family = "bernoulli", noncentered = True)
    
    # Apply the .build() method prior to fitting the model
    multilevel_model.build() 

    # Run the sampling (ADJUST THE AMOUNT OF SAMPLING (TUNE, DRAW, ETC.) HERE AS NEEDED)
    try:
        print("Starting model sampling...")
        
        if group_high_school_ind == 1:
            multilevel_fitted = multilevel_model.fit(idata_kwargs = {"log_likelihood": True})
        
        if group_middle_school_ind == 1:
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
# 08 - Model 03 without hs_advanced_math_y and with "Cache High" and "0" students filtered out.
# 09 - Model 06 without hs_advanced_math_y and with "Cache High" and "0" students filtered out.
