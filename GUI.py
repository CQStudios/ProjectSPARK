import Item
from Constants import *
from DObject import *
import math

class GUI(DObject):
    def __init__(self,x,y, parent):
        '''again, parent must be a level object.'''
        DObject.__init__(self,x,y,[None])
        self.NRGGUI = []
        self.NRGGUI.append(pygame.image.load('objects/Bar/insectblank.png'))
        self.NRGGUI.append(pygame.image.load('objects/Bar/optimusblank.png'))
        self.NRGGUI.append(pygame.image.load('objects/Bar/cyanblank.png'))
        self.Gimg = self.NRGGUI[0]
        self.Himg = pygame.image.load('objects/Bar/darkblue.png')
        self.font = pygame.font.Font('Font/Prototype.ttf',22)
        self.parent = parent
        self.flashframe = 0
        self.MAXFLASHLENGTH = 8
        self.flash = 0
    def update(self):
        self.flashframe += 1
        if self.parent.User.spark:
            self.Gimg = self.NRGGUI[self.parent.User.spark.state]
            #self.Himg = self.parent.User.health
            
    def Draw(self, surface, relrect):
        self.update()
        NRGlvl = MaxNRG = energy = state = health=1
        if self.parent.User.spark:
            NRGlvl = self.parent.User.spark.NRGlvl
            MaxNRG = self.parent.User.spark.MaxNRG
            energy = self.parent.User.spark.energy
            state = self.parent.User.spark.state
            health = self.parent.User.health
            Mhealth = self.parent.User.MAX_HEALTH
        r = 10+NRGlvl*20
        d = (self.Gimg.get_width()-10)*energy/MaxNRG
        if d < 0:
            d = 0
        nrgimg = pygame.image.load('objects/Bar/guage'+str(NRGlvl)+'.png').convert_alpha()
        w = NRGlvl*2+2
        red = (state/2+1)*100%255
        grn = (state/1+1)*100%255
        blu = (state/.5+1)*330%255
        pygame.draw.line(surface, (0,0,0),(100,50),(101+d,50),w+2)
        pygame.draw.line(surface, (red,grn,blu),(100,50),(100+d,50),w)
        pygame.draw.line(surface, (red+(255-red)/2,grn+(255-grn)/2,blu+(255-blu)/2),(100,50),(100+d,50),2*w/3)
        pygame.draw.line(surface, (255-red/5,255-grn/5,255-blu/5),(100,50),(100+d,50),w/3)
        surface.blit(self.Gimg,(90,26,self.Gimg.get_width(),self.Gimg.get_height()))
        surface.blit(nrgimg,(45+self.Gimg.get_width(),20,nrgimg.get_width(),nrgimg.get_height()))
        
        d = (self.Himg.get_width()-15)*health/Mhealth
        if d < 0:
            d = 0
        w = 8
        
        grn = health/(Mhealth+(Mhealth/(health+.5)))*300-70*self.flash/self.MAXFLASHLENGTH
        if grn > 255:grn=255
        if grn<0:grn=0
        red = (Mhealth*1.5-health)/Mhealth*200+70*self.flash/self.MAXFLASHLENGTH
        if red > 255:
            red = 255
        elif red <0:
            red = 0
        blu = red/100*grn/100*(255/3)
        if blu >255:
            blu = 255
        elif blu <0:
            blu = 0
        nimg = self.Himg.copy()
        
        if health/Mhealth <= .8 and self.flashframe > self.MAXFLASHLENGTH*2.5:
            pygame.draw.line(nimg, (red,grn,0,255-grn),(10,24),(11+(self.Himg.get_width()-10),24),w+8)
            self.flash+=1
            if self.flash >= self.MAXFLASHLENGTH:
                self.MAXFLASHLENGTH = Constants.FPS*(health/Mhealth/3)+2
                self.flashframe = 0
                self.flash = 0
        pygame.draw.line(nimg, (0,0,0),(10,24),(11+d,24),w+4)
        pygame.draw.line(nimg, (red*.8,grn*.8,blu*.8),(10,24),(10+d,24),w+2)
        pygame.draw.line(nimg, (red+(255-red)/4,grn+(255-grn)/4,blu+(255-blu)/4),(10,24),(10+d,24),2*w/3)
        pygame.draw.line(nimg, (red+(255-red)/3,grn+(255-grn)/3,blu+(255-blu)/3),(10,24),(10+d,24),w/3)
        nimg.blit(self.Himg,(0,0,self.Himg.get_width(),self.Himg.get_height()))
        Htext2 = self.font.render(str(health),True,(255,200,30))
        Htext = self.font.render(str(health),True,(0,0,0))
        Htext1= Htext.copy()
        Htext1.blit(Htext,(2,0,Htext.get_width(),Htext.get_height()))
        Htext1.blit(Htext2,(2,2,Htext2.get_width(),Htext2.get_height()))
        nimg.blit(Htext1,(nimg.get_width()-Htext2.get_width(),nimg.get_height()-Htext2.get_height(),Htext2.get_width(),Htext2.get_height()))
        surface.blit(nimg,(90,76,self.Himg.get_width(),self.Himg.get_height()))
        
    
