import pygame, math, Constants, Player
from pygame.locals import *
def AI_Run_Jump(self):
    '''base AI'''
    o=x=sq=tr=lsx=lsy=rsx=rsy=l1=l2=r1=r2=0
    #print self.direction
    lsx = cmp(self.ddx,0)
    #lsx = 1-self.direction*2
    changeddir = 0
    if self.collisionrect.centerx <= self.prevpos[0]+1 and self.direction ==0:
        #this means we stopped going right
        if self.state/2 in [6,7,8]:
            lsx = 1-self.direction*2
        if self.grounded and self.state/2 in [9]:
            self.direction = 1
            self.ddx = -1
            lsx = -1
        elif self.grounded:
            changeddir = 1
    elif self.collisionrect.centerx >= self.prevpos[0]-1 and self.direction ==1:
        if self.state/2 in [6,7,8]:
            lsx = 1-self.direction*2
        if self.grounded and self.state/2 in [9]:
            #if we're grounded, but not in land animation
            self.direction = 0
            self.ddx = 1
            lsx = 1
        elif self.grounded:
            changeddir = 1
    if self.grounded:
        o = changeddir
    if self.state/2 in [6,7]:
        o = 1
    if self.ddy > Constants.GRAV and not self.jump:
        o = 1
    self.PumpInput({"L1":l1,"L2":l2,"R1":r1,"R2":r2,"X":x,"O":o,"Tri":tr,"Sqr":sq,"LSX":lsx,"LSY":lsy,"RSX":rsx,"RSY":rsy})
    
def AI_Run_Fall(self):
    '''base AI'''
    o=x=sq=tr=lsx=lsy=rsx=rsy=l1=l2=r1=r2=0
    #print self.direction
    lsx = cmp(self.ddx,0)
    #lsx = 1-self.direction*2
    changeddir = 0
    if self.collisionrect.centerx <= self.prevpos[0]+1 and self.direction ==0:
        #this means we stopped going right
        if self.state/2 in [6,7,8]:
            lsx = 1-self.direction*2
        elif self.grounded:
            self.direction = 1
            self.ddx = -1
            lsx = -1
    elif self.collisionrect.centerx >= self.prevpos[0]-1 and self.direction ==1:
        if self.state/2 in [6,7,8]:
            lsx = 1-self.direction*2
        elif self.grounded:
            #if we're grounded, but not in land animation
            self.direction = 0
            self.ddx = 1
            lsx = 1
    self.PumpInput({"L1":l1,"L2":l2,"R1":r1,"R2":r2,"X":x,"O":o,"Tri":tr,"Sqr":sq,"LSX":lsx,"LSY":lsy,"RSX":rsx,"RSY":rsy})
        
def AI_Run(self):
    '''Runs, when it starts falling it turns around'''
    o=x=sq=tr=lsx=lsy=rsx=rsy=l1=l2=r1=r2=0
    #print self.direction
    lsx = cmp(self.ddx,0)
    #lsx = 1-self.direction*2
    changeddir = 0
    if self.collisionrect.centerx <= self.prevpos[0] and self.direction ==0:
        #this means we stopped going right
        if self.state/2 in [6,7,8]:
            lsx = 1-self.direction*2
        elif self.grounded:
            self.direction = 1
            self.ddx = -.2
            lsx = -1
    elif self.collisionrect.centerx >= self.prevpos[0] and self.direction ==1:
        if self.state/2 in [6,7,8]:
            lsx = 1-self.direction*2
        elif self.grounded:
            #if we're grounded, but not in land animation
            self.direction = 0
            self.ddx = .2
            lsx = 1
    if not self.grounded:
        check = Rect(self.collisionrect.centerx,self.collisionrect.bottom,cmp(self.ddx,0),Constants.TLHGHT/3)
        ndir = 1
        for obj in self.collideswith:
            if check.colliderect(obj.collisionrect):
                #grounded, 
                ndir = 0
                break
        if ndir:
            self.direction = 1-self.direction
            lsx = self.ddx = 1-self.direction*2
            self.collisionrect.centerx = self.prevpos[0]
            
    self.PumpInput({"L1":l1,"L2":l2,"R1":r1,"R2":r2,"X":x,"O":o,"Tri":tr,"Sqr":sq,"LSX":lsx,"LSY":lsy,"RSX":rsx,"RSY":rsy})
    
def AI_Run_Tortadillo(self):
    '''Runs, when it starts falling it turns around
    attacks players.'''
    o=x=sq=tr=lsx=lsy=rsx=rsy=l1=l2=r1=r2=0
    #print self.direction
    lsx = cmp(self.ddx,0)
    #lsx = 1-self.direction*2
    changeddir = 0
    if self.collisionrect.centerx <= self.prevpos[0] and self.direction ==0:
        #this means we stopped going right
        if self.state/2 in [6,7,8]:
            lsx = 1-self.direction*2
        elif self.grounded:
            self.direction = 1
            self.ddx = -.9
            lsx = -1
    elif self.collisionrect.centerx >= self.prevpos[0] and self.direction ==1:
        if self.state/2 in [6,7,8]:
            lsx = 1-self.direction*2
        elif self.grounded:
            #if we're grounded, but not in land animation
            self.direction = 0
            self.ddx = .9
            lsx = 1
    if not self.grounded:
        check = Rect(self.collisionrect.centerx,self.collisionrect.bottom,cmp(self.ddx,0),Constants.TLHGHT/3)
        ndir = 1
        for obj in self.parent.world:
            if check.colliderect(obj.collisionrect):
                #grounded, 
                ndir = 0
                break
        if ndir:
            self.direction = 1-self.direction
            lsx = self.ddx = 1-self.direction*2
            self.collisionrect.centerx = self.prevpos[0]
            
    self.PumpInput({"L1":l1,"L2":l2,"R1":r1,"R2":r2,"X":x,"O":o,"Tri":tr,"Sqr":sq,"LSX":lsx,"LSY":lsy,"RSX":rsx,"RSY":rsy})
        
        
