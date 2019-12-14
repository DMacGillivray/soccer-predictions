import pathlib
import pickle

from pfuncs import (get_filepaths,
                    copy_files)

PROJECT_DIR = pathlib.Path().cwd().resolve()
CLEANED_DIR = PROJECT_DIR / 'data' / '03-cleaned'
STDZED_DIR = PROJECT_DIR / 'data' / '04-standardized'
REF_DIR = PROJECT_DIR / 'data' / 'reference'


def get_std_dict_from_path(fp, std_dict_top_dir):
    # '/media/david/5C14F53A14F517AA/code/ana_py37/projects/soccer-predictions
    # /data/03-cleaned/whoscored-com-shotmaps/england/english-premier-league/
    # 2009-2010/Arsenal__Aston Villa.png')
    fp_parts = str(fp).split('/')
    nation = fp_parts[-4]
    league = fp_parts[-3]
    fn = league + '.pkl'
    fp = std_dict_top_dir / nation / league / fn
    try:
        with open(fp, 'rb') as handle:
            std_dict = pickle.load(handle)
    except IOError:
        std_dict = {'key': 'value'}
    return std_dict


def standardize_team_names_on_fp(fp, std_names_dict):
    # dest_fps = []
    # Change to create parallel list, and then copy across with standard names
    # ######################## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ###############
    # for heatmap_fp in heatmap_fps:
    #     print(heatmap_fp)
    if std_names_dict == {'key': 'value'}:
        fn = None
    else:
        h = str(fp).split('__')[0].split('/')[-1].lower().replace(' ', '-')
        a = str(fp).split('__')[1].split('/')[0].split('.')[0].lower()\
            .replace(' ', '-')
        if h in std_names_dict.keys():
            h = std_names_dict[h]
        if a in std_names_dict.keys():
            a = std_names_dict[a]
        fn = h + '__' + a + fp.suffix
    return fn


def standardize_filenames(src_fps, std_dict_top_dir):
    stdzed_fns = []
    for fp in src_fps:
        std_dict = get_std_dict_from_path(fp, std_dict_top_dir)
        fn = standardize_team_names_on_fp(fp, std_dict)
        stdzed_fns.append(fn)
    return stdzed_fns


def standardize_filepaths(cleaned_src_fps,
                          stdzed_fns,
                          dest_top_dir,
                          source_dir):
    # '/media/david/5C14F53A14F517AA/code/ana_py37/projects/soccer-predictions/data/
    # 03-cleaned/whoscored-com-shotmaps/england/english-premier-league/2009-2010
    # /Arsenal__Aston Villa.png'
    # stdzed_fn = 'arsenal__aston-villa.png'
    stdzed_dest_fps = []
    for cleaned_src_fp, stdzed_fn in zip(cleaned_src_fps, stdzed_fns):
        if stdzed_fn is None:
            stdzed_dest_fp = False
        else:
            fp_parts = str(cleaned_src_fp).split('/')
            nation = fp_parts[-4]
            league = fp_parts[-3]
            season = fp_parts[-2]
            stdzed_dest_fp = (dest_top_dir / source_dir / nation / league /
                              season / stdzed_fn)
            # print(fp)
            # Compile dest file path
        stdzed_dest_fps.append(stdzed_dest_fp)
    return stdzed_dest_fps


def standardize_image_team_names(source_dir):
    cleaned_src_fps = get_filepaths(CLEANED_DIR / source_dir, ext='png')
    stdzed_fns = standardize_filenames(cleaned_src_fps, REF_DIR)
    stdzed_dest_fps = standardize_filepaths(cleaned_src_fps,
                                            stdzed_fns,
                                            STDZED_DIR,
                                            source_dir)
    # Because not all the standardized dictionaries are available
    # We only want to copy images that have actually been standardized
    cleaned_src_fps = [src_fp for src_fp, dest_fp in zip(cleaned_src_fps,
                       stdzed_dest_fps) if dest_fp is not False]
    stdzed_dest_fps = [dest_fp for src_fp, dest_fp in zip(cleaned_src_fps,
                       stdzed_dest_fps) if dest_fp is not False]
    n_copied = copy_files(cleaned_src_fps, stdzed_dest_fps)
    print(n_copied)


if __name__ == "__main__":
    for source_dir in ['whoscored-com-heatmaps', 'whoscored-com-shotmaps']:
        standardize_image_team_names(source_dir)
