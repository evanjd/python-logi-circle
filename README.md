# Python Logi Circle API

> Python 3.6+ API for interacting with Logi Circle cameras, written with asyncio and aiohttp.

[![PyPI version](https://badge.fury.io/py/logi-circle.svg)](https://badge.fury.io/py/logi-circle)
![License](https://img.shields.io/packagist/l/doctrine/orm.svg)
[![Build Status][travis-badge]][travis-url]
[![Coverage Status][coverage-badge]][coverage-url]
[![Open Issues][open-issues-badge]][open-issues-url]

This library exposes the [Logi Circle](https://www.logitech.com/en-us/product/circle-2-home-security-camera) family of cameras as Python objects, wrapping Logi Circle's official API.

[Now available as a Home Assistant integration!](https://www.home-assistant.io/components/logi_circle/) :tada:

**The API this library wraps is not yet publicly available.** If you want something you can use today, check out the [v0.1 branch](https://github.com/evanjd/python-logi-circle/tree/v0.1.x). Please note that v0.1.x wraps Logitech's private API and won't be supported once the public API is released.

## Features implemented

- Download real-time live stream data to disk or serve to your application as a raw bytes object
- Download any activity video to disk or serve to your application as a raw bytes object
- Download still images from camera to disk or serve to your application as a raw bytes object
- Query/filter the activity history by start time and/or activity properties (duration, relevance)
- Set name, timezone, streaming mode and privacy mode of a given camera
- On-demand polling from server to update camera properties
- Subscribe to WebSocket API to handle camera property updates and activities pushed from API
- Read camera properties (see "play with props" example)

## Features planned

- Update Home Assistant integration to support v0.2.x version of this library (dependent on Logitech's public release of their API)

## Usage example

#### Setup and authenticate:

Requires API access from Logitech (not yet publicly available).

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

    asyncio.get_event_loop().run_until_complete(authorize())
```

#### Grab latest still image:

```python
async def get_snapshot_images():
    for camera in await logi.cameras:
        if camera.streaming:
            await camera.live_stream.download_jpeg(filename='%s.jpg' % (camera.name),
                                                   quality=75,  # JPEG compression %
                                                   refresh=False)  # Don't force cameras to wake
    await logi.close()

asyncio.get_event_loop().run_until_complete(get_snapshot_images())
```

#### Download 30s of live stream video from 1st camera (requires ffmpeg):

```python
async def get_livestream():
    camera = (await logi.cameras)[0]
    filename = '%s-livestream.mp4' % (camera.name)

    await camera.live_stream.download_rtsp(filename=filename,
                                           duration=30)

    await logi.close()

asyncio.get_event_loop().run_until_complete(get_livestream())
```

#### Download latest activity for all cameras:

```python
async def get_latest_activity():
    for camera in await logi.cameras:
            last_activity = await camera.last_activity
            if last_activity:
                # Get activity as image
                await last_activity.download_jpeg(filename='%s-last-activity.jpg' % (camera.name))
                # Get activity as video
                await last_activity.download_mp4(filename='%s-last-activity.mp4' % (camera.name))

    await logi.close()

asyncio.get_event_loop().run_until_complete(get_latest_activity())
```

#### Turn off streaming for all cameras:

```python
async def disable_streaming_all():
    for camera in await logi.cameras:
        if camera.streaming:
            await camera.set_config(prop='streaming',
                                    value=False)
            print('%s is now off.' % (camera.name))
        else:
            print('%s is already off.' % (camera.name))
    await logi.close()

asyncio.get_event_loop().run_until_complete(disable_streaming_all())
```

#### Subscribe to camera events with WS API:

```python
async def subscribe_to_events():
    subscription = await logi.subscribe(['accessory_settings_changed',
                                         "activity_created",
                                         "activity_updated",
                                         "activity_finished"])
    while True:
        await subscription.get_next_event()

asyncio.get_event_loop().run_until_complete(subscribe_to_events())
```

#### Play with props:

```python
async def play_with_props():
    for camera in await logi.cameras:
        last_activity = await camera.get_last_activity()
        print('%s: %s' % (camera.name,
                          ('is charging' if camera.charging else 'is not charging')))
        if camera.battery_level >= 0:
            print('%s: %s%% battery remaining' %
                  (camera.name, camera.battery_level))
            print('%s: Battery saving mode is %s' %
                  (camera.name, 'on' if camera.battery_saving else 'off'))
        print('%s: Model number is %s' % (camera.name, camera.model))
        print('%s: Mount is %s' % (camera.name, camera.mount))
        print('%s: Signal strength is %s%% (%s)' % (
            camera.name, camera.signal_strength_percentage, camera.signal_strength_category))
        if last_activity:
            print('%s: last activity was at %s and lasted for %s seconds.' % (
                camera.name, last_activity.start_time.isoformat(), last_activity.duration.total_seconds()))
        print('%s: Firmware version %s' % (camera.name, camera.firmware))
        print('%s: MAC address is %s' % (camera.name, camera.mac_address))
        print('%s: Microphone is %s and gain is set to %s (out of 100)' % (
            camera.name, 'on' if camera.microphone else 'off', camera.microphone_gain))
        print('%s: Speaker is %s and volume is set to %s (out of 100)' % (
            camera.name, 'on' if camera.speaker else 'off', camera.speaker_volume))
        print('%s: LED is %s' % (
            camera.name, 'on' if camera.led else 'off'))
        print('%s: Recording mode is %s' % (
            camera.name, 'on' if camera.recording else 'off'))
    await logi.close()

asyncio.get_event_loop().run_until_complete(play_with_props())
```

## Thanks

- This first version of API borrowed a lot of the design and some utility functions from [tchellomello's](https://github.com/tchellomello) [Python Ring Doorbell](https://github.com/tchellomello/python-ring-doorbell) project. It made a great template for how to implement a project like this, so thanks!
- Thanks [sergeymaysak](https://github.com/sergeymaysak) for suggesting a switch to aiohttp, it made integrating with Home Assistant much easier.
- Logitech for reaching out and providing support to reimplement this library using their official API.

## Contributing

Pull requests are very welcome, every little bit helps!

1. Raise an issue with your feature request or bug before starting work.
2. Fork it (<https://github.com/evanjd/python-logi-circle/fork>).
3. Create your feature branch (`git checkout -b feature/fooBar`).
4. Commit your changes (`git commit -am 'Add some fooBar'`).
5. Add/update tests if needed, then run `tox` to confirm no test failures.
6. Push to the branch (`git push origin feature/fooBar`).
7. Create a new pull request!

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
