import random

from entities.drawable_entity import DrawableEntity
from utils import rect_in_world, rects_are_overlapping, normalize


class Explorer(DrawableEntity):
    SIZE = 7
    MAX_VELOCITY = 0.9
    PICKUP_REACH = 1
    SENSOR_RANGE = 15
    SENSE_DELAY = 100
    COLOR = 'blue'
    SENSOR_COLOR = 'yellow'

    def __init__(self, x, y, world):
        self.x = x
        self.y = y
        self.world = world
        self.dx, self.dy = self._get_new_direction()
        self.ticks = 0
        self.has_rock = False

    def draw(self, canvas):
        helper = Explorer(self.x, self.y, self.world)
        helper.SIZE = 2 * self.SENSOR_RANGE + self.SIZE
        top_left, bottom_right = helper.get_bounds()
        canvas.create_oval(top_left.x,
                           top_left.y,
                           bottom_right.x,
                           bottom_right.y,
                           outline=self.SENSOR_COLOR)

        top_left, bottom_right = self.get_bounds()
        canvas.create_rectangle(top_left.x,
                                top_left.y,
                                bottom_right.x,
                                bottom_right.y,
                                fill=self.COLOR)

    def tick(self):
        self._tick()
        self.ticks += 1

    def _tick(self):
        if self.has_rock:
            # Try to drop at base.
            if self._drop_available():
                self.has_rock = False
                return

            # Head towards base.
            self.dx, self.dy = normalize(self.world.mars_base.x - self.x,
                                         self.world.mars_base.y - self.y)

        else:
            # Pick up.
            rock = self._rock_available()
            if rock:
                self.has_rock = True
                self.world.remove_entity(rock)
                return

            # Head towards rock.
            rock = self._sense_rock()
            if rock:
                self.dx, self.dy = normalize(rock.x - self.x, rock.y - self.y)

        # Keep walkin'.
        while not self._can_move():
            self.dx, self.dy = self._get_new_direction()
        self._move()

    def _move(self):
        self.x += self.dx
        self.y += self.dy

    def _get_new_direction(self):
        dx = random.uniform(-self.MAX_VELOCITY, self.MAX_VELOCITY)
        dy = random.uniform(-self.MAX_VELOCITY, self.MAX_VELOCITY)
        return normalize(dx, dy)

    def _can_move(self):
        new_self = Explorer(self.x + self.dx,
                            self.y + self.dy,
                            self.world)
        bounds = new_self.get_bounds()

        if not rect_in_world(bounds, new_self.world):
            return False

        for other in new_self.world.entities:
            # Allow collisions with other explorers.
            if isinstance(other, Explorer):
                continue

            if rects_are_overlapping(bounds, other.get_bounds()):
                return False

        return True

    def _rock_available(self):
        for rock in self.world.rocks:
            if rects_are_overlapping(self.get_bounds(),
                                     rock.get_bounds(),
                                     self.PICKUP_REACH):
                return rock

        return False

    def _sense_rock(self):
        # Wait a bit so that the explorers spread out.
        if self.ticks < self.SENSE_DELAY:
            return None

        for rock in self.world.rocks:
            if rects_are_overlapping(self.get_bounds(),
                                     rock.get_bounds(),
                                     self.SENSOR_RANGE):
                return rock

        return None

    def _drop_available(self):
        if rects_are_overlapping(self.get_bounds(),
                                 self.world.mars_base.get_bounds(),
                                 self.PICKUP_REACH):
            return True
        return False
