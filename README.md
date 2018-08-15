# Python Logi Circle API

> Python 2.7/3.x API for interacting with Logi Circle cameras

[![Open Issues][open-issues-badge]][open-issues-url]

This library exposes the [Logi Circle](https://www.logitech.com/en-us/product/circle-2-home-security-camera) family of cameras as Python objects. The goal is to expose most of the functionality from Logi's 1st party applications, allowing integration of those features into other projects.

Note that the API this project is based on is not open, and therefore could change/break at any time.

I've only just started this project, so the code is rough, tests aren't done and lots of features are missing. Watch this space.

## Installation

```# Installing master version
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

## Features planned

- Query activity history (ASAP)
- Download still image from live feed (ASAP)
- Poll method on Camera object to update state from server (ASAP)
- Motion alerts (eventually)
- Live streaming support (eventually)
- Logi Circle CLI (eventually)

## Usage example

As this project is still in its early days, expect breaking changes. But here's a quick example:

```
from logi_circle import Logi

logi_api = Logi('my@email.com', 'my-password')

# Loop through all available cameras
for camera in logi_api.cameras:
    print('Camera %s has %s battery remaining.' % (
        camera.name, camera.battery_level))

    last_activity = camera.last_activity
    print('Camera %s last activity was at %s and lasted for %s seconds.' % (
        camera.name, last_activity.start_time_local, last_activity.duration.total_seconds()))

    # Download activity
    last_activity.download('%s-last-activity.mp4' % (camera.name))
```

## Release History

- 0.0.1
  - Initial commit

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
