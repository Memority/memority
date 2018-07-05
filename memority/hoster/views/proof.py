from aiohttp import web

from models import HosterFile
from .utils import logger, error_response


async def proof(request):
    """
    Given file hash and "from_" and "to_" integers (hash in request.match_info, from_ and to_ in GET params),
    calculating proof of storing file (hash of chunk between two byte positions in file).

    :param request: web.Request
    :return: web.Response
    """

    file_hash = request.match_info.get('id')
    query = request.query
    from_ = query.get('from', '')
    to_ = query.get('to', '')
    logger.info(f'File storage proof | file: {file_hash} | from: {from_} | to: {to_}')

    if not (from_.isdigit() and to_.isdigit()):
        return error_response("Invalid GET parameters. Both must be integers.")

    try:
        file = HosterFile.find(file_hash)
        chunk_hash = await file.compute_chunk_hash(int(from_), int(to_))
    except HosterFile.NotFound:
        msg = f'File not found | file: {file_hash}'
        logger.warning(msg)
        return error_response(msg, code=404)

    return web.json_response({
        "status": "success",
        "data": {
            "hash": chunk_hash
        }
    })
