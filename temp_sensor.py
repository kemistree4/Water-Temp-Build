# import glob
import time
import board
import digitalio
import pwmio
import adafruit_character_lcd.character_lcd as characterlcd

# base_dir = '/sys/bus/w1/devices/'
# device_folder = glob.glob(base_dir + '28*')[0]
# device_file = device_folder + '/w1_slave'

#Assigning temp output files to object. Objects are lists.
#Just like R we do this to make things easier to access
temp_sensor_1 = '/sys/bus/w1/devices/28-00000de599d3/w1_slave'
temp_sensor_2 = 'N/A'

# Function reads the raw output from the temp sensor
def read_temp_raw(sensor=temp_sensor_1):
    f = open(sensor, 'r')
    time.sleep(0.5)
    lines = f.readlines()
    f.close()
    return lines

#Function check raw output for errors, parses into readable output,
#and return temperature in Farenheit and Celcius
def read_temp():
    lines = read_temp_raw()
    time.sleep(0.5)
    print(lines)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()       
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

    
# Set rows and columns for LCD display
lcd_columns = 16
lcd_rows = 2

# Raspberry Pi Pin Config:
lcd_rs = digitalio.DigitalInOut(board.D26)  # LCD pin 4
lcd_en = digitalio.DigitalInOut(board.D19)  # LCD pin 6
lcd_d7 = digitalio.DigitalInOut(board.D27)  # LCD pin 14
lcd_d6 = digitalio.DigitalInOut(board.D22)  # LCD pin 13
lcd_d5 = digitalio.DigitalInOut(board.D24)  # LCD pin 12
lcd_d4 = digitalio.DigitalInOut(board.D25)  # LCD pin 11
lcd_rw = digitalio.DigitalInOut(board.D4)  # LCD pin 5.  Determines whether to read to or write from the display.
# Not necessary if only writing to the display. Used on shield.

red = pwmio.PWMOut(board.D21)
green = pwmio.PWMOut(board.D12)
blue = pwmio.PWMOut(board.D18)

# Initialize the LCD class
# The lcd_rw parameter is optional.  You can omit the line below if you're only
# writing to the display.
lcd = characterlcd.Character_LCD_RGB(
    lcd_rs,
    lcd_en,
    lcd_d4,
    lcd_d5,
    lcd_d6,
    lcd_d7,
    lcd_columns,
    lcd_rows,
    red,
    green,
    blue,
    lcd_rw,
)

#Variables used to set LCD background color. First channel is red, second is green,
#third is blue. Set values from 0 to 100.
RED = [100, 0, 0]
GREEN = [0, 100, 0]
BLUE = [0, 0, 100]

#Function takes high and low Farenheight settings as input to set the
#acceptable water term range. The loop reads the current temp and changes the color and message
#on the LCD screen accordingly
def display(hi=59, low=57):
    while True:
        cur_temp = read_temp()
        if cur_temp[1] > hi:
            lcd.clear()
            lcd.color = RED
            lcd.message = "High temp" + "\n" + str(cur_temp[1])[0:4] + " degrees F"
            continue
        if cur_temp[1] <= hi and cur_temp[1] > low:
            lcd.clear()
            lcd.color = GREEN
            lcd.message = "Normal temp" + "\n" + str(cur_temp[1])[0:4] + " degrees F"
            continue
        if cur_temp[1] <= low:
            lcd.clear()
            lcd.color = BLUE
            lcd.message = "Low temp" + "\n" + str(cur_temp[1])[0:4] + " degrees F"
            continue

display(80,76)
