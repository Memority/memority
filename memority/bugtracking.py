import os

import raven

from settings import settings

raven_client = raven.Client(
    dsn='https://7f943c9a0edc4af688fab169e0cac527:0c84e4329d044d589763e6c852a14d84@sentry.io/306286',

    include_paths=[os.path.dirname(__file__)],
    ignore_exceptions=[
        KeyboardInterrupt,
        NotImplementedError,
        'asyncio.CancelledError',
        'smart_contracts.smart_contract_api.exceptions.ContractNeedsUpdate'
    ],
    release=settings.version
)
