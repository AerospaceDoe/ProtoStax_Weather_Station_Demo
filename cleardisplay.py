#!/usr/bin/python
# -*- coding:utf-8 -*-

# *************************************************** 
#   This is a example program for
#   a Weather Station using Raspberry Pi 3 Model B, Waveshare ePaper Display and ProtoStax enclosure
#   --> https://www.waveshare.com/product/displays/e-paper/epaper-2/2.7inch-e-paper-hat.htm
#   --> https://www.protostax.com/products/protostax-for-raspberry-pi-b
#
#   This program is used to clear the ePaper display. If you are powering down your
#   Raspberry Pi and storing it and the ePaper display, it is recommended
#   that the display be cleared prior to storage, to prevent any burn-in.
 
#   Written by Sridhar Rajagopal for ProtoStax.
#   Modified by AerospaceDoe.
#   BSD license. All text above must be included in any redistribution
# *

import sys
# sys.path.append(r'lib')

from waveshare_epd import epd2in7
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

try:
    epd = epd2in7.EPD()
    epd.init()
    print("Clear...")
    epd.Clear(0xFF)

    epd.sleep()

except :
    print ('traceback.format_exc():\n%s',traceback.format_exc())
    exit()
