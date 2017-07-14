from itertools import chain
from pathlib import Path

from idol_images import idol_img_path
from logs import log_path


def clean():
    for _path in chain(log_path.iterdir(), idol_img_path.iterdir()):
        path = Path(_path)
        if not path.name.endswith('.py') and not path.is_dir():
            path.unlink()


if __name__ == '__main__':
    clean()
