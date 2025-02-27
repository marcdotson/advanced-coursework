
import pandas as pd
import bambi as bmb
import arviz as az

# Load in the dataset
df = pd.read_csv('data/modeling_data.csv', low_memory=False)

# Columns to exclude from modeling
col_drop = [
    'student_number', 'days_attended', 'days_absent', 'school_membership',
    'extended_school_year_y', 'environment_v', 'gender_f', 'hs_complete_status_ao',
    'hs_complete_status_ct', 'hs_complete_status_do', 'hs_complete_status_gc',
    'hs_complete_status_gg', 'hs_complete_status_gr', 'hs_complete_status_rt',
    'ell_entry_date', 'entry_date', 'first_enroll_us', 'test_date',
    'hs_complete_status_nan', 'tribal_affiliation_nan', 'exit_code_nan',
    'reading_intervention_y', 'read_grade_level_y', 'ell_disability_group'
]

# Define base dataframe (without excluded columns)
df_base = df.drop(columns=col_drop, axis=1)

# Extract potential predictors (excluding the target 'ac_ind')
all_predictors = df_base.columns.difference(["ac_ind"]).tolist()

# Set batch size (how many columns to add per iteration)
batch_size = 5

if __name__ == '__main__':
    print("Starting model iteration...")

    # Iterate over additional columns in batches
    for i in range(0, len(all_predictors), batch_size):
        # Select next batch of five columns
        current_batch = all_predictors[i:i + batch_size]  # Only tests 5 at a time
        predictors_str = " + ".join(current_batch)
        formula_new = f"ac_ind ~ {predictors_str}"

        print(f"\n🔹 Testing model with {len(current_batch)} predictors: {current_batch}")

        # Define and build Bambi model
        flat_model = bmb.Model(formula_new, df_base, family="bernoulli")
        flat_model.build()

        # Fit the model
        flat_fitted = flat_model.fit(
            draws=500, target_accept=0.85, random_seed=42, idata_kwargs={"log_likelihood": True}
        )

        # Plot results
        az.plot_trace(flat_fitted, combined=True)
        az.plot_forest(flat_fitted, combined=True, hdi_prob=0.95)

        print(f"✅ Completed iteration {i//batch_size + 1} with {len(current_batch)} predictors.")

    print("\nAll iterations complete!")
