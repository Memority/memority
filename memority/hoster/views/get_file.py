from aiohttp import web

from models import HosterFile
from .utils import logger, error_response


async def get_file(request):
    """
    Given file hash (in request.match_info), returns file body.
    If there is no deposit for the file, returns HTTP 402.

    :param request: web.Request
    :return: web.Response
    """

    file_hash = request.match_info.get('id')
    logger.info(f'File content | file: {file_hash}')

    try:
        file = HosterFile.find(file_hash)
        if not await file.check_deposit():
            return error_response(  # ToDo: rm status code
                'No deposit for file',
                402
            )

    except HosterFile.NotFound:
        logger.warning(f'File not found | file: {file_hash}')
        raise web.HTTPNotFound(reason='File not found!')

    return web.Response(body=await file.get_body())
