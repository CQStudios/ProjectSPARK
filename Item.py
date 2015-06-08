import pygame, glob, DObject, Constants, math, OnScreenMenu
from pygame.locals import *
from DObject import *
from Constants import *

class Door(DObject):
    def __init__(self, x, y, path = "level",filename = "exp.json",destination = (0,0),radius = 1, imglst = glob.glob('TileSets/SpaceShip/Door*.png')):
        DObject.__init__(self,x,y)
        T = pygame.transform.scale
        imglst.sort()
        #self.imglst = [T(pygame.image.load(i).convert_alpha(),(TLWDTH,TLHGHT)) for i in imglst]
        self.imglst = [pygame.image.load(i).convert_alpha() for i in imglst]
        self.image = self.imglst[0]
        #pygame.transform.scale(img.convert_alpha(),(TLWDTH,TLHGHT))
        self.path=path
        self.location = [x,y]
        self.filename=filename
        self.destination=destination
        self.radius=radius
        self.interactables = []
        self.rect = self.image.get_rect()
        self.rect.midbottom= [self.x,self.y+TLHGHT/2]
        self.object = None
        self.reqtag = self.prereq = self.gentag = None
        self.story = 'Main'
        self.TRIGGED = False
        self.frame = 0
        self.collisionrect = self.rect
        
    def SetDestination(self,dest):
        self.destination = dest
        
    def addInteractable(self,o):
        self.interactables.append(o)
        
    def SetRadius(self,r):
        self.radius = r
        
    def update(self):
        self.image = self.imglst[self.frame%len(self.imglst)]
        if self.frame != 0:
            self.frame += 1
        if (self.object != None and self.frame > (len(self.imglst)+1)):
            if self.object.parent.path + self.object.parent.filename != self.path+self.filename and self.object == Constants.CUR_LEVEL.User:
                print "Changing level..."
                self.object.parent.SetLevel(self.object,self.path,self.filename)
            print "loc: " + str(self.location)+ "; map: "+self.filename +"; dest:"+str(self.destination)
            self.object.collisionrect.center = self.destination
            self.object.update()
            self.object.update()
            try:
                self.object.spark.pastpos = []
            except:
                pass
            self.object = None
            self.frame = 0
            if self.TRIGGED:
                return
            if self.prereq != None:
                for tag in self.prereq:
                    if tag not in Constants.P_STORY_PROGRESSION[self.story]:
                        return
                if 'Generator_'+str(self.ox)+str(self.oy)+Constants.CUR_LEVEL.filename not in Constants.P_STORY_PROGRESSION[self.story]:
                    Constants.P_STORY_PROGRESSION[self.story].append('Generator_'+str(self.ox)+str(self.oy)+Constants.CUR_LEVEL.filename)
            #after adding self, check  if required tags are here, if so, increment story.
            if self.reqtag != None:
                for i in self.reqtag:
                    if i not in Constants.P_STORY_PROGRESSION[self.story]:
                        return
            Constants.P_STORY_PROGRESSION[self.story][0] += 1
            self.TRIGGED = True
            if self.gentag != None and self.gentag not in Constants.P_STORY_PROGRESSION:
                Constants.P_STORY_PROGRESSION[self.gentag] = {0}
             
        for o in self.interactables:
            dx = o.rect.centerx - self.rect.centerx
            dy = o.rect.bottom - self.rect.bottom
            if abs(dx) > self.radius or abs(dy) > self.radius:
                #if we aren't anywhere close, skip it without calculating
                continue
            d = dx*dx+dy*dy
            d = math.sqrt(d)
            if d <= self.radius:
                self.trigger(o)
                
    def Draw(self, surface, relrect = None):
        if relrect == None:
            #we weren't given a location to defer to
            surface.blit(self.image,self.rect)    
        else:
            surface.blit(self.image,relrect)
            
    def trigger(self,o):
        '''as a door, go to new map or elsewhere on map'''
        if (str(type(o))=="<class 'Player.Player'>"):
            if o.crouchcount == 1 and self.object == None:
                self.object = o
                self.frame = 1
            
