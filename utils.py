from typing import Optional

import json
import os
import time
from datetime import datetime, timedelta
from io import BytesIO

import requests
from cairosvg import svg2png
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd4in2b_V2  # type: ignore

ICON_TEXT_SPACER: int = 8


def get_text_dimensions(
    canvas: tuple[Image.Image, ImageDraw.ImageDraw, bool], text: tuple[str, ImageFont.FreeTypeFont]
) -> tuple[int, int]:
    _ImageDraw = canvas[1]
    _text_to_print, _font = text

    _text_bbox = _ImageDraw.textbbox((0, 0), "%s" % _text_to_print, _font)
    _text_bbox_width, _text_bbox_height = _text_bbox[2], _text_bbox[3]

    return (_text_bbox_width, _text_bbox_height)


def put_icon_and_text_center(
    canvas: tuple[Image.Image, ImageDraw.ImageDraw, bool],
    icon: Optional[tuple[str, str, int]],
    text: Optional[tuple[str, ImageFont.FreeTypeFont]],
    current_top: int = 0,
) -> int:
    _Image, _ImageDraw, _with_frames = canvas

    if icon is not None:
        _svg_dir, _icon_filename, _icon_size = icon
        _icon = get_icon(_svg_dir, _icon_filename, _icon_size).convert(mode="1")
        _icon_width, _icon_height = _icon.width, _icon.height
    else:
        _icon = None
        _icon_width, _icon_height = 0, 0

    if text is not None:
        _text_to_print, _font = text
        _text_to_print_width, _text_to_print_height = get_text_dimensions(canvas, text)
    else:
        _text_to_print = None
        _text_to_print_width, _text_to_print_height = 0, 0

    _width: int = int(_Image.width)
    _blockwidth = (
        _text_to_print_width
        + _icon_width
        + (ICON_TEXT_SPACER if (_text_to_print is not None and _icon is not None) else 0)
    )
    _blockheight = max(_icon_height, _text_to_print_height)

    if _icon is not None:
        _Image.paste(
            _icon,
            (int(_width / 2 - _blockwidth / 2), current_top + int((_blockheight - _icon_height) / 2)),
        )

    if _text_to_print is not None:
        _ImageDraw.text(
            (
                int(_width / 2 - _blockwidth / 2) + ((_icon_width + ICON_TEXT_SPACER) if icon is not None else 0),
                current_top + int((_blockheight - _text_to_print_height) / 2),
            ),
            _text_to_print,
            font=_font,
            fill=0,
        )

    if _with_frames:
        _ImageDraw.rectangle(
            [
                int(_width / 2 - _blockwidth / 2), current_top,
                (
                    int(_width / 2 - _blockwidth / 2) + _blockwidth,
                    current_top + _blockheight,
                ),
            ],
            outline=0,
        )
        if _icon is not None and _text_to_print is not None:
            _ImageDraw.rectangle(
                [
                    int(_width / 2 - _blockwidth / 2), current_top + int((_blockheight - _icon_height) / 2),
                    (
                        int(_width / 2 - _blockwidth / 2) + _icon_width,
                        current_top + int((_blockheight - _icon_height) / 2) + _icon_height,
                    ),
                ],
                outline=0,
            )
        if _icon is not None:
            print("%s, %s" % (_icon_width, _icon_height))

    return _blockheight


def time_till_full(full_minutes: int = 15, delay_minutes: int = 3) -> tuple[datetime, int]:
    _until: datetime = datetime.now().replace(
        minute=datetime.now().minute // full_minutes * full_minutes, second=0
    ) + timedelta(minutes=(full_minutes + delay_minutes))
    _seconds_until: int = int((_until - datetime.now()).total_seconds())

    return (_until, _seconds_until)


def init_image(
    width: int, height: int, to_paper: bool = False
) -> tuple[Image.Image, Image.Image, ImageDraw.ImageDraw, ImageDraw.ImageDraw]:
    _HBimage = Image.new("1", (width, height), 255)
    _HRimage: Image.Image = Image.new("1", (width, height), 255)
    _drawr: ImageDraw.ImageDraw = ImageDraw.Draw(_HRimage)
    if to_paper:
        _drawb: ImageDraw.ImageDraw = ImageDraw.Draw(_HBimage)
    else:
        _drawb: ImageDraw.ImageDraw = _drawr
    return (_HBimage, _HRimage, _drawb, _drawr)


def get_weatherapi_response_json(url: str) -> dict:
    _max_retry: int = 5
    _response_content_json = {}
    while _max_retry > 0:
        try:
            _response = requests.get(url)
            if _response.status_code == 200:
                _response_content_json = json.loads(_response.content)
        except:
            pass
        if _response_content_json:
            break
        _max_retry -= 1
        time.sleep(30)
    if not _response_content_json:
        raise RuntimeError("REST API call failed.")
    return _response_content_json


def init_display(to_paper: bool = False) -> tuple[epd4in2b_V2.EPD, int, int]:
    if to_paper:
        _epd = epd4in2b_V2.EPD()
        print("epaper init and Clear")
        _epd.init()
        _epd.Clear()
        print("epaper inited and Cleared")
        _width: int = _epd.width
        _height: int = _epd.height
    else:
        _epd = None
        _width: int = 400
        _height: int = 300
    return (_epd, _height, _width)  # reversed because of portrait orientation


def get_weatherapi_icon(apifilename: str, iconsfilename: str, code: int, is_day: int = 1) -> str:
    with open(apifilename) as _user_file:
        _weatherapi_parsed_json = json.load(_user_file)
    with open(iconsfilename) as _user_file:
        _icons_parsed_json = json.load(_user_file)
    try:
        _ret: str = _icons_parsed_json[
            _weatherapi_parsed_json["%s" % code]["icon-day"]
            if is_day == 1
            else _weatherapi_parsed_json["%s" % code]["icon-night"]
        ]["Resource"]
    except:
        _ret: str = "wi-na.svg"
    return _ret


def get_icon(path: str, file: str, size: int = 64, background: bool = True) -> Image.Image:
    _icon: str = os.path.join(path, file)
    _foreimage = Image.open(BytesIO(svg2png(url=_icon, parent_width=size * 4, parent_height=size * 4)))
    _foreimage = _foreimage.crop(_foreimage.getbbox())
    _foreimage = _foreimage.resize((int(size * (_foreimage.width / _foreimage.height)), size), Image.NEAREST)
    if background:
        _backimage = Image.new("RGBA", _foreimage.size, (255, 255, 255))
        _outputimage = Image.alpha_composite(_backimage, _foreimage)
    else:
        _outputimage = _foreimage
    return _outputimage


def define_fonts(path: str, file: str, sizes: dict = {"S": 16, "M": 24, "L": 32, "XL": 48, "XXL": 64}) -> dict:
    _font = os.path.join(path, file)
    _fonts = {}
    for name, size in sizes.items():
        _fonts[name] = ImageFont.truetype(_font, size)
    return _fonts
