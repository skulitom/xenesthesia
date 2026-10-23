"""Original, seamless animated colour field in VTF 7.2 RGB888 format.

The data is generated from mathematics, never from Valve's texture images.
File layout: Valve SDK src/public/vtf/vtf.h (smallest mip, then each frame).
"""
import math
import struct
from pathlib import Path

SIZE = 64
FRAMES = 128
FPS = 8


def frame_pixels(frame):
    """A looping flow field: lobes bend, separate and rejoin in texture space."""
    t = math.tau * frame / FRAMES
    pixels = bytearray()
    for y in range(SIZE):
        v = math.tau * (y + .5) / SIZE
        for x in range(SIZE):
            u = math.tau * (x + .5) / SIZE
            # Independent, periodic cross-currents deform the colour shapes.
            # They never move the underlying game texture or follow the camera.
            a = u + .65*math.sin(v+t) + .28*math.sin(2*v-2*t)
            b = v + .55*math.sin(u-t) + .24*math.cos(2*u+t)
            sx, sy = math.sin(a), math.sin(b)
            radius = math.hypot(sx, sy)
            fold = math.cos(6 * math.atan2(sy, sx)) * radius
            phase = .45*math.sin(t) + 2.2*math.cos(a)*math.cos(b) + 1.1*fold
            phase += .35*math.sin(2*t + radius*3)
            grain = (((x*1973 + y*9277) ^ (x*y*26699)) % 256 / 255 - .5) * .025
            for offset in (0, math.tau/3, 2*math.tau/3):
                # MOD2X: .5 is neutral; keep luminance and texture detail intact.
                pixels.append(round(255 * (.5 + grain + .28 * math.cos(phase + offset))))
    return bytes(pixels)


def downsample(rgb, size):
    target = bytearray()
    for y in range(0, size, 2):
        for x in range(0, size, 2):
            for c in range(3):
                target.append(round(sum(rgb[((y+dy)*size+x+dx)*3+c]
                                        for dy in (0, 1) for dx in (0, 1))/4))
    return bytes(target)


def build(content):
    levels = [[] for _ in range(int(math.log2(SIZE))+1)]
    for frame in range(FRAMES):
        rgb, size = frame_pixels(frame), SIZE
        for level in levels:
            level.append(rgb)
            if size > 1:
                rgb = downsample(rgb, size)
                size //= 2
    header = bytearray(80)
    struct.pack_into('<4sIIIHHIHH', header, 0, b'VTF\0', 7, 2, 80,
                     SIZE, SIZE, 0x2, FRAMES, 0)  # trilinear, wrap both axes
    struct.pack_into('<3f', header, 32, .5, .5, .5)
    struct.pack_into('<fIBiBBH', header, 48, 1., 2, len(levels), -1, 0, 0, 1)
    target = Path(content)/'materials/xenesthesia/prism.vtf'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(header + b''.join(frame for level in reversed(levels) for frame in level))
    print(f'Generated original prismatic colour texture: {target.stat().st_size} bytes.')


if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1]/'content')