class TextSign(DObject):
    def __init__(self, x, y, content = ["default","string","content"],radius = 1, imglst = glob.glob('TileSets/SpaceShip/SignMon*.png')):
        DObject.__init__(self,x,y)
        T = pygame.transform.scale
        imglst.sort()
        self.ox, self.oy = x,y
        #self.imglst = [T(pygame.image.load(i).convert_alpha(),(TLWDTH,TLHGHT)) for i in imglst]
        self.imglst = [pygame.image.load(i).convert_alpha() for i in imglst]
        self.image = self.imglst[0]
        #pygame.transform.scale(img.convert_alpha(),(TLWDTH,TLHGHT))
        self.content = content
        self.location = [x,y]
        self.radius=radius
        self.interactables = []
        self.rect = self.image.get_rect()
        self.rect.midbottom= [self.x,self.y+TLHGHT/2]
        self.object = None
        self.frame = 0
        self.collisionrect = self.rect
        self.content = content
        self.reqtag = self.prereq = self.gentag = None
        self.story = 'Main'
        self.TRIGGED = self.Reload = False
        self.box = OnScreenMenu.TextBox(None,self.content,20,Constants.SCREEN.get_height()-140,Constants.SCREEN.get_width()-40,120)
    def addInteractable(self,o):
        self.interactables.append(o)
    def SetRadius(self,r):
        self.radius = r
    def update(self):
        self.image = self.imglst[self.frame%len(self.imglst)]
        if self.frame != 0:
            self.frame += 1
        if (self.object != None and self.frame >= (len(self.imglst))):
            #TODO generate text box
            self.object.changeState(0+self.object.direction)
            self.object.image = self.object.imglst[self.object.direction][self.object.frame].convert_alpha()
            self.object.groundobj.PushToGround(self.object)
            self.object.rect.midbottom = self.object.collisionrect.midbottom
            self.box.Reload = self.Reload
            self.box.Activate(Constants.CUR_LEVEL)
            self.object = None
            self.frame = 0
            
            if self.TRIGGED:
                return
            #check if the pre-requisites are complete before adding self to tag list.
            if self.prereq != None:
                print "prereq: "+str(self.prereq)
                for tag in self.prereq:
                    if tag not in Constants.P_STORY_PROGRESSION[self.story]:
                        return
                if 'TextSign_'+str(self.ox)+str(self.oy)+Constants.CUR_LEVEL.filename not in Constants.P_STORY_PROGRESSION[self.story]:
                    Constants.P_STORY_PROGRESSION[self.story].append('TextSign_'+str(self.ox)+str(self.oy)+Constants.CUR_LEVEL.filename)
            else:
                if 'TextSign_'+str(self.ox)+str(self.oy)+Constants.CUR_LEVEL.filename not in Constants.P_STORY_PROGRESSION[self.story]:
                    Constants.P_STORY_PROGRESSION[self.story].append('TextSign_'+str(self.ox)+str(self.oy)+Constants.CUR_LEVEL.filename)
            #after adding self, check  if required tags are here, if so, increment story.
            if self.reqtag != None:
                print "reqtag: "+str(self.reqtag)
                for i in self.reqtag:
                    if i not in Constants.P_STORY_PROGRESSION[self.story]:
                        return
            Constants.P_STORY_PROGRESSION[self.story][0] += 1
            if self.effect != None:
                self.effect()
            print "upped story int to: "+str(Constants.P_STORY_PROGRESSION[self.story][0])
            self.TRIGGED = True
            if self.gentag != None and self.gentag not in Constants.P_STORY_PROGRESSION:
                Constants.P_STORY_PROGRESSION[self.gentag] = {0}  
                 
        for o in self.interactables:
            dx = o.rect.centerx - self.rect.centerx
            dy = o.rect.bottom - self.rect.bottom
            if abs(dx) > self.radius or abs(dy) > self.radius:
                #if we aren't anywhere close, skip it without calculating
                continue
            d = dx*dx+dy*dy
            d = math.sqrt(d)
            if d <= self.radius:
                self.trigger(o)
                
    def Draw(self, surface, relrect = None):
        if relrect == None:
            #we weren't given a location to defer to
            surface.blit(self.image,self.rect)    
        else:
            surface.blit(self.image,relrect)
            
    def trigger(self,o):
        '''as a door, go to new map or elsewhere on map'''
        if (str(type(o))=="<class 'Player.Player'>"):
            if o.crouchcount == 1 and self.object == None:
                self.object = o
                self.frame = 1

                
