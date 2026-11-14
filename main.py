
"""
Jungle Escape
An original Pygame Zero platform game.
Run with: python -m pgzero main.py
"""

import math
import random
from pygame import Rect

WIDTH = 900
HEIGHT = 600
TITLE = "Jungle Escape"

GROUND_Y = 540
GRAVITY = 0.65

PLATFORMS = [
    (0, GROUND_Y, WIDTH, 60),
    (150, 440, 170, 18),
    (390, 355, 170, 18),
    (635, 445, 150, 18),
    (690, 290, 130, 18),
]

COIN_POSITIONS = [
    (205, 405),
    (455, 320),
    (700, 405),
    (755, 255),
]

game_state = "menu"
sound_enabled = True
score = 0
music_started = False


class SpriteAnimation:
    """Cycles through a sequence of image names at a fixed frame rate."""

    def __init__(self, frames, speed=0.16):
        self.frames = frames
        self.speed = speed
        self.timer = 0
        self.index = 0

    def update(self, dt):
        self.timer += dt

        if self.timer >= self.speed:
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)

    def image(self):
        return self.frames[self.index]


class Player:
    """Handles the hero's movement, jumping, animation and health."""

    def __init__(self):
        self.actor = Actor("hero_idle_0", (70, 490))
        self.velocity_y = 0
        self.speed = 4
        self.on_ground = False
        self.health = 3
        self.invulnerable = 0

        self.idle_animation = SpriteAnimation(
            ["hero_idle_0", "hero_idle_1"], 0.35
        )

        self.walk_animation = SpriteAnimation(
            [
                "hero_walk_0",
                "hero_walk_1",
                "hero_walk_2",
                "hero_walk_3",
            ],
            0.12,
        )

    def update(self, dt):
        moving = False

        if keyboard.left or keyboard.a:
            self.actor.x -= self.speed
            moving = True

        if keyboard.right or keyboard.d:
            self.actor.x += self.speed
            moving = True

        self.actor.x = max(24, min(WIDTH - 24, self.actor.x))

        old_bottom = self.actor.bottom

        self.velocity_y += GRAVITY
        self.actor.y += self.velocity_y
        self.on_ground = False

        for x, y, width, height in PLATFORMS:
            if (
                self.velocity_y >= 0
                and old_bottom <= y + 8
                and self.actor.bottom >= y
                and self.actor.right > x
                and self.actor.left < x + width
            ):
                self.actor.bottom = y
                self.velocity_y = 0
                self.on_ground = True

        if keyboard.space and self.on_ground:
            self.velocity_y = -13
            self.on_ground = False
            play_sound("jump")

        if moving:
            self.walk_animation.update(dt)
            self.actor.image = self.walk_animation.image()
        else:
            self.idle_animation.update(dt)
            self.actor.image = self.idle_animation.image()

        if self.invulnerable > 0:
            self.invulnerable -= dt

    def hurt(self):
        if self.invulnerable <= 0:
            self.health -= 1
            self.invulnerable = 1.2
            play_sound("hit")


class Enemy:
    """A ground enemy that patrols between two boundary points."""

    def __init__(self, x, y, left_edge, right_edge):
        self.actor = Actor("slime_idle_0", (x, y))
        self.left_edge = left_edge
        self.right_edge = right_edge
        self.direction = 1
        self.speed = 1.5

        self.idle = SpriteAnimation(
            ["slime_idle_0", "slime_idle_1"], 0.35
        )

        self.walk = SpriteAnimation(
            ["slime_walk_0", "slime_walk_1"], 0.18
        )

        self.pause_timer = 0

    def update(self, dt):
        if self.pause_timer > 0:
            self.pause_timer -= dt
            self.idle.update(dt)
            self.actor.image = self.idle.image()
            return

        self.actor.x += self.direction * self.speed

        if self.actor.x >= self.right_edge:
            self.actor.x = self.right_edge
            self.direction = -1
            self.pause_timer = 0.35

        elif self.actor.x <= self.left_edge:
            self.actor.x = self.left_edge
            self.direction = 1
            self.pause_timer = 0.35

        self.walk.update(dt)
        self.actor.image = self.walk.image()


