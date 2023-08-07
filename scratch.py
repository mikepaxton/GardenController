# ... (rest of the code remains the same)

# Define the watering schedule for each garden bed as described in the previous response.
# Make sure to follow the day index (0 to 6) where 0 is Monday, 1 is Tuesday, and so on, up to 6 for Sunday.
garden_bed_schedule = [
    [0, 1, 2, 3, 4, 5, 6],  # Garden Bed 1 (Every day)
    [0, 2, 4],  # Garden Bed 2 (Monday, Wednesday, Friday)
    [1, 3, 5],  # Garden Bed 3 (Tuesday, Thursday, Saturday)
    [0, 3, 6],  # Garden Bed 4 (Monday, Thursday, Sunday)
    [1, 4],  # Garden Bed 5 (Tuesday, Friday)
    [2, 5],  # Garden Bed 6 (Wednesday, Saturday)
    [0],  # Garden Bed 7 (Monday only)
    [1],  # Garden Bed 8 (Tuesday only)
]

# Define the watering time and duration for each garden bed (hour, minute, duration in minutes).
# For example, the first garden bed (index 0) will be watered at 7:00 AM for 10 minutes (hour=7, minute=0, duration=10),
# the second garden bed (index 1) will be watered at 12:30 PM for 15 minutes (hour=12, minute=30, duration=15), and so on.
watering_times = [
    (7, 0, 10),    # Garden Bed 1 watering time (7:00 AM for 10 minutes)
    (12, 30, 15),  # Garden Bed 2 watering time (12:30 PM for 15 minutes)
    (15, 45, 8),   # Garden Bed 3 watering time (3:45 PM for 8 minutes)
    (10, 15, 12),  # Garden Bed 4 watering time (10:15 AM for 12 minutes)
    (8, 30, 20),   # Garden Bed 5 watering time (8:30 AM for 20 minutes)
    (16, 0, 10),   # Garden Bed 6 watering time (4:00 PM for 10 minutes)
    (9, 30, 15),   # Garden Bed 7 watering time (9:30 AM for 15 minutes)
    (11, 0, 10),   # Garden Bed 8 watering time (11:00 AM for 10 minutes)
]

def is_watering_day(garden_bed_index, current_day):
    # Check if the current day is in the watering schedule for the specified garden bed.
    return current_day in garden_bed_schedule[garden_bed_index]

def is_watering_time(garden_bed_index, current_time):
    # Check if the current time matches the watering time for the specified garden bed.
    return current_time[:2] == watering_times[garden_bed_index][:2]

# Create a list to store the watering duration countdown for each garden bed, initialized to 0 (not watering).
watering_duration_countdown = [0] * len(watering_times)

def control_relays():
    # This function continuously monitors the state of the relay buttons and controls the corresponding relays.
    while True:  # Continue looping indefinitely
        current_date_time = rtc.RTC().datetime  # Get the current date and time

        # Get the day of the week (0 to 6, where 0 is Monday and 6 is Sunday) from the current_date_time.
        current_day = current_date_time.tm_wday

        # Get the current time as a tuple (hour, minute) from the current_date_time.
        current_time = (current_date_time.tm_hour, current_date_time.tm_min)

        for i, button_state in enumerate(buttons):
            # Check if it's a watering day for the current garden bed (i).
            if is_watering_day(i, current_day) and is_watering_time(i, current_time):
                if watering_duration_countdown[i] == 0:
                    # If it's a watering day, the current time matches the watering time, and the watering hasn't started yet,
                    # activate the corresponding relay by setting its value to RELAY_ACTIVE.
                    relays[i].value = RELAY_ACTIVE
                    print(f"Relay {i + 1} for Garden Bed {i + 1} Activated")
                    # Set the watering duration countdown in seconds based on the specified duration in minutes.
                    watering_duration_countdown[i] = watering_times[i][2] * 60
            else:
                # If it's not a watering day or the watering time does not match, set the corresponding relay value to RELAY_INACTIVE to turn off the relay.
                relays[i].value = RELAY_INACTIVE
                print(f"Relay {i + 1} for Garden Bed {i + 1} Off")
                watering_duration_countdown[i] = 0  # Reset the watering duration countdown when not watering.

            # Decrement the watering duration countdown for the current garden bed if it's greater than 0.
            if watering_duration_countdown[i] > 0:
                watering_duration_countdown[i] -= 1

        time.sleep(0.1)  # Introduce a small delay (0.1 seconds) for debounce and smoother button handling.

        time.sleep(1)   # Additional delay (1 second) to avoid rapid looping and reduce processor load.

# ... (rest of the code remains the same)
