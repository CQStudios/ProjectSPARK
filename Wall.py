import pygame, glob, DObject, Constants
from pygame.locals import *
from DObject import *
from Constants import *

#
#
#
# true WALLS
#
#
# so it didn't work. lets make sure it didn't mess up the old logic.
       
class Wall(DObject):
    def __init__(self, x, y, slope = [0,0], img = pygame.image.load('world/0.png'),xoff = 0, yoff=0):
        DObject.__init__(self,x,y)
        self.image = pygame.transform.scale(img.convert_alpha(),(TLWDTH,TLHGHT))
        self.rect = self.image.get_rect()
        self.rect.center= [self.x,self.y]
        self._ST=slope[0]
        self._ET=slope[1]
        self.CanCollide = True
        self.tract = 1.0 #do not modify player's physics
        self.xoff=xoff
        self.yoff=yoff
        self.collisionrect = self.rect
        
    def getSlope(self,x):
        if self._ST*self.rect.height - self._ET*self.rect.height == 0:
            return self._ST*self.rect.height
        return float(self._ST*self.rect.height)-float(x)/self.rect.width*(float(self._ST*self.rect.height)-float(self._ET*self.rect.height))
        
    def Draw(self, surface, relrect = None):
        if relrect == None:
            #we weren't given a location to defer to
            surface.blit(self.image,(self.rect.x+self.xoff,self.rect.y+self.yoff,self.rect.width,self.rect.height))    
        else:
            surface.blit(self.image,(relrect.x+self.xoff,relrect.y+self.yoff,relrect.width,relrect.height))
    
    def PushToGround(self,obj):
        obj.collisionrect.bottom = self.rect.top + self.getSlope(obj.collisionrect.centerx - self.rect.left)
        obj.rect.midbottom = obj.collisionrect.midbottom
        
    def act(self,o,dx,dy):
        '''push colliding objects to borders if they don't meet the criteria'''
        l = o.collisionrect.centerx - self.rect.left
        YREP = self.getSlope(l)
        oldYREP = self.getSlope(l-dx)
        oPt = self.rect.top+oldYREP
        Pt = self.rect.top+YREP
        #print Pt-o.collisionrect.centery
        b = ""
        #specialstate is true if the object has any relavant abilities.
        specialstate = False
        try:
            if o.spark.CurrentAction in "Dash":
                specialstate = True
        except:
            specialstate = False
        if o.groundobj and not o.jump and not specialstate:
            #print "grounded"
            t1 = o.groundobj.rect.left - self.rect.right
            t2 = o.groundobj.rect.right - self.rect.left
            if t1 == 0:
                #print "right"
                #ground object within our range of influence, collision on this objects right
                if abs((self._ET*self.rect.height+self.rect.top) - (o.groundobj._ST*o.groundobj.rect.height+o.groundobj.rect.top)) <=1:
                    #print "deferred from rightside collision ============"
                    if (o.collisionrect.centery >= self.rect.bottom) or (o.prevpos[1] >= self.rect.bottom):
                        o.collisionrect.top += (self.rect.bottom-o.collisionrect.top)
                        #o.y += (self.rect.bottom-o.collisionrect.top)
                        
                    elif (o.collisionrect.centerx >= self.rect.left) and (o.collisionrect.centerx <= self.rect.right):
                        o.touchground(self)
                        o.collisionrect.bottom += (Pt-o.collisionrect.bottom)
                        #o.y += (Pt-o.collisionrect.bottom)
                        o.ddy = 0
                        o.contact = True
                    elif o.grounded:
                        o.touchground(o.groundobj)
                    return
            if t2 == 0:
                #print "left"
                #ground object within our range of influence, collision on this objects right
                if abs((self._ST*self.rect.height+self.rect.top) - (o.groundobj._ET*o.groundobj.rect.height+o.groundobj.rect.top)) <=1:
                    #print "deferred from leftside collision ~~~~~~~~~~~~"
                    if (o.collisionrect.centery >= self.rect.bottom) or (o.prevpos[1] >= self.rect.bottom):
                        o.collisionrect.top = self.rect.bottom
                        #o.y += (self.rect.bottom-o.collisionrect.top)
                    elif (o.collisionrect.centerx >= self.rect.left) and (o.collisionrect.centerx <= self.rect.right ):
                        o.touchground(self)
                        o.collisionrect.bottom += (Pt-o.collisionrect.bottom)
                        #o.y += (Pt-o.collisionrect.bottom)
                        o.ddy = 0
                        o.contact = True
                    elif o.grounded:
                        o.touchground(o.groundobj)
                    return
                    
        if o.collisionrect.centery >= Pt: # o.prevpos[1]>=oPt:
            #DEAL WITH ALL CASES IN WHICH WE HAVE NO CHANCE OF GETTING ON
            #IF another object is this object's grounded block, we can defer to that
            b += "CANT GET ON:::"
            #print "BULL"
            
            if dx != 0 or (dy == 0 and dx == 0):
                b+="dx check:::"
                #moving into the block from the sides
                if (o.collisionrect.centerx >= self.rect.left) and (o.prevpos[0] <= self.rect.left):
                    #collision from the left side
                    o.collisionrect.right = self.rect.left
                    o.ddx = 0
                    o.dx = 0
                    b+="Halted along my left:::"
                elif (o.collisionrect.centerx <= self.rect.right) and (o.prevpos[0] >= self.rect.right):
                    #collision from the right side
                    o.collisionrect.left = self.rect.right
                    o.ddx = 0
                    o.dx=0
                    b+="Halted along my right:::"
                elif o.prevpos[0] <= self.rect.left:
                    o.collisionrect.right = self.rect.left
                    o.ddx = 0
                elif o.prevpos[0] >= self.rect.right:
                    o.collisionrect.left = self.rect.right
                    o.ddx = 0
                else:
                    #print "SHIIIIIIIIIIIIIIIIIIITTTT"
                    pass
                #elif o.collisionrect.centerx <= self.rect.centerx and o.prevpos[0] <= self.rect.centerx: 
                #    #print "strange~~~~~~~~~~~~~~~~~~~~~~~~~ddddddddddddddd"
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
                #print "unhandled error with o.centery under block's slope"
                #print "dx: "+str(dx)+" - dy: " +str(dy)
                pass
            #print b   
            pass
        else:
            #centery is at or above the slope
            b+="wtf guess we are on"
            if o.ddy < 0:
                return
            if (o.collisionrect.centerx < self.rect.left)or(o.collisionrect.centerx > self.rect.right):
                #the center isn't inside, don't affect it.
                #print "4~~"
                return
            elif dy == 0:
                b+="5~~"
                #center is inside it. only shift if bottom is below what it should be.
                o.contact = False
                if o.collisionrect.bottom >= Pt-4 or o.collisionrect.bottom >= oPt-4:
                    o.collisionrect.bottom = Pt
                    o.contact = True
                    #print b+"6~~"
                return
            elif o.collisionrect.bottom < Pt:
                #print b+"7~~"
                #dy != 0, dx ==0, so there is no true collision here.
                return
            else:
                #print b+"8~~"
                o.touchground(self)
                if dy > 0:
                    o.ddy = 0
                    o.collisionrect.bottom = Pt
                    o.contact = True
                #call objects method for touching ground
