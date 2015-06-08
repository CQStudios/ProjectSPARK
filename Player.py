import pygame, Constants, DObject, Wall, sys, Spark, math, json, Item, Enemy, AI,Camera
from pygame.locals import *
from Constants import *
from DObject import *


class Player(DObject):
    def __init__(self,x,y,parsurf=[None],img = None,parent = None,isfoc = False):
        DObject.__init__(self,x,y,parentsurface = parsurf)
        self.parent = parent
        self.health = self.MAX_HEALTH = 50.0
        self.defense = 10.0
        self.imglst = []
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
        self.MakeImglst()
        self.frame = 0 #the image itself to use in the current state
        self.state = 0 #idle right. the integer represents the animation states all states are divisible by 2. odds are left facing
        self.image = self.imglst[self.state + self.direction][self.frame]
        self.rect = Rect(0,0,PLW,PLH)
        self.rect.midbottom = [self.x,self.y]
        self.collisionrect = Rect(x,y,36,52)
        self.collisionrect.midbottom = [self.x,self.y]
        #~~~~~ other features
        self.collideswith = []
        self.triggerswith = []
        self.spark = Spark.Spark(self)
        self.inputs = PS3.copy()
        self.PrevInputs = self.inputs.copy()
        self.PumpInput();self.PumpInput()#<set all to 0.0
        self.groundobj = Wall.Wall(x,y)
        self.IsFocus = isfoc
        self.SparkOnly = False
        self.AI = AI.AI_Run
        self.stun = 0
    def MakeImglst(self,prefix = ''):
        self.imglst = []
        self.imglst.append(MIL2("player/"+str(prefix)+"MaiIdle*.png",5)[0])
        self.imglst.append(MIL2("player/"+str(prefix)+"MaiIdle*.png",5)[1])
        self.imglst.append(MIL2("player/"+str(prefix)+"CrouchStart*.png",2)[0])
        self.imglst.append(MIL2("player/"+str(prefix)+"CrouchStart*.png",2)[1])
        self.imglst.append(MIL2("player/"+str(prefix)+"CrouchHold*.png",4)[0])
        self.imglst.append(MIL2("player/"+str(prefix)+"CrouchHold*.png",4)[1])
        self.imglst.append(MIL2("player/"+str(prefix)+"CrouchRelease*.png",2)[0])
        self.imglst.append(MIL2("player/"+str(prefix)+"CrouchRelease*.png",2)[1])
        self.imglst.append(MIL2("player/"+str(prefix)+"Walk*.png",7)[0])
        self.imglst.append(MIL2("player/"+str(prefix)+"Walk*.png",7)[1])
        self.imglst.append(MIL2("player/"+str(prefix)+"Run*.png",3)[0])
        self.imglst.append(MIL2("player/"+str(prefix)+"Run*.png",3)[1])
        self.imglst.append(MIL2("player/"+str(prefix)+"JumpStart*.png",1)[0])
        self.imglst.append(MIL2("player/"+str(prefix)+"JumpStart*.png",1)[1])
        self.imglst.append(MIL2("player/"+str(prefix)+"JumpRise*.png",2)[0])
        self.imglst.append(MIL2("player/"+str(prefix)+"JumpRise*.png",2)[1])
        self.imglst.append(MIL2("player/"+str(prefix)+"Fall*.png",4)[0])
        self.imglst.append(MIL2("player/"+str(prefix)+"Fall*.png",4)[1])
        self.imglst.append(MIL2("player/"+str(prefix)+"Land*.png",1)[0])
        self.imglst.append(MIL2("player/"+str(prefix)+"Land*.png",1)[1])
        self.imglst.append(MIL2("player/"+str(prefix)+"Hurt*.png",4)[0])
        self.imglst.append(MIL2("player/"+str(prefix)+"Hurt*.png",4)[1])
    def SAVE(self,path,filename):
        ''' Save self as a json file named 'filename' in the given 'path'. '''
        x=y=0
        if self.groundobj:
            x=self.groundobj.rect.centerx
            y=self.groundobj.rect.top
        data = {'x':x,'y':y,'spark':self.spark.MakeJson(),'path':self.parent.path,'filename':self.parent.filename,'health':self.health,'MaxHealth':self.MAX_HEALTH,'Story':Constants.P_STORY_PROGRESSION}
        with open(path+filename, 'w') as savefile:
            json.dump(data, savefile)
            
    def LOAD(self,path,filename):
        '''This *should* set the CUR_LEVEL and global values for the program operating this instance of the player.'''
        dfile = json.load(open(path+filename))
        lpath = 'yolo'
        lfile = 'yolo'
        x = y = 0
        for element in dfile:
            if element == 'x':
                x = dfile[element]
            elif element == 'y':
                y = dfile[element]
            elif element == 'spark':
                self.spark.LoadJson(dfile[element])
            elif element == 'health':
                self.health = dfile[element]
            elif element == 'MaxHealth':
                self.MAX_HEALTH = dfile[element]
            elif element == 'path':
                lpath = dfile[element]
            elif element == 'filename':
                lfile = dfile[element]
            elif element == 'Story':
                Constants.P_STORY_PROGRESSION = dfile[element]
        print "old: "+self.parent.path+self.parent.filename + " ~ new: "+lpath+lfile
        self.parent.SetLevel(self,lpath,lfile)
        self.parent.currentsavefile = [path,filename]
        self.collisionrect.midbottom = (x,y)
        
        
    def changeState(self,num):
        '''num must be divisible by 2'''
        #print "changestate state: "+str(self.state)+"  num: "+str(num)
        if (self.state+self.direction)/2 == num/2:
            return False
        if self.state == 18 and self.inputs[COM['Crouch']] > .75:
            self.state = 4
            self.frame = 0
            self.crouching = True
            return
        self.state = num
        self.frame = 0
    def HorizMotion(self, amnt, useinputs = False):
        '''use this instead of setting it every instance'''
        self.ddx += amnt
        if self.grounded:
            frict = self.ddx*P_FRICTION*self.groundobj.tract
            if abs(self.ddx) < P_WALKSPEED and useinputs:
                self.ddx += self.inputs[COM['Move']]*P_WALKACCEL*self.groundobj.tract
                self.ddx -= frict
                #if self.state/2 == 5:
                #    self.changeState(8)
            elif abs(self.ddx) < P_MAXRUNSPEED and useinputs:
                self.ddx += self.inputs[COM['Move']]*P_RUNACCEL*self.groundobj.tract
                self.ddx -= frict
                #if self.state/2 == 4:
                #    self.changeState(10)
        else:
            frict = self.ddx*P_AIRFRICTION
            if abs(self.ddx) < P_MAXAIRSPEED and useinputs:
                self.ddx += self.inputs[COM['Move']]*P_AIRRUNACCEL
                self.ddx -= frict
                
    def AdjustState(self):
        '''would use self.inputs to determine state. changes states, setting previous state to the one the frame before'''
        cur_frame = 0
        self.frame += 1
        self.prevstate = self.state
        if not Constants.ENABLENOGRAV:
            self.ddy += GRAV
        if self.spark.CurrentAction == "Dash":
            self.spark.CAcounter+=1
            if self.spark.CAcounter > 10:
                self.spark.CAcounter = 0
                self.spark.CurrentAction = "None"
            else:
                self.ddx = cmp(self.inputs[COM['Move']],0)*P_MAXRUNSPEED*3
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
        else:
            #not grounded
            if self.wasonground:
                self.collisionrect.bottom+= self.ddy
            else:
                self.JumpLeeWay += 1
                
            if self.ddy >= 0 and (self.JumpLeeWay > 4):
                #falling off of something
                self.changeState(16)
                #print "falling trigger"
            elif self.ddy <= 4 and (self.JumpLeeWay > 4):
                #falling off of something
                self.changeState(14)
                #print "falling trigger"
        #Landing animation goes to idle when done, blocks movement
        if self.state/2==9:
            #print "landing animation" + str(self.frame)
            if self.crouching:
                self.changeState(4)
                return
            if not (self.frame/len(self.imglst[self.state+self.direction]))>=1:    
                #return is needed. but we need to handle motion.
                self.HorizMotion(self.inputs[COM['Move']])
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
          
        #if jump button is held, jump where possible JUMP INPUT        
        if self.inputs[COM['Jump']]:
            self.crouching = False
            if self.grounded or self.JumpLeeWay < 4:
                if not self.jump:
                    #Constants.SoundBank[8].play() sound is stupid on this. :/
                    self.ddy = P_SHORTHOP #we add because it should be 0 beforehand
                    x = self.inputs[COM['Move']]
                    if cmp(x*self.ddx,0) < 0:
                        #if opposite dirs, slow
                        self.ddx += x*P_WALKSPEED
                        
                self.jump=True;self.grounded=False;self.changeState(12)
            elif self.ddy < 0 and not self.doublejump:
                #currently burning first jump. increase effect of jump.
                self.dy += P_JUMPEXTENSION
        #otherwise if I'm crouching
        elif self.inputs[COM['Crouch']] > .75:
            if self.grounded:
                cur_frame = self.frame
                self.crouching = True
                loc = self.collisionrect.midbottom
                self.collisionrect.height = 25
                self.collisionrect.midbottom = loc
                self.ddx -= self.ddx*P_FRICTION*2 #retain 80% x accel per frame
                self.crouchcount += 1
        else:
            self.crouching = False
        if not self.crouching:
            loc = self.collisionrect.midbottom
            self.collisionrect.height = 52
            self.collisionrect.midbottom = loc
            self.crouchcount = 0
            
        #if we have attempted movement in the y axis
        if Constants.ENABLENOGRAV:
            self.ddy -= self.ddy*P_AIRFRICTION
            if abs(self.ddy) < P_MAXAIRSPEED:
                self.ddy += P_AIRRUNACCEL*self.inputs[COM['Crouch']]
                
        #if we have attempted movement in the x axis
        if self.inputs[COM['Move']] != 0:
            self.direction = int(cmp(0,self.inputs[COM['Move']])/2.0 + .5) # facing
            #add some acceleration to the left each frame
            if self.grounded:
                if abs(self.ddx) < P_MAXRUNSPEED:
                    if self.ddx < P_WALKSPEED:
                        self.ddx += P_WALKACCEL*self.inputs[COM['Move']]*self.groundobj.tract + self.ddx*P_FRICTION
                        self.ddx += P_FRICTION*abs(self.ddx)*self.inputs[COM['Move']]
                    else:
                        self.ddx += P_RUNACCEL*self.inputs[COM['Move']]*self.groundobj.tract + self.ddx*P_FRICTION
                elif cmp(self.ddx,0) != cmp(self.inputs[COM['Move']],0):
                    #different directions, we can reduce.
                    self.ddx += P_RUNACCEL*self.inputs[COM['Move']]*self.groundobj.tract
                    #print "Was past max speed on ground - moving back"
                #variable acceleration based on stick position. 
                #max is like 2 or something, but we know we're running. 
                #set to run animation
                
            elif not self.grounded:
                #aerial control
                if abs(self.ddx) < P_MAXAIRSPEED:
                    self.ddx += P_AIRRUNACCEL*self.inputs[COM['Move']]
                else:
                    self.ddx -= self.ddx*P_AIRFRICTION
        elif self.inputs[COM['Move']] == 0:
            if self.grounded:
                if self.state/2 not in [1,2,3]:
                    self.changeState(0)
            else:
                self.ddx -= self.ddx*P_AIRFRICTION
            if self.wasonground and not self.grounded:
                pass #TODO, do we need to change states?
        if self.crouching and self.state not in [2,4,6]:
            self.changeState(2);
            self.frame = cur_frame
        elif not self.crouching:
            if self.state == 4:
                self.changeState(6)
        #~~~~~~~~``ADJUSTING BASED ON INPUTS IS DONE``~~~~~~~~~~~~~~~~        
        #now we adjust animations based on frame data
        #idle,walk,run,crouchhold,jumprise,hurt and fall have cycling frames.
        #jumpstart, land, must move to a different animation when done
        if self.state/2 in [0,2,4,5,7,8,10]:
            self.frame = self.frame%len(self.imglst[self.state+self.direction])
            if self.ddy > 0 and self.state/2 == 7:
                #jump rise becomes fall after y accel > 0
                self.changeState(16)
            if self.state/2 == 0:
                if abs(self.ddx) > .5:
                    self.changeState(8)
        if self.state/2 == 4 and abs(self.ddx)>P_WALKSPEED:
            self.changeState(10)
        elif self.state/2 == 5 and abs(self.ddx)<P_WALKSPEED:
            print "setting to walk"
            self.changeState(8)
            print "finished"
        if self.state ==6 and not self.grounded:
            self.changeState(16)   
        if self.frame/len(self.imglst[self.state+self.direction]):
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
        #print "state: \t\t"+str(self.state)
        self.wasonground = self.grounded
        self.grounded = False
        
    def touchground(self,touchedobj):
        self.grounded = True
        self.contact = True
        self.jump = self.doublejump = False
        self.groundobj = touchedobj
        
    def Draw(self,surf, relrect = None):
        LELx = self.groundobj.rect.x - self.rect.x
        LELy = self.groundobj.rect.y - self.rect.y
        if self.SparkOnly:
            self.spark.Draw(surf,Camera.RelRect(self.spark,Constants.CUR_CAMERA))
            return
        self.spark.Draw(surf,Camera.RelRect(self.spark,Constants.CUR_CAMERA))
        if relrect == None:
            #we weren't given a location to defer to
            if self.stun <=0:
                surf.blit(self.image,(self.rect.x-10,self.rect.y,self.rect.width,self.rect.height))
                surf.blit(self.image,(self.rect.x+10,self.rect.y,self.rect.width,self.rect.height))
            surf.blit(self.image,self.rect)
            
        else:
            if self.stun <=0:
                surf.blit(self.image,(relrect.x-10, relrect.y,relrect.width,relrect.height))
                surf.blit(self.image,(relrect.x+10, relrect.y,relrect.width,relrect.height))
            surf.blit(self.image,relrect)
            #pygame.draw.rect(surf,(200,200,100),(relrect.left+LELx,relrect.top+LELy,TLWDTH,TLHGHT),4)
        if self.health>self.MAX_HEALTH:
            self.health= self.MAX_HEALTH
            
        
        
        
        
    def setCollideables(self,spritegroups):
        self.collideswith = spritegroups
    def setTriggers(self,list_of_objects):
        self.triggerswith = list_of_objects
    def addTrigger(self,DObjectObj):
        self.triggerswith.append(DObjectObj)
    def addCollideable(self,DObjectObj):
        self.collideswith.append(DObjectObj)
        
    def damage(self,obj,amount,s,sub):
        if self.stun >= 0:
            self.spark.damage(obj,amount,s,sub)
            self.stun = -s
        if self.health <= 0:
            if self in self.parent.all_updates:
                self.parent.all_updates.remove(self)
            for i in self.parent.all_layers:
                if self in i:
                    i.remove(self)
        
    def checktrigger(self):
        if not self.crouching or self.crouchcount > 0:
            return
        for o in self.triggerswith:
            dx = o.rect.centerx - self.rect.centerx
            dy = o.rect.bottom - self.rect.bottom
            if abs(dx) > o.radius or abs(dy) > o.radius:
                continue
            d = dx*dx+dy*dy
            #print "d^2 is :" + str(d)
            d = math.sqrt(d)
            #print "d is :"+str(d)
            #print str(self.collisionrect.centerx) + ","+str(self.collisionrect.bottom)
            #print str(o.rect.centerx) + ","+str(o.rect.bottom)
            
            if d < o.radius:
                o.trigger(self)
                      
    
    def update(self):
        '''Use PumpInput before calling this method, otherwise there will be no user input. When the game is paused, update should never be called.'''
        #print self
        if not self.IsFocus:
            self.AI(self)
        self.stun += 1
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
        if self.inputs[COM['Pause']] and not self.PrevInputs[COM['Pause']]:
            self.parent.GUI.Activate()
        if self.inputs['Sel'] and not self.PrevInputs['Sel']:
            e = Player(self.x,self.y,parent = self.parent)
            e.collideswith = self.collideswith
            self.parent.all_layers[2].add(e)
            self.parent.all_updates.append(e)
        if self.inputs['DD'] and not self.PrevInputs['DD']:
            Constants.P_STORY_PROGRESSION['Main'][0] += 1
            print Constants.P_STORY_PROGRESSION
            #self.groundobj.kill()
            #if self.groundobj in self.parent.all_world:
            #    self.parent.all_world.remove(self.groundobj)
            #print 'killed pls'
        if self.inputs['DU'] and not self.PrevInputs['DU']:
            Constants.ENABLENOGRAV = True
        if self.inputs['DR'] and not self.PrevInputs['DR']:
            Constants.ENABLENOGRAV = False
            
    def collide(self, movx, movy):
        if self.collideswith:
            for o in self.collideswith:
                if self.collisionrect.colliderect(o):
                    print "Player has hit" + str(type(o))
        for o in self.parent.world:
            if not o.CanCollide:
                continue
            if self.collisionrect.colliderect(o):
                if 'Wall' in str(type(o)):#(str(type(o))in["<class 'Wall.Wall'>","<class 'Wall.MovePlat'>","<class 'Wall.Platform'>","<class 'Wall.MovPlatform'>"]):
                    o.act(self,movx,movy)
                    #print "should do stuff"
                elif (str(type(o))=="<class 'Player.Player'>"):
                    o.act(self,movx,movy)
                    #print "should do stuff"
                else:
                    print "failed. no non-wall objects should be around."
                    
        
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
        action = 0
        if self.inputs[COM['Act']] and not self.PrevInputs[COM['Act']]:
            action = 1
        if self.inputs[COM['Shield']] and not self.PrevInputs[COM['Shield']]:
            self.spark.changeState(2)
        elif self.inputs[COM['Shoot']] and not self.PrevInputs[COM['Shoot']]:
            self.spark.changeState(1)
        elif self.inputs[COM['Charge']] and not self.PrevInputs[COM['Charge']]:
            self.spark.changeState(0)
            
        self.spark.StoreValues(action,[self.inputs[COM['Move']],self.inputs[COM['Crouch']]],[self.inputs['RSX'],self.inputs['RSY']])
        
        
    def act(self, obj, dx,dy):
        '''default collision between us and an object.'''
        pass
