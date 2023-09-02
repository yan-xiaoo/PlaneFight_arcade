import random
import arcade
from typing import Union


class BackgroundMusicPlayer:
    """
    背景音乐播放器，用于播放背景音乐
    """
    instance = []

    def __init__(self):
        self.sound = getattr(self, "sound", None)
        self.music_player = getattr(self, "music_player", None)

    def __new__(cls):
        if not cls.instance:
            self = super().__new__(cls)
            self.__init__()
            cls.instance.append(self)
        return cls.instance[0]

    def play_bgm(self, source: Union[tuple, list, str, arcade.Sound], volume=1.0):
        """
        播放背景音乐
        :param volume: 播放音量，默认为1
        :param source: 音乐文件
        """
        if isinstance(source, list) or isinstance(source, tuple):
            source = random.choice(source)
        if isinstance(source, str):
            source = arcade.Sound(source, streaming=True)
        if self.sound is not None:
            # 如果输入的声音已经在播放，就什么都不做
            # 否则会导致同一音乐被从头开始播放
            if self.sound.file_name == source.file_name and self.sound.is_playing(self.music_player):
                return
            else:
                # 停止目前已经有的音乐，开始新的
                self.music_player.pause()
                self.sound.stop(self.music_player)
        self.sound = source
        self.music_player = source.play(volume=volume, loop=True)

    def stop(self):
        self.sound.stop(self.music_player)

    def play_if_not_started(self, sources: Union[list, tuple, str, arcade.Sound], volume=1) -> None:
        """
        如果sources中的音乐没有被播放，则播放sources中随机一个音乐
        :param volume: 音量
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
