#____________________________________________________________________________
                             #IMPORT LIBRARIES
#____________________________________________________________________________ 
import arviz as az
import pandas as pd
#____________________________________________________________________________ 
                     #LOAD IN THE MODEL OUTPUT/ DATASET
#____________________________________________________________________________ 

# Load trace from the NetCDF file
try:
    trace = az.from_netcdf("data/trace_output.nc")
    df = pd.read_csv("data/modeling_data.csv")
except Exception as e:
    print(f"Loading Data failed: {e}")

#____________________________________________________________________________
                           #
#____________________________________________________________________________
# Store the summary statistics for the trace
summary = az.summary(trace, hdi_prob=0.95)

#columns that were dropped from the model **** MAKE SURE THIS MATCHES ANY COLUMNS DROPPED FROM THE MODELING SCRIPT****
col_drop = ['student_number', 'ac_ind', 'ell_disability_group', 'ell_disability_index']

# map out our predictor names and group names for better interpretability
predictor_names = df.drop(columns = col_drop, axis = 1).columns.tolist()

#{0: 'ell_with_disability', 1: 'ell_without_disability', 2: 'non_ell_with_disability', 3: 'non_ell_without_disability'}
group_labels = dict(enumerate(df["ell_disability_group"].astype("category").cat.categories))

az.summary(trace, hdi_prob=0.95)

