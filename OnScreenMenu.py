#Menu
import DObject, pygame,Constants, Player, Spark, Level, ImportTile, json, sys, Tortadillo, Item, NPC
from DObject import *
from pygame import*
from Constants import *
pygame.font.init()
Buf = 10
class Menu(DObject):
    def __init__(self,x,y,width,height,parent):
        '''parent must be a level reference'''
        DObject.__init__(self,x,y)
        self.image = pygame.Surface((width,height), pygame.SRCALPHA, 32)
        self.image.fill((0,0,0,180))
        self.rect = self.image.get_rect()
        self.width = width
        self.height = height
        self.active = False
        self.parent = parent
        self.xoff = x
        self.yoff = y
        self.StoredUpdateObjs = []
        self.state = [0]
        self.textfont = pygame.font.Font('Font/Prototype.ttf',14)
        self.previousstates = [0]
        self.select = 1
        self.text = []
        self.jsonfile = json.load(open('MenuText.json'))
        self.warning = pygame.Surface((1,1))
        self.frame = 0
        self.maxclick = False
    def Activate(self):
        Constants.SoundBank[2].play()
        self.StoredUpdateObjs = self.parent.all_updates
        self.parent.all_updates = [self]
        self.parent.all_layers[-1].add(self)
        self.listen = self.parent.User
        self.rect.right = self.listen.rect.left
        self.rect.bottom = self.listen.rect.top
        self.changestate(1)
        
    def Inactivate(self):
        Constants.SoundBank[3].play()
        if self.parent.all_updates == [self]:
            self.parent.all_updates = self.StoredUpdateObjs
        if self in self.parent.all_layers[-1]:
            self.parent.all_layers[-1].remove(self)
        self.changestate(0)
        self.previousstates=[0]
        self.frame = 0
        self.warning = Surface((1,1))
        
    def changestate(self,st):
        self.text = []
        self.state = st
        try:
            for i in range(len(self.jsonfile[str(self.state)])):
                color = (150,150,255)
                if i == 0: 
                    color = (180,150,0)
                self.text.append(self.textfont.render(self.jsonfile[str(self.state)][i],True,color))
            self.select = 1
        except KeyError:
            return -1        
                
    def update(self):
        self.frame +=1
        self.x = self.listen.x
        self.y = self.listen.y
        pIn = self.listen.PrevInputs.copy()
        In = self.listen.inputs.copy() 
        if In['Str'] and not pIn['Str']:
            self.Inactivate()    
        if abs(In['RSX'])>.05:# and not abs(pIn['RSX'])>.75:
            self.xoff += 250.0/FPS*In['RSX']
        if abs(In['RSY'])>.05:# and not abs(pIn['RSY'])>.75:
            self.yoff += 250.0/FPS*In['RSY']
        if self.xoff < Buf:self.xoff=Buf
        elif self.xoff > SCRNWDTH-Buf-self.width:self.xoff=SCRNWDTH-Buf-self.width
        if self.yoff < Buf:self.yoff=Buf
        elif self.yoff > SCRNHGHT-Buf-self.height:self.yoff=SCRNHGHT-Buf-self.height
        #if abs(In['LSX'])>.75 and not abs(pIn['LSX'])>.75:
        #    self.select += cmp(In['LSX'],0)%len(self.text)
        if abs(In['LSY'])>.75 and not abs(pIn['LSY'])>.75 and len(self.text) > 0:
            if In['LSY']>0:
                self.select = (self.select+1) % len(self.text)
                if self.select == 0:self.select = 1
            if In['LSY']<0:
                self.select = (self.select-1) % len(self.text)
                if self.select == 0:self.select = len(self.text)-1
        #EXECUTE
        if In['X'] and not pIn['X']:
            Constants.SoundBank[1].play()
            print "selected: " + str(self.jsonfile[str(self.state)][self.select])
            self.previousstates.append(self.state)
            if self.changestate(str(self.jsonfile[str(self.state)][self.select])) == -1:
                #failure, option was end option
                self.maxclick = True
                self.state = self.previousstates[-1]
                self.previousstates=self.previousstates[:-1]
            else:
                self.maxclick = False
        if In['O'] and not pIn['O']:
            Constants.SoundBank[0].play()
            self.StepBack()
        if self.state == 'NO':
            print "prevstates:: "+str(self.previousstates)
            self.StepBack()
            self.StepBack()
        if self.state == 'yes':
            path = ''
            for element in self.previousstates:
                path += str(element)+' '
            print path
            if 'View Stats' in path:
                #(self.parent,content,20,20,200,Constants.SCREEN.get_height()-40)
                content = [["CURRENT STATS/","Max Health: "+str(Constants.CUR_LEVEL.User.MAX_HEALTH),"Max Energy Level: "+str(Constants.CUR_LEVEL.User.spark.MaxNRGlvl),"Max Energy: "+str(Constants.CUR_LEVEL.User.spark.MaxNRG*(Constants.CUR_LEVEL.User.spark.MaxNRGlvl+1)),"Fire power: "+str(Constants.CUR_LEVEL.User.spark.power),"Main Story Int: "+str(Constants.P_STORY_PROGRESSION['Main'][0]),"# of stories: "+str(len(Constants.P_STORY_PROGRESSION))," "]]
                e = TextBox(self.parent,content,40,200,Constants.SCREEN.get_width()/3,Constants.SCREEN.get_height()/2)
                e.Activate()
            elif 'Save1'in path:
                self.listen.SAVE('Saves/','F1.json')
                self.setwarning("Saved in Slot1")
            elif 'Save2'in path:
                self.listen.SAVE('Saves/','F2.json')
                self.setwarning("Saved in Slot2")
            elif 'Save3'in path:
                self.listen.SAVE('Saves/','F3.json')
                self.setwarning("Saved in Slot3")
            elif 'Save4'in path:
                self.listen.SAVE('Saves/','F4.json')
                self.setwarning("Saved in Slot4")
            elif 'Save5'in path:
                self.listen.SAVE('Saves/','F5.json')
                self.setwarning("Saved in Slot5")
            elif 'Save6'in path:
                self.listen.SAVE('Saves/','F6.json')
                self.setwarning("Saved in Slot6")
            elif 'Reset'in path:
                self.listen.LOAD('Saves/','DEFAULT.json')
            try:
                if 'Load1'in path:
                    self.listen.LOAD('Saves/','F1.json')
                    self.setwarning("Loading Slot1")
                    self.previousstates = [0]
                    self.Inactivate()
                    return
                elif 'Load2'in path:
                    self.listen.LOAD('Saves/','F2.json')
                    self.setwarning("Loading Slot2")
                    self.previousstates = [0]
                    self.Inactivate()
                    return
                elif 'Load3'in path:
                    self.listen.LOAD('Saves/','F3.json')
                    self.setwarning("Loading Slot3")
                    self.previousstates = [0]
                    self.Inactivate()
                    return
                elif 'Load4'in path:
                    self.listen.LOAD('Saves/','F4.json')
                    self.setwarning("Loading Slot4")
                    self.previousstates = [0]
                    self.Inactivate()
                    return
                elif 'Load5'in path:
                    self.listen.LOAD('Saves/','F5.json')
                    self.setwarning("Loading Slot5")
                    self.previousstates = [0]
                    self.Inactivate()
                    return
                elif 'Load6'in path:
                    self.listen.LOAD('Saves/','F6.json')
                    self.setwarning("Loading Slot6")
                    self.previousstates = [0]
                    self.Inactivate()
                    return
            except IOError:
                self.previousstates = self.previousstates[:-2]
                #self.state = 'IOError'
                self.changestate('IOError')
                print "shit"
                return
            if 'Exit'in path:
                self.Inactivate()
            elif 'Quit'in path:
                pygame.quit()
                sys.exit()
            self.Inactivate()
        if self.state == "Volume" and self.maxclick==True:
            self.parent.setvolume(float(self.jsonfile[self.state][self.select]))
            self.Inactivate()
            return
        elif self.state == "FPS" and self.maxclick==True:
            Constants.FPS = self.select*5
            self.Inactivate()
            
            
            
            
        elif self.state == "Options" and self.maxclick==True:
            if self.jsonfile[self.state][self.select] == "Alternate Music":
                Constants.CUR_LEVEL.setmusic(1)
            elif self.jsonfile[self.state][self.select] == "Toggle Fullscreen":
                SCREEN_SIZE = (SCRNWDTH, SCRNHGHT)
                #cursize = (pygame.display.get_surface().get_rect().width,pygame.display.get_surface().get_rect().height)
                Constants.FLLSCRN = not Constants.FLLSCRN
                if Constants.FLLSCRN:
                    #Constants.SCREEN = pygame.display.set_mode(SCREEN_SIZE,FULLSCREEN,32)
                    Constants.SCREEN = pygame.display.set_mode(SCREEN_SIZE,FULLSCREEN | HWSURFACE,32)
                else:
                    Constants.SCREEN = pygame.display.set_mode(SCREEN_SIZE,32)
                Constants.CUR_CAMERA.rect = pygame.display.get_surface().get_rect()
                Constants.CUR_CAMERA.rect.center = Constants.CUR_LEVEL.User.rect.center
                Constants.CUR_CAMERA.Bounds = pygame.Rect(Constants.CUR_CAMERA.rect.centerx-Constants.CUR_CAMERA.rect.width/2-140,Constants.CUR_CAMERA.rect.centery-Constants.CUR_CAMERA.rect.height/2-140,Constants.CUR_CAMERA.rect.width+280,Constants.CUR_CAMERA.rect.height+280)
                Constants.CUR_CAMERA.Bounds.center = Constants.CUR_CAMERA.rect.center
                Constants.CUR_CAMERA.WallBounds = pygame.Rect(Constants.CUR_CAMERA.rect.centerx-Constants.CUR_CAMERA.rect.width*2/3,Constants.CUR_CAMERA.rect.centery-Constants.CUR_CAMERA.rect.height*2/3,Constants.CUR_CAMERA.rect.width*3/2,Constants.CUR_CAMERA.rect.height*3/2)
                Constants.CUR_CAMERA.WallBounds.center = Constants.CUR_CAMERA.rect.center
            self.Inactivate()
            
            
            
        elif self.state == "Generate Object" and self.maxclick==True:
            if self.jsonfile[self.state][self.select] == "Player":
                e = Player.Player(self.xoff+Constants.CUR_CAMERA.rect.x,self.yoff+Constants.CUR_CAMERA.rect.y,parent = self.parent)
                e.collideswith = self.parent.User.collideswith
                self.parent.all_layers[2].add(e)
                self.StoredUpdateObjs.append(e)
            if self.jsonfile[self.state][self.select] == "Tortadillo":
                e = Tortadillo.Tortadillo(self.xoff+Constants.CUR_CAMERA.rect.x,self.yoff+Constants.CUR_CAMERA.rect.y,parent = self.parent)
                e.collideswith = self.parent.User.collideswith
                self.parent.all_layers[2].add(e)
                self.StoredUpdateObjs.append(e)
            if self.jsonfile[self.state][self.select] == "Generator":
                e = Item.Generator(self.xoff+Constants.CUR_CAMERA.rect.x,self.yoff+Constants.CUR_CAMERA.rect.y,parent = self.parent)
                self.parent.all_layers[2].add(e)
                self.StoredUpdateObjs.append(e)
            if self.jsonfile[self.state][self.select] == "NPC":
                e = NPC.NPC(self.xoff+Constants.CUR_CAMERA.rect.x,self.yoff+Constants.CUR_CAMERA.rect.y,parent = self.parent)
                self.parent.all_layers[3].add(e)
                self.StoredUpdateObjs.append(e)
            #self.previousstates = self.previousstates[:-1]
            self.changestate("Generate Object")
            self.maxclick = False
            #self.Inactivate()
        #elif self.maxclick == True:
        #    self.Inactivate()
        if self.state == 0:
            self.Inactivate()
    def StepBack(self):
        if self.previousstates[-1] == '0':
            self.state = '0'
            return
        st = self.previousstates[-1]
        self.changestate(st)
        #print "prevstates:: "+str(self.previousstates)
        #print "Leaving: " + str(self.state)
        self.previousstates.remove(self.state)
        
    def setwarning(self,_Str):
        self.warning = self.textfont.render(_Str,True,(180,150,0))
        self.frame = 0
        
    def Draw(self,surf,relrect):
        pygame.draw.rect(surf,(150,150,255,120),(self.xoff,self.yoff,self.width,self.height),8)
        self.canvas = self.image.copy()
        
        for i in range(len(self.text)):
            xoff = 0
            if i == self.select: xoff = 20
            if i == 0:
                xoff = -10
            self.canvas.blit(self.text[i],(20+xoff,20+i*(self.text[i].get_height()+5),self.text[i].get_width(),self.text[i].get_height()))
        if self.frame < Constants.FPS*1.5:
            self.canvas.blit(self.warning,(((self.canvas.get_width()-self.warning.get_width())/2),(self.canvas.get_height()-self.warning.get_height()-5),self.warning.get_width(),self.warning.get_height()))
        surf.blit(self.canvas,(self.xoff,self.yoff,self.width,self.height))
        
        
        
        
        
        
