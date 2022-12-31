import time
import board
import digitalio
import pwmio
import adafruit_character_lcd.character_lcd as characterlcd
import json
import sys
import random
import requests
from twilio.rest import Client

#Assigning digital temp sensor output files to object. Objects are lists.
temp_sensor_1 = '/sys/bus/w1/devices/28-00000e64d174/w1_slave'
temp_sensor_2 = '/sys/bus/w1/devices/28-00000e642647/w1_slave'

# Function reads the raw output from the temp sensor
def read_raw(sensor=temp_sensor_1):
    f = open(sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines

# Function check raw output for errors, parses into readable output,
# and return temperature in Farenheit and Celcius. Occasionally the code throws an exception where it doesn't get a reading from
# the temp sensor. It's a temporary exception and always catches it on the next cycle so I added in an try/except loop
# that just tries again. 
def read_temp():
    while True:
        try:
            lines = read_raw()
            time.sleep(0.2)
            lines_2 = read_raw(sensor=temp_sensor_2)
            while lines[0].strip()[-3:] != 'YES' and lines_2[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = read_raw()
                lines_2 = read_raw(sensor=temp_sensor_2)
            equals_pos = lines[1].find('t=')
            equals_pos_2 = lines_2[1].find('t=')
            if equals_pos != -1 and equals_pos_2 != -1:
                temp_string_1 = lines[1][equals_pos+2:]
                temp_string_2 = lines_2[1][equals_pos_2+2:]
                temp_c_1 = float(temp_string_1) / 1000.0
                temp_c_2 = float(temp_string_2) / 1000.0
                temp_f_1 = temp_c_1 * 9.0 / 5.0 + 32.0
                temp_f_2 = temp_c_2 * 9.0 / 5.0 + 32.0
        except:
            continue
        else:
            return temp_c_1, temp_c_2, temp_f_1, temp_f_2
            break

# Set rows and columns for LCD display
lcd_columns = 16
lcd_rows = 2

# Raspberry Pi Pin Config:
lcd_rs = digitalio.DigitalInOut(board.D23)  # LCD pin 4
lcd_en = digitalio.DigitalInOut(board.D19)  # LCD pin 6
lcd_d7 = digitalio.DigitalInOut(board.D27)  # LCD pin 14
lcd_d6 = digitalio.DigitalInOut(board.D22)  # LCD pin 13
lcd_d5 = digitalio.DigitalInOut(board.D24)  # LCD pin 12
lcd_d4 = digitalio.DigitalInOut(board.D25)  # LCD pin 11
lcd_rw = digitalio.DigitalInOut(board.D4)  # LCD pin 5.  Determines whether to read to or write from the display.
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

#Hex codes for slack message colors
red = "#f22638"
green = "#53f226"
blue = "#118de4"

#Function that yells at slack channel. This is basically a copy/paste from slack's website
def temp_message(message = "Test", color = None):
    url = "https://hooks.slack.com/services/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"
    title = ("Temperature check")
    slack_data = {
        "username": "Coffbot-2000",
        #"icon_emoji": ":satellite:",
        #"channel" : "#somerandomcahnnel",
        "attachments": [
            {
                "color": color,
                "fields": [
                    {
                        "title": title,
                        "value": (message),
                        "short": "false",
                    }
                ]
            }
        ]
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return color

# Uses a twilio account. This is code from their website for talking to their API 
def temp_sms(body = "Test"):
    phone_list = [("Rikeem", '+15049825075')              
              ]
    account_sid = 'AC7c78d082702e2dedbd54be340be70b8f'
    auth_token = '09bc0e764233339dfa604586dc2ff3de'
    client = Client(account_sid, auth_token)
    
    for i in phone_list:
        message = client.messages \
            .create(
                 body=body,
                 from_ =  '+16695872896',
                 to = i[1]
             )

# Alarm function that appends a list of four value, adding the newest
# measure to the front and deleting the oldest. Program will only alarm
# if all four values in the list are the same. This minimizes the chance of
# superfluous alarms as the sensor bounces between values in between alarm states

alarm_lst = [None, None, None, None]

def alarm_mod(new_value):
    alarm_lst.insert(0, new_value)
    alarm_lst.pop(-1)
    return alarm_lst

# Variables used to set LCD background color. First channel is red, second is green,
# third is blue. Set values from 0 to 100.
RED = [100, 0, 0]
GREEN = [0, 100, 0]
BLUE = [0, 0, 100]

# Function takes high and low Farenheight settings as input to set the
# acceptable water term range. The loop reads the current temp and changes the color and message
# on the LCD screen accordingly. 

def display(hi=57.2, low=51.8):
        baseline = [None, None, None, None]
        while True:
            try:
                cur_temp = read_temp()
                if cur_temp[2] > hi or cur_temp[3] > hi:
                    lcd.clear()
                    cur_color = RED
                    alarm_mod(RED)
                    lcd.message = str(cur_temp[2])[0:4] + " degrees F" + "\n" + str(cur_temp[3])[0:4] + " degrees F" 
                elif (cur_temp[2] <=hi and cur_temp[3] <= hi) and (cur_temp[2] > low and cur_temp[3] > low):
                    lcd.clear()
                    cur_color = GREEN
                    alarm_mod(GREEN)
                    lcd.message = str(cur_temp[2])[0:4] + " degrees F" + "\n" + str(cur_temp[3])[0:4] + " degrees F"               
                elif cur_temp[2]<= low or cur_temp[3] <= low:
                    lcd.clear()
                    cur_color = BLUE
                    alarm_mod(BLUE)
                    cur_color = BLUE
                    lcd.message = str(cur_temp[2])[0:4] + " degrees F" + "\n" + str(cur_temp[3])[0:4] + " degrees F"
                if alarm_lst[0] == alarm_lst[1] == alarm_lst[2] == alarm_lst[3] and alarm_lst != baseline:
                    if alarm_lst[0] == RED:
                        temp_message(message = f"Temp too high! Tank 1 temperature is {cur_temp[2]} degrees Farenheight. Tank 2 temperature is {cur_temp[3]} degrees Farenheight. Please contact fish room manager!", color = red)
                        baseline = [alarm_lst[0],alarm_lst[1],alarm_lst[2],alarm_lst[3]]
                        temp_sms(body=f"Water temp too high!Tank 1 temperature is {cur_temp[2]} degrees Farenheight. Tank 2 temperature is {cur_temp[3]} degrees Farenheight. Please contact fish room manager!")
                        lcd.color = RED
                    if alarm_lst[0] == GREEN:
                        temp_message(message = "Water temp in normal range.", color = green)
                        baseline = [alarm_lst[0],alarm_lst[1],alarm_lst[2],alarm_lst[3]]
                        temp_sms(body="Water temp is in normal range")
                        lcd.color = GREEN
                    if alarm_lst[0] == BLUE:
                        temp_message(message = f"Temp too low! Tank 1 temperature is {cur_temp[2]} degrees Farenheight. Tank 2 temperature is {cur_temp[3]} degrees Farenheight. Please contact fish room manager!", color = blue)
                        baseline = [alarm_lst[0],alarm_lst[1],alarm_lst[2],alarm_lst[3]]
                        temp_sms(body=f"Water temp too low! Tank 1 temperature is {cur_temp[2]} degrees Farenheight. Tank 2 temperature is {cur_temp[3]} degrees Farenheight. Please contact fish room manager!")
                        lcd.color = BLUE
            except:
                continue
            else:
                continue
                      
if __name__ == '__main__':
    display(hi=80,low=70)