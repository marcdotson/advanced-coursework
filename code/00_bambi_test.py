
import pandas as pd
import bambi as bmb
import arviz as az
import os 


# Define the folder path where the trace plots will be saved
folder_path = "outputs/"

# Check if the folder exists, and create it if not
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Load in the dataset
df = pd.read_csv('data/modeling_data.csv', low_memory=False)


##################################################################################################################
#PREP THE MODEL AND SPECIFY COLUMNS TO DROP
##################################################################################################################

# Columns to exclude from modeling (THESE ARE THE COLUMNS FROM THE ANTECEDENT SCRIPT, THEY MAY NEED TO BE ADJUSTED)
col_drop = [
    'student_number', 'days_attended', 'days_absent', 'school_membership',
    'extended_school_year_y', 'environment_v', 'gender_f', 'hs_complete_status_ao',
    'hs_complete_status_ct', 'hs_complete_status_do', 'hs_complete_status_gc',
    'hs_complete_status_gg', 'hs_complete_status_gr', 'hs_complete_status_rt',
    'ell_entry_date', 'entry_date', 'first_enroll_us', 'test_date',
    'hs_complete_status_nan', 'tribal_affiliation_nan', 'exit_code_nan',
    'reading_intervention_y', 'read_grade_level_y', 'ell_disability_group'
]

# Define base dataframe after dropping columns
df_base = df.drop(columns=col_drop, axis=1)

# Extract potential predictors (excluding the target 'ac_ind')
all_predictors = " + ".join(df_base.columns.difference(["ac_ind"]))

#create the string formated model formula 
model_formula =  f"ac_ind ~ {all_predictors}"


################################################################################################
# RUN THE FLAT MODEL AND EXPORT DRAWS TO A FILE
################################################################################################

if __name__ == '__main__':
    print("Starting model setup...")

    #establish the flat Logistic Regression Model
    flat_model = bmb.Model(model_formula, df_base, family="bernoulli")
    # apply the .build() method prior to fitting the model
    flat_model.build() 

    # Run the sampling *******ADJUST THE AMOUNT OF SAMPLING (TUNE, DRAW, ETC.) HERE AS NEEDED ********
    try:
        print("Starting model sampling...")
        #fit the model with the the flat_model that was created prior
        flat_fitted = flat_model.fit(
            draws=2000, chains=4, tune=1000, target_accept=0.85, random_seed=42, idata_kwargs={"log_likelihood": True})
        print("Sampling complete.")

    except Exception as e:
        print(f"Sampling failed: {e}")
        flat_fitted = None  # Set output to None if sampling fails

    # Only try to export if it is not none
    if flat_fitted is not None:
        # Save trace to a NetCDF file
        print('Saving Model Trace to a File...')
        flat_fitted.to_netcdf("outputs/flat-model-output.nc")
        print('Trace successfully saved, look for it in the data folder')

        # Extract posterior summary to save sorted predictors to a csv
        summary = az.summary(flat_fitted)
       # Sort predictors by mean effect size (largest to smallest)
        sorted_summary = summary.reindex(summary["mean"].sort_values(ascending=False).index)
        # Save ordered model output to CSV
        sorted_summary.to_csv("outputs/flat-model-output-ordered.csv")
        print("Ordered model output saved successfully!")

    else:
        print("Trace is None, cannot save trace to a file.")

