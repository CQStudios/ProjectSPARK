import Constants, Player, Item, Wall, ImportTile, Camera, GUI, Spark, glob
from Constants import *
class Level(object):
    '''Read a map and create a level'''
    def __init__(self, usr = None, path = 'level/', filename= 'exp.json'):
        self.SongTitle = 'None'
        self.all_world = []
        self.updates = []
        self.all_updates = []
        self.path = path
        self.filename = filename
        self.all_sprite = pygame.sprite.Group()
        self.layers = [pygame.sprite.Group() for i in range(6)]
        self.all_layers = [pygame.sprite.Group() for i in range(6)]
        self.User = usr
        self.width = self.height = -1
        self.map = None
        self.lvlsongs = ''
        self.lvlsng = 0
        self.MakeMap()
        self.GUI = None
        self.SongTitle = None
        self.volumelevel = 1.0
        self.currentsavefile = ['Saves/','F1.json']
    
    def MakeMap(self):
    	self.map= ImportTile.Map(self.path,self.filename)
    	if self.User == None:
            self.User = Player.Player(self.map.default_location[0],self.map.default_location[1],isfoc = True)
        if self.map.helmet:
            self.User.MakeImglst('H')
        else:
            self.User.MakeImglst('')
        self.User.collisionrect.midbottom = (self.map.default_location[0],self.map.default_location[1])
    	self.User.parent = self
    	self.all_updates.append(self.User)
    	#~~~~experiment with make and generate
    	trigs = []
    	stuff = self.map.Make(None,"Walls","Walls")
    	for o in stuff:
    	    self.all_layers[1].add(o)
    	    self.all_world.append(o)
    	    self.all_sprite.add(o)
    	stuff = self.map.Make(None,"Platforms","Platforms")
    	for o in stuff:
    	    self.all_layers[1].add(o)
    	    self.all_world.append(o)
    	    self.all_sprite.add(o)
    	stuff = self.map.Make(None,"MovePlat","MovePlatforms")
    	for o in stuff:
    	    self.all_layers[2].add(o)
    	    self.all_updates.append(o)
    	    self.all_world.append(o)
    	    self.all_sprite.add(o)
    	stuff = self.map.Make(None,"Panels","Panels")
    	for o in stuff:
    	    self.all_layers[0].add(o)
    	    self.all_sprite.add(o)
    	stuff = self.map.Make(None,"Foreground","Panels")
    	#use 'Foreground' tagged layers to make 'Panels'
    	for o in stuff:
    	    self.all_layers[4].add(o)
    	    self.all_sprite.add(o)
    	stuff = self.map.Make(None,'Door','Doors')
    	for o in stuff:
    	    self.all_layers[1].add(o)
    	    trigs.append(o)
    	    o.addInteractable(self.User)
    	    self.all_updates.append(o)
    	    self.all_sprite.add(o)
    	stuff = self.map.Make(None,'Charger','Chargers')
    	for o in stuff:
    	    self.all_layers[1].add(o)
    	    trigs.append(o)
    	    o.addInteractable(self.User)
    	    self.all_updates.append(o)
    	    self.all_sprite.add(o)
    	stuff = self.map.Make(None,'Sign','Signs')
    	for o in stuff:
    	    self.all_layers[1].add(o)
    	    trigs.append(o)
    	    o.addInteractable(self.User)
    	    self.all_updates.append(o)
    	    self.all_sprite.add(o)
    	stuff = self.map.Make(None,'NPC','NPC')
    	for o in stuff:
    	    self.all_layers[3].add(o)
    	    self.all_updates.append(o)
    	    self.all_sprite.add(o)
    	stuff = self.map.Make(None,'Generator','Generator')
    	for o in stuff:
    	    self.all_layers[2].add(o)
    	    self.all_updates.append(o)
    	self.world = self.all_world
    	self.User.setTriggers(trigs)
    	self.all_sprite.add(self.User)
    	self.all_layers[3].add(self.User)
    	self.width = self.map.MapW * TLWDTH
    	self.height = self.map.MapH * TLHGHT
    	self.setmusic(0)
    	Constants.frame = 0
    	Constants.CUR_CAMERA = Camera.Camera(Constants.SCREEN, self.User.collisionrect, (self.width, self.height))
    	self.CUR_GUI = GUI.GUI(0,0,self)
    	
    def setvolume(self,i):
        self.volumelevel = i
        pygame.mixer.music.set_volume(i)
        for x in Constants.SoundBank:
            x.set_volume(i*2/3)
        
    def setmusic(self,i):
        self.levelsongs = glob.glob(self.map.music_list)
        self.levelsongs.sort()
        self.lvlsng = (self.lvlsng + i)%len(self.levelsongs)
        if self.SongTitle == self.levelsongs[self.lvlsng]:
            return
        pygame.mixer.music.load(self.levelsongs[self.lvlsng])
        pygame.mixer.music.play(-1)
        self.SongTitle = self.levelsongs[self.lvlsng]
    	
    def SetLevel(self, usr = None, path='level/', filename='exp.json'):
        if usr != None:
            self.User=usr
            self.User.parent = self
            del self.User.collideswith[:]
            del self.User.triggerswith[:]
        for i in self.all_layers:
            i.empty()
        for i in self.layers:
            i.empty()
        self.all_sprite.empty()
        del self.all_world[:]
        del self.updates[:]
        del self.all_updates[:]
        del self.all_sprite
        del self.layers[:]
        del self.all_layers[:]
        del self.map
        self.all_world = []
        self.updates = []
        self.all_updates = []
        self.path = path
        self.filename = filename
        self.all_sprite = pygame.sprite.Group()
        self.layers = [pygame.sprite.Group() for i in range(6)]
        self.all_layers = [pygame.sprite.Group() for i in range(6)]
        self.map = None
        self.MakeMap()
        self.User.IsFocus = True
    def GameRestart(self):
        if self.currentsavefile:
            self.User.LOAD(self.currentsavefile[0],self.currentsavefile[1])
    def ReloadLevel(self):
        loc = self.User.collisionrect.midbottom
        self.SetLevel(self.User,self.path,self.filename)
        self.User.collisionrect.midbottom = loc
    def get_size(self):
        return (self.width, self.height)

