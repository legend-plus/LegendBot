import os
from PIL import Image
import subprocess
import sys

if len(sys.argv) < 5:
    print("Correct usage: create_sprite.py <name> <sprite name> <base sprite> <character filename> [gif]")
    sys.exit()
else:
    char_name = sys.argv[1]
    sprite_name = sys.argv[2]
    base_path = sys.argv[3]
    char_path = sys.argv[4]
    if len(sys.argv) == 6 and sys.argv[5] != "false":
        gif = True
        args = ["convert", "-delay", "20", "-loop", "1", "none", "none.gif"]
    else:
        gif = False
        args = []

original_sprite = Image.open(base_path)
left_sprite = Image.open(char_path + "_left.png")
up_sprite = Image.open(char_path + "_up.png")
right_sprite = Image.open(char_path + "_right.png")
down_sprite = Image.open(char_path + "_down.png")

left_sprite.convert("RGBA")
up_sprite.convert("RGBA")
right_sprite.convert("RGBA")
down_sprite.convert("RGBA")

base_sprite = original_sprite.copy()
base_sprite.paste(left_sprite, (0, 0), left_sprite)
if not gif:
    base_sprite.save("sprites/" + char_name + "_left_" + sprite_name + ".png")
else:
    base_sprite.save("sprites/" + char_name + "_left_" + sprite_name + "1.png")
    base_sprite.save("sprites/" + char_name + "_left_" + sprite_name + "2.png")
    args[5] = "sprites/" + char_name + "_left_" + sprite_name + "*"
    args[6] = "sprites/" + char_name + "_left_" + sprite_name + ".gif"
    subprocess.call(args)
    os.remove("sprites/" + char_name + "_left_" + sprite_name + "1.png")
    os.remove("sprites/" + char_name + "_left_" + sprite_name + "2.png")

base_sprite = original_sprite.copy()
base_sprite.paste(up_sprite, (0, 0), up_sprite)
if not gif:
    base_sprite.save("sprites/" + char_name + "_up_" + sprite_name + ".png")
else:
    base_sprite.save("sprites/" + char_name + "_up_" + sprite_name + "1.png")
    base_sprite.save("sprites/" + char_name + "_up_" + sprite_name + "2.png")
    args[5] = "sprites/" + char_name + "_up_" + sprite_name + "*"
    args[6] = "sprites/" + char_name + "_up_" + sprite_name + ".gif"
    subprocess.call(args)
    os.remove("sprites/" + char_name + "_up_" + sprite_name + "1.png")
    os.remove("sprites/" + char_name + "_up_" + sprite_name + "2.png")

base_sprite = original_sprite.copy()
base_sprite.paste(right_sprite, (0, 0), right_sprite)
if not gif:
    base_sprite.save("sprites/" + char_name + "_right_" + sprite_name + ".png")
else:
    base_sprite.save("sprites/" + char_name + "_right_" + sprite_name + "1.png")
    base_sprite.save("sprites/" + char_name + "_right_" + sprite_name + "2.png")
    args[5] = "sprites/" + char_name + "_right_" + sprite_name + "*"
    args[6] = "sprites/" + char_name + "_right_" + sprite_name + ".gif"
    subprocess.call(args)
    os.remove("sprites/" + char_name + "_right_" + sprite_name + "1.png")
    os.remove("sprites/" + char_name + "_right_" + sprite_name + "2.png")

base_sprite = original_sprite.copy()
base_sprite.paste(down_sprite, (0, 0), down_sprite)
if not gif:
    base_sprite.save("sprites/" + char_name + "_down_" + sprite_name + ".png")
else:
    base_sprite.save("sprites/" + char_name + "_down_" + sprite_name + "1.png")
    base_sprite.save("sprites/" + char_name + "_down_" + sprite_name + "2.png")
    args[5] = "sprites/" + char_name + "_down_" + sprite_name + "*"
    args[6] = "sprites/" + char_name + "_down_" + sprite_name + ".gif"
    subprocess.call(args)
    os.remove("sprites/" + char_name + "_down_" + sprite_name + "1.png")
    os.remove("sprites/" + char_name + "_down_" + sprite_name + "2.png")
