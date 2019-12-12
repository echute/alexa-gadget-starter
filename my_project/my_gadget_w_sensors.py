#
# Copyright 2019 Amazon.com, Inc. or its affiliates.  All Rights Reserved.
# These materials are licensed under the Amazon Software License in connection with the Alexa Gadgets Program.
# The Agreement is available at https://aws.amazon.com/asl/.
# See the Agreement for the specific terms and conditions of the Agreement.
# Capitalized terms not defined in this file have the meanings given to them in the Agreement.
#

import json
from agt import AlexaGadget
import sys
import logging

from gpiozero import RGBLED, Button
from colorzero import Color
import adafruit_ssd1306 
import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import os

# Necessary to allow printing out of bluetooth info
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup the temperature probe
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
temp_sensor = '/sys/bus/w1/devices/28-00000b569e13/w1_slave'

def write_text(text):
    # Define the Reset Pin
    oled_reset = digitalio.DigitalInOut(board.D26)
     
    WIDTH = 128
    HEIGHT = 32
    BORDER = 5  
     
    # Use for SPI
    spi = board.SPI()
    oled_cs = digitalio.DigitalInOut(board.D13)
    oled_dc = digitalio.DigitalInOut(board.D19)
    oled = adafruit_ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, oled_dc, oled_reset, oled_cs)
     
    # Clear display.
    oled.fill(0)
    oled.show()
     
    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    image = Image.new('1', (oled.width, oled.height))
     
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
     
    # Load default font.
    font = ImageFont.load_default()
     
    # Draw text
    (font_width, font_height) = font.getsize(text)
    draw.text((oled.width//2 - font_width//2, oled.height//2 - font_height//2),
              text, font=font, fill=255)
     
    # Display image
    oled.image(image)
    oled.show()
    return

# Read the temperature probe
def get_temp(sensor_num):
    f = open(temp_sensor, 'r')
    lines = f.readlines()
    f.close()
    line1 = lines[1]
    temp = float(line1.split("t=")[1]) / 1000.0
    temp_fahr = temp * (9.0 / 5.0) + 32.0
    if int(sensor_num) == 1:
        return temp_fahr
    else:
        return temp

class MyGadget(AlexaGadget):

    def __init__(self):
        super().__init__()

    # Function that recieves a payload from Alexa
    def on_custom_mygadget_alexatopi(self, directive):
        # Parse the payload sent in on the directive
        # NOTE: This payload will contain all of the slot values from the
        # intent that was used
        payload = json.loads(directive.payload.decode("utf-8"))
        # Print out the payload
        print("Received data: " + str(payload))
        # Use the person slot from the payload to call write_text()
        write_text(str(payload['data']['person']['value']))

    # Function that recieves a payload from Alexa (could be empty)
    # and then sends one back within 5 seconds.
    def on_custom_mygadget_pitoalexa(self, directive):
        # Parse the payload sent in on the directive
        # NOTE: This payload will contain all of the slot values from the
        # intent that was used
        payload = json.loads(directive.payload.decode("utf-8"))
        # Print out the payload
        print("Received data: " + str(payload))
        # Construct a response event to send back to Alexa using (or not using)
        # the data sent in with the payload from the directive
        # NOTE: I have constructed the cloud functions such that whatever you send
        # out in the event payload here will be spoken by Alexa when it is recieved
        payload = {'data': "The probe reads " + str(get_temp(payload['data']['sensor_num']['value'])) + " degrees."}
        # Send the payload in the event back to Alexa
        self.send_custom_event('Custom.MyGadget', 'PiToAlexa', payload)
        
MyGadget().main()
