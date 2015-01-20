import Image 

im = Image.open("test1.png")
im = im.convert("RGB")

b = im.load()
width,height = im.size

all_pixels = []
for x in range(width):
    for y in range(height):
        cpixel = b[x,y]
        all_pixels.append(cpixel)
print all_pixels 
