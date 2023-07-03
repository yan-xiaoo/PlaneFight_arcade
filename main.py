import random
import math
import json

import arcade
import arcade.gui
import pyglet.clock

from configure import *

NO = 'no'
SIMPLE = 'simple'
HARD = 'hard'

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 750
SCREEN_TITLE = "Plane War"

BACKGROUND_SPEED = 480  # 像素/秒
BACKGROUND_LISTS = ["images/meteorBrown_small2.png",
                    "images/meteorBrown_small2.png",
                    "images/meteorGrey_small1.png",
                    "images/meteorGrey_small2.png",
                    "images/background_star.png"]

BULLET = ["images/laser2.png", "images/laser3.png"]
PLAYER = "images/player_ship.png"
PLAYER_HURT = "images/player_hurt.png"
PLAYER_HEAL = "images/player_heal.png"
PLAYER_FIRE = 'images/fire01.png'
PLAYER_BULLET = ["images/laser1.png"]
ENEMY = ["images/enemy1.png", "images/enemy2.png",
         "images/enemy3.png", "images/enemy4.png"]

EXPLODE = "images/explode.png"
EXPLODE_LIST = [arcade.texture.load_texture(EXPLODE),
                arcade.texture.load_texture(EXPLODE, flipped_vertically=True),
                arcade.texture.load_texture(EXPLODE, flipped_horizontally=True),
                arcade.texture.load_texture(EXPLODE, flipped_horizontally=True,
                                            flipped_vertically=True)]

HEAL = "images/heal.png"
SHIELD = "images/shield.png"
UNLIMITED_BULLET = ["images/player_skill1_false.png", "images/player_skill1_true.png",
                    ["images/player_skill1_hint1.png",
                     "images/player_skill1_hint2.png"]]
CHASE_FIRE = ["images/player_skill2_false.png", "images/missile.png", ["images/player_skill2_hint1.png",
                                                                       "images/player_skill2_hint2.png"]]

FIRE_SOUND = "sound/laser1.wav"

PLAYER_SPEED = 480  # 像素/秒
BULLET_SPEED = 300
PLAYER_BULLET_SPEED = 500

with open("difficulty.json", 'r') as f:
    DIFFICULTY = json.load(f)

SCORE_DIFFICULTY = [[0, 100, 0], [100, 150, 1], [150, 200, 2],
                    [200, 300, 3], [300, 400, 4]]


def get_difficulty(score: int):
    for i in SCORE_DIFFICULTY:
        if i[0] <= score < i[1]:
            return i[2]
    return 4


class BackgroundObjects(arcade.Sprite):
    """
    背景中会出现的一些飞行的小东西，比如星星，流星之类的
    """

    def __init__(self, image, scale=1):
        super().__init__(image, scale)
        self.center_y = SCREEN_HEIGHT
        self.center_x = random.randint(0, SCREEN_WIDTH)

    def on_update(self, delta_time=None):
        self.center_y -= BACKGROUND_SPEED * delta_time
        if self.top < 0:
            self.remove_from_sprite_lists()


class TextureButton(arcade.gui.UITextureButton):
    def __init__(self, textures, cur_index=0, update_time=0.25, enable=False, *args, **kwargs):
        super().__init__(texture=textures[cur_index], *args, **kwargs)
        self.many_textures = textures
        self.current_indexing = cur_index
        self.total_update_time = self.update_time = update_time
        self.enabled = enable

    def on_update(self, dt):
        if not self.enabled:
            self.texture = self.many_textures[1]
            return
        self.update_time -= dt
        if self.update_time <= 0:
            self.update_time = self.total_update_time
            self.current_indexing += 1
            self.current_indexing %= len(self.many_textures)
            self.texture = self.many_textures[self.current_indexing]


