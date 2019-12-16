# -*- coding: utf-8 -*-
import pathlib

import pandas as pd

from pfuncs import (get_filepaths,
                    read_csvs_to_dfs,
                    write_dfs_to_filepaths)

PROJECT_DIR = pathlib.Path().cwd().resolve()
TRANSFORMED_DIR = PROJECT_DIR / 'data' / '08-transformed'
ALL_STACKED_DIR = PROJECT_DIR / 'data' / '09-all-stacked'


def transformed_to_all_stacked():
    filepaths = get_filepaths(TRANSFORMED_DIR, ext='csv')
    dfs = read_csvs_to_dfs(filepaths)
    dfs = [pd.concat(dfs, axis=1, sort=True)]
    filepaths = [ALL_STACKED_DIR / 'full.csv']
    n_written = write_dfs_to_filepaths(dfs, filepaths)
    print(n_written)


if __name__ == "__main__":
    transformed_to_all_stacked()
