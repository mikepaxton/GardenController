"""
******************* NOTE:  This code is by no means done.
******************* Although it is technically working as is, there are additional features I want to add.
Author: Mike Paxton
Creation Date: 08/06/2023
CircuitPython Version 8.2

The purpose of this program is to control 8 relays, one for each of my garden beds using a Raspberry Pico.
I'm using an 8 channel relay along with 8 buttons to control each channel.
Incorporate a scheduling system.


"""
import os, ssl, wifi, socketpool, adafruit_requests, ipaddress
import board
import time
from digitalio import DigitalInOut, Direction, Pull
import rtc
import circuitpython_schedule as schedule


# Constants for relay state: RELAY_ACTIVE and RELAY_INACTIVE
# RELAY_ACTIVE is used to indicate that a relay is turned on or activated.
# RELAY_INACTIVE is used to indicate that a relay is turned off or deactivated.
# In this code, the relays are controlled by setting their values to these constants.
# For most relay modules, activating a relay requires setting its GPIO pin to a logic level that energizes the relay.
# The actual behavior may depend on how the relay module is connected and whether it is active LOW or active HIGH.
# These constants help to provide clear and consistent names for the relay states throughout the code.
# If your relay module operates differently, you can adjust the values of these constants accordingly.
RELAY_ACTIVE = False
RELAY_INACTIVE = True

# GPIO Pin Definitions in lists
# 'relay_pins' contains the GPIO pins used for controlling the relays, and 'button_pins' contains the GPIO pins
# used for reading the button states.
# You can simply add or remove relays and buttons to match your gardens setup.
relay_pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7]
button_pins = [board.GP8, board.GP9, board.GP10, board.GP11, board.GP12, board.GP13, board.GP14, board.GP15]


# Create Lists "relays" and "buttons".  Define the directions of both and set the relay's at startup to inactive.
relays = [DigitalInOut(pin) for pin in relay_pins]
buttons = [DigitalInOut(pin) for pin in button_pins]

# Set the relays as output and set them to inactive or off.  We don't want the relays to all start at once when
# the system boots up.
for relay in relays:
    relay.direction = Direction.OUTPUT
    relay.value = RELAY_INACTIVE

for button in buttons:
    button.direction = Direction.INPUT
    button.pull = Pull.UP

# Define the socket pool as a global variable at the module level+
pool = None


def wifi_connect():
    print("Connecting to WiFi...")
    # Connect to your Wi-Fi network using the provided SSID and password
    wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
    print("Connected to WiFi")
    print("My IP address is", wifi.radio.ipv4_address)


def turn_off_wifi():  # Not using this.  TODO: Need to determine if I should turn off the radio when not in use.
    wifi.radio.disconnect()


def get_world_time():
    global pool  # Access the global pool variable
    if pool is None:
        pool = socketpool.SocketPool(wifi.radio)
    request = adafruit_requests.Session(pool, ssl.create_default_context())
    url = "https://worldtimeapi.org/api/timezone/"
    timezone = "America/Los_Angeles"  # Change your timezone to match.
    url = url + timezone
    print(f"Accessing URL \n{url}")
    response = request.get(url)
    json_data = response.json()
    # Extract the Unix timestamp and raw_offset from the JSON data
    unixtime = json_data["unixtime"]
    raw_offset = json_data["raw_offset"]
    # Check for daylight savings time
    dst_offset = json_data.get("dst_offset", 0)
    # Calculate the location time by adding the Unix timestamp and raw_offset
    location_time = unixtime + raw_offset
    # Determine if Daylight Saving Time (DST) is in effect. If not found set to False.
    dst_active = bool(json_data.get("dst", False))
    print(f"Is DST Active: {dst_active}")
    # Adjust for daylight savings time if needed.
    if dst_active:
        location_time += dst_offset
    # Convert the location time to a time.struct_time object representing the current time
    current_time = time.localtime(location_time)
    return current_time


def set_rtc_datetime():
    current_time = get_world_time()
    # Set the internal clock of the RTC (Real-Time Clock) using the current_time struct_time object
    clock = rtc.RTC()
    clock.datetime = time.struct_time(current_time)
    current_date_time = clock.datetime
    print(f"Current Time: {current_date_time}")


def control_relays():
    # This function continuously monitors the state of the relay buttons and controls the corresponding relays.

    while True:  # Continue looping indefinitely
        for i, button_state in enumerate(buttons):
            # Check if the button has been pressed (active LOW), indicating that the relay should be activated.
            if not button_state.value:
                # Activate the corresponding relay by setting its value to RELAY_ACTIVE.
                relays[i].value = RELAY_ACTIVE
                # Print a message indicating that the relay has been activated.
                print(f"Relay {i + 1} Activated")
            else:
                # If the button is not pressed (active HIGH), set the corresponding relay value to RELAY_INACTIVE.
                # to turn off the relay.
                relays[i].value = RELAY_INACTIVE
                # Print a message indicating that the relay has been turned off.
                print(f"Relay {i + 1} Off")

        time.sleep(0.1)  # Introduce a small delay (0.1 seconds) for debounce and smoother button handling.

        time.sleep(1)   # Additional delay (1 second) to avoid rapid looping and reduce processor load.


# Call the function at boot to set the date and time from the internet.
wifi_connect()
set_rtc_datetime()
control_relays()
