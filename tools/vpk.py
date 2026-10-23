"""Small read-only VPK directory reader used to validate release archives."""
from pathlib import Path
import struct
import zlib

def read_vpk(path):
    path = Path(path)
    data = path.read_bytes()
    signature, version, tree_size = struct.unpack_from('<III', data)
    if signature != 0x55AA1234 or version not in (1, 2):
        raise ValueError('Unsupported VPK header')
    header = 12 if version == 1 else 28
    position = header

    def string():
        nonlocal position
        end = data.index(0, position)
        value = data[position:end].decode('utf8')
        position = end + 1
        return value

    entries = {}
    while extension := string():
        while folder := string():
            while name := string():
                crc, preload_size, archive, offset, size, terminator = struct.unpack_from('<IHHIIH', data, position)
                position += 18
                if terminator != 0xFFFF:
                    raise ValueError('Invalid VPK entry')
                preload = data[position:position + preload_size]
                position += preload_size
                full_name = ('' if folder == ' ' else folder + '/') + name + ('' if extension == ' ' else '.' + extension)
                entries[full_name] = (crc, preload, archive, offset, size)
    if position != header + tree_size:
        raise ValueError('VPK tree size mismatch')

    def read(name):
        crc, preload, archive, offset, size = entries[name]
        if archive == 0x7FFF:
            body = data[header + tree_size + offset:header + tree_size + offset + size]
        else:
            prefix = path.stem.removesuffix('_dir')
            with path.with_name(f'{prefix}_{archive:03d}.vpk').open('rb') as file:
                file.seek(offset)
                body = file.read(size)
        result = preload + body
        if len(body) != size or zlib.crc32(result) != crc:
            raise ValueError(f'Corrupt VPK entry: {name}')
        return result
    return entries, read

if __name__ == '__main__':
    import sys
    entries, read = read_vpk(sys.argv[1])
    if len(sys.argv) > 2:
        print(read(sys.argv[2]).decode('utf8', errors='replace'))
    else:
        print('\n'.join(entries))
