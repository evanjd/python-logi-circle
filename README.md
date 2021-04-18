# Python Logi Circle API

> Python 3.6+ API for interacting with Logi Circle cameras, written with asyncio and aiohttp.

[![PyPI version](https://badge.fury.io/py/logi-circle.svg)](https://badge.fury.io/py/logi-circle)
![License](https://img.shields.io/packagist/l/doctrine/orm.svg)
[![Build Status][github-actions-badge]][github-actions-url]
[![Coverage Status][coverage-badge]][coverage-url]
[![Open Issues][open-issues-badge]][open-issues-url]

This library exposes the [Logi Circle](https://www.logitech.com/en-us/product/circle-2-home-security-camera) family of cameras as Python objects, wrapping Logi Circle's official API.

[Now available as a Home Assistant integration!](https://www.home-assistant.io/components/logi_circle/) :tada:

There are two versions of this API:

- `2.x` - which targets the public API ([`master` branch](https://github.com/evanjd/python-logi-circle/tree/master))
- [`1.x`](https://github.com/evanjd/python-logi-circle/tree/private-api) - which targets the private API **(you are here)**

## Installation

#### Installing release version

```bash
$ pip install logi-circle
```

#### Installing development master

```bash
$ pip install \
    git+https://github.com/evanjd/python-logi-circle
```

## Features available

- Download real-time live stream data to disk or serve to your application as a raw bytes object
- Query/filter the activity history by start time and/or activity properties (duration, relevance)
- Download any activity video to disk or serve to your application as a raw bytes object
- Download still images from camera to disk or serve to your application as a raw bytes object
- Set streaming mode, privacy mode, LED status, speaker volume, microphone gain and other properties of camera
- On-demand polling from server to update camera properties
- Camera properties exposed:
  - ID
  - Node ID
  - Name
  - Live image (as JPEG)
  - Last activity
  - Timezone
  - Connected status (is it powered and in range)
  - Streaming status (is currently streaming and capable of recording activities)
  - Privacy mode (is it recording activities)
  - Firmware version
  - Battery %
  - Charging status
  - Model
  - Model generation (eg. 1st gen, 2nd gen)
  - Mount (eg. Wired, Wireless)
  - Connected Wifi SSID
  - Signal strength %
  - IP address
  - MAC address
  - Microphone status and gain
  - Speaker status and volume
  - LED enabled
  - Plan name
  - Temperature (if supported by your device)
  - Relative humidity % (if supported by your device)
- Activity properties exposed:
  - Start time (local or UTC)
  - End time (local or UTC)
  - Duration
  - Relevance level (indicating whether people/objects were detected)

## Features planned

- Motion alerts (eventually)
- Logi Circle CLI (eventually)
- Speaker support (maybe)

## Usage example

#### Setup and authenticate:

```python
import asyncio
from logi_circle import Logi

logi_api = Logi('my@email.com', 'my-password')
```

#### Grab latest still image for each camera:

```python
async def get_snapshot_images():
    for camera in await logi_api.cameras:
        await camera.get_snapshot_image('%s.jpg' % (camera.name))
    await logi_api.logout()

loop = asyncio.get_event_loop()
loop.run_until_complete(get_snapshot_images())
loop.close()
```

#### Download latest activity for all cameras:

```python
async def get_latest_activity():
    for camera in await logi_api.cameras:
        last_activity = await camera.last_activity
        await last_activity.download('%s-last-activity.mp4' % (camera.name))
    await logi_api.logout()

loop = asyncio.get_event_loop()
loop.run_until_complete(get_latest_activity())
loop.close()
```

#### Stream live stream data to disk:

```python
async def get_livestream():
    camera = (await logi_api.cameras)[0]
    filename = '%s-livestream.mp4' % (camera.name)

    # Grab 1 minute of footage from live stream
    await camera.record_livestream(filename=filename, duration=timedelta(minutes=1))

    await logi_api.logout()

loop = asyncio.get_event_loop()
loop.run_until_complete(get_livestream())
loop.close()
```

#### Download last 24 hours activity for the 1st camera (limited to 100, 5 at a time):

```python
from datetime import datetime, timedelta

# Don't go nuts with parallelising downloads, you'll probably hit rate limits.
semaphore = asyncio.Semaphore(5)

async def download(camera, activity):
    async with semaphore:
        file_name = '%s - %s.mp4' % (camera.name,
                                     activity.start_time.isoformat())
        await activity.download(file_name)

async def run():
    my_camera = (await logi_api.cameras)[0]
    activities = await my_camera.query_activity_history(date_filter=datetime.now() - timedelta(hours=24), date_operator='>', limit=100)
    tasks = []

    for activity in activities:
        task = asyncio.ensure_future(download(my_camera, activity))
        tasks.append(task)

    await asyncio.gather(*tasks)
    logi_api.logout()

loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run())
loop.run_until_complete(future)
```

#### Turn off streaming for all cameras

```python
async def disable_streaming_all():
    for camera in await logi_api.cameras:
        if camera.streaming_mode is True:
            await camera.set_streaming_mode(False)
            print('%s is now off.' % (camera.name))
        else:
            print('%s is already off.' % (camera.name))
    await logi_api.logout()

loop = asyncio.get_event_loop()
loop.run_until_complete(disable_streaming_all())
loop.close()
```

#### Play with camera properties

```python
async def play_with_props():
    for camera in await logi_api.cameras:
        last_activity = await camera.last_activity
        print('%s: %s' % (camera.name,
                          ('is charging' if camera.is_charging else 'is not charging')))
        print('%s: %s%% battery remaining' %
              (camera.name, camera.battery_level))
        print('%s: Battery saving mode is %s' %
              (camera.name, 'on' if camera.battery_saving else 'off'))
        print('%s: Model number is %s' % (camera.name, camera.model))
        print('%s: Model generation is %s' % (camera.name, camera.model_generation))
        print('%s: Mount is %s' % (camera.name, camera.mount))
        print('%s: Signal strength is %s%% (%s)' % (
            camera.name, camera.signal_strength_percentage, camera.signal_strength_category))
        print('%s: last activity was at %s and lasted for %s seconds.' % (
            camera.name, last_activity.start_time.isoformat(), last_activity.duration.total_seconds()))
        print('%s: Firmware version %s' % (camera.name, camera.firmware))
        print('%s: IP address is %s' % (camera.name, camera.ip_address))
        print('%s: MAC address is %s' % (camera.name, camera.mac_address))
        print('%s: Microphone is %s and gain is set to %s (out of 100)' % (
            camera.name, 'on' if camera.microphone_on else 'off', camera.microphone_gain))
        print('%s: Speaker is %s and volume is set to %s (out of 100)' % (
            camera.name, 'on' if camera.speaker_on else 'off', camera.speaker_volume))
        print('%s: LED is %s' % (
            camera.name, 'on' if camera.led_on else 'off'))
        print('%s: Privacy mode is %s' % (
            camera.name, 'on' if camera.privacy_mode else 'off'))
        print('%s: Subscribed to plan %s' % (
            camera.name, camera.plan_name))
    await logi_api.logout()

loop = asyncio.get_event_loop()
loop.run_until_complete(play_with_props())
loop.close()
```

## Release History

- 0.0.1
  - Initial commit
- 0.0.2
  - Added support for querying activity history
- 0.0.3
  - Added support for retrieving the latest still image for a given camera
- 0.0.4
  - Replaced requests with aiohttp
  - Added support for turning camera on & off
  - Added update() method to Camera object to refresh data from server
- 0.1.0
  - Added preliminary support for live streams (to be improved)
- 0.1.1
  - Fixed timing bug causing live streams to download at half real-time speeds
  - Live streams will now automatically append to an existing file (instead of overwriting)
  - Added a bunch of new camera properties
  - Added support for setting privacy mode, LED status, speaker status, speaker volume, microphone status and microphone gain
- 0.1.2
  - Removed `is_streaming` property as I've discovered this is not a binary sensor for 2nd gen cameras. Replaced with `streaming_mode`.
  - `set_streaming_mode` now accepts a string instead a boolean.
  - Added `model_name` property.
- 0.1.3
  - Renamed `model_name` to `model_type` to better reflect what the property reports.
  - Added rudimentary feature detection, exposed via `supported_features` and `supports_feature` methods and derived from model type.
- 0.1.4
  - Fixed missing `last_activity_time` sensor on 2nd gen wired cameras.
- 0.1.5
  - Added `get_livestream_image` and `record_livestream` methods to camera object, allowing snapshots (images) and videos of a specified length to be recorded from the camera's livestream (both requiring ffmpeg)
- 0.1.6
  - `set_streaming_mode` now accepts a boolean instead of string.
  - Removed `model_type` property, replaced with `mount` and `model_generation` properties.
  - Added `battery_saving` property and `set_battery_saving_mode` method
- 0.1.7
  - Implemented rudimentary throttling on `update()` requests

## Meta

Evan Bruhn – [@evanjd](https://github.com/evanjd) – evan.bruhn@gmail.com

Distributed under the MIT license. See `LICENSE` for more information.

## Thanks

- This API borrows a lot of design and some utility functions from [tchellomello's](https://github.com/tchellomello) [Python Ring Doorbell](https://github.com/tchellomello/python-ring-doorbell) project. Our projects are doing similar things with similar devices and I really appreciated how simple and readable python-ring-doorbell is.
- Thanks [sergeymaysak](https://github.com/sergeymaysak) for suggesting a switch to aiohttp and for a tip to make downloading snapshot images more reliable.

## Contributing

They're very welcome, every little bit helps! I'm especially keen for help supporting devices that I do not own and cannot test with (eg. Circle 2 wired and wireless cameras).

1. Raise an issue with your feature request or bug before starting work.
2. Fork it (<https://github.com/evanjd/python-logi-circle/fork>).
3. Create your feature branch (`git checkout -b feature/fooBar`).
4. Commit your changes (`git commit -am 'Add some fooBar'`).
5. Add/update tests if needed, then run `tox` to confirm no test failures.
6. Push to the branch (`git push origin feature/fooBar`).
7. Create a new pull request!

<!-- Markdown link & img dfn's -->

[open-issues-badge]: https://img.shields.io/github/issues/evanjd/python-logi-circle.svg
[open-issues-url]: https://github.com/evanjd/python-logi-circle/issues
[github-actions-badge]: https://github.com/evanjd/python-logi-circle/actions/workflows/python-package.yml/badge.svg
[github-actions-url]: https://github.com/evanjd/python-logi-circle/actions/workflows/python-package.yml
[coverage-badge]: https://img.shields.io/coveralls/github/evanjd/python-logi-circle/master.svg
[coverage-url]: https://coveralls.io/github/evanjd/python-logi-circle?branch=master