class TextBox(DObject):
    def __init__(self,parent,text=["example","a dictionary containing strings","printing the next line when (confirm) is pressed"],x=10,y=10,width=None,height=3):
        '''parent must be a level reference.'''
        #height is the number of text lines you may display tel:209-527-6242 fax:209-527-6251 attn: Magie Sanchez. need cover page. 1124 Eleventh street. modesto, ca. 95354 !!!!!
        #8849 villa la jolla drive.
        DObject.__init__(self,x,y)
        self.textfont = pygame.font.Font('Font/Prototype.ttf',18)
        if width == None:
            width = Constants.SCREEN.get_width()-x*2
        self.image = pygame.Surface((width,height), pygame.SRCALPHA, 32)
        self.image.fill((0,0,0,180))
        self.rect = self.image.get_rect()
        self.width = width
        self.height = height
        self.parent = parent
        self.xoff = x
        self.yoff = y
        self.StoredUpdateObjs = []
        self.state = []
        self.previousstates = []
        self.select = 1
        self.info = text
        self.text = []
        self.frame = 0
        self.Reload = False
        self.maxclick = False
        
    def Activate(self,parent = None):
        Constants.SoundBank[4].play()
        if parent != None:
            self.parent = parent
        self.StoredUpdateObjs = self.parent.all_updates
        self.parent.all_updates = [self]
        self.parent.all_layers[-1].add(self)
        self.listen = self.parent.User
        self.rect.right = self.listen.rect.right
        self.rect.bottom = self.listen.rect.bottom
        self.changestate(0)
        return
        
    def Inactivate(self):
        Constants.SoundBank[6].play()
        if self in self.parent.all_updates:
            for o in self.StoredUpdateObjs:
                self.parent.all_updates.append(o)
            self.parent.all_updates.remove(self)
        if self in self.parent.all_layers[-1]:
            self.parent.all_layers[-1].remove(self)
        self.changestate(0)
        self.previousstates=[0]
        self.frame = 0
        self.maxclick = False
        if self.Reload:
            self.parent.ReloadLevel()
        
    def changestate(self,st):
        self.state = st
        self.text = []
        try:
            for i in range(len(self.info[self.state])):
                color = (150,150,255)
                string = self.info[self.state][i]
                if len(self.info)-1==self.state and i == len(self.info[self.state])-1:
                    color = (230,200,100)
                if '<' in string or '>' in string or '`' in string or '/' in string:
                    condensed = None
                    sep = []
                    pre = ''
                    color = (150,150,255)
                    for c in range(len(string)):
                        if string[c] not in ['<','>','`','/']:
                            pre = pre + string[c]
                        else:
                            if string[c] == '>':
                                color = (0,255,100)
                            elif string[c] == '<':
                                color = (150,150,255)
                            elif string[c] == '`':
                                color = (210,0,255)
                            elif string[c] == '/':
                                color = (255,50,50)
                            sep.append(self.textfont.render(pre,True,color))
                            pre = ''
                    sep.append(self.textfont.render(pre,True,color))
                    w=0
                    h=sep[0].get_height()
                    for i in range(len(sep)):
                        w += sep[i].get_width()
                    condensed = pygame.Surface((w,h),pygame.SRCALPHA,32)
                    w=0
                    for i in range(len(sep)):
                        condensed.blit(sep[i],(w,0,sep[i].get_width(),sep[i].get_height()))
                        w += sep[i].get_width()
                    self.text.append(condensed)
                else:
                    self.text.append(self.textfont.render(string,True,color))
        except IndexError:
            return -1        
                
    def update(self):
        self.frame +=1
        self.x = self.listen.x
        self.y = self.listen.y
        pIn = self.listen.PrevInputs.copy()
        In = self.listen.inputs.copy()
        if self.xoff < Buf:self.xoff=Buf
        elif self.xoff > SCRNWDTH-Buf-self.width:self.xoff=SCRNWDTH-Buf-self.width
        if self.yoff < Buf:self.yoff=Buf
        elif self.yoff > SCRNHGHT-Buf-self.height:self.yoff=SCRNHGHT-Buf-self.height
        #EXECUTE
        if In['X'] and not pIn['X']:
            Constants.SoundBank[4].play()
            self.previousstates.append(self.state)
            if self.changestate(self.state+1) == -1:
                #failure, option was end option
                self.maxclick = True
                self.state = self.previousstates[-1]
                self.previousstates=self.previousstates[:-1]
            else:
                self.maxclick = False
        if self.maxclick:
            self.Inactivate()
        
    def Draw(self,surf,relrect):
        pygame.draw.rect(surf,(150,150,255,120),(self.xoff,self.yoff,self.width,self.height),8)
        self.canvas = self.image.copy()
        
        for i in range(len(self.text)):
            xoff = 0
            if i == 0:
                xoff = 20
            self.canvas.blit(self.text[i],(20+xoff,20+i*(self.text[i].get_height()+5),self.text[i].get_width(),self.text[i].get_height()))
        surf.blit(self.canvas,(self.xoff,self.yoff,self.width,self.height))
        