class Benefit(arcade.Sprite):
    """
    游戏中所有可以被玩家触碰捡起，给玩家带来好处的物体的基类
    """

    def __init__(self, image, scale=1.0, center=None, time=10):
        super().__init__(image, scale)
        if center is not None:
            self.center_x = center[0]
            self.center_y = center[1]
        self.append_texture(arcade.make_soft_circle_texture(30, (42, 45, 50)))

        self.time = time
        self.total_change_time = self.change_time = 0.33

    def on_update(self, delta_time: float = 1 / 60):
        self.time -= delta_time
        self.change_time -= delta_time
        if self.time <= 0:
            self.kill()

    def update_animation(self, delta_time: float = 1 / 60):
        if self.time <= 3 and self.change_time <= 0:
            self.change_time = self.total_change_time
            self.cur_texture_index += 1
            self.cur_texture_index = self.cur_texture_index % 2
            self.set_texture(self.cur_texture_index)

    def on_touched(self, player):
        """
        子类应当重写本方法以实现玩家触碰到增益时的效果
        :param player: 玩家对象
        :return:
        """
        pass


class Healer(Benefit):
    def on_touched(self, player):
        player: Player
        player.health += 3
        self.kill()


class Shield(Benefit):
    def on_touched(self, player):
        player: Player
        player.invincible += 3
        self.kill()


class UnlimitedBullet(Benefit):
    def on_touched(self, player):
        player: Player
        player.skills[0] = True
        self.kill()


class ChaseFire(Benefit):
    def on_touched(self, player):
        player: Player
        player.skills[1] = True
        self.kill()


BENEFITS = {Healer: HEAL, Shield: SHIELD, UnlimitedBullet: UNLIMITED_BULLET[1], ChaseFire: CHASE_FIRE[1]}


class LivingSprite(arcade.Sprite):
    """
    所有会拥有“生命”，会被有“攻击”的物体打死的物体的父类
    """

    def __init__(self, image, scale=1, health=1, invincible=0.5, *args, **kwargs):
        super().__init__(image, scale, *args, **kwargs)
        self._extra_health = 0
        if health is None:
            self._health = 1
            self.total_health = 1
        else:
            self._health = health
            self.total_health = health
        if invincible is None:
            self.total_invincible = 0.5
        else:
            self.total_invincible = invincible
        self.invincible = 0

    def on_update(self, delta_time: float = 1 / 60):
        if self.invincible > 0:
            self.invincible -= delta_time

    def on_damaged(self, bullet):
        if self.invincible <= 0:
            try:
                self.health -= bullet.damage
            except AttributeError:
                print("Warning: 出现未规定伤害的子弹，假设其伤害为1")
                self.health -= 1
            self.invincible += self.total_invincible
            if self.health <= 0:
                self.kill()

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, new_health):
        new_health = new_health if new_health < self._total_health else self._total_health
        self.on_health_change(new_health - self.health)
        self._health = new_health

    def on_health_change(self, delta_health):
        """
        该函数会在对象生命值变化时被调用
        请通过重写该函数实现受伤害时的表现
        :return:
        """
        pass

    @property
    def total_health(self):
        return self._total_health

    @total_health.setter
    def total_health(self, value):
        self._total_health = value


