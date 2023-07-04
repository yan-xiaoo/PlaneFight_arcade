import random
import math
import json
from collections import namedtuple

import arcade
import arcade.gui
import pyglet.clock

from configure import *
import os

NO = 'no'
SIMPLE = 'simple'
HARD = 'hard'

os.chdir(os.path.dirname(os.path.abspath(__file__)))

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

BOSS = "images/boss.png"
MISSILE_ENEMY = "images/missile_enemy.png"

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
HEALTH_IMAGES = ["images/heart_empty.png", "images/heart.png"]
CANCEL_IMAGE = "images/cancel.png"

FIRE_SOUND = "sound/laser1.wav"
PLAY_FIRE_SOUND = True

PLAYER_SPEED = 480  # 像素/秒
BULLET_SPEED = 300
PLAYER_BULLET_SPEED = 500

with open("difficulty.json", 'r') as f:
    DIFFICULTY = json.load(f)

SCORE_DIFFICULTY = [[0, 100, 0], [100, 150, 1], [150, 200, 2],
                    [200, 300, 3], [300, 400, 4]]

LOADING_HINTS = []
try:
    with open("loading_hints.txt", 'r', encoding='utf-8') as f:
        while True:
            one_hint = f.readline()
            if not one_hint:
                break
            one_hint = one_hint.replace(r"\\n", '\n')
            if not one_hint.startswith("#"):
                LOADING_HINTS.append(one_hint.strip('\n'))
except (UnicodeError, FileNotFoundError):
    pass

try:
    with open("hints.json", 'r') as f:
        HINTS_STATUS = json.load(f)
except (UnicodeError, FileNotFoundError, json.JSONDecodeError):
    HINTS_STATUS = {
        "first_time": True,
        "skill1": True,
        "skill2": True,
        "heal": True,
        "shield": True
    }

try:
    # noinspection PyStatementEffect
    HINTS_STATUS['first_time']
    # noinspection PyStatementEffect
    HINTS_STATUS['skill1']
    # noinspection PyStatementEffect
    HINTS_STATUS['skill2']
    # noinspection PyStatementEffect
    HINTS_STATUS['heal']
    # noinspection PyStatementEffect
    HINTS_STATUS['shield']
except KeyError:
    print("Warning: 存储教程完成状态文件出现问题，已经重置该文件")
    HINTS_STATUS = {
        "first_time": True,
        "skill1": True,
        "skill2": True,
        "heal": True,
        "shield": True
    }

try:
    with open("setting.txt", 'r') as f:
        PLAY_FIRE_SOUND = bool(int(f.readline().strip()))
except (FileNotFoundError, UnicodeError, ValueError):
    PLAY_FIRE_SOUND = True


def get_difficulty(score: int):
    for i in SCORE_DIFFICULTY:
        if i[0] <= score < i[1]:
            return i[2]
    return 4


def get_rect(self):
    return Rect(left=self.left, right=self.right, top=self.top, bottom=self.bottom)


# 把这个方法强行塞到arcade.Sprite里头，就变成这个类的方法了，之后继承arcade.Sprite的东西都有这个方法了
arcade.Sprite.get_rect = get_rect


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


class HealthBar:
    def __init__(self, health_images, game_scene):
        self.health_images = health_images
        game_scene: GameView
        self.game_scene = game_scene
        self.buttons = [arcade.gui.UITextureButton(texture=health_images[1]) for _ in range(5)]
        self.box = arcade.gui.UIBoxLayout(vertical=False)
        for one in self.buttons:
            self.box.add(one.with_space_around(right=5))

    def on_update(self, _):
        health = self.game_scene.player.health
        for i in range(health):
            self.buttons[i].texture = self.health_images[1]
        for i in range(health, self.game_scene.player.total_health):
            self.buttons[i].texture = self.health_images[0]


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

    def __init__(self, image, scale=1, health=1, invincible=0.5, total_health=1, *args, **kwargs):
        super().__init__(image, scale, *args, **kwargs)
        self._extra_health = 0
        if health is None:
            self._health = 1
            self.total_health = 1
        else:
            self._health = health
            self.total_health = total_health
        if invincible is None:
            self.total_invincible = 0.5
        else:
            self.total_invincible = invincible
        self.invincible = 0
        self._max_damage = 1

    def on_update(self, delta_time: float = 1 / 60):
        if self.invincible > 0:
            self.invincible -= delta_time
        if self.invincible <= 0:
            self._max_damage = 1

    def on_damaged(self, bullet):
        if self.invincible <= 0:
            try:
                self.health -= bullet.damage
                self._max_damage = bullet.damage
            except AttributeError:
                print("Warning: 出现未规定伤害的子弹，假设其伤害为1")
                self.health -= 1
                self._max_damage = 1
            self.invincible += self.total_invincible
            if self.health <= 0:
                self.kill()
        if hasattr(bullet, 'damage') and self.invincible > 0:
            if bullet.damage > self._max_damage:
                self.health -= bullet.damage
                self.health += self._max_damage
                self._max_damage = bullet.damage

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


