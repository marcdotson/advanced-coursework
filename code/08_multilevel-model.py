#____________________________________________________________________________
                             #IMPORT LIBRARIES
#____________________________________________________________________________ 
import pymc as pm
import pandas as pd

#____________________________________________________________________________ 
                              #LOAD IN THE DATA
#____________________________________________________________________________ 
#load in the dataset
df = pd.read_csv('data/modeling_data.csv')

#____________________________________________________________________________
                          #SPECIFY COLUMNS TO DROP
#____________________________________________________________________________

#columns to drop later prior to modeling ADD MORE AS NECCESSARY
col_drop = ['student_number', 'ac_ind', 'ell_disability_group']

#____________________________________________________________________________
                 #PREP THE MODEL ON A SUBSET OF THE DATA
#____________________________________________________________________________

########################################################################################################
# ******ONLY UNCOMMENT THE CODE BELOW IF YOU WOULD LIKE TO RUN THE MODEL WITH A SUBSET OF THE DATA******
########################################################################################################

# Set the sample fraction for the subset data
sample_fraction = 0.1

#establish the subset DF to test to see if the model is set up correctly
subset_df = df[['student_number','ac_ind', 'overall_gpa', 'teacher_218966', 'english_score', 'ell_disability_group']]

# Stratified sampling
subset_df = subset_df.groupby("ell_disability_group", group_keys=False).apply(lambda x: x.sample(frac=sample_fraction, random_state=42))

# Convert categorical group column to an array
group_idx = subset_df["ell_disability_group"].astype("category").cat.codes.values
group_names = subset_df["ell_disability_group"].astype("category").cat.categories.tolist()
num_groups = len(group_names)

# Predictor variables 
X = subset_df.drop(columns=col_drop, axis=1).values
predictor_names = subset_df.drop(columns=col_drop, axis=1).columns.tolist()
num_predictors = len(predictor_names)

# Outcome variable
y = subset_df["ac_ind"].values 

#____________________________________________________________________________
                   #PREP THE MODEL ON THE FULL DATASET
#____________________________________________________________________________

# # Convert categorical group column to an array
# group_idx = df["ell_disability_group"].astype("category").cat.codes.values
# group_names = df["ell_disability_group"].astype("category").cat.categories.tolist()
# num_groups = len(group_names)

# # Predictor variables 
# X = df.drop(columns=col_drop, axis=1).values
# predictor_names = df.drop(columns=col_drop, axis=1).columns.tolist()
# num_predictors = len(predictor_names)

# # Outcome variable
# y = df["ac_ind"].values 

#____________________________________________________________________________
                    #RUN THE MODEL AND EXPORT TRACE TO A FILE
#____________________________________________________________________________
if __name__ == '__main__':
    print("Starting model setup...")

    #set up and create the model
    with pm.Model(coords={"group": group_names, "predictor": predictor_names}) as model:
        # Group-level intercepts (varying by ELL-Disability group)
        mu_a = pm.Normal("mu_a", mu=0, sigma=1)                   # Hyperprior for intercept mean
        sigma_a = pm.Exponential("sigma_a", 1)                    # Hyperprior for variance
        a = pm.Normal("a", mu=mu_a, sigma=sigma_a, dims = 'group')  # Varying intercepts for groups

         # Group-level slopes
        mu_b = pm.Normal("mu_b", mu=0, sigma=1, dims="predictor")  
        sigma_b = pm.Exponential("sigma_b", 1, dims="predictor")  
        b = pm.Normal("b", mu=mu_b, sigma=sigma_b, dims=("group", "predictor"))  # Use both coordinates

        # Linear predictor (logit model)
        logit_p = a[group_idx] + pm.math.sum(b[group_idx] * X, axis=1)

        # Sigmoid transformation to convert log-odds to probability
        p = pm.Deterministic("p", pm.math.sigmoid(logit_p))

        # Likelihood (Bernoulli response)
        y_obs = pm.Bernoulli("y_obs", p=p, observed=y)

        # Run the sampling *******ADJUST THE AMOUNT OF SAMPLING (TUNE) HERE AS NEEDED ********
        try:
            print("Starting model sampling...")
            trace = pm.sample(2000, tune=2000, target_accept=0.95, return_inferencedata=True)
            print("Sampling complete.")

        except Exception as e:
            print(f"Sampling failed: {e}")
            trace = None  # Set trace to None if sampling fails

        # Only try to export the trace if it is not none
        if trace is not None:
            # Assign coordinate names before saving
            trace = trace.assign_coords(group=group_names, predictor=predictor_names)
            
            # Save trace to a NetCDF file
            print('Saving Trace File...')
            trace.to_netcdf("data/trace_output.nc")
            print('File successfully saved, look for it in the data folder')

        else:
            print("Trace is None, cannot save trace to a file.")




