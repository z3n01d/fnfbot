
from typing import TypedDict
from ctypes import windll

import json
import sys
import keyboard
import asyncio

class Preset(TypedDict):
    name: str
    note_height: float
    hit_delay: float
    notes: dict[str,dict["bind": str,"x": float]]

preset: Preset = {}

preset_filename = sys.argv[1] or sys.argv[0]
preset_source = None

if not preset_filename.endswith(".json"):
    preset_filename += ".json"

if preset_filename is None:
    raise ValueError("Failed to parse a preset, did you forget to specify a preset .json file?")

with open(preset_filename) as file:
    preset_source = file.read()

if preset_source is None:
    raise ValueError("Failed to parse a preset, did you forget to specify a preset .json file?")

preset = json.loads(preset_source)

print(f"Loaded {preset['name']} preset")

paused = True
closing = False

dc = windll.user32.GetDC(0)

def getRGBfromI(RGBint: int):
    blue =  RGBint & 255
    green = (RGBint >> 8) & 255
    red =   (RGBint >> 16) & 255
    return red, green, blue

def getIfromRGB(rgb: (int,int,int)):
    red,green,blue = rgb
    RGBint = (red<<16) + (green<<8) + blue
    return RGBint

def get_pixel(x,y):
    return windll.gdi32.GetPixel(dc,x,y)

def is_empty(iterable):
    try:
        next(iterable)
    except:
        return True
    return False

""" def get_color_average(color: (float,float,float)):
    return (color[0] + color[1] + color[2]) / 3 """

async def detect_arrow(arrow: str):
    data = preset["notes"][arrow]

    raw_pixel = get_pixel(data["x"],preset["note_height"])
    pixel = getRGBfromI(raw_pixel)

    if pixel[0] > 1:
        await asyncio.sleep(preset["hit_delay"])
        keyboard.press(data["bind"])
    else:
        keyboard.release(data["bind"])



async def detect():
    if paused: return

    for _ in range(700):
        await asyncio.gather(
            detect_arrow("left"),
            detect_arrow("right"),
            detect_arrow("up"),
            detect_arrow("down")
        )

def pause():
    global paused
    paused = not paused
    if paused:
        print("Paused")
    else:
        print("Unpaused")

def close():
    global closing
    closing = True
    exit(0)

keyboard.add_hotkey("c",pause)
keyboard.add_hotkey("x",close)

print("Bot loaded\nPress X to exit\nPress C to pause/unpause")


async def main():
    while 1:
        if closing: break
        await detect()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

try:
    loop.run_until_complete(main())
    loop.run_until_complete(loop.shutdown_asyncgens())
finally:
    loop.close()