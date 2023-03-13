#!/usr/bin/env python
import json
import os
import time

import credentials_weatherapi
import utils

TO_PAPER: bool = False
WITH_FRAMES: bool = not TO_PAPER
PADDING: int = 10
SPACING: int = 14
MAIN_ICON_SIZE: int = 130
REGULAR_ICON_SIZE: int = 48
SMALL_ICON_SIZE = REGULAR_ICON_SIZE - 16
REFRESH_INTERVAL_MIN: int = 15
top: int = 0 + PADDING

SVG_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "weather_icons")  # type: ignore
API_REQ: str = r"&q=52.22,21.00&aqi=no"

epd, WIDTH, HEIGHT = utils.init_display(TO_PAPER)

fontsB: dict = utils.define_fonts("/home/pi_lukasz/fonts/readex", "ReadexPro-Bold.ttf", {"L": 32, "XXL": 78})

fontsR: dict = utils.define_fonts("/home/pi_lukasz/fonts/readex", "ReadexPro-Regular.ttf", {"S": 18, "M": 24})


try:
    while True:
        response_content_json = utils.get_weatherapi_response_json(
            credentials_weatherapi.api_url + credentials_weatherapi.api_key + API_REQ
        )

        print("LOGGING:\n\n%s" % json.dumps(response_content_json, indent=2))  # type: ignore

        if TO_PAPER:
            epd.init()  # type: ignore
            print("epaper re-inited")

        HBimage, HRimage, drawb, drawr = utils.init_image(WIDTH, HEIGHT, TO_PAPER)

        if not TO_PAPER:
            drawb.rectangle([(0, 0), (WIDTH - 1, HEIGHT - 1)], outline=0)

        top = 0 + PADDING

        # title
        top += (
            utils.put_icon_and_text_center(
                (HRimage, drawb, WITH_FRAMES),
                None,
                ("%s" % response_content_json["location"]["name"], fontsR["S"]),
                top,
            )
            + SPACING * 2
        )
        # main icon
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
            - 25
        )
        # big temperature
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
        )
        # feels like
        top += (
            utils.put_icon_and_text_center(
                (HRimage, drawb, WITH_FRAMES),
                (SVG_DIR, "user.svg", SMALL_ICON_SIZE),
                (
                    "%s\N{Degree Sign}C" % response_content_json["current"]["feelslike_c"],
                    fontsR["M"],
                ),
                top,
            )
            + SPACING * 2
        )
        # wind
        top += (
            utils.put_icon_and_text_center(
                (HRimage, drawb, WITH_FRAMES),
                (SVG_DIR, "wi-strong-wind.svg", REGULAR_ICON_SIZE),
                ("%skm/h" % response_content_json["current"]["wind_kph"], fontsB["L"]),
                top,
            )
            + SPACING
        )
        # rain
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
            epd.display(epd.getbuffer(HBimage), epd.getbuffer(HRimage))  # type: ignore
            epd.sleep()  # type: ignore
            print("epaper sleeps")
        else:
            HRimage.convert(mode="1").show()

        if not TO_PAPER:
            break
        until, seconds_until = utils.time_till_full()
        print("Sleeping until %s" % "{:%H:%M:%S}".format(until))
        time.sleep(seconds_until)

except IOError as e:
    print(e)

except KeyboardInterrupt:
    print("ctrl + c:")
