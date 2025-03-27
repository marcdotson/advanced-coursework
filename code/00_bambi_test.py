import pandas as pd
import bambi as bmb
import arviz as az
import os
import matplotlib.pyplot as plt


# Define the folder path where the trace plots will be saved
folder_path = "output/"

# Check if the folder exists, and create it if not
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Load in the dataset
df = pd.read_csv('data/modeling_data.csv', low_memory=False)

# Define target and predictors
df = pd.get_dummies(df, drop_first= False)

##################################################################################################################
# PREP THE MODEL AND SPECIFY COLUMNS TO DROP
##################################################################################################################

# Columns to exclude from modeling
col_drop = ['student_number', 'ell_disability_group_non_ell_without_disability']

#add the teacher and exit codes to the dropped columns
for col in df.columns:
    if col.startswith('teacher') or col.startswith('exit'):
        col_drop.append(col)

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
            # draws=2000, chains=4, tune=1000, target_accept=0.85, random_seed=42, idata_kwargs={"log_likelihood": True})
            draws=2000, inference_method='mcmc', random_seed=42)
        print("Sampling complete.")

    except Exception as e:
        print(f"Sampling failed: {e}")
        flat_fitted = None  # Set output to None if sampling fails

    # Only try to export if it is not none
    if flat_fitted is not None:
        # Save trace to a NetCDF file
        print('Saving Model Trace to a File...')
        flat_fitted.to_netcdf("output/flat-model-output.nc")
        print('Trace successfully saved, look for it in the data folder')

        # Extract posterior summary to save sorted predictors to a csv
        summary = az.summary(flat_fitted)
       # Sort predictors by mean effect size (largest to smallest)
        sorted_summary = summary.reindex(summary["mean"].sort_values(ascending=False).index)
        # Save ordered model output to CSV
        sorted_summary.to_csv("output/flat-model-output-ordered.csv")
        print("Ordered model output saved successfully!")

    else:
        print("Trace is None, cannot save trace to a file.")

