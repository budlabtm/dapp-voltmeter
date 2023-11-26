### Institute of Nuclear Physics
# Dual-Channel Voltage Flow Analizer

Provides real-time visualization and mathematical processing of voltage from the high-frequency resonator.

## Installation

The application is written in Python, and therefore installation in a special virtual environment is recommended.

> Virtual environments should be organized as containers.

If there is no virtual environment already installed, it can be done using following command:

``` shell
sudo apt install python3-virtualenv
```

After installing virtual environment, create new one:

``` shell
virtualenv ~/venv/env{x}-{y}
```

where `{x}` and `{y}` - major and minor parts of environment version respectively.

To activate virtual environment:

``` shell
source ~/venv/env{x}-{y}/bin/activate
```

> It is recommended to add previous command to user's configuration script (e.g. ~/.bashrc). In this case, the current version of the virtual environment (and the applications installed in it) will be activated automatically. Be sure to update it, after new version of environment installed.

To install application module itself, execute the following command:

``` shell
pip install -e git+https://github.com/Institute-of-Nuclear-Physics/desktop-client-hfr-voltage.git@v1.0#egg=desktop_client_hfr_voltage
```

After that, application ready to run:

``` shell
python -m desktop_client_hfr_voltage
```
