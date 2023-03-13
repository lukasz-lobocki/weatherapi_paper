#!/usr/bin/env python

import requests, json
import credentials_weatherapi
import time

from waveshare_epd import epd4in2b_V2
from PIL import Image, ImageDraw, ImageFont

from cairosvg import svg2png
from io import BytesIO
import weather_svgs
import os
import utils

toPaper = False

svgdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "weather_icons")
api_req = r"&q=52.22,20.90&aqi=no"

padding = 1
spacing = 12
mainconsize = 150

fonts = utils.defFonts(
    "/home/pi_lukasz/fonts/readex",
    "ReadexPro-Bold.ttf",
    {"S": 16, "M": 24, "L": 32, "XL": 48, "XXL": 64},
)

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
if toPaper:
    epd = epd4in2b_V2.EPD()
    print("init and Clear")
    epd.init()
    epd.Clear()
    print("inited and Cleared")

while True:
    response = requests.get(
        credentials_weatherapi.api_url + credentials_weatherapi.api_key + api_req
    )
    response_content_json = json.loads(response.content)
    print("LOGGING:\n\n%s" % json.dumps(response_content_json, indent=2))

    print("init")
    if toPaper:
        epd.init()
        height = epd.height
        width = epd.width
    else:
        height = 300
        width = 400

    HBimage = Image.new("1", (height, width), 255)
    HRimage = Image.new("1", (height, width), 255)
    drawr = ImageDraw.Draw(HRimage)
    #    drawb = ImageDraw.Draw(HBimage)
    drawb = drawr
    drawb.rectangle((0, 0, height - 1, width - 1), outline=0)

    top = 0 + padding
    left = 0 + padding

    HRimage.paste(
        utils.getIcon(svgdir, "113/wi-day-sunny.svg", mainconsize).convert(mode="1"),
        (int(height / 2 - mainconsize / 2), top),
    )
    top += mainconsize
    
    drawb.text(
        (
            int(
                height / 2
                - utils.get_text_dimensions(
                    "%s\N{Degree Sign}C" % response_content_json["current"]["temp_c"],
                    font=fonts["XXL"],
                )[0]
                / 2
            ),
            top,
        ),
        "%s\N{Degree Sign}C" % response_content_json["current"]["temp_c"],
        font=fonts["XXL"],
        fill=0,
    )
    top += fonts["XXL"].size + spacing

    drawb.text(
        (
            int(
                height / 2
                - utils.get_text_dimensions(
                    "Feels like %s\N{Degree Sign}C" % response_content_json["current"]["feelslike_c"],
                    font=fonts["S"],
                )[0]
                / 2
            ),
            top,
        ),
        "Feels like %s\N{Degree Sign}C" % response_content_json["current"]["feelslike_c"],
        font=fonts["S"],
        fill=0,
    )
    top += fonts["S"].size + spacing

       
    foreground = Image.open(
        BytesIO(svg2png(bytestring=weather_svgs.svg_wind_06))
    ).convert("RGBA")
    background = Image.new("RGBA", foreground.size, (255, 255, 255))
    alpha_composite = Image.alpha_composite(background, foreground)
    HRimage.paste(alpha_composite.convert(mode="1"), (left - 20, top - 30))
    drawb.text(
        (left + 62, top - 2),
        "%skm/h" % response_content_json["current"]["wind_kph"],
        font=fonts["L"],
        fill=0,
    )
    top += fonts["L"].size + spacing + 42

    foreground = Image.open(
        BytesIO(svg2png(bytestring=weather_svgs.svg_umbrella_01))
    ).convert("RGBA")
    background = Image.new("RGBA", foreground.size, (255, 255, 255))
    alpha_composite = Image.alpha_composite(background, foreground)
    HRimage.paste(alpha_composite.convert(mode="1"), (left + 5, top - 0))
    drawb.text(
        (left + 62, top),
        "%smm" % response_content_json["current"]["precip_mm"],
        font=fonts["L"],
        fill=0,
    )
    top += fonts["L"].size + spacing

    drawb.text(
        (left, top),
        "Visibility %skm" % response_content_json["current"]["vis_km"],
        font=fonts["M"],
        fill=0,
    )
    top += fonts["M"].size + spacing

    if toPaper:
        epd.display(epd.getbuffer(HBimage), epd.getbuffer(HRimage))
        epd.sleep()
    else:
        HRimage.convert(mode="1").show()
    #         HRimage.show()

    print("Sleeping")
    time.sleep(15 * 60)

# except IOError as e:
#     print(e)
#
# except KeyboardInterrupt:
#     print("ctrl + c:")
#     epd.init()
#     epd4in2b_V2.epdconfig.module_exit()
#     exit()
