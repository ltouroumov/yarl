import re
from sfml import sf


def cantor_tuple(*items):
    *z1, zn = items
    if len(z1) == 0:
        return zn
    else:
        return cantor_pairing(cantor_tuple(*z1), z1)


def cantor_pairing(z1, z2):
    n1 = (z1 * -2 + 1) if z1 < 0 else (z1 * 2)
    n2 = (z2 * -2 + 1) if z2 < 0 else (z2 * 2)
    return (n1 + n2)*(n1 + n2 + 1)*0.5 + n2


def dump_vec2(vec2d):
    return ("%i;%i" % (vec2d.x, vec2d.y)).encode("ascii")


def load_vec2(data):
    x, y = map(float, data.decode('ascii').split(";"))
    return sf.Vector2(x, y)


def make_slug(raw_str):
    slug = raw_str.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = re.sub(r'[-]+', '-', slug)
    return slug


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated
        self._instance = None

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        if self._instance is None:
            self._instance = self._decorated()

        return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)