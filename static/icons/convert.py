#!/usr/bin/env python
import Image
import os
import sys

def usage():
    print "%s filename" % sys.argv[0]
    sys.exit(0)

def main():
    if len(sys.argv) < 2:
        usage()
        return
    filename = sys.argv[1]
    image = Image.open(filename)
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            alpha = image.getpixel((x, y))[-1]
            image.putpixel((x, y), (255, 255, 255, alpha))
    image.save(filename.replace('.png', '_white.png'))

if '__main__' in __name__:
    main()
