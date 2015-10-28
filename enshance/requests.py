"""A wrapper around requests that records all requests made with it.
    Supports get, put, post, delete and request
    all calls return an instance of Response
"""
from __future__ import absolute_import

import json
import time
import logging
import functools

import six
import furl
import requests
from requests.structures import CaseInsensitiveDict

from enshance import settings
from orcid import models


logger = logging.getLogger(__name__)


def _maybe_load_response(method, url):
    try:
        return Response.get(url=url.lower(), method=method)
    except Response.DoesNotExist:
        return None


def record_or_load_response(method, url, throttle=None, force=False, params=None, expected=(200,), **kwargs):

    resp = _maybe_load_response(method, url)

    if not force and resp and resp.ok:
        logger.info('Return recorded response from "{}"'.format(url))
        return resp

    if force:
        logger.warning('Force updating request to "{}"'.format(url))
    else:
        logger.info('Making request to "{}"'.format(url))

    maybe_sleep(throttle)

    response = requests.request(method, url, **kwargs)

    if not response.ok:
        logger.info('Got non-ok response code. url: {}, mehtod: {}'.format(url, method))

    if isinstance(response.content, six.text_type):
        response.content = response.content.encode('utf8')

    if not resp:
        return Response(
            url=url.lower(),
            method=method,
            ok=response.ok,
            content=response.content,
            encoding=response.encoding,
            status_code=response.status_code,
            headers_str=json.dumps(dict(response.headers))
        ).save()

    logger.warning('Skipped recorded response from "{}"'.format(url))

    return resp.update(
        ok=(response.ok or response.status_code in expected),
        content=response.content,
        encoding=response.encoding,
        status_code=response.status_code,
        headers_str=json.dumps(dict(response.headers))
    ).save()


def maybe_sleep(sleepytime):
    # exists so that this alone can be mocked in tests
    if sleepytime:
        time.sleep(sleepytime)


def request(method, url, params=None, **kwargs):
    """Make a recorded request or get a record matching method and url

    :param str method: Get, Put, Post, or Delete
    :param str url: Where to make the request to
    :param bool force: Whether or not to force the new request to be made
    :param int throttle: A time in seconds to sleep before making requests
    :param dict kwargs: Addition keywords to pass to requests
    """
    if params:
        url = furl.furl(url).set(args=params).url
    logger.info(url)
    if settings.RECORD_HTTP_TRANSACTIONS:
        return record_or_load_response(method, url, **kwargs)

    logger.info('Making request to "{}"'.format(url))
    throttle = kwargs.pop('throttle', 0)
    maybe_sleep(throttle)
    # Need to prevent force from being passed to real requests module
    kwargs.pop('force', None)
    return requests.request(method, url, **kwargs)


get = functools.partial(request, 'get')
put = functools.partial(request, 'put')
post = functools.partial(request, 'post')
delete = functools.partial(request, 'delete')


class Response(object):

    response = None

    class DoesNotExist(Exception):
        pass

    def __init__(self, *args, **kwargs):
        if kwargs:
            key = kwargs['method'].lower() + kwargs['url'].lower()
            self.response = models.Response(key=key, *args, **kwargs)
        else:
            self.response = args[0]

    @property
    def method(self):
        return str(self.response.method)

    @property
    def url(self):
        return str(self.response.url)

    @property
    def ok(self):
        return bool(self.response.ok)

    @property
    def content(self):
        if isinstance(self.response.content, memoryview):
            return self.response.content.tobytes()
        if isinstance(self.response.content, bytes):
            return self.response.content
        return str(self.response.content)

    @property
    def encoding(self):
        return str(self.response.encoding)

    @property
    def headers_str(self):
        return str(self.response.headers_str)

    @property
    def status_code(self):
        return int(self.response.status_code)

    @property
    def time_made(self):
        return str(self.response.time_made)

    def save(self, *args, **kwargs):
        self.response.save()
        return self

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.response, k, v)
        return self.save()

    @classmethod
    def get(cls, url=None, method=None):
        key = method.lower() + url.lower()
        try:
            return cls(models.Response.objects.get(key=key))
        except models.Response.DoesNotExist:
            raise cls.DoesNotExist

    def json(self):
        try:
            content = self.content.decode('utf-8')
        except AttributeError:  # python 3eeeee!
            content = self.content
        return json.loads(content)

    @property
    def headers(self):
        return CaseInsensitiveDict(json.loads(self.headers_str))

    @property
    def text(self):
        return six.u(self.content)
