import pygame, Constants, threading
from Constants import *
from pygame.locals import *

# import threading and utilize a threading component in your update.
# we want to only draw/update important objects and those that are on screen. 
# In reality we may need more constants defining the walls and other stuff. maybe it's best for the player not to hold a copy. 
# instead each class should check themselves inside those constants. Then our thread can handle whether or not the object belongs in
# the update list or in the layers list. (this prevents the draw call from calling them, instead our HandleScopes() function checks before the draw)
#

def RelRect(actor,camera):
    '''creates a relative rect for drawing to the screen using a subrect of the world it is inside.'''
    return pygame.Rect(actor.rect.x-camera.rect.x, actor.rect.y-camera.rect.y, actor.rect.w, actor.rect.h)

class Camera(object):
    '''Class for displaying a portion of a level to the screen'''
    def __init__(self, Screen, Focus, Level_size):
        '''Screen(Surface),Focus(Rect),Level_size([int,int])'''
        self.focus = Focus #must be pygame.Rect
        self.rect = Screen.get_rect()
        self.rect.center = self.focus.center
        self.Bounds = pygame.Rect(self.rect.centerx-self.rect.width/2-TLWDTH*4,self.rect.centery-self.rect.height/2-TLHGHT*4,self.rect.width+TLWDTH*8,self.rect.height+TLHGHT*8)
        self.Bounds.center = self.rect.center
        self.WallBounds = pygame.Rect(self.rect.centerx-self.rect.width/2-TLWDTH*7,self.rect.centery-self.rect.height/2-TLWDTH*7,self.rect.width+TLWDTH*14,self.rect.height+TLWDTH*14)
        self.WallBounds.center = self.rect.center
        self.WorldBounds = Rect(0-TLWDTH/2,0-TLHGHT/2,Level_size[0],Level_size[1])
        self.UPDTSPD = 25
        self.T1 = threading.Thread()
        self.T1.start()
        self.T2 = threading.Thread()
        self.T2.start()
        self.T3 = threading.Thread()
        self.T3.start()
        
    def update(self):
        '''updates camera. fixes display to center over the self.focus object'''
        self.rect = pygame.display.get_surface().get_rect()
        
        dx = self.focus.centerx - self.rect.centerx +.05
        dy = self.focus.centery - self.rect.centery +.05
        #dx is positive if the focus moved right
        #dy is positive if the focus moved down.
        if abs(dx) > self.UPDTSPD:
            self.rect.centerx = self.focus.centerx - self.UPDTSPD*cmp(dx,0)
        if abs(dy) > self.UPDTSPD:
            self.rect.centery = self.focus.centery - self.UPDTSPD*cmp(dy,0)
        self.rect.clamp_ip(self.WorldBounds)
        self.Bounds.center = self.rect.center
        self.WallBounds.center = self.rect.center
        
    def AdjustObjects(self,what):
        if what in [1,4]:
            rem = []
            for s in Constants.CUR_LEVEL.all_updates:
                Permit = (str(type(s)) in ["<class 'Wall.MovePlatform'>","<class 'Wall.MoveWall'>","<class 'Player.Player'>"] )
                if s.rect.colliderect(self.Bounds) or Permit:
                    rem.append(s)
            #del Constants.CUR_LEVEL.updates[:]
            Constants.CUR_LEVEL.updates = rem
            #updates handled, now layers.
        if what in [2,4]:
            #handles layers
            mem = [pygame.sprite.Group() for i in range(len(Constants.CUR_LEVEL.layers))]
            for i in range(len(Constants.CUR_LEVEL.all_layers)):
                for s in Constants.CUR_LEVEL.all_layers[i]:
                    if s.rect.colliderect(self.Bounds):
                        mem[i].add(s)
            for i in Constants.CUR_LEVEL.layers:
                i.empty()
            Constants.CUR_LEVEL.layers = mem
        if what in [3,4]:
            #handles wallbounds
            rem = []
            for s in Constants.CUR_LEVEL.all_world:
                if s.rect.colliderect(self.WallBounds):
                    rem.append(s)
            #del Constants.CUR_LEVEL.world[:]
            Constants.CUR_LEVEL.world = rem
        return
    def ThreadStart(self):
        self.T1 = threading.Thread(target=self.AdjustObjects,args=[1])
        self.T1.start()
        self.T2 = threading.Thread(target=self.AdjustObjects,args=[2])
        self.T2.start()
        self.T3 = threading.Thread(target=self.AdjustObjects,args=[3])
        self.T3.start()
    def ThreadJoin(self):
        self.T1.join()
        self.T2.join()
        self.T3.join()
    def Draw(self, surf, orders = []):
        '''expecting 2d array. orders is a list of spritegroups'''
        for e in range(len(orders)):
            self.Draw_sprites(surf,orders[e])
            #for each element in the range, draw the spritegroup
        Constants.CUR_LEVEL.CUR_GUI.Draw(surf,None)
        #TODO this is the other way
    def Draw_sprites(self, surf, sprites):
        '''expects a single spritegroup. Calls Draw() on all objects in said group'''
        for s in sprites:
            if s.rect.colliderect(self.rect):
                s.Draw(surf, RelRect(s,self))
        
