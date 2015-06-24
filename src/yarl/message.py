__author__ = 'jdavid'


class MessageBus(object):

    class Listen(object):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def __call__(self, decorated):
            if not hasattr(decorated, '__listeners__'):
                decorated.__listeners__ = []

            listener = MessageListener(decorated, *self.args, **self.kwargs)
            decorated.__listeners__.append(listener)

            return decorated

    def __init__(self):
        pass

    def emit(self, message):
        pass


class MessageListener(object):
    def __init__(self, callback, filters=None):
        self.callback = callback
        self.filters = filters
