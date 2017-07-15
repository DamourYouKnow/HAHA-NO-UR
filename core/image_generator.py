from collections import deque
from io import BytesIO
from logging import INFO
from pathlib import Path
from typing import List, Sequence, Tuple
from urllib.parse import urlsplit

from PIL import Image, ImageDraw, ImageColor

from bot import SessionManager
from idol_images import idol_img_path

CIRCLE_DISTANCE = 10


async def create_image(session_manager: SessionManager,
                       urls: list, num_rows: int,
                       align: bool = False) -> BytesIO:
    """
    Creates a stitched together image of idol circles.
    :param session_manager: the SessionManager
    :param urls: urls of single images to be stitched together.
    :param num_rows: Number of rows to use in the image
    :param align: to align middle the image or not.
    :return: path pointing to created image
    """
    num_rows = min((num_rows, len(urls)))
    # Save images that do not exists
    imgs = []
    for url in urls:
        url_path = Path(urlsplit(url).path)
        file_path = idol_img_path.joinpath(url_path.name)

        next_img = Image.open(
                await get_one_img(url, file_path, session_manager))
        # TODO D'Amour add labels only if album, pass in add_labels as boolean.
        next_img = _add_label(next_img)

        imgs.append(next_img)

    res = BytesIO()
    # Load images
    image = _build_image(imgs, num_rows, 10, 10, align)
    image.save(res, 'PNG')
    return BytesIO(res.getvalue())


async def get_one_img(url: str, path: Path,
                      session_manager: SessionManager) -> BytesIO:
    """
    Get a single image. If image is not found in local storge, download it.

    :param url: url of image
    :param path: path where image will be saved to
    :param session_manager: the SessionManager
    :return: a BytesIO of the image.
    """
    if path.is_file():
        return BytesIO(path.read_bytes())
    resp = await session_manager.get(url)
    async with resp:
        session_manager.logger.log(
            INFO, 'Saving ' + url + ' to ' + str(path))
        image = await resp.read()
        path.write_bytes(image)
        return BytesIO(image)

def _add_label(img: Image):
    """
    Adds a label with text to an image.

    :param img: Image to add label to.
    """
    label = _create_label(100, 25, [], '#ff0000', '#ffffff')
    img = img.convert('RGBA')
    temp_canvas = Image.new('RGBA', img.size)

    # TODO D'Amour: make this not (0, 0)
    temp_canvas.paste(label, (0, 0))
    return Image.alpha_composite(img, temp_canvas)

def _create_label(width: int, height: int, texts: List,
                 background_colour: str, outline_colour: str) -> Image:
    """
    :param size: Tuple of (width, height) representing label size.
    :param texts: List of text to add to the label, each text string will be
        seperated by a dividing line.
    :param colour: Colour of image.

    :return: Label image.
    """
    label_img = Image.new('RGBA', (width, height))
    label_draw = ImageDraw.Draw(label_img)
    bounds = [(0, 0), (width, height)]
    label_draw.rectangle(bounds, background_colour, outline_colour)
    label_draw.text((0, 0), "test", outline_colour)

    # TODO D'Amour: add texts
    del label_draw
    return label_img


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
