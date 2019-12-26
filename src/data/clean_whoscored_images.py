import pathlib
import sys

PROJECT_DIR = pathlib.Path.cwd().resolve()
sys.path.append(str(PROJECT_DIR))

from pfuncs import (get_filepaths,
                    make_equiv_image_dest_fps,
                    copy_files) # noqa E402

SCOPED_DIR = PROJECT_DIR / 'data' / '02-scoped'
CLEANED_DIR = PROJECT_DIR / 'data' / '03-cleaned'


def clean_image(image):
    """
    Placeholder
    """
    return image


def clean_up_images(images):
    clean_images = []
    for image in images:
        image = clean_image(image)
        images.append(image)
    return clean_images


def clean_whoscored_heatmap_images():
    image_dir = 'whoscored-com-heatmaps'
    filepaths = get_filepaths(SCOPED_DIR / image_dir, ext='png')

    # clean_images = clean_up_images(images)
    # cleaned_filepaths = make_filepaths_from_images(CLEANED_DIR,
    #                                                clean_images,
    #                                                data_origin=image_dir)
    # n_written = write_images_to_filepaths(clean_images, clean_filepaths)

    dest_fps = make_equiv_image_dest_fps(SCOPED_DIR,
                                         CLEANED_DIR,
                                         filepaths)
    n_copied = copy_files(filepaths, dest_fps)
    print(n_copied)


def clean_whoscored_shotmap_images():
    image_dir = 'whoscored-com-shotmaps'
    filepaths = get_filepaths(SCOPED_DIR / image_dir, ext='png')

    # clean_images = clean_up_images(images)
    # cleaned_filepaths = make_filepaths_from_images(CLEANED_DIR,
    #                                                clean_images,
    #                                                data_origin=image_dir)
    # n_written = write_images_to_filepaths(clean_images, clean_filepaths)

    dest_fps = make_equiv_image_dest_fps(SCOPED_DIR,
                                         CLEANED_DIR,
                                         filepaths)
    n_copied = copy_files(filepaths, dest_fps)
    print(n_copied)


if __name__ == "__main__":
    clean_whoscored_heatmap_images()
    clean_whoscored_shotmap_images()
