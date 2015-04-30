import pygame
from pygame.locals import *

def RelRect(actor,camera):
    '''creates a relative rect for drawing to the screen using a subrect of the world it is inside.'''
    return pygame.Rect(actor.rect.x-camera.rect.x, actor.rect.y-camera.rect.y, actor.rect.w, actor.rect.h)

class Camera(object):
    '''Class for displaying a portion of a level to the screen'''
    def __init__(self,Screen, Focus, Level_size):
        '''Screen(Surface),Focus(Rect),Level_size([int,int])'''
        self.focus = Focus #must be pygame.Rect
        self.rect = Screen.get_rect()
        self.rect.center = self.focus.center
        self.WorldBounds = Rect(0,0,Level_size)
        self.UPDTSPD = 25
    def update(self):
        '''updates camera. fixes display to center over the self.focus object'''
        dx = self.focus.centerx - self.rect.centerx +.05
        dy = self.focus.centery - self.rect.centery +.05
        #dx is positive if the focus moved right
        #dy is positive if the focus moved down.
        
        if abs(dx) > self.UPDTSPD:
            self.rect.centerx = self.focus.centerx - self.UPDTSPD*cmp(dx,0)
        if abs(dy) > self.UPDTSPD:
            self.rect.centery = self.focus.centery - self.UPDTSPD*cmp(dy,0)
        self.rect.clamp_ip(self.WorldBounds)
    
    def draw_sprites(self,surface,sprites):
        '''objects in sprites must have 'image' and 'rect' members. surface must be a pygame surface.'''
        for s in sprites:
            if s.rect.colliderect(self.rect):
                surf.blit(s.image,RelRect(s,self))
                
