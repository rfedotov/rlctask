import sched, time
import logging
import cv2
import sys
import ffmpeg
import redis
import schedule
import yaml
import argparse
import asyncio
from pathlib import Path

from utils import timestamp
from db.redis import RedisThumbnail
#from sheduler import do_stuff_periodically

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)
logger = logging.getLogger()


def ffmpeg_(db_model, stream_uri, files_dir):
    logger.debug('start extracting ...')
    ts = timestamp()
    width = 640
    filename = "image_{}.jpg".format(ts)
    file_path = Path(files_dir) / filename
    (
        ffmpeg
        .input(stream_uri, ss=0)
        .filter('scale', 640, -1)
        .output(str(file_path), vframes=1)
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
    )
    thumb = dict(ts=ts, filename=filename, width=width, stream=stream_uri)
    db_model.save(thumb)
    logger.debug('end extracting %s...', filename)

def print_some_times(config):
    logger.debug('start process')
    redis_db = redis.Redis(host=config['redis_host'], port=config['redis_port'], db=config['redis_db'])
    schedule.every(15).seconds.do(ffmpeg_, RedisThumbnail(redis_db), config['stream_uri'], config['files_dir'])
    #while True:
    #    schedule.run_pending()
    #from time import time, sleep
    while True:
        startTime = time.time()
        ffmpeg_(RedisThumbnail(redis_db), config['stream_uri'], config['files_dir'])
        endTime = time.time()-startTime
        time.sleep(config['interval_sec']-endTime)
    #asyncio.run(do_stuff_periodically(5, ffmpeg_, RedisThumbnail(redis_db), config['stream_uri'], config['files_dir']))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="display a square of a given number", type=str)
    args = parser.parse_args()
    f = open(args.config)
    try:
        config = yaml.safe_load(f.read())
    except ImportError:
        logger.error('ImportError load')
    logger.debug('config %s', config)
    print_some_times(config)