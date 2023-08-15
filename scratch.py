"""
****************************************************************************************************************
NOTE:  This code is by no means done.  It is a work in progress.
Most of the time I only commit working code to GitHub but there still is a chance some of the code may fail.
I don't always have time to check the code in a working environment.
****************************************************************************************************************

Author: Mike Paxton
Creation Date: 08/12/2023
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
import json

# Setting debug too True will print out messages to REPL.  Set it too False to keep the processor load down.
debug = True


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

# Define onboard LED and set it to OUTPUT
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT


# Used for creating a visual display of certain error messages
# Currently only used for failed Wi-Fi connection. Flashes 5 times
def flash_led(times, on_duration, off_duration):
    for _ in range(times):
        led.value = True  # Turn on the LED
        time.sleep(on_duration)
        led.value = False  # Turn off the LED
        time.sleep(off_duration)


def wifi_connect(max_retries=5, retry_interval=5, simulate_failure=False):
    retries = 0

    while retries < max_retries:
        try:
            # Display status message indicating the Wi-Fi connection process.
            if debug: print(f"Connecting to WiFi (Attempt {retries + 1}/{max_retries})...")
            if simulate_failure:
                raise Exception("Simulated connection failure")  # Simulate a connection failure
            # Connect to the Wi-Fi network using the SSID and password retrieved from environment variables.
            wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
            # Display confirmation message upon successful connection.
            if debug: print("Connected to WiFi")
            # Turn off the LED to indicate successful connection.
            led.value = False
            # Display the IP address assigned to the device by the Wi-Fi network.
            if debug: print("My IP address is", wifi.radio.ipv4_address)
            return  # Exit the function on successful connection
        except Exception as e:
            # Display an error message if a connection attempt fails.
            if debug: print(f"Error: Failed to connect to WiFi - {e}")
            retries += 1
            # Flash the LED five times fairly quickly to indicate connection failure.
            flash_led(5, 0.1, 0.1)  # Flash LED 5 times, each flash is 0.1s on, 0.1s off
            time.sleep(retry_interval)

    # Display an error message if maximum retries are reached without successful connection.
    if debug: print(f"Error: Unable to establish a WiFi connection after {max_retries} attempts.")
    # Flash the LED five times fairly quickly to indicate connection failure.
    flash_led(5, 0.1, 0.1)  # Flash LED 5 times, each flash is 0.1s on, 0.1s off
    time.sleep(1)  # Wait for 1 second before turning off the LED.
    led.value = False  # Turn off the LED.


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
    if debug: print(f"Current RTC Date/Time: {current_date_time}")
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


# Initialize scheduling data with empty lists for load_schedule_data
watering_days = []
watering_times = []


# Load schedule data from JSON file then create two lists.  One for watering_days and the other watering_times
def load_schedule_data():
    # Declare the global variables
    global watering_days, watering_times

    try:
        # Open the Water_Schedule.json file for reading
        with open('Water_Schedule.json', 'r') as file:
            # Load JSON data from the file
            schedule_data = json.load(file)

            # List of relay names in the desired order
            #  ********* Need to change this code so relay# are not hardcoded. ********
            relay_order = ["relay0", "relay1", "relay2", "relay3", "relay4", "relay5", "relay6", "relay7"]

            # # Reset the lists before populating them as we are using .append to build each list
            watering_days = []
            watering_times = []

            # Iterate through each relay name in the order and build both lists for scheduling
            for relay_name in relay_order:
                # Check if the relay name exists in the watering_days data
                if relay_name in schedule_data["watering_days"]:
                    if debug: print("Found Relay in JSON File")
                    # Append the schedule for the relay to watering_days
                    watering_days.append(schedule_data["watering_days"][relay_name])
                    # Append the first watering time for the relay to watering_times
                    watering_times.append(schedule_data["watering_times"][relay_name])
                else:
                    # Print a message if the relay name is not found in the schedule data
                    print(f"Relay {relay_name} not found in schedule data.")

            # Print out both lists to console
            if debug: print(f"Garden Bed Schedule List: {watering_days}")
            if debug: print(f"Watering Times List: {watering_times}")

            # Return the populated watering_days and watering_times lists
            return watering_days, watering_times

    except Exception as e:
        # Print an error message if an exception occurs while loading schedule data
        print(f"Error loading schedule data: {e}")
        # Return empty lists as a fallback
        return [], []


load_schedule_data()  # Grab scheduling data before we get started


def is_watering_day(relay_bed_index, current_day):
    # Check if the current day is included in the watering schedule for the specified garden bed.
    # Returns True if the garden bed should be watered on the current day, False otherwise.
    if debug: print(f"Relay: {relay_bed_index} Watering Days: {watering_days[relay_bed_index]}")
    return current_day in watering_days[relay_bed_index]


def is_watering_time(relay_bed_index, current_time):
    # Check if the current time matches the watering time for the specified garden bed.
    # Returns True if the garden bed should be watered on the current time, False otherwise.
    # Must convert list to a tuple in order to return True if match is made.
    if debug: print(f"Relay: {relay_bed_index} Watering Time: {watering_times[relay_bed_index][:2]}")
    return current_time == tuple(watering_times[relay_bed_index][:2])


# Define variables for the main loop.
manual_activation_flags = [False] * len(relays)  # When relay is manually activated set this flag for that relay
end_time_duration = [0] * len(relays)  # When a relay is activated due to schedule set its end of run time
schedule_running = [False] * len(relays)  # When a relay is activated due to schedule set its schedule running flag


def check_manual_button():
    # Loop through each relay and its associated manual button to control the relays.
    for i, manual_button_state in enumerate(buttons):
        # Check if the manual button is pressed (active LOW), indicating manual relay activation.
        if not manual_button_state.value:
            time.sleep(.1)  # Introduce a small delay (0.1 seconds) for debounce and smoother button handling.
            # Activate the corresponding relay by setting its value to RELAY_ACTIVE.
            relays[i].value = RELAY_ACTIVE
            # Set the manual activation flag for the relay to True.
            manual_activation_flags[i] = True
            if debug: print(f"Manual Activation: Relay {i} for Garden Bed {i + 1} Activated")
        else:
            # If the manual button is not pressed.
            if not schedule_running[i]:  # We may have relay running under a schedule and don't want to turn it off.
                # Deactivate the relay.
                relays[i].value = RELAY_INACTIVE
                # Reset the manual activation flag for the relay to False.
                manual_activation_flags[i] = False
                if debug: print(f"Relay {i} for Garden Bed {i + 1} Off")


def print_relay_properties():
    for relay_index in range(len(relays)):
        print(f"Relay Index: {relay_index}")
        print(f"Manual Activation Flag: {manual_activation_flags[relay_index]}")
        print(f"End Time Duration: {end_time_duration[relay_index]}")
        print(f"Schedule Running: {schedule_running[relay_index]}")
        print(f"Watering Days: {watering_days[relay_index]}")
        print(f"Watering Times: {watering_times[relay_index][2]}")
        print("\n")


def main_loop():
    try:

        # Attempt to establish a Wi-Fi connection with a maximum of 3 retries and a 10-second interval between each attempt.
        # To simulate a connection failure, set simulate_failure to True, which will trigger LED flashing on the Pico board.
        wifi_connect(max_retries=3, retry_interval=10, simulate_failure=False)
        set_rtc_datetime()  # From the Internet get current local day of week and time and update RTC

        while True:  # Continuously loop to monitor and manage relay control and scheduling.
            try:
                if debug: print("Entering main loop...")

                # Every loop iteration get current time and day of the week from Pico RTC for checking scheduled
                # watering days and times.
                current_date_time = rtc.RTC().datetime
                current_day = current_date_time.tm_wday
                current_time = (current_date_time.tm_hour, current_date_time.tm_min)

                # Define a list of weekday names for debug printing use
                weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                if debug: print("Current day:", current_day, "(", weekday_names[current_day], ")")
                if debug: print("Current Real Time:", f"{current_time[0]:02d}:{current_time[1]:02d}")
                if debug: print(f"Current Structured Time: {current_time}")

                check_manual_button()  # Check for any manual buttons being pushed
                load_schedule_data()  # Reload schedule data

                # Check if the pause_schedule_button is not pressed (active LOW) to proceed with automated scheduling.
                if pause_schedule_button.value:
                    if debug: print("Scheduling active")
                    # Iterate through each relay to determine automated scheduling.
                    for i in range(len(relays)):
                        if is_watering_day(i, current_day) and is_watering_time(i, current_time):
                            if debug: print(f"Relay {i}: Watering Day and Time are True")
                            # Check if the relay is not manually activated and the schedule hasn't started yet.
                            if not manual_activation_flags[i] and end_time_duration[i] == 0:
                                # Activate the relay and calculate the end time for the scheduled duration.
                                relays[i].value = RELAY_ACTIVE
                                # Get the third element (0-2) watering duration from watering_times
                                # multiply by 60 for minutes, add the current time elapsed in seconds from Pico boot.
                                # This calculates the new end_time_duration or how long to water for current relay.
                                end_time_duration[i] = watering_times[i][2] * 60 + int(time.monotonic())
                                schedule_running[i] = True  # Set the relay's schedule_running flag to True.
                                if debug: print(f"Relay {i} for Garden Bed {i + 1} Activated")
                                if debug:print(f"End Time: {end_time_duration[i]}")
                                if debug: print(f"Schedule Running Flag: {schedule_running}")
                            else:
                                if debug: print(f"Relay {i} for Garden Bed {i + 1} was been manually activated")

                        # Check if a watering schedule is currently running and if the end time has been reached.
                        if schedule_running[i] and end_time_duration[i] < int(time.monotonic()):
                            # Deactivate the relay as the watering schedule has ended.
                            relays[i].value = RELAY_INACTIVE
                            # Update the schedule_running flag to indicate that the schedule has ended.
                            schedule_running[i] = False
                            end_time_duration[i] = 0

                else:
                    if debug: print("Scheduling paused")
                    # Handles cases when the pause_schedule_button is pressed.
                    for i in range(len(relays)):
                        if not manual_activation_flags[i]:  # We don't want to turn off a manually activated relay
                            # Deactivate the relay.
                            relays[i].value = RELAY_INACTIVE
                            # if a relays were running on a schedule and then the schedule was turned off we need to
                            # reset those active relays scheduled flag and end time.
                            schedule_running[i] = False
                            end_time_duration[i] = 0
                            if debug: print(f"Relay {i} for Garden Bed {i + 1} Off")

                uptime()  # This will print to the console how long the Pico has been up and running.
                if debug: print_relay_properties()
                time.sleep(1.5)  # Add a short delay to prevent tight looping causing excessive cpu processing

            except Exception as main_loop_error:
                # Handle errors that occur in the main loop.
                print(f"Main Loop Error: {main_loop_error}")
                # Flash the LED three times to indicate a main loop error.
                flash_led(3, 0.1, 0.1)
                time.sleep(1)  # Wait for 1 second before continuing.

    except Exception as main_error:
        # Handle errors that occur before entering the main loop.
        print(f"Main Error: {main_error}")
        # Flash the LED five times to indicate a main error.
        flash_led(5, 0.1, 0.1)
        time.sleep(1)  # Wait for 1 second before exiting.


# Call the main function
if __name__ == "__main__":
    main_loop()