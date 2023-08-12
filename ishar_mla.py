import random
import math
import json
import sys
import time
from typing import Union
from collections import namedtuple
import arcade
import arcade.gui
import pyglet.clock
import pyglet.media

from configure import *
import os

# 定义追踪难度的常量
NO = 'no'
SIMPLE = 'simple'
HARD = 'hard'

# 为能兼容Pyinstaller而使用，在这里修改工作目录，这样arcade才能在打包好的东西中找到其需要的文件
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 屏幕的宽，高，标题
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 750
SCREEN_TITLE = "Plane War"

# 定义背景速度与背景图片的路径
BACKGROUND_SPEED = 480  # 像素/秒
BACKGROUND_LISTS = ["images/meteorBrown_small2.png",
                    "images/meteorBrown_small2.png",
                    "images/meteorGrey_small1.png",
                    "images/meteorGrey_small2.png",
                    "images/background_star.png"]

BACKGROUND_COLOR = (12, 20, 53)
BACKGROUND_COLOR2 = (10, 18, 40)

# 这是敌方子弹的图片
BULLET = ["images/laser2.png", "images/laser3.png"]
PLAYER = "images/player_ship.png"
PLAYER_HURT = "images/player_hurt.png"
PLAYER_HEAL = "images/player_heal.png"
PLAYER_FIRE = 'images/fire01.png'
# 我方子弹的图片
PLAYER_BULLET = "images/laser1.png"
ENEMY = ["images/enemy1.png", "images/enemy2.png",
         "images/enemy3.png", "images/enemy4.png"]

start = time.time()
BOSS = arcade.load_texture("dlc_ishar_mla/images/fight_idle/1.png")
BOSS_MOVE = [f"dlc_ishar_mla/images/move1/{i}.png" for i in range(1, 15)]
BOSS_MOVE = [arcade.load_texture_pair(i) for i in BOSS_MOVE]
BOSS_MOVE = list(zip(*BOSS_MOVE))
BOSS_SKILL = [f"dlc_ishar_mla/images/skill1/{i}.png/" for i in range(1, 29)]
BOSS_SKILL = [arcade.load_texture_pair(i) for i in BOSS_SKILL]
BOSS_SKILL = list(zip(*BOSS_SKILL))
BOSS_DIE = [f"dlc_ishar_mla/images/die1/{i}.png" for i in range(1, 30)]
BOSS_DIE = [arcade.load_texture_pair(i) for i in BOSS_DIE]
BOSS_DIE = list(zip(*BOSS_DIE))
BOSS_ATTACK = [f"dlc_ishar_mla/images/attack1/{i}.png" for i in range(1, 29)]
BOSS_ATTACK = [arcade.load_texture_pair(i) for i in BOSS_ATTACK]
BOSS_ATTACK = list(zip(*BOSS_ATTACK))
BOSS_ATTACK_1 = "dlc_ishar_mla/images/boss_attack_1.png"
BOSS_THROW_BALL = 'dlc_ishar_mla/images/throw_ball.png'
BOSS_TEARS = "dlc_ishar_mla/images/tear.png"
BOSS_TEARS_TOUCHED = "dlc_ishar_mla/images/tear_down.png"
BOSS_TEARS_ENERGY = "dlc_ishar_mla/images/tear_energy.png"
ALL_BOSS_TEXTURES = [*BOSS_MOVE[0], *BOSS_MOVE[1], *BOSS_SKILL[0], *BOSS_SKILL[1], *BOSS_DIE[0], *BOSS_DIE[1], *BOSS_ATTACK[0], *BOSS_ATTACK[1]]


# 敌方导弹的图片
MISSILE_ENEMY = "images/missile_enemy.png"

# 爆炸特效是一张图片和这张图的水平/竖直翻转构成的
EXPLODE = "images/explode.png"
EXPLODE_LIST = [arcade.texture.load_texture(EXPLODE),
                arcade.texture.load_texture(EXPLODE, flipped_vertically=True),
                arcade.texture.load_texture(EXPLODE, flipped_horizontally=True),
                arcade.texture.load_texture(EXPLODE, flipped_horizontally=True,
                                            flipped_vertically=True)]

# 增益所使用的图像
HEAL = "images/heal.png"
SHIELD = "images/shield.png"
UNLIMITED_BULLET = ["images/player_skill1_false.png", "images/player_skill1_true.png",
                    ["images/player_skill1_hint1.png",
                     "images/player_skill1_hint2.png"]]
CHASE_FIRE = ["images/player_skill2_false.png", "images/missile.png", ["images/player_skill2_hint1.png",
                                                                       "images/player_skill2_hint2.png"]]
HEALTH_IMAGES = ["images/heart_empty.png", "images/heart.png"]
CANCEL_IMAGE = "images/cancel.png"
FIGHT_IDLE = [f"dlc_ishar_mla/images/fight_idle/{i}.png" for i in range(1, 92)]

FIRE_SOUND = "sound/laser1.wav"
BATTLE_SOUND = ["dlc_ishar_mla/sounds/battle1.wav", "dlc_ishar_mla/sounds/battle2.wav"]
MENU_SOUND = ["dlc_ishar_mla/sounds/menu1.wav", "dlc_ishar_mla/sounds/menu2.wav",
              "dlc_ishar_mla/sounds/menu3.wav"]
MENU_SOUND_DISTORTED = ['dlc_ishar_mla/sounds/menu_distorted1.wav',
                        'dlc_ishar_mla/sounds/menu_distorted2.wav']
BOSS_SOUND = "dlc_ishar_mla/sounds/boss.wav"

WIN_SOUND = "sound/win.mp3"
LOSE_SOUND = "sound/lose.mp3"

PLAYER_SPEED = 480  # 像素/秒
BULLET_SPEED = 300
PLAYER_BULLET_SPEED = 500

BOSS_KILLED = False

# 读取难度设置（即多少分对应什么样的敌人）
with open("difficulty.json", 'r') as f:
    DIFFICULTY = json.load(f)

# 定义分数与难度的对应关系
SCORE_DIFFICULTY = [[0, 100, 0], [100, 150, 1], [150, 200, 2],
                    [200, 300, 3], [300, 400, 4]]

# 读取过场提示
# 就算过场提示不存在也不会报错，只是没有了而已
LOADING_HINTS = []
try:
    with open("loading_hints1.txt", 'r', encoding='utf-8') as f:
        while True:
            one_hint = f.readline()
            if not one_hint:
                break
            one_hint = one_hint.replace(r"\\n", '\n')
            if not one_hint.startswith("#"):
                LOADING_HINTS.append(one_hint.strip('\n'))
except (UnicodeError, FileNotFoundError):
    pass

DEFAULT_HINTS = {
    "first_time": True,
    "skill1": True,
    "skill2": True,
    "heal": True,
    "shield": True,
    "benefit": True,
    "roll": True
}
# 读取教程完成状态。不存在教程状态文件的话，假设全部教程都未完成
try:
    with open("hints.json", 'r') as f:
        HINTS_STATUS = json.load(f)
except (UnicodeError, FileNotFoundError, json.JSONDecodeError):
    HINTS_STATUS = DEFAULT_HINTS

# 检查教程字典中是否有所需的键，没有就判断该文件已经损坏，重置教程状态
for one_key in DEFAULT_HINTS.keys():
    HINTS_STATUS.setdefault(one_key, True)

# 读取是否播放开火声音
try:
    with open("setting.txt", 'r') as f:
        PLAY_FIRE_SOUND = bool(int(f.readline().strip()))
except (FileNotFoundError, UnicodeError, ValueError):
    PLAY_FIRE_SOUND = True


def get_difficulty(score: int):
    """
    获取当前的得分对应什么难度
    :param score: 得分
    :return: 对应的难度，一个0～4的数字
    """
    for i in SCORE_DIFFICULTY:
        if i[0] <= score < i[1]:
            return i[2]
    return 4


