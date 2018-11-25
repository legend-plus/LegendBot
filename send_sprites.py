import sys

materials = ["straw","water","magma","wood","cobble","path","stone","grass","snow"]
dirs = ["left","up","right","down"]

if len(sys.argv) < 2:
    print("Usage: send_sprites.py <char name>")
    sys.exit()
else:
    char = sys.argv[1]

for material in materials:
    for dir in dirs:
        emoji = ":" + char + "_" + dir + "_" + material + ":"
        print(emoji + " = \\" + emoji)