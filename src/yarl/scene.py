import logging

logger = logging.getLogger(__name__)


class SceneGraph(object):
    def __init__(self):
        self.stack = list()

    def top(self):
        return self.stack[-1]

    def push(self, scene):
        old_top = self.top()
        old_top.on_exit(next_scene=scene)
        self.stack.append(scene)
        scene.on_enter(prev_scene=old_top)

    def pop(self):
        old_top = self.stack.pop()
        new_top = self.top()
        old_top.on_exit(next_scene=new_top)
        new_top.on_enter(prev_scene=old_top)

    def update(self):
        top = self.top()
        top.update()

    def display(self, render):
        top = self.top()
        top.display(render)


class Scene(object):
    def __init__(self, scene_graph):
        self.name = type(self).__name__
        self.scene_graph = scene_graph
        self.on_init()

    def on_init(self):
        logger.debug("%s.on_init()", self.name)

    def on_enter(self, prev_scene):
        logger.debug("%s.on_enter(%s)", self.name, type(prev_scene).__name__)

    def on_exit(self, next_scene):
        logger.debug("%s.on_exit(%s)", self.name, type(next_scene).__name__)

    def update(self):
        pass

    def display(self, render):
        raise NotImplementedError
