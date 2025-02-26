################################################################################################
# Create a DAG
import networkx as nx
import matplotlib.pyplot as plt

# Create a directed graph
G = nx.DiGraph()

# Add edges based on the DAG structure
edges = [
    ("Teacher", "AC_Ind"),
    ("Teacher", "Grades"),
    ("Attendance", "Grades"),
    ("School", "Teacher"),
    ("School", "Grades"),
    ("School", "AC_Ind"),
    ("Disadvantage", "Grades"),
    ("Disadvantage", "Attendance"),
    ("Disadvantage", "AC_Ind"),
    ("Overall_GPA", "AC_Ind")
]

G.add_edges_from(edges)

# Draw the DAG
plt.figure(figsize=(10, 8))
pos = nx.shell_layout(G)  # Trying a shell layout for better separation
nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=3000, font_size=10)
plt.title("DAG for Advanced Coursework ASC Project")
plt.show()

################################################################################################
import pymc as pm
import pandas as pd

# Load in the dataset
df = pd.read_csv('data/modeling_data.csv', low_memory = False)

# import polars as pl
# import polars.selectors as cs
# 
# dfpl = pl.read_csv('data/modeling_data.csv')
# dfpl.group_by(pl.col(['exit_code_nan'])).agg(n = pl.len())
# dfpl.select(cs.contains('teacher')).columns
# dfpl = (dfpl
#     .with_columns(
#         pl.sum_horizontal(cs.contains('school')).alias('new')
#     )
# )
# dfpl.group_by(pl.col('new')).agg(n = pl.len())

# TODO: Keep columns to drop here or move to the end of the 07_combine_data-table script?
col_drop = ['student_number', 'days_attended', 'days_absent', 'school_membership', 
            'extended_school_year_y', 'environment_v', 'gender_f', 'hs_complete_status_ao',
            'hs_complete_status_ct', 'hs_complete_status_do', 'hs_complete_status_gc',
            'hs_complete_status_gg', 'hs_complete_status_gr', 'hs_complete_status_rt',
            # TODO: Update with changes Matt makes (see PR)
            'ell_entry_date', 'entry_date', 'first_enroll_us', 'test_date',
            'hs_complete_status_nan', 'tribal_affiliation_nan', 'exit_code_nan',
            'reading_intervention_y', 'read_grade_level_y'
]

# ell_disability_group is the group variable (currently a string)

########################################################################################################
# ******ONLY UNCOMMENT THE CODE BELOW IF YOU WOULD LIKE TO RUN THE MODEL WITH A SUBSET OF THE DATA******
########################################################################################################

# Set the sample fraction for the subset data
# sample_fraction = 0.1

# #establish the subset DF to test to see if the model is set up correctly
# subset_df = df[['student_number','ac_ind', 'overall_gpa', 'teacher_218966', 'english_score', 'ell_disability_group']]

# # Stratified sampling
# subset_df = subset_df.groupby("ell_disability_group", group_keys=False).apply(lambda x: x.sample(frac=sample_fraction, random_state=42))

# # Convert categorical group column to an array
# group_idx = subset_df["ell_disability_group"].astype("category").cat.codes.values
# group_names = subset_df["ell_disability_group"].astype("category").cat.categories.tolist()
# num_groups = len(group_names)

# # Predictor variables 
# X = subset_df.drop(columns=col_drop, axis=1).values
# predictor_names = subset_df.drop(columns=col_drop, axis=1).columns.tolist()
# num_predictors = len(predictor_names)

# # Outcome variable
# y = subset_df["ac_ind"].values 

#____________________________________________________________________________
                   #PREP THE MODEL ON THE FULL DATASET
#____________________________________________________________________________

# # Convert categorical group column to an array
group_idx = df["ell_disability_group"].astype("category").cat.codes.values
group_names = df["ell_disability_group"].astype("category").cat.categories.tolist()
num_groups = len(group_names)

# Predictor variables 
X = df.drop(columns=col_drop, axis=1).values
predictor_names = df.drop(columns=col_drop, axis=1).columns.tolist()
num_predictors = len(predictor_names)

# Outcome variable
y = df["ac_ind"].values 

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