class Boss(LivingSprite):
    def __init__(self, image, game_scene, scale=1, health=1, invincible=0.5, total_health=1, *args, **kwargs):
        super().__init__(image=image, scale=scale, health=health, invincible=invincible, total_health=total_health,
                         *args, **kwargs)
        self.skill3_count = None
        self.skill2_count = None
        self._shot_count = None
        self.towards = 1
        self.game_view: GameView = game_scene
        self.damage = 1

        self.skill_cd = [6, 10, 15, 10]
        self.total_skill_cd = [16, 10, 15, 25]
        self.main_cd = 0
        self.main_cd_total = 6
        self.right_range = SCREEN_WIDTH
        self.left_range = 0
        self.skills = [self.shot, self.chase_shot, self.many_bullets, self.additional_planes]

    def on_update(self, delta_time: float = 1 / 60):
        super().on_update(delta_time)
        self.center_x += random.randint(0, 200) * delta_time * self.towards
        if self.center_x + self.width / 2 > self.right_range:
            self.center_x = self.right_range - self.width / 2
            self.towards = -self.towards
        if self.center_x < self.left_range + self.width / 2:
            self.center_x = self.left_range + self.width / 2
            self.towards = -self.towards

        for one in range(len(self.skill_cd)):
            self.skill_cd[one] -= delta_time
        self.main_cd -= delta_time

        self.skill()

    def skill(self):
        skill_available = [self.skills[i] for i in range(len(self.skills)) if self.skill_cd[i] <= 0]
        if random.random() < 0.1 and len(skill_available) > 0 >= self.main_cd:
            self.main_cd = self.main_cd_total
            skill = random.choice(skill_available)
            index = self.skills.index(skill)
            self.skill_cd[index] = self.total_skill_cd[index]
            skill()

    def drop_benefit(self):
        benefit = random.choice(list(BENEFITS.keys()))
        b = benefit(BENEFITS[benefit], center=(random.randint(int(SCREEN_WIDTH / 2 - 150), int(SCREEN_WIDTH / 2 + 150)),
                                               random.randint(int(SCREEN_HEIGHT / 2 - 150),
                                                              int(SCREEN_HEIGHT / 2 + 100))),
                    scale=2)
        self.game_view.game_scene.add_sprite("Benefit", b)

    def on_health_change(self, delta_health):
        benefit = False
        for one in range(self.health, self.health + abs(delta_health)):
            if one % 50 == 0:
                benefit = True
        if benefit:
            self.drop_benefit()

    def shot(self):
        self.game_view.clock.schedule_interval_soft(self._shot, 0.75)
        self._shot_count = 0

    def _shot(self, _=None):
        bullet = Bullet((self.center_x, self.bottom), BULLET[1], chase=NO, speed=250)
        self.game_view.game_scene.add_sprite("EnemyBullet", bullet)
        self._shot_count += 1
        if self._shot_count >= 8:
            self.game_view.clock.unschedule(self._shot)

    def chase_shot(self):
        self.skill2_count = 0
        self.game_view.clock.schedule_interval_soft(self._chase_shot, 0.5)

    def _chase_shot(self, _=None):
        self.skill2_count += 1
        bullet = Bullet((self.center_x, self.bottom), MISSILE_ENEMY, chase=HARD, speed=250, chase_time=1.5,
                        player=self.game_view.player)
        self.game_view.game_scene.add_sprite("EnemyBullet", bullet)
        if self.skill2_count >= 3:
            self.game_view.clock.unschedule(self._chase_shot)

    def many_bullets(self):
        self.skill3_count = 0
        self.game_view.clock.schedule_interval_soft(self._many_bullets, 0.1)

    def _many_bullets(self, _=None):
        self.skill3_count += 1
        bullet1 = Bullet((self.center_x, self.bottom), BULLET[1], chase=SIMPLE, speed=350, player=self.game_view.player)
        bullet2 = Bullet((self.center_x - 30, self.bottom), BULLET[1], chase=SIMPLE, speed=350,
                         player=self.game_view.player)
        bullet3 = Bullet((self.center_x + 30, self.bottom), BULLET[1], chase=SIMPLE, speed=350,
                         player=self.game_view.player)
        self.game_view.game_scene.add_sprite("EnemyBullet", bullet1)
        self.game_view.game_scene.add_sprite("EnemyBullet", bullet2)
        self.game_view.game_scene.add_sprite("EnemyBullet", bullet3)

        if self.skill3_count >= 10:
            self.game_view.clock.unschedule(self._many_bullets)

    def additional_planes(self):
        plane_a = SpecialPlane(image=ENEMY[0], scale=1, game_view=self.game_view, fire=True, chase=SIMPLE,
                               center_y=self.center_y, health=4, invincible=0)
        plane_b = SpecialPlane(image=ENEMY[0], scale=1, game_view=self.game_view, fire=True, chase=SIMPLE,
                               center_y=self.center_y, health=4, invincible=0)
        plane_a.center_x = 70
        plane_a.total_fire_cd = plane_b.total_fire_cd = 1.5
        plane_b.center_x = SCREEN_WIDTH - 70

        self.left_range = 110
        self.right_range = SCREEN_WIDTH - 110

        self.game_view.game_scene.add_sprite("Enemy", plane_a)
        self.game_view.game_scene.add_sprite("Enemy", plane_b)

        self.game_view.clock.schedule_once(lambda event: setattr(self, "left_range", 0), 15)
        self.game_view.clock.schedule_once(lambda event: setattr(self, "right_range", SCREEN_WIDTH), 15)


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
        self.total_health = self.health = health if health is not None else 1
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


