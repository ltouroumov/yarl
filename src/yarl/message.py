import logging
from yarl.util import apply_seq

logger = logging.getLogger(__name__)


class MessageBus(object):

    class Listen(object):
        def __init__(self, event, *args, **kwargs):
            self.event = event
            self.args = args
            self.kwargs = kwargs

        def __call__(self, decorated):
            if not hasattr(decorated, '__listeners__'):
                decorated.__listeners__ = []

            listener = MessageListener(decorated, self.event, *self.args, **self.kwargs)
            decorated.__listeners__.append(listener)

            return decorated

    def __init__(self):
        self.listeners = dict()

    def register(self, handler):
        props = [getattr(handler, prop) for prop in dir(handler)]
        listeners = sum([getattr(prop, '__listeners__') for prop in props if hasattr(prop, '__listeners__')], [])

        if len(listeners) == 0:
            logger.warn("object %s has no listeners", handler)
            return

        for listener in listeners:
            listener.instance = handler
            self.add_listener(listener)

    def add_listener(self, listener):
        if listener.event not in self.listeners:
            self.listeners[listener.event] = list()

        self.listeners[listener.event].append(listener)

    def emit(self, name, event, source=None):
        if name in self.listeners:
            listeners = self.listeners[name]
            apply_seq(listeners, 'handle', event, source)
        else:
            logger.info("No listeners defined for event %s", name)
            self.listeners[name] = []


class MessageListener(object):
    def __init__(self, callback, event, filters=None):
        self.instance = None
        self.callback = callback
        self.event = event
        self.filters = filters

    def handle(self, event, source):
        if self.instance is not None:
            self.callback(self.instance, event, source)
        else:
            self.callback(event, source)