def get_rect(obj):
    """
    获取一个有left, right, top, bottom对象的矩形
    :param obj: 需要获取矩形的对象
    :return: Rect对象
    """
    return Rect(left=obj.left, right=obj.right, top=obj.top, bottom=obj.bottom)


class BackgroundMusicPlayer:
    """
    背景音乐播放器，用于播放背景音乐
    """
    instance = []

    def __new__(cls):
        if not cls.instance:
            self = super().__new__(cls)
            self.music_player = None
            self.sound = None
            cls.instance.append(self)
        return cls.instance[0]

    def play_bgm(self, source: Union[list, str, arcade.Sound], volume=1.0):
        """
        播放背景音乐
        :param volume: 播放音量，默认为1
        :param source: 音乐文件
        """
        if isinstance(source, list):
            source = random.choice(source)
        if isinstance(source, str):
            source = arcade.Sound(source, streaming=True)
        if self.sound is not None:
            if self.sound.file_name == source.file_name and self.sound.is_playing(self.music_player):
                return
            self.music_player.pause()
            self.sound.stop(self.music_player)
        self.sound = source
        self.music_player = source.play(volume=volume, loop=True)
        self.music_player.seek(0)

    def stop(self):
        self.sound.stop(self.music_player)

    def play_if_not_started(self, sources, volume: float = 1) -> None:
        """
        如果sources中的音乐没有被播放，则播放sources[index]对应的音乐
        :param volume: 声音大小，0～1间的值
        :param sources: 检查是否在播放的音乐的列表
        :return: None
        """
        if not isinstance(sources, list) and not isinstance(sources, tuple):
            sources = [sources]
        for i, one in enumerate(sources):
            if isinstance(one, str):
                sources[i] = arcade.Sound(one, streaming=True)
        if self.sound is None:
            self.play_bgm(sources, volume=volume)
        elif self.sound.file_name not in [name.file_name for name in sources]:
            self.play_bgm(sources, volume=volume)


class TextureSprite(arcade.Sprite):
    def __init__(self, textures, cur_texture=0, change_time=0.1, enabled=False):
        super().__init__(texture=textures[cur_texture], center_x=540, center_y=375, scale=0.5)
        self.textures = textures
        self.cur_texture = cur_texture
        self.change_time = self.total_change_time = change_time
        self.enabled = enabled

    def on_update(self, delta_time: float = 1 / 60):
        self.change_time -= delta_time
        if self.change_time < 0 and self.enabled:
            self.cur_texture += 1
            self.cur_texture = self.cur_texture % len(self.textures)
            self.texture = self.textures[self.cur_texture]
            self.change_time = self.total_change_time

    def change_animation(self, new_textures):
        """
        更换动画图片组。请注意，这会重置动画。尽量保留被换掉的Texture的引用，你不会想再加载它们一遍的。
        :param new_textures:
        :return:
        """
        self.textures = new_textures
        self.cur_texture = 0
        self.texture = self.textures[self.cur_texture]


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


class BackgroundObjects(arcade.Sprite):
    """
    背景中会出现的一些飞行的小东西，比如星星，流星之类的
    """

    def __init__(self, image, scale=1):
        """
        创建一个飞行的小物体
        :param image: 物体的图片
        :param scale: 物体的缩放大小
        """
        super().__init__(image, scale)
        # 背景物体初始y轴坐标在最上方，x轴坐标随机
        self.center_y = SCREEN_HEIGHT
        self.center_x = random.randint(0, SCREEN_WIDTH)

    def on_update(self, delta_time=None):
        self.center_y -= BACKGROUND_SPEED * delta_time
        if self.top < 0:
            self.remove_from_sprite_lists()


class TextureButton(arcade.gui.UITextureButton):
    """
    一个可以定时切换图片的按钮，基于arcade里面的TextureButton
    """

    def __init__(self, textures, cur_index=0, update_time=0.25, enable=False, *args, **kwargs):
        """
        创建一个可以定时切换图片的按钮
        :param textures: 使用的材质（图片）列表
        :param cur_index: 初始材质是什么
        :param update_time: 切换材质的时间间隔
        :param enable: 是否启用切换。也可以修改enabled属性来启用或禁用
        :param args: 其他传递给arcade.gui.TextureButton的参数
        :param kwargs: 其他传递给arcade.gui.TextureButton的参数
        """
        super().__init__(texture=textures[cur_index], *args, **kwargs)
        self.many_textures = textures
        self.current_indexing = cur_index
        self.initial_index = cur_index
        self.total_update_time = self.update_time = update_time
        self._enabled = enable

    def on_update(self, dt):
        if self.enabled:
            self.update_time -= dt
            if self.update_time <= 0:
                self.update_time = self.total_update_time
                self.current_indexing += 1
                self.current_indexing %= len(self.many_textures)
                self.texture = self.many_textures[self.current_indexing]

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, new):
        self._enabled = new


class HealthBar:
    """
    显示玩家血量的血条，游戏中左侧的那五个心心
    """

    def __init__(self, health_images, game_scene):
        """
        创建一个血条对象。注意，创建完后需要手动把box属性加入UIManager中
        :param health_images: 血条图标。第一个是空心，第二个是实心
        :param game_scene: 游戏场景
        """
        self.health_images = health_images
        game_scene: GameView
        self.game_scene = game_scene
        # 使用一堆图片按钮来显示血量图片
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
        """
        创建一个增益，增益具有持续时间的限制，存在时间快到时会闪烁，  超过时间后会自动消失
        :param image: 增益图片
        :param scale: 增益的缩放大小
        :param center: 增益中心的位置
        :param time: 增益在屏幕上持续的时间
        """
        super().__init__(image, scale)
        if center is not None:
            self.center_x = center[0]
            self.center_y = center[1]
        # 添加一个和背景颜色一样的图片，通过图片切换实现“一闪一闪”的效果
        self.append_texture(arcade.make_soft_circle_texture(30, (42, 45, 50)))

        self.time = time
        self.total_change_time = self.change_time = 0.33

    def on_update(self, delta_time: float = 1 / 60):
        self.time -= delta_time
        self.change_time -= delta_time
        if self.time <= 0:
            self.kill()

    def update_animation(self, delta_time: float = 1 / 60):
        # 在存在时间小于3秒，且闪烁cd到之后开始闪烁
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
    """
    治疗增益，可以为玩家治疗3点血量
    """

    def on_touched(self, player):
        player: Player
        player.health += 3
        self.kill()


class Shield(Benefit):
    """
    无敌增益，为玩家提供3秒无敌时间
    """

    def on_touched(self, player):
        player: Player
        player.invincible += 3
        player.no_hurt = True
        self.kill()


class UnlimitedBullet(Benefit):
    """
    技能增益，可以使玩家一技能“过载模式”完成充能
    """

    def on_touched(self, player):
        player: Player
        player.skills[0] = True
        self.kill()


class ChaseFire(Benefit):
    """
        技能增益，可以使玩家二技能“追踪弹”完成充能
    """

    def on_touched(self, player):
        player: Player
        player.skills[1] = True
        self.kill()


# 存储所有增益的字典，方便随机抽取增益。格式为：类对象：该增益的图标
BENEFITS = {Healer: HEAL, Shield: SHIELD, UnlimitedBullet: UNLIMITED_BULLET[1], ChaseFire: CHASE_FIRE[1]}


