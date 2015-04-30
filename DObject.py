import pygame, Constants, glob
from pygame.locals import *
from Constants import *


def MIL(fdct):
    '''fdct is a dictionary of filenames for each animation.
    returns a dictionary of pygame images.'''
    Final = []
    R = []
    L = []
    for flnm in fdct:
        R.append(pygame.image.load(flnm))
        #D's elements are images now
    for img in R:
        L.append(pygame.transform.flip(img,True,False))
    Final.append(R)
    Final.append(L)
    return Final
def MIL2(fdct, delay = 1):
    '''fdct is a filename* for each animation.
    returns a dictionary of pygame images.'''
    Final = []
    delay = int(delay)
    fdct = glob.glob(fdct)
    fdct.sort()
    R = []
    L = []
    for flnm in fdct:
        for i in range(delay):
            R.append(pygame.image.load(flnm))
        #D's elements are images now
    for img in R:
        L.append(pygame.transform.flip(img,True,False))
    Final.append(R)
    Final.append(L)
    return Final
#[moveable,collidable,Z,_,_,_]
class DObject(pygame.sprite.Sprite):
    '''class for all visual entities in game'''
    def __init__(self,x,y,flags=[0,1,0,0,0,0],parentsurface = [None]):
        self.x = x #top left
        self.y = y
        self.flags = flags
        #flags are [ZAxisLevel,Tangibility,HasAction,na,na,na]
        #TODO DECIDE ON A GDMN FORMAT FOR THIS.
        #DObjects should be assigned to different sprite groups based on these flags at startup of the level.
        pygame.sprite.Sprite.__init__(self)
        #self.image = pygame.image.load('world/0.png').convert()
        self.image = pygame.image.load('world/0.png')
        #must replace image with specific image you want in inherited class
        self.rect = Rect(x,y,TLWDTH,TLHGHT)
        self.rect.topleft = [self.x,self.y]
        self.__parsurfs = parentsurface
        self.parsurf = self.__parsurfs[0]
        self.CanCollide = True
        #__parsurfs holds list of 5 surfaces, they should be blitted to screen each frame in order. 
        #this mimics background/foreground blits
        #0=truebackground; 1=BlitsBehindCharacter; 2=BlitsAtCharacterLevel; 3=BlitsAfterCharacter; 4=BlitsLastSpecialEffects
        
