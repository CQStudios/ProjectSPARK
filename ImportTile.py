import pygame, json, sys, Constants, Wall, Item, glob, NPC
sys.path.append('/TileSets/Grass/')
from pygame.locals import *
from Constants import *

class Map():
    def __init__(self,path,filename):
        self.filename  = filename
        self.path = path
        self.filename= filename
        self.filejson = json.load(open(path+filename))
        self.MapH = self.filejson['height']
        self.MapW = self.filejson['width']
        self.TW = self.filejson['tilewidth']
        self.TH = self.filejson['tileheight']
        self.MapProperties = self.filejson['properties']
        self.music_list = self.filejson['Songs']
        l = self.filejson['defaultplayerlocation']
        self.default_location = (l[0]*TLWDTH,l[1]*TLHGHT)
        try:
            self.nograv = bool(self.filejson['NoGrav'])
            if self.nograv:
                Constants.P_AIRFRICTION = 0
            
        except:
            self.nograv = False
        try:
            Constants.BACKGROUNDIMG = pygame.image.load(self.filejson['img'])
        except:
            Constants.BACKGROUNDIMG = pygame.image.load('space.png')
        try:
            Constants.BGINCREMENT = float(self.filejson['bgscrollspeed'])
        except:
            Constants.BGINCREMENT = 0.2
        try:
            self.helmet = bool(self.filejson['Helmet'])
        except:
            self.helmet = False
            Constants.P_AIRFRICTION = .02
        self.spshtname = self.filejson['tilesets'][0]['image']
        self.spsht = pygame.image.load(path+self.spshtname)
        self.layers = [self.filejson['layers'][i] for i in range(len(self.filejson['layers']))]
        
    def Make(self,layers=None,tag=None,_class=None):
        '''if layers is left alone, get all objects using the tag, otherwise only the tag  objects within that layer.'''
        #The idea behind this, is you get all tagged items. 
        if tag == None or _class == None:
            return
        objs = []
        if layers == None:
            for i in range(len(self.layers)):
                o = self.Generate(i,tag, _class)
                if o != None:
                    for j in o:
                        objs.append(j)
        Constants.ENABLENOGRAV = self.nograv
        return objs
        

    def Generate(self,layer, tag, _class):
        '''generate objects in the layer if the tag provided matches the layer tag.'''
        sloped = [44,49,50,52,57,58,59]
        objects = []
        xIO=self.spsht.get_width()/self.TW;
        if self.layers[layer]['name'] != tag:
            return
            #not an appropriate layer, skip it
        life = [[-1,-1]]
        try:
            life = self.layers[layer]['life']
        except:
            life = [[-1,-1]]
        try:
            story = self.layers[layer]['story']
        except:
            story = 'Main'
        quit = True
        for i in life:
            #i = [start,end] pair
            #basically life applies to either the main storyline, which can be unspecified, or the specified storylie
            if (i[0] <= Constants.P_STORY_PROGRESSION[story][0] or i[0]==-1) and (i[1] >= Constants.P_STORY_PROGRESSION[story][0] or i[1]==-1):
                quit = False
                break
        if quit:
            return
        prereq = reqtag = False
        try:
            prereq = self.layers[layer]['prereq']
            #expect list
        except:
            prereq = None
        try:
            reqtag = self.layers[layer]['reqtag']
        except:
            reqtag = None
        try:
            gentag = self.layers[layer]['gentag']
        except:
            gentag = None
        try:
            event = self.layers[layer]['isevent']
        except:
            event = False
        try:
            Reload = bool(self.layers[layer]['reload'])
        except:
            Reload = False
        try:
            effect = self.layers[layer]['effect']
        except:
            effect = None
        if effect != None:
            if effect == "NRGlvlup":
                effect = NRGlvlup
            elif effect == "NRGup":
                effect = NRGup
            elif effect == "healthup":
                effect = healthup
            elif effect == "powerup":
                effect = powerup
            else:
                effect = None
        if gentag != None or reqtag != None or prereq != None:
            event = True
        event = not event
        #~~~~~~~~ prereq, required tags, and story are defined ~~~~~~~~~~~~
        if _class == "Walls":
            for i in range(len(self.layers[layer]['data'])):
                #i holds tile information.
                data=self.layers[layer]['data'][i];slope=[0,0];xoff=0;yoff=0
                #use xoffset and yoffset to change where the essential center point is.
                #this changes "block" location, 
                if data in [0,64]:
                    continue
                F=24
                #following block makes proper slopes
                if data in [49,49+F]:slope = [.5,1]
                if data in [50,50+F]:slope = [0,.5]
                if data in [51,51+F]:slope = [0,1]
                if data in [52,52+F,43,43+F]:slope = [.5,.5]
                if data in [44,44+F]:
                    slope = [.5,.5];yoff=-TLHGHT/2
                if data in [57,57+F]:slope = [1,.5]
                if data in [58,58+F]:slope = [.5,0]
                if data in [59,59+F]:slope = [1,0]
                objects.append(Wall.Wall((self.TW*(i%self.MapW)+xoff),(self.TH*(i/self.MapW)+yoff),slope,self.spsht.subsurface(Rect(self.TW*((data-1)%xIO),self.TH*((data-1)/xIO),self.TW,self.TH)),-xoff,-yoff))
        if _class == "Platforms":
            for i in range(len(self.layers[layer]['data'])):
                #i holds tile information.
                data=self.layers[layer]['data'][i];slope=[0,0];xoff=0;yoff=0
                #use xoffset and yoffset to change where the essential center point is.
                #this changes "block" location, 
                if data in [0,64]:
                    continue
                F=24
                #following block makes proper slopes
                if data in [49,49+F]:slope = [.5,1]
                if data in [50,50+F]:slope = [0,.5]
                if data in [51,51+F]:slope = [0,1]
                if data in [52,52+F,43,43+F]:slope = [.5,.5]
                if data in [44,44+F]:
                    slope = [.5,.5];yoff=-TLHGHT/2
                if data in [57,57+F]:slope = [1,.5]
                if data in [58,58+F]:slope = [.5,0]
                if data in [59,59+F]:slope = [1,0]
                objects.append(Wall.Platform((self.TW*(i%self.MapW)+xoff),(self.TH*(i/self.MapW)+yoff),slope,self.spsht.subsurface(Rect(self.TW*((data-1)%xIO),self.TH*((data-1)/xIO),self.TW,self.TH)),-xoff,-yoff))
        elif _class == "Panels":
            for i in range(len(self.layers[layer]['data'])):
                #i holds tile information.
                data=self.layers[layer]['data'][i];slope=[0,0]
                if data in [0,64]:
                    continue
                objects.append(Wall.Wall((self.TW*(i%self.MapW)),(self.TH*(i/self.MapW)),slope,self.spsht.subsurface(Rect(self.TW*((data-1)%xIO),self.TH*((data-1)/xIO),self.TW,self.TH))))
        elif _class == "Doors":
            x=self.layers[layer]['location'][0]*self.TW
            y=self.layers[layer]['location'][1]*self.TH
            dest=[self.layers[layer]['dx']*self.TW,self.layers[layer]['dy']*self.TH]
            rad = self.layers[layer]['radius']
            p =self.layers[layer]['path']
            f =self.layers[layer]['filename']
            try:
                imgl = glob.glob('TileSets/SpaceShip/'+str(self.layers[layer]['img'])+'.png')
            except:
                imgl = glob.glob('TileSets/SpaceShip/Door*.png')
            objects.append(Item.Door(x,y,p,f,dest,rad,imglst = imgl))
            objects[-1].prereq = prereq
            objects[-1].reqtag = reqtag
            objects[-1].story = story
            objects[-1].gentag = gentag
            objects[-1].TRIGGED = event
        elif _class == "Signs":
            x=self.layers[layer]['location'][0]*self.TW
            y=self.layers[layer]['location'][1]*self.TH
            rad = self.layers[layer]['radius']
            c = self.layers[layer]['content']
            try:
                imglst = glob.glob('TileSets/SpaceShip/Sign'+str(self.layers[layer]['img'])+'*.png')
            except:
                imglst = glob.glob('TileSets/SpaceShip/SignMon*.png')
            objects.append(Item.TextSign(x,y,c,rad,imglst))
            objects[-1].prereq = prereq
            objects[-1].reqtag = reqtag
            objects[-1].story = story
            objects[-1].gentag = gentag
            objects[-1].TRIGGED = event
            objects[-1].Reload = Reload
            objects[-1].effect = effect
        elif _class == "NPC":
            #(self,x,y,prefix = None,content = None,parent = None,isfoc = False)
            x=self.layers[layer]['location'][0]*self.TW
            y=self.layers[layer]['location'][1]*self.TH+TLHGHT/2
            try:
                c = self.layers[layer]['content']
            except:
                c = None
            try:
                pref = self.layers[layer]['img']
            except:
                pref = None
            objects.append(NPC.NPC(x,y,prefix = pref,content = c,parent = Constants.CUR_LEVEL))
            objects[-1].prereq = prereq
            objects[-1].reqtag = reqtag
            objects[-1].story = story
            objects[-1].gentag = gentag
            objects[-1].TRIGGED = event
            objects[-1].Reload = Reload
            objects[-1].effect = effect
        elif _class == "Generator":
            #(self,x,y,prefix = None,content = None,parent = None,isfoc = False)
            x=self.layers[layer]['location'][0]*self.TW
            y=self.layers[layer]['location'][1]*self.TH+TLHGHT/2
            try:
                c = self.layers[layer]['objtype']
            except:
                c = 'Tortadillo'
            try:
                pref = self.layers[layer]['amount']
            except:
                pref = 1
            objects.append(Item.Generator(x,y,Constants.CUR_LEVEL,c,pref))
            objects[-1].prereq = prereq
            objects[-1].reqtag = reqtag
            objects[-1].story = story
            objects[-1].gentag = gentag
            objects[-1].TRIGGED = event
            
        elif _class == "MovePlatforms":
            x=self.layers[layer]['location'][0]*self.TW
            y=self.layers[layer]['location'][1]*self.TH
            dx= self.layers[layer]['dx']
            dy= self.layers[layer]['dy']
            spd = self.layers[layer]['speed']
            data=self.layers[layer]['data'];slope=[0,0];xoff=0;yoff=0
            F=24
            #following block makes proper slopes
            if data in [49,49+F]:slope = [.5,1]
            if data in [50,50+F]:slope = [0,.5]
            if data in [51,51+F]:slope = [0,1]
            if data in [52,52+F,43,43+F]:slope = [.5,.5]
            if data in [44,44+F]:
                slope = [.5,.5];yoff=-TLHGHT/2
            if data in [57,57+F]:slope = [1,.5]
            if data in [58,58+F]:slope = [.5,0]
            if data in [85,85-F]:slope = [.9,.9]
            if data in [59,59+F]:slope = [1,0]
            objects.append(Wall.MovePlatform((x+xoff),(y+yoff),slope,self.spsht.subsurface(Rect(self.TW*((data-1)%xIO),self.TH*((data-1)/xIO),self.TW,self.TH)),-xoff,-yoff,dx,dy,spd))
        elif _class == "MoveWalls":
            x=self.layers[layer]['location'][0]*self.TW
            y=self.layers[layer]['location'][1]*self.TH
            dx= self.layers[layer]['dx']
            dy= self.layers[layer]['dy']
            spd = self.layers[layer]['speed']
            data=self.layers[layer]['data'];slope=[0,0];xoff=0;yoff=0
            F=24
            #following block makes proper slopes
            if data in [49,49+F]:slope = [.5,1]
            if data in [50,50+F]:slope = [0,.5]
            if data in [51,51+F]:slope = [0,1]
            if data in [52,52+F,43,43+F]:slope = [.5,.5]
            if data in [44,44+F]:
                slope = [.5,.5];yoff=-TLHGHT/2
            if data in [57,57+F]:slope = [1,.5]
            if data in [58,58+F]:slope = [.5,0]
            if data in [85,85-F]:slope = [.9,.9]
            if data in [59,59+F]:slope = [1,0]
            objects.append(Wall.MoveWall((x+xoff),(y+yoff),slope,self.spsht.subsurface(Rect(self.TW*((data-1)%xIO),self.TH*((data-1)/xIO),self.TW,self.TH)),-xoff,-yoff,dx,dy,spd))
            
        elif _class == "Chargers":
            x=self.layers[layer]['location'][0]*self.TW
            y=self.layers[layer]['location'][1]*self.TH
            rad = self.layers[layer]['radius']
            meter=self.layers[layer]['meter']
            amount = self.layers[layer]['amount']
            objects.append(Item.Charger(x,y,meter,amount,rad))
        
        return objects
            
    def GetTileset(filename):
        pass
    def CreateMiniMap(self):
        '''minimap is 7x7 instead of 70x70'''
        img = pygame.Surface(((self.MapW+2)*7,(self.MapH+2)*7),pygame.SRCALPHA,32)
        for layer in self.filejson:
            if 'Wall' in layer['name']:
                color = (30,255,120)
                for data in layer['data']:
                    F=24
                    #following block makes proper slopes
                    if data in [49,49+F]:slope = [.5,1]
                    if data in [50,50+F]:slope = [0,.5]
                    if data in [51,51+F]:slope = [0,1]
                    if data in [52,52+F,43,43+F]:slope = [.5,.5]
                    if data in [44,44+F]:
                        slope = [.5,.5];yoff=-TLHGHT/2
                    if data in [57,57+F]:slope = [1,.5]
                    if data in [58,58+F]:slope = [.5,0]
                    if data in [85,85-F]:slope = [.9,.9]
                    if data in [59,59+F]:slope = [1,0]
                    
           #layers include walls, moveplats, doors
            

def NRGlvlup():
    Constants.SoundBank[5].play()
    if Constants.CUR_LEVEL.User.spark.MaxNRGlvl >4:
        return
    Constants.CUR_LEVEL.User.spark.MaxNRGlvl += 1
def NRGup():
    Constants.SoundBank[5].play()
    Constants.CUR_LEVEL.User.spark.MaxNRG = Constants.CUR_LEVEL.User.spark.MaxNRG*1.2
def healthup():
    Constants.SoundBank[5].play()
    Constants.CUR_LEVEL.User.MAX_HEALTH += 25
def powerup():
    Constants.SoundBank[5].play()
    Constants.CUR_LEVEL.User.spark.power += 4
    
