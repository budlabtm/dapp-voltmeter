from setuptools import setup

setup(
    name='desktop_client_hfr_voltage',
    version='1.0',
    packages=['desktop_client_hfr_voltage'],
    setup_requires=['setuptools'],
    install_requires=[
        'PyQt6',
        'pyqtgraph',
        'numpy',
        'scipy',
        'paho-mqtt',
    ]
)
