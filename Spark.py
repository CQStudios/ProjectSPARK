import Item
from Constants import *
from DObject import *
import math

global TIMEPERBAR
TIMEPERBAR = 20
class Spark(pygame.sprite.Sprite):
    def __init__(self, parent = "SparkOnly"):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.health = 20 #TODO
        self.state = 0 #can be 0, 1 or 2 chr, off, def
        self.action = 0
        self.LS = [0,0]
        self.RS = [0,0]
        self.imglst = []
        self.pastpos =[[self.parent.rect.centerx,self.parent.rect.centery]]
        self.statelist = [0,1,2]
        self.energy = FPS*TIMEPERBAR #takes 10 seconds to load up fully in charge state
        self.MaxNRG = FPS*TIMEPERBAR # take TIMEPERBAR seconds to recharge a bar. 
        self.NRGlvl = 0
        self.MaxNRGlvl = 5
        self.power = 8
        if parent != "SparkOnly":
            self.imglst.append(MIL2('objects/spark/SparkNorm*',3)[1])
            self.imglst.append(MIL2('objects/spark/SparkNorm*',3)[0])
            self.imglst.append(MIL2('objects/spark/fire/sparkfire*.png',1)[0])
            self.imglst.append(MIL2('objects/spark/fire/sparkfire*.png',1)[1])
            self.imglst.append(MIL2('objects/spark/shield/shield*',2)[1])
            self.imglst.append(MIL2('objects/spark/shield/shield*',2)[1])
        else:
            self.imglst.append(MIL2('objects/spark/SparkNorm*',3)[1])
            self.imglst.append(MIL2('objects/spark/SparkNorm*',3)[0])
            self.imglst.append(MIL2('objects/spark/fire/sparkfire*.png',1)[0])
            self.imglst.append(MIL2('objects/spark/fire/sparkfire*.png',1)[1])
            self.imglst.append(MIL2('objects/spark/shield/shield*',2)[1])
            self.imglst.append(MIL2('objects/spark/shield/shield*',2)[1])
        self.image = pygame.image.load('objects/spark/fire/sparkfireR1.png')
        self.original = self.image
        self.frame = 0
        self.x = self.parent.rect.centerx
        self.y = self.parent.rect.centery
        self.rect = self.image.get_rect()
        self.CanPerformADInfinitely = False       
        self.CurrentAction = "None"
        self.CAcounter = 0
        self.xoff = self.yoff=0
        
    def MakeJson(self):
        '''returns json file of current status, used for saving.'''
        savedata = {'state':self.state,'energy':self.energy,'MaxNRG':self.MaxNRG,'MaxNRGlvl':self.MaxNRGlvl,'NRGlvl':self.NRGlvl, 'power':self.power}
        return savedata
        
    def LoadJson(self,data):
        for tag in data:
            if tag =="state":self.state = data[tag]
            if tag =="energy":self.energy = data[tag]
            if tag =="MaxNRG":self.MaxNRG = data[tag]
            if tag =="MaxNRGlvl":self.MaxNRGlvl = data[tag]
            if tag =="NRGlvl":self.NRGlvl = data[tag]
            if tag =="power":self.power = data[tag]
        print "Loading Spark: done"
        
    def changeState(self, newstate):
        newstate = newstate%3
        self.state = newstate
        self.image = self.imglst[self.state*2+self.parent.direction][self.frame%len(self.imglst[self.state*2+self.parent.direction])]
        #self.Gimg = self.guilst[newstate]
        
    def Draw(self,surface,relrect):
        if relrect == None:
            #we weren't given a location to defer to
            surface.blit(self.image,self.rect)
        else:
            surface.blit(self.image,(relrect.x+self.xoff,relrect.y+self.yoff,relrect.width,relrect.height))
        #draw gui for debuging TODO
        #draw energy bar
        
    def FixNRG(self, amount = 0.0):
        self.energy += amount
        if amount == 0:
            if self.state == 0:
                self.energy += 3.0
            elif self.state == 2:
                self.energy -= .5
        if self.energy > self.MaxNRG:
            self.NRGlvl += 1
            dif = self.energy-self.MaxNRG
            if self.NRGlvl > self.MaxNRGlvl:
                self.NRGlvl = self.MaxNRGlvl
                self.energy = self.MaxNRG
            else:
                self.energy = dif
        if self.energy < 0:
            self.NRGlvl -= 1
            dif = self.energy
            if self.NRGlvl < 0:
                self.NRGlvl = 0
                self.energy = 0
            else:
                self.energy = self.MaxNRG+dif
        #print "NRGlvl: "+str(self.NRGlvl) + " energy: "+str(self.energy)
        
        
    def update(self, interactables = None):
        while len(self.pastpos)<6:
            self.pastpos.append([self.parent.rect.centerx,self.parent.rect.centery])
        self.frame +=1
        self.FixNRG()
        direction = self.parent.direction
        ppos = self.pastpos.pop(0)
        self.x = ppos[0]
        self.y = ppos[1]
        self.xoff = self.yoff = 0
        self.rect = self.image.get_rect()
        #self.pastpos.append([200,200])
        if self.RS[0]:
            direction = (cmp(self.RS[0],0)-1)/-2
        #if offensive state, must float behind. 
        #if defensive state, rotate image based on right stick, or
        #on left stick if the action command is held
        #if charge state, play the image matching the parent.
        if self.state == 0:
            #charge state
            if self.parent.SparkOnly:
                self.x = self.parent.rect.centerx
                self.y = self.parent.rect.centery
            self.xoff = self.parent.rect.width/2*(1-(1-self.parent.direction)*2)
            self.yoff = -self.rect.height/2
            self.image = self.imglst[self.state*2+direction][self.frame%len(self.imglst[self.state*2+direction])]
            self.rect.center = (self.x,self.y)
            if self.action == 1:
                #indicates button press while in charge form. Do something to the player
                angle = 0
                #if not self.parent.grounded and not self.parent.doublejump and (self.MaxNRG*(self.NRGlvl)+self.energy > FPS*3):
                if not self.parent.grounded:
                    #parent in air, push them in the direction indicated by the right stick or left stick
                    self.AirDash(250)
                elif self.parent.grounded:
                    self.Dash(150)
        elif self.state == 1:
            #offensive
            self.x = self.parent.rect.centerx + self.RS[0]*self.rect.width
            self.y = self.parent.rect.centery + self.RS[1]*self.rect.height
            dx = -self.parent.image.get_width()/3-self.image.get_width()/3
            dy = -self.image.get_height()/2 -10
            vx = 10.0*math.cos(self.frame/21.4)
            vy = 10.0*math.sin(self.frame/33.3)
            if vx == 0.0:
                vx += .1
            if vy == 0.0:
                vy += .1
            if self.action == 1:
                self.FireBullet(10)
                
            self.image = self.imglst[self.state*2+direction][self.frame%len(self.imglst[self.state*2+direction])]
            x = 1
            y = 0.0001
            #if self.RS[0]:x=self.RS[0]
            #if self.RS[1]:y=-self.RS[1]
            if self.RS[0] or self.RS[1]:
                if self.RS[0]:x = self.RS[0]
                if self.RS[1]:y = -self.RS[1]
            else:
                if self.LS[0]:x = self.LS[0]
                if self.LS[1]:y = -self.LS[1]
            self.image = pygame.transform.rotate(self.image.copy(),math.degrees(math.atan((y)/(x))))
            self.rect = self.image.get_rect()
            #self.x = self.parent.x + vx + dx 
            #self.y = self.parent.y + vy + dy
            self.rect.center = (self.x,self.y)
            
        
        elif self.state == 2:
            #defensive
            #if not (action or right stick)
            #
            self.image = self.imglst[self.state*2+direction][self.frame%len(self.imglst[self.state*2+direction])]
            #self.x = self.parent.x
            #self.y = self.parent.y
            self.rect.center = (self.x,self.y)
        if self.MaxNRG*(self.NRGlvl)+self.energy <= 1:
            self.changeState(0)       
        
    def damage(self,obj,amount,s,subtype="physical"):
        if self.state == 2:
            #defensive
            if (amount)*5 > self.MaxNRG*(self.NRGlvl)+self.energy:
                #not enough energy. eat into health
                self.parent.health -= (amount-(self.MaxNRG*(self.NRGlvl)+self.energy))
                self.FixNRG(-(self.MaxNRG*(self.NRGlvl)+self.energy))
            else:
                self.FixNRG(-(amount*10))
            if self.parent.inputs['R1']:
                if subtype in "energy projectile physical":
                    print "reflect this object"
                    try:
                        obj.damage(self.parent,amount,s,subtype)
                    except:
                        pass
            if subtype in "energy":
                self.FixNRG(amount*2)
        else:
            self.parent.health -= amount
            print "spark says objects health is: "+str(self.parent.health)
        
    def FireBullet(self,NRG_used):
        if self.MaxNRG*(self.NRGlvl)+self.energy < NRG_used:
            self.energy = 0
            self.NRGlvl = 0
        else:
            self.energy -= NRG_used
        x=y=0.0
        Constants.SoundBank[7].play()
        if abs(self.RS[0])<=.01 and abs(self.RS[1])<=.01:
            x = self.LS[0]
            y = self.LS[1]
        else:
            x = self.RS[0]
            y = self.RS[1]
        if x == y and y == 0:
            x = 1.0 *(1-self.parent.direction*2)
            y = 0.0
        tot = math.sqrt(x*x+y*y)
        x = x/tot*20.0
        x = int(x/4)*4
        y = y/tot*20.0
        y = int(y/4)*4
        x += self.parent.ddx/5
        y += self.parent.ddy/5
        #if abs(x) > 15 and abs(y)>15:
        #    x = cmp(x,0)*15;y = cmp(y,0)*15
        #elif abs(
        rrx = 1
        rry = 0
        if self.RS[0] or self.RS[1]:
            if self.RS[0]:
                rrx = self.RS[0]
            if self.RS[1]:
                rry = self.RS[1]
        else:
            if self.LS[0]:
                rrx = self.LS[0]
            if self.LS[1]:
                rry = self.LS[1]
        rrx= self.x + self.rect.width/4*rrx
        rry= self.y + self.rect.height/4*rry + 5
        bul = Item.Bullet(rrx,rry,amount=self.power,parent = self.parent.parent,dx=x,dy=y,lifetime=.8)
        bul.SetOrigin(self.parent)
        #bul = Item.Bullet(self.parent.rect.centerx,self.parent.rect.centery,amount=8,parent = self.parent.parent,dx=x,dy=y,lifetime=.8)
        #bul.SetOrigin(self.parent)
        for i in self.parent.parent.world:
            bul.addInteractable(i)
        for i in self.parent.parent.all_updates:
            bul.addInteractable(i)
        bul.Activate(3)
        
    def Dash(self, NRG_used):
        '''puts player x speed at 2x the run speed'''
        if self.MaxNRG*(self.NRGlvl)+self.energy < NRG_used:
            return
        Constants.SoundBank[8].play()
        self.energy -= NRG_used
        self.parent.ddy = -10
        self.CurrentAction = "Dash"
        self.parent.ddx = P_MAXRUNSPEED*cmp(self.parent.ddx,0)
         
    def AirDash(self, NRG_used):
        '''should be executed when possible. whoever calls this must set energy and NRGlvls.'''
        if self.MaxNRG*(self.NRGlvl)+self.energy < NRG_used or (self.parent.doublejump and not self.CanPerformADInfinitely):
            #if we've used this before in the air and can't do it repeatedly.
            print "lol"
            self.parent.doublejump = True
            return
        else:
            Constants.SoundBank[8].play()
            self.energy -= NRG_used
            self.parent.doublejump = True
        if abs(self.RS[0]) <= 0 and abs(self.RS[1]) <= 0:
            #right stick null, use left stick. first option is to air dodge.
            #right stick within deadzone
            x = self.LS[0]; y = self.LS[1];
            hyp = math.sqrt(x*x+y*y) 
            ratio = 1/(hyp+.0000001) #would turn the hypotenuse into a unit vector
            if (x == y) and (y == 0):
                y = -.5
                ratio = 1
            if (x/(self.parent.ddx+.00001) < 0)or (self.parent.ddx == 0) : #different signs or 0 speed
                self.parent.ddx += x * ratio * P_WALKSPEED
            else: #same signs, add on but don't exceed 1.5x P_WALKSPEED
                self.parent.ddx += x * ratio * P_WALKSPEED
            if y/(self.parent.ddy+.00001) < 0: #different signs
                self.parent.ddy += y * ratio * P_MAXFALLSPEED
            else: #same signs, add on but don't exceed 1.5x P_FALLSPEED
                self.parent.ddy += y * ratio * P_MAXFALLSPEED
        else:
            self.parent.ddx = 0
            self.parent.ddy = 0
            x = self.RS[0]; y = self.RS[1]; hyp = math.sqrt(x*x+y*y)
            ratio = 1/(hyp+.0000001) #would turn the hypotenuse into a unit vector
            if (x/(self.parent.ddx+.00001) < 0)or (self.parent.ddx == 0) : #different signs or 0 speed
                self.parent.ddx += x * ratio * 4*P_MAXRUNSPEED
            else: #same signs, add on but don't exceed 1.5x P_MAXRUNSPEED
                self.parent.ddx += x * ratio * 4.5*P_MAXRUNSPEED
            if y/(self.parent.ddy+.00001) < 0: #different signs
                self.parent.ddy += y * ratio * 2 * P_MAXFALLSPEED
            else: #same signs, add on but don't exceed 1.5x P_FALLSPEED
                self.parent.ddy += y * ratio * 2.5* P_MAXFALLSPEED
        
        
    def StoreValues(self, action, LS=[0.0,0.0],RS=[0.0,0.0]):
        '''action is -1,0,1. -1 = release, 0 = no change from previous state.
        1 is press. for LS and RS, they are dicts of two elements each. 
        LS[0] and RS[0] are x values between -1 and 1, likewise for y values
        in LS[1] and RS[1]
        Assume that deadzone is compensated for in the reading device'''
        
        self.action = action
        self.LS[0] = LS[0]
        self.LS[1] = LS[1]
        self.RS[0] = RS[0]
        self.RS[1] = RS[1]
        
        
        
        
        
        
        