class LivingSprite(arcade.Sprite):
    """
    所有会拥有“生命”，会被有“攻击”的物体打死的物体的父类
    """

    def __init__(self, image=None, scale=1, health=None, invincible=None, total_health=None, *args, **kwargs):
        """
        创建一个有生命的精灵。
        由于游戏的伤害机制影响，一个东西的无敌时间内，假如其受到更高的伤害，则会转而受更高的伤害。
        因此，存在一个属性no_hurt，可以使得一个东西在无敌时间内彻底不受伤害。
        no_hurt = True时无敌时间内：不受任何伤害
        no_hurt = False时无敌时间内：可能会受到更高的伤害。
        因为一般情况下，我们需要无敌时的伤害替换机制，因此no_hurt默认为False，且只能手动设为True,无敌时间结束后还原为False
        :param image: 图片
        :param scale: 精灵的缩放
        :param health: 目前的血量
        :param invincible: 受攻击后的无敌时间长度
        :param total_health: 总血量，影响被治疗时的治疗量（治疗无法使血量超过上限）
        :param args: 其他给arcade.Sprite的参数
        :param kwargs: 其他给arcade.Sprite的参数
        """
        super().__init__(image, scale, *args, **kwargs)
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
        self.no_hurt = False
        self._max_damage = 0

    def on_update(self, delta_time: float = 1 / 60):
        if self.invincible > 0:
            self.invincible -= delta_time
        if self.invincible <= 0:
            self._max_damage = 0
            self.no_hurt = False

    def on_damaged(self, bullet):
        if self.invincible <= 0:
            try:
                bullet_damage = bullet.damage
            except AttributeError:
                print("Warning: 出现未规定伤害的子弹，假设其伤害为1")
                bullet_damage = 1
            self.health -= bullet_damage
            self._max_damage = bullet_damage
            if bullet_damage > 0:
                self.invincible += self.total_invincible
            if self.health <= 0:
                self.kill()
        if hasattr(bullet, 'damage') and self.invincible > 0 and not self.no_hurt:
            if bullet.damage > self._max_damage:
                self.health -= bullet.damage
                self.health += self._max_damage
                self._max_damage = bullet.damage

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, new_health):
        # 控制血量不超过上限
        new_health = new_health if new_health < self.total_health else self.total_health
        new_health = 0 if new_health < 0 else new_health
        self.on_health_change(new_health - self.health)
        self._health = new_health

    def on_health_change(self, delta_health):
        """
        该函数会在对象生命值变化时被调用
        请通过重写该函数实现受伤害时的表现
        :return:
        """
        pass