import Tortadillo               
class Generator(DObject):
    #
    # should generate appropriate numbers of enemies. enemy type must be specified
    #
    #
    #
    
    def __init__(self, x, y, parent, objtype="Tortadillo",amount = 4):
        DObject.__init__(self,x,y)
        self.ox,self.oy = x,y
        self.objtype = objtype 
        self.amount = amount
        self.frame = 0
        self.num = 0
        self.parent=parent
        self.rect = pygame.Rect(0,0,TLWDTH,TLHGHT)
        self.rect.center = [self.x,self.y]
        self.xoff = x;self.yoff = y
        self.collisionrect = self.rect
        self.generate = self.gen
        self.prereq = self.reqtag = self.gentag = None
        self.story = 'Main'
        self.TRIGGED  = False
        if self.objtype == "Tortadillo":
            self.generate = self.tortgen
         
    def update(self):
        self.frame += 1
        if self.frame > Constants.FPS/2 and self.num < self.amount:
            self.frame = 0
            self.generate()
            self.num += 1
        if self.num >= self.amount:
            self.parent.all_updates.remove(self)
            self.kill()
            #check if the pre-requisites are complete before adding self to tag list.
            if self.TRIGGED:
                return
            if self.prereq != None:
                for tag in self.prereq:
                    if tag not in Constants.P_STORY_PROGRESSION[self.story]:
                        return
                if 'Generator_'+str(self.ox)+str(self.oy)+Constants.CUR_LEVEL.filename not in Constants.P_STORY_PROGRESSION[self.story]:
                    Constants.P_STORY_PROGRESSION[self.story].append('Generator_'+str(self.ox)+str(self.oy)+Constants.CUR_LEVEL.filename)
            else:
                if 'Generator_'+str(self.ox)+str(self.oy)+Constants.CUR_LEVEL.filename not in Constants.P_STORY_PROGRESSION[self.story]:
                    Constants.P_STORY_PROGRESSION[self.story].append('Generator_'+str(self.ox)+str(self.oy)+Constants.CUR_LEVEL.filename)
            #after adding self, check  if required tags are here, if so, increment story.
            if self.reqtag != None:
                for i in self.reqtag:
                    if i not in Constants.P_STORY_PROGRESSION[self.story]:
                        return
            Constants.P_STORY_PROGRESSION[self.story][0] += 1
            self.TRIGGED = True
            if self.gentag != None and self.gentag not in Constants.P_STORY_PROGRESSION:
                Constants.P_STORY_PROGRESSION[self.gentag] = {0}
                
    def Draw(self, surface, relrect = None):
        #pygame.draw.rect(surface,(255,0,0),relrect,4)
        pass
                
    def tortgen(self):
        
        e = Tortadillo.Tortadillo(self.x,self.y,parent = self.parent)
        e.collideswith = self.parent.User.collideswith
        self.parent.all_layers[2].add(e)
        self.parent.all_updates.append(e)
    def gen(self):
        print "default generator"
        






class Charger(DObject):
    def __init__(self, x, y, meter="energy",amount = 10,radius=30,imglst = glob.glob('TileSets/SpaceShip/Charger*.png')):
        DObject.__init__(self,x,y)
        #charger objects fully restore (or partially restore) a meter when interacted with.
        if meter == 'energy':
            imglst = glob.glob('TileSets/SpaceShip/Charger*.png')
        elif meter == 'health':
            imglst = glob.glob('TileSets/SpaceShip/Medical*.png')
        self.meter = meter 
        self.amount = amount
        imglst.sort()
        self.imglst = [pygame.image.load(i) for i in imglst]
        self.img = self.imglst[0]
        self.frame = 0
        self.radius=radius
        self.interactables = []
        self.rect = pygame.Rect(0,0,TLWDTH,TLHGHT)
        self.rect.center = [self.x,self.y]
        self.collisionrect = self.rect
        
    def SetRadius(self,r):
        self.radius = r
        
    def addInteractable(self,o):
        self.interactables.append(o)   

    def update(self):
        self.image = self.imglst[self.frame%len(self.imglst)]
        self.frame += 1
        if self.frame >= len(self.imglst):
            self.frame =0
        for o in self.interactables:
            dx = o.collisionrect.centerx - self.rect.centerx
            dy = o.collisionrect.bottom - self.rect.bottom
            if abs(dx) > self.radius or abs(dy) > self.radius:
                #if we aren't anywhere close, skip it without calculating
                continue
            d = dx*dx+dy*dy
            d = math.sqrt(d)
            
            if d <= self.radius:
                self.trigger(o)
                
    def Draw(self, surface, relrect = None):
        if relrect == None:
            #we weren't given a location to defer to
            surface.blit(self.image,self.rect)    
        else:
            surface.blit(self.image,relrect)
            
    def trigger(self,o):
        '''as a charger, restore meter'''
        if (str(type(o))=="<class 'Player.Player'>"):
            try:
                if self.meter == "energy":
                    o.spark.FixNRG(self.amount)
                if self.meter == "health":
                    o.health += self.amount
            except:
                print"oh shit, tried charging an object that didn't support it"
                



