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
group_high_school_ind = 0   # Group by high schools
group_middle_school_ind = 0 # Group by middle schools


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
# all_predictors = " + ".join(df_base.columns.difference(["ac_ind", "high_school", "middle_school"]))

# Specify the model formula
if group_high_school_ind == 1:
    all_predictors = " + ".join(df_base.columns.difference(["ac_ind", "high_school", "middle_school"]))
    model_formula = f"ac_ind ~ ({all_predictors} | high_school)"
    # model_formula = f"ac_ind ~ {all_predictors} + ({all_predictors} | high_school)"

elif group_middle_school_ind == 1:
    all_predictors = " + ".join(df_base.columns.difference(["ac_ind", "high_school", "middle_school"]))
    model_formula = f"ac_ind ~ ({all_predictors} | middle_school) + ({all_predictors} | high_school)"

else:
    # df_base = pd.get_dummies(df_base, columns=['high_school'], drop_first=False, dtype=int)
    # df_base = pd.get_dummies(df_base, columns=['middle_school'], drop_first=True, dtype=int)

    # df_base = df_base.rename(columns={
    #     'high_school_Green Canyon': 'high_school_Green_Canyon',
    #     'high_school_Mountain Crest': 'high_school_Mountain_Crest',
    #     'high_school_Sky View': 'high_school_Sky_View',
    #     'middle_school_North Cache Middle': 'middle_school_North_Cache_Middle',
    #     'middle_school_South Cache Middle': 'middle_school_South_Cache_Middle',
    #     'middle_school_Spring Creek Middle': 'middle_school_Spring_Creek_Middle'
    # })

    all_predictors = " + ".join(df_base.columns.difference(["ac_ind"]))
    model_formula = f"ac_ind ~ {all_predictors}"

################################################
# RUN THE MULTILEVEL MODEL 
################################################

if __name__ == '__main__':
    print("Starting model setup...")

    if group_high_school_ind == 1 or group_middle_school_ind == 1:
        # Establish the Multilevel Logistic Regression Model
        multilevel_model = bmb.Model(model_formula, df_base, family = "bernoulli", noncentered = True)
        
        # Apply the .build() method prior to fitting the model
        multilevel_model.build()

    else:
        # Establish the Flat Logistic Regression Model
        flat_model = bmb.Model(model_formula, df_base, family = "bernoulli")
        
        # Apply the .build() method prior to fitting the model
        flat_model.build()

    # Run the sampling (ADJUST THE AMOUNT OF SAMPLING (TUNE, DRAW, ETC.) HERE AS NEEDED)
    try:
        print("Starting model sampling...")
        
        # if group_high_school_ind == 1:
        #     multilevel_fitted = multilevel_model.fit(idata_kwargs = {"log_likelihood": True})
        #     # multilevel_fitted = multilevel_model.fit(draws=2000, idata_kwargs = {"log_likelihood": True})
        
        # if group_middle_school_ind == 1:
        #     multilevel_fitted = multilevel_model.fit(draws=2000, idata_kwargs = {"log_likelihood": True})
        
        if group_high_school_ind == 1 or group_middle_school_ind == 1:
            # multilevel_fitted = multilevel_model.fit(idata_kwargs = {"log_likelihood": True})
            multilevel_fitted = multilevel_model.fit(draws=2000, idata_kwargs = {"log_likelihood": True})

        else:
            flat_fitted = flat_model.fit(idata_kwargs = {"log_likelihood": True})

        print("Sampling complete.")

    except Exception as e:
        print(f"Sampling failed: {e}")

        if group_high_school_ind == 1 or group_middle_school_ind == 1:
            multilevel_fitted = None  # Set output to None if sampling fails

        else:
            flat_fitted = None        # Set output to None if sampling fails


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
if (group_high_school_ind == 1 or group_middle_school_ind == 1) and multilevel_fitted is not None:
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

if group_high_school_ind == 0 and group_middle_school_ind == 0 and flat_fitted is not None:
    print('Saving Model Output to a File...')

    # Generate incremented filenames
    netcdf_filename = get_next_filename(folder_path, "flat-model-output", "nc")
    csv_filename = get_next_filename(folder_path, "flat-model-output-ordered", "csv")

    # Save the NetCDF file
    flat_fitted.to_netcdf(netcdf_filename)
    print(f'Output successfully saved as {netcdf_filename}')

    # Extract posterior summary
    summary = az.summary(flat_fitted)

    # Sort predictors by absolute mean effect size
    sorted_summary = summary.reindex(summary["mean"].abs().sort_values(ascending=False).index)

    # Save ordered model output to CSV
    sorted_summary.to_csv(csv_filename)
    print(f"Ordered model output saved as {csv_filename}!")

else:
    print("Cannot save output to a file.")

# Flat Models:
# 01 - Original flat model.
# 02 - Flat model that corresponds with Multilevel Model 08.
# 05 - Flat model that corresponds with Multilevel Model 09.
# 06 - Flat Model 02 but with high and middle schools as fixed effects (Green Canyon and 0 as references).

# Multilevel Models:
# 01 - All schools as random effects | ell_disability_group, otherwise fixed effects.
# 02 - Everything but school as random effects | ell_disability_group, otherwise fixed effects.
# 03 - Everything as random effects | high_school (including the intercept), no other schools.
# 04 - Everything as random effects | both high_school and middle_school (including the intercept).
# 05 - 04 run for twice as long.
# 06 - 03 run on the post-COVID data.
# 07 - 04 run for twice as long on the post-COVID data.
# 08 - 03 without hs_advanced_math_y and with "Cache High" and "0" students filtered out.
# 09 - 08 run on the post-COVID data.
# 10 - 08 as a mixed effect model, including all predictors as both fixed and random effects.
# 11 - 10 run for twice as long.