class Boss(LivingSprite):
    def __init__(self, textures: Union[arcade.Texture, tuple[arcade.Texture]], game_scene, scale=1, health=1000, invincible=0.1, total_health=1000,
                 cur_texture=0, change_time=0.1, *args, **kwargs):
        self.large = False
        self._call_back = None
        if not hasattr(textures, '__getitem__'):
            textures = [textures]
            cur_texture = 0
        super().__init__(texture=textures[cur_texture], scale=scale, health=health, invincible=invincible,
                         total_health=total_health,
                         *args, **kwargs)
        self._towards = 1
        self.facing = 0  # 0: 右， 1: 左
        self.game_view: GameView = game_scene
        # 决定Boss撞到玩家时会造成多少伤害
        self.damage = 1

        self.cur_texture = cur_texture
        self.change_time = self.total_change_time = change_time

        self.boss_move_textures = BOSS_MOVE
        self.boss_skill_textures = BOSS_SKILL
        self.boss_attack_textures = BOSS_ATTACK
        self.boss_die_textures = BOSS_DIE

        self.walking = True
        self.textures = self.boss_move_textures[0]
        self.enabled = True
        self._stored_textures = None
        self.playing_animation = False
        self.center_y = SCREEN_HEIGHT * 0.82
        self.tears = [True, True, True]

        self._energy = 0
        self.energy_cd = 1
        self.total_energy_cd = 1

        # Boss技能初始cd
        self.skill_cd = [6, 10, 10, 5]
        # Boss技能除了第一次外，之后每一次释放的cd
        self.total_skill_cd = [16, 10, 15, 40]
        # 技能公用cd，防止出现Boss一堆技能一起放的情况出现
        self.main_cd = 0
        self.main_cd_total = 6
        # Boss巡航（左右移动）的边界
        # 在召唤出小飞机之后，Boss巡航边界会变小一点点
        self.right_range = SCREEN_WIDTH
        self.left_range = 0
        # Boss所有的技能，释放时会用random.choice()随机选择一个
        self.skills = [self.shot, self.throw_ball, self.heal, self.tear]

        # 用于计算Boss技能效果并控制技能结束的变量
        self._skill1_count = None
        self._skill2_count = None
        self._skill3_count = None

    @property
    def towards(self):
        return self._towards

    @towards.setter
    def towards(self, new):
        self._towards = new
        self.facing = 0 if self._towards == 1 else 1
        if self._towards == 1:
            self.change_animation(self.boss_move_textures[0])
        else:
            self.change_animation(self.boss_move_textures[1])

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, new):
        self._energy = new if new <= 125 else 125

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
        if hasattr(bullet, 'damage') and self.invincible > 0 and not self.no_hurt:
            if bullet.damage > self._max_damage:
                self.health -= bullet.damage
                self.health += self._max_damage
                self._max_damage = bullet.damage

    def change_animation(self, new_textures):
        """
        更换动画图片组。请注意，这会重置动画。尽量保留被换掉的Texture的引用，你不会想再加载它们一遍的。
        :param new_textures:
        :return:
        """
        self.textures = new_textures
        self.cur_texture = 0
        self.texture = self.textures[self.cur_texture]

    def play_animation(self, new_textures, default=None, callback=None):
        """
        播放一组动画，并在动画之后回到默认的动画组。
        :param callback: 动画播放完后调用的回调函数
        :param new_textures: 新的动画组的材质
        :param default: 默认动画组，None：调用之前的动画组
        :return:
        """
        self.playing_animation = True
        self._stored_textures = default if default is not None else self.textures
        self.change_animation(new_textures)
        self._call_back = callback

    def play_animation_and_stop(self, new_textures, callback=None):
        self.playing_animation = True
        self._stored_textures = None
        self.change_animation(new_textures)
        self._call_back = callback

    def on_update(self, delta_time: float = 1 / 60):
        super().on_update(delta_time)
        # 移动Boss
        if self.walking:
            self.center_x += 100 * delta_time * self.towards
            if self.center_x + self.width / 2 > self.right_range + 100:
                self.center_x = self.right_range - self.width / 2 + 100
                self.towards = -self.towards
            if self.center_x < self.left_range + self.width / 2 - 100:
                self.center_x = self.left_range + self.width / 2 - 100
                self.towards = -self.towards

        # 减小技能cd
        for one in range(len(self.skill_cd)):
            self.skill_cd[one] -= delta_time
        self.main_cd -= delta_time
        self.energy_cd -= delta_time
        if self.energy_cd <= 0:
            self.energy_cd = self.total_energy_cd
            self.energy += 1

        # 尝试释放技能
        self.skill()

    def update_animation(self, delta_time: float = 1 / 60):
        self.change_time -= delta_time
        if self.change_time < 0 and self.enabled:
            self.cur_texture += 1
            if self.cur_texture >= len(self.textures):
                if self.playing_animation:
                    if self._stored_textures is not None:
                        self.change_animation(self._stored_textures)
                        if self._call_back is not None:
                            if isinstance(self._call_back, list):
                                for one in self._call_back:
                                    one()
                            else:
                                self._call_back()
                            self._call_back = None
                        self.playing_animation = False
                        self._stored_textures = None
                    else:
                        self.enabled = False
                        self.texture = self.textures[-1]
                        if self._call_back is not None:
                            if isinstance(self._call_back, list):
                                for one in self._call_back:
                                    one()
                            else:
                                self._call_back()
                            self._call_back = None
                        self.playing_animation = False
                        return
            self.cur_texture = self.cur_texture % len(self.textures)
            self.texture = self.textures[self.cur_texture]
            self.change_time = self.total_change_time

    def skill(self):
        skill_available = [self.skills[i] for i in range(len(self.skills)) if self.skill_cd[i] <= 0]
        if self.energy == 125 and self.health > 0:
            self.energy = 0
            self.walking = False
            self.large = True
            self.play_animation(self.boss_attack_textures[self.facing],
                                callback=[lambda: setattr(self, "walking", True),
                                          lambda: self.many_bullets(),
                                          lambda: setattr(self, "large", False)])
        # 满足两个条件：技能cd为0，主cd为0时每帧有10%概率释放
        if random.random() < 0.1 and len(skill_available) > 0 >= self.main_cd and not self.large:
            self.main_cd = self.main_cd_total
            skill = random.choice(skill_available)
            index = self.skills.index(skill)
            self.skill_cd[index] = self.total_skill_cd[index]
            self.walking = False
            if index <= 1 or index == 3 and not self.large:
                self.play_animation(self.boss_attack_textures[self.facing],
                                    callback=lambda: setattr(self, "walking", True))
                skill()
            elif index == 2 and not self.large:
                self.play_animation(self.boss_skill_textures[self.facing],
                                    callback=[lambda: setattr(self, "walking", True),
                                              lambda: skill()])

    def drop_benefit(self):
        """
        随机掉落一种补给，位置在屏幕中心的（300， 250）区域内
        :return:
        """
        benefit = random.choice(list(BENEFITS.keys()))
        b = benefit(BENEFITS[benefit], center=(random.randint(int(SCREEN_WIDTH / 2 - 150), int(SCREEN_WIDTH / 2 + 150)),
                                               random.randint(int(SCREEN_HEIGHT / 2 - 150),
                                                              int(SCREEN_HEIGHT / 2 + 100))),
                    scale=2)
        self.game_view.game_scene.add_sprite("Benefit", b)

    def on_health_change(self, delta_health):
        benefit = False
        tear = False
        for one in range(self.health, self.health + abs(delta_health)):
            if one % 50 == 0:
                benefit = True
            if one == self.total_health / 4 and self.tears[0]:
                self.tears[0] = False
                tear = True
            if one == self.total_health / 2 and self.tears[1]:
                self.tears[1] = False
                tear = True
            if one == self.total_health * 3 / 4 and self.tears[2]:
                self.tears[2] = False
                tear = True
        # 伊莎玛拉给自己回血不掉补给品
        if delta_health > 0:
            benefit = False
        # 每被打掉50点血量就掉一个补给
        # 没想到吧，你的补给是Boss掉的（
        if benefit:
            self.drop_benefit()
        if tear:
            self.tear()

    def shot(self):
        """
        一技能：Boss持续发射5发子弹，间隔1秒，弱追踪我方。
        :return:
        """
        self.game_view.clock_not_paused.schedule_interval_soft(self._shot, 1)
        self._skill1_count = 0

    def _shot(self, _=None):
        bullet = Bullet((self.center_x, self.bottom), BOSS_ATTACK_1, chase=SIMPLE, speed=300,
                        player=self.game_view.player, scale=0.75)
        self.game_view.game_scene.add_sprite("EnemyBullet", bullet)
        self._skill1_count += 1
        if self._skill1_count >= 5:
            self.game_view.clock_not_paused.unschedule(self._shot)

    def throw_ball(self):
        """
        二技能：2.5秒内，Boss每隔0.5秒发射一发追踪弹，一共发射5发，弱追踪1.5秒，在其尽头停住，持续对碰撞的玩家造成伤害
        :return:
        """
        self._skill2_count = 0
        self.game_view.clock_not_paused.schedule_interval_soft(self._throw_ball, 2)

    def _throw_ball(self, _=None):
        self._skill2_count += 1
        bullet = ThrowBall(BOSS_THROW_BALL,
                           player_position=(self.game_view.player.center_x, self.game_view.player.center_y),
                           center=(self.center_x, self.bottom))
        self.game_view.game_scene.add_sprite("Enemy", bullet)
        if self._skill2_count >= 3:
            self.game_view.clock_not_paused.unschedule(self._throw_ball)

    def heal(self):
        """
        三技能：Boss为自己，场上的单位和自己回血
        :return:
        """
        self.health += 25
        self.game_view.player.health += 5
        for one_enemy in self.game_view.game_scene['Enemy']:
            if isinstance(one_enemy, ThrowBall):
                one_enemy.living_time += 3
            else:
                one_enemy.health += 3

    def tear(self):
        tear = Tear(image=BOSS_TEARS, center=(random.randint(int(SCREEN_WIDTH / 2 - 100), int(SCREEN_WIDTH / 2 + 100)),
                                              random.randint(int(SCREEN_HEIGHT / 2 - 30), int(SCREEN_HEIGHT / 2 + 30))),
                    boss=self)
        self.game_view.game_scene.add_sprite("Enemy", tear)

    def many_bullets(self):
        """
        三技能：无尽火力，Boss持续发射子弹，每0.1秒发射三发，持续1秒，一共发射30发
        子弹在发射时锁定玩家位置，并持续沿着该方向移动
        :return:
        """
        self._skill3_count = 0
        self.game_view.clock_not_paused.schedule_interval_soft(self._many_bullets, 0.1)

    def _many_bullets(self, _=None):
        self._skill3_count += 1
        bullet1 = Bullet((self.center_x, self.bottom), BOSS_ATTACK_1, chase=SIMPLE, speed=350,
                         player=self.game_view.player)
        bullet2 = Bullet((self.center_x - 30, self.bottom), BOSS_ATTACK_1, chase=SIMPLE, speed=350,
                         player=self.game_view.player)
        bullet3 = Bullet((self.center_x + 30, self.bottom), BOSS_ATTACK_1, chase=SIMPLE, speed=350,
                         player=self.game_view.player)
        self.game_view.game_scene.add_sprite("EnemyBullet", bullet1)
        self.game_view.game_scene.add_sprite("EnemyBullet", bullet2)
        self.game_view.game_scene.add_sprite("EnemyBullet", bullet3)
        # 在该技能期间无法释放其他技能
        self.main_cd = self.main_cd_total

        if self._skill3_count >= 50:
            self.game_view.clock_not_paused.unschedule(self._many_bullets)


