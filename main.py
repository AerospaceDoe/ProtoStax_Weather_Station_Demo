#!/usr/bin/python
# -*- coding:utf-8 -*-

# *************************************************** 
#   This is a example program for
#   a Weather Station using Raspberry Pi 3 Model B, Waveshare ePaper Display and ProtoStax enclosure
#   --> https://www.waveshare.com/product/displays/e-paper/epaper-2/2.7inch-e-paper-hat.htm
#   --> https://www.protostax.com/products/protostax-for-raspberry-pi-b
#
#   It uses the weather API provided by Open Weather Map (https://openweathermap.org/api) to
#   query the current weather for a given location and then display it on the ePaper display.
#   It refreshes the weather information every 10 minutes and updates the display.
 
#   Written by Sridhar Rajagopal for ProtoStax.
#   Modified by AerospaceDoe.
#   BSD license. All text above must be included in any redistribution
# *

import sys
# sys.path.append(r'libs')

import signal
from waveshare_epd import epd2in7
from waveshare_epd import epdconfig
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import string

import pyowm

from pyowm.utils import timestamps

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

# Requires OpenWeatherMap One Call API 3.0 subscription (Base plan is sufficient) - https://home.openweathermap.org/subscriptions
# Fetching weather data every 10 minutes results in only 144 API calls per day.

owm = pyowm.OWM('REPLACE_WITH_YOUR_OWM_API_KEY')   # REPLACE HERE with your own API key - https://openweathermap.org/api

location = "London, GB"   # REPLACE HERE with your location name

# Geo coords [loc_lat, loc_lon] 
# Find your geo coords here: https://openweathermap.org/find

loc_lat = 51.5085   # REPLACE HERE with your geo coords latitude
loc_lon = -0.1257   # REPLACE HERE with your geo coords longitude

weather_icon_dict = {
                     # Thunderstorm
                     200 : u"\uf01e", 201 : u"\uf01e", 202 : u"\uf01e",     # thunderstorm with rain
                     210 : u"\uf016", 211 : u"\uf016", 212 : u"\uf016", 221 : u"\uf016",    # thunderstorm
                     230 : u"\uf01e", 231 : u"\uf01e", 232 : u"\uf01e",     # thunderstorm with drizzle

                     # Drizzle
                     300 : u"\uf01c", 301 : u"\uf01c",  # drizzle
                     302 : u"\uf019",
                     310 : u"\uf017",
                     311 : u"\uf019", 312 : u"\uf019",
                     313 : u"\uf01a",
                     314 : u"\uf019",
                     321 : u"\uf01c",   # shower drizzle

                     # Rain
                     500 : u"\uf01c",   # light rain
                     501 : u"\uf019", 502 : u"\uf019", 503 : u"\uf019", 504 : u"\uf019",    # rain
                     511 : u"\uf017",   # freezing rain
                     520 : u"\uf01a", 521 : u"\uf01a", 522 : u"\uf01a",     # shower rain
                     531 : u"\uf01d",   # ragged shower rain

                     # Snow
                     600 : u"\uf01b", 601 : u"\uf01b",  # light snow
                     602 : u"\uf0b5",   # heavy snow
                     611 : u"\uf017", 612 : u"\uf017", 613 : u"\uf017", 615 : u"\uf017", 616 : u"\uf017", 620 : u"\uf017",  # rain and snow
                     621 : u"\uf01b", 622 : u"\uf01b",  # shower snow

                     # Atmosphere
                     701 : u"\uf014",   # mist
                     711 : u"\uf062",   # smoke
                     721 : u"\uf0b6",   # haze
                     731 : u"\uf063",   # sand, dust whirls
                     741 : u"\uf014",   # fog
                     751 : u"\uf082",   # sand
                     761 : u"\uf063", 762 : u"\uf063",  # dust, volcanic ash
                     771 : u"\uf011",   # squalls
                     781 : u"\uf056",   # tornado

                     # Clear & Clouds
                     800 : u"\uf00d",   # clear sky
                     801 : u"\uf011", 802 : u"\uf011",  # clouds
                     803 : u"\uf012",   # broken clouds
                     804 : u"\uf013",   # overcastclouds

                     # Extreme
                     900 : u"\uf056", # tornado
                     901 : u"\uf01d", # tropical storm
                     902 : u"\uf073", # hurricane
                     903 : u"\uf076", # cold
                     904 : u"\uf072", # hot
                     905 : u"\uf021", # windy
                     906 : u"\uf015", # hail

                     # Additional
                     951 : u"\uf00d", # calm
                     952 : u"\uf021", # light breeze
                     953 : u"\uf021", # gentle breeze
                     954 : u"\uf050", # moderate breeze         11-15 knots
                     955 : u"\uf050", # fresh breeze            16-21 knots
                     956 : u"\uf0cc", # strong breeze           22-27 knots
                     957 : u"\uf0cc", # high wind, near gale    28-33 knots
                     958 : u"\uf0cd", # gale    34-40
                     959 : u"\uf0cd", # severe gale
                     960 : u"\uf0ce", # storm
                     961 : u"\uf0ce", # violent storm
                     962 : u"\uf0cf", # hurricane
                     # https://www.windfinder.com/wind/windspeed.htm

                     10800: u"\uf02e"
}

