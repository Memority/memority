import logging

from aiohttp import web

from models import HosterFile, HosterFileM2M
from settings import settings
from smart_contracts import token_contract
from utils import InvalidSignature

__all__ = ['final_metadata', 'proof', 'create_metadata', 'load_body', 'get_file', 'file_list', 'file_host_status']

logger = logging.getLogger('memority')


def _error_response(msg, code=200):
    return web.json_response(
        {
            "status": "error",
            "message": msg
        },
        status=code
    )


async def get_file(request):
    file_hash = request.match_info.get('id')
    logger.info(f'File content | file: {file_hash}')
    try:
        file = HosterFile.find(file_hash)
        if not await file.check_deposit():
            return _error_response('No deposit for file', 402)
    except HosterFile.NotFound:
        logger.warning(f'File not found | file: {file_hash}')
        raise web.HTTPNotFound(reason='File not found!')
    return web.Response(body=await file.get_body())


async def file_list(request):
    logger.info('File list')
    files = HosterFile.list_hashes()
    return web.json_response({
        "status": "success",
        "data": {
            "files": files
        }
    })


async def create_metadata(request):
    data = await request.json()
    required = ['file_hash', 'owner_key', 'signature', 'client_contract_address', 'size']
    logger.info(f'Creating metadata | file: {data["file_hash"]} | owner: {data["client_contract_address"]}')
    if not all([field in data for field in required]):
        logger.warning(f'Validation error | fields: {", ".join(data.keys())}')
        raise web.HTTPBadRequest(
            reason='''Validation error!
            Fields 'file_hash', 'owner_key', 'signature', 'client_contract_address' are required.'''
        )

    if data.get('size') > (settings.disk_space_for_hosting * (1024 ** 3) - HosterFile.get_total_size()):
        return _error_response('Not enough space')

    if not await token_contract.get_deposit(
            owner_contract_address=data['client_contract_address'],
            file_hash=data['file_hash'],
            ping=True):
        logger.warning(f'No deposit for file '
                       f'| client contract: {data["client_contract_address"]} | file: {data["file_hash"]}')
        return _error_response(
            "No deposit for file!",
            402
        )

    try:
        instance = await HosterFile.create_metadata(**data)
        if 'hosts' in data:
            request.app['scheduler'].update()
    except InvalidSignature:
        logger.warning(f'Invalid signature | file: {data["file_hash"]} | signature: {data["signature"]}')
        raise web.HTTPBadRequest(reason='Invalid signature!')
    except HosterFile.AlreadyExists:
        logger.warning(f'File metadata already exists | file: {data["file_hash"]}')
        return _error_response("already exists", code=422)
    else:
        response_data = {
            "status": "success",
            "data": {
                "file": {
                    "hash": instance.hash
                }
            }
        }
        code = 201
    return web.json_response(response_data, status=code)


async def load_body(request: web.Request):
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


async def proof(request):
    file_hash = request.match_info.get('id')
    query = request.query
    from_ = query.get('from', '')
    to_ = query.get('to', '')
    logger.info(f'File storage proof | file: {file_hash} | from: {from_} | to: {to_}')
    if not (from_.isdigit() and to_.isdigit()):
        return _error_response("invalid GET parameters")
    try:
        file = HosterFile.find(file_hash)
        chunk_hash = await file.compute_chunk_hash(int(from_), int(to_))
    except HosterFile.NotFound:
        msg = f'File not found | file: {file_hash}'
        logger.warning(msg)
        return _error_response(msg, code=404)
    return web.json_response(
        {
            "status": "success",
            "data": {
                "hash": chunk_hash
            }
        }
    )


async def file_host_status(request):
    file_hash = request.match_info.get('id')
    host_address = request.match_info.get('host')
    logger.info(f'File host status | file: {file_hash} | host: {host_address}')
    try:
        status = HosterFileM2M.get_status(file_hash, host_address)
    except HosterFileM2M.NotFound:
        msg = f'Hoster file not found | file: {file_hash} | host: {host_address}'
        logger.warning(msg)
        return _error_response(msg, code=404)
    return web.json_response(
        {
            "status": "success",
            "data": {
                "status": status
            }
        }
    )


async def final_metadata(request):
    # ToDo: merge with create_metadata
    file_hash = request.match_info.get('id', None)
    logger.info(f'Uploading final metadata | file: {file_hash}')
    try:
        instance = HosterFile.find(file_hash)
    except HosterFile.NotFound:
        logger.warning(f'File not found | file: {file_hash}')
        raise web.HTTPNotFound(reason='File not found!')
    data = await request.json()
    hosts = data.get('hosts')
    instance.add_hosts(hosts)
    logger.info('Updating schedule...')
    request.app['scheduler'].update()
    logger.info('Schedule updated')
    return web.json_response({
        "status": "success",
        "data": {
            "file": {
                "hash": instance.hash
            }
        }
    })