#
#
#
# true Platforms
#
# so basically all we really need is to change the act() function
#
       
class Platform(DObject):
    def __init__(self, x, y, slope = [0,0], img = pygame.image.load('world/0.png'),xoff = 0, yoff=0):
        DObject.__init__(self,x,y)
        self.image = pygame.transform.scale(img.convert_alpha(),(TLWDTH,TLHGHT))
        self.rect = self.image.get_rect()
        self.rect.center= [self.x,self.y]
        self._ST=slope[0]
        self._ET=slope[1]
        self.CanCollide = True
        self.tract = 1.0 #do not modify player's physics
        self.xoff=xoff
        self.yoff=yoff
        self.collisionrect = self.rect
        
    def getSlope(self,x):
        if self._ST*self.rect.height - self._ET*self.rect.height == 0:
            return self._ST*self.rect.height
        return float(self._ST*self.rect.height)-float(x)/self.rect.width*(float(self._ST*self.rect.height)-float(self._ET*self.rect.height))
        
    def Draw(self, surface, relrect = None):
        if relrect == None:
            #we weren't given a location to defer to
            surface.blit(self.image,(self.rect.x+self.xoff,self.rect.y+self.yoff,self.rect.width,self.rect.height))    
        else:
            surface.blit(self.image,(relrect.x+self.xoff,relrect.y+self.yoff,relrect.width,relrect.height))
    
    def PushToGround(self,obj):
        obj.collisionrect.bottom = self.rect.top + self.getSlope(obj.collisionrect.centerx - self.rect.left)
        obj.rect.midbottom = obj.collisionrect.midbottom
        
    def act(self,o,dx,dy):
        '''push colliding objects to borders if they don't meet the criteria'''
        l = o.collisionrect.centerx - self.rect.left
        YREP = self.getSlope(l)
        oldYREP = self.getSlope(l-dx)
        oPt = self.rect.top+oldYREP
        Pt = self.rect.top+YREP
        #print Pt-o.collisionrect.centery
        b = ""
        #specialstate is true if the object has any relavant abilities.
        specialstate = False
        try:
            if o.spark.CurrentAction in "Dash":
                specialstate = True
        except:
            specialstate = False
        ydist = o.collisionrect.bottom - Pt
        if o.groundobj and not o.jump and not specialstate and abs(ydist)<12:
            #print "grounded"
            #TODO potential bug when ground object is next to this object but not on the same y level
            t1 = o.groundobj.rect.left - self.rect.right
            t2 = o.groundobj.rect.right - self.rect.left
            if t1 == 0:
                #print "right"
                #ground object within our range of influence, collision on this objects right
                if abs((self._ET*self.rect.height+self.rect.top) - (o.groundobj._ST*o.groundobj.rect.height+o.groundobj.rect.top)) <=1:
                    #print "deferred from rightside collision ============"
                    if (o.collisionrect.centerx >= self.rect.left) and (o.collisionrect.centerx <= self.rect.right):
                        o.touchground(self)
                        o.collisionrect.bottom += (Pt-o.collisionrect.bottom)
                        #o.y += (Pt-o.collisionrect.bottom)
                        o.ddy = 0
                        o.contact = True
                    elif o.grounded:
                        o.touchground(o.groundobj)
                    return
            elif t2 == 0:
                #print "left"
                #ground object within our range of influence, collision on this objects right
                if abs((self._ST*self.rect.height+self.rect.top) - (o.groundobj._ET*o.groundobj.rect.height+o.groundobj.rect.top)) <=1:
                    #print "deferred from leftside collision ~~~~~~~~~~~~"
                    if (o.collisionrect.centerx >= self.rect.left) and (o.collisionrect.centerx <= self.rect.right ):
                        o.touchground(self)
                        o.collisionrect.bottom += (Pt-o.collisionrect.bottom)
                        #o.y += (Pt-o.collisionrect.bottom)
                        o.ddy = 0
                        o.contact = True
                    else:
                        o.touchground(o.groundobj)
                    return
        if o.inputs[COM['Crouch']] > .95:
            pass
        elif o.collisionrect.bottom-o.collisionrect.height/3 <= Pt or o.prevpos[1]<=(oPt-o.collisionrect.height/3):
            #centery is at or above the slope
            if o.ddy < 0:
                if o.collisionrect.centery >= Pt:
                    o.collisionrect.bottom = Pt
                return
            if (o.collisionrect.centerx < self.rect.left)or(o.collisionrect.centerx > self.rect.right):
                #the center isn't inside, don't affect it.
                #print "4~~"
                return
            elif dy == 0:
                b+="5~~"
                #center is inside it. only shift if bottom is below what it should be.
                o.contact = False
                if o.collisionrect.bottom >= Pt-4 or o.collisionrect.bottom >= oPt-4:
                    o.collisionrect.bottom = Pt
                    o.contact = True
                    #print b+"6~~"
                return
            elif o.collisionrect.bottom < Pt:
                #print b+"7~~"
                #dy != 0, dx ==0, so there is no true collision here.
                return
            else:
                #print b+"8~~"
                o.touchground(self)
                if dy > 0:
                    o.ddy = 0
                    o.collisionrect.bottom = Pt
                    o.contact = True
                #call objects method for touching ground


