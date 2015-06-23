# MouseTrap

* Version: 3.17.4-pre
* License: GPL v2.0 (see LICENSE)


## Software Requirements

* Linux (developed on Fedora 20 and Ubuntu)
* Python 2.7+
* PyYAML 3
* OpenCV 2+
* Python-Xlib 0.12+
* Gnome Common
* Python setup-tools
* Numpy

## Install Dependencies for Fedora21, Python3, OpenCV3
Uses script bin/install_dependencies_fedora21_python3_opencv3.bash
to install the mousetrap dependencies for Fedora21, Python3 and OpenCV3.
* Using terminal, navigate to the mousetrap folder.
* Enter the following command in the terminal:
  ./bin/install_dependencies_fedora21_python3_opencv3.bash
* This will begin the installation process of the dependencies:
  *     Installation of Python, gnome common and python setup-tools
  *     Installs Numpy
  *     Installs Python library x-lib
  *     Installs openCV 3
* Let Script run through until finished.


## Download, build, and install MouseTrap using autotools

    $ git clone git://git.gnome.org/mousetrap
    $ cd mousetrap
    $ ./autogen.sh
    $ make
    $ sudo make install

By default Python 2.7 is used. To use Python 3, set $PYTHON to the
path to the python3 executable. For example, assuming python3 is in your
$PATH:

    $ PYTHON="$(which python3)" ./autogen.sh

Options passed to autogen.sh will be passed on to gnome-autogen.sh and
ultimately configure. So, for example, you can override the guessed prefix by
passing --prefix to autogen.sh:

    $ ./autogen.sh --prefix=/usr/local

Note: prefix is guessed based on the installed location of Python.


## Download, build, and install MouseTrap using pip

    $ git clone git://git.gnome.org/mousetrap
    $ cd mousetrap
    $ sudo pip install .


## Uninstal MouseTrap using autotools

    $ sudo make uninstall


## Running MouseTrap

    $ mousetrap


## Stopping MouseTrap

From the terminal in which you started MouseTrap

    ^C


## Using MouseTrap

By default, MouseTrap tracks your face, allowing you to control the
mouse pointer using a joystick metaphor. When you look left,
the pointer moves left; look right, it moves right; look up, it moves up;
look down, it moves down; look straight ahead, it stops moving. To click,
close your left eye for about 1.5 seconds.


## Configuring MouseTrap

To customize MouseTrap's configuration, place a copy of the annotated built-in
configuration in ~/.mousetrap.yaml, and then edit it.

    mousetrap --dump-annotated > ~/.mousetrap.yaml

MouseTrap loads its configuration from the following locations in order. Later
locations may override values of those that come before it.

* Built-in: something like `/usr/local/lib/python2.7/mousetrap/mousetrap.yaml`
* User: `~/.mousetrap.yaml`
* Command-line: `mousetrap --config path/to/myconfig.yaml`

Load and dump configuration:

    mousetrap --dump-config

Dump built-in annotated configuration.

    mousetrap --dump-annotated


## Translating MouseTrap

Use `src/mousetrap/locale/_language_/LC_MESSAGES/mousetrap.po` as your template (POT file).


## Writing a plugin for MouseTrap

### Example plugin class

```python
# Import the interface for plugins.
import mousetrap.plugins.interface as interface

# Create a logger for logging.
import logging
LOGGER = logging.getLogger(__name__)


# Define a class that inherits from mousetrap.plugins.interface.Plugin
class MyPlugin(interface.Plugin):

    # Define a constructor that takes an instance of mousetrap.config.Config
    # as the first parameter (after self).
    def __init__(self, config):
        self._config = config

        # Access class configuration by using self as a key.
        # Here we retrieve 'x' from our class configuration.
        self._x = config[self]['x']

    # Define a run method that takes an instance of mousetrap.main.App as the
    # first parameter (after self). Run is called on each pass of the main
    # loop.
    def run(self, app):

        # App contains data shared between the system and plugins.
        # See mousetrap.main.App for attributes that are defined by mousetrap.
        # For example, we can access the pointer:
        app.pointer.set_position((0, 0))

        # We can access attributes that are populated by other plugins.
        image = app.image

        # We can make attributes available to other plugins by adding them
        # to app.
        app.greeting = 'Just saying %s!' % (self._x)
```

### 2. Edit configuration file to tell MouseTrap about your plugin.

```yaml
#~/.mousetrap.yaml

assembly:
- mousetrap.plugins.camera.CameraPlugin     # sets app.image
- mousetrap.plugins.display.DisplayPlugin   # displays app.image in a window
- python.path.to.MyPlugin                   # runs after CameraPlugin

classes:
  python.path.to.MyPlugin:
    x: hi
```

For more examples, see the plugins in `src/mousetrap/plugins`.


## Developing

Makefile targets
* `all` - builds
* `install` - installs
* `run` - runs without install
* `check` - tests
* `lint` - style checker
* `clean` - deletes files created by `make` or `make all`
* `devclean` - deletes all files ignored by git
* `pristine` - `devclean` plus deletes all files not tracked by git
* `dist` - makes distribution
* `distcheck` - makes and tests distribution
* `distclean` - cleans extra files generated by `dist`
