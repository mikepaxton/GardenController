"""
****************************************************************************************************************
NOTE:  This code is by no means done.  It is a work in progress.
Most of the time I only commit working code to GitHub but there still is a chance some of the code may fail.
I don't always have time to check the code in a working environment.
****************************************************************************************************************

Author: Mike Paxton
Creation Date: 08/07/2023
CircuitPython Version 8.2.2

The purpose of this program is to control 8 relays for watering each of my garden beds using a Raspberry Pico and
CircuitPython.  The system is being designed to work off a solar system so controlling battery usage is paramount.

I'm using an 8 channel relay along with 8 buttons to control each relay channel.

I've incorporated a simple automated scheduling system which allows for specifying the days of the week, time of day
and duration each garden bed relay runs.  Currently, each garden bed relay can only run once per day using the
automated scheduling.  However, you can always use the manual button to activate a relay and let it run the desired
amount of time, then manually turn it off.

A Pause Schedule Button has been added which when pressed will put the automated scheduling system on hold. This works
great for days when it's raining, and you don't want the system to run.
You can still use the manual relay buttons to run any of the relays while scheduling is paused.


"""
import os, ssl, wifi, socketpool, adafruit_requests
from digitalio import DigitalInOut, Direction, Pull
import board, time, rtc

# Setting debug too True will print out messages to REPL.  Set it too False to keep the processor load down.
debug = False


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

# Define the GPIO pins for controlling the relays and reading the button states using lists.
# The first relay in the relay_pins list is associated with the first button in the button_pins list,
# the second relay with the second button, and so on. This organization allows you to easily map buttons to specific
# relays for control and monitoring purposes.
relay_pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7]
button_pins = [board.GP8, board.GP9, board.GP10, board.GP11, board.GP12, board.GP13, board.GP14, board.GP15]


# Create DigitalInOut instances for each GPIO pin in 'relay_pins' and 'button_pin' to control the corresponding
# relays and buttons.
relays = [DigitalInOut(pin) for pin in relay_pins]
buttons = [DigitalInOut(pin) for pin in button_pins]

# Set relays as output and set them to inactive or off.  The relays should remain off when the system boots.
for relay in relays:
    relay.direction = Direction.OUTPUT
    relay.value = RELAY_INACTIVE

# Set buttons as input.  Buttons are wired to ground so use internal Pull.UP resisters.
for button in buttons:
    button.direction = Direction.INPUT
    button.pull = Pull.UP

# Define the socket pool as a global variable at the module level+
pool = None

# Define the GPIO pin for the pause button.
# Change the pin number (GP16) to match the pin you are using for the new button.
pause_schedule_button = DigitalInOut(board.GP16)

# Set the new button as input and enable internal pull-up resistor.
pause_schedule_button.direction = Direction.INPUT
pause_schedule_button.pull = Pull.UP


def wifi_connect():
    # Display status message indicating the Wi-Fi connection process.
    if debug: print("Connecting to WiFi...")
    # Connect to the Wi-Fi network using the SSID and password retrieved from environment variables.
    wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
    # Display confirmation message upon successful connection.
    if debug: print("Connected to WiFi")
    # Display the IP address assigned to the device by the Wi-Fi network.
    if debug: print("My IP address is", wifi.radio.ipv4_address)


def get_local_time():
    global pool  # Access the global pool variable
    # If the socket pool doesn't exist, create it using the Wi-Fi radio connection.
    if pool is None:
        pool = socketpool.SocketPool(wifi.radio)
    # Create an Adafruit Requests session using the socket pool and SSL context.
    request = adafruit_requests.Session(pool, ssl.create_default_context())
    # Define the URL for querying world time based on the specified timezone.
    url = "https://worldtimeapi.org/api/timezone/"
    timezone = "America/Los_Angeles"  # Change your timezone to match.
    url = url + timezone
    # Display a message indicating the URL being accessed.
    if debug: print(f"Accessing URL \n{url}")
    # Send a GET request to the URL and retrieve JSON data containing world time information.
    response = request.get(url)
    json_data = response.json()
    # Extract the Unix timestamp and time zone offset from the JSON data.
    unixtime = json_data["unixtime"]
    raw_offset = json_data["raw_offset"]
    # Check for daylight savings time and retrieve its offset if applicable.
    dst_offset = json_data.get("dst_offset", 0)
    # Calculate the location time by adding the Unix timestamp and raw offset.
    location_time = unixtime + raw_offset
    # Determine if Daylight Saving Time (DST) is in effect.
    dst_active = bool(json_data.get("dst", False))
    # Display whether DST is active.
    if debug: print(f"Is DST Active: {dst_active}")
    # Adjust the location time for daylight savings time if applicable.
    if dst_active:
        location_time += dst_offset
    # Convert the location time to a time.struct_time object representing the current time.
    current_time = time.localtime(location_time)
    return current_time


