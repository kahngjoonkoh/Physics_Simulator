import pygame
from pygame import gfxdraw as gfx
import random
from settings import *

class Obj(pygame.sprite.Sprite):
    def __init__(self, pos, mass, radius, v0x, v0y, trail: bool=False, static: bool = False):
        super().__init__()

        self.static = static
        self.trail = trail

        self.m = mass
        self.r = radius

        self.x = pos[0]
        self.y = pos[1]

        self.vx = v0x
        self.vy = v0y

        self.ax = 0
        self.ay = 0

        self.trail_hist = []

        self.image = pygame.Surface([self.r*2+1, self.r*2+1])
        self.colour = generate_rand_colour()
        self.update_image()
        self.rect = self.image.get_rect(center=pos)

    def update_xy(self, x, y):
        if self.trail == True:
            self.trail_hist.append((self.x, self.y))
            if len(self.trail_hist) > 1000:
                self.trail_hist.pop(0)
        self.x = x
        self.y = y

    def update_image(self):
        self.image = pygame.Surface([self.r * 2 + 1, self.r * 2 + 1])
        self.image.fill(BG_COLOR)
        self.image.set_colorkey(BG_COLOR)
        draw_aa_circle(self.image, int(self.r), int(self.r), int(self.r), self.colour)
        digits = max(len(str(self.m)), 3)
        font = pygame.font.SysFont('Arial', int(self.r/digits*3))
        text = font.render(str(self.m), True, BLACK, self.colour)
        textRect = text.get_rect()
        textRect.center = (self.r, self.r)

        self.image.blit(text, textRect)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def draw(self, screen, tx, ty):
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.image, (self.rect[0]+tx, self.rect[1]+ty))

def generate_rand_colour():
    return [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]

def draw_aa_circle(s, x, y, radius, color):
    gfx.aacircle(s, x, y, radius, color)
    gfx.filled_circle(s, x, y, radius, color)