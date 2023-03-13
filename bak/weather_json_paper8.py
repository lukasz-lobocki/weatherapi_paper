#!/usr/bin/env python
import json
import credentials_weatherapi
import time
import os

import utils

TO_PAPER = False
WITH_FRAMES = False
PADDING = 6
SPACING = 10
MAIN_ICON_SIZE = 150
REGULAR_ICON_SIZE = 48
REFRESH_INTERVAL_MIN = 15
top = 0 + PADDING

SVG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "weather_icons")
API_REQ = r"&q=52.22,20.90&aqi=no"

epd, HEIGHT, WIDTH = utils.init_display(TO_PAPER)

fontsB = utils.define_fonts(
    "/home/pi_lukasz/fonts/readex", "ReadexPro-Bold.ttf", {"L": 32, "XXL": 64}
)

fontsR = utils.define_fonts(
    "/home/pi_lukasz/fonts/readex", "ReadexPro-Regular.ttf", {"S": 18, "M": 24}
)


# def put_icon_and_text_center(canvas, icon=None, text=None, current_top=0):
#     _height = canvas[0].width	#reversed because of portrait orientation
#     _blockheight = (
#         (utils.get_text_dimensions(" %s" % text[0], text[1])[0])
#         if text is not None
#         else 0
#     ) + (icon[2] if icon is not None else 0)
#     if icon is not None:
#         canvas[0].paste(
#             utils.get_icon(icon[0], icon[1], icon[2]).convert(mode="1"),
#             (int(_height / 2 - _blockheight / 2), current_top),
#         )
#     if WITH_FRAMES:
#         canvas[1].rectangle(
#             [
#                 (int(_height / 2 - _blockheight / 2), current_top),
#                 (
#                     int(_height / 2 - _blockheight / 2) + _blockheight,
#                     current_top
#                     + max(
#                         (icon[2] if icon is not None else 0),
#                         (
#                             utils.get_text_dimensions(text[0], text[1])[1]
#                             if text is not None
#                             else 0
#                         ),
#                     ),
#                 ),
#             ],
#             outline=0,
#         )
#     if text is not None:
#         canvas[1].text(
#             (
#                 int(_height / 2 - _blockheight / 2)
#                 + (icon[2] if icon is not None else 0)
#                 + 4,
#                 current_top + 3,
#             ),
#             text[0],
#             font=text[1],
#             fill=0,
#         )
#     return max(
#         (icon[2] if icon is not None else 0),
#         (utils.get_text_dimensions(text[0], text[1])[1] if text is not None else 0),
#     )
#

try:
    while True:
        response_content_json = utils.get_weatherapi_response_json(
            credentials_weatherapi.api_url + credentials_weatherapi.api_key + API_REQ
        )

        print("LOGGING:\n\n%s" % json.dumps(response_content_json, indent=2))

        if TO_PAPER:
            epd.init()
            print("epaper re-inited")

        HBimage, HRimage, drawb, drawr = utils.init_image(HEIGHT, WIDTH, TO_PAPER)

        if not TO_PAPER:
            drawb.rectangle([(0, 0), (HEIGHT - 1, WIDTH - 1)], outline=0)

        top = 0 + PADDING

        top += (
            utils.put_icon_and_text_center(
                (HRimage, drawb, WITH_FRAMES),
                None,
                ("Tusia, Łukasz, Szymek, Jaś", fontsR["S"]),
                top,
            )
            + SPACING
            - 6
        )

        top += (
            utils.put_icon_and_text_center(
                (HRimage, drawb, WITH_FRAMES),
                (
                    SVG_DIR,
                    utils.get_weatherapi_icon(
                        "weatherapi.json",
                        "icons.json",
                        response_content_json["current"]["condition"]["code"],
                        response_content_json["current"]["is_day"],
                    ),
                    MAIN_ICON_SIZE,
                ),
                None,
                top,
            )
            + SPACING
            - 28
        )

        top += (
            utils.put_icon_and_text_center(
                (HRimage, drawb, WITH_FRAMES),
                None,
                (
                    "%s\N{Degree Sign}C" % response_content_json["current"]["temp_c"],
                    fontsB["XXL"],
                ),
                top,
            )
            + SPACING
            - 2
        )

        top += (
            utils.put_icon_and_text_center(
                (HRimage, drawb, WITH_FRAMES),
                (SVG_DIR, "user.svg", REGULAR_ICON_SIZE - 14),
                (
                    "%s\N{Degree Sign}C"
                    % response_content_json["current"]["feelslike_c"],
                    fontsR["M"],
                ),
                top,
            )
            + SPACING
            + 10
        )

        top += (
            utils.put_icon_and_text_center(
                (HRimage, drawb, WITH_FRAMES),
                (SVG_DIR, "wi-strong-wind.svg", REGULAR_ICON_SIZE),
                ("%skm/h" % response_content_json["current"]["wind_kph"], fontsB["L"]),
                top,
            )
            + SPACING
        )

        top += (
            utils.put_icon_and_text_center(
                (HRimage, drawb, WITH_FRAMES),
                (SVG_DIR, "wi-umbrella.svg", REGULAR_ICON_SIZE),
                ("%smm" % response_content_json["current"]["precip_mm"], fontsB["L"]),
                top,
            )
            + SPACING
        )

        if TO_PAPER:
            epd.display(epd.getbuffer(HBimage), epd.getbuffer(HRimage))
            epd.sleep()
            print("epaper sleeps")
        else:
            HRimage.convert(mode="1").show()

        print("Sleeping until %s" % "{:%H:%M:%S}".format(utils.time_till_full()[0]))
        # break  ##########################
        time.sleep(utils.time_till_full()[1])

except IOError as e:
    print(e)

except KeyboardInterrupt:
    print("ctrl + c:")
