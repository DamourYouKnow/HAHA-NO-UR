import os
import posixpath
import urllib.parse
import aiohttp
from PIL import Image

IDOL_IMAGES_PATH = 'idol_images/'
OUTPUT_PATH = 'scout_output/'
CIRCLE_DISTANCE = 10


async def create_image(
        idol_circle_urls: list, num_rows: int, output_filename: str) -> str:
    """
    Creates a stitched together image of idol circles.

    :param idol_circle_urls: urls of idol circle images to be stitched together.
    :param num_rows: Number of rows to use in the image
    :param output_filename: name of output image file

    :return: path pointing to created image
    """
    image_filepaths = []  # list of image filepaths

    # Save images that do not exists
    for image_url in idol_circle_urls:
        url_path = urllib.parse.urlsplit(image_url).path
        filename = posixpath.basename(url_path)
        image_filepaths.append(IDOL_IMAGES_PATH + filename)

        await download_image_from_url(image_url, IDOL_IMAGES_PATH + filename)

    # Load images
    circle_images = []
    for image_filepath in image_filepaths:
        circle_images.append(Image.open(image_filepath))

    image = await _build_image(circle_images, num_rows, 10, 10)

    image.save(OUTPUT_PATH + output_filename, 'PNG')
    return OUTPUT_PATH + output_filename


async def download_image_from_url(url: str, path: str) -> str:
    """
    Downloads an image from a url and saves it to a specified location.

    :param url: url of image
    :param path: path where image will be saved to

    :return: path of saved image
    """
    # Create directories for storing images if they do not exist
    _ensure_path_exists(IDOL_IMAGES_PATH)
    _ensure_path_exists(OUTPUT_PATH)

    if not os.path.exists(path):
        print('Saving ' + url + ' to ' + path)
        fp = open(path, 'wb')
        response = await aiohttp.get(url)
        image = await response.read()
        fp.write(image)
        fp.close()

    return path


async def _build_image(circle_images: list, num_rows: int,
        x_distance: int, y_distance: int) -> object:
    """
    Stitches together a list of images to an output image.

    :param circle_images: list of image object being stitched together
    :param num_rows: number of rows to lay the image out in
    :param: x_distance: x spacing between each image
    :param y_distane: y spacing between each image

    :return: ouput image object
    """
    # Compute required height and width
    circle_width, circle_height = circle_images[0].size
    out_height = num_rows * (circle_height + y_distance)
    out_width = ((len(circle_images) + 1) * (circle_width + x_distance)) // 2

    image = Image.new('RGBA', (out_width, out_height))

    circle_rows = []
    for row_index in range(0, num_rows):
        circle_rows.append([])

    i = 0
    for circle_image in circle_images:
        circle_rows[i % len(circle_rows)].append(circle_image)
        i += 1

    x = 0
    y = 0
    for row_index in range(0, len(circle_rows)):
        x = 0

        # Offset row
        if (row_index + 1) % 2 == 0:
            x += circle_width // 2

        for col_index in range(0, len(circle_rows[row_index])):
            image.paste(circle_rows[row_index][col_index], (x, y))
            x += circle_width + x_distance

        y += circle_height + y_distance

    return image


def _ensure_path_exists(path: str):
    """
    Makes sure a path exists. Creates new directory if it does not.

    :param path: path being checked
    """
    try:
        os.mkdir(path)
    except OSError as Exception:
        return
