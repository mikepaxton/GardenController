import time
import board, busio
from digitalio import DigitalInOut, Direction, Pull
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd

# create I2C connection
i2c = busio.I2C(board.GP27, board.GP26)  # # Pi Pico RP2040
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, 16, 2)

lcd.color = [100, 0, 0]
lcd.message = "Hello\nCircuitPython"

class LcdController:
    def __init__(self):
        """
        Initializes the LCD controller.

        This constructor initializes the I2C bus and connects to the LCD display.
        It also sets up the backlight control pin and turns on the backlight by default.
        """
        i2c = board.I2C()  # Initialize the I2C bus (You might need to provide specific I2C parameters here)
        self.lcd = character_lcd.Character_LCD_RGB_I2C(i2c, 16, 2)  # Initialize the LCD display

        # Initialize the backlight control pin
        self.backlight = DigitalInOut(board.D28)
        self.backlight.direction = Direction.OUTPUT
        self.backlight.value = True  # Turn on the backlight by default
        self.current_menu = SchedMenu(self)
        self.current_day = 0  # Initialize with Monday

    def set_backlight(self, value):
        """
        Controls the backlight of the LCD display.

        Parameters:
            value (bool): True to turn on the backlight, False to turn it off.
        """
        self.backlight.value = value

    def handle_buttons(self):
        """
        Handles button presses on the LCD display.

        This method checks if the select button on the LCD is pressed and prints a message.

        Example usage:
            lcd.set_backlight_color('red')  # Set the backlight color to red
        """
        if self.lcd.select_button:
            print("Select button pressed")

    def set_backlight_color(self, color):
        # Define LCD colors using RGB values
        lcd_color_red = [100, 0, 0]  # Red color
        lcd_color_green = [0, 100, 0]  # Green color
        lcd_color_blue = [0, 0, 100]  # Blue color
        lcd_color_white = [100, 100, 100]  # White color (equal intensity of all components)

        # Set the backlight color based on the provided color parameter
        if color == 'red':
            r, g, b = lcd_color_red
        elif color == 'green':
            r, g, b = lcd_color_green
        elif color == 'blue':
            r, g, b = lcd_color_blue
        elif color == 'white':
            r, g, b = lcd_color_white
        else:
            raise ValueError("Invalid color specified")

        self.lcd.color = (r, g, b)


class SchedMenu:
    def __init__(self, lcd):
        # Initialize with the LCD instance and default values
        self.lcd = lcd
        self.day_abbreviations = ["M", "T", "W", "T", "F", "S", "S"]  # Abbreviations for days of the week
        self.check_mark = bytearray([0x0, 0x0, 0x4, 0xa, 0x11, 0x0, 0x0, 0x0])  # Custom check mark character
        self.current_selection = 0  # Tracks the current selected item (0: Days, 1: HH, 2: MM, 3: DD)
        self.days_to_water = [False] * 7  # Initialize all days to not water
        self.start_time = 0  # Default start time
        self.duration = 1  # Default duration

    def handle_buttons(self):
        # Handle button presses to navigate and update selections
        if self.lcd.left_button:
            self.current_selection = (self.current_selection - 1) % 4
        elif self.lcd.right_button:
            self.current_selection = (self.current_selection + 1) % 4
        elif self.lcd.select_button:
            if self.current_selection == 0:  # Days selection
                self.days_to_water[self.lcd.current_day] = not self.days_to_water[self.lcd.current_day]
            elif self.current_selection == 1:  # HH selection
                self.start_time = (self.start_time + 1) % 24
            elif self.current_selection == 2:  # MM selection
                self.start_time = (self.start_time + 60) % (24 * 60)
            elif self.current_selection == 3:  # DD selection
                self.duration = (self.duration % 9) + 1

        self.update_schedule_display()  # Update the LCD display based on selections

    def update_schedule_display(self):
        # Clear the LCD display
        self.lcd.clear()

        # Join the day abbreviations to create the top row of days
        days_str = "\t".join(self.day_abbreviations)

        # Convert start time to hours and minutes
        start_hour, start_minute = divmod(self.start_time, 60)

        # Prepare the duration as a string
        duration_str = f"{self.duration}"

        # Display the days of the week, and HH MM DD
        self.lcd.message("HH\tMM\t DD\n")
        self.lcd.message(days_str + "\n")

        # Determine whether to display a check mark or space for the current day
        day_marker = self.check_mark if self.days_to_water[self.lcd.current_day] else " "

        # Display start time, minutes, and duration based on current selection
        if self.current_selection == 1:
            self.lcd.message(f"{start_hour}^\t{start_minute}\t{duration_str}")
        elif self.current_selection == 2:
            self.lcd.message(f"{start_hour}\t{start_minute}^\t{duration_str}")
        else:
            self.lcd.message(f"{start_hour}\t{start_minute}\t{duration_str}")

        self.lcd.message("\t" * (4 - self.lcd.current_day))  # Adjust to the right based on day position




# Create an instance of the LcdController class
#lcd = LcdController()
# Create an instance of the SchedMenu class and pass the lcd instance to it
#shed_menu = SchedMenu(lcd)