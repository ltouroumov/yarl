__author__ = 'jdavid'


def cantor_pairing(vec2d):
    return (vec2d.x + vec2d.y)*(vec2d.x + vec2d.y + 1)/2 + vec2d.y