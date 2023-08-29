Garden Control System with Raspberry Pi Pico W and CircuitPython

Author: Mike Paxton 
Modification Date: 08/28/2023
CircuitPython Version: 8.2.2

TODO: The current set_rtc_datetime function grabs unixtime, raw_offset and DST (daylight savings) to calculate and
 set the real time clock built into the Pico. It would be nice to just grab datetime and find a way to parse and format
 the variable.  Would make the code much cleaner.

TODO: Create a web interface of some sort which will allow us to modify the schedule and/or turn on/off relays.

TODO: Look into using the Bluetooth soil moisture sensors the I purchased when switchdocs stopped selling
 raspberry pi project parts. It appears the currently CircuitPython does not support the Pico.  No libraries found.
 I might be able to use Home Assistants built in ability to use Bluetooth/Wi-Fi devices and tie them in with the Pico
 using HA conditions.  I'm pretty sure I saw a YouTube video doing just this with the Bluetooth
 moisture sensors i'm using.
TODO:  Integrate Adafruit's 16x2 RGB Character Display w/i2c backpack.  Use the display and its 5 buttons to 
add/remove relays as well as modify each relays schedule. This will be the primary means of editing relays and their 
schedules.

Breakdown of current code:

Automated Garden Watering System

This script manages an automated garden watering system using a Raspberry Pi Pico microcontroller.
The system controls multiple relays, each associated with a garden bed. It supports manual relay activation,
automated scheduling, and logging of events and system status.

Modules:
BUILT-IN Modules
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
NON-BUILT-IN Modules - Must install in /lib folder
- adafruit_requests: Provides a session for making HTTP requests.

Global Constants:
- RELAY_ACTIVE: Constant indicating relay activation.
- RELAY_INACTIVE: Constant indicating relay deactivation.

Global Variables:
- debug: Boolean indicating whether to print debug messages.
- enable_logging: Boolean indicating whether to enable event logging.
- log_interval: Time interval in minutes for updating the log file.
- log_filename: Name of the log file.

Functions:
- flash_led(times, on_duration, off_duration): Flashes the onboard LED with specified timings.
- wifi_connect(max_retries, retry_interval, simulate_failure): Establishes Wi-Fi connection.
- get_local_time(): Retrieves current local time from an online time API.
- set_rtc_datetime(): Sets Pico's RTC with current local time.
- update_log(log_text): Updates log file with provided text and date/time.
- cpu_temp(): Retrieves Pico's CPU temperature in Celsius.
- log_cpu_temp(): Logs CPU temperature to the log file at specified intervals.
- uptime(): Prints Pico's current uptime.
- load_schedule_data(): Loads watering schedule data from a JSON file.
- is_watering_day(relay_bed_index, current_day): Checks if it's a watering day for a garden bed.
- is_watering_time(relay_bed_index, current_time): Checks if it's a watering time for a garden bed.
- check_manual_button(): Checks state of manual buttons and controls relays.
- calculate_end_time(start, duration_minutes): Calculates watering end time.
- print_relay_properties(): Prints relay properties for debugging.
- main_loop(): Main loop managing relay control and scheduling.

Main Execution:
- Creates or verifies the existence of the log file.
- Enters the main loop to manage relay control and scheduling.

Introduction

The Garden Control System is designed to efficiently manage the watering of up to 8 garden beds using a Raspberry Pi 
Pico W microcontroller and CircuitPython. This system is particularly suitable for solar-powered setups where 
conserving battery usage is crucial. It incorporates both automated scheduling and manual control options, ensuring 
optimal watering conditions for your garden beds.

Features

Automated Scheduling: The system supports automated scheduling for each garden bed. You can specify the days of the 
week and the time when each bed should be watered. The watering schedule is stored in the Water_Schedule.json file.
The system gets the current date/time from the internet so you will need a Pico W.  The date and time are stored in 
the Pico W's onboard Real Time Clock (RTC).

Manual Control: Each garden bed is equipped with a dedicated button, allowing you to manually activate the watering 
process for individual beds. This feature is helpful for immediate watering needs.

Pause Schedule: The system includes a "Pause Schedule" button that suspends the automated watering schedule.  This 
is useful for rainy days or when you prefer manual control.

Onboard LED Indicator: The Raspberry Pi Pico's onboard LED provides visual feedback about system status, such as 
Wi-Fi connection and errors.

Installation and Setup

