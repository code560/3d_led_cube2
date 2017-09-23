from led_object import LedObject
from ..util import led_draw_util

class LedRippleObject(LedObject):

    FIRST_R = 2

    def __init__(self, x, y, color, lifetime = 0 ):
        super(LedRippleObject, self).__init__(lifetime)
        self.x = x
        self.y = y
        self.color = color
        self.produced = 0
        self.ripples = [LedRippleObject.FIRST_R]
        self.last_update = 0.0

    def is_expired(self):
        return (self.produced != 0 and len(self.ripples) == 0)

    def draw(self, canvas):
        is_need_update = False
        if self.last_update == 0:
            self.last_update = self.elapsed()
            
        if self.elapsed() - self.last_update > 0.1:
            self.last_update = self.elapsed()
            is_need_update = True

        if min(self.ripples) - 4 >= LedRippleObject.FIRST_R and self.produced < 4:
            self.ripples.append(LedRippleObject.FIRST_R)
            self.produced += 1

        new_ripples = []
        for r in self.ripples:
            if r > 40:
                continue
            else:
                led_draw_util.circle(canvas, self.x, self.y, 0, self.color, r)

            if is_need_update:
                new_ripples.append(r+1)
            else:
                new_ripples.append(r)
        
        self.ripples = new_ripples