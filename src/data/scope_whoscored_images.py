import pathlib

from pfuncs import load_pickle, copy_files

PROJECT_DIR = pathlib.Path().cwd().resolve()

RAW_DIR = PROJECT_DIR / 'data' / '01-raw'
SCOPED_DIR = PROJECT_DIR / 'data' / '02-scoped'
SCOPE_DICT_DIR = PROJECT_DIR / 'data' / 'reference' / 'scope-dict'


def make_whoscored_image_src_fps(top_level_dir,
                                 scope_data,
                                 image_type='game-heatmaps'):
    src_fps = []
    for nation, league in zip(scope_data['nations'], scope_data['leagues']):
        for season in scope_data['seasons']:
            src_stub = (top_level_dir / 'football-data' / nation / league /
                        season / 'who-scored-com')
            src_dir = src_stub / image_type
            src_fp_sublist = list(src_dir.glob('*.png'))
            if src_dir.exists() and len(src_fp_sublist) > 0:
                src_fps.extend(src_fp_sublist)
    return src_fps


def make_whoscored_image_dest_fps(src_top_level_dir,
                                  dest_top_level_dir,
                                  src_fps,
                                  image_type='game-heatmaps'):
    # src looks like
    # /media/david/5C14F53A14F517AA/code/ana_py37/projects/soccer-predictions/data
    # /01-raw/football-data/germany/bundesliga/2009-2010/who-scored-com/
    # game-heatmaps/Bayern__Bochum.png

    # dest shoulkd look like
    # '/media/david/5C14F53A14F517AA/code/ana_py37/projects/soccer-predictions/data
    # /02-scoped/whoscored-com-heatmaps/germany/bundesliga/2009-2010/Bayern__Bochum.png'
    dest_fps = []
    for src_fp in src_fps:
        src_fp_parts = str(src_fp).split('/')
        source_parts = src_fp_parts[-3].split('-')
        source = source_parts[0] + source_parts[1] + '-' + \
            source_parts[-1] + '-' + image_type.split('-')[-1]
        nation = src_fp_parts[-6]
        league = src_fp_parts[-5]
        season = src_fp_parts[-4]
        dest_fp = (dest_top_level_dir / source / nation /
                   league / season / src_fp.name)
        dest_fps.append(dest_fp)
    return dest_fps


def scope_whoscored_heatmap_images():
    image_type = 'game-heatmaps'

    scope_dict = load_pickle(SCOPE_DICT_DIR)
    src_fps = make_whoscored_image_src_fps(RAW_DIR,
                                           scope_dict,
                                           image_type=image_type)
    dest_fps = make_whoscored_image_dest_fps(RAW_DIR,
                                             SCOPED_DIR,
                                             src_fps,
                                             image_type=image_type)
    n_copied = copy_files(src_fps, dest_fps)
    print(n_copied)


def scope_whoscored_shotmap_images():
    image_type = 'game-shotmaps'

    scope_dict = load_pickle(SCOPE_DICT_DIR)
    src_fps = make_whoscored_image_src_fps(RAW_DIR,
                                           scope_dict,
                                           image_type=image_type)
    dest_fps = make_whoscored_image_dest_fps(RAW_DIR,
                                             SCOPED_DIR,
                                             src_fps,
                                             image_type=image_type)
    n_copied = copy_files(src_fps, dest_fps)
    print(n_copied)


if __name__ == "__main__":
    scope_whoscored_heatmap_images()
    scope_whoscored_shotmap_images()
