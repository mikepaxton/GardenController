# Raspberry Pi Pico Garden Watering System

#### NOTE: I've not had time to complete the README, but it's fairly up-to-date.


The Raspberry Pi Pico W Garden Watering System is a CircuitPython-based project that controls the watering of garden 
beds using the Raspberry Pi Pico W microcontroller. This system allows you to automate the watering of your garden 
based on a predefined schedule or manually activating the watering of individual garden beds.

For my specific application, I'm powering this garden controller using a pre-existing 12V solar panel system 
installed in my chicken coop. The coop, situated near the garden, has a 100W solar panel with a 30A controller 
and a 12V deep cycle battery. As this garden watering system will exclusively run during the summer season, the 
capacity of this setup should be sufficient to power all 8 relays/solenoids throughout the daylight hours.

The system's reliance on Wi-Fi and internet connection makes it suitable for environments with reliable network 
availability.  You could use this code with some modifications if you don't have or don't want to use Wi-Fi.  You 
would need to purchase a suitable Real-Time-Controller (RTC) and modify the function set_rtc_datetime().
NOTE:  The Raspberry Pico W does have a built-in RTC, but it's not battery backed up so when it looses power it 
will loose the date/time.

## Features:

- Automated watering based on schedules.
- Manual activation of individual garden bed watering.
- Real-time logging of system events and cpu temp.
- User-friendly LCD display for status and information (future enhancement).
- Wi-Fi connectivity for remote control (future enhancement).

## Installation:

### Current files you will need on the Pico W
* /main.py
* /boot.py
* /Water_Schedule.json
* /settings.toml
* /log.txt
* /lib/adafruit_requests.py

1. Download and install the latest version of CircuitPython for the Raspberry Pico W.
2. Clone this repository to your local machine using Git or by downloading the ZIP archive.
3. Install dependencies listed below into the cloned Garden Controller folder.
4. Copy the files listed above to your Pico W placing them in the proper directories.
5. Connect the Raspberry Pi Pico to the relay modules and buttons according to the GPIO pin assignments listed below.
6. Modify the CIRCUITPY_WIFI_SSID and CIRCUITPY_WIFI_PASSWORD environment variables in the settings.toml file to 
   match your Wi-Fi network credentials.
7. Edit the Watering_Schedule.json file to reflect your personal watering preferences.