class Bullet(DObject):
    def __init__(self,x,y,subtype="energy",amount=2,radius=30,lifetime=2,imglst=MIL2('TileSets/SpaceShip/items/EnergyBullet*.png',2)[0],dx=5,dy=0,parent = None,stun=0):
        DObject.__init__(self,x,y)
        self.parent = parent
        self.subtype = subtype
        self.amount = amount
        self.stun = stun
        #self.imglst = [pygame.image.load(i) for i in imglst]
        self.imglst = [pygame.transform.scale(imglst[I],(TLWDTH/4,TLHGHT/4)) for I in range(len(imglst))]
        self.img = self.imglst[0]
        self.frame = 0
        self.lifetime = lifetime*FPS
        self.radius=radius
        self.interactables = []
        self.rect = pygame.Rect(0,0,self.img.get_width(),self.img.get_height())
        self.rect.center = [self.x,self.y]
        self.collisionrect = self.rect
        self.oldspeed = [dx,dy]
        self.speed = [dx,dy]
        self.startpt = [x,y]
        self.origin = None
        
    def SetRadius(self,r):
        self.radius = r
        
    def SetOrigin(self,o):
        self.origin = o
        
    def addInteractable(self,o):
        self.interactables.append(o)
        
    def Activate(self,i):
        self.parent.all_updates.append(self)
        self.parent.all_layers[i].add(self)
        
    def EndAnim(self):
        self.imglst = [i for i in MIL2('TileSets/SpaceShip/items/PhaseEnergyBullet*.png',5)[0]]
        #self.imglst = [pygame.image.load(i) for i in MIL2('TileSets/SpaceShip/items/PhaseEnergyBullet*.png',5)[0]]
        self.lifetime = self.frame + FPS/8
        self.startpt = [self.x,self.y]
        self.oldspeed = self.speed
        self.speed = [0,0]
        
    def Inactivate(self):
        for i in range(len(self.parent.all_layers)):
            if self in self.parent.all_layers[i]:
                self.parent.all_layers[i].remove(self)
        if self in self.parent.all_updates:
            self.parent.all_updates.remove(self)
        
    def update(self):
        self.image = self.imglst[self.frame%len(self.imglst)]
        self.frame += 1
        if self.frame >= self.lifetime:
            #destroy self
            self.Inactivate()
        if self.speed == [0,0]:
            return
        for o in self.interactables:
            if o == self.origin:
                continue
            if not self.rect.colliderect(o.collisionrect):
                continue
            if ("Platform" in str(type(o))):
                continue
            elif ("Wall" in str(type(o))):
                slope = (o.getSlope(self.rect.centerx-o.rect.left)+o.rect.top)
                if self.rect.centery >= slope:
                    self.trigger(o)
                else:
                    continue
            elif ("Player" in str(type(o))):
                self.trigger(o)
                print "bullet interacted with player"
                break
            elif ("Tortadillo" in str(type(o))):
                self.trigger(o)
                print "bullet interacted with Tortadillo"
                break
            dx = o.collisionrect.centerx - self.rect.centerx
            dy = o.collisionrect.bottom - self.rect.bottom
            if abs(dx) > self.radius or abs(dy) > self.radius:
                continue
            d = dx*dx+dy*dy
            d = math.sqrt(d)
            if d <= self.radius:
                self.trigger(o)
                break
                
        self.x = self.startpt[0]+self.frame*self.speed[0]
        self.y = self.startpt[1]+self.frame*self.speed[1]
        self.rect.center = [self.x,self.y]
        self.collisionrect.center = self.rect.center
    def Draw(self, surface, relrect = None):
        if relrect == None:
            #we weren't given a location to defer to
            surface.blit(self.image,self.rect)    
        else:
            surface.blit(self.image,(relrect.x-self.image.get_width()/2,relrect.y-self.image.get_height()/2,relrect.width,relrect.height))
            
    def trigger(self,o):
        '''as a bullet, call damage'''
        if ('Player' in str(type(o))):
            o.damage(self,self.amount,self.stun,self.subtype)
            self.EndAnim()
        if ('Tortadillo' in str(type(o))):
            o.damage(self,self.amount,self.stun,self.subtype)
            self.EndAnim()
        elif ("Wall" in str(type(o))):
            self.EndAnim()
        elif ("Item"in str(type(o))):
            print 'twas an item'
            return
        else:
            print type(o)
            self.EndAnim()

