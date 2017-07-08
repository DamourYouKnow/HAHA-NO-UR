import urllib.parse
from collections import deque
from logging import INFO
from pathlib import Path
from typing import List, Sequence, Tuple

from PIL import Image

from bot import SessionManager
from idol_images import idol_img_path
from scout_output import scout_output_path

CIRCLE_DISTANCE = 10


async def create_image(session_manager: SessionManager,
                       idol_circle_urls: list, num_rows: int,
                       output_filename: str,
                       align: bool = False) -> str:
    """
    Creates a stitched together image of idol circles.
    :param session_manager: the SessionManager
    :param idol_circle_urls: urls of idol circle images to be stitched together.
    :param num_rows: Number of rows to use in the image
    :param output_filename: name of output image file
    :param align: to align middle the image or not.
    :return: path pointing to created image
    """
    if num_rows > len(idol_circle_urls):
        num_rows = len(idol_circle_urls)

    image_filepaths = []  # list of image filepaths
    # Save images that do not exists
    for image_url in idol_circle_urls:
        url_path = urllib.parse.urlsplit(image_url).path
        file_path = idol_img_path.joinpath(Path(url_path).name)
        image_filepaths.append(file_path)
        await download_image_from_url(image_url, file_path, session_manager)
    # Load images
    circle_images = [Image.open(str(i)) for i in image_filepaths]
    image = _build_image(circle_images, num_rows, 10, 10, align)
    output_path = scout_output_path.joinpath(output_filename)
    image.save(str(output_path), 'PNG')
    return str(output_path)


async def download_image_from_url(
        url: str, path: Path, session_manager: SessionManager) -> Path:
    """
    Downloads an image from a url and saves it to a specified location.

    :param url: url of image
    :param path: path where image will be saved to
    :param session_manager: the SessionManager

    :return: path of saved image
    """
    # Create directories for storing images if they do not exist
    if not idol_img_path.is_dir():
        idol_img_path.mkdir(parents=True, exist_ok=True)
    if not scout_output_path.is_dir():
        scout_output_path.mkdir(parents=True, exist_ok=True)
    response = await session_manager.get(url)
    async with response:
        #  Checking if the image already exists in two different ways because
        # python is cross platform 4Head.
        if not path.is_file():
            session_manager.logger.log(
                INFO, 'Saving ' + url + ' to ' + str(path))
            image = await response.read()
            path.write_bytes(image)
    return path


def _build_image(circle_images: list, num_rows: int,
                 x_padding: int, y_padding: int, align: bool) -> Image:
    """
    Stitches together a list of images to an output image.

    :param circle_images: list of image object being stitched together
    :param num_rows: number of rows to lay the image out in
    :param x_padding: x spacing between each image
    :param y_padding: y spacing between each row
    :param align: Whether the rows are aligned or spaced out.

    :return: ouput image object
    """
    sizes = [circle.size for circle in circle_images]
    positions, x, y = compute_pos(sizes, num_rows, x_padding, y_padding, align)
    image_queue = deque(circle_images)
    img = Image.new('RGBA', (x, y))
    for row in positions:
        for c in row:
            img.paste(image_queue.popleft(), c)
    return img


def compute_pos(
        sizes: List[Tuple[int]], num_rows: int,
        x_padding: int, y_padding: int, align: bool) -> tuple:
    """
    Compute all images positions from the list of images and number of rows.

    :param sizes: A list of sizes for all images.
    :param num_rows: the number of rows.
    :param x_padding: x spacing between each image
    :param y_padding: y spacing between each row
    :param align: to align middle the image or not.
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
        if not align and diff > 0:
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
