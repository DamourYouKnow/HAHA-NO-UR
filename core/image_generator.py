from collections import deque
from io import BytesIO
from logging import INFO
from pathlib import Path
from typing import List, Sequence, Tuple
from urllib.parse import urlsplit

from PIL import Image, ImageDraw, ImageFont

from bot import SessionManager
from idol_images import idol_img_path

CIRCLE_DISTANCE = 10
LABEL_COLOURS = {
    "Smile": "#FF6698", 
    "Pure": "#77EE87", 
    "Cool": "#66CCEE",
    "All": "#CC76E4"
}

# TODO seperate function that album_command calls.
async def create_image(session_manager: SessionManager, cards: list,
                       num_rows: int, align: bool=False,
                       add_labels: bool=False) -> BytesIO:
    """
    Creates a stitched together scout image of idol circles.
    :param session_manager: the SessionManager
    :param cards: cards to be stitched together.
    :param num_rows: Number of rows to use in the image
    :param align: to align middle the image or not.
    :param add_labels: to add labels or not.
    :return: path pointing to created image
    """
    # TODO, cards in album_cards dictionary will need an extra property.
    num_rows = min((num_rows, len(cards)))

    imgs = []
    for card in cards:
        image_field = 'round_card_image'
        count_field = 'unidolized_count'
        idolized = ('idolized' in card and card['idolized'])
       
        no_img = (idolized or card['card_image'] == None or card['round_card_image'] == None)
        if no_img:
            image_field = 'round_card_idolized_image'

        if idolized:
            count_field = 'idolized_count'

        url = "http:" + card[image_field]
        url_path = Path(urlsplit(url).path)
        file_path = idol_img_path.joinpath(url_path.name)
        next_img = Image.open(
                await get_one_img(url, file_path, session_manager))

        if add_labels:
            texts = [str(card['_id']), str(card[count_field])]
            next_img = _add_label(
                    next_img, texts, LABEL_COLOURS[card['attribute']])

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


def _add_label(img: Image, texts: list, colour: str):
    """
    Adds a label with text to an image.

    :param img: Image to add label to.
    """
    label = _create_label(100, 25, texts, colour, '#000000')
    img = img.convert('RGBA')
    temp_canvas = Image.new('RGBA', img.size)

    img_width, img_height = img.size
    label_width, label_height = label.size
    label_x = int((0.5 * img_width) - (0.5 * label_width)) # Center vertically
    label_y = img_height - label_height
    temp_canvas.paste(label, (label_x, label_y))
    return Image.alpha_composite(img, temp_canvas)


def _create_label(width: int, height: int, texts: list,
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

    bounds = [(0, 0), (width-1, height-1)]
    label_draw.rectangle(bounds, background_colour, outline_colour)

    font_size = _compute_label_font_size(label_img, texts, 'arial.ttf')
    font = ImageFont.truetype('arial.ttf', font_size)

    # This made sense when I wrote it.
    container_x, container_y = 0, 0
    container_w, container_h = width / len(texts), height
    for text in texts:
        # Get container x,y midpoints.
        container_mid_x = container_w / 2
        container_mid_y = container_h / 2

        # Get size of next text
        text_w, text_h = font.getsize(text)

        # Compute position of next text, centered in current container
        text_x = (container_x + container_mid_x) - (0.5 * text_w)
        text_y = (container_y + container_mid_y) - (0.5 * text_h)

        # Draw text and dividing line
        label_draw.text((text_x, text_y), text, outline_colour, font)
        line_pos = [(container_x, 0), (container_x, container_h)]
        label_draw.line(line_pos, outline_colour)

        # Get next container position
        container_x += container_w

    del label_draw
    return label_img


def _compute_label_font_size(label: Image, texts: List, font_type: str) -> int:
    """
    Computes the largest possible font size that a label can support for its
        given text.

    :param label: Target label image.
    :param texts: List of text to put on the label.

    :return: Largest possible font size.
    """
    label_width, label_height = label.size

    text_max_width = label_width / len(texts)
    text_max_height = label_height
    max_str = max(texts, key=len)

    font_size = 1
    font = ImageFont.truetype(font_type, font_size)
    font_width, font_height = font.getsize(max_str)
    while font_width < text_max_width and font_height < text_max_height:
        font_size += 1
        font = ImageFont.truetype(font_type, font_size)
        font_width, font_height = font.getsize(max_str)

    #return font_size - 1
    return 18 # FIXME I'm too tired for this shit right now.


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
