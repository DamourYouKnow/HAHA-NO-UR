import os
import shutil
import urllib
import requests
import posixpath
from PIL import Image

IDOL_CIRCLES_PATH = "idol_circles/"
OUTPUT_PATH = "scout_output/"
CIRCLE_DISTANCE = 10

'''
Creates a stitched together image of idol circles.

idol_circles: List - urls of idol circle images to be stitched together.
output_filename: String - name of output image file

return: String - path pointing to created image.
'''
def create_image(idol_circle_urls, output_filename):
    # Create directories for stroing images if they do not exist
    ensure_path_exists(IDOL_CIRCLES_PATH)
    ensure_path_exists(OUTPUT_PATH)

    image_filepaths = [] # list of image filepaths

    # Save images that do not exists
    for image_url in idol_circle_urls:
        url_path = urllib.parse.urlsplit(image_url).path
        filename = posixpath.basename(url_path)
        image_filepaths.append(IDOL_CIRCLES_PATH + filename)

        if not os.path.exists(IDOL_CIRCLES_PATH + filename):
            download_image_from_url(image_url, IDOL_CIRCLES_PATH + filename)

    # Load images
    circle_images = []
    for image_filepath in image_filepaths:
        circle_images.append(Image.open(image_filepath))

    # Create transparent background
    circle_width, circle_height = circle_images[0].size

    stitch_height = circle_height
    stitch_width = (
        circle_width +
        (len(circle_images) * (circle_width))
    )

    print(str(stitch_height))
    print(str(stitch_width))

    image = Image.new("RGBA", (stitch_width, stitch_height))

    x = 0
    for circle_image in circle_images:
        image.paste(circle_image, (x, 0))
        x += circle_width

    image.save(OUTPUT_PATH + output_filename, "PNG")

'''
Downloads an image from a url and saves it to a specified location

url: String - url of image
path: String - path where the image will be saved to
'''
def download_image_from_url(url, path):

    print("Saving " + url + " to " + path)
    fp = open(path, "wb")
    fp.write(requests.get(url).content)
    fp.close()

'''
Makes sure a path exists. Creates new directory if it does not.

path: String - path being checked
'''
def ensure_path_exists(path):
    try:
        os.mkdir(path)
    except OSError as Exception:
        return


test_idols = [
    "http://i.schoolido.lu/c/1RoundShizuku.png",
    "http://i.schoolido.lu/c/4RoundMarika.png",
    "http://i.schoolido.lu/c/2RoundCoco.png",
    "http://i.schoolido.lu/c/3RoundYuu.png",
    "http://i.schoolido.lu/c/5RoundSana.png",
    "http://i.schoolido.lu/c/6RoundFumie.png",
    "http://i.schoolido.lu/c/7RoundMinami.png",
    "http://i.schoolido.lu/c/8RoundChristina.png",
    "http://i.schoolido.lu/c/9RoundAkemi.png",
    "http://i.schoolido.lu/c/10RoundIruka.png",
    "http://i.schoolido.lu/c/11RoundAya.png"
]

create_image(test_idols, "test.png")
