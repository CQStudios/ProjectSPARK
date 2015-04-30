import pygame, glob, DObject, Constants
from pygame.locals import *
from DObject import *
from Constants import *

class Wall(DObject):
    def __init__(self, x, y, slope = [0,0], img = pygame.image.load('world/0.png')):
        DObject.__init__(self,x,y)
        self.image = pygame.transform.scale(img.convert_alpha(),(TLWDTH,TLHGHT))
        self.rect = self.image.get_rect()
        self.rect.center= [self.x,self.y]
        self._ST=slope[0]
        self._ET=slope[1]
        self.CanCollide = True
        self.tract = 1.0 #do not modify player's physics
        
    def getSlope(self,x):
        if self._ST*self.rect.height - self._ET*self.rect.height == 0:
            return self._ST*self.rect.height
        return float(self._ST*self.rect.height)-float(x)/self.rect.width*(float(self._ST*self.rect.height)-float(self._ET*self.rect.height))
        
    def Draw(self, surface, relrect = None):
        if relrect == None:
            #we weren't given a location to defer to
            surface.blit(self.image,self.rect)    
        else:
            surface.blit(self.image,relrect)
            
    def act(self,o,dx,dy):
        '''push colliding objects to borders if they don't meet the criteria'''
        l = o.collisionrect.centerx - self.rect.left
        YREP = self.getSlope(l)
        oldYREP = self.getSlope(l-dx)
        oPt = self.rect.top+oldYREP
        Pt = self.rect.top+YREP
        print Pt-o.collisionrect.centery
        b = ""
        if o.collisionrect.centery >= Pt: # o.prevpos[1]>=oPt:
            #DEAL WITH ALL CASES IN WHICH WE HAVE NO CHANCE OF GETTING ON
            b += "CANT GET ON:::"
            print "BULL"
            if dx != 0 or (dy == 0 and dx == 0):
                b+="dx check:::"
                #moving into the block from the sides
                if (o.collisionrect.centerx >= self.rect.left) and (o.prevpos[0] <= self.rect.left):
                    #collision from the left side
                    o.collisionrect.right = self.rect.left
                    o.ddx = -1
                    o.dx = 0
                    b+="Halted along my left:::"
                elif (o.collisionrect.centerx <= self.rect.right) and (o.prevpos[0] >= self.rect.right):
                    #collision from the right side
                    o.collisionrect.left = self.rect.right
                    o.ddx = 1
                    o.dx=0
                    b+="Halted along my right:::"
                elif o.prevpos[0] <= self.rect.left:
                    o.collisionrect.right = self.rect.left
                elif o.prevpos[0] >= self.rect.right:
                    o.collisionrect.left = self.rect.right
                else:
                    print "SHIIIIIIIIIIIIIIIIIIITTTT"
                #elif o.collisionrect.centerx <= self.rect.centerx and o.prevpos[0] <= self.rect.centerx: 
                #    print "strange~~~~~~~~~~~~~~~~~~~~~~~~~ddddddddddddddd"
            elif (o.collisionrect.centerx >= self.rect.left)and(o.collisionrect.centerx <= self.rect.right):
                #center is inside this block, and below it. 
                #set collision rect.top if prevpos was also below
                if o.prevpos[1] > self.rect.bottom:
                    o.collisionrect.top = self.rect.bottom
                    b+= "Halted along my bottom"
                else:
                    o.collisionrect.bottom = Pt
                    o.contact = True
                    o.ddy = 0
                    o.touchground(self)
                    b+= "Halted along my top/slope"
                
            else:
                print "unhandled error with o.centery under block's slope"
                print "dx: "+str(dx)+" - dy: " +str(dy)
            print b   
        else:
            #centery is at or above the slope
            b+="wtf guess we are on"
            if (o.collisionrect.centerx < self.rect.left)or(o.collisionrect.centerx > self.rect.right):
                #the center isn't inside, don't affect it.
                print "4~~"
                return
            elif dy == 0:
                b+="5~~"
                #center is inside it. only shift if bottom is below what it should be.
                o.contact = False
                if o.collisionrect.bottom >= Pt-4 or o.collisionrect.bottom >= oPt-4:
                    o.collisionrect.bottom = Pt
                    o.contact = True
                    print b+"6~~"
                return
            elif o.collisionrect.bottom < Pt:
                print b+"7~~"
                #dy != 0, dx ==0, so there is no true collision here.
                return
            else:
                print b+"8~~"
                o.touchground(self)
                if dy > 0:
                    o.ddy = 0
                    o.collisionrect.bottom = Pt
                    o.contact = True
                #call objects method for touching ground
