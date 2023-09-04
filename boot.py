"""
NOTE:
This boot.py file allows both the Raspberry Pico and a host computer to write to the filesystem at the same time.
It's using the "disable_concurrent_write_protection" to achieve this. When True, the check that makes sure the
underlying filesystem data is written by one computer is disabled. Disabling the protection allows CircuitPython and
a host to write to the same filesystem with the risk that the filesystem will be corrupted.
"""
import storage

storage.remount("/", readonly=False, disable_concurrent_write_protection=True)