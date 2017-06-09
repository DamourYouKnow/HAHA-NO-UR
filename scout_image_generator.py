import urllib.parse
from collections import deque
from pathlib import Path
from typing import List, Sequence, Tuple

from PIL import Image
from aiohttp import ClientSession

IDOL_IMAGES_PATH = Path('idol_images')
OUTPUT_PATH = Path('scout_output')
CIRCLE_DISTANCE = 10


async def create_image(
        idol_circle_urls: list, num_rows: int, output_filename: str) -> Path:
    """
    Creates a stitched together image of idol circles.
    :param idol_circle_urls: urls of idol circle images to be stitched together.
    :param num_rows: Number of rows to use in the image
    :param output_filename: name of output image file
    :return: path pointing to created image
    """
    image_filepaths = []  # list of image filepaths
    # Save images that do not exists
    session = ClientSession()
    for image_url in idol_circle_urls:
        url_path = urllib.parse.urlsplit(image_url).path
        file_path = IDOL_IMAGES_PATH.joinpath(Path(url_path).name)
        image_filepaths.append(file_path)
        await download_image_from_url(image_url, file_path, session)
    session.close()
    # Load images
    circle_images = [Image.open(str(i)) for i in image_filepaths]
    image = _build_image(circle_images, num_rows, 10, 10)
    output_path = OUTPUT_PATH.joinpath(output_filename)
    image.save(str(output_path), 'PNG')
    return str(output_path)


async def download_image_from_url(
        url: str, path: Path, session: ClientSession) -> Path:
    """
    Downloads an image from a url and saves it to a specified location.
    :param url: url of image
    :param path: path where image will be saved to
    :param session: the aiohttp ClientSession
    :return: path of saved image
    """
    # Create directories for storing images if they do not exist
    if not IDOL_IMAGES_PATH.is_dir():
        IDOL_IMAGES_PATH.mkdir(parents=True, exist_ok=True)
    if not OUTPUT_PATH.is_dir():
        OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    async with session.get(url) as r:
        if r.status == 200 and not path.is_file():
            print('Saving ' + url + ' to ' + str(path))
            image = await r.read()
            path.write_bytes(image)
    return path


def _build_image(circle_images: list, num_rows: int,
                 x_padding: int, y_padding: int) -> Image:
    """
    Stitches together a list of images to an output image.
    :param circle_images: list of image object being stitched together
    :param num_rows: number of rows to lay the image out in
    :param x_padding: x spacing between each image
    :param y_padding: y spacing between each row
    :return: ouput image object
    """
    sizes = [circle.size for circle in circle_images]
    positions, x, y = compute_pos(sizes, num_rows, x_padding, y_padding)
    image_queue = deque(circle_images)
    img = Image.new('RGBA', (x, y))
    for row in positions:
        for c in row:
            img.paste(image_queue.popleft(), c)
    return img


def compute_pos(
        sizes: List[Tuple[int]], num_rows: int,
        x_padding: int, y_padding: int) -> tuple:
    """
    Compute all images positions from the list of images and number of rows.
    :param sizes: A list of sizes for all images.
    :param num_rows: the number of rows.
    :param x_padding: x spacing between each image
    :param y_padding: y spacing between each row
    :return: Positions for all images, the total x size, the total y size
    """
    total_x, total_y = 0, 0
    rows = split(sizes, num_rows)
    res = []
    row_x_sizes = []

    for row in rows:
        row_x_sizes.append(
            sum([i[0] for i in row]) + x_padding * (len(row) - 1))
        row_y = max([i[1] for i in row])
        res.append(compute_row(row, x_padding, total_y))
        total_y += row_y + y_padding
        total_x = max(row_x_sizes)
    i = 0
    for row, row_x, row_sizes in zip(res, row_x_sizes, rows):
        actual = row_sizes[-1][0] + row[-1][0]
        diff = round((total_x - actual) / 2)
        if diff > 0:
            res[i] = [(x + diff, y) for x, y in row]
        i += 1
    return res, total_x, total_y - y_padding


def compute_row(
        row_sizes: List[Tuple[int]],
        x_padding: int, y_pos: int) -> List[Tuple[int]]:
    """
    Compute the positions for a single row.
    :param row_sizes: the list of image sizes in that row.
    :param x_padding: the x padding in between images.
    :param y_pos: the y position of that row.
    :return: A list of (x, y) positions for that row.
    """
    res = []
    x = 0
    for size in row_sizes:
        res.append((x, y_pos))
        x += size[0] + x_padding
    return res


def split(in_: Sequence, chunks: int) -> List[List]:
    """
    Split a sequence into roughly equal chunks.
    :param in_: the input sequence.
    :param chunks: the number of chunks.
    :return: the sequence split up into chunks.
    """
    k, m = divmod(len(in_), chunks)
    return [
        in_[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]
        for i in range(chunks)
    ]


def _build_image_old(circle_images: list, num_rows: int,
                     x_distance: int, y_distance: int):
    """
    Stitches together a list of images to an output image.
    :param circle_images: list of image object being stitched together
    :param num_rows: number of rows to lay the image out in
    :param: x_distance: x spacing between each image
    :param y_distance: y spacing between each image
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
