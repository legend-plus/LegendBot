def render_integer(sprites, number, padding):
    to_render = str(number).zfill(padding)
    output = ""
    for x in range(len(to_render)):
        character = to_render[x]
        if x == 0:
            pos = "l"
        elif x == len(to_render) -1:
            pos = "r"
        else:
            pos = "m"
        if "gui" in sprites and "num" in sprites["gui"]:
            if (pos + character) in sprites["gui"]["num"]:
                output += sprites["gui"]["num"][pos + character]
            else:
                output += sprites["items"]["unknown"]
        else:
            output += sprites["items"]["unknown"]
    return output