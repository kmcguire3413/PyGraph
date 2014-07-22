'''
    This is one of the most simpliest image formats out there, and it is
    very useful to have it handy to quickly and easily dump out data in
    an image format.

    I copied the code mostly from the internet but made it into a class
    as a nicer package and so you can handle multiple images at once instead
    of using globals like the original author did.

    You can also continue to change it even after you write it out!
'''

import struct
import array
import math

def drange(s, e, step = 1):
    if s > e:
        # decrement mode
        return range(s, e, step * -1)
    # increment mode
    return range(s, e, step)

def swap2(x, y):
    return y, x

class TGAImage:
    def __init__(self, width, height, scale = 1):
        self.scale = scale
        self.w = width * scale
        self.h = height * scale
        self.offset = 0
        self.colortype = 0
        self.imagetype = 2
        self.palettestart = 0
        self.palettelen = 0
        self.palbits = 8
        self.xorigin = 0
        self.yorigin = 0
        self.bpp = 24
        self.orientation = 0
        self.data = array.array('B', (255 for i in range(self.w * self.h * 3 * self.scale)))
    def put(self, x, y, rgb):
        x = x * self.scale
        y = y * self.scale
        self.putnoscale(x, y, rgb)
    def putscaled(self, x, y, rgb):
        x = x * self.scale
        y = y * self.scale
        for _y in range(0, self.scale):
            for _x in range(0, self.scale):
                self.putnoscale(x + _x, y + _y, rgb)
    def putnoscale(self, x, y, rgb):
        y = (self.h - 1) - y
        self.data[(y * self.w + x) * 3 + 0] = rgb[2]
        self.data[(y * self.w + x) * 3 + 1] = rgb[1]
        self.data[(y * self.w + x) * 3 + 2] = rgb[0]
    def putline(self, x0, y0, x1, y1, color):
        x0 = x0 * self.scale
        y0 = y0 * self.scale
        x1 = x1 * self.scale
        y1 = y1 * self.scale

        steep = abs(y1 - y0) > abs(x1 - x0)

        if steep:
            x0, y0 = swap2(x0, y0)
            x1, y1 = swap2(x1, y1)
        if x0 > x1:
            x0, x1 = swap2(x0, x1)
            y0, y1 = swap2(y0, y1)

        dX = x1 - x0
        dY = abs(y1 - y0)
        err = dX // 2
        if y0 < y1:
            ystep = 1
        else:
            ystep = -1
        y = y0

        for x in range(x0, x1):
            if steep:
                self.putnoscale(y, x, color)
            else:
                self.putnoscale(x, y, color)
            err = err - dY
            if err < 0:
                y += ystep
                err += dX

        '''
            bool steep = Math.Abs(y1 - y0) > Math.Abs(x1 - x0);
            if (steep) { Swap<int>(ref x0, ref y0); Swap<int>(ref x1, ref y1); }
            if (x0 > x1) { Swap<int>(ref x0, ref x1); Swap<int>(ref y0, ref y1); }
            int dX = (x1 - x0), dY = Math.Abs(y1 - y0), err = (dX / 2), ystep = (y0 < y1 ? 1 : -1), y = y0;
 
            for (int x = x0; x <= x1; ++x)
            {
                if (!(steep ? plot(y, x) : plot(x, y))) return;
                err = err - dY;
                if (err < 0) { y += ystep;  err += dX; }
            }
        '''
    def save(self, path):
        fo = open(path, 'wb')
        header = struct.pack(
            '<BBBHHBHHHHBB',
            self.offset, self.colortype, self.imagetype,
            self.palettestart, self.palettelen, self.palbits,
            self.xorigin, self.yorigin, self.w, self.h, self.bpp,
            self.orientation
        )
        fo.write(header)
        fo.write(self.data.tobytes())
        fo.close()
    def drawpoints(self, points):
        ml = 0.0
        mr = 0.0
        mt = 0.0
        mb = 0.0
        # establish boundary
        for point in points:
            if point[0] > mr:
                mr = point[0]
            if point[0] < ml:
                ml = point[0]
            if point[1] > mt:
                mt = point[1]
            if point[1] < mb:
                mb = point[1]
        # render pixels for points
        mr = mr + -ml
        mt = mt + -mb
        for point in points:
            x = point[0]
            y = point[1]
            x = x + -ml             # adjust back to left
            y = y + -mb             # adjust back to bottom
            x = (x / mr) * (self.w - 1)   # scale to width
            y = (y / mt) * (self.h - 1)   # scale to height
            self.put(int(x), int(y), (90, 170, 90))
