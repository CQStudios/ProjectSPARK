import pygame, json, sys, Constants, Wall
sys.path.append('/TileSets/Grass/')
from pygame.locals import *
from Constants import *

class Map():
    def __init__(self,path,filename):
        self.filename  = filename
        self.filejson = json.load(open(path+filename))
        self.MapH = self.filejson['height']
        self.MapW = self.filejson['width']
        self.TW = self.filejson['tilewidth']
        self.TH = self.filejson['tileheight']
        self.MapProperties = self.filejson['properties']
        self.spshtname = self.filejson['tilesets'][0]['image']
        self.spsht = pygame.image.load(path+self.spshtname)
        self.layers = [self.filejson['layers'][i] for i in range(len(self.filejson['layers']))]
        
    def test(self, sx, sy):
        lm = [[str(x)+":"+str(y) for x in range(sx)] for y in range(sy)]
        return lm
        
    def GetMap(self, layer):
        '''objective: return a list of integers derived from a json tilemap
        '''
        Map = []
        row = []
        #lmap = [[0 for x in range()] for i in range]
        H = self.filejson['layers'][layer]['height']
        W = self.filejson['layers'][layer]['width']
        X = self.filejson['layers'][layer]['x']
        Y = self.filejson['layers'][layer]['y']
        nmap=[ [self.filejson['layers'][layer]['data'][y*W+x] for x in range(W)] for y in range(H)]
        for i in range(H):
            row = []
            for j in range(W):
                row.append(self.filejson['layers'][layer]['data'][i*W+j])
            Map.append(row)
        #print mapjson['layers'][0]['data']
        return Map
        
        
    def MakeWalls(self):
        objs = []
        for i in range(len(self.layers)):
            o = self.GenerateWalls(i)
            if o != None:
                for j in o:
                    objs.append(j)
        return objs
    def MakePanels(self):
        objs = []
        for i in range(len(self.layers)):
            o = self.GeneratePanels(i)
            if o != None:
                for j in o:
                    objs.append(j)
        return objs


    def GenerateWalls(self,layer):
        '''Generate Wall objects from the layer provided if the layer is named "Walls"'''
        #generate wall objects
        sloped=[49,50,51,57,58,59] #these ints have slopes
        objects = []
        xIO=self.spsht.get_width()/self.TW;
        if self.layers[layer]['name'] != 'Walls':
            return
        for i in range(len(self.layers[layer]['data'])):
            #i holds tile information.
            data=self.layers[layer]['data'][i];slope=[0,0]
            if data in [0,64]:
                continue
            #following block makes proper slopes
            if data == 49:slope = [.5,1]
            if data == 50:slope = [0,.5]
            if data == 51:slope = [0,1]
            if data == 57:slope = [1,.5]
            if data == 58:slope = [.5,0]
            if data == 59:slope = [1,0]
            objects.append(Wall.Wall((self.TW*(i%self.MapW)),(self.TH*(i/self.MapW)),slope,self.spsht.subsurface(Rect(self.TW*((data-1)%xIO),self.TH*((data-1)/xIO),self.TW,self.TH))))
        return objects
        
    def GeneratePanels(self,layer):
        '''Generate Wall objects from the layer provided if the layer is named "Panels"'''
        #generate wall objects that don't collide
        objects = []
        xIO=self.spsht.get_width()/self.TW;
        if self.layers[layer]['name'] != 'Panels':
            return
        for i in range(len(self.layers[layer]['data'])):
            #i holds tile information.
            data=self.layers[layer]['data'][i];slope=[0,0]
            if data in [0,64]:
                continue
            objects.append(Wall.Wall((self.TW*(i%self.MapW)),(self.TH*(i/self.MapW)),slope,self.spsht.subsurface(Rect(self.TW*((data-1)%xIO),self.TH*((data-1)/xIO),self.TW,self.TH))))
        return objects
            
    def GetTileset(filename):
        pass
        
pathname = 'level/'
levelfilename = 'exp.json'
identities = Map(pathname, levelfilename)
l = identities.GetMap(0)
nm = pathname + identities.spshtname
d = pygame.image.load(nm)
print d
print identities.spshtname
print nm
print identities.test(3,7)
