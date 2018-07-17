import os
import shutil

from settings import settings
from ..utils import Exit


async def set_storage_path(path):
    if not os.path.isdir(path):
        raise Exit(f"Not a directory: {path}")
    if path == os.path.normpath(settings.boxes_dir):
        return 'ok'
    from_dir = settings.boxes_dir
    for filename in os.listdir(from_dir):
        shutil.move(os.path.join(from_dir, filename), os.path.join(path, filename))
    os.rmdir(from_dir)
    settings.boxes_dir = path
    return 'ok'
