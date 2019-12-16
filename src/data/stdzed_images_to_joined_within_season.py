import pathlib

from pfuncs import (get_filepaths,
                    read_csvs_to_dfs,
                    write_dfs_to_filepaths,
                    make_filepaths_from_dfs,
                    make_equiv_image_dest_fps,
                    copy_files)

PROJECT_DIR = pathlib.Path().cwd().resolve()
STDZED_DIR = PROJECT_DIR / 'data' / '04-standardized'
JOINED_DIR = PROJECT_DIR / 'data' / '05-joined'
REF_DIR = PROJECT_DIR / 'data' / 'reference'


def form_image_fp(row, image_type=None):
    row = row.copy(deep=True)
    nation = row['nation']
    league = row['league']
    season = row['season']
    h = row['h']
    a = row['a']
    fn = h + '__' + a + '.png'
    rel_path = str(pathlib.Path(nation) / league / season / image_type / fn)
    return rel_path


def insert_filepaths(dfs, image_type):
    for df in dfs:
        df[image_type] = df.apply(form_image_fp, image_type=image_type, axis=1)
    return dfs


# def check_filepath_exists(dfs, source_dir, image_type):
#     for df in dfs:
#         df[image_type] = df.apply(check_image_fp,
#  image_type=image_type, axis=1)


def insert_rel_path_into_dfs(image_type):
    filepaths = get_filepaths(JOINED_DIR)
    df_origs = read_csvs_to_dfs(filepaths)
    dfs = insert_filepaths(df_origs, image_type)
    return dfs


def make_merged_image_filepaths(existing_image_fps, top_dir, image_type):
    new_image_fps = make_equiv_image_dest_fps(STDZED_DIR, JOINED_DIR,
                                              existing_image_fps)
    new_image_fps1 = [str(fp).replace(top_dir, '').split('/') for
                      fp in new_image_fps]
    [(fp.insert(-1, image_type)) for fp in new_image_fps1]
    final_image_fps = [pathlib.Path('/'.join(fp)) for fp in new_image_fps1]
    return final_image_fps


def update_for_image_file_exists(df_origs, image_type):
    updated_dfs = []
    for df_orig in df_origs:
        df = df_orig.copy(deep=True)
        mask = [pathlib.Path(JOINED_DIR / val).exists() for
                val in df[image_type].values]*1
        df[image_type + '_exists'] = mask
        df[image_type + '_exists'] = df[image_type + '_exists'].astype(int)
        updated_dfs.append(df)
    return updated_dfs


def join_images_within_seasons():
    image_types = ['heatmap', 'shotmap']
    for image_type in image_types:
        dfs = insert_rel_path_into_dfs(image_type)
        top_dir = 'whoscored-com-' + image_type + 's'
        existing_image_fps = get_filepaths(STDZED_DIR / top_dir, ext='png')
        new_image_fps = make_merged_image_filepaths(existing_image_fps,
                                                    top_dir,
                                                    image_type)
        n_copied = copy_files(existing_image_fps, new_image_fps)
        print(n_copied)
        updated_dfs = update_for_image_file_exists(dfs, image_type)
        save_fps = make_filepaths_from_dfs(JOINED_DIR, updated_dfs, '')
        n_written = write_dfs_to_filepaths(updated_dfs, save_fps)
        print(n_written)


if __name__ == "__main__":
    join_images_within_seasons()