class Enemy(LivingSprite):
    def __init__(self, image, game_view, scale: int = 1, speed: float = 180, fire: bool = False,
                 fire_cd: float = 1, chase: str = NO, center_x=None, center_y=None, health=None, damage=None,
                 invincible=0.5,
                 *args, **kwargs):
        """
        创建一架敌机
        :param image: 用于创建飞机的图片
        :param game_view: 游戏的View页面，用来获取player的位置
        :param scale: 图片缩放的尺寸
        :param speed: 飞机飞行的速度
        :param fire: 飞机是否可以开火
        :param fire_cd: 飞机开火的cd，fire为False时不必须指定
        :param chase: 飞机的子弹是否追踪：no: 不追踪 simple: 发射时锁定 hard: 强追踪1s
        :param center_x: 飞机的初始位置x，可以不指定，默认为随机位置
        :param center_y: 飞机的初始位置y，可以不指定，默认为屏幕顶端
        :param health: 飞机的生命值，默认为1
        :param damage: 飞机在与玩家碰撞时造成的伤害，默认为1
        :param invincible: 飞机受伤后的无敌时间，默认为0.5s
        """
        super().__init__(image, scale, health=health, invincible=invincible, *args, **kwargs)
        self.change_y = -speed
        self.can_fire = fire
        self.total_fire_cd = fire_cd
        self.fire_cd = self.total_fire_cd / 2
        self.chase = chase
        self.game_view = game_view

        if center_y is None:
            self.center_y = SCREEN_HEIGHT + 20
        else:
            self.center_y = center_y
        if center_x is None:
            self.center_x = random.randint(0, SCREEN_WIDTH)
        else:
            self.center_x = center_x

        if self.chase != NO and self.game_view is None:
            raise ValueError("敌机子弹追踪必须要获取我方位置")

        self.bullets = []
        self.health = health if health is not None else 1
        self.damage = damage if damage is not None else 1

    def on_update(self, delta_time: float = 1 / 60):
        super().on_update(delta_time)
        self.center_y += self.change_y * delta_time
        self.fire_cd -= delta_time
        self.fire()
        if self.top < 0 or self.bottom > SCREEN_HEIGHT or self.left < 0 or self.right > SCREEN_WIDTH:
            self.kill()

    def kill(self):
        for one_bullet in self.bullets:
            one_bullet.kill()
        if random.random() < 0.15:
            benefit = random.choice(list(BENEFITS.keys()))
            self.game_view.game_scene.add_sprite("Benefit",
                                                 benefit(image=BENEFITS[benefit], scale=2,
                                                         center=(self.center_x, self.center_y)))
        super().kill()

    def fire(self):
        if not self.can_fire:
            return None
        if self.fire_cd <= 0:
            self.fire_cd = self.total_fire_cd
            bullet = Bullet(center=(self.center_x, self.bottom), chase=self.chase, player=self.game_view.player)
            self.game_view.game_scene.add_sprite("EnemyBullet", bullet)
            self.bullets.append(bullet)


class Bullet(arcade.Sprite):
    def __init__(self, center, image=None, chase=NO, player=None, damage=1, chase_time=1, speed=BULLET_SPEED):
        """
        创建一颗子弹
        :param chase: 子弹是否追踪
        :param player: 玩家位置，用在追踪时计算
        :param damage: 该子弹命中时造成的伤害
        """
        if image is None:
            super().__init__(random.choice(BULLET))
        else:
            super().__init__(image)
        self.chase = chase
        self.player = player
        self.center_x = center[0]
        self.center_y = center[1]
        self.chase_time = chase_time
        if self.chase != NO and self.player is None:
            raise ValueError("子弹进行追踪必须获取玩家位置")
        if chase == SIMPLE:
            x_diff = player.center_x - self.center_x
            y_diff = player.center_y - self.center_y
            angle = math.atan2(y_diff, x_diff)
            self.angle = math.degrees(angle) - 90
            self.change_y = math.sin(angle) * speed
            self.change_x = math.cos(angle) * speed
        elif chase == NO:
            self.change_y = -speed

        self.damage = damage
        self.speed = speed

    def on_update(self, delta_time=None):
        self.chase_time -= delta_time
        if self.player.health <= 0:
            self.kill()
        if self.chase == HARD and self.chase_time > 0:
            x_diff = self.player.center_x - self.center_x
            y_diff = self.player.center_y - self.center_y
            angle = math.atan2(y_diff, x_diff)
            self.angle = math.degrees(angle) - 90
            self.change_y = math.sin(angle) * self.speed
            self.change_x = math.cos(angle) * self.speed
        if self.center_x > SCREEN_WIDTH or self.center_x < 0 or self.center_y > SCREEN_HEIGHT or self.center_y < 0:
            self.kill()

        self.center_y += self.change_y * delta_time
        self.center_x += self.change_x * delta_time


class PlayerBullet(arcade.Sprite):
    def __init__(self, images, go_through=False):
        super().__init__(images)
        self.through = go_through

    def on_update(self, delta_time: float = 1 / 60):
        self.center_y += delta_time * PLAYER_BULLET_SPEED
        if self.top > SCREEN_HEIGHT:
            self.kill()


