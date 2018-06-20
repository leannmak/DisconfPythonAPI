#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2017, Leann Mak <leannmak@139.com>
#
# This is the api module for the disconf-python-api package.
#
try:
    import simplejson as json
except ImportError:
    import json

import re
import urllib2
import cookielib
from poster.encode import multipart_encode
from poster.streaminghttp import StreamingHTTPHandler, \
    StreamingHTTPRedirectHandler, StreamingHTTPSHandler

import constants as C


class DisconfAPIException(Exception):
    pass


class DisconfAPI(object):
    '''
        Disconf API for Python
    '''
    __auth = None
    _state = {}
    _method = {}

    # create a new DisconfAPI Object if not exists
    def __new__(cls, *args, **kw):
        if cls not in cls._state:
            cls._state[cls] = super(DisconfAPI, cls).__new__(cls, *args, **kw)
        return cls._state[cls]

    # constructor : disconf api's [url, user_name, user_password, api_list]
    def __init__(self):
        self.__url = C.DEFAULT_DISCONF_URL
        self.__user = C.DEFAULT_DISCONF_USER_NAME
        self.__password = C.DEFAULT_DISCONF_PASSWORD
        self.__disconf_api_prefix = '/api/'
        self._disconf_api_list = {
            '^app/list$': [C.DEFAULT_METHODS[0]],
            '^app$': [C.DEFAULT_METHODS[1]],
            '^account/session$': [C.DEFAULT_METHODS[0]],
            '^account/signin$': [C.DEFAULT_METHODS[1]],
            '^account/signout$': [C.DEFAULT_METHODS[0]],
            '^env/list$': [C.DEFAULT_METHODS[0]],
            '^web/config/item$': [C.DEFAULT_METHODS[1]],
            '^web/config/file$': [C.DEFAULT_METHODS[1]],
            '^web/config/filetext$': [C.DEFAULT_METHODS[1]],
            '^web/config/versionlist$': [C.DEFAULT_METHODS[0]],
            '^web/config/list$': [C.DEFAULT_METHODS[0]],
            '^web/config/simple/list$': [C.DEFAULT_METHODS[0]],
            '^web/config/[0-9]+$': [C.DEFAULT_METHODS[0],
                                    C.DEFAULT_METHODS[3]],
            '^web/config/zk/[0-9]+$': [C.DEFAULT_METHODS[0]],
            '^web/config/download/[0-9]+$': [C.DEFAULT_METHODS[0]],
            '^web/config/downloadfilebatch$': [C.DEFAULT_METHODS[0]],
            '^web/config/item/[0-9]+$': [C.DEFAULT_METHODS[2]],
            '^web/config/file/[0-9]+$': [C.DEFAULT_METHODS[1]],
            '^web/config/filetext/[0-9]+$': [C.DEFAULT_METHODS[2]],
            '^zoo/zkdeploy$': C.DEFAULT_METHODS[0]}

    # get a DisconfAPIFactory Object
    def __getattr__(self, api):
        if api not in self.__dict__:
            api_org = re.sub('_', '/', api)
            self._method[api_org] = None
            for k, v in self._disconf_api_list.items():
                if re.match(k, api_org):
                    self._method[api_org] = v
                    break
            if not self._method[api_org]:
                self._method.pop(api_org)
                raise DisconfAPIException(
                    'No such Disconf API: %s' % api_org)
            self.__dict__[api] = DisconfAPIFactory(self, api_org)
        return self.__dict__[api]

    # user login for disconf api which returns a cookie as self.__auth
    def login(self):
        cookie = self.set_handlers()
        user_info = {'name': self.__user,
                     'password': self.__password,
                     'remember': 1}
        try:
            self.url_request(
                api='account/signin', method='POST', **user_info)
        except urllib2.HTTPError:
            raise DisconfAPIException('Disconf URL Error')
        cookie.save(ignore_discard=True, ignore_expires=True)
        self.__auth = cookie

    # check user login status for disconf
    def is_login(self):
        return self.__auth is not None

    # check user authorization for disconf
    def __checkAuth__(self):
        if not self.is_login():
            raise DisconfAPIException('Disconf-Web NOT Logged In')

    # set handlers for url request
    def set_handlers(self):
        cookie_file = C.DEFAULT_COOKIEFILE
        loglevel = C.DEFAULT_LOGLEVEL
        handlers = [
            StreamingHTTPHandler(debuglevel=loglevel),
            StreamingHTTPRedirectHandler,
            StreamingHTTPSHandler(debuglevel=loglevel)]
        cookie = cookielib.MozillaCookieJar(cookie_file)
        handlers.append(urllib2.HTTPCookieProcessor(cookie))
        opener = urllib2.build_opener(*handlers)
        urllib2.install_opener(opener)
        self.__urllib = urllib2
        return cookie

    # request a disconf api: post/get/put/delete
    def url_request(self, api, method, **params):
        api = '%s%s' % (self.__disconf_api_prefix, api)
        method = method.upper()
        if params and (method == 'GET' or method == 'PUT'):
            api += '?'
            for k, v in params.items():
                api += '%s=%s&' % (k, v)
        data, headers = multipart_encode(params)
        headers["User-Agent"] = "DisconfAPI"
        request = self.__urllib.Request(
            url='%s%s' % (self.__url, api), data=data, headers=headers)
        request.get_method = lambda: method
        opener = self.__urllib.urlopen(
            url=request, timeout=C.DEFAULT_DISCONF_TIMEOUT)
        content = opener.read()
        try:
            content = json.loads(content)
        except ValueError:
            pass
        return content


"""
   Decorate Method
"""


# add to verify authorization
def check_auth(func):
    def ret(self, *args, **params):
        self.__checkAuth__()
        return func(self, *args, **params)
    return ret


# add to get pure disconf api response
def disconf_api(func):
    def wrapper(self, method, **params):
        return self.url_request(method=method, **params)
    return wrapper


class DisconfAPIFactory(object):
    """
        Disconf API Factory
    """
    # the construtor
    def __init__(self, dapi, api):
        # a DisconfAPI Object
        self.__dapi = dapi
        # a disconf api like 'app/list', ...
        self.__api = api

    # verify user authorization for disconf using the DisconfAPI Object
    def __checkAuth__(self):
        self.__dapi.__checkAuth__()

    # call a api method like post/get/put/delete of DisconfAPIFactory
    def __getattr__(self, method):
        def func(**params):
            if method.upper() not in self.__dapi._method[self.__api]:
                raise DisconfAPIException(
                    'No such API Method: %s %s' % (method.upper(), self.__api))
            return self.proxy_api(method=method, **params)
        return func

    # request a disconf api using the DisconfAPI Object
    def url_request(self, method, **params):
        return self.__dapi.url_request(
            api=self.__api, method=method, **params)

    # the request proxy method
    @check_auth
    @disconf_api
    def proxy_api(self, method, **params):
        pass
