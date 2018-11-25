import json
import sys

get_emoji = True
lines = []

while get_emoji:
    emoji_line = input()
    if emoji_line != "":
        lines.append(emoji_line)
    else:
        get_emoji = False

emoji_map = [x.split(" ") for x in lines]
sprites = {}

for sprite in emoji_map:
    name = sprite[0].replace(":","")
    parts = name.split("_")
    material = parts[-1]
    dir = parts[-2]
    id = sprite[-1].split(":")[2].replace(">", "")
    if sprite[-1][0:3] == "<a:":
        animated = True
    else:
        animated = False
    if material not in sprites:
        sprites[material] = {}
    if not animated:
        sprites[material][dir] = "<:_:" + id + ">"
    else:
        sprites[material][dir] = "<a:_:" + id + ">"

print(json.dumps(sprites, indent=2))
