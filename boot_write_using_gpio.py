import board
import digitalio
import storage

# Assigning a pin to control the r/w of circuitpython
switch = digitalio.DigitalInOut(board.GP18)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

# The pin state controls the r/w ability
# If pin = ground --> returns false --> CircuitPython can write to itself
# If pin = float --> returns true --> CircuitPython cannot write to itself
storage.remount("/", switch.value)
