import polars as pl
import pandas as pd

all_teachers = pl.read_csv('./data/all_teacher_grid.csv')
non_ac_teachers = pl.read_csv('./data/non_ac_teacher_grid.csv')
sky_view = pl.read_csv('./data/sky_view_non_ac_teacher_grid.csv')
green_canyon = pl.read_csv('./data/green_canyon_non_ac_teacher_grid.csv')
ridgeline = pl.read_csv('./data/ridgeline_non_ac_teacher_grid.csv')
mountain_crest = pl.read_csv('./data/mountain_crest_non_ac_teacher_grid.csv')
cache_high = pl.read_csv('./data/cache_high_non_ac_teacher_grid.csv')
spring_creek_middle = pl.read_csv('./data/spring_creek_middle_non_ac_teacher_grid.csv')
north_cache_middle = pl.read_csv('./data/north_cache_middle_non_ac_teacher_grid.csv')
south_cache_middle = pl.read_csv('./data/south_cache_middle_non_ac_teacher_grid.csv')

data_frames = [
    all_teachers, non_ac_teachers, sky_view, green_canyon, ridgeline, 
    mountain_crest, cache_high, spring_creek_middle, north_cache_middle, south_cache_middle
]
target_columns = ['ac_ind'] * len(data_frames)
sheet_names = [
    'all_teachers', 'non_ac_teachers', 'sky_view', 'green_canyon', 'ridgeline', 
    'mountain_crest', 'cache_high', 'spring_creek_middle', 'north_cache_middle', 'south_cache_middle'
]

def compute_correlation(df, target_column):
    numeric_df = df.select(pl.all().exclude('student_number')).to_pandas()
    corr_matrix = numeric_df.corr()

    if target_column not in corr_matrix:
        return pl.DataFrame({'Variable': [], target_column: []})

    corr_with_target = pl.from_pandas(
        corr_matrix.reset_index().rename(columns={"index": "Variable"})
    ).select(['Variable', target_column])

    return corr_with_target.sort(target_column, descending=True)

with pd.ExcelWriter('data/teacher_correlations.xlsx') as writer:
    sheet_written = False
    for df, target_column, sheet_name in zip(data_frames, target_columns, sheet_names):
        corr_data = compute_correlation(df, target_column)

        if not corr_data.is_empty():
            corr_data.to_pandas().to_excel(writer, sheet_name=sheet_name, index=False)
            sheet_written = True
        else:
            print(f"Correlation data for '{sheet_name}' is empty and was skipped.")

    if not sheet_written:
        raise ValueError("No sheets were written. All correlation data were empty.")