class GravSwitch(DObject):
    '''TODO implement new image which switches gravity on/off when flipped. time limit -> enable un reachable areas to be reached '''
    def __init__(self, x, y, content = ["default","string","content"],radius = 1, imglst = glob.glob('TileSets/SpaceShip/SignMon*.png')):
        DObject.__init__(self,x,y)
        T = pygame.transform.scale
        imglst.sort()
        self.ox, self.oy = x,y
        #self.imglst = [T(pygame.image.load(i).convert_alpha(),(TLWDTH,TLHGHT)) for i in imglst]
        self.imglst = [pygame.image.load(i).convert_alpha() for i in imglst]
        self.image = self.imglst[0]
        #pygame.transform.scale(img.convert_alpha(),(TLWDTH,TLHGHT))
        self.content = content
        self.location = [x,y]
        self.radius=radius
        self.interactables = []
        self.rect = self.image.get_rect()
        self.rect.midbottom= [self.x,self.y+TLHGHT/2]
        self.object = None
        self.frame = 0
        self.collisionrect = self.rect
        self.content = content
        self.reqtag = self.prereq = self.gentag = None
        self.story = 'Main'
        self.TRIGGED = self.Reload = False
        self.box = OnScreenMenu.TextBox(None,self.content,20,Constants.SCREEN.get_height()-140,Constants.SCREEN.get_width()-40,120)
    def addInteractable(self,o):
        self.interactables.append(o)
    def SetRadius(self,r):
        self.radius = r
    def update(self):
        self.image = self.imglst[self.frame%len(self.imglst)]
        if self.frame != 0:
            self.frame += 1
        if (self.object != None and self.frame >= (len(self.imglst))):
            #TODO generate text box
            self.object.changeState(0+self.object.direction)
            self.object.image = self.object.imglst[self.object.direction][self.object.frame].convert_alpha()
            self.object.groundobj.PushToGround(self.object)
            self.object.rect.midbottom = self.object.collisionrect.midbottom
            self.box.Reload = self.Reload
            self.box.Activate(Constants.CUR_LEVEL)
            self.object = None
            self.frame = 0
            
            if self.TRIGGED:
                return
            #check if the pre-requisites are complete before adding self to tag list.
            if self.prereq != None:
                print "prereq: "+str(self.prereq)
                for tag in self.prereq:
                    if tag not in Constants.P_STORY_PROGRESSION[self.story]:
                        return
                if 'TextSign_'+str(self.ox)+str(self.oy)+Constants.CUR_LEVEL.filename not in Constants.P_STORY_PROGRESSION[self.story]:
                    Constants.P_STORY_PROGRESSION[self.story].append('TextSign_'+str(self.ox)+str(self.oy)+Constants.CUR_LEVEL.filename)
            else:
                if 'TextSign_'+str(self.ox)+str(self.oy)+Constants.CUR_LEVEL.filename not in Constants.P_STORY_PROGRESSION[self.story]:
                    Constants.P_STORY_PROGRESSION[self.story].append('TextSign_'+str(self.ox)+str(self.oy)+Constants.CUR_LEVEL.filename)
            #after adding self, check  if required tags are here, if so, increment story.
            if self.reqtag != None:
                print "reqtag: "+str(self.reqtag)
                for i in self.reqtag:
                    if i not in Constants.P_STORY_PROGRESSION[self.story]:
                        return
            Constants.P_STORY_PROGRESSION[self.story][0] += 1
            if self.effect != None:
                self.effect()
            print "upped story int to: "+str(Constants.P_STORY_PROGRESSION[self.story][0])
            self.TRIGGED = True
            if self.gentag != None and self.gentag not in Constants.P_STORY_PROGRESSION:
                Constants.P_STORY_PROGRESSION[self.gentag] = {0}  
                 
        for o in self.interactables:
            dx = o.rect.centerx - self.rect.centerx
            dy = o.rect.bottom - self.rect.bottom
            if abs(dx) > self.radius or abs(dy) > self.radius:
                #if we aren't anywhere close, skip it without calculating
                continue
            d = dx*dx+dy*dy
            d = math.sqrt(d)
            if d <= self.radius:
                self.trigger(o)
                
    def Draw(self, surface, relrect = None):
        if relrect == None:
            #we weren't given a location to defer to
            surface.blit(self.image,self.rect)    
        else:
            surface.blit(self.image,relrect)
            
    def trigger(self,o):
        '''as a door, go to new map or elsewhere on map'''
        if (str(type(o))=="<class 'Player.Player'>"):
            if o.crouchcount == 1 and self.object == None:
                self.object = o
                self.frame = 1
            
