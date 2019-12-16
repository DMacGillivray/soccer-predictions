import pathlib

from pfuncs import (get_filepaths,
                    read_csvs_to_dfs,
                    write_dfs_to_filepaths,
                    make_equiv_image_dest_fps)

PROJECT_DIR = pathlib.Path().cwd().resolve()

STACKED_DIR = PROJECT_DIR / 'data' / '06-stacked-seasons'
FEATURED_DIR = PROJECT_DIR / 'data' / '07-time-series-featured'


def apply_feature1(df):
    return df


def apply_feature2(df):
    return df


def apply_features(dfs):
    featured_dfs = []
    for df in dfs:
        df = apply_feature1(df)
        df = apply_feature2(df)
        featured_dfs.append(df)
    return featured_dfs


def apply_ts_features():
    filepaths = get_filepaths(STACKED_DIR, ext='csv')
    dfs = read_csvs_to_dfs(filepaths)
    featured_dfs = apply_features(dfs)
    featured_filepaths = make_equiv_image_dest_fps(STACKED_DIR,
                                                   FEATURED_DIR,
                                                   filepaths)
    n_saved = write_dfs_to_filepaths(featured_dfs, featured_filepaths)
    print(n_saved)


if __name__ == "__main__":
    apply_ts_features()