PlayerBullet.damage = 1


class Player(LivingSprite):
    """
    玩家的飞机
    """

    def __init__(self, game_view, image=None, scale=1.0, fire_cd=0.25):
        super().__init__(image, scale, health=5, invincible=0.5)
        self._enemy = []
        self._enemy_killed = 0
        self.bullet_through = False
        self.fire_cd = self.total_fire_cd = fire_cd
        self.game_view: GameView = game_view
        self.append_texture(arcade.load_texture(PLAYER_HURT))
        self.append_texture(arcade.load_texture(PLAYER_HEAL))

        self.fire_sprite = arcade.Sprite(PLAYER_FIRE, 0.5)
        self.fire_sprite.center_x = self.center_x
        self.fire_sprite.center_y = self.center_y
        self.game_view.game_scene.add_sprite("Player", self.fire_sprite)

        self._health = 5
        self.damage = 1

        self.invincible_effect = arcade.Sprite(texture=arcade.texture.make_soft_circle_texture(100, (95, 185, 240)))
        self.invincible_effect.visible = False
        self.game_view.game_scene.add_sprite("Player", self.invincible_effect)

        self.skills = {0: False, 1: False}

    def on_update(self, delta_time=None):
        super().on_update(delta_time)
        self.center_y += self.change_y * delta_time
        self.center_x += self.change_x * delta_time
        self.fire_cd -= delta_time

        if self.change_y == self.change_x == 0:
            self.fire_sprite.visible = False
        else:
            self.fire_sprite.visible = True
            self.fire_sprite.visible = True
        self.fire_sprite.center_x = self.center_x
        self.fire_sprite.top = self.bottom

        # 重置玩家位置，阻止其跑出屏幕
        if self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1
        if self.bottom < 1:
            self.bottom = 1
        if self.left < 1:
            self.left = 1
        if self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

    def update_animation(self, delta_time: float = 1 / 60):
        if self.health == 1:
            self.cur_texture_index += 1
            self.cur_texture_index = self.cur_texture_index % 2
            self.set_texture(self.cur_texture_index)
        if self.invincible > 0:
            self.invincible_effect.visible = True
            self.invincible_effect.center_x = self.center_x
            self.invincible_effect.center_y = self.center_y
        else:
            self.invincible_effect.visible = False

    def fire(self):
        if self.fire_cd <= 0 < self.health:
            self.fire_cd = self.total_fire_cd
            player_bullet = PlayerBullet(random.choice(PLAYER_BULLET), self.bullet_through)
            player_bullet.center_x = self.center_x
            player_bullet.center_y = self.top
            self.game_view.game_scene.add_sprite("PlayerBullet", player_bullet)
            self.game_view.fire_sound.play(volume=0.3)

    def kill(self):
        super().kill()
        self.fire_sprite.kill()

    def on_health_change(self, delta_health):
        if delta_health < 0:
            self.set_texture(1)
        elif delta_health > 0:
            self.set_texture(2)
        self.game_view.clock.schedule_once(lambda event: self.set_texture(0), 0.5)

    def unlimited_bullets(self, duration=5):
        """
        技能1:技能期间发弹间隔大幅度缩短，且子弹可以穿透敌方
        :param duration: 持续时间
        :return: 无
        """
        if self.skills[0]:
            self.skills[0] = False
            self.total_fire_cd = 0.05
            self.bullet_through = True
            self.game_view.clock.schedule_once(lambda event: setattr(self, "total_fire_cd", 0.25), duration)
            self.game_view.clock.schedule_once(lambda event: setattr(self, "bullet_through", False), duration)

    def chase_bullets(self):
        """
        你的攻击，结束了吗。现在，轮到我了，没意见吧！
        向场上所有敌方单位发射一颗伤害为10的追踪弹
        （搞笑的是，这个追踪弹其实用的是敌方子弹的类，只不过把追踪目标选成了敌方）
        :return:
        """
        if self.skills[1]:
            self.skills[1] = False
            self._enemy_killed = 0
            self._enemy = []
            self.game_view.clock.schedule_interval_soft(self._chase_bullets, 0.2)

    def _chase_bullets(self, _):
        for enemy in self.game_view.game_scene.get_sprite_list("Enemy"):
            if enemy not in self._enemy and self._enemy_killed + len(self._enemy) <= 6:
                self._enemy.append(enemy)
                bullet = Bullet((self.center_x, self.center_y), CHASE_FIRE[1], chase=HARD, player=enemy, damage=10,
                                chase_time=9999999, speed=600)
                self.game_view.game_scene.add_sprite("PlayerBullet", bullet)

        for one in self._enemy:
            one: arcade.Sprite
            if not one.sprite_lists:
                self._enemy_killed += 1
                self._enemy.remove(one)

        if self._enemy_killed >= 10:
            self._enemy.clear()
            self.game_view.clock.unschedule(self._chase_bullets)

    def on_damaged(self, bullet):
        if self.bullet_through:
            # 一技能期间有50%概率不受攻击伤害
            if random.random() < 0.5:
                super().on_damaged(bullet)
        else:
            super().on_damaged(bullet)


