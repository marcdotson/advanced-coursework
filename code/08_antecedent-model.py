import pandas as pd
import pymc as pm
import bambi as bmb
import arviz as az
import networkx as nx
import matplotlib.pyplot as plt

################################################################################################
# Create a DAG
G = nx.DiGraph()

# Add edges based on the DAG structure
edges = [
    ("Teacher", "AC_Ind"),
    ("Teacher", "Overall_GPA"),
    ("Attendance", "Overall_GPA"),
    ("School", "Teacher"),
    ("School", "Overall_GPA"),
    ("School", "AC_Ind"),
    ("Disadvantage", "Overall_GPA"),
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
# Load in the dataset
df = pd.read_csv('data/modeling_data.csv', low_memory = False)

import polars as pl
import polars.selectors as cs
import seaborn.objects as so

dfpl = pl.read_csv('data/modeling_data.csv')
dfpl.group_by(pl.col('hs_advanced_math_y')).agg(n = pl.len())

(so.Plot(dfpl, x="scram_membership")
    .add(so.Bars(), so.Hist())
)

dfpl = (dfpl
    .with_columns(
        pl.sum_horizontal(cs.contains('exit_code')).alias('new')
    )
)
dfpl.group_by(pl.col('new')).agg(n = pl.len())

col_drop = ['student_number']

# Convert categorical group column to an integer array
group_idx = df["ell_disability_group"].astype("category").cat.codes.values
group_names = df["ell_disability_group"].astype("category").cat.categories.tolist()

# Predictor variables
X = df.drop(columns=col_drop, axis=1).values
predictor_names = df.drop(columns=col_drop, axis=1).columns.tolist()

# Outcome variable
y = df["ac_ind"].values 

################################################################################################
# RUN A FLAT TEST MODEL FIRST (using Bambi)
df_new = df.drop(columns=col_drop, axis=1)

predictors_new = "+".join(df_new.columns.difference(["ac_ind"]))
formula_new = f"ac_ind ~ {predictors_new}"

flat_model = bmb.Model('ac_ind ~ ethnicity_y', df_new, family="bernoulli")
flat_model.build()


pymc_model = flat_model.backend.model


flat_fitted = flat_model.fit(
    draws=2000, target_accept=0.85, random_seed=42, idata_kwargs={"log_likelihood": True}
)

az.plot_trace(flat_fitted, combined = True)
az.plot_forest(flat_fitted, combined = True, hdi_prob=0.95) #kind = 'ridgeplot')

################################################################################################
# RUN THE MODEL AND EXPORT DRAWS TO A FILE
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