class SpecialPlane(Enemy):
    def __init__(self, image, scale=1, life_time=15, *args, **kwargs):
        super().__init__(image=image, scale=scale, *args, **kwargs)
        self.life = life_time
        self.change_y = 0

    def on_update(self, delta_time: float = 1 / 60):
        super().on_update(delta_time)
        self.life -= delta_time
        if self.life <= 0:
            self.kill()

    def kill(self):
        if self.life > 0:
            benefit = random.choice(list(BENEFITS.keys()))
            self.game_view.game_scene.add_sprite("Benefit",
                                                 benefit(image=BENEFITS[benefit], scale=2,
                                                         center=(self.center_x, self.center_y)))
        super().kill()


class Bullet(arcade.Sprite):
    def __init__(self, center, image=None, chase=NO, player=None, damage=1, chase_time=1.0, speed=BULLET_SPEED):
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
        if self.player is not None and self.player.health <= 0:
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
        super().__init__(image, scale, health=5, total_health=5, invincible=0.5)
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
            if PLAY_FIRE_SOUND:
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
            if not self.game_view.boss_fight:
                self.game_view.clock.schedule_once(lambda event: setattr(self, "total_fire_cd", 0.25), duration)
                self.game_view.clock.schedule_once(lambda event: setattr(self, "bullet_through", False), duration)
            else:
                self.game_view.clock.schedule_once(lambda event: setattr(self, "total_fire_cd", 0.25), duration * 2)
                self.game_view.clock.schedule_once(lambda event: setattr(self, "bullet_through", False), duration * 2)

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
            if not self.game_view.boss_fight:
                self.game_view.clock.schedule_interval_soft(self._chase_bullets, 0.2)
            else:
                self.game_view.clock.schedule_interval_soft(self._chase_bullets_boss, 0.2)

    def _chase_bullets_boss(self, _):
        self._enemy_killed += 1
        bullet = Bullet((self.center_x, self.center_y), CHASE_FIRE[1], chase=HARD, player=self.game_view.boss,
                        damage=15,
                        chase_time=9999999, speed=600)
        self.game_view.game_scene.add_sprite("PlayerBullet", bullet)
        if self._enemy_killed > 4:
            self.game_view.clock.unschedule(self._chase_bullets_boss)

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
                                               width=200,
                                               style={"font_name": "Kenney Future", "font_size": 20,
                                                      "bg_color": (56, 56, 56)})
        start_button.on_click = lambda event: self.window.show_view(GameView())
        self.menu_v_box.add(start_button.with_space_around(bottom=20))
        setting_button = arcade.gui.UIFlatButton(text="Setting",
                                                 width=200,
                                                 style={"font_name": "Kenney Future", "font_size": 20,
                                                        "bg_color": (56, 56, 56)})
        setting_button.on_click = lambda event: self.window.show_view(SettingView())
        self.menu_v_box.add(setting_button.with_space_around(bottom=20))
        quit_button = arcade.gui.UIFlatButton(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50, text="Quit",
                                              width=200,
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


Rect = namedtuple("Rect", ['left', 'right', 'top', 'bottom'])


def __add__(self, another):
    return Rect(self.left + another.left, self.right + another.right, self.top + another.top,
                self.bottom + another.bottom)


Rect.__add__ = __add__


class HelpView(arcade.View):
    """
    游戏内悬浮帮助的主要组件
    """

    def __init__(self, game_view, hints=None, rects: list[Rect] = None, show_keys=False, callback=None):
        super().__init__()
        self.rect_to_draw = None
        self.game_view: GameView = game_view
        self.ui_manager = arcade.gui.UIManager()
        self.exit_button = arcade.gui.UITextureButton(texture=arcade.load_texture(CANCEL_IMAGE))
        self.exit_button.on_click = self.on_exit
        self.hint = arcade.gui.UITextArea(text="", font_name="华文黑体", font_size=20, text_color=(255, 255, 255),
                                          multiline=True)
        self.hints = hints if hints is not None else ['']
        self.rects = rects if rects is not None else []
        self.call_back = callback
        if show_keys:
            if 0 > len(self.hints) <= 1:
                self.hints[0] = self.hints[0] + "\n这是最后一条，按下ESC退出教程"
            elif len(self.hints) == 2:
                self.hints[0] = self.hints[0] + "\n按下回车显示下一条\n按下ESC退出教程"
                self.hints[1] = self.hints[1] + "\n这是最后一条，按下Z键显示上一条\n按下ESC退出教程"
            elif len(self.hints) > 2:
                self.hints[0] = self.hints[0] + "\n按下回车显示下一条\n按下ESC退出教程"
                self.hints[-1] = self.hints[-1] + "\n这是最后一条，按下Z键显示上一条\n按下ESC退出教程"
                for i in range(1, len(self.hints) - 1):
                    self.hints[i] += "\n按下回车显示下一条\n按下Z键显示上一条"
        self.hint.text = self.hints[0]
        self.hint.fit_content()
        self.cursor = 0
        self.ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="right",
            align_y=-30,
            align_x=-80,
            anchor_y='top',
            child=self.exit_button
        ))
        self.ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center",
            anchor_y='center',
            child=self.hint
        ))

    def next(self):
        self.cursor += 1
        if self.cursor >= len(self.hints):
            self.cursor = len(self.hints) - 1
        self.hint.text = self.hints[self.cursor]
        self.hint.fit_content()
        try:
            self.rects[self.cursor]
        except IndexError:
            self.rect_to_draw = None
        else:
            rect = self.rects[self.cursor]
            if isinstance(rect, Rect):
                self.rect_to_draw = rect
            else:
                self.rect_to_draw = None

    def last(self):
        self.cursor -= 1
        if self.cursor < 0:
            self.cursor = 0
        self.cursor = self.cursor % len(self.hints)
        self.hint.text = self.hints[self.cursor]
        self.hint.fit_content()
        try:
            self.rects[self.cursor]
        except IndexError:
            self.rect_to_draw = None
        else:
            rect = self.rects[self.cursor]
            if isinstance(rect, Rect):
                self.rect_to_draw = rect
            else:
                self.rect_to_draw = None

    def on_show_view(self):
        self.ui_manager.enable()
        self.game_view.game_ui_manager.disable()
        self.game_view.paused = True

    def on_hide_view(self):
        self.ui_manager.disable()
        self.game_view.game_ui_manager.enable()
        self.game_view.paused = False
        if self.call_back is not None:
            self.call_back()

    def on_update(self, delta_time: float):
        self.game_view.update(delta_time)
        self.ui_manager.on_update(delta_time)

    def on_draw(self):
        self.clear()
        self.game_view.on_draw()
        self.ui_manager.draw()
        if self.rect_to_draw is not None:
            arcade.draw_lrtb_rectangle_outline(self.rect_to_draw.left, self.rect_to_draw.right, self.rect_to_draw.top,
                                               self.rect_to_draw.bottom,
                                               color=(255, 255, 255), border_width=5)

    def on_exit(self, _=None):
        self.window.show_view(self.game_view)

    def on_key_press(self, symbol, _modifiers):
        if symbol == arcade.key.ESCAPE:  # resume game
            self.window.show_view(self.game_view)
        if symbol == arcade.key.ENTER:
            self.next()
        if symbol == arcade.key.Z:
            self.last()


