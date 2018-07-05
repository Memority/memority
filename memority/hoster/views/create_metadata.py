from aiohttp import web

from models import HosterFile
from settings import settings
from smart_contracts import token_contract
from utils import InvalidSignature
from .utils import logger, error_response


class MetadataCreationError(Exception):
    pass


def verify_required_fields(data: dict):
    required = ['file_hash', 'owner_key', 'signature', 'client_address', 'size']

    if not all([field in data for field in required]):
        logger.warning(f'Validation error | fields: {", ".join(data.keys())}')
        raise web.HTTPBadRequest(
            reason='''Validation error!
            Fields 'file_hash', 'owner_key', 'signature', 'client_address' are required.'''
        )


def check_free_space(file_size: int, file_hash: str):
    free_space = settings.disk_space_for_hosting * (1024 ** 3) - HosterFile.get_total_size()

    if file_size > free_space:
        logger.warning(
            f'Not enough space for uploading file '
            f'| file: {file_hash} '
            f'| size: {file_size} bytes'
            f'| free space: {free_space} bytes'
        )
        raise MetadataCreationError('Not enough space')


async def check_deposit(client_address, file_hash):
    deposit = await token_contract.get_deposit(
        owner_address=client_address,
        file_hash=file_hash,
        ping=True
    )

    if not deposit:
        logger.warning(
            f'No deposit for file '
            f'| client contract: {client_address} '
            f'| file: {file_hash}'
        )
        raise MetadataCreationError("No deposit for file")


async def create_metadata(request):
    """
    Creates metadata for file.
    There must be enough disk space and non-zero deposit for file.
    Required fields in POST data:
        - file_hash
        - owner_key
        - signature
        - client_address
        - size

    :param request: web.Request
    :return: web.Response
    """

    data = await request.json()
    logger.info(
        f'Creating metadata '
        f'| file: {data["file_hash"]} '
        f'| owner: {data["client_address"]}'
    )

    verify_required_fields(data)

    try:
        check_free_space(data.get('size'), data.get('file_hash'))
        await check_deposit(data.get('client_address'), data.get('file_hash'))
        instance = await HosterFile.create_metadata(**data)

    except MetadataCreationError as err:
        return error_response(str(err))

    except HosterFile.AlreadyExists:
        logger.warning(
            f'File metadata already exists '
            f'| file: {data["file_hash"]}'
        )
        return error_response("already exists")

    except InvalidSignature:
        logger.warning(
            f'Invalid signature '
            f'| file: {data["file_hash"]} '
            f'| signature: {data["signature"]}'
        )
        raise web.HTTPBadRequest(reason='Invalid signature!')

    else:
        logger.info(
            f'Metadata created successfully '
            f'| file: {data["file_hash"]} '
            f'| owner: {data["client_address"]}'
        )
        return web.json_response({
            "status": "success",
            "data": {
                "file": {
                    "hash": instance.hash
                }
            }
        })