class FlyingEnemy:
    """A flying enemy moving inside a bounded air lane."""

    def __init__(self, x, y, left_edge, right_edge):
        self.actor = Actor("bat_idle_0", (x, y))
        self.left_edge = left_edge
        self.right_edge = right_edge
        self.direction = -1
        self.speed = 1.8
        self.base_y = y
        self.phase = random.random() * 6
        self.pause_timer = 0

        self.idle = SpriteAnimation(
            ["bat_idle_0", "bat_idle_1"], 0.32
        )

        self.fly = SpriteAnimation(
            ["bat_fly_0", "bat_fly_1"], 0.13
        )

    def update(self, dt):
        if self.pause_timer > 0:
            self.pause_timer -= dt
            self.idle.update(dt)
            self.actor.image = self.idle.image()
            return

        self.actor.x += self.direction * self.speed

        if self.actor.x <= self.left_edge:
            self.actor.x = self.left_edge
            self.direction = 1
            self.pause_timer = 0.35

        elif self.actor.x >= self.right_edge:
            self.actor.x = self.right_edge
            self.direction = -1
            self.pause_timer = 0.35

        self.phase += dt * 3
        self.actor.y = self.base_y + math.sin(self.phase) * 12

        self.fly.update(dt)
        self.actor.image = self.fly.image()


class Coin:
    """A collectible coin with a two-frame shimmer animation."""

    def __init__(self, x, y):
        self.actor = Actor("coin_0", (x, y))
        self.animation = SpriteAnimation(
            ["coin_0", "coin_1"], 0.16
        )
        self.collected = False

    def update(self, dt):
        self.animation.update(dt)
        self.actor.image = self.animation.image()


def play_sound(name):
    if sound_enabled:
        getattr(sounds, name).play()


def start_game():
    global player, enemies, flying_enemies
    global coins, score, game_state

    player = Player()

    enemies = [
        Enemy(260, 522, 220, 370),
        Enemy(590, 522, 520, 650),
    ]

    flying_enemies = [
        FlyingEnemy(740, 365, 650, 835)
    ]

    coins = [
        Coin(x, y) for x, y in COIN_POSITIONS
    ]

    score = 0
    game_state = "playing"

    if sound_enabled:
        music.play("background")


def draw_button(label, center, width=230):
    x, y = center

    button_rect = Rect(
        x - width // 2,
        y - 24,
        width,
        48,
    )

    screen.draw.filled_rect(
        button_rect,
        (36, 93, 62),
    )

    screen.draw.rect(
        button_rect,
        (225, 242, 190),
    )

    screen.draw.text(
        label,
        center=(x, y),
        fontsize=25,
        color="white",
    )


def draw_background():
    screen.fill((123, 190, 205))

    screen.draw.filled_rect(
        Rect(0, 390, WIDTH, 210),
        (63, 132, 76),
    )

    # Distant hills and decorative jungle foliage.
    for x in range(-30, WIDTH + 60, 150):
        screen.draw.filled_circle(
            (x, 385), 90, (83, 158, 91)
        )

        screen.draw.filled_circle(
            (x + 50, 420), 65, (49, 119, 72)
        )

    screen.draw.filled_rect(
        Rect(0, GROUND_Y, WIDTH, 60),
        (107, 72, 43),
    )

    for x, y, width, height in PLATFORMS[1:]:
        screen.draw.filled_rect(
            Rect(x, y, width, height),
            (118, 78, 43),
        )

        screen.draw.filled_rect(
            Rect(x, y, width, 6),
            (78, 151, 67),
        )

    # Exit gate.
    gate_rect = Rect(835, 455, 38, 85)

    screen.draw.filled_rect(
        gate_rect,
        (92, 55, 33),
    )

    screen.draw.rect(
        gate_rect,
        (247, 207, 105),
    )


