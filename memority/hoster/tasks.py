import sys

import os

sys.path.extend([os.path.normpath(os.path.join(os.path.dirname(__file__), os.path.pardir))])

import aiohttp
import asyncio
import logging
import multiprocessing as mp
import random
from celery import Celery
from celery.bin.celery import main as main_
from celery.schedules import crontab
from datetime import datetime, timedelta

import logger
from models import HosterFile
from settings import settings

app = Celery('tasks', broker=f'sqla+sqlite:///{settings.db_path}')

logger.setup_logging()
logger = logging.getLogger('monitoring')


def run_in_loop(func):
    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(func(*args, **kwargs))

    wrapper.__name__ = func.__name__

    return wrapper


@app.task
@run_in_loop
async def request_payment_for_file(file_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(
                f'http://{settings.daemon_address}/tasks/request_payment_for_file/',
                json={
                    "file_id": file_id
                }
        ) as response:
            data = await response.json()
            if data.get('status') == 'success':
                logger.info(f'request_payment_for_file result: {data.get("data").get("result")}')
            else:
                logger.warning(f'request_payment_for_file result: {data.get("message")}')


@app.task
@run_in_loop
async def check_ip():
    async with aiohttp.ClientSession() as session:
        async with session.post(f'http://{settings.daemon_address}/tasks/check_ip/') as response:
            data = await response.json()
            if data.get('status') == 'success':
                logger.info(f'check_ip result: {data.get("data").get("result")}')
            else:
                logger.warning(f'check_ip result: {data.get("message")}')


@app.task
@run_in_loop
async def perform_monitoring_for_file(file_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(
                f'http://{settings.daemon_address}/tasks/perform_monitoring_for_file/',
                json={
                    "file_id": file_id
                }
        ) as response:
            data = await response.json()
            if data.get('status') == 'success':
                logger.info(f'perform_monitoring_for_file result: {data.get("data").get("result")}')
            else:
                logger.warning(f'perform_monitoring_for_file result: {data.get("message")}')


@app.task
def request_payment_for_all_files():
    for file in HosterFile.objects.all():
        request_payment_for_file.delay(file.id)


@app.task
def schedule_monitoring():
    for file in HosterFile.objects.all():
        perform_monitoring_for_file.apply_async(
            eta=datetime.now() + timedelta(
                # 48 = minutes in 8 hours / number of hosters
                minutes=int(file.my_monitoring_number * 48 + random.randint(0, 48))
            ),
            kwargs={"file_id": file.id}
        )


@app.task
def test():
    print('*' * 1000)


app.conf.beat_schedule = {
    'test-every-minute': {
        'task': 'hoster.tasks.test',
        'schedule': crontab(hour='*', minute='*')
    },
    'check-ip-every-hour': {
        'task': 'hoster.tasks.check_ip',
        'schedule': crontab(hour='*', minute=0)
    },
    'request-payment-every-week': {
        'task': 'hoster.tasks.request_payment_for_all_files',
        'schedule': crontab(day_of_week=0, hour=0, minute=0)
    },
    'schedule-monitoring-every-8-hours': {
        'task': 'hoster.tasks.schedule_monitoring',
        'schedule': crontab(hour='*/8', minute=0)
    }
}

app.conf.timezone = 'UTC'


def create_celery_processes():
    working_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    if os.path.isfile(os.path.join(working_dir, 'celerybeat.pid')):
        os.remove(os.path.join(working_dir, 'celerybeat.pid'))
    os.chdir(working_dir)
    return [
        mp.Process(  # start beat
            target=main_,
            args=[['_', '-A', 'hoster.tasks', 'beat', '--loglevel=info']]
        ),
        mp.Process(  # start worker
            target=main_,
            args=[['_', '-A', 'hoster.tasks', 'worker', '--loglevel=info', '--pool=eventlet', '-E']]
        )
    ]
