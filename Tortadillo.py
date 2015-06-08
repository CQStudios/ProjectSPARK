import pygame, Constants, DObject, Wall, sys, Spark, math, json, Item, Enemy, AI
from pygame.locals import *
from Constants import *
from DObject import *

WALKSPEED = 2 #6.5 for normal, 10 for charge 
WALKACCEL = .2 #.7 for normal, .45 for charge
MAXRUNSPEED = 10 # 7.5 for normal modes, 13 for charge
RUNACCEL = 1.5 #3.5 for normal2.5for charge
RUNDECEL = 2.5 #5.5 for normal,3.5for charge 

FRICTION = .2 #percent of horizontal acceleration to remove. .2 for normal, .08 for charge

SHORTHOP = -18 #-30
JUMPEXTENSION = -6 #-.8
MAXFALLSPEED = 15
MAXRISESPEED = -20 #-30
AIRRUNACCEL = 1.0 #2.2 for normal .8 for charge 
MAXAIRSPEED = 6 #10 for normal modes, 15 for charge

AIRFRICTION = .02 #.02 for normal, .01 for charge
DEFAULT_HEALTH = 20



class Tortadillo(DObject):
    def __init__(self,x,y,parsurf=[None],img = None,parent = None,isfoc = False):
        DObject.__init__(self,x,y,parentsurface = parsurf)
        self.parent = parent
        self.imglst = []
        self.ACCEL = WALKACCEL
        self.SPEED = WALKSPEED
        #~~~~~~~ movement attributes
        self.dx=0.0
        self.dy=0.0
        self.ddx = 0.0
        self.ddy = 0.0
        self.x = float(x)
        self.y = float(y)
        self.prevpos = [x,y]
        #~~~~~~~ contact flags
        self.contact = False
        self.wasonground = False
        self.grounded = False
        self.direction = 0
        self.crouching = False
        self.crouchcount = 0
        self.prevstate = None
        
        self.health = 20.0
        self.defense = 3.0
        self.power = 5
        self.SeeEnemy = False
        self.Attacking = False
        self.Helpless = False
        
        self.jump = self.doublejump = False
        #self.health = Constants.
        self.JumpLeeWay = 0 #number of frames we were airborn
        #~~~~~~~ image/draw material + collision rect definition
        #imglst holds a dictionary of all the available sprites and animations
        #State represents animation state, not true states.
        self.imglst.append(MIL2("objects/Tortadillo/Idle*.png",5)[0])
        self.imglst.append(MIL2("objects/Tortadillo/Idle*.png",5)[1])
        self.imglst.append(MIL2("objects/Tortadillo/Walk*.png",5)[0])
        self.imglst.append(MIL2("objects/Tortadillo/Walk*.png",5)[1])
        self.imglst.append(MIL2("objects/Tortadillo/Run*.png",5)[0])
        self.imglst.append(MIL2("objects/Tortadillo/Run*.png",5)[1])
        self.imglst.append(MIL2("objects/Tortadillo/Fall*.png",4)[0])
        self.imglst.append(MIL2("objects/Tortadillo/Fall*.png",4)[1])
        self.imglst.append(MIL2("objects/Tortadillo/Attack1*.png",3)[0])
        self.imglst.append(MIL2("objects/Tortadillo/Attack1*.png",3)[1])
        self.imglst.append(MIL2("objects/Tortadillo/Helpless*.png",3)[0])
        self.imglst.append(MIL2("objects/Tortadillo/Helpless*.png",3)[1])
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.frame = 0 #the image itself to use in the current state
        self.state = 0 #idle right. the integer represents the animation states all states are divisible by 2. odds are left facing
        self.image = self.imglst[self.state + self.direction][self.frame]
        self.rect = Rect(0,0,PLW,PLH)
        self.rect.midbottom = [self.x,self.y]
        self.collisionrect = Rect(x,y,36,52)
        self.collisionrect.midbottom = [self.x,self.y]
        self.visionrect = pygame.rect.Rect(x,y,280,140)
        self.armorrect = pygame.rect.Rect(x,y,20,70)
        #~~~~~ other features
        self.collideswith = None
        self.triggerswith = None
        self.inputs = PS3.copy()
        self.PrevInputs = self.inputs.copy()
        self.PumpInput();self.PumpInput()#<set all to 0.0
        self.groundobj = Wall.Wall(x,y)
        self.IsFocus = isfoc
        self.AI = AI.AI_Run_Tortadillo
 
    def changeState(self,num):
        '''num must be divisible by 2'''
        #print "changestate state: "+str(self.state+self.direction)+"  num: "+str(num)
        if (self.state+self.direction)/2 == num/2:
            return False
        self.state = num
        self.frame = 0
    def HorizMotion(self, amnt, useinputs = False):
        '''use this instead of setting it every instance'''
        self.ddx += amnt
        if self.grounded:
            frict = self.ddx*FRICTION*self.groundobj.tract
            if abs(self.ddx) < self.SPEED and useinputs:
                self.ddx += self.inputs[COM['Move']]*self.ACCEL*self.groundobj.tract
                self.ddx -= frict
            
        else:
            frict = self.ddx*AIRFRICTION
            if abs(self.ddx) < MAXAIRSPEED and useinputs:
                self.ddx += self.inputs[COM['Move']]*AIRRUNACCEL
                self.ddx -= frict
                
    def AdjustState(self):
        '''would use self.inputs to determine state. changes states, setting previous state to the one the frame before'''
        cur_frame = 0
        self.frame += 1
        self.prevstate = self.state
        self.ddy += GRAV
        
        self.prevpos = [self.collisionrect.centerx,self.collisionrect.centery]
        if self.grounded and not self.wasonground and self.JumpLeeWay > 4:
            self.changeState(0) #no land animation
        if self.grounded:
            self.JumpLeeWay = 0
        elif not self.grounded:
            #not grounded
            if self.wasonground:
                self.collisionrect.bottom+= self.ddy
            else:
                self.JumpLeeWay += 1
            if self.ddy >= GRAV and (self.JumpLeeWay > 4):
                self.changeState(6) #fall animation
        #adjust x acceleration first
        #can fix positive Y accel to add gravity
        if self.grounded:
            self.ddx -= FRICTION*self.ddx
        else:
            self.ddx -= self.ddx*AIRFRICTION
            if self.ddy > MAXFALLSPEED or self.ddy < MAXRISESPEED:
                self.ddy -= cmp(self.ddy,0)*GRAV
        self.crouching = False
        #if we have attempted movement in the x axis
        if self.inputs[COM['Move']] != 0:
            self.direction = int(cmp(0,self.inputs[COM['Move']])/2.0 + .5) # facing
            #add some acceleration to the left each frame
            if self.grounded:
                if abs(self.ddx) < self.SPEED:
                    self.ddx += self.ACCEL*self.inputs[COM['Move']]*self.groundobj.tract + self.ddx*FRICTION
                elif cmp(self.ddx,0) != cmp(self.inputs[COM['Move']],0):
                    self.ddx += self.ACCEL*self.inputs[COM['Move']]*self.groundobj.tract
                if self.Helpless:
                    self.changeState(10)
                elif self.Attacking:
                    self.changeState(8)
                elif self.SeeEnemy != False:
                    self.changeState(4)
                else:
                    self.changeState(2)
            elif not self.grounded:
                if abs(self.ddx) < MAXAIRSPEED:
                    self.ddx += AIRRUNACCEL*self.inputs[COM['Move']]
                else:
                    self.ddx -= self.ddx*AIRFRICTION
        elif self.inputs[COM['Move']] == 0:
            if self.grounded:
                self.changeState(0)
            else:
                self.ddx -= self.ddx*AIRFRICTION
            if self.wasonground and not self.grounded:
                pass #TODO, do we need to change states?
                
        if self.state/2 in [0,1,2,3,4,5]:
            self.frame = self.frame%len(self.imglst[self.state+self.direction])
        elif self.frame/len(self.imglst[self.state+self.direction]):
            self.frame = 0
            num = 0
            if self.state/2 in [3,9]:
                num = 0
            elif self.state/2 in [1,6]:
                num = self.state+2
            self.changeState(num)
        self.wasonground = self.grounded
        self.grounded = False
        
    def touchground(self,touchedobj):
        self.grounded = True
        self.contact = True
        self.groundobj = touchedobj
        
    def Draw(self,surf, relrect = None):
        LELx = self.groundobj.rect.x - self.rect.x
        LELy = self.groundobj.rect.y - self.rect.y        
        if relrect == None:
            #we weren't given a location to defer to
            surf.blit(self.image,self.rect)
        else:
            surf.blit(self.image,relrect)
            #pygame.draw.rect(surf,(200,200,100),(relrect.left+LELx,relrect.top+LELy,TLWDTH,TLHGHT),4)        
        
        
    def setCollideables(self,spritegroups):
        self.collideswith = spritegroups
    def setTriggers(self,list_of_objects):
        self.triggerswith = list_of_objects
    def addTrigger(self,DObjectObj):
        self.triggerswith.append(DObjectObj)
    def addCollideable(self,DObjectObj):
        self.collideswith.append(DObjectObj)
        
    def damage(self,obj,amount,stun,subtype):
        if subtype in "physical":
            return
        if obj.collisionrect.colliderect(self.armorrect):
            self.health -= float(amount/self.defense)
        else:
            self.health -= amount
            
        print "Tortadillo health is: "+str(self.health)
        if self.health <= 0:
            if self in self.parent.all_updates:
                self.parent.all_updates.remove(self)
            for i in self.parent.all_layers:
                if self in i:
                    i.remove(self)
    
    def update(self):
        '''Use PumpInput before calling this method, otherwise there will be no user input. When the game is paused, update should never be called.'''
        if not self.IsFocus:
            self.AI(self)
        self.dy = .01
        self.dx = 0
        self.AdjustState()
        self.image = self.imglst[self.state+self.direction][self.frame].convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.collisionrect.midbottom
        #physics portion
        self.dx+= self.ddx
        self.collisionrect.right+=math.floor(self.dx+.5)
        self.collide(self.dx,0)
        #now test for contact
        self.dy += self.ddy 
        self.collisionrect.bottom += self.dy
        self.collide(0, self.dy)
        #set image rect data
        #self.collisionrect.midbottom = (self.x,self.y)
        self.x = self.collisionrect.centerx
        self.y = self.collisionrect.centery
        self.armorrect.centerx = self.collisionrect.centerx+(self.direction*2-1)*(self.collisionrect.width*2/3)
        self.visionrect.centerx = self.collisionrect.centerx+(1-self.direction*2)*self.visionrect.width/2
        self.armorrect.centery = self.rect.centery
        self.visionrect.bottom = self.collisionrect.bottom
        if self.SeeEnemy != False:
            print self.SeeEnemy
            self.ACCEL = RUNACCEL
            self.SPEED = MAXRUNSPEED
        else:
            self.ACCEL = WALKACCEL
            self.SPEED = WALKSPEED
        
        
    def collide(self, movx, movy):
        self.SeeEnemy = False
        for o in self.parent.world:
            if not o.CanCollide:
                continue
            if self.collisionrect.colliderect(o):
                if ('Wall' in str(type(o))):
                    o.act(self,movx,movy)
                else:
                    print "Tortadillo failed. no non-wall objects should be around."
        for o in self.parent.updates:
            if not o.CanCollide or o == self:
                continue
            if self.collisionrect.colliderect(o):
                if (str(type(o))=="<class 'Player.Player'>"):
                    o.act(self,movx,movy)
                    o.damage(self,self.power,Constants.FPS/2,'physical')
            if self.visionrect.colliderect(o):
                print 'visionrect hit: '+ str(type(o))
                if 'Player' in str(type(o)):
                    self.SeeEnemy = o
    def PumpInput(self,commands={None}):
        '''store commands for use in the update method.
        check Constants.py to understand the format
        stores relevant info in children'''
        self.PrevInputs = self.inputs.copy()
        for i in self.inputs:
            self.inputs[i]= 0.0
        for element in commands:
            if element in self.inputs:
                self.inputs[element] = commands[element]
        
    def act(self, obj, dx,dy):
        '''default collision between us and an object.'''
        if 'Player' in str(type(obj)):
            obj.damage(self,self.power)
