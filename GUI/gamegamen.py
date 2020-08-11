import pygame
import random
import math
from dataclasses import dataclass
import dataclasses
from pygame.locals import *

import GUI.Colors as Color
from Game.game import Game, Operation, M_Operation
from Game.puyo import Puyo, Puyopuyo

successes, failures = pygame.init()
print(pygame.font.get_fonts())
font10 = pygame.font.Font('freesansbold.ttf', 10)
font15 = pygame.font.Font('freesansbold.ttf', 15)
font20 = pygame.font.Font('freesansbold.ttf', 20)
print("Initializing pygame: {0} successes and {1} failures.".format(successes, failures))

screen = pygame.display.set_mode((900, 480))
clock = pygame.time.Clock()
FPS = 60
masusize = 20
square = (masusize, masusize)
square_center = (masusize // 2, masusize // 2)
puyo_r = masusize // 2

usePUYOCOLOR = []


class Masu(pygame.sprite.Sprite):

    def __init__(self, x, y, puyo: Puyo):
        super().__init__()
        self.image = pygame.Surface(square, pygame.SRCALPHA)
        self.rect = self.image.get_rect()  # Get rect of some size as 'image'.
        self.velocity = [50 + x, 50 + y]
        self.puyo = puyo
        if puyo is not None:
            id = self.puyo.get_puyo()
            if id == -2:
                self.image.fill(Color.BLACK)
            elif id == -1:
                pygame.draw.circle(self.image, Color.WHITE2, square_center, puyo_r)
            else:
                pygame.draw.circle(self.image, usePUYOCOLOR[id - 1], square_center, puyo_r)
        else:
            self.image.fill(Color.BLACK2)
        self.rect.move_ip(*self.velocity)

    def update(self):
        if self.puyo is not None:
            id = self.puyo.get_puyo()
            if id > 0:
                pygame.draw.circle(self.image, usePUYOCOLOR[id - 1], square_center, puyo_r)
                text = font10.render(str(self.puyo.uid), True, Color.WHITE)
                self.image.blit(text, (5, 2))

        else:
            self.image.fill(Color.BLACK2)


class GameGamen():
    def __init__(self, g: Game = None):
        global usePUYOCOLOR
        if g is None:
            g = Game()
        self.g = g
        usePUYOCOLOR = random.sample(Color.PUYOCOLORS, self.g.color_len)
        stage_list = self.g.stage.stage_list()
        rows = self.g.stage.height
        cols = self.g.stage.width
        self.next = [[None, None], [None, None]]
        self.maseme = []
        self.masume_group = pygame.sprite.RenderUpdates()

        for y in range(rows):
            self.maseme.append([])
            for x in range(cols):
                self.maseme[y].append(Masu(x * (masusize + 2), y * (masusize + 2), stage_list[y][x]))
                self.masume_group.add(self.maseme[y][x])
        for n in range(4):
            self.next[n // 2][n % 2] = Masu((x + 2) * (masusize + 2), (4 + n + n // 2) * (masusize + 2), None)
            self.masume_group.add(self.next[n // 2][n % 2])

        self.masume_group.add(self.maseme[y][x])

        self.running = True
        self.skipping = False
        self.finish = False
        self.flame = 0
        self.one_flame = True

        self.OI = 4  # operation interval
        self.oI_left = self.OI
        self.oI_right = self.OI
        self.oI_down = self.OI

        self.g.next()

        self.isdraw = True

    def reset(self):
        self.__init__()

    def play(self):
        self.draw('')
        while self.running:
            self.loop()
        print("Exited the game loop. Game will quit...")
        quit()  # Not actually necessary since the script will exit anyway.

    def key_push_check(self):
        one_flame = False
        skipping = False
        operation = Operation()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return 'quit'
            if event.type == KEYDOWN:  # キーを押したとき
                # ESCキーならスクリプトを終了
                if event.key == K_ESCAPE:
                    sys.exit()
                if event.key == K_a:
                    operation.turn_left = True
                elif event.key == K_d:
                    operation.turn_right = True
                elif event.key == K_r:
                    self.reset()
                    return 'reset'
                elif event.key == K_g:
                    one_flame = True

        # 押されているキーをチェック
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]:
            if self.oI_left < 0:
                operation.left = True
            else:
                if self.oI_left == self.OI:
                    operation.left = True
                self.oI_left -= 1
        else:
            self.oI_left = self.OI
        if pressed_keys[K_RIGHT]:
            if self.oI_right < 0:
                operation.right = True
            else:
                if self.oI_right == self.OI:
                    operation.right = True
                self.oI_right -= 1
        else:
            self.oI_right = self.OI

        if pressed_keys[K_DOWN]:
            if self.oI_down < 0:
                operation.down = True
            else:
                if self.oI_down == self.OI:
                    operation.down = True
                self.oI_down -= 2
        else:
            self.oI_down = self.OI

        if pressed_keys[K_0]:
            one_flame = True
            skipping = True
        elif pressed_keys[K_9]:
            one_flame = True
        elif pressed_keys[K_s]:
            operation.down = True
            one_flame = True
        return one_flame, skipping, operation

    def draw(self, move, operation: Operation = None):
        g = self.g
        stage = self.g.stage
        screen.fill(Color.WHITE)

        stage_list, puyolist = stage.stage_list(move_puyo=True)
        for y in range(len(stage_list)):
            for x in range(len(stage_list[0])):
                self.maseme[y][x].puyo = stage_list[y][x]

        for i, puyopuyo_info in enumerate((g.next_puyo.iteration(), g.nxnx_puyo.iteration())):
            self.next[i][0].puyo = puyopuyo_info[0][2]
            self.next[i][1].puyo = puyopuyo_info[1][2]

        self.masume_group.update()
        self.masume_group.draw(screen)

        for puyoinfo in puyolist:
            id = puyoinfo[2].get_puyo()
            pygame.draw.circle(screen, usePUYOCOLOR[id - 1],
                               (int(50 + (masusize + 2) * puyoinfo[0] + 10),
                                int(50 + (masusize + 2) * puyoinfo[1] + 10)), puyo_r)

        flame_text = font20.render(str(self.flame), True, (255, 0, 0))
        screen.blit(flame_text, (0, 0))
        h = 0
        for i in range(len(usePUYOCOLOR)):
            text = font20.render(str(stage.puyoColection.titles(i + 1)), True, usePUYOCOLOR[i])
            screen.blit(text, (400, 20 + 20 * i))

        if operation is not None:
            i = i + 10
            for key, value in dataclasses.asdict(operation).items():
                text = font20.render(f"{key}, {value}", True, Color.BLACK)
                screen.blit(text, (400, 20 + 20 * i))
                i += 1

        text = font20.render(move, True, Color.BLACK)
        screen.blit(text, (400, 150))
        text = font20.render(str(g.point), True, Color.BLACK)
        screen.blit(text, (400, 180))
        if g.turn_end:
            text = font20.render('turn end', True, Color.BLACK)
            g.turn_end = False
            screen.blit(text, (400, 210))
        pygame.display.update()

    def loop(self):
        g = self.g
        dt = clock.tick(FPS if not self.skipping else 0) / 1000
        key_push = self.key_push_check()
        if key_push == 'reset':
            if self.isdraw:
                self.draw(None)
            return False
        elif key_push == 'quit':
            return False
        else:
            self.one_flame, self.skipping, g.operation = key_push
        if self.one_flame and not self.finish:
            self.flame += 1
            stage, move = g.loop()
            if g.batankyu:
                move = 'batankyu'
                self.finish = True
            if self.isdraw:
                self.draw(move, g.operation)
        return True

    def skiploop(self, m_operation: M_Operation):
        g = self.g
        dt = clock.tick(FPS if not self.skipping else 0) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            if event.type == KEYDOWN:  # キーを押したとき
                # ESCキーならスクリプトを終了
                if event.key == K_ESCAPE:
                    sys.exit()
                if event.key == K_p:
                    if not self.finish:
                        end_moves = g.skip_loop(m_operation)
                        end_moves = g.skip_loop(m_operation)
                        if g.batankyu:
                            self.finish = True
                            return False
                        if self.isdraw:
                            self.draw(end_moves[-1][2], end_moves[-1][0])
        return True


if __name__ == '__main__':
    game = GameGamen()
    # game.play()
    game.draw('')
    while True:
        game.skiploop(m_operation=M_Operation(side=6))
    # game.play()
