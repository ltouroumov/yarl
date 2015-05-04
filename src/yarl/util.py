import re
from sfml import sf


def cantor_pairing(z1, z2):
    n1 = (z1 * -2 + 1) if z1 < 0 else (z1 * 2)
    n2 = (z2 * -2 + 1) if z2 < 0 else (z2 * 2)
    return (n1 + n2)*(n1 + n2 + 1)*0.5 + n2


def dump_vec2(vec2d):
    return {'x': vec2d.x, 'y': vec2d.y}


def load_vec2(data):
    return sf.Vector2(data['x'], data['y'])


def make_slug(raw_str):
    slug = raw_str.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = re.sub(r'[-]+', '-', slug)
    return slug