class SettingView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = arcade.gui.UIManager()
        self.exit_button = arcade.gui.UIFlatButton(text="Main Menu", width=200,
                                                   style={"font_name": "Kenney Future", "font_size": 20,
                                                          "bg_color": (56, 56, 56)})
        self.exit_button.on_click = self.on_click_exit
        self.ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_y='top',
            anchor_x='left',
            align_x=30,
            align_y=-30,
            child=self.exit_button
        ))

        self.reset_area = arcade.gui.UIBoxLayout(vertical=False)
        self.reset_text = arcade.gui.UITextArea(text="重置所有教程为未完成", font_name="华文黑体", font_size=20,
                                                text_color=(255, 255, 255))
        self.reset_text.fit_content()
        self.reset_area.add(self.reset_text.with_space_around(right=30))
        self.reset_button = arcade.gui.UIFlatButton(text="Reset", width=150,
                                                    style={"font_name": "Kenney Future", "font_size": 20,
                                                           "bg_color": (56, 56, 56)})
        self.reset_button.on_click = self.on_click_reset
        self.reset_area.add(self.reset_button)

        self.complete_area = arcade.gui.UIBoxLayout(vertical=False)
        self.complete_text = arcade.gui.UITextArea(text="标记所有教程为完成", font_name="华文黑体", font_size=20,
                                                   text_color=(255, 255, 255))
        self.complete_text.fit_content()
        self.complete_area.add(self.complete_text.with_space_around(right=30))
        self.complete_button = arcade.gui.UIFlatButton(text="Complete", width=200,
                                                       style={"font_name": "Kenney Future", "font_size": 20,
                                                              "bg_color": (56, 56, 56)})
        self.complete_button.on_click = self.on_click_complete
        self.complete_area.add(self.complete_button)

        self.sound_area = arcade.gui.UIBoxLayout(vertical=False)
        text = "关闭射击音效" if PLAY_FIRE_SOUND else "开启射击音效"
        self.sound_text = arcade.gui.UITextArea(text=text, font_name="华文黑体", font_size=20,
                                                text_color=(255, 255, 255))
        self.sound_text.fit_content()
        self.sound_area.add(self.sound_text.with_space_around(right=30))
        text = "Close" if PLAY_FIRE_SOUND else "Open"
        self.sound_button = arcade.gui.UIFlatButton(text=text, width=150,
                                                    style={"font_name": "Kenney Future", "font_size": 20,
                                                           "bg_color": (56, 56, 56)})
        self.sound_button.on_click = self.on_click_sound
        self.sound_area.add(self.sound_button)

        self.ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center",
            anchor_y='center',
            align_y=50,
            child=self.reset_area
        ))
        self.ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center",
            anchor_y='center',
            align_y=-10,
            child=self.complete_area
        ))
        self.ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_y='center',
            anchor_x='center',
            align_y=-70,
            child=self.sound_area
        ))

    def on_show_view(self):
        self.ui_manager.enable()

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_click_exit(self, _=None):
        menu_view = MenuView()
        self.window.show_view(menu_view)

    def on_click_complete(self, text=None):
        if text not in ["Ok", "Cancel"]:
            m = arcade.gui.UIMessageBox(width=300, height=150, message_text="Mark all tutorials as completed?", buttons=["Ok", "Cancel"],
                                        callback=self.on_click_complete)
            self.ui_manager.add(m)
        elif text == 'Ok':
            global HINTS_STATUS
            HINTS_STATUS = {
                "first_time": False,
                "skill1": False,
                "skill2": False,
                "heal": False,
                "shield": False
            }

    def on_click_reset(self, text=None):
        if text not in ["Ok", "Cancel"]:
            m = arcade.gui.UIMessageBox(width=300, height=150, message_text="Mark all tutorials as not read?", buttons=["Ok", "Cancel"],
                                        callback=self.on_click_reset)
            self.ui_manager.add(m)
        elif text == 'Ok':
            global HINTS_STATUS
            HINTS_STATUS = {
                "first_time": True,
                "skill1": True,
                "skill2": True,
                "heal": True,
                "shield": True
            }

    def on_click_sound(self, _=None):
        global PLAY_FIRE_SOUND
        PLAY_FIRE_SOUND = not PLAY_FIRE_SOUND
        self.sound_text.text = "关闭射击音效" if PLAY_FIRE_SOUND else "开启射击音效"
        self.sound_text.fit_content()
        self.sound_button.text = "Close" if PLAY_FIRE_SOUND else "Open"

    def on_update(self, delta_time: float):
        self.ui_manager.on_update(delta_time)

    def on_draw(self):
        self.clear()
        self.ui_manager.draw()


