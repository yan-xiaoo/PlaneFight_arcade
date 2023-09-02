import arcade


class LivingSprite(arcade.Sprite):
    """
    所有会拥有“生命”，会被有“攻击”的物体打死的物体的父类
    """

    def __init__(self, image=None, frames=None, scale=1, health=None, invincible=None, total_health=None, enable_hurt_color=False,
                 hurt_color=arcade.color.DARK_SALMON, *args, **kwargs):
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
        :param enable_hurt_color: 是否启用受伤时变色
        :param hurt_color: 受伤时的颜色
        :param args: 其他给arcade.Sprite的参数
        :param kwargs: 其他给arcade.Sprite的参数
        """
        super().__init__(image, scale, *args, **kwargs)
        self.cur_frame_idx = 0
        self.time_counter = 0
        self.frames: [arcade.sprite.AnimationKeyframe] = frames
        if frames is not None:
            self.textures = [frame.texture for frame in frames]
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
        self.hurt_time = 0
        self.hurt_color_enabled = enable_hurt_color
        self.hurt_color = hurt_color

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
        if delta_health < 0 and self.hurt_color_enabled:
            self.hurt_time = self.total_invincible

    def update_animation(self, delta_time: float = 1 / 60):
        if self.hurt_color_enabled:
            if self.hurt_time >= 0:
                self.hurt_time -= delta_time
                self.color = self.hurt_color
            else:
                self.color = arcade.color.WHITE

        if self.frames is not None:
            self.time_counter += delta_time
            while self.time_counter > self.frames[self.cur_frame_idx].duration / 1000.0:
                self.time_counter -= self.frames[self.cur_frame_idx].duration / 1000.0
                self.cur_frame_idx += 1
                if self.cur_frame_idx >= len(self.frames):
                    self.cur_frame_idx = 0
                cur_frame = self.frames[self.cur_frame_idx]
                self.texture = cur_frame.texture
