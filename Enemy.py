import pygame, Constants, DObject, Wall, sys, Spark, math, json, Item
from pygame.locals import *
from Constants import *
from DObject import *


class Enemy(DObject):
    def __init__(self,x,y,parsurf=[None],img = None,parent = None):
        DObject.__init__(self,x,y,parentsurface = parsurf)
        self.parent = parent
        self.health = 20
        self.imglst = []
        #~~~~~~~ movement attributes
        self.dx=0.0
        self.dy=0.0
        self.ddx = 0.0
        self.ddy = 0.0
        self.x = float(x)
        self.y = float(y)
        self.prevpos = [0.0,0.0]
        #~~~~~~~ contact flags
        self.contact = False
        self.jump = True
        self.wasonground = False
        self.doublejump = True
        self.grounded = False
        self.direction = 0
        self.crouching = False
        self.crouchcount = 0
        self.prevstate = None
        #self.health = Constants.
        self.JumpLeeWay = 0 #number of frames we were airborn
        #~~~~~~~ image/draw material + collision rect definition
        #imglst holds a dictionary of all the available sprites and animations
        #State represents animation state, not true states.
        self.imglst.append(MIL2("player/MaiIdle*.png",5)[0])
        self.imglst.append(MIL2("player/MaiIdle*.png",5)[1])
        self.imglst.append(MIL2("player/CrouchStart*.png",4)[0])
        self.imglst.append(MIL2("player/CrouchStart*.png",4)[1])
        self.imglst.append(MIL2("player/CrouchHold*.png",4)[0])
        self.imglst.append(MIL2("player/CrouchHold*.png",4)[1])
        self.imglst.append(MIL2("player/CrouchRelease*.png",4)[0])
        self.imglst.append(MIL2("player/CrouchRelease*.png",4)[1])
        self.imglst.append(MIL2("player/Walk*.png",3)[0])
        self.imglst.append(MIL2("player/Walk*.png",3)[1])
        self.imglst.append(MIL2("player/Run*.png",5)[0])
        self.imglst.append(MIL2("player/Run*.png",5)[1])
        self.imglst.append(MIL2("player/JumpStart*.png",1)[0])
        self.imglst.append(MIL2("player/JumpStart*.png",1)[1])
        self.imglst.append(MIL2("player/JumpRise*.png",4)[0])
        self.imglst.append(MIL2("player/JumpRise*.png",4)[1])
        self.imglst.append(MIL2("player/Fall*.png",4)[0])
        self.imglst.append(MIL2("player/Fall*.png",4)[1])
        self.imglst.append(MIL2("player/Land*.png",1)[0])
        self.imglst.append(MIL2("player/Land*.png",1)[1])
        self.imglst.append(MIL2("player/Hurt*.png",4)[0])
        self.imglst.append(MIL2("player/Hurt*.png",4)[1])
        self.imglst.append(MIL2("player/Attack1*.png",3)[0])
        self.imglst.append(MIL2("player/Attack1*.png",3)[1])
        self.imglst.append(MIL2("player/Attack2*.png",3)[0])
        self.imglst.append(MIL2("player/Attack2*.png",3)[1])
        self.frame = 0 #the image itself to use in the current state
        self.state = 0 #idle right. the integer represents the animation states all states are divisible by 2. odds are left facing
        self.image = self.imglst[self.state + self.direction][self.frame]
        self.rect = Rect(0,0,PLW,PLH)
        self.rect.midbottom = [self.x,self.y]
        self.collisionrect = Rect(x,y,36,52)
        self.collisionrect.midbottom = [self.x,self.y]
        #~~~~~ other features
        self.collideswith = None
        self.triggerswith = None
        self.spark = Spark.Spark(self)
        self.inputs = PS3.copy()
        self.PrevInputs = self.inputs.copy()
        self.PumpInput();self.PumpInput()#<set all to 0.0
        self.groundobj = Wall.Wall(x,y)
        
    def AI(self):
        '''base AI'''
        o=x=sq=tr=lsx=lsy=rsx=rsy=l1=l2=r1=r2=0
        if self.groundobj != None:
            o = 1
        self.PumpInput({"L1":l1,"L2":l2,"R1":r1,"R2":r2,"X":x,"O":o,"Tri":tr,"Sqr":sq,"LSX":lsx,"LSY":lsy,"RSX":rsx,"RSY":rsy})
        
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
            frict = self.ddx*P_FRICTION*self.groundobj.tract
            if abs(self.ddx) < P_MAXRUNSPEED and useinputs:
                self.ddx += self.inputs['LSX']*P_RUNACCEL*self.groundobj.tract
                self.ddx -= frict
            
        else:
            frict = self.ddx*P_AIRFRICTION
            if abs(self.ddx) < P_MAXAIRSPEED and useinputs:
                self.ddx += self.inputs['LSX']*P_AIRRUNACCEL
                self.ddx -= frict
                
    def AdjustState(self):
        '''would use self.inputs to determine state. changes states, setting previous state to the one the frame before'''
        cur_frame = 0
        self.frame += 1
        self.prevstate = self.state
        self.ddy += GRAV
        if self.spark.CurrentAction == "Dash":
            self.spark.CAcounter+=1
            if self.spark.CAcounter > 10:
                self.spark.CAcounter = 0
                self.spark.CurrentAction = "None"
            else:
                self.ddx = cmp(self.inputs['LSX'],0)*P_MAXRUNSPEED*3
        if self.JumpLeeWay >=4:
            self.jump = True
        self.prevpos = [self.collisionrect.centerx,self.collisionrect.centery]
        if self.grounded and not self.wasonground and self.JumpLeeWay > 4:
            #we weren't on the ground, but now we are. Land animation
            self.changeState(18)
            #print "land animation trigger"
            #self.wasonground = True
        if self.grounded:
            self.JumpLeeWay = 0
        elif not self.grounded:
            #not grounded
            if self.wasonground:
                self.collisionrect.bottom+= self.ddy
            else:
                self.JumpLeeWay += 1
                
            if self.ddy >= 0 and (self.JumpLeeWay > 4):
                #falling off of something
                self.changeState(16)
                #print "falling trigger"
            
        #Landing animation goes to idle when done, blocks movement
        if self.state/2==9:
            #print "landing animation" + str(self.frame)
            if not (self.frame/len(self.imglst[self.state+self.direction]))>=1:    
                #return is needed. but we need to handle motion.
                self.HorizMotion(self.inputs['LSX'])
                return
            else:
                self.changeState(0)
        
        #adjust x acceleration first
        #can fix positive Y accel to add gravity
        if self.grounded:
            #apply friction
            self.ddx -= P_FRICTION*self.ddx
        else:
            self.ddx -= self.ddx*P_AIRFRICTION
            if self.ddy > P_MAXFALLSPEED or self.ddy < P_MAXRISESPEED:
                self.ddy -= cmp(self.ddy,0)*GRAV
                
        #if O button is held, jump where possible JUMP INPUT        
        if self.inputs["O"]:
            self.crouching = False
            if self.grounded or self.JumpLeeWay < 4:
                if not self.jump:
                    self.ddy = P_SHORTHOP #we add because it should be 0 beforehand
                    x = self.inputs['LSX']
                    if cmp(x*self.ddx,0) < 0:
                        #if opposite dirs, slow
                        self.ddx += x*P_WALKSPEED
                        
                self.jump=True;self.grounded=False;self.changeState(12)
            elif self.ddy < 0 and not self.doublejump:
                #currently burning first jump. increase effect of jump.
                self.dy += P_JUMPEXTENSION
        #otherwise if I'm crouching
        elif self.inputs['LSY'] > .75:
            if self.grounded:
                cur_frame = self.frame
                self.crouching = True
                self.ddx -= self.ddx*P_FRICTION*2 #retain 80% x accel per frame
                self.crouchcount += 1
        else:
            self.crouching = False
        if not self.crouching:
            self.crouchcount = 0
        #if we have attempted movement in the x axis
        if self.inputs['LSX'] != 0:
            self.direction = int(cmp(0,self.inputs['LSX'])/2.0 + .5) # facing
            #add some acceleration to the left each frame
            if self.grounded:
                if abs(self.ddx) < P_MAXRUNSPEED:
                    self.ddx += P_RUNACCEL*self.inputs['LSX']*self.groundobj.tract + self.ddx*P_FRICTION
                elif cmp(self.ddx,0) != cmp(self.inputs['LSX'],0):
                    #different directions, we can reduce.
                    self.ddx += P_RUNACCEL*self.inputs['LSX']*self.groundobj.tract
                    #print "Was past max speed on ground - moving back"
                #variable acceleration based on stick position. 
                #max is like 2 or something, but we know we're running. 
                #set to run animation
                self.changeState(8)
            elif not self.grounded:
                #aerial control
                if abs(self.ddx) < P_MAXAIRSPEED:
                    self.ddx += P_AIRRUNACCEL*self.inputs['LSX']
                else:
                    self.ddx -= self.ddx*P_AIRFRICTION
        elif self.inputs['LSX'] == 0:
            if self.grounded:
                self.changeState(0)
            else:
                self.ddx -= self.ddx*P_AIRFRICTION
            if self.wasonground and not self.grounded:
                pass #TODO, do we need to change states?
        if self.crouching and self.state not in [2,4]:
            self.changeState(2);
            self.frame = cur_frame
        #~~~~~~~~``ADJUSTING BASED ON INPUTS IS DONE``~~~~~~~~~~~~~~~~        
        #now we adjust animations based on frame data
        #idle,walk,run,crouchhold,jumprise,hurt and fall have cycling frames.
        #jumpstart, land, must move to a different animation when done
        if self.state/2 in [0,2,4,5,7,8,10]:
            self.frame = self.frame%len(self.imglst[self.state+self.direction])
            if self.ddy > 0 and self.state/2 == 7:
                #jump rise becomes fall after y accel > 0
                self.changeState(16)
        elif self.frame/len(self.imglst[self.state+self.direction]):
            self.frame = 0
            num = 0
            if self.state/2 in [3,9]:
                num = 0
            elif self.state/2 in [1,6]:
                num = self.state+2
            self.changeState(num)
        #this should solve frame adjustment + state change.
        #print "grounded: \t"+str(self.grounded)
        #print "wasgrounded: \t"+str(self.wasonground)
        #print "jump: \t\t"+str(self.jump)
        self.wasonground = self.grounded
        self.grounded = False
        #self.wasonground = False
        
    def touchground(self,touchedobj):
        self.grounded = True
        self.contact = True
        self.jump = self.doublejump = False
        self.groundobj = touchedobj
        
    def Draw(self,surf, relrect = None):
        pygame.draw.rect(self.image,(100,100,100),self.collisionrect,2)
        rx = self.collisionrect.left-self.rect.left
        tx = self.rect.right-self.collisionrect.right+self.collisionrect.width
        ry = self.collisionrect.top-self.rect.top
        #pygame.draw.line(self.image,(200,200,200),(rx,ry),(tx,ry),3)
        LELx = self.groundobj.rect.x - self.rect.x
        LELy = self.groundobj.rect.y - self.rect.y
        if relrect == None:
            #we weren't given a location to defer to
            surf.blit(self.image,self.rect)
        else:
            surf.blit(self.image,relrect)
            #pygame.draw.rect(surf,(200,200,100),(relrect.left+LELx,relrect.top+LELy,TLWDTH,TLHGHT),4)
        self.spark.Draw(surf,relrect)
        
        
        
        
    def setCollideables(self,spritegroups):
        self.collideswith = spritegroups
    def setTriggers(self,list_of_objects):
        self.triggerswith = list_of_objects
    def addTrigger(self,DObjectObj):
        self.triggerswith.append(DObjectObj)
    def addCollideable(self,DObjectObj):
        self.collideswith.append(DObjectObj)
    
    def checktrigger(self):
        if not self.crouching or self.crouchcount > 0:
            return
        for o in self.triggerswith:
            dx = o.rect.centerx - self.rect.centerx
            dy = o.rect.bottom - self.rect.bottom
            if abs(dx) > o.radius or abs(dy) > o.radius:
                continue
            d = dx*dx+dy*dy
            print "d^2 is :" + str(d)
            d = math.sqrt(d)
            print "d is :"+str(d)
            print str(self.collisionrect.centerx) + ","+str(self.collisionrect.bottom)
            print str(o.rect.centerx) + ","+str(o.rect.bottom)
            
            if d < o.radius:
                o.trigger(self)
        
    def update(self):
        '''Use PumpInput before calling this method, otherwise there will be no user input. When the game is paused, update should never be called.'''
        self.AI()
        self.dy = .01
        self.dx = 0
        self.AdjustState()
        self.image = self.imglst[self.state+self.direction][self.frame].convert_alpha()
        #physics portion
        self.dx+= self.ddx
        #self.x += math.floor(self.dx+.5)
        self.collisionrect.right+=math.floor(self.dx+.5)
        self.collide(self.dx,0)
        self.rect.midbottom = self.collisionrect.midbottom
        #now test for contact
        self.dy += self.ddy 
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if not self.contact:
            #in air
            self.jump = True
        if not self.grounded:
            self.jump = True
            if self.contact == True:
                self.jump = False
                self.doublejump = False
        #self.y += self.dy        
        self.collisionrect.bottom += self.dy
        self.collide(0, self.dy)
        #print self.contact
        #print "````````````"

        
        #set image rect data
        #self.collisionrect.midbottom = (self.x,self.y)
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.collisionrect.midbottom
        self.x = self.rect.left
        self.y = self.rect.top
        
        #end fix 
        #if self.contact == False:
        #    self.grounded = False
        #    self.wasonground = False #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.spark.update()
        if self.inputs['Str'] and not self.PrevInputs['Str']:
            self.parent.GUI.Activate()
        
        
    def collide(self, movx, movy):
        for o in self.collideswith:
            
            if not o.CanCollide:
                continue
            if self.collisionrect.colliderect(o):
                if (str(type(o))in["<class 'Wall.Wall'>","<class 'Wall.MovePlat'>"]):
                    o.act(self,movx,movy)
                    #print "should do stuff"
                elif (str(type(o))=="<class 'Player.Player'>"):
                    o.act(self,movx,movy)
                    #print "should do stuff"
                else:
                    #print "fail"
                    pass
        
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
                
        action = self.inputs['R1']-self.PrevInputs['R1']
        if self.inputs['R1']==0:
            action = 0
        if self.inputs['L2']>self.PrevInputs['L2']:
            self.spark.changeState(self.spark.state-1)
        if self.inputs['R2']>self.PrevInputs['R2']:
            self.spark.changeState(self.spark.state+1)
        self.spark.StoreValues(action,[self.inputs['LSX'],self.inputs['LSY']],[self.inputs['RSX'],self.inputs['RSY']])
        
        
    def act(self, obj):
        #TODO fix this. this shouldn't be collisions
        #it should be called when you crouch next to something
        #you go through crouch animation, but you only check at the state change into
        #the crouch startup. if something has the "HasCrouchAction" flag, call it's act()
        '''default collision between us and an object.'''
        if obj.flags[moveable]:
            #if an object is moveable, you can push it.
            dx = float((obj.rect.centerx - self.rect.centerx)/obj.rect.width)
            #if on left, is +.
            dy = float((obj.rect.centery - self.rect.centery)/obj.rect.height)
            #if on top, is +.
            obj.dx
            if abs(dx)>abs(dy):
                #move based on dx
                if dx<0:
                    obj.rect.left = self.rect.right
                else:
                    obj.rect.right = self.rect.left
            else:
                if dy<0:
                    obj.rect.top = self.rect.bottom
                else:
                    obj.rect.bottom = self.rect.top
        