def draw():
    draw_background()

    if game_state == "menu":
        screen.draw.text(
            "JUNGLE ESCAPE",
            center=(WIDTH // 2, 150),
            fontsize=58,
            color="white",
            shadow=(2, 2),
            scolor="black",
        )

        screen.draw.text(
            "Collect all four coins and reach the golden gate!",
            center=(WIDTH // 2, 220),
            fontsize=23,
            color="white",
        )

        draw_button("START GAME", (WIDTH // 2, 320))

        draw_button(
            "SOUND: " + ("ON" if sound_enabled else "OFF"),
            (WIDTH // 2, 390),
        )

        draw_button("EXIT", (WIDTH // 2, 460))
        return

    if game_state in ("playing", "won", "lost"):
        for coin in coins:
            if not coin.collected:
                coin.actor.draw()

        for enemy in enemies:
            enemy.actor.draw()

        for enemy in flying_enemies:
            enemy.actor.draw()

        if (
            game_state != "lost"
            or int(player.invulnerable * 10) % 2 == 0
        ):
            player.actor.draw()

        screen.draw.text(
            "Health: " + "♥ " * player.health,
            (18, 16),
            fontsize=27,
            color="white",
        )

        screen.draw.text(
            "Coins: " + str(score) + "/4",
            (18, 48),
            fontsize=24,
            color="white",
        )

        screen.draw.text(
            "Move: ← → / A D     Jump: SPACE",
            (WIDTH - 350, 18),
            fontsize=18,
            color="white",
        )

    if game_state == "won":
        screen.draw.filled_rect(
            Rect(190, 205, 520, 170),
            (28, 75, 48),
        )

        screen.draw.text(
            "YOU ESCAPED!",
            center=(450, 250),
            fontsize=48,
            color="yellow",
        )

        screen.draw.text(
            "Press ENTER to play again  |  ESC for menu",
            center=(450, 315),
            fontsize=21,
            color="white",
        )

    elif game_state == "lost":
        screen.draw.filled_rect(
            Rect(190, 205, 520, 170),
            (75, 35, 35),
        )

        screen.draw.text(
            "GAME OVER",
            center=(450, 250),
            fontsize=48,
            color="white",
        )

        screen.draw.text(
            "Press ENTER to try again  |  ESC for menu",
            center=(450, 315),
            fontsize=21,
            color="white",
        )


def update(dt):
    global game_state

    if game_state != "playing":
        return

    player.update(dt)

    for enemy in enemies:
        enemy.update(dt)

    for enemy in flying_enemies:
        enemy.update(dt)

    for coin in coins:
        if not coin.collected:
            coin.update(dt)

            if player.actor.colliderect(coin.actor):
                coin.collected = True
                score_coin()

    for enemy in enemies + flying_enemies:
        if player.actor.colliderect(enemy.actor):
            player.hurt()

    if player.actor.top > HEIGHT:
        player.health = 0

    if player.health <= 0:
        game_state = "lost"
        play_sound("game_over")

    exit_gate = Rect(835, 455, 38, 85)

    if (
        score == len(coins)
        and player.actor.colliderect(exit_gate)
    ):
        game_state = "won"
        play_sound("win")


def score_coin():
    global score

    score += 1
    play_sound("coin")


def on_mouse_down(pos):
    global sound_enabled, game_state

    x, y = pos

    if game_state == "menu":
        if 296 <= y <= 344 and 335 <= x <= 565:
            start_game()

        elif 366 <= y <= 414 and 335 <= x <= 565:
            sound_enabled = not sound_enabled

            if sound_enabled:
                music.play("background")
            else:
                music.stop()

        elif 436 <= y <= 484 and 335 <= x <= 565:
            exit()


def on_key_down(key):
    global game_state

    if key == keys.ESCAPE:
        game_state = "menu"

    elif key == keys.RETURN and game_state in ("won", "lost"):
        start_game()


def on_key_up(key):
    pass


def on_music_end():
    if sound_enabled:
        music.play("background")
