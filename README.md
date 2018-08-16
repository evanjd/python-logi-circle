# Python Logi Circle API

> Python 2.7/3.x API for interacting with Logi Circle cameras

[![Open Issues][open-issues-badge]][open-issues-url]

This library exposes the [Logi Circle](https://www.logitech.com/en-us/product/circle-2-home-security-camera) family of cameras as Python objects. The goal is to expose most of the functionality from Logi's 1st party applications, allowing integration of those features into other projects.

Note that the API this project is based on is not open, and therefore could change/break at any time.

I've only just started this project, so the code is rough, tests aren't done and lots of features are missing. Watch this space.

## Installation

#### Installing development master

```bash
$ pip install \
    git+https://github.com/evanjd/python-logi-circle
```

PyPi package soon.

## Features available

- Camera properties exposed:
  - ID
  - Name
  - Timezone
  - Connected status (is it powered and in range)
  - Battery %
  - Charging status
  - Model
  - Signal strength %
  - Temperature (if supported by your device)
  - Relative humidity % (if supported by your device)
- Download latest activity as MP4, either downloaded to a file or served to your application in a Requests object
- Query and filter the activity history

## Features planned

- Download still image from live feed (ASAP)
- Poll method on Camera object to update state from server (ASAP)
- Motion alerts (eventually)
- Live streaming support (eventually)
- Logi Circle CLI (eventually)

## Usage example

As this project is still in its early days, expect breaking changes!

#### Authenticate:

```python
from logi_circle import Logi

logi_api = Logi('my@email.com', 'my-password')
```

#### Download latest activity for all cameras:

```python
for camera in logi_api.cameras:
    camera.last_activity.download('%s-last-activity.mp4' % (camera.name))
```

#### Download last 24 hours activity for the 1st camera (limited to 100):

```python
from datetime import datetime, timedelta

my_camera = logi_api.cameras[0]
activities = my_camera.query_activity_history(date_filter=datetime.now() - timedelta(hours=24), date_operator='>', limit=100)
for activity in activities:
    file_name = '%s - %s.mp4' % (my_camera.name, activity.start_time.isoformat())
    activity.download(file_name)
```

#### Download last 6 hours activity for the 1st camera where duration is greater than a minute and relevance level is >= 1

```python
from datetime import datetime, timedelta

my_camera = logi_api.cameras[0]
activities = my_camera.query_activity_history(date_filter=datetime.now() - timedelta(hours=6),
        property_filter='playbackDuration > 60000 AND relevanceLevel >= 1',
        date_operator='>',
        limit=100)
for activity in activities:
    file_name = '%s - %s.mp4' % (my_camera.name, activity.start_time.isoformat())
    activity.download(file_name)
```

#### Play with camera properties

```python
for camera in logi_api.cameras:
    last_activity = camera.last_activity
    print('%s: %s' % (camera.name, ('is charging' if camera.is_charging else 'is not charging')))
    print('%s: %s%% battery remaining' % (camera.name, camera.battery_level))
    print('%s: Model number is %s' % (camera.name, camera.model))
    print('%s: Signal strength is %s%% (%s)' % (camera.name, camera.signal_strength_percentage, camera.signal_strength_category))
    print('%s: last activity was at %s and lasted for %s seconds.' % (
        camera.name, last_activity.start_time.isoformat(), last_activity.duration.total_seconds()))
```

## Release History

- 0.0.1
  - Initial commit
- 0.0.2
  - Added support for querying activity history

## Meta

Evan Bruhn – [@evanjd](https://github.com/evanjd) – evan.bruhn@gmail.com

Distributed under the MIT license. See `LICENSE` for more information.

## Thanks

- This API borrows a lot of design and some utility functions from [tchellomello's](https://github.com/tchellomello) [Python Ring Doorbell](https://github.com/tchellomello/python-ring-doorbell) project. Our projects are doing similar things with similar devices and I really appreciated how simple and readable python-ring-doorbell is.

## Contributing

They're very welcome, every little bit helps! I'm especially keen for help supporting devices that I do not own and cannot test with (eg. Circle 2 indoor & outdoor cameras).

1. Fork it (<https://github.com/evanjd/python-logi-circle/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

<!-- Markdown link & img dfn's -->

[open-issues-badge]: https://img.shields.io/github/issues/evanjd/python-logi-circle.svg
[open-issues-url]: https://github.com/evanjd/python-logi-circle/issues
