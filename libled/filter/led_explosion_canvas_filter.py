from led_canvs_filter import LedCanvasFilter
from ..led_cube import *
from ..util.color import Color
from ..util.cube_util import *
from ..util.common_util import *
import math
import time
import numpy as np
import colorsys
import random
import time
from ..util.hw_controller_util import get_data_as_json
from ..util.sound_interface import SoundInterface


def red(ix):
    i = int(ix) % 90
    if i < 30:
        return i * 255 / 30
    elif i < 60:
        return (60 - i) * 255 / 30
    else:
        return 0
def rgb(ix):
    n = math.floor(ix * 1 * 90)
    return red(n) * 0x10000 + red(n+30) * 0x100 + red(n+60) * 0x1

class LedExplosionCanvasFilter(LedCanvasFilter):

    def __init__(self, canvas, dimension=3, enable_controller=False):
        super(LedExplosionCanvasFilter, self).__init__(canvas, enable_controller)
        self.t = 0
        self.dimension = dimension
        self.param = None
        self.speeds = self.get_new_canvas()
        self.centers = self.get_new_canvas()
        self.wav = 'se_explosion.wav'
        self._pre_sign = -1
        self.sin = 0

    def get_new_canvas(self):
        return create_nested_dict(3)

    def get_speeds(self, x, y, z):
        ctrl = 1
        if self.speeds[x][y][z] is None:
            self.speeds[x][y][z] = (random.uniform(1.5 * ctrl, 3.0 * ctrl), 
                                    random.uniform(2.0 * ctrl, 4.0 * ctrl))
        return self.speeds[x][y][z]
        
    def get_center(self, x, y, z):
        if self.centers[x][y][z] is None:
            if self.dimension == 3:
                self.centers[x][y][z] = \
                        (LED_WIDTH / 2.0 + random.uniform(-1, 1),  \
                        LED_HEIGHT / 4.0 * 3 + random.uniform(-1, 1), \
                        LED_DEPTH / 2 + random.uniform(-1, 1))
            else:
                self.centers[x][y][z] = \
                        (LED_WIDTH / 2.0 + random.uniform(-1, 1),  \
                        LED_HEIGHT / 4.0 * 3 + random.uniform(-1, 1), \
                        -1 + random.uniform(-1, 1))
        return self.centers[x][y][z]

    def pre_draw(self):
        super(LedExplosionCanvasFilter, self).pre_draw()
        self.param = self.get_param_from_controller(defaults={'a0':0.5, 'a1':0.5})
        self.t += 0.01 + (self.param['a0'] * 0.28)
        self.sin = math.sin(self.t)
        sign = np.sign(math.sin(self.t))
        # play sound
        if self._pre_sign < 0 and sign > 0:
            SoundInterface.play(wav=self.wav)
        self._pre_sign = sign

    def set_led(self, xx, yy, zz, color):
        x = int(round(xx))
        y = int(round(yy))
        z = int(round(zz))
        center = self.get_center(x, y, z)

        if self.sin > 0:
            for speed in self.get_speeds(x, y, z):
                pt = np.array([xx - center[0], yy - center[1], zz - center[2]])
                pt *= self.sin * 6 * speed * self.param['a1'] + 1
                self.canvas.set_led(pt[0] + center[0], pt[1] + center[1], pt[2] + center[2], color)
        else:
            self.canvas.set_led(xx, yy, zz, color)
