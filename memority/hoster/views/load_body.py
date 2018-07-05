from aiohttp import web

from models import HosterFile
from utils import InvalidSignature
from .utils import logger


async def load_body(request: web.Request):
    """
    Given file hash (metadata for this file must be created earlier) and file body in request.content,
    saves it to filesystem.

    :param request: web.Request
    :return: web.Response
    """

    file_hash = request.match_info.get('id')
    data_reader = request.content.iter_chunks()
    logger.info(f'Loading file body | file: {file_hash}')

    try:
        instance = await HosterFile.load_body(data_reader, file_hash)

    except HosterFile.NotFound:
        logger.warning(f'File not found | file: {file_hash}')
        raise web.HTTPNotFound(reason='File not found!')

    except InvalidSignature:
        logger.warning(f'Invalid signature | file: {file_hash}')
        raise web.HTTPBadRequest(reason='Invalid signature!')

    return web.json_response({
        "status": "success",
        "data": {
            "file": {
                "hash": instance.hash
            }
        }
    })
