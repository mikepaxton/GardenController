# Raspberry Pi Pico Garden Watering System

The Raspberry Pi Pico Garden Watering System is a CircuitPython-based project that controls the watering of garden beds 
using the Raspberry Pi Pico microcontroller. This system allows you to automate the watering of your garden based on 
a predefined schedule or manually activate watering for individual garden beds.
### NOTE: I've not had time to complete the README but it's fairly up to date.

## Features

- Automated watering based on schedules.
- Manual activation of individual garden bed watering.
- Real-time logging of system events and cpu temp.
- User-friendly LCD display for status and information (future enhancement).
- Wi-Fi connectivity for remote control (future enhancement).

## Installation

1. **Hardware Setup**: Connect your Raspberry Pi Pico to the garden bed watering system as per the provided instructions.
   

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
   * LCD Backlight ------------- GPIO-28

2. **Software Setup**: Flash the provided Python script onto your Raspberry Pi Pico.

3. **Dependencies**: Make sure you have the required libraries installed. You can install them using pip:

   ```shell
   pip install adafruit-circuitpython-requests


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
Where HH is hour of the day on 24hr clock, MM is minutes and DD is the duration to watering time in minutes.
If you want to run the relay for two hours then set the duration to 120.

## Manual Activation
Manual activation of watering for individual garden beds is possible using manual buttons. The check_manual_button 
function checks the state of manual buttons and controls the corresponding relays.