class GameView(arcade.View):
    """
    游戏的主程序
    """

    def __init__(self, boss_fight=False, boss_health=1000):
        super().__init__()
        # 以下为游戏界面内容
        # 游戏中的GUI
        self.showed = False
        self.boss_health = boss_health
        self.game_ui_manager = arcade.gui.UIManager()
        self.game_v_box = arcade.gui.UIBoxLayout()
        self.exit_button = arcade.gui.UIFlatButton(0, 0, text="Main Menu",
                                                   width=200,
                                                   style={"font_name": "Kenney Future", "font_size": 20,
                                                          "bg_color": (56, 56, 56)})
        menu_view = MenuView()
        self.exit_button.on_click = lambda event: self.window.show_view(menu_view)
        self.game_v_box.add(self.exit_button.with_space_around(bottom=20))
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

        self.health_bar = HealthBar([arcade.load_texture(HEALTH_IMAGES[0]), arcade.load_texture(HEALTH_IMAGES[1])],
                                    self)
        self.boss_health_bar = arcade.gui.UITextArea(text="Boss: 1000 / 1000", font_name="Kenney Future", font_size=30,
                                                     text_color=(255, 0, 0), width=500)

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
            align_y=-150,
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
        self.game_ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x='left',
            align_x=30,
            align_y=-100,
            anchor_y='top',
            child=self.health_bar.box
        ))
        # 建立游戏对象
        self.game_scene: arcade.Scene = arcade.Scene()
        self.paused = False
        self.clock = pyglet.clock.Clock()

        # 控制方向所用的变量
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False

        self.firing = False

        self.boss_fight = boss_fight

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
        if self.boss_fight:
            self.boss = Boss(image=BOSS, game_scene=self, health=self.boss_health, total_health=1000, invincible=0.1,
                             center_x=SCREEN_WIDTH / 2, center_y=SCREEN_HEIGHT - 180)
            self.game_scene.add_sprite("Enemy", self.boss)
            self.game_ui_manager.add(arcade.gui.UIAnchorWidget(
                anchor_x='center',
                anchor_y='top',
                align_y=-30,
                align_x=50,
                child=self.boss_health_bar
            ))

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
        if self.score_enable:
            self.score_text.text = f"Score: {self.score}"
        else:
            self.score_text.text = f""
        if not self.paused:
            # 先更新内容
            self.game_scene.on_update(diff)
            self.game_scene.update_animation(diff)
            self.health_bar.on_update(diff)

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
            if len(self.game_scene['Enemy']) <= 2 and random.random() < 0.1 and not self.boss_fight:
                spawn_enemy(self, [1, 3], str(get_difficulty(self.score)))

            # 检查Boss该不该生成
            if self.score > 500 and not self.boss_fight:
                self.boss_fight = True
                self.boss = Boss(image=BOSS, game_scene=self, health=self.boss_health, total_health=1000,
                                 invincible=0.1,
                                 center_x=SCREEN_WIDTH / 2, center_y=SCREEN_HEIGHT - 180)
                self.game_scene.add_sprite("Enemy", self.boss)
                self.game_ui_manager.add(arcade.gui.UIAnchorWidget(
                    anchor_x='center',
                    anchor_y='top',
                    align_y=-30,
                    align_x=50,
                    child=self.boss_health_bar
                ))

            # Boss战时才更新的内容：
            if self.boss_fight:
                self.boss_health_bar.text = f"Boss: {self.boss.health} / {self.boss.total_health}"

            # 检查玩家是否获得增益
            for one_benefit in self.player.collides_with_list(self.game_scene["Benefit"]):
                one_benefit: Benefit
                if isinstance(one_benefit, UnlimitedBullet) and HINTS_STATUS['skill1']:
                    self.clock.schedule_once(self.show_skill1_hints, 0.1)
                elif isinstance(one_benefit, ChaseFire) and HINTS_STATUS['skill2']:
                    self.clock.schedule_once(self.show_skill2_hints, 0.1)
                elif isinstance(one_benefit, Healer) and HINTS_STATUS['heal']:
                    self.clock.schedule_once(self.show_heal_hints, 0.1)
                elif isinstance(one_benefit, Shield) and HINTS_STATUS['shield']:
                    self.clock.schedule_once(self.show_shield_hints, 0.1)
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
            if self.boss_fight and self.boss.health <= 0:
                self.end_game(True)

    def end_game(self, win: bool):
        """
        结束游戏
        :param win: 游戏是否赢了，赢：True，输：False
        :return:
        """
        over_view = GameOverView(win, self)
        self.window.show_view(over_view)

    def show_first_time_hints(self):
        """展示第一次进入游戏时的提示"""
        words = ["欢迎来到游戏！\n看起来你第一次进入游戏，\n下面的教程将会帮你熟悉本游戏",
                 "左侧矩形圈出的是你控制的飞机的心心。\n"
                 "你的飞机一共有五颗心心\n"
                 "，受到伤害就会减少一颗。\n"
                 "失去所有心心后，游戏失败",
                 "通过WASD键控制飞机，按住空格或鼠标左键射击\n"
                 "成功击败游戏最后出现的Boss后，游戏胜利",
                 "你可以通过点击左上方圈出的按钮返回主界面",
                 "你可以通过点击右上角圈出的按钮或E键暂停"]
        right_box = get_rect(self.game_v_box_right)
        pause_button_box = Rect(right_box.left, right_box.right, right_box.top,
                                right_box.top - self.pause_button.height)
        rects = [None, get_rect(self.health_bar.box), None,
                 get_rect(self.game_v_box), pause_button_box]
        hint_view = HelpView(self, hints=words, rects=rects, show_keys=True,
                             callback=lambda: HINTS_STATUS.__setitem__("first_time", False))
        self.window.show_view(hint_view)

    def show_skill1_hints(self, _=None):
        words = ["你刚刚捡起的是技能补给，能够使你的一技能完成充能。",
                 "充能完成后，右侧圈起的技能图标会亮起，下方的按键也会不断闪烁\n"
                 "此时按下“1”键即可激活技能",
                 "该技能的效果为：在五秒内玩家的攻击间隔极大程度缩短，\n"
                 "并且子弹可以穿过敌人。\n"
                 "同时，受到攻击时有50%概率不受伤害"]
        rects = [None, get_rect(self.player_skill1_image), None]
        hint_view = HelpView(self, hints=words, rects=rects, show_keys=True,
                             callback=lambda: HINTS_STATUS.__setitem__("skill1", False))
        self.window.show_view(hint_view)

    def show_skill2_hints(self, _=None):
        words = ["你刚刚捡起的是技能补给，能够使你的二技能完成充能。",
                 "充能完成后，右侧圈起的技能图标会亮起，\n"
                 "下方的按键也会不断闪烁。此时按下“2”键即可激活技能",
                 "该技能的效果为：持续锁定场上敌机，向它们发射追踪弹，\n"
                 "技能持续直到有七名被锁定的敌人被击败"]
        rects = [None, get_rect(self.player_skill2_image), None]
        hint_view = HelpView(self, hints=words, rects=rects, show_keys=True,
                             callback=lambda: HINTS_STATUS.__setitem__("skill2", False))
        self.window.show_view(hint_view)

    def show_heal_hints(self, _=None):
        words = ["你刚刚捡起的是血量补给，可以为你恢复血量\n"
                 "一个血量补给可以恢复三颗心心",
                 "请注意，在心心已满时捡起血量补给不会有任何作用"]
        rects = [get_rect(self.health_bar.box), None]
        hint_view = HelpView(self, hints=words, rects=rects, show_keys=False,
                             callback=lambda: HINTS_STATUS.__setitem__("heal", False))
        self.window.show_view(hint_view)

    def show_shield_hints(self, _=None):
        words = ["你刚刚捡起的是无敌盾补给，可以为你提供无敌状态\n"
                 "该补给可以使你在三秒内不受任何伤害",
                 "无敌状态下，你的飞机周围会出现一圈淡蓝色光晕",
                 "该补给的效果可以叠加"]
        rects = [None, get_rect(self.player), None]
        hint_view = HelpView(self, hints=words, rects=rects, show_keys=False,
                             callback=lambda: HINTS_STATUS.__setitem__("shield", False))
        self.window.show_view(hint_view)

    def on_key_press(self, symbol, modifiers):
        """Called whenever a key is pressed. """

        if symbol == arcade.key.UP or symbol == arcade.key.W:
            self.up_pressed = True
            self.update_player_speed()
        elif symbol == arcade.key.DOWN or symbol == arcade.key.S:
            self.down_pressed = True
            self.update_player_speed()
        elif symbol == arcade.key.LEFT or symbol == arcade.key.A:
            self.left_pressed = True
            self.update_player_speed()
        elif symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.right_pressed = True
            self.update_player_speed()

        if symbol == PAUSE_KEY:
            self.on_click_pause()
        if symbol == FIRE_KEY:
            self.firing = True
        if symbol == FPS_KEY:
            self.fps_enable = not self.fps_enable
        if symbol == SCORE_KEY:
            self.score_enable = not self.score_enable
        if symbol == arcade.key.KEY_1:
            self.player.unlimited_bullets(5)
        if symbol == arcade.key.KEY_2:
            self.player.chase_bullets()

    def on_key_release(self, symbol: object, modifiers):
        """Called when the user releases a key. """

        if symbol == arcade.key.UP or symbol == arcade.key.W:
            self.up_pressed = False
            self.update_player_speed()
        elif symbol == arcade.key.DOWN or symbol == arcade.key.S:
            self.down_pressed = False
            self.update_player_speed()
        elif symbol == arcade.key.LEFT or symbol == arcade.key.A:
            self.left_pressed = False
            self.update_player_speed()
        elif symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.right_pressed = False
            self.update_player_speed()
        if symbol == FIRE_KEY:
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
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.player.change_x = 0
        self.player.change_y = 0

        self.firing = False

        if HINTS_STATUS['first_time']:
            self.show_first_time_hints()

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

    def __init__(self, result: bool, game_scene):
        """
        :param result: True:胜利 False:失败
        """
        super().__init__()
        self.result = result
        game_scene: GameView
        self.game_scene = game_scene
        self.over_ui_manager = arcade.gui.UIManager()
        self.over_v_box = arcade.gui.UIBoxLayout()
        win = "Win!" if result else "Lose"
        main_text = arcade.gui.UITextArea(text=f"You {win}", height=70, width=325,
                                          font_name="Kenney Future", font_size=40)
        self.over_ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=100 if LOADING_HINTS else 70,
            child=main_text
        ))

        self.hint_text = arcade.gui.UITextArea(font_name="华文黑体", font_size=25)
        if LOADING_HINTS:
            self.over_ui_manager.add(arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                align_y=20,
                child=self.hint_text
            ))
            self.hint_text.text = random.choice(LOADING_HINTS)
            self.hint_text.fit_content()

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
            align_y=-100 if LOADING_HINTS else -80,
            child=self.over_v_box
        ))

        hint_text = arcade.gui.UITextArea(font_name="华文黑体", font_size=15)
        self.over_ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="right",
            anchor_y="bottom",
            align_x=-30,
            align_y=30,
            child=hint_text
        ))
        if LOADING_HINTS:
            hint_text.text = "按Enter显示下一条"
            hint_text.fit_content()

    def on_hide_view(self):
        self.over_ui_manager.disable()

    def on_show_view(self):
        self.over_ui_manager.enable()

    def on_draw(self):
        self.clear()
        self.over_ui_manager.draw()

    def replay(self, _=None):
        if self.game_scene.boss_fight and not self.result:
            game_view = GameView(boss_fight=True,
                                 boss_health=min(self.game_scene.boss.health + 50, self.game_scene.boss_health))
        else:
            game_view = GameView(boss_fight=False)
        self.window.show_view(game_view)

    def main_menu(self, _=None):
        menu_view = MenuView()
        self.window.show_view(menu_view)

    def next_hint(self):
        try:
            cursor = LOADING_HINTS.index(self.hint_text.text)
        except ValueError:
            return
        else:
            cursor += 1
            cursor = cursor % len(LOADING_HINTS)
        self.hint_text.text = LOADING_HINTS[cursor]
        self.hint_text.fit_content()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ENTER and LOADING_HINTS:
            self.next_hint()


def main():
    arcade.load_font("font/Kenney Future.ttf")
    arcade.load_font("font/华文黑体.ttf")
    arcade.enable_timings()
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.set_background_color((42, 45, 50))
    menu_view = MenuView()
    window.show_view(menu_view)
    try:
        arcade.run()
    finally:
        with open("hints.json", 'w') as file:
            json.dump(HINTS_STATUS, file, indent=4, ensure_ascii=False)
        with open("setting.txt", 'w') as file:
            file.write("1" if PLAY_FIRE_SOUND else "0")


if __name__ == '__main__':
    main()
