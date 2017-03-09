# Disconf Python API
[![Build Status](https://travis-ci.org/leannmak/DisconfPythonAPI.svg?branch=master)](https://travis-ci.org/leannmak/DisconfPythonAPI)
[![Download Status](https://img.shields.io/badge/download-1024%2Fmonth-green.svg)](https://github.com/leannmak/DisconfPythonAPI)

A simple way to connect to Disconf-Web api. (c) 2017.

## Prerequests

* python 2.7
* git
* easy_install && pip
* pyenv && pyenv-virtualenv

## Usage

```
$ https://github.com/leannmak/DisconfPythonAPI.git
$ cd DisconfPythonAPI
$ pip install -r requirements.txt
```

## Examples

```
from dapi import DisconfAPI

dapi = DisconfAPI()
dapi.login()
# GET /api/app/list
app = dapi.app_list.get()['page']['result'][0]
# GET /api/env/list
env = dapi.env_list.get()['page']['result'][0]
# GET /api/web/config/versionlist
version = dapi.web_config_versionlist.get(
    **{'appId': app['id']})['page']['result'][0]
# POST /api/web/config/file
with open('test', 'rb') as myfile:
    print dapi.web_config_file.post(
        **{'appId': app['id'], 'envId': env['id'],
           'version': version, 'myfilerar': myfile})
```

## Disconf-Web API List

```
http://disconf.readthedocs.io/zh_CN/latest/tutorial-web/src/12-open-api-for-web.html
```