## Hardware Setup:
The following is a list of the main components used.
* [Raspberry Pi Pico W](https://www.adafruit.com/product/5525)
* [8 Channel Relay](https://www.amazon.com/gp/product/B00KTELP3I/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
* [Latching On/Off Push Buttons](https://www.amazon.com/gp/product/B083JWSSG3/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1)
* [12v 3/4 Male Solenoid valve, normally closed](https://www.amazon.com/gp/product/B07JG9KZ9N/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
* [12v to 5v DC step down converter](https://www.amazon.com/VOLRANTISE-Converter-Voltage-Regulator-Transformer/dp/B09WZ837ZB/ref=sr_1_10?keywords=12v%2Bto%2B5%2Bvolt%2Bconverter&qid=1693805461&sprefix=12v%2Bto%2B5%2Bvolt%2Caps%2C169&sr=8-10&th=1)
* [Prototype PCB solder-able breadboard](https://www.amazon.com/gp/product/B07ZYNWJ1S/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1)
* [Mount screw terminal block connectors](https://www.amazon.com/gp/product/B09F6TC7RP/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
* [Solid core hook-up wire](https://www.amazon.com/gp/product/B088KQFHV7/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1)
* [20 x 1 Female Headers](https://www.adafruit.com/product/4155)

### GPIO wiring:
 * Connect Relays to following Pins
   * Relay 0 ------------------  GPIO-0
   * Relay 1 ------------------  GPIO-1
   * Relay 2 ------------------  GPIO-2
   * Relay 3 ------------------  GPIO-3
   * Relay 4 ------------------  GPIO-4
   * Relay 5 ------------------  GPIO-5
   * Relay 6 ------------------  GPIO-6
   * Relay 7 ------------------  GPIO-7
   * Relay 5v to 5 volt power supply
   * Relay Ground to ground on Pico and 
       5v power source if other than Pico
 
 * Relay Manual On/Off Buttons
   * Relay 0 Button -----------  GPIO-8
   * Relay 1 Button -----------  GPIO-9
   * Relay 2 Button -----------  GPIO-10
   * Relay 3 Button -----------  GPIO-11
   * Relay 4 Button -----------  GPIO-12
   * Relay 5 Button -----------  GPIO-13
   * Relay 6 Button -----------  GPIO-14
   * Relay 7 Button -----------  GPIO-15
   * All Buttons to ground
 * Other GPIO Pins Used
   * Pause Schedule Button ----- GPIO-16
   * LCD Backlight ------------- GPIO-28 (Not implemented yet)

**Dependencies**: Make sure you have the required libraries installed. You can install them using pip:
```
   pip install adafruit-circuitpython-requests'
```

## Managing Schedules
The system manages watering schedules using the load_schedule_data function, which reads schedule data from a JSON file.
Each relay can be run on multiple days of the week by specifying 0-7 where 0 is Monday, 6 is Sunday and 7 is every day.
If you want to water every day just place a 7 in the relays array (list).  
## Example Water_Schedule.json file.
```
{
    "watering_days": {
        "relay0": [0, 1, 2, 3, 4, 5, 6],
        "relay1": [7],
        "relay2": [0, 2, 4]
    },
    "watering_times": {
        "relay0": [
            [16, 35, 1],
            [19, 15, 2]
        ],
        "relay1": [
            [2, 45, 8],
            [17, 30, 3]
        ],
        "relay2": [
            [3, 45, 8]
        ]
    }
}
```
## Days of the week are:
0: Monday
1: Tuesday
2: Wednesday
3: Thursday
4: Friday
5: Saturday
6: Sunday
7: Every day (Special use: Water every day)

## Watering Times 
Times are in a Tuple: HH, MM, DD
Where HH is hour of the day on a 24hr clock, MM is minutes and DD is the duration of watering time in minutes.  So 
if you want to water a bed for two hours you would put 120 in the duration.
Each relay can run multiple times per day, just additional lists to the desired relay.  Remember, formatting is 
critical in json files.

### For reference, this is the format the Pico RTC stores the date/time
Current Time Format: struct_time(tm_year=2023, tm_mon=8, tm_mday=6, tm_hour=17, tm_min=51, tm_sec=40, tm_wday=6, tm_yday=218, tm_isdst=-1)

## Manual Activation
Manual activation of watering for individual garden beds is possible using manual buttons. The check_manual_button 
function checks the state of manual buttons and controls the corresponding relays.

### Current  Functions:
- check_for_logging: Check for the existence of a log file and create it if necessary.
- flash_led(times, on_duration, off_duration): Flashes the onboard LED with specified timings.
- wifi_connect(max_retries, retry_interval, simulate_failure): Establishes Wi-Fi connection.
- get_local_time(): Retrieves current local time from an online time API.
- set_rtc_datetime(): Sets Pico's RTC with current local time.
- update_log(log_text): Updates log file with provided text and date/time.
- cpu_temp(): Retrieves Pico's CPU temperature in Celsius.
- log_cpu_temp(): Logs CPU temperature to the log file at specified intervals.
- uptime(): Prints Pico's current uptime to serial console.
- load_schedule_data(): Loads watering schedule data from a JSON file.
- is_watering_day(relay_bed_index, current_day): Checks if it's a watering day for a garden bed.
- is_watering_time(relay_bed_index, current_time): Checks if it's a watering time for a garden bed.
- check_manual_button(): Checks state of manual buttons and controls relays.
- calculate_end_time(start, duration_minutes): Calculates watering end time.
- print_relay_properties(): Prints relay properties for debugging.
- main_loop(): Main loop managing relay control and scheduling.

## CircuitPython Modules Used:

### BUILT-IN Modules
- os: Provides functions for interacting with the operating system.
- ssl: Provides SSL (Secure Sockets Layer) protocol functions.
- wifi: Provides Wi-Fi connectivity features.
- socketpool: Provides a socket pool for handling network connections.
- digitalio: Provides digital I/O (input/output) functionality.
- board: Provides pin definitions for the board.
- time: Provides time-related functions.
- rtc: Provides access to the Real-Time Clock (RTC) module.
- microcontroller: Provides access to microcontroller-specific features.
- json: Provides functions for working with JSON (JavaScript Object Notation) data.
#### NON-BUILT-IN Modules - Must install in Pico /lib folder
- adafruit_requests: Provides a session for making HTTP requests.


## TODO List:
* TODO: Investigate the possibility of dynamically configuring GPIO pins for both Relays and Buttons based on the 
  number of relays specified in the Water_Schedule.json file.

* TODO: Incorporate the [Adafruit 16x2 LCD i2c shield kit](https://www.adafruit.com/product/772) for adding/deleting relays and modifying the schedule.

* TODO: Look into integrating this system into Home Assistant which would run either as a VM or docker image.  This 
  would allow me to control the garden watering system from the internet.  Additionally, might allow me to integrate 
  the bluetooth moisture sensors into the system.  As yet CircuitPython does not allow for control of these devices.


## Disclaimer
This code is provided "as-is" without any warranty. It is intended for educational purposes and personal use.
The author is not responsible for any consequences resulting from the use of this code.