class Enemy(LivingSprite):
    def __init__(self, image, game_view, scale: int = 1, speed: float = 180, fire: bool = False,
                 fire_cd: float = 1, chase: str = NO, center_x=None, center_y=None, health=None, damage=None,
                 invincible=0.5, benefit_chance=0.15,
                 *args, **kwargs):
        """
        创建一架敌机。一般的飞机会在顶部产生，竖直向下飞行
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
        :param benefit_chance: 飞机死亡后掉落补给的概率，一个小数，默认为0.15（15%）
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
            self.center_x = random.randint(50, SCREEN_WIDTH - 50)
        else:
            self.center_x = center_x

        if self.chase != NO and self.game_view is None:
            raise ValueError("敌机子弹追踪必须要获取我方位置")

        self.bullets = []
        self.total_health = self.health = health if health is not None else 1
        self.damage = damage if damage is not None else 1
        self.benefit_chance = benefit_chance

    def on_update(self, delta_time: float = 1 / 60):
        super().on_update(delta_time)
        self.center_y += self.change_y * delta_time
        self.fire_cd -= delta_time
        self.fire()
        # 因为飞机初始会在屏幕上面一点，所以不检测飞上去的情况
        if self.top < 0 or self.left < 0 or self.right > SCREEN_WIDTH:
            self.kill()

    def kill(self):
        """
        飞机被打败时执行的操作：清除自己发射过的子弹；有一定概率掉落补给
        :return:
        """
        for one_bullet in self.bullets:
            one_bullet.kill()
        if random.random() < self.benefit_chance:
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
    """
    Boss召唤出的小飞机，因为其不会移动，会自己消失所以重写了Enemy
    """

    def __init__(self, image, scale=1, life_time=15, *args, **kwargs):
        super().__init__(image=image, scale=scale, *args, **kwargs)
        self.life = life_time
        # 把速度设为0，就不会移动了
        self.change_y = 0

    def on_update(self, delta_time: float = 1 / 60):
        super().on_update(delta_time)
        self.life -= delta_time
        if self.life <= 0:
            self.kill()

    def kill(self):
        # 检查自己是否是被击败而不是自然消失
        if self.life > 0:
            benefit = random.choice(list(BENEFITS.keys()))
            self.game_view.game_scene.add_sprite("Benefit",
                                                 benefit(image=BENEFITS[benefit], scale=2,
                                                         center=(self.center_x, self.center_y)))
        super().kill()


class Bullet(arcade.Sprite):
    def __init__(self, center, image=None, chase=NO, player=None, damage=1, chase_time=1.0, speed=BULLET_SPEED,
                 **kwargs):
        """
        创建一颗子弹
        :param center: 子弹的中心位置
        :param image: 子弹的图片，可以不指定，默认为随机的子弹图片
        :param chase: 子弹是否追踪
        :param player: 玩家位置，用在追踪时计算
        :param damage: 该子弹命中时造成的伤害
        :param chase_time: 子弹追踪的时间长度，在chase=HARD时才有用
        :param speed: 子弹的速度
        """
        if image is None:
            super().__init__(random.choice(BULLET), **kwargs)
        else:
            super().__init__(image, **kwargs)
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
        if self.left > SCREEN_WIDTH or self.right < 0 or self.bottom > SCREEN_HEIGHT or self.top < 0:
            self.kill()

        self.center_y += self.change_y * delta_time
        self.center_x += self.change_x * delta_time


class ThrowBall(arcade.Sprite):
    def __init__(self, image, player_position, center, scale=1, damage=1, speed=300, living_time=10, **kwargs):
        super().__init__(image, scale, **kwargs)
        self.invincible = 0
        self.damage = damage
        self.speed = speed
        self.health = 999
        self.player_position = player_position
        self.living_time = living_time
        self.center_x = center[0]
        self.center_y = center[1]
        x_diff = player_position[0] - self.center_x
        y_diff = player_position[1] - self.center_y
        angle = math.atan2(y_diff, x_diff)
        self.angle = math.degrees(angle) - 90
        self.change_y = math.sin(angle) * speed
        self.change_x = math.cos(angle) * speed

    def on_update(self, delta_time: float = 1 / 60):
        self.center_y += self.change_y * delta_time
        self.center_x += self.change_x * delta_time
        if self.invincible > 0:
            self.invincible -= delta_time

        if abs(self.center_x - self.player_position[0] + self.center_y - self.player_position[1]) <= 5:
            self.change_y = self.change_x = 0

        if self.center_y < 0 or self.center_y > SCREEN_HEIGHT or self.center_x < 0 or self.center_x > SCREEN_WIDTH:
            self.change_y = self.change_x = 0

        if self.change_x == self.change_y == 0:
            self.living_time -= delta_time

        if self.living_time < 0:
            self.kill()

    def on_damaged(self, player):
        if self.invincible <= 0:
            self.living_time -= 2 * player.damage
            self.invincible += 0.1


class Tear(arcade.Sprite):
    def __init__(self, image, center, boss, scale=1, damage=1, speed=300, living_time=10, **kwargs):
        super().__init__(image, scale, **kwargs)
        self.invincible = 0
        self.damage = damage
        self.speed = speed
        self.health = 999
        self.living_time = living_time
        self.center_x = center[0]
        self.center_y = center[1]
        self.boss: Boss = boss
        self.energy_cd = 1.5
        self.total_energy_cd = 3

    def on_update(self, delta_time: float = 1 / 60):
        self.living_time -= delta_time
        if self.living_time <= 0:
            self.kill()
        self.energy_cd -= delta_time
        if self.energy_cd <= 0 and self.damage != 0:
            self.energy_cd = self.total_energy_cd
            self.boss.energy += 25
            self.texture = arcade.load_texture(BOSS_TEARS_ENERGY)
            self.boss.game_view.clock_not_paused.schedule_once(lambda event: setattr(self, "texture", arcade.load_texture(BOSS_TEARS)), 0.5)

    def on_damaged(self, player=None):
        if isinstance(player, Player):
            self.damage = 0

    @property
    def touched(self):
        return self.damage == 0

    def update_animation(self, delta_time: float = 1 / 60):
        if self.touched:
            self.texture = arcade.load_texture(BOSS_TEARS_TOUCHED)


class PlayerBullet(arcade.Sprite):
    def __init__(self, images, go_through=False):
        super().__init__(images)
        self.through = go_through
        self.damage = 1

    def on_update(self, delta_time: float = 1 / 60):
        self.center_y += delta_time * PLAYER_BULLET_SPEED
        if self.top > SCREEN_HEIGHT:
            self.kill()


class Player(LivingSprite):
    """
    玩家的飞机
    """

    def __init__(self, game_view, image=None, scale=1.0, fire_cd=0.25):
        super().__init__(image, scale, health=5, total_health=5, invincible=0.5)
        self.bullet_through = False
        self.fire_cd = self.total_fire_cd = fire_cd
        self.game_view: GameView = game_view
        self.append_texture(arcade.load_texture(PLAYER_HURT))
        self.append_texture(arcade.load_texture(PLAYER_HEAL))

        # 飞机背后那个尾焰，只在飞机移动时出现
        self.fire_sprite = arcade.Sprite(PLAYER_FIRE, 0.5)
        self.fire_sprite.center_x = self.center_x
        self.fire_sprite.center_y = self.center_y
        self.game_view.game_scene.add_sprite("Player", self.fire_sprite)

        self._health = 5
        self.damage = 1

        self.invincible_effect = arcade.Sprite()
        self.invincible_effect.append_texture(
            arcade.texture.make_soft_circle_texture(100, (95, 185, 240), outer_alpha=100))
        self.invincible_effect.append_texture(arcade.texture.make_soft_circle_texture(100, (95, 185, 240)))
        self.invincible_effect.visible = False
        self.game_view.game_scene.add_sprite("Player", self.invincible_effect)

        # 存储玩家的技能是否可以使用
        self.skills = {0: False, 1: False}

        # 玩家技能所需要的记录变量
        self._enemy = []
        self._enemy_killed = 0
        self.skill1_time = 0
        self.skill2_break = 0

    def on_update(self, delta_time=None):
        super().on_update(delta_time)
        self.center_y += self.change_y * delta_time
        self.center_x += self.change_x * delta_time
        self.fire_cd -= delta_time

        if self.change_y == self.change_x == 0:
            self.fire_sprite.visible = False
        else:
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
        # 只剩一点血时，在红蓝色间闪烁
        if self.health == 1:
            self.cur_texture_index += 1
            self.cur_texture_index = self.cur_texture_index % 2
            self.set_texture(self.cur_texture_index)
        # 无敌时间剩余较长的无敌特效
        if self.invincible > 1:
            self.invincible_effect.set_texture(0)
            self.invincible_effect.visible = True
            self.invincible_effect.center_x = self.center_x
            self.invincible_effect.center_y = self.center_y
        # 无敌时间剩余1秒内的无敌特效，更淡了一些
        elif 1 >= self.invincible > 0:
            self.invincible_effect.set_texture(1)
            self.invincible_effect.visible = True
            self.invincible_effect.center_x = self.center_x
            self.invincible_effect.center_y = self.center_y
        else:
            self.invincible_effect.visible = False

    def fire(self):
        if self.fire_cd <= 0 < self.health:
            self.fire_cd = self.total_fire_cd
            player_bullet = PlayerBullet(PLAYER_BULLET, self.bullet_through)
            player_bullet.center_x = self.center_x
            player_bullet.center_y = self.top
            self.game_view.game_scene.add_sprite("PlayerBullet", player_bullet)
            if PLAY_FIRE_SOUND:
                self.game_view.fire_sound.play(volume=0.3)

    def kill(self):
        super().kill()
        self.fire_sprite.kill()
        self.invincible_effect.kill()

    def on_health_change(self, delta_health):
        # 被伤害或治疗后的0.5秒内切换自己的图片
        if delta_health < 0:
            self.set_texture(1)
        elif delta_health > 0:
            self.set_texture(2)
        self.game_view.clock_not_paused.schedule_once(lambda event: self.set_texture(0), 0.5)

    def unlimited_bullets(self, duration=5):
        """
        技能1:技能期间发弹间隔大幅度缩短，且子弹可以穿透敌方
        :param duration: 持续时间
        :return: 无
        """
        if self.skills[0] and not self.bullet_through:
            self.skills[0] = False
            self.total_fire_cd = 0.05
            self.bullet_through = True
            if not self.game_view.boss_fight:
                self.game_view.clock_not_paused.schedule_once(lambda event: setattr(self, "total_fire_cd", 0.25),
                                                              duration)
                self.game_view.clock_not_paused.schedule_once(lambda event: setattr(self, "bullet_through", False),
                                                              duration)
            else:
                self.game_view.clock_not_paused.schedule_once(lambda event: setattr(self, "total_fire_cd", 0.25),
                                                              duration * 2)
                self.game_view.clock_not_paused.schedule_once(lambda event: setattr(self, "bullet_through", False),
                                                              duration * 2)

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
                self.game_view.clock_not_paused.schedule_interval_soft(self._chase_bullets, 0.2)
            else:
                self.game_view.clock_not_paused.schedule_interval_soft(self._chase_bullets_boss, 0.2)

    def _chase_bullets_boss(self, _):
        self._enemy_killed += 1
        bullet = Bullet((self.center_x, self.center_y), CHASE_FIRE[1], chase=HARD, player=self.game_view.boss,
                        damage=15,
                        chase_time=9999999, speed=600)
        self.game_view.game_scene.add_sprite("PlayerBullet", bullet)
        if self._enemy_killed > 4:
            self.game_view.clock_not_paused.unschedule(self._chase_bullets_boss)

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

        if self._enemy_killed >= 10 or self.game_view.boss_fight:
            self._enemy.clear()
            self.game_view.clock_not_paused.unschedule(self._chase_bullets)

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
        self.sound_player = BackgroundMusicPlayer()
        self.menu_ui_manager = arcade.gui.UIManager()
        self.menu_v_box = arcade.gui.UIBoxLayout()
        main_text = arcade.gui.UITextArea(text="Plane War", height=70, width=390,
                                          font_name="Kenney Future", font_size=40)
        self.menu_v_box.add(main_text.with_space_around(bottom=50))
        start_button = arcade.gui.UIFlatButton(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, text="Start",
                                               width=200,
                                               style={"font_name": "Kenney Future", "font_size": 20,
                                                      "bg_color": BACKGROUND_COLOR})
        start_button.on_click = lambda event: self.window.show_view(GameView())
        self.menu_v_box.add(start_button.with_space_around(bottom=20))
        setting_button = arcade.gui.UIFlatButton(text="Setting",
                                                 width=200,
                                                 style={"font_name": "Kenney Future", "font_size": 20,
                                                        "bg_color": BACKGROUND_COLOR})
        setting_button.on_click = lambda event: self.window.show_view(SettingView(self))
        self.menu_v_box.add(setting_button.with_space_around(bottom=20))
        quit_button = arcade.gui.UIFlatButton(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50, text="Quit",
                                              width=200,
                                              style={"font_name": "Kenney Future", "font_size": 20,
                                                     "bg_color": BACKGROUND_COLOR})
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
        if not BOSS_KILLED:
            self.sound_player.play_if_not_started(MENU_SOUND)
        else:
            self.sound_player.play_if_not_started(MENU_SOUND_DISTORTED, volume=0.7)

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
                self.hints[0] = self.hints[0] + "\n这是最后一条，继续按下回车或左键退出教程"
            elif len(self.hints) == 2:
                self.hints[0] = self.hints[0] + "\n按下回车或左键显示下一条\n按下ESC退出教程"
                self.hints[1] = self.hints[1] + "\n这是最后一条，按下Z键显示上一条\n按下回车或左键退出教程"
            elif len(self.hints) > 2:
                self.hints[0] = self.hints[0] + "\n按下回车或左键显示下一条\n按下ESC退出教程"
                self.hints[-1] = self.hints[-1] + "\n这是最后一条，按下Z键显示上一条\n按下回车或左键退出教程"
                for i in range(1, len(self.hints) - 1):
                    self.hints[i] += "\n按下回车显示下一条\n按下Z键显示上一条"
        self.hint.text = self.hints[0]
        self.hint.fit_content()
        self.cursor = 0
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
            self.on_exit()
            return
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

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.next()


class SettingView(arcade.View):
    def __init__(self, menu_view: MenuView):
        super().__init__()
        self.menu_view = menu_view
        self.ui_manager = arcade.gui.UIManager()
        self.exit_button = arcade.gui.UIFlatButton(text="Main Menu", width=200,
                                                   style={"font_name": "Kenney Future", "font_size": 20,
                                                          "bg_color": BACKGROUND_COLOR})
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
                                                           "bg_color": BACKGROUND_COLOR})
        self.reset_button.on_click = self.on_click_reset
        self.reset_area.add(self.reset_button)

        self.complete_area = arcade.gui.UIBoxLayout(vertical=False)
        self.complete_text = arcade.gui.UITextArea(text="标记所有教程为完成", font_name="华文黑体", font_size=20,
                                                   text_color=(255, 255, 255))
        self.complete_text.fit_content()
        self.complete_area.add(self.complete_text.with_space_around(right=30))
        self.complete_button = arcade.gui.UIFlatButton(text="Complete", width=200,
                                                       style={"font_name": "Kenney Future", "font_size": 20,
                                                              "bg_color": BACKGROUND_COLOR})
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
                                                           "bg_color": BACKGROUND_COLOR})
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
        self.window.show_view(self.menu_view)

    def on_click_complete(self, text=None):
        if text not in ["Ok", "Cancel"]:
            m = arcade.gui.UIMessageBox(width=300, height=150, message_text="Mark all tutorials as completed?",
                                        buttons=["Ok", "Cancel"],
                                        callback=self.on_click_complete)
            self.ui_manager.add(m)
        elif text == 'Ok':
            global HINTS_STATUS
            another = DEFAULT_HINTS.copy()
            for a_key, value in another.items():
                another[a_key] = False
            HINTS_STATUS = another

    def on_click_reset(self, text=None):
        if text not in ["Ok", "Cancel"]:
            m = arcade.gui.UIMessageBox(width=300, height=150, message_text="Mark all tutorials as not read?",
                                        buttons=["Ok", "Cancel"],
                                        callback=self.on_click_reset)
            self.ui_manager.add(m)
        elif text == 'Ok':
            global HINTS_STATUS
            HINTS_STATUS = DEFAULT_HINTS

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

    def __init__(self, boss_fight=False, boss_health=500):
        super().__init__()
        # 以下为游戏界面内容
        # 游戏中的GUI
        self.boss_dead = False
        self.sound_player = BackgroundMusicPlayer()

        self.showed = False
        self.boss_health = boss_health
        self.game_ui_manager = arcade.gui.UIManager()
        self.game_v_box = arcade.gui.UIBoxLayout()
        self.exit_button = arcade.gui.UIFlatButton(0, 0, text="Main Menu",
                                                   width=200,
                                                   style={"font_name": "Kenney Future", "font_size": 20,
                                                          "bg_color": BACKGROUND_COLOR})
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
        self.player_skill1_image = TextureButton(
            textures=[self.player_skill1_texture[0], self.player_skill1_texture[1]], width=64,
            height=64, enable=False, update_time=0.15)
        self.player_skill1_hint = TextureButton(textures=self.player_skill1_texture[2], width=50, height=50,
                                                cur_index=1)

        self.player_skill2_texture = [arcade.load_texture(CHASE_FIRE[0]),
                                      arcade.load_texture(CHASE_FIRE[1]),
                                      [arcade.load_texture(CHASE_FIRE[2][0]),
                                       arcade.load_texture(CHASE_FIRE[2][1])]]
        self.player_skill2_image = TextureButton(
            textures=[self.player_skill2_texture[0], self.player_skill2_texture[1]], width=64,
            height=64, enable=False, update_time=0.15)
        self.player_skill2_hint = TextureButton(textures=self.player_skill2_texture[2], width=50, height=50,
                                                cur_index=1)
        self.skill_selected = 0

        self.game_v_box_right.add(self.player_skill1_image.with_space_around(top=30))
        self.game_v_box_right.add(self.player_skill1_hint.with_space_around())
        self.game_v_box_right.add(self.player_skill2_image.with_space_around(top=30))
        self.game_v_box_right.add(self.player_skill2_hint.with_space_around())

        self.health_bar = HealthBar([arcade.load_texture(HEALTH_IMAGES[0]), arcade.load_texture(HEALTH_IMAGES[1])],
                                    self)
        self.boss_health_bar = arcade.gui.UITextArea(text="1000 / 1000", font_name="Kenney Future", font_size=30,
                                                     text_color=(255, 0, 0), width=500)
        self.boss_energy_bar = arcade.gui.UITextArea(text="Energy: 0 / 125", font_name="Kenney Future", font_size=25,
                                                     text_color=(0, 255, 255), width=500)

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
        self.bad_timer = BadClock()
        self.clock_not_paused = pyglet.clock.Clock(time_function=self.bad_timer)

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
            self.boss = Boss(textures=BOSS, game_scene=self, health=self.boss_health, total_health=500, invincible=0.1,
                             center_x=SCREEN_WIDTH / 2, center_y=SCREEN_HEIGHT - 180, scale=0.5)
            self.game_scene.add_sprite("Enemy", self.boss)
            self.game_ui_manager.add(arcade.gui.UIAnchorWidget(
                anchor_x='center',
                anchor_y='top',
                align_y=-30,
                align_x=50,
                child=self.boss_health_bar
            ))
            self.game_ui_manager.add(arcade.gui.UIAnchorWidget(
                anchor_x='center',
                anchor_y='top',
                align_y=-80,
                align_x=50,
                child=self.boss_energy_bar
            ))
            self.sound_player.play_bgm(BOSS_SOUND, volume=0.7)
            self.player.center_x = SCREEN_WIDTH / 2
            self.player.center_y = 0
        else:
            self.sound_player.play_bgm(BATTLE_SOUND)

        self.game_scene.get_sprite_list("Enemy").preload_textures(ALL_BOSS_TEXTURES)

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
        self.clock_not_paused.tick()
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
            self.bad_timer.update(diff)

            # 更新玩家技能提示
            if self.player.skills[0]:
                self.player_skill1_hint.enabled = True
                if self.skill_selected == 1:
                    self.player_skill1_image.enabled = True
                else:
                    self.player_skill1_image.enabled = False
                    self.player_skill1_image.texture = self.player_skill1_texture[1]
            else:
                self.player_skill1_hint.enabled = False
                self.player_skill1_hint.texture = self.player_skill1_texture[2][1]
                self.player_skill1_image.enabled = False
                self.player_skill1_image.texture = self.player_skill1_texture[0]

            if self.player.skills[1]:
                self.player_skill2_hint.enabled = True
                if self.skill_selected == 2:
                    self.player_skill2_image.enabled = True
                else:
                    self.player_skill2_image.enabled = False
                    self.player_skill2_image.texture = self.player_skill2_texture[1]
            else:
                self.player_skill2_hint.enabled = False
                self.player_skill2_hint.texture = self.player_skill2_texture[2][1]
                self.player_skill2_image.enabled = False
                self.player_skill2_image.texture = self.player_skill2_texture[0]

            # 然后，随机生成敌人
            if len(self.game_scene['Enemy']) <= 2 and random.random() < 0.1 and not self.boss_fight:
                spawn_enemy(self, [1, 3], str(get_difficulty(self.score)))

            # 检查Boss该不该生成
            if self.score > 0 and not self.boss_fight:
                self.boss_fight = True
                for one_enemy in self.game_scene["Enemy"]:
                    one_enemy.benefit_chance = 0
                    one_enemy.kill()
                self.boss = Boss(textures=BOSS, game_scene=self, health=self.boss_health, total_health=500,
                                 invincible=0.1,
                                 center_x=SCREEN_WIDTH / 2, center_y=SCREEN_HEIGHT - 180, scale=0.5)
                self.game_scene.add_sprite("Enemy", self.boss)
                self.game_ui_manager.add(arcade.gui.UIAnchorWidget(
                    anchor_x='center',
                    anchor_y='top',
                    align_y=-30,
                    align_x=50,
                    child=self.boss_health_bar
                ))
                self.game_ui_manager.add(arcade.gui.UIAnchorWidget(
                    anchor_x='center',
                    anchor_y='top',
                    align_y=-80,
                    align_x=50,
                    child=self.boss_energy_bar
                ))
                self.sound_player.play_bgm(BOSS_SOUND, volume=0.7)
                self.player.center_x = SCREEN_WIDTH / 2
                self.player.center_y = 0

            # Boss战时才更新的内容：
            if self.boss_fight:
                self.boss_health_bar.text = f"{self.boss.health} / {self.boss.total_health}"
                self.boss_energy_bar.text = f"Energy: {self.boss.energy} / 125"

            if self.game_scene['Benefit'] and HINTS_STATUS['benefit']:
                self.clock.schedule_once(self.show_benefit_hint, 0.6)

            if not HINTS_STATUS['skill1'] and not HINTS_STATUS['skill2'] and HINTS_STATUS['roll']:
                self.show_roll_hint()

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
                    if (not hasattr(one_bullet, "through") or not one_bullet.through) and not isinstance(one_enemy,
                                                                                                         Tear):
                        one_bullet.kill()
                    if one_enemy.health <= 0:
                        if not (hasattr(self, "boss") and one_enemy == self.boss):
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
                    self.player.on_damaged(one_enemy)
                    if self.player.health <= 0:
                        explode = Explosion((self.player.center_x, self.player.center_y))
                        self.game_scene.add_sprite("Explosion", explode)
                        break
                    one_enemy.on_damaged(self.player)
                    if one_enemy.health <= 0:
                        if not (hasattr(self, "boss") and one_enemy == self.boss):
                            explode = Explosion((one_enemy.center_x, one_enemy.center_y))
                            self.game_scene.add_sprite("Explosion", explode)
                            self.score += 10
                            break

            # 检查玩家是否想开火
            if self.firing:
                self.player.fire()

            if self.player.health <= 0:
                self.end_game(False)
            if self.boss_fight and self.boss.health <= 0 and not self.boss_dead:
                self.boss_dead = True
                self.player.invincible += 999
                self.player.no_hurt = True
                self.boss.invincible += 999
                self.boss.no_hurt = True
                self.boss.walking = False
                for index in range(len(self.boss.skill_cd)):
                    self.boss.skill_cd[index] += 999

                self.boss.play_animation_and_stop(BOSS_DIE[self.boss.facing], lambda: self.end_game(True))

    def end_game(self, win: bool):
        """
        结束游戏
        :param win: 游戏是否赢了，赢：True，输：False
        :return:
        """
        self.sound_player.stop()
        sound = arcade.Sound(WIN_SOUND if win else LOSE_SOUND, streaming=False)
        if win:
            global BOSS_KILLED
            BOSS_KILLED = True
        sound.play(volume=0.5)
        over_view = GameOverView(win, self)
        self.window.show_view(over_view)

    def show_first_time_hints(self):
        """展示第一次进入游戏时的提示"""
        words = ["欢迎来到游戏！\n看起来你第一次进入游戏，\n下面的教程将会帮你熟悉本游戏\n",
                 "左侧矩形圈出的是你控制的飞机的心心。\n"
                 "你的飞机一共有五颗心心\n"
                 "，受到伤害就会减少一颗。\n"
                 "失去所有心心后，游戏失败\n",
                 "通过WASD键控制飞机，按住空格或鼠标左键射击\n"
                 "成功击败游戏最后出现的Boss后，游戏胜利\n",
                 "你可以通过点击左上方圈出的按钮返回主界面\n",
                 "你可以通过点击右上角圈出的按钮或E键暂停\n",
                 "正式开始游戏前，请把输入法调整到英文状态\n"]
        right_box = get_rect(self.game_v_box_right)
        pause_button_box = Rect(right_box.left, right_box.right, right_box.top,
                                right_box.top - self.pause_button.height)
        rects = [None, get_rect(self.health_bar.box), None,
                 get_rect(self.game_v_box), pause_button_box, None]
        hint_view = HelpView(self, hints=words, rects=rects, show_keys=True,
                             callback=lambda: HINTS_STATUS.__setitem__("first_time", False))
        self.window.show_view(hint_view)

    def show_skill1_hints(self, _=None):
        words = ["你刚刚捡起的是技能补给，\n"
                 "能够使你的一技能完成充能。\n",
                 "充能完成后，右侧圈起的技能图标会亮起,\n"
                 "下方的按键也会不断闪烁, 此时按下“1”键即可激活技能\n",
                 "该技能的效果为：在五秒内玩家的攻击间隔极大程度缩短，\n"
                 "并且子弹可以穿过敌人。\n"
                 "同时，受到攻击时有50%概率不受伤害\n"]
        rects = [None, get_rect(self.player_skill1_image), None]
        hint_view = HelpView(self, hints=words, rects=rects, show_keys=True,
                             callback=lambda: HINTS_STATUS.__setitem__("skill1", False))
        self.window.show_view(hint_view)

    def show_skill2_hints(self, _=None):
        words = ["你刚刚捡起的是技能补给，\n"
                 "能够使你的二技能完成充能。\n",
                 "充能完成后，右侧圈起的技能图标会亮起，\n"
                 "下方的按键也会不断闪烁。此时按下“2”键即可激活技能\n",
                 "该技能的效果为：持续锁定场上敌机，向它们发射追踪弹，\n"
                 "技能持续直到有七名被锁定的敌人被击败\n"]
        rects = [None, get_rect(self.player_skill2_image), None]
        hint_view = HelpView(self, hints=words, rects=rects, show_keys=True,
                             callback=lambda: HINTS_STATUS.__setitem__("skill2", False))
        self.window.show_view(hint_view)

    def show_heal_hints(self, _=None):
        words = ["你刚刚捡起的是血量补给，可以为你恢复血量\n"
                 "一个血量补给可以恢复三颗心心\n"
                 "血量可以在左侧框出的区域查看\n",
                 "请注意，在心心已满时捡起血量补给不会有任何作用\n"]
        rects = [get_rect(self.health_bar.box), None]
        hint_view = HelpView(self, hints=words, rects=rects, show_keys=True,
                             callback=lambda: HINTS_STATUS.__setitem__("heal", False))
        self.window.show_view(hint_view)

    def show_shield_hints(self, _=None):
        words = ["你刚刚捡起的是无敌盾补给，可以为你提供无敌状态\n"
                 "该补给可以使你在三秒内不受任何伤害\n",
                 "无敌状态下，你的飞机周围会出现一圈淡蓝色光晕\n",
                 "该补给的效果可以叠加\n"]
        rects = [None, get_rect(self.player), None]
        hint_view = HelpView(self, hints=words, rects=rects, show_keys=True,
                             callback=lambda: HINTS_STATUS.__setitem__("shield", False))
        self.window.show_view(hint_view)

    def show_benefit_hint(self, _=None):
        words = ["场上出现了补给品，请注意被矩形圈出的物品\n",
                 "补给品会提供多种增益。尝试捡起它吧！\n"]
        # 这个函数的延时触发较长，可能出现补给品被检走导致没了的情况，得不到rect了
        # 如果这种事情真的发生了，我们就不展示教程，下次再说
        try:
            rects = [get_rect(self.game_scene['Benefit'][0]), None]
        except IndexError:
            return
        hint_view = HelpView(self, hints=words, rects=rects, show_keys=True,
                             callback=lambda: HINTS_STATUS.__setitem__("benefit", False))
        self.window.show_view(hint_view)

    def show_roll_hint(self, _=None):
        words = ["使用鼠标滚轮可以选取你的技能\n"
                 "向上滚动可以选取一技能，\n"
                 "向下滚动可以选取二技能\n",
                 "你选中的技能在充能完成后，右侧的图标会持续闪烁\n"
                 "此时按下鼠标右键即可快速释放技能\n"]
        rects = [None, get_rect(self.game_v_box_right)]
        hint_view = HelpView(self, hints=words, rects=rects, show_keys=True,
                             callback=lambda: HINTS_STATUS.__setitem__("roll", False))
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
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            if self.skill_selected == 1:
                self.player.unlimited_bullets(5)
            elif self.skill_selected == 2:
                self.player.chase_bullets()

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.firing = False

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        # 我也不知道为啥，但是windows下鼠标滚轮向上是负的，向下是正的
        # macOS下滚轮向下负的，向上正的……
        if "win32" in sys.platform:
            scroll_y = -scroll_y
        if scroll_y > 0:
            self.skill_selected = 2
        if scroll_y < 0:
            self.skill_selected = 1

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
        main_text = arcade.gui.UITextArea(text=f"You {win}", height=70, width=350,
                                          font_name="Kenney Future", font_size=40)
        self.over_ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=160 if LOADING_HINTS else 130,
            child=main_text
        ))
        score_text = arcade.gui.UITextArea(text=f"Score: {self.game_scene.score}",
                                           font_name="Kenney Future", font_size=20, width=200)
        self.over_ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=100 if LOADING_HINTS else 70,
            child=score_text
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
                                                       "bg_color": BACKGROUND_COLOR})
        replay_button.on_click = self.replay
        self.over_v_box.add(replay_button.with_space_around(bottom=20))

        main_menu_button = arcade.gui.UIFlatButton(70, SCREEN_HEIGHT - 50, text="Main Menu",
                                                   width=250,
                                                   style={"font_name": "Kenney Future", "font_size": 20,
                                                          "bg_color": BACKGROUND_COLOR})
        main_menu_button.on_click = self.main_menu
        self.over_v_box.add(main_menu_button.with_space_around(bottom=20))

        self.over_ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=-100 if LOADING_HINTS else -80,
            child=self.over_v_box
        ))

        hint_text = arcade.gui.UITextArea(font_name="华文黑体", font_size=25)
        self.over_ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="right",
            anchor_y="bottom",
            align_x=-30,
            align_y=30,
            child=hint_text
        ))
        if LOADING_HINTS:
            hint_text.text = "按回车显示下一条提示"
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
                                 boss_health=self.game_scene.boss.health)
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
    arcade.set_background_color(BACKGROUND_COLOR2)
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
