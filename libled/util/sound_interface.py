# -*- coding: utf-8 -*-
import json
import threading

import logger
import requests
import zmq
from sound_pool import SoundPool

# debug
# import logging
# logging.basicConfig(level=logging.DEBUG)


class SoundInterface(object):
    def __new__(cls):
        raise NotImplementedError('Cant call this Constructor.')

    domain = 'http://localhost:5701/audio/v1/'
    __content_id = ''

    pool = SoundPool(1)

    @classmethod
    def init(cls, id):
        cls.__content_id = id
        cls.post('init')

    @classmethod
    def close(cls):
        cls.stop()
        cls.pool.abort = True
        # zmq
        # SoundInterface.push.close()

    @classmethod
    def play(cls, wav='', loop=False, stop=False):
        func = 'play'
        data_ = {
            'wav': wav,
            'loop': loop,
            'stop': stop
        }
        cls.post(func, data_=data_)

    @classmethod
    def pause(cls):
        func = 'pause'
        cls.post(func)

    @classmethod
    def resume(cls):
        func = 'resume'
        cls.post(func)

    @classmethod
    def stop(cls):
        func = 'stop'
        cls.post(func)

    @classmethod
    def volume(cls, val=0.5):
        func = 'volume'
        data_ = {
            'val': val
        }
        cls.post(func, data_=data_)

    @classmethod
    def post(cls, func, data_=None):
        args = {'domain': cls.domain,
                'func': func,
                'id': cls.__content_id}
        if data_ is not None:
            args['data'] = data_
        cls.pool.put(args)

    @classmethod
    def __post_threading(cls, arg):
        th = threading.Thread(target=cls.__post_requests,
                              args=(arg,))
        th.start()

    @classmethod
    def __post_requests(cls, arg):
        uri_ = arg.get('domain') + arg.get('func')
        param_ = {'content_id': arg.get('id')}
        data_ = arg.get('data')
        proxies = {
            'http': '',
            'https': '',
        }
        timeout = 0.1
        res = requests.post(
            uri_,
            data=json.dumps(data_),
            params=param_,
            headers={'Content-Type': 'application/json'},
            proxies=proxies,
            timeout=timeout)
        return res

    @classmethod
    def __post_push(cls, arg):
        cls.push.send_json(arg)

    @classmethod
    def _init_pool(cls):
        # zmq
        # cls.pool.set_work(cls.__post_push)
        # cls.pool.set_work(cls.__post_requests)
        cls.pool.set_work(cls.__post_threading)
        cls.pool.set_complated(
            lambda x: logger.d('post result = {}'.format(x)))

    # zmq
    # @classmethod
    # def _init_push(cls):
    #     ctx = zmq.Context()
    #     cls.push = ctx.socket(zmq.PUSH)
    #     cls.push.connect('tcp://localhost:5751')


SoundInterface.pool.run_async()
SoundInterface._init_pool()
# zmq
# SoundInterface._init_push()
