# Python Logi Circle API (WIP rewrite)

> Python 3.6+ API for interacting with Logi Circle cameras, written with asyncio and aiohttp.

[![PyPI version](https://badge.fury.io/py/logi-circle.svg)](https://badge.fury.io/py/logi-circle)
![License](https://img.shields.io/packagist/l/doctrine/orm.svg)
[![Build Status][travis-badge]][travis-url]
[![Coverage Status][coverage-badge]][coverage-url]
[![Open Issues][open-issues-badge]][open-issues-url]

This library exposes the [Logi Circle](https://www.logitech.com/en-us/product/circle-2-home-security-camera) family of cameras as Python objects, wrapping Logi Circle's official API.

[Now available as a Home Assistant integration!](https://www.home-assistant.io/components/logi_circle/) :tada:

**This branch hosts a WIP rewrite based on Logitech's public API. It is not yet fully functional. This is intended to replace the 0.1.x wrapper (based on the private API) once completed.**

## Usage example

#### Setup and authenticate:

Requires API access from Logitech. Link to obtain that access TBA.

```python
import asyncio
from logi_circle import LogiCircle

logi = LogiCircle(client_id='your-client-id',
                  client_secret='your-client-secret',
                  redirect_uri='https://your-redirect-uri',
                  api_key='your-api-key')

if not logi.authorized:
    print('Navigate to %s and enter the authorization code passed back to your redirect URI' % (logi.authorize_url))
    code = input('Code: ')

    async def authorize():
        await logi.authorize(code)
        await logi.close()

    asyncio.get_event_loop().run_until_complete(authorize()).close()
```

## Meta

Evan Bruhn – [@evanjd](https://github.com/evanjd) – evan.bruhn@gmail.com

Distributed under the MIT license. See `LICENSE` for more information.

<!-- Markdown link & img dfn's -->

[open-issues-badge]: https://img.shields.io/github/issues/evanjd/python-logi-circle.svg
[open-issues-url]: https://github.com/evanjd/python-logi-circle/issues
[travis-badge]: https://travis-ci.com/evanjd/python-logi-circle.svg?branch=master
[travis-url]: https://travis-ci.com/evanjd/python-logi-circle
[coverage-badge]: https://img.shields.io/coveralls/github/evanjd/python-logi-circle/master.svg
[coverage-url]: https://coveralls.io/github/evanjd/python-logi-circle?branch=master