# Main function

def main():
    epd = epd2in7.EPD()
    # while True:

    # Get Weather data from OWM
    mgr = owm.weather_manager()

    one_call=mgr.one_call(lat=loc_lat, lon=loc_lon)
    current=one_call.current
    forecast_hourly=one_call.forecast_hourly
    forecast_daily=one_call.forecast_daily

    # print("Current: " + str(current)) # Current T
    # print("Hourly[0]: " + str(forecast_hourly[0])) # T+0h
    # print("Hourly[1]: " + str(forecast_hourly[1])) # T+1h
    # print("Daily[0]: " + str(forecast_daily[0]))  # Today
    # print("Daily[1]: " + str(forecast_daily[1]))  # Tomorrow

    reftime = current.reference_time()
    description = string.capwords(current.detailed_status)
    temperature = current.temperature('celsius')
    humidity = current.humidity
    pressure = current.pressure
    clouds = current.clouds
    wind = current.wind()
    sunrise = current.sunrise_time()
    sunset = current.sunset_time()

    if current.weather_code==800 :
        if current.reference_time() >= current.sunrise_time() and current.reference_time() < current.sunrise_time() :
            weathercodecurrent=current.weather_code
        else :
            weathercodecurrent=current.weather_code+10000
    else :
        weathercodecurrent=current.weather_code

    # print("weather code: "+ str(weathercodecurrent))
    # print("location: " + location)
    # print("weather: " + str(current))
    # print("description: " + description)
    # print("temperature: " + str(temperature))
    # print("humidity: " + str(humidity))
    # print("pressure: " + str(pressure))
    # print("clouds: " + str(clouds))
    # print("wind: " + str(wind))
    # print("sunrise: " + time.strftime( '%H:%M', time.localtime(sunrise)))
    # print("sunset: " + time.strftime( '%H:%M', time.localtime(sunset)))

    description_today=forecast_daily[0].status
    temperature_today=forecast_daily[0].temperature('celsius')
    # print(str(temperature_today))

    description_tomo=forecast_daily[1].status
    temperature_tomo=forecast_daily[1].temperature('celsius')
    # print(str(temperature_tomo))

    description_afttomo=forecast_daily[2].status
    temperature_afttomo=forecast_daily[2].temperature('celsius')
    # print(str(temperature_afttomo))

    # Display Weather Information on e-Paper Display

    # print("Clear...")
    epd.init()
    epd.Clear(0xFF)

    # Drawing on the Horizontal image
    ScreenImage = Image.new('1', (epd2in7.EPD_WIDTH, epd2in7.EPD_HEIGHT), 255)  # 176*264
    # ScreenImage = Image.new('1', (176, 264), 255)  # 176*264

    # print("Drawing")
    drawscreen = ImageDraw.Draw(ScreenImage)
    font12 = ImageFont.truetype('fonts/arial.ttf', 12)
    font14 = ImageFont.truetype('fonts/arial.ttf', 14)
    font16 = ImageFont.truetype('fonts/arial.ttf', 16)
    font18 = ImageFont.truetype('fonts/arial.ttf', 18)
    font20 = ImageFont.truetype('fonts/arial.ttf', 20)
    font22 = ImageFont.truetype('fonts/arial.ttf', 22)
    font24 = ImageFont.truetype('fonts/arial.ttf', 24)
    font26 = ImageFont.truetype('fonts/arial.ttf', 26)
    font28 = ImageFont.truetype('fonts/arial.ttf', 28)

    fontweathermicro = ImageFont.truetype('fonts/weathericons-regular-webfont.ttf', 14)
    fontweathertiny = ImageFont.truetype('fonts/weathericons-regular-webfont.ttf', 16)
    fontweathersmall = ImageFont.truetype('fonts/weathericons-regular-webfont.ttf', 30)
    fontweathermid = ImageFont.truetype('fonts/weathericons-regular-webfont.ttf', 40)
    fontweatherbig = ImageFont.truetype('fonts/weathericons-regular-webfont.ttf', 60)

    bbox1 = font12.getbbox(location)
    w1, h1 = bbox1[2] - bbox1[0], bbox1[3] - bbox1[1]
    bbox2 = font18.getbbox(description)
    w2, h2 = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
    bbox3 = fontweatherbig.getbbox(weather_icon_dict[weathercodecurrent])
    w3, h3 = bbox3[2] - bbox3[0], bbox3[3] - bbox3[1]

    lastUpdated = time.strftime('%H:%M')
    currentDate= time.strftime('%a - %d.%m.%y')

    # EPD_WIDTH       = 176
    # EPD_HEIGHT      = 264

    # print(currentTime)
    drawscreen.text((91+42, -5),'{}'.format(u'\uf04c'),font=fontweathertiny, fill=0)
    drawscreen.text((100+44, 1), '{}'.format(lastUpdated),font=font12, fill=0)

    # print(location)
    drawscreen.text((1, 1), '{}'.format(location+' '), font = font12, fill = 0)

    bbox4 = font22.getbbox(currentDate)
    w4, h4 = bbox4[2] - bbox4[0], bbox4[3] - bbox4[1]

    drawscreen.text((176/2-w4/2, 16), '{}'.format(currentDate+' '), font = font22, fill = 0)

    drawscreen.text((176/2- w2/2, 40+5), description, font = font18, fill = 0)
    drawscreen.text((8, 44+13), weather_icon_dict[weathercodecurrent], font = fontweatherbig, fill = 0)

    tempstr = str("{0}".format(int(round(temperature['temp']))))

    bbox5 = font28.getbbox(tempstr)
    w5, h5 = bbox5[2] - bbox5[0], bbox5[3] - bbox5[1]

    drawscreen.text((88, 56+13), tempstr+' ', font = font28, fill = 0)

    drawscreen.text((88+w5+2, 54+13), '{}'.format(u'\uf03c'), font = fontweathersmall, fill = 0)

    drawscreen.text((90, 84+13), str("Humid.: {}% ".format(int(round(humidity)))), font = font14, fill = 0)
    drawscreen.text((90, 84+13+14), str("Wind: {}m/s ".format(int(round(wind["speed"])))), font = font14, fill = 0)
    drawscreen.text((90, 84+13+14+14), str("Cloud: {}% ".format(int(round(clouds)))), font = font14, fill = 0)

    # drawscreen.line((59, 150, 59, 264), fill = 0)
    # drawscreen.line((59*2, 150, 59*2, 264), fill = 0)

    bbox6 = font16.getbbox('Today')
    w6, h6 = bbox6[2] - bbox6[0], bbox6[3] - bbox6[1]
    bbox7 = font12.getbbox(forecast_daily[0].status)
    w7, h7 = bbox7[2] - bbox7[0], bbox7[3] - bbox7[1]
    bbox8 = fontweathermid.getbbox(weather_icon_dict[forecast_daily[0].weather_code])
    w8, h8 = bbox8[2] - bbox8[0], bbox8[3] - bbox8[1]
    bbox9 = font14.getbbox(str(int(round(temperature_today['max']))))
    w9, h9 = bbox9[2] - bbox9[0], bbox9[3] - bbox9[1]
    bbox10 = font14.getbbox(str(int(round(temperature_today['min']))))
    w10, h10 = bbox10[2] - bbox10[0], bbox10[3] - bbox10[1]

    drawscreen.text((29-w6/2, 148+3), '{}'.format('Today'), font = font16, fill = 0)
    drawscreen.text((29-w7/2, 150+18+3), '{}'.format(forecast_daily[0].status), font = font12, fill = 0)
    drawscreen.text((29-w8/2, 174+3), weather_icon_dict[forecast_daily[0].weather_code], font = fontweathermid, fill = 0)
    drawscreen.text((29-w9/2-6, 220+10+3), str('{}'.format(int(round(temperature_today['max'])))), font = font14, fill = 0)
    drawscreen.text((29-w10/2-6, 235+10+3), str('{}'.format(int(round(temperature_today['min'])))), font = font14, fill = 0)
    drawscreen.text((29+w9/2-6+1, 220+10+3), '{}'.format(u'\uf03c'), font = fontweathermicro, fill = 0)
    drawscreen.text((29+w10/2-6+1, 235+10+3), '{}'.format(u'\uf03c'), font = fontweathermicro, fill = 0)

    bbox11 = font16.getbbox('TMW')
    w11, h11 = bbox11[2] - bbox11[0], bbox11[3] - bbox11[1]
    bbox12 = font12.getbbox(forecast_daily[1].status)
    w12, h12 = bbox12[2] - bbox12[0], bbox12[3] - bbox12[1]
    bbox13 = fontweathermid.getbbox(weather_icon_dict[forecast_daily[1].weather_code])
    w13, h13 = bbox13[2] - bbox13[0], bbox13[3] - bbox13[1]
    bbox14 = font14.getbbox(str(int(round(temperature_tomo['max']))))
    w14, h14 = bbox14[2] - bbox14[0], bbox14[3] - bbox14[1]
    bbox15 = font14.getbbox(str(int(round(temperature_tomo['min']))))
    w15, h15 = bbox15[2] - bbox15[0], bbox15[3] - bbox15[1]

    drawscreen.text((89-w11/2, 148+3), '{}'.format('TMW'), font = font16, fill = 0)
    drawscreen.text((89-w12/2, 150+18+3), '{}'.format(forecast_daily[1].status), font = font12, fill = 0)
    drawscreen.text((89-w13/2, 174+3), weather_icon_dict[forecast_daily[1].weather_code], font = fontweathermid, fill = 0)
    drawscreen.text((89-w14/2-6, 220+10+3), str('{}'.format(int(round(temperature_tomo['max'])))), font = font14, fill = 0)
    drawscreen.text((89-w15/2-6, 235+10+3), str('{}'.format(int(round(temperature_tomo['min'])))), font = font14, fill = 0)

    drawscreen.text((89+w14/2-6+1, 220+10+3), '{}'.format(u'\uf03c'), font = fontweathermicro, fill = 0)
    drawscreen.text((89+w15/2-6+1, 235+10+3), '{}'.format(u'\uf03c'), font = fontweathermicro, fill = 0)

    bbox16 = font16.getbbox('TDAT')
    w16, h16 = bbox16[2] - bbox16[0], bbox16[3] - bbox16[1]
    bbox17 = font12.getbbox(forecast_daily[2].status)
    w17, h17 = bbox17[2] - bbox17[0], bbox17[3] - bbox17[1]
    bbox18 = fontweathermid.getbbox(weather_icon_dict[forecast_daily[2].weather_code])
    w18, h18 = bbox18[2] - bbox18[0], bbox18[3] - bbox18[1]
    bbox19 = font14.getbbox(str(int(round(temperature_afttomo['max']))))
    w19, h19 = bbox19[2] - bbox19[0], bbox19[3] - bbox19[1]
    bbox20 = font14.getbbox(str(int(round(temperature_afttomo['min']))))
    w20, h20 = bbox20[2] - bbox20[0], bbox20[3] - bbox20[1]

    drawscreen.text((148-w16/2, 148+3), '{}'.format('TDAT'), font = font16, fill = 0)
    drawscreen.text((148-w17/2, 150+18+3), '{}'.format(forecast_daily[2].status), font = font12, fill = 0)
    drawscreen.text((148-w18/2, 174+3), weather_icon_dict[forecast_daily[2].weather_code], font = fontweathermid, fill = 0)
    drawscreen.text((148-w19/2-6, 220+10+3), str('{}'.format(int(round(temperature_afttomo['max'])))), font = font14, fill = 0)
    drawscreen.text((148-w20/2-6, 235+10+3), str('{}'.format(int(round(temperature_afttomo['min'])))), font = font14, fill = 0)

    drawscreen.text((148+w19/2-6+1, 220+10+3), '{}'.format(u'\uf03c'), font = fontweathermicro, fill = 0)
    drawscreen.text((148+w20/2-6+1, 235+10+3), '{}'.format(u'\uf03c'), font = fontweathermicro, fill = 0)

    time_string = time.strftime("%H_%M_%S")
    
    # Debug
    # ScreenImage.save('test_'+time_string+'.png')

    RotatedImage=ScreenImage.rotate(180)
    epd.display(epd.getbuffer(RotatedImage))

    time.sleep(15)
    epd.sleep()

    # Sleep for 5 minutes - loop will continue after 5 minutes
    # time.sleep(300) # Wake up every 5 minutes to update weather display
    
    # See: cat /etc/crontab #  Run once every 10 mins

# gracefully exit without a big exception message if possible
def ctrl_c_handler(signal, frame):
    print('Goodbye!')
    # XXX : TODO
    #
    # To preserve the life of the ePaper display, it is best not to keep it powered up -
    # instead putting it to sleep when done displaying, or cutting off power to it altogether.
    #
    # epdconfig.module_exit() shuts off power to the module and calls GPIO.cleanup()
    # The latest epd library chooses to shut off power (call module_exit) even when calling epd.sleep()
    # epd.sleep() calls epdconfig.module_exit(), which in turns calls cleanup().
    # We can therefore end up in a situation calling GPIO.cleanup twice
    #
    # Need to cleanup Waveshare epd code to call GPIO.cleanup() only once
    # for now, calling epdconfig.module_init() to set up GPIO before calling module_exit to make sure
    # power to the ePaper display is cut off on exit
    # I have also modified epdconfig.py to initialize SPI handle in module_init() (vs. at the global scope)
    # because slepe/module_exit closes the SPI handle, which wasn't getting initialized in module_init
    epdconfig.module_init()
    epdconfig.module_exit()
    exit(0)

signal.signal(signal.SIGINT, ctrl_c_handler)

if __name__ == '__main__':
    main()
