import pygame, glob, DObject, Constants
from pygame.locals import *
from DObject import *
from Constants import *

class TriggerObj(DObject):
    def __init__(self, x, y, path = "level",filename = "exp.json",destination = (200,400),radius = 1, img = pygame.image.load('TileSets/SpaceShip/Door1.png')):
        DObject.__init__(self,x,y)
        
        self.image = pygame.transform.scale(img.convert_alpha(),(TLWDTH,TLHGHT))
        self.path=path
        self.filename=filename
        self.destination=destination
        self.radius=radius
        self.rect = self.image.get_rect()
        self.rect.center= [self.x,self.y+(self.image.get_height()-TLHGHT)/2]
        print "location: "+ str(x)+","+str(y)
        
    def SetDestination(dest):
        self.destination = dest
    def SetRadius(r):
        self.radius = r
    def Draw(self, surface, relrect = None):
        if relrect == None:
            #we weren't given a location to defer to
            surface.blit(self.image,self.rect)    
        else:
            surface.blit(self.image,relrect)
            
    def trigger(self,o):
        '''as a door, go to new map or elsewhere on map'''
        if (str(type(o))=="<class 'Player.Player'>"):
            print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
            #if o.parent.map.path + o.parent.map.filename != self.path+self.filename:
                # reload map with ours and then move player to dest
            #    print "crap"
            o.collisionrect.center = self.destination