class Explosion(arcade.Sprite):
    def __init__(self, center):
        super().__init__()
        self.textures = EXPLODE_LIST
        self.center_x = center[0]
        self.center_y = center[1]
        self.life_time = 0.5

    def update_animation(self, delta_time: float = 1 / 60):
        self.cur_texture_index += 1
        if self.cur_texture_index >= len(self.textures):
            self.cur_texture_index = self.cur_texture_index % len(self.textures)
        self.set_texture(self.cur_texture_index)

    def on_update(self, delta_time: float = 1 / 60):
        self.life_time -= delta_time
        if self.life_time <= 0:
            self.kill()


def spawn_enemy(game_view, numbers: list[int], difficulty: str):
    game_view: GameView
    for _ in range(random.randint(*numbers)):
        while 1:
            plane = Enemy(random.choice(ENEMY), game_view, speed=random.randint(*DIFFICULTY[difficulty]["speed"]),
                          health=DIFFICULTY[difficulty]["health"], fire=DIFFICULTY[difficulty]["fire"],
                          fire_cd=DIFFICULTY[difficulty]["fire_cd"], chase=DIFFICULTY[difficulty]["chase"])
            if not plane.collides_with_list(game_view.game_scene["Enemy"]):
                break
        game_view.game_scene.add_sprite("Enemy", plane)


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        # 以下为初始界面内容
        self.menu_scene = arcade.Scene()
        self.menu_ui_manager = arcade.gui.UIManager()
        self.menu_v_box = arcade.gui.UIBoxLayout()
        main_text = arcade.gui.UITextArea(text="Plane War", height=70, width=390,
                                          font_name="Kenney Future", font_size=40)
        self.menu_v_box.add(main_text.with_space_around(bottom=50))
        start_button = arcade.gui.UIFlatButton(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, text="Start",
                                               width=150,
                                               style={"font_name": "Kenney Future", "font_size": 20,
                                                      "bg_color": (56, 56, 56)})
        start_button.on_click = lambda event: self.window.show_view(GameView())
        self.menu_v_box.add(start_button.with_space_around(bottom=20))
        quit_button = arcade.gui.UIFlatButton(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50, text="Quit",
                                              width=150,
                                              style={"font_name": "Kenney Future", "font_size": 20,
                                                     "bg_color": (56, 56, 56)})
        quit_button.on_click = lambda event: arcade.exit()
        self.menu_v_box.add(quit_button.with_space_around(bottom=20))
        self.menu_ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=-50,
            child=self.menu_v_box
        ))

    def on_draw(self):
        self.clear()
        self.menu_ui_manager.draw()

    def on_show_view(self):
        self.menu_ui_manager.enable()

    def on_hide_view(self):
        self.menu_ui_manager.disable()


