import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
import busio, board, time, microcontroller
import os, ssl, wifi, socketpool, adafruit_requests
from digitalio import DigitalInOut, Direction, Pull
import board, time, rtc, microcontroller
import json

debug = False
enable_logging = False


def wifi_connect(max_retries=5, retry_interval=5, simulate_failure=False):
    """
    Establishes a Wi-Fi connection using the provided SSID and password.

    This function attempts to connect to a Wi-Fi network using the SSID and password retrieved from
    settings.toml file. It will retry the connection up to the specified number of times, with a
    defined interval between retries. If the connection is successful, it displays a confirmation
    message and turns off an LED indicator. If the maximum number of retries is reached without a
    successful connection, it displays an error message, flashes the LED to indicate failure, and
    turns off the LED after a brief delay.

    :parameters
        max_retries (int): Maximum number of connection attempts before giving up.
        retry_interval (int): Time interval in seconds between connection retries.
        simulate_failure (bool): If True, simulates a connection failure for testing purposes.

    :returns: None

    Example: wifi_connect(max_retries=3, retry_interval=10, simulate_failure=False)
    """
    retries = 0

    while retries < max_retries:
        try:
            # Display status message indicating the Wi-Fi connection process.
            if debug: print(f"Connecting to WiFi (Attempt {retries + 1}/{max_retries})...")
            if simulate_failure:  # For debug
                raise Exception("Simulated connection failure")  # Simulate a connection failure
            # Connect to the Wi-Fi network using the SSID and password retrieved from settings.toml
            wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
            if debug: print("Connected to WiFi")
            # Display the IP address assigned to the device by the Wi-Fi network.
            if debug: print("My IP address is", wifi.radio.ipv4_address)
            return  # Exit the function on successful connection
        except Exception as e:
            # Display an error message if a connection attempt fails.
            if debug: print(f"Error: Failed to connect to WiFi - {e}")
            retries += 1
            time.sleep(retry_interval)

    # Display an error message if maximum retries are reached without successful connection.
    if debug: print(f"Error: Unable to establish a WiFi connection after {max_retries} attempts.")
    # Flash the LED five times fairly quickly to indicate connection failure.
    time.sleep(1)  # Wait for 1 second before turning off the LED.


def get_local_time():
    """
    Retrieves and returns the current local time based on a specified timezone.

    This function retrieves the current local time from an online time API based on a specified timezone.
    It makes an HTTP GET request to the worldtimeapi.org API, retrieves JSON data containing world time information,
    and processes the data to calculate the current local time. The function takes into account the timezone offset,
    raw offset, and daylight saving time (DST) information to accurately determine the current time.
    The resulting time is returned as a time.struct_time object, which provides various components of the time
    (hour, minute, second, etc.) in a structured format.

    :returns:
        current_time (time.struct_time): A struct_time object representing the current local time.
    """
    # Create a new socket pool for this function's use
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
    """
    Sets the Real-Time Clock (RTC) of the device with the current local time.

    This function retrieves the current local time from an online time API using the `get_local_time` function.
    It then creates an instance of the RTC to manage the device's internal clock and sets the RTC datetime using
    the retrieved current time. The function also displays the newly set RTC date and time, as well as the
    current time in a formatted, human-readable format.

    :returns: None
    """
    # Obtain the current local time from the network using get_local_time() function.
    current_time = get_local_time()

    # Create an instance of the Real-Time Clock (RTC) to manage the device's internal clock.
    clock = rtc.RTC()

    # Set the internal RTC datetime using the retrieved current_time as a struct_time object.
    clock.datetime = time.struct_time(current_time)

    # Display the newly set RTC date and time.
    current_date_time = clock.datetime
    if debug: print(f"RTC Date/Time Set: {current_date_time}")

    # Format and print the current time in a human-readable format.
    if debug: print(f"Formatted Time: {current_time.tm_hour:d}:{current_time.tm_min:02d}:{current_time.tm_sec:02}")


def cpu_temp():
    """
    Retrieves the current temperature of the Raspberry Pi Pico's CPU in Celsius.

    This function queries the Pico's internal temperature sensor to determine
    the current temperature of the CPU. The returned temperature is in degrees Celsius.
    Can be used in debug but is intended to be displayed on LCD Character display to monitor potential overheating
    issues due to being exposed outdoor temperatures.

    :returns:
        temp (float): The current CPU temperature in Celsius.
    """
    temp = microcontroller.cpu.temperature
    return temp


# create I2C connection
i2c = busio.I2C(board.GP27, board.GP26)  # # Pi Pico RP2040
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, 16, 2)
lcd.color = [0, 100, 0]  # Set display backlight to Green
# Attempt to connect to Wi-Fi
wifi_connect(max_retries=3, retry_interval=10, simulate_failure=False)

# Get current local day of the week and time from the Internet and update RTC
set_rtc_datetime()

while True:

    try:
        # Get the current date and time from the Pico's Real-Time Clock (RTC).
        current_date_time = rtc.RTC().datetime
        current_day = current_date_time.tm_wday  # Extract the current day of the week (0-6, Monday is 0)
        current_time = (current_date_time.tm_hour, current_date_time.tm_min)  # Current time as (hour, minute)

        lcd.message = f"{current_time[0]:02d}:{current_time[1]:02d}\ncpu temp: {cpu_temp()}"
        print(f"{current_time[0]:02d}:{current_time[1]:02d}\ncpu temp: {cpu_temp()}")
        time.sleep(2)

    except Exception as main_loop_error:
        # Handle errors that occur in the main loop
        print(f"Main Loop Error: {main_loop_error}")