class DialogueBox(DObject):
    def __init__(self,parent,text=["example","a dictionary containing strings","printing the next line when (confirm) is pressed"],x=10,y=10,width=None,height=3):
        '''parent must be a level reference.'''
        #height is the number of text lines you may display tel:209-527-6242 fax:209-527-6251 attn: Magie Sanchez. need cover page. 1124 Eleventh street. modesto, ca. 95354 !!!!!
        #8849 villa la jolla drive.
        DObject.__init__(self,x,y)
        self.textfont = pygame.font.Font('Font/Prototype.ttf',18)
        if width == None:
            width = Constants.SCREEN.get_width()-x*2
        self.image = pygame.Surface((width,height), pygame.SRCALPHA, 32)
        self.image.fill((0,0,0,180))
        self.rect = self.image.get_rect()
        self.width = width
        self.height = height
        self.parent = parent
        self.xoff = x
        self.yoff = y
        self.StoredUpdateObjs = []
        self.state = []
        self.previousstates = []
        self.select = 1
        self.info = text
        self.text = []
        self.frame = 0
        self.maxclick = False
        
    def Activate(self,parent = None):
        if parent != None:
            self.parent = parent
        self.StoredUpdateObjs = self.parent.all_updates
        self.parent.all_updates = [self]
        self.parent.all_layers[-1].add(self)
        self.listen = self.parent.User
        self.rect.right = self.listen.rect.right
        self.rect.bottom = self.listen.rect.bottom
        self.changestate(0)
        
    def Inactivate(self):
        if self in self.parent.all_updates:
            for o in self.StoredUpdateObjs:
                self.parent.all_updates.append(o)
            self.parent.all_updates.remove(self)
        if self in self.parent.all_layers[-1]:
            self.parent.all_layers[-1].remove(self)
        self.changestate(0)
        self.previousstates=[0]
        self.frame = 0
        self.maxclick = False
        
    def changestate(self,st):
        self.state = st
        self.text = []
        try:
            for i in range(len(self.info[self.state])):
                color = (150,150,255)
                string = self.info[self.state][i]
                if len(self.info)-1==self.state and i == len(self.info[self.state])-1:
                    color = (230,200,100)
                if '<' in string or '>' in string or '`' in string or '/' in string:
                    condensed = None
                    sep = []
                    pre = ''
                    color = (150,150,255)
                    for c in range(len(string)):
                        if string[c] not in ['<','>','`','/']:
                            pre = pre + string[c]
                        else:
                            if string[c] == '>':
                                color = (0,255,100)
                            elif string[c] == '<':
                                color = (150,150,255)
                            elif string[c] == '`':
                                color = (210,0,255)
                            elif string[c] == '/':
                                color = (255,50,50)
                            sep.append(self.textfont.render(pre,True,color))
                            pre = ''
                    sep.append(self.textfont.render(pre,True,color))
                    w=0
                    h=sep[0].get_height()
                    for i in range(len(sep)):
                        w += sep[i].get_width()
                    condensed = pygame.Surface((w,h),pygame.SRCALPHA,32)
                    w=0
                    for i in range(len(sep)):
                        condensed.blit(sep[i],(w,0,sep[i].get_width(),sep[i].get_height()))
                        w += sep[i].get_width()
                    self.text.append(condensed)
                else:
                    self.text.append(self.textfont.render(string,True,color))
        except IndexError:
            return -1        
                
    def update(self):
        self.frame +=1
        self.x = self.listen.x
        self.y = self.listen.y
        pIn = self.listen.PrevInputs.copy()
        In = self.listen.inputs.copy()
        if self.xoff < Buf:self.xoff=Buf
        elif self.xoff > SCRNWDTH-Buf-self.width:self.xoff=SCRNWDTH-Buf-self.width
        if self.yoff < Buf:self.yoff=Buf
        elif self.yoff > SCRNHGHT-Buf-self.height:self.yoff=SCRNHGHT-Buf-self.height
        #EXECUTE
        if In['X'] and not pIn['X']:
            self.previousstates.append(self.state)
            if self.changestate(self.state+1) == -1:
                #failure, option was end option
                self.maxclick = True
                self.state = self.previousstates[-1]
                self.previousstates=self.previousstates[:-1]
            else:
                self.maxclick = False
        if self.maxclick:
            self.Inactivate()
        
    def Draw(self,surf,relrect):
        pygame.draw.rect(surf,(150,150,255,120),(self.xoff,self.yoff,self.width,self.height),8)
        self.canvas = self.image.copy()
        
        for i in range(len(self.text)):
            xoff = 0
            if i == 0:
                xoff = 20
            self.canvas.blit(self.text[i],(20+xoff,20+i*(self.text[i].get_height()+5),self.text[i].get_width(),self.text[i].get_height()))
        surf.blit(self.canvas,(self.xoff,self.yoff,self.width,self.height))
         
        
        
 
# state represents depth in the menu. 
#
#
#
#
#
#
#
#
#
