"""
boot_write_no_gpio.py file for Pico data logging without using GPIO Pint.
Rename this file to boot_write_using_gpio.py to enable event logging without using GPIO pins.
If this file is present (named as = boot_write_using_gpio.py) when the pico starts up, make the filesystem writeable by CircuitPython.
"""
import storage

storage.remount("/", readonly=False)