Clone the Repository: Clone this repository to your local machine using Git or by downloading the ZIP archive.
Circuit Setup: Connect the Raspberry Pi Pico to the relay modules and buttons according to the GPIO pin assignments 
specified in the code.
Wi-Fi Configuration: Modify the CIRCUITPY_WIFI_SSID and CIRCUITPY_WIFI_PASSWORD environment variables in the code to 
match your Wi-Fi network credentials.
JSON Schedule: Update the Water_Schedule.json file with your desired watering schedule. The file is organized with 
each garden bed's schedule and watering times.

 * Relays
   * Relay 0 ------------------  GPIO-0
   * Relay 1 ------------------  GPIO-1
   * Relay 2 ------------------  GPIO-2
   * Relay 3 ------------------  GPIO-3
   * Relay 4 ------------------  GPIO-4
   * Relay 5 ------------------  GPIO-5
   * Relay 6 ------------------  GPIO-6
   * Relay 7 ------------------  GPIO-7
 * Relay Manual On/Off Buttons
   * Relay 0 Button -----------  GPIO-8
   * Relay 1 Button -----------  GPIO-9
   * Relay 2 Button -----------  GPIO-10
   * Relay 3 Button -----------  GPIO-11
   * Relay 4 Button -----------  GPIO-12
   * Relay 5 Button -----------  GPIO-13
   * Relay 6 Button -----------  GPIO-14
   * Relay 7 Button -----------  GPIO-15
 * Other GPIO Pins Used
   * Pause Schedule Button ----- GPIO-16
     * LCD Backlight ----------- GPIO-28

Usage

Automated Scheduling: The system will automatically water the garden beds based on the schedule specified in the 
Water_Schedule.json file. Beds will be watered on the designated days and times.  Manual Control: Press the 
corresponding button for a garden bed to manually activate its watering process. The manual activation flag will be 
set for the respective bed.
Pause Schedule: Press the "Pause Schedule" button to halt the automated watering schedule. You can still use manual 
control during this pause.

Troubleshooting

If you encounter Wi-Fi connection issues, modify the wifi_connect function parameters in the code to adjust retry
attempts and intervals.
Ensure that the GPIO pins for relays and buttons are correctly connected to the Raspberry Pi Pico according to the 
provided assignments.
Double-check the formatting of the Water_Schedule.json file to avoid errors in the watering schedule.

How the system should function:
Each garden bed will have its own 12v solenoid and a corresponding button to activate/deactivate it.
The system is being designed to work off of a solar battery system.  Not far from my garden is my chicken coop which 
also uses a Raspberry Pico to control the opening and closing of the coop door.  (The code for that project can be 
found on my GitHub page under ChickenCoop-CircuitPython.)  I have a 100w solar panel on top of the coop which 
charges a 12v deep cycle battery inside the coop.  My goal is to run th 12v line in underground conduit from my 
chicken coop battery to the garden.  Since the garden is only in use during the summer months, my hope is that solar 
system will work for  both projects.

I want to integrate this garden system with Home Assistant which I will be running on my Synology Server as a Docker
container.

Goals for integration are:
Allow me to manually turn on/off each garden bed from my phone via the Home Assistant iPhone app.
Provide an easy way to setup each garden bed with the days of the week and times of day to run.
Home Assistant will then connect to the Pico via the Pico's HTTP server and update the water_schedule.json file 
with the changes made each beds schedule.

This is the format the Pico RTC uses for date/time
Current Time Format: struct_time(tm_year=2023, tm_mon=8, tm_mday=6, tm_hour=17, tm_min=51, tm_sec=40, tm_wday=6, tm_yday=218, tm_isdst=-1)

tm_wday=
0: Monday
1: Tuesday
2: Wednesday
3: Thursday
4: Friday
5: Saturday
6: Sunday

The program utilizes the watering schedule stored in the JSON file named "Water_Schedule.json" for each individual 
garden bed. This file is formatted in JSON and contains multiple days and corresponding times when watering should 
be initiated. The garden_bed_schedule variable empowers you to define which day(s) of the week each garden bed 
should be activated. Additionally, the watering_times variable provides the means to designate the specific time 
during the day when each bed should be watered as well as the duration of the run time.


Important Notes

The provided code is a work in progress and may require further refinement. Only tested and working portions are 
typically committed to GitHub.
The system's reliance on Wi-Fi connection makes it suitable for environments with reliable network availability.

Disclaimer

This code is provided "as-is" without any warranty. It is intended for educational purposes and personal use.
The author is not responsible for any consequences resulting from the use of this code.

License

This project is licensed under the MIT License