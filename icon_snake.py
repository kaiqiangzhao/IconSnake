#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pygame.locals import *
import random
import pygame
import config


class Food:
    def __init__(self, x, y):
        # 初始化食物的位置
        self.x = x
        self.y = y
        self.icon = pygame.transform.scale(
                pygame.image.load("icon_basket/foods/first_food.png").convert_alpha(),
                config.SNAKE_NODE_SIZE
        )

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            config.BORDER_COLOR,
            (
                self.x - config.BORDER_WIDTH,
                self.y - config.BORDER_WIDTH,
                config.SNAKE_NODE_SIZE[0] + 2 * config.BORDER_WIDTH,
                config.SNAKE_NODE_SIZE[1] + 2 * config.BORDER_WIDTH
            ),
            config.BORDER_WIDTH,
            border_radius=config.BORDER_RADIUS
        )
        if self.icon:
            surface.blit(self.icon, (self.x, self.y))


class Snake:
    def __init__(self, length=2, step=50):
        """
        length: 初始长度
        direction: 初始方向
        step: 一步走多少个像素
        """
        self.x = []
        self.y = []
        self.icons = []
        self.step = step
        self.length = length
        self.direction = 0

        # 初始化
        for i in range(length-1, -1, -1):
            self.x.append(i * step)
            self.y.append(0)

        head = pygame.transform.rotate(
            pygame.transform.scale(
                pygame.image.load("icon_basket/snake/head.png").convert_alpha(),
                config.SNAKE_NODE_SIZE
            ),
            -90
        )
        tail = pygame.transform.scale(
            pygame.image.load("icon_basket/snake/tail.png").convert_alpha(),
            config.SNAKE_NODE_SIZE
        )
        self.head = [head]
        self.tail = [tail]

    def update(self):
        for i in range(self.length-1, 0, -1):
            self.x[i] = self.x[i-1]
            self.y[i] = self.y[i-1]
        if self.direction == 0:
            self.x[0] = self.x[0] + self.step
        if self.direction == 1:
            self.x[0] = self.x[0] - self.step
        if self.direction == 2:
            self.y[0] = self.y[0] - self.step
        if self.direction == 3:
            self.y[0] = self.y[0] + self.step

    def move_right(self):
        if self.direction == 2:
            angle = -90
        else:
            angle = 90
        for index, img in enumerate(self.head):
            self.head[index] = pygame.transform.rotate(img, angle)
        self.direction = 0

    def move_left(self):
        if self.direction == 2:
            angle = 90
        else:
            angle = -90
        for index, img in enumerate(self.head):
            self.head[index] = pygame.transform.rotate(img, angle)
        self.direction = 1

    def move_up(self):
        if self.direction == 0:
            angle = 90
        else:
            angle = -90
        for index, img in enumerate(self.head):
            self.head[index] = pygame.transform.rotate(img, angle)
        self.direction = 2

    def move_down(self):
        if self.direction == 0:
            angle = -90
        else:
            angle = 90
        for index, img in enumerate(self.head):
            self.head[index] = pygame.transform.rotate(img, angle)
        self.direction = 3

    def draw(self, surface):
        all_icons = []
        if self.length == 3 and self.icons:
            self.tail.append(self.icons.pop())
        all_icons.extend([*self.head, *self.icons, *self.tail])
        for i in range(0, self.length):
            pygame.draw.rect(
                surface,
                config.BORDER_COLOR,
                (
                    self.x[i]-config.BORDER_WIDTH,
                    self.y[i]-config.BORDER_WIDTH,
                    config.SNAKE_NODE_SIZE[0]+2*config.BORDER_WIDTH,
                    config.SNAKE_NODE_SIZE[1]+2*config.BORDER_WIDTH
                 ),
                config.BORDER_WIDTH,
                border_radius=config.BORDER_RADIUS
            )
            surface.blit(all_icons[i], (self.x[i], self.y[i]))