class GameView(arcade.View):
    """
    游戏的主程序
    """

    def __init__(self):
        super().__init__()
        # 以下为游戏界面内容
        # 游戏中的GUI
        self.game_ui_manager = arcade.gui.UIManager()
        self.game_v_box = arcade.gui.UIBoxLayout()
        exit_button = arcade.gui.UIFlatButton(0, 0, text="Main Menu",
                                              width=200,
                                              style={"font_name": "Kenney Future", "font_size": 20,
                                                     "bg_color": (56, 56, 56)})
        menu_view = MenuView()
        exit_button.on_click = lambda event: self.window.show_view(menu_view)
        self.game_v_box.add(exit_button.with_space_around(bottom=20))
        self.score_text = arcade.gui.UITextArea(text="Score: 0", height=30, width=300,
                                                font_name="Kenney Future", font_size=20)

        self.pause_image = arcade.load_texture("images/pause_square.png")
        self.continue_image = arcade.load_texture("images/play.png")
        self.fire_sound = arcade.Sound(FIRE_SOUND, streaming=False)
        # 似乎arcade的音频系统在第一次播放声音前不会加载它
        # 但加载音频会导致肉眼可见的卡顿
        # 因此这里以零音量播放一次，让其提前加载好
        self.fire_sound.play(volume=0)

        self.game_v_box_right = arcade.gui.UIBoxLayout()
        self.pause_button = arcade.gui.UITextureButton(texture=arcade.load_texture("images/pause_square.png"))
        self.pause_button.on_click = self.on_click_pause
        self.game_v_box_right.add(self.pause_button)

        self.fps_text = arcade.gui.UITextArea(text="FPS: 0", height=30, width=200,
                                              font_name="Kenney Future", font_size=20)

        self.player_skill1_texture = [arcade.load_texture(UNLIMITED_BULLET[0]),
                                      arcade.load_texture(UNLIMITED_BULLET[1]),
                                      [arcade.load_texture(UNLIMITED_BULLET[2][0]),
                                       arcade.load_texture(UNLIMITED_BULLET[2][1])]]
        self.player_skill1_image = arcade.gui.UITextureButton(texture=self.player_skill1_texture[0], width=64,
                                                              height=64)
        self.player_skill1_hint = TextureButton(textures=self.player_skill1_texture[2], width=50, height=50)

        self.player_skill2_texture = [arcade.load_texture(CHASE_FIRE[0]),
                                      arcade.load_texture(CHASE_FIRE[1]),
                                      [arcade.load_texture(CHASE_FIRE[2][0]),
                                       arcade.load_texture(CHASE_FIRE[2][1])]]
        self.player_skill2_image = arcade.gui.UITextureButton(texture=self.player_skill2_texture[0], width=64,
                                                              height=64)
        self.player_skill2_hint = TextureButton(textures=self.player_skill2_texture[2], width=50, height=50)

        self.game_v_box_right.add(self.player_skill1_image.with_space_around(top=30))
        self.game_v_box_right.add(self.player_skill1_hint.with_space_around())
        self.game_v_box_right.add(self.player_skill2_image.with_space_around(top=30))
        self.game_v_box_right.add(self.player_skill2_hint.with_space_around())

        self.game_ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="left",
            align_x=30,
            align_y=-30,
            anchor_y="top",
            child=self.game_v_box
        ))
        self.game_ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="left",
            align_x=30,
            align_y=-120,
            anchor_y="top",
            child=self.score_text
        ))
        self.game_ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="right",
            align_y=-30,
            align_x=-30,
            anchor_y='top',
            child=self.game_v_box_right
        ))
        self.game_ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="left",
            align_x=30,
            align_y=30,
            anchor_y="bottom",
            child=self.fps_text
        ))
        # 建立游戏对象
        self.game_scene: arcade.Scene = arcade.Scene()
        self.paused = False
        self.clock = pyglet.clock.Clock()

        # 精灵
        self.player = Player(self)

        # 控制方向所用的变量
        self.up_pressed = None
        self.down_pressed = None
        self.left_pressed = None
        self.right_pressed = None

        self.firing = None
        self.fps_enable = False
        self.score = 0
        self.score_enable = True

    def setup(self):
        # 创建场景
        self.game_scene = arcade.Scene()
        self.game_scene.add_sprite_list("Background")
        self.game_scene.add_sprite_list("Benefit")
        self.game_scene.add_sprite_list("Enemy")
        self.game_scene.add_sprite_list("EnemyBullet")
        self.game_scene.add_sprite_list("Player")
        self.game_scene.add_sprite_list("PlayerBullet")
        self.game_scene.add_sprite_list("Explosion")

        # 玩家
        self.player = Player(self, PLAYER)
        self.player.center_x = SCREEN_WIDTH / 2
        self.player.center_y = self.player.height / 2
        self.game_scene.add_sprite("Player", self.player)

        self.paused = False
        self.fps_enable = False
        self.score = 0
        self.score_enable = True

    def on_draw(self):
        self.clear()
        self.game_scene.draw()
        self.game_ui_manager.draw()

    def update(self, delta_time: float):
        """
        更新游戏状态
        :param delta_time: 两次调用的间隔
        :return: 无
        """
        diff = self.clock.tick()
        if self.fps_enable:
            self.fps_text.text = f"FPS: {arcade.get_fps():.2f}"
        else:
            self.fps_text.text = ''
        if not self.paused:
            # 先更新内容
            self.game_scene.on_update(diff)
            self.game_scene.update_animation(diff)

            if self.score_enable:
                self.score_text.text = f"Score: {self.score}"
            else:
                self.score_text.text = f""

            # 更新玩家技能提示
            if self.player.skills[0]:
                self.player_skill1_hint.enabled = True
                self.player_skill1_image.texture = self.player_skill1_texture[1]
            else:
                self.player_skill1_hint.enabled = False
                self.player_skill1_image.texture = self.player_skill1_texture[0]

            if self.player.skills[1]:
                self.player_skill2_hint.enabled = True
                self.player_skill2_image.texture = self.player_skill2_texture[1]
            else:
                self.player_skill2_hint.enabled = False
                self.player_skill2_image.texture = self.player_skill2_texture[0]

            # 首先，随机的生成一些背景中的小东西
            if random.randint(0, 100) > 99:
                picture = random.randint(0, 7)
                if picture > 4:
                    picture = 4
                self.game_scene.add_sprite("Background",
                                           BackgroundObjects(BACKGROUND_LISTS[picture],
                                                             scale=random.randint(75, 125) / 100))
            # 然后，随机生成敌人
            if len(self.game_scene['Enemy']) <= 2 and random.random() < 0.1:
                spawn_enemy(self, [1, 3], str(get_difficulty(self.score)))

            # 检查玩家是否获得增益
            for one_benefit in self.player.collides_with_list(self.game_scene["Benefit"]):
                one_benefit: Benefit
                one_benefit.on_touched(self.player)

            # 检查玩家子弹与敌人碰撞
            for one_enemy in self.game_scene['Enemy']:
                one_enemy: Enemy
                for one_bullet in one_enemy.collides_with_list(self.game_scene["PlayerBullet"]):
                    one_enemy.on_damaged(one_bullet)
                    if not hasattr(one_bullet, "through") or not one_bullet.through:
                        one_bullet.kill()
                    if one_enemy.health <= 0:
                        explode = Explosion((one_enemy.center_x, one_enemy.center_y))
                        self.game_scene.add_sprite("Explosion", explode)
                        self.score += 10
                        break

            if self.player.health > 0:
                # 检查敌人子弹与玩家碰撞
                for one_bullet in self.player.collides_with_list(self.game_scene["EnemyBullet"]):
                    one_bullet.kill()
                    self.player.on_damaged(one_bullet)
                    if self.player.health <= 0:
                        explode = Explosion((self.player.center_x, self.player.center_y))
                        self.game_scene.add_sprite("Explosion", explode)
                        break

            # 检查玩家与敌人碰撞
            if self.player.health > 0:
                for one_enemy in self.player.collides_with_list(self.game_scene["Enemy"]):
                    one_enemy.on_damaged(self.player)
                    if one_enemy.health <= 0:
                        explode = Explosion((one_enemy.center_x, one_enemy.center_y))
                        self.game_scene.add_sprite("Explosion", explode)
                        self.score += 10
                    self.player.on_damaged(one_enemy)
                    if self.player.health <= 0:
                        explode = Explosion((self.player.center_x, self.player.center_y))
                        self.game_scene.add_sprite("Explosion", explode)
                        break

            # 检查玩家是否想开火
            if self.firing:
                self.player.fire()

            if self.player.health <= 0:
                self.end_game(False)
            if self.score > 500:
                self.end_game(True)

    def end_game(self, win: bool):
        """
        结束游戏
        :param win: 游戏是否赢了，赢：True，输：False
        :return:
        """
        over_view = GameOverView(win)
        self.window.show_view(over_view)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
            self.update_player_speed()
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
            self.update_player_speed()
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
            self.update_player_speed()

        if key == PAUSE_KEY:
            self.on_click_pause()
        if key == FIRE_KEY:
            self.firing = True
        if key == FPS_KEY:
            self.fps_enable = not self.fps_enable
        if key == SCORE_KEY:
            self.score_enable = not self.score_enable
        if key == arcade.key.KEY_1:
            self.player.unlimited_bullets(5)
        if key == arcade.key.KEY_2:
            self.player.chase_bullets()

    def on_key_release(self, key: object, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.update_player_speed()
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
            self.update_player_speed()
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
            self.update_player_speed()
        if key == FIRE_KEY:
            self.firing = False

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.firing = True

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.firing = False

    def update_player_speed(self):
        # Calculate speed based on the keys pressed
        self.player.change_x = 0
        self.player.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player.change_y = PLAYER_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player.change_y = -PLAYER_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player.change_x = -PLAYER_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player.change_x = PLAYER_SPEED

    def on_show_view(self):
        self.game_ui_manager.enable()
        self.setup()

    def on_hide_view(self):
        self.game_ui_manager.disable()

    def on_click_pause(self, _=None):
        self.paused = not self.paused
        if self.paused:
            self.pause_button.texture = self.continue_image
        else:
            self.pause_button.texture = self.pause_image


class GameOverView(arcade.View):
    """
    游戏结束时的界面
    """

    def __init__(self, result: bool):
        """
        :param result: True:胜利 False:失败
        """
        super().__init__()
        self.result = result
        self.over_ui_manager = arcade.gui.UIManager()
        self.over_v_box = arcade.gui.UIBoxLayout()
        win = "Win!" if result else "Lose"
        main_text = arcade.gui.UITextArea(text=f"You {win}", height=70, width=325,
                                          font_name="Kenney Future", font_size=40)
        self.over_ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=50,
            child=main_text
        ))

        replay_button = arcade.gui.UIFlatButton(70, SCREEN_HEIGHT - 50, text="Replay",
                                                width=250,
                                                style={"font_name": "Kenney Future", "font_size": 20,
                                                       "bg_color": (56, 56, 56)})
        replay_button.on_click = self.replay
        self.over_v_box.add(replay_button.with_space_around(bottom=20))

        main_menu_button = arcade.gui.UIFlatButton(70, SCREEN_HEIGHT - 50, text="Main Menu",
                                                   width=250,
                                                   style={"font_name": "Kenney Future", "font_size": 20,
                                                          "bg_color": (56, 56, 56)})
        main_menu_button.on_click = self.main_menu
        self.over_v_box.add(main_menu_button.with_space_around(bottom=20))

        self.over_ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=-80,
            child=self.over_v_box
        ))

    def on_hide_view(self):
        self.over_ui_manager.disable()

    def on_show_view(self):
        self.over_ui_manager.enable()

    def on_draw(self):
        self.clear()
        self.over_ui_manager.draw()

    def replay(self, _=None):
        game_view = GameView()
        self.window.show_view(game_view)

    def main_menu(self, _=None):
        menu_view = MenuView()
        self.window.show_view(menu_view)


def main():
    arcade.load_font("font/Kenney Pixel.ttf")
    arcade.enable_timings()
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.set_background_color((42, 45, 50))
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == '__main__':
    main()
