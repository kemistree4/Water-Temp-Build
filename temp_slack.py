# -*- coding: utf-8 -*-

import board
import digitalio
import pwmio
import adafruit_character_lcd.character_lcd as characterlcd
import json
import sys
import random
import requests

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

#Hex codes for slack message colors
red = "#f22638"
green = "#53f226"
blue = "#118de4"

#Function that yells at slack channel
def temp_message(message = "Water temp too high!", color = red):
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


if __name__ == '__main__':
    temp_message()