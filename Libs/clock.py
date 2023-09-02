import random

from pyglet.clock import Clock
from functools import wraps
import arcade
import time


__all__ = ["BadClock", "GameClock"]


class BadClock:
    """
    一个坏了的钟，仅仅在你更新它时才会走
    你问这玩意有什么用？用来当作pyglet.clock.Clock的计时函数。这样一来，游戏暂停的时候
    pyglet.clock.Clock就会觉得时间根本没走过，就不会更新游戏了
    """

    def __init__(self):
        self.time = time.time()
        self.time_passed = 0

    def __call__(self, *args, **kwargs):
        return self.time + self.time_passed

    def update(self, time_passed):
        """
        更新这个坏了的钟
        :param time_passed: 距离上一次更新过去的时间
        :return:None
        """
        self.time_passed += time_passed


class GameClock(Clock):
    """
    用于计算和限制帧率的类

    也可以用来定期地调用函数。添加了对于“在x秒内每y秒调用一个函数‘的支持
    """

    def schedule_interval_until(self, end_time, interval):
        """
        每间隔interval秒调用一个函数func，直到end_time秒之后结束
        本函数是一个装饰器，用法举例：

        @clock.schedule_interval_until(5, 1)
        def print_hello(dt):
            print("Hello world!")
        注意，该函数func的调用结束时间可能比你预想的早一个周期。比如，在上方的例子中，
        函数print_hello会在第1，2，3，4秒末被调用一次，第5秒末因为已经调用了unschedule，该函数不会被调用。
        函数func的参数要求与clock.schedule方法的要求一致。具体来说，函数第一个参数会被传入两次调用的间隔，而不是你自定义的值。
        :param end_time: 结束调用时间，单位为秒
        :param interval: 每两次调用函数间隔的时间，单位为秒
        :return:
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.schedule_interval(func, interval, *args, **kwargs)
                self.schedule_once(lambda dt: self.unschedule(func), end_time)

            return wrapper

        return decorator

    def schedule_interval_soft_until(self, end_time, interval):
        """
        与GameClock.schedule_interval_until基本相同。不过该函数调用的是
        schedule_interval_soft来规划
        :param end_time: 结束调用时间，单位为秒
        :param interval: 每两次调用函数间隔的时间，单位为秒
        :return:
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.schedule_interval_soft(func, interval, *args, **kwargs)
                self.schedule_once(lambda dt: self.unschedule(func), end_time)

            return wrapper

        return decorator


if __name__ == '__main__':
    clock = GameClock()


    @clock.schedule_interval_until(5, 1)
    def print_number(_, name):
        """你好"""
        print(f"Hello {name}!")


    class MyWindow(arcade.Window):
        def __init__(self):
            super().__init__()
            self.sprite = arcade.Sprite("../images/enemy1.png")
            self.sprite.color = arcade.color.GOLD
            self.sprite.center_x = self.width / 2
            self.sprite.center_y = self.height / 2
            print_number("World")

        def on_update(self, delta_time: float):
            clock.tick()

        def on_key_press(self, symbol: int, modifiers: int):
            if symbol == arcade.key.SPACE:
                self.sprite.color = random.choice([arcade.color.RED, arcade.color.GOLD, arcade.color.WHITE])

        def on_draw(self):
            self.sprite.draw()


    window = MyWindow()
    arcade.run()
