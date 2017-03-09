#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2017, Leann Mak <leannmak@139.com>
#
# This is the test module for the disconf-python-api package.
#
import sys
sys.path.append('.')

import unittest
from mock import patch, Mock

from dapi import DisconfAPIException, DisconfAPI


class TestDAPI(unittest.TestCase):
    '''
        Unit test for DAPI in Discer
    '''
    def setUp(self):
        ''' create disconf api object and set auth state true '''
        self.dapi = DisconfAPI()
        self.dapi._DisconfAPI__auth = 'i@mcookie'

    def tearDown(self):
        ''' clear auth state and remove disconf api object '''
        self.dapi._DisconfAPI__auth = None
        self.dapi = None

    def test_app_list_api(self):
        ''' api   test: ask for app list '''
        result = None
        # normal
        value = {
            'message': {},
            'sessionId': 'i@theSession',
            'success': 'true',
            'page': {
                'orderBy': None,
                'pageNo': None,
                'pageSize': None,
                'totalCount': 1,
                'result': [
                    {'id': 0, 'name': 'bye-disconf'},
                    {'id': 7, 'name': 'hey-disconf'}
                ],
                'order': None,
                'footResult': None
            }
        }
        apps = Mock(return_value=value)
        with patch.object(DisconfAPI, 'url_request', apps):
            result = self.dapi.app_list.get()
            self.assertEqual(len(result), 4)
            self.assertEqual(result['success'], 'true')
        # no api
        with self.assertRaises(DisconfAPIException) as cm:
            self.dapi.app_lists
        self.assertIn('No such Disconf API', cm.exception.message)
        # no method
        with self.assertRaises(DisconfAPIException) as cm:
            self.dapi.app_list.post()
        self.assertIn('No such API Method', cm.exception.message)
        # no login
        self.dapi._DisconfAPI__auth = None
        with self.assertRaises(DisconfAPIException) as cm:
            self.dapi.app_list.get()
        self.assertIn('Disconf-Web NOT Logged In', cm.exception.message)