def set_rtc_datetime():
    # Get the current world time using the function get_world_time().
    current_time = get_local_time()
    # Create an RTC (Real-Time Clock) instance to manage the internal device clock.
    clock = rtc.RTC()
    # Set the internal RTC datetime using the current_time struct_time object.
    clock.datetime = time.struct_time(current_time)
    # Display the current date and time that has been set in the RTC.
    current_date_time = clock.datetime
    if debug: print(f"Current Time: {current_date_time}")
    # Format and print the current time in a human-readable format.
    if debug: print(f"Printable Time: {current_time.tm_hour:d}:{current_time.tm_min:02d}:{current_time.tm_sec:02}")


def uptime():
    # Get the current uptime in seconds from the Pico
    uptime_seconds = time.monotonic()
    # Convert uptime to a more human-readable format (hours, minutes, seconds)
    uptime_hours = int(uptime_seconds // 3600)
    uptime_minutes = int((uptime_seconds % 3600) // 60)
    uptime_seconds %= 60
    # Print the uptime in a readable format
    print(f"Current Uptime: {uptime_hours} hours, {uptime_minutes} minutes, {uptime_seconds} seconds")


# Define the watering schedule for each garden bed, where each sublist corresponds to a garden bed's watering days.
# The indices of the sublist represent days of the week (0 = Monday, 6 = Sunday).
garden_bed_schedule = [
    [0, 1, 2, 3, 4, 5, 6],  # Garden Bed 1 (Every day)
    [0, 2, 4],  # Garden Bed 2 (Monday, Wednesday, Friday)
    [0, 3, 5],  # Garden Bed 3 (Tuesday, Thursday, Saturday)
    [0, 3, 6],  # Garden Bed 4 (Monday, Thursday, Sunday)
    [1, 4],  # Garden Bed 5 (Tuesday, Friday)
    [3, 5],  # Garden Bed 6 (Wednesday, Saturday)
    [0],  # Garden Bed 7 (Monday only)
    [1],  # Garden Bed 8 (Tuesday only)
]

# Define the watering time and duration for each garden bed using tuples: (hour, minute, duration in minutes).
# Times are in 24hr format, 6,10 is 6:10am, 13:45 is 1:45pm and so on.
watering_times = [
    (16, 19, 1),  # Garden Bed 1 watering time (7:00 AM for 10 minutes)
    (9, 40, 1),  # Garden Bed 2 watering time (12:30 PM for 15 minutes)
    (9, 22, 1),  # Garden Bed 3 watering time (3:45 PM for 8 minutes)
    (6, 4, 1),  # Garden Bed 4 watering time (10:15 AM for 12 minutes)
    (6, 5, 1),  # Garden Bed 5 watering time (8:30 AM for 20 minutes)
    (6, 6, 1),  # Garden Bed 6 watering time (4:00 PM for 10 minutes)
    (6, 7, 1),  # Garden Bed 7 watering time (9:30 AM for 15 minutes)
    (6, 8, 1),  # Garden Bed 8 watering time (11:00 AM for 10 minutes)
]


def is_watering_day(garden_bed_index, current_day):
    # Check if the current day is included in the watering schedule for the specified garden bed.
    # Returns True if the garden bed should be watered on the current day, False otherwise.
    return current_day in garden_bed_schedule[garden_bed_index]


def is_watering_time(garden_bed_index, current_time):
    # Check if the current time matches the watering time for the specified garden bed.
    # Returns True if the garden bed should be watered on the current time, False otherwise.
    return current_time[:2] == watering_times[garden_bed_index][:2]


# Define variables for the main loop.
manual_activation_flags = [False] * len(relays)  # When relay is manually activated set this flag for that relay
end_time_duration = [0] * len(watering_times)  # When a relay is activated due to schedule set its end of run time
schedule_running = [False] * len(relays)  # When a relay is activated due to schedule set its schedule running flag


def main():

    wifi_connect()  # Connect to the WiFi network.
    set_rtc_datetime()  # Set the Pico's Real Time Clock with current date and time.

    while True:  # Continuously loop to monitor and manage relay control and scheduling.
        # Get the current date and time from the Pico's built-in RTC.
        current_date_time = rtc.RTC().datetime
        # Determine the day of the week (0 to 6, where 0 is Monday and 6 is Sunday).
        current_day = current_date_time.tm_wday
        # Extract the current time as a tuple (hour, minute) from the current_date_time.
        current_time = (current_date_time.tm_hour, current_date_time.tm_min)

        # Loop through each relay and its associated manual button to control the relays.
        for i, manual_button_state in enumerate(buttons):
            # Check if the manual button is pressed (active LOW), indicating manual relay activation.
            if not manual_button_state.value:
                time.sleep(.1)  # Introduce a small delay (0.1 seconds) for debounce and smoother button handling.
                # Activate the corresponding relay by setting its value to RELAY_ACTIVE.
                relays[i].value = RELAY_ACTIVE
                # Set the manual activation flag for the relay to True.
                manual_activation_flags[i] = True
                if debug: print(f"Manual Activation: Relay {i + 1} for Garden Bed {i + 1} Activated")
            else:
                # If the manual button is not pressed.
                if not schedule_running[i]:  # We may have relay running under a schedule and don't want to turn it off.
                    # Deactivate the relay.
                    relays[i].value = RELAY_INACTIVE
                    # Reset the manual activation flag for the relay to False.
                    manual_activation_flags[i] = False
                    if debug: print(f"Relay {i + 1} for Garden Bed {i + 1} Off")

            # Check if the pause_schedule_button is not pressed (active LOW) to proceed with automated scheduling.
        if pause_schedule_button.value:
            time.sleep(.1)  # Introduce a small delay (0.1 seconds) for debounce and smoother button handling.
            print("Scheduling active")
            # Iterate through each relay to determine automated scheduling.
            for i in range(len(relays)):
                if is_watering_day(i, current_day) and is_watering_time(i, current_time):
                    # Check if the relay is not manually activated and the schedule hasn't started yet.
                    if not manual_activation_flags[i] and end_time_duration[i] == 0:
                        # Activate the relay and calculate the end time for the scheduled duration.
                        relays[i].value = RELAY_ACTIVE
                        end_time_duration[i] = watering_times[i][2] * 60 + int(time.monotonic())
                        schedule_running[i] = True  # Set the relay's schedule_running flag to True.
                        if debug: print(f"Relay {i + 1} for Garden Bed {i + 1} Activated")
                        if debug: print(f"End Time: {end_time_duration[i]}")
                        if debug: print(f"Schedule Running Flag: {schedule_running}")

                # Check if a watering schedule is currently running and if the end time has been reached.
                if schedule_running[i] and end_time_duration[i] < int(time.monotonic()):
                    # Deactivate the relay as the watering schedule has ended.
                    relays[i].value = RELAY_INACTIVE
                    # Update the schedule_running flag to indicate that the schedule has ended.
                    schedule_running[i] = False
                    end_time_duration[i] = 0

        else:
            # Handles cases when the pause_schedule_button is pressed.
            for i in range(len(relays)):
                if not manual_activation_flags[i]:
                    # Deactivate the relay.
                    relays[i].value = RELAY_INACTIVE
                    # Reset the watering duration countdown when not watering.
                    end_time_duration[i] = 0
                    if debug: print(f"Relay {i + 1} for Garden Bed {i + 1} Off")

        # End of loop iteration.


# Call this function at boot start the automated scheduling as well as checking for manual button presses.
# Run the main function
if __name__ == "__main__":
    main()