class Game:
    def __init__(self, name="Icon Snake"):
        self.name = name
        self.window_width = config.WINDOW_WIDTH
        self.window_height = config.WINDOW_HEIGHT
        self._running = True
        self._display_surf = None
        self._snake_surf = None
        self._food_surf = None
        self.snake = None
        self.food = None
        self.foods = None
        self.col = self.window_width // config.FOOD_SIZE[0] - 1  # 列数
        self.row = self.window_height // config.FOOD_SIZE[1] - 1  # 行数

    def rand_food_position(self):
        # TODO: 寻找更好的数据结构和算法, 减少数据类型转换
        empty_points = set([(i, j) for i in range(self.col+1) for j in range(self.row+1)])
        snake_points = set([(i//self.snake.step, j//self.snake.step) for i, j in zip(self.snake.x, self.snake.y)])
        empty_points.difference_update(snake_points)
        rand_point = random.choice(list(empty_points))
        if not rand_point:
            self._running = False
            return 0, 0
        rand_x = rand_point[0] * config.FOOD_SIZE[0]
        rand_y = rand_point[1] * config.FOOD_SIZE[1]
        return rand_x, rand_y

    def is_collision_self(self, x1, y1, x2, y2):
        # 是否碰撞到自己
        # 如何判断两个矩形是否相交
        snake_width, snake_height = config.SNAKE_NODE_SIZE
        head_x_line = (x1, x1 + snake_width)
        head_y_line = (y1, y1 + snake_height)
        body_x_line = (x2, x2 + snake_width)
        body_y_line = (y2, y2 + snake_height)
        max_x_line = max(head_x_line[0], body_x_line[0])
        min_x_line = min(head_x_line[1], body_x_line[1])
        max_y_line = max(head_y_line[0], body_y_line[0])
        min_y_line = min(head_y_line[1], body_y_line[1])
        if max_x_line < min_x_line and max_y_line < min_y_line:
            return True
        else:
            return False

    def is_collision_food(self, x1, y1, x2, y2):
        # 是否碰撞到食物
        food_width, food_height = config.FOOD_SIZE
        snake_width, snake_height = config.SNAKE_NODE_SIZE
        head_x_line = (x1, x1 + snake_width)
        head_y_line = (y1, y1 + snake_height)
        food_x_line = (x2, x2 + food_width)
        food_y_line = (y2, y2 + food_height)
        max_x_line = max(head_x_line[0], food_x_line[0])
        min_x_line = min(head_x_line[1], food_x_line[1])
        max_y_line = max(head_y_line[0], food_y_line[0])
        min_y_line = min(head_y_line[1], food_y_line[1])
        if max_x_line < min_x_line and max_y_line < min_y_line:
            return True
        else:
            return False

    def is_collision_win(self, x1, y1):
        # 是否碰撞到墙壁
        if 0 <= x1 + config.SNAKE_NODE_SIZE[0]/2 <= self.window_width \
                and 0 <= y1 + config.SNAKE_NODE_SIZE[1]/2 <= self.window_height:
            return False
        return True

    def init_display_surf(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.window_width, self.window_height), 0, 32)
        self._display_surf.fill(config.BACKGROUND)  # 背景
        if os.path.exists("static/game_icon.png"):
            logo_surf = pygame.image.load("static/game_icon.png").convert_alpha()
            pygame.display.set_icon(logo_surf)
        pygame.display.set_caption("Icon Snake")

    def init_word_surf(self):
        font = pygame.font.Font("static/weimijianshu.otf", self.window_width//16)
        tip = font.render('按任意键开始 Icon Snake!!!', True, config.FONT_COLOR)
        self._display_surf.blit(tip, ((self.window_width - tip.get_width()) / 2, (self.window_height - tip.get_height()) / 2))

    def init_element(self):
        self.snake = Snake(length=config.SNAKE_INIT_LEN)
        rand_x, rand_y = self.rand_food_position()
        self.food = Food(rand_x, rand_y)
        self.foods = [os.path.join(config.FOOD_ICON_PATH, fname) for fname in os.listdir(config.FOOD_ICON_PATH) if fname.endswith("png")]
        self.foods.remove("icon_basket/foods/first_food.png")
        # 打乱原有顺序
        random.shuffle(self.foods)
        # 插入定制顺序的图片
        food_vip_path = "icon_basket/foods_vip/"
        if os.path.exists(food_vip_path):
            for img_name in sorted(os.listdir("icon_basket/foods_vip/")):
                self.foods.insert(int(img_name.split(".")[0]), os.path.join(food_vip_path, img_name))

    def on_loop(self):
        self.snake.update()

        if self.is_collision_win(self.snake.x[0], self.snake.y[0]):
            self._running = False
            return None

        for i in range(2, self.snake.length):
            if self.is_collision_self(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                self._running = False
                return None

        # 把食物当成蛇的一部分进行碰撞检测
        if self.is_collision_food(self.snake.x[0], self.snake.y[0], self.food.x, self.food.y):
            self.snake.length = self.snake.length + 1
            self.snake.x.append(self.food.x)
            self.snake.y.append(self.food.y)
            self.snake.icons.append(self.food.icon)
            self.food.x, self.food.y = self.rand_food_position()
            if not self.foods:
                self._running = False
                return None
            # imgs_path = random.choice(self.foods)
            # self.foods.remove(imgs_path)
            imgs_path = self.foods.pop(0)
            self.food.icon = pygame.transform.smoothscale(
                pygame.image.load(imgs_path).convert_alpha(),
                config.FOOD_SIZE
            )

    def on_render(self):
        self._display_surf.fill(config.BACKGROUND)  # 重新渲染背景
        self.snake.draw(self._display_surf)
        self.food.draw(self._display_surf)
        pygame.display.flip()

    def execute(self):
        self.init_element()
        self._running = True
        clock = pygame.time.Clock()
        while self._running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit()  # 接收到退出事件后，退出程序
                elif event.type == KEYDOWN:
                    if event.key == K_RIGHT and self.snake.direction != 1 and self.snake.direction != 0:  # 不能倒着走
                        self.snake.move_right()
                    elif event.key == K_LEFT and self.snake.direction != 0 and self.snake.direction != 1:
                        self.snake.move_left()
                    elif event.key == K_UP and self.snake.direction != 3 and self.snake.direction != 2:
                        self.snake.move_up()
                    elif event.key == K_DOWN and self.snake.direction != 2 and self.snake.direction != 3:
                        self.snake.move_down()
                    elif event.key == K_ESCAPE:
                        self._running = False
            self.on_loop()
            self.on_render()
            clock.tick(6)  # 帧率, 也对于蛇的移动速度

    def quit(self):
        pygame.quit()

    def restart(self):
        self.init_element()
        self.execute()

    def start(self):
        self.init_display_surf()
        self.init_word_surf()
        pygame.display.update()

        clock = pygame.time.Clock()
        fail_flag = False
        while True:  # 键盘监听事件
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.quit()  # 终止程序
                    elif not fail_flag:
                        self.execute()
                        fail_flag = True
                    else:
                        self.restart()
            clock.tick(5)


if __name__ == "__main__":
    game = Game()
    game.start()