#
#
#
# Moving PLATFORMS
# You can jump through these.
# crouching will let you fall.
#
#
class MovePlatform(Wall):
    def __init__(self, x, y, slope = [0,0], img = pygame.image.load('world/0.png'),xoff = 0, yoff=0, dx = 3, dy = 0, spd =10.0):
        Wall.__init__(self,x,y,slope,img,xoff,yoff)
        self.start = [self.rect.centerx,self.rect.centery]
        self.end = [self.start[0]+(dx)*TLWDTH,self.start[1]+(dy)*TLHGHT]
        self.pos = [self.start[0],self.start[1]]
        self.speed = spd
        self.count = 0
        self.iter = 1
        self.ObjectsOnMe = []
    
    def update(self):
        '''move from one endpoint to the other'''
        oldpos = (int(self.pos[0]),int(self.pos[1]))
        self.count += self.iter
        if self.count >= abs(self.speed*FPS) or self.count <= 0:
            if self.speed>0:
                self.rect.center = self.end
            else:
                self.rect.center = self.start
            #self.speed = -self.speed
            self.iter = -self.iter
            self.pos = [self.rect.centerx,self.rect.centery]
            
        
        self.pos[0]=float(self.start[0]+(self.end[0]-self.start[0])/(FPS*self.speed)*self.count)
        self.pos[1]=float(self.start[1]+(self.end[1]-self.start[1])/(FPS*self.speed)*self.count)
        pos = (int(self.pos[0]),int(self.pos[1]))
        #self.rect.center = self.pos
        self.rect.center = pos
        if self.ObjectsOnMe != None:
            for data in self.ObjectsOnMe:
                data[0].collisionrect.centerx += pos[0]-oldpos[0]
                data[0].collisionrect.centery += pos[1]-oldpos[1]
                #((self.rect.left+data[1]+.5),(self.rect.top+data[2]+.5))
        self.ObjectsOnMe = []
    def act(self,o,dx,dy):
        '''push colliding objects to borders if they don't meet the criteria'''
        l = o.collisionrect.centerx - self.rect.left
        YREP = self.getSlope(l)
        oldYREP = self.getSlope(l-dx)
        oPt = self.rect.top+oldYREP
        Pt = self.rect.top+YREP
        #print Pt-o.collisionrect.centery
        b = ""
        data = [o,l,YREP]
        #specialstate is true if the object has any relavant abilities.
        specialstate = False
        try:
            if o.spark.CurrentAction in "Dash":
                specialstate = True
        except:
            specialstate = False
        if o.groundobj and not o.jump and not specialstate:
            #print "grounded"
            t1 = o.groundobj.rect.left - self.rect.right
            t2 = o.groundobj.rect.right - self.rect.left
            if t1 == 0:
                #print "right"
                #ground object within our range of influence, collision on this objects right
                if abs((self._ET*self.rect.height+self.rect.top) - (o.groundobj._ST*o.groundobj.rect.height+o.groundobj.rect.top)) <=1:
                    #print "deferred from rightside collision ============"
                    if (o.collisionrect.centerx >= self.rect.left) and (o.collisionrect.centerx <= self.rect.right):
                        o.touchground(self)
                        self.ObjectsOnMe.append(data)
                        o.collisionrect.bottom = Pt
                        o.ddy = 0
                        o.contact = True
                    elif o.grounded:
                        o.touchground(o.groundobj)
                        self.ObjectsOnMe.append(data)
                    return
            elif t2 == 0:
                #print "left"
                #ground object within our range of influence, collision on this objects right
                if abs((self._ST*self.rect.height+self.rect.top) - (o.groundobj._ET*o.groundobj.rect.height+o.groundobj.rect.top)) <=1:
                    #print "deferred from leftside collision ~~~~~~~~~~~~"
                    if (o.collisionrect.centerx >= self.rect.left) and (o.collisionrect.centerx <= self.rect.right):
                        o.touchground(self)
                        self.ObjectsOnMe.append(data)
                        o.collisionrect.bottom = Pt
                        o.ddy = 0
                        o.contact = True
                    elif o.grounded:
                        o.touchground(o.groundobj)
                        self.ObjectsOnMe.append(data)
                    return
        if o.inputs[COM['Crouch']] > .95:
            pass
        elif o.collisionrect.bottom-o.collisionrect.height/3 <= Pt or o.prevpos[1]<=(oPt-o.collisionrect.height/3):
            #centery is at or above the slope
            b+="wtf guess we are on"
            if o.ddy < 0:
                if o.collisionrect.centery >= Pt:
                    o.collisionrect.bottom = Pt
                return
            if (o.collisionrect.centerx < self.rect.left)or(o.collisionrect.centerx > self.rect.right):
                #the center isn't inside, don't affect it.
                #print "4~~"
                return
            elif dy == 0:
                b+="5~~"
                #center is inside it. only shift if bottom is below what it should be.
                o.contact = False
                if o.collisionrect.bottom >= Pt-4 or o.collisionrect.bottom >= oPt-4:
                    o.collisionrect.bottom = Pt
                    o.contact = True
                    #print b+"6~~"
                return
            elif o.collisionrect.bottom < Pt:
                #print b+"7~~"
                #dy != 0, dx ==0, so there is no true collision here.
                return
            else:
                #print b+"8~~"
                o.touchground(self)
                self.ObjectsOnMe.append(data)
                if dy > 0:
                    o.ddy = 0
                    o.collisionrect.bottom = Pt
                    o.contact = True
                #call objects method for touching ground
        






