import pandas as pd
import numpy as np
import os

# XXX: Do we want to change the hs names to numerical values or leave them as strings?

# Import the clearinghouse data to the eda and model data
clearinghouse_df = pd.read_csv(os.path.join('../data', 'cleaned-clearinghouse-data.csv'))
clearinghouse_df.rename(columns={'Student_ID': 'student_number'}, inplace=True)
# clearinghouse_df.info()
# clearinghouse_df.head()

# # Read in the eda data
# eda_df = pd.read_csv('../data/exploratory_data.csv')
# print(f"Unique student_numbers in clearinghouse_df: {clearinghouse_df['student_number'].nunique()}")
# print(f"Unique student_numbers in eda_df: {eda_df['student_number'].nunique()}")
# print(f"Number of duplicated student_numbers in eda_df: {eda_df['student_number'].duplicated().sum()}")
# eda_df.info()
# eda_df.head()
# TODO : Join the Clearinghouse Data to the EDA Data
# FIXME: Troubleshoot EDA data duplicates

# # Combine the clearinghouse data to the eda data
# try:
#     eda_merged_df = pd.merge(eda_df, clearinghouse_df, on='student_number', how='left')
#     print("EDA data merged with clearinghouse data successfully")
#     print(eda_merged_df.head())
# except:
#     print("EDA data merged with clearinghouse data failed")
# XXX : Figure out why merging creates duplicates

# Combine the clearinghouse data to the model data
model_df = pd.read_csv(os.path.join('../data', 'modeling_data.csv'))
try:
    merged_model_df = pd.merge(model_df, clearinghouse_df, on='student_number', how='left')
    print("Model data merged with clearinghouse data successfully")
    print(merged_model_df.head())
    merged_model_df.to_csv(os.path.join('../data', 'merged_modeling_data.csv'), index=False)
except:
    print("Model data merged with clearinghouse data failed")