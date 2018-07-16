import logging

from models import HosterFile
from smart_contracts import token_contract

logger = logging.getLogger('monitoring')


async def request_payment_for_file(data):
    """
    Request payment for file

    :return:  info message [str]
    """
    file = HosterFile.objects.get(hash=data.get('file_hash'))
    logger.info(
        f'Requesting payment for file '
        f'| file: {file.hash}'
    )

    if token_contract.time_to_pay(file.hash):
        logger.info(
            f'Requesting payment for file '
            f'| file: {file.hash}'
        )
        amount = await token_contract.request_payout(file.client_address, file.hash)
        logger.info(
            f'Successfully requested payment for file '
            f'| file: {file.hash} '
            f'| amount: {amount}'
        )
        return f'Successfully requested payment for file | file: {file.hash} | amount: {amount}'

    return 'Not time_to_pay'