#
#
#
# MOVING WALLS
#
#
        
class MoveWall(Wall):
    def __init__(self, x, y, slope = [0,0], img = pygame.image.load('world/0.png'),xoff = 0, yoff=0, dx = 3, dy = 0, spd =10.0):
        Wall.__init__(self,x,y,slope,img,xoff,yoff)
        self.start = [self.rect.centerx,self.rect.centery]
        self.end = [self.start[0]+(dx)*TLWDTH,self.start[1]+(dy)*TLHGHT]
        self.pos = [self.start[0],self.start[1]]
        self.speed = spd
        self.count = 0
        self.iter = 1
        self.ObjectsOnMe = []
    
    def update(self):
        '''move from one endpoint to the other'''
        oldpos = (int(self.pos[0]),int(self.pos[1]))
        self.count += self.iter
        if self.count >= abs(self.speed*FPS) or self.count <= 0:
            if self.speed>0:
                self.rect.center = self.end
            else:
                self.rect.center = self.start
            #self.speed = -self.speed
            self.iter = -self.iter
            self.pos = [self.rect.centerx,self.rect.centery]
            
        
        self.pos[0]=float(self.start[0]+(self.end[0]-self.start[0])/(FPS*self.speed)*self.count)
        self.pos[1]=float(self.start[1]+(self.end[1]-self.start[1])/(FPS*self.speed)*self.count)
        pos = (int(self.pos[0]),int(self.pos[1]))
        #self.rect.center = self.pos
        self.rect.center = pos
        if self.ObjectsOnMe != None:
            for data in self.ObjectsOnMe:
                data[0].collisionrect.centerx += pos[0]-oldpos[0]
                data[0].collisionrect.centery += pos[1]-oldpos[1]
                #((self.rect.left+data[1]+.5),(self.rect.top+data[2]+.5))
        self.ObjectsOnMe = []
    def act(self,o,dx,dy):
        '''push colliding objects to borders if they don't meet the criteria'''
        l = o.collisionrect.centerx - self.rect.left
        YREP = self.getSlope(l)
        oldYREP = self.getSlope(l-dx)
        oPt = self.rect.top+oldYREP
        Pt = self.rect.top+YREP
        #print Pt-o.collisionrect.centery
        b = ""
        data = [o,l,YREP]
        #specialstate is true if the object has any relavant abilities.
        specialstate = False
        try:
            if o.spark.CurrentAction in "Dash":
                specialstate = True
        except:
            specialstate = False
        if o.groundobj and not o.jump and not specialstate:
            #print "grounded"
            t1 = o.groundobj.rect.left - self.rect.right
            t2 = o.groundobj.rect.right - self.rect.left
            if t1 == 0:
                #print "right"
                #ground object within our range of influence, collision on this objects right
                if abs((self._ET*self.rect.height+self.rect.top) - (o.groundobj._ST*o.groundobj.rect.height+o.groundobj.rect.top)) <=1:
                    #print "deferred from rightside collision ============"
                    if (o.collisionrect.centery >= self.rect.bottom) or (o.prevpos[1] >= self.rect.bottom):
                        o.collisionrect.top = self.rect.bottom
                        
                    elif (o.collisionrect.centerx >= self.rect.left) and (o.collisionrect.centerx <= self.rect.right):
                        o.touchground(self)
                        self.ObjectsOnMe.append(data)
                        o.collisionrect.bottom = Pt
                        o.ddy = 0
                        o.contact = True
                    else:
                        o.touchground(o.groundobj)
                    return
            if t2 == 0:
                #print "left"
                #ground object within our range of influence, collision on this objects right
                if abs((self._ST*self.rect.height+self.rect.top) - (o.groundobj._ET*o.groundobj.rect.height+o.groundobj.rect.top)) <=1:
                    #print "deferred from leftside collision ~~~~~~~~~~~~"
                    if (o.collisionrect.centery >= self.rect.bottom) or (o.prevpos[1] >= self.rect.bottom):
                        o.collisionrect.top = self.rect.bottom
                    elif (o.collisionrect.centerx >= self.rect.left) and (o.collisionrect.centerx <= self.rect.right ):
                        o.touchground(self)
                        self.ObjectsOnMe.append(data)
                        o.collisionrect.bottom = Pt
                        o.ddy = 0
                        o.contact = True
                    else:
                        o.touchground(o.groundobj)
                    return
                    
        if o.collisionrect.centery >= Pt: # o.prevpos[1]>=oPt:
            #DEAL WITH ALL CASES IN WHICH WE HAVE NO CHANCE OF GETTING ON
            #IF another object is this object's grounded block, we can defer to that
            b += "CANT GET ON:::"
            #print "BULL"
            
            if dx != 0 or (dy == 0 and dx == 0):
                b+="dx check:::"
                #moving into the block from the sides
                if (o.collisionrect.centerx >= self.rect.left) and (o.prevpos[0] <= self.rect.left):
                    #collision from the left side
                    o.collisionrect.right = self.rect.left
                    o.ddx = 0
                    o.dx = 0
                    b+="Halted along my left:::"
                elif (o.collisionrect.centerx <= self.rect.right) and (o.prevpos[0] >= self.rect.right):
                    #collision from the right side
                    o.collisionrect.left = self.rect.right
                    o.ddx = 0
                    o.dx=0
                    b+="Halted along my right:::"
                elif o.prevpos[0] <= self.rect.left:
                    o.collisionrect.right = self.rect.left
                    o.ddx = 0
                elif o.prevpos[0] >= self.rect.right:
                    o.collisionrect.left = self.rect.right
                    o.ddx = 0
                else:
                    #print "SHIIIIIIIIIIIIIIIIIIITTTT"
                    pass
                #elif o.collisionrect.centerx <= self.rect.centerx and o.prevpos[0] <= self.rect.centerx: 
                #    #print "strange~~~~~~~~~~~~~~~~~~~~~~~~~ddddddddddddddd"
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
                    self.ObjectsOnMe.append(data)
                    b+= "Halted along my top/slope"
                
            else:
                #print "unhandled error with o.centery under block's slope"
                #print "dx: "+str(dx)+" - dy: " +str(dy)
                pass
            #print b   
            pass
        else:
            #centery is at or above the slope
            b+="wtf guess we are on"
            if o.ddy < 0:
                return
            if (o.collisionrect.centerx < self.rect.left)or(o.collisionrect.centerx > self.rect.right):
                #the center isn't inside, don't affect it.
                #print "4~~"
                return
            elif dy == 0:
                b+="5~~"
                #center is inside it. only shift if bottom is below what it should be.
                o.contact = False
                if o.collisionrect.bottom >= Pt-4 or o.collisionrect.bottom >= oPt-4:
                    o.collisionrect.bottom = Pt
                    o.contact = True
                    #print b+"6~~"
                return
            elif o.collisionrect.bottom < Pt:
                #print b+"7~~"
                #dy != 0, dx ==0, so there is no true collision here.
                return
            else:
                #print b+"8~~"
                o.touchground(self)
                self.ObjectsOnMe.append(data)
                if dy > 0:
                    o.ddy = 0
                    o.collisionrect.bottom = Pt
                    o.contact = True
                #call objects method for touching ground
        
