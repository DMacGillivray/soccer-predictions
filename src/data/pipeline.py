# 01-raw to 02-scoped
from scope_football_data_co_uk import scope_football_data_co_uk
from scope_indatabet_com import scope_indatabet_com
from scope_whoscored_images import (scope_whoscored_heatmap_images,
                                    scope_whoscored_shotmap_images)

# 02-scoped to 03-cleaned
from clean_football_data_co_uk import clean_football_data_co_uk
from clean_indatabet_com import clean_indatabet_com
from clean_whoscored_images import (clean_whoscored_heatmap_images,
                                    clean_whoscored_shotmap_images)

# 03-cleaned to 04-standardized
from standardize_df_team_names import standardize_df_team_names
from standardize_image_team_names import standardize_image_sources

# 04-standardized to 05-joined
from standardized_to_joined_within_season import join_dfs_within_seasons
from stdzed_images_to_joined_within_season import join_images_within_seasons

# 05-joined to 06-stacked
from joined_df_to_stacked_seasons import stackseasons

# 06-stacked to 07-time-series-featured
from stacked_to_ts_featured import apply_ts_features

# 07-time-series-featured to 08-transformed
from transform_long_to_wide import run_transform_ts_to_supervised

# 08-transformed to 09-all-stacked
from transformed_to_all_stacked import transformed_to_all_stacked


def run_pipeline():
    scope_football_data_co_uk()
    scope_indatabet_com()
    scope_whoscored_heatmap_images()
    scope_whoscored_shotmap_images()
    clean_football_data_co_uk()
    clean_indatabet_com()
    clean_whoscored_heatmap_images()
    clean_whoscored_shotmap_images()
    standardize_df_team_names()
    standardize_image_sources()
    join_dfs_within_seasons()
    join_images_within_seasons()
    stackseasons()
    apply_ts_features()
    run_transform_ts_to_supervised()
    transformed_to_all_stacked()


if __name__ == "__main__":
    run_pipeline()
