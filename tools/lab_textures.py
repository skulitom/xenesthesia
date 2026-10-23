"""Original mathematical texture data: carpet colour and liquid normal vectors.

No game images are copied or modified. Both fields loop smoothly in time; the
liquid field also tiles in space. MIT, like the other original generators.
"""
import math
import struct
from pathlib import Path
from prism_texture import downsample

SIZE = 64
WEAVE_FRAMES = 128
EDDY_FRAMES = 256


def smooth(a, b, x):
    t = max(0., min(1., (x-a)/(b-a)))
    return t*t*(3-2*t)


def weave_colour(u, v, phase):
    # Neutral along the perimeter: frayed edges and the rectangular rug border
    # retain their authored appearance. The base texture and alpha never move.
    edge = smooth(.035, .15, min(u, v, 1-u, 1-v))
    x, y = (u-.5)*math.tau, (v-.5)*math.tau
    a = x + .38*math.sin(2*y+phase)
    b = y + .38*math.sin(2*x-phase)
    radius = math.hypot(a, b)
    petals = math.cos(6*math.atan2(b, a) + .6*math.sin(phase))
    flow = 2.6*radius + .8*petals*smooth(0, .6, radius)
    flow += .8*math.sin(phase) + .35*math.sin(2*phase-radius)
    return tuple(round(255*(.5 + edge*.3*math.cos(flow+offset)))
                 for offset in (0, math.tau/3, 2*math.tau/3))


def eddy_normal(u, v, phase):
    x, y = math.tau*(u % 1), math.tau*(v % 1)
    a = x + .7*math.sin(y+phase)
    b = y + .6*math.sin(x-phase)
    # Opposing, evolving currents, not a single rotating or scrolling sheet.
    nx = .48*(math.sin(b+phase) + .4*math.sin(2*a-b-2*phase))
    ny = .48*(math.cos(a-phase) + .4*math.cos(2*b+a+phase))
    length = math.sqrt(nx*nx + ny*ny + 1)
    return tuple(round(255*(n/length*.5+.5)) for n in (nx, ny, 1.)) + (255,)


def pixels(frame, normal=False):
    count = EDDY_FRAMES if normal else WEAVE_FRAMES
    phase = math.tau*(frame % count)/count
    function = eddy_normal if normal else weave_colour
    return bytes(c for y in range(SIZE) for x in range(SIZE)
                 for c in function((x+.5)/SIZE, (y+.5)/SIZE, phase))


def normal_downsample(rgba, size):
    out = bytearray()
    for y in range(0, size, 2):
        for x in range(0, size, 2):
            normal = [sum(rgba[((y+dy)*size+x+dx)*4+c]/127.5-1
                          for dx in (0, 1) for dy in (0, 1))/4 for c in range(3)]
            length = math.sqrt(sum(n*n for n in normal))
            out.extend(round(255*(n/length*.5+.5)) for n in normal)
            out.append(255)
    return bytes(out)


def build(content):
    for name, normal, frames in [('weave', False, WEAVE_FRAMES),
                                  ('eddy_normal', True, EDDY_FRAMES)]:
        levels = [[] for _ in range(int(math.log2(SIZE))+1)]
        for frame in range(frames):
            data, size = pixels(frame, normal), SIZE
            for level in levels:
                level.append(data)
                if size > 1:
                    data = normal_downsample(data, size) if normal else downsample(data, size)
                    size //= 2
        header = bytearray(80)
        # Normal maps use linear RGBA8888 with opaque alpha; colour is RGB888.
        flags = 0x82 if normal else 0xE  # trilinear; normal OR clamp S/T
        struct.pack_into('<4sIIIHHIHH', header, 0, b'VTF\0', 7, 2, 80,
                         SIZE, SIZE, flags, frames, 0)
        struct.pack_into('<3f', header, 32, .5, .5, .5)
        struct.pack_into('<fIBiBBH', header, 48, 1., 0 if normal else 2,
                         len(levels), -1, 0, 0, 1)
        target = Path(content)/f'materials/xenesthesia/{name}.vtf'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(header+b''.join(f for level in reversed(levels) for f in level))
        print(f'Generated {name}: {target.stat().st_size} bytes.', flush=True)
