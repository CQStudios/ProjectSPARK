import pygame,json,glob
from pygame.locals import *
pygame.init()

global _COM,TLWDTH, TLHGHT, SCRNWDTH, SCRNHGHT, CMTLRNC, PLW, PLH, P_WALKSPEED, P_WALKACCEL, P_MAXFALLSPEED, PS3, FPS, GRAV, P_RUNACCEL, P_AIRFRICTION, P_AIRRUNACCEL, P_MAXAIRSPEED, P_MAXRISESPEED, C_WALL,C_MAI,C_PANEL,C_SPARK, C_DOOR, C_WARP, C_MOVEPLAT, CLASSES,P_MAXRUNSPEED, CUR_LEVEL, CUR_CAMERA, CUR_CLOCK, SCREEN, FLLSCRN,DISPLAYSIZE,ENABLENOGRAV,BACKGROUNDIMG,BGINCREMENT,frame, SoundBank
Sounds = glob.glob('SFX/SFX*')
Sounds.sort()
SoundBank = [pygame.mixer.Sound(i) for i in Sounds]
BGINCREMENT = 0.2
BACKGROUNDIMG = pygame.image.load('space.png')
DISPLAYSIZE = (pygame.display.Info().current_w,pygame.display.Info().current_h)
COM = json.load(open('controls.json'))
FLLSCRN = False
C_WALL = "Wall"
C_MAI = "Mai"
C_SPARK = "Spark"
C_DOOR = "Door"
C_WARP = "Warp"
C_MOVEPLAT = "MovePlat"
CLASSES = [C_WALL,C_MAI,C_SPARK,C_DOOR,C_WARP,C_MOVEPLAT]
TLWDTH = 70
TLHGHT = 70
PLW = 42
PLH = 42
SCRNWDTH = 1024 # 1268for presentation projectors
SCRNHGHT = 680 #768for presentation projectors
CMTLRNC = 20 

P_WALKSPEED = 7.5 #6 for normal, 10 for charge 
P_WALKACCEL = .3 #.6 for normal, .45 for charge
P_MAXRUNSPEED = 8.5 # 7.5 for normal modes, 13 for charge
P_RUNACCEL = 3.5 #3.5 for normal, 2.5 for charge
P_RUNDECEL = 4 #5 for normal, 3.5 for charge 

P_FRICTION = .3 #percent of horizontal acceleration to remove. .2 for normal, .08 for charge

P_SHORTHOP = -18 #-30
P_JUMPEXTENSION = -6 #-.8
P_MAXFALLSPEED = 25
P_MAXRISESPEED = -20 #-30
P_AIRRUNACCEL = 2.2 #2.2 for normal .8 for charge 
P_MAXAIRSPEED = 10 #10 for normal modes, 15 for charge

P_AIRFRICTION = .02 #.02 for normal, .01 for charge
P_DEFAULT_HEALTH = 20
P_STORY_PROGRESSION = {'Main':[0,'arbitrarytag','None'],'Side1':[3,'sidequesttag']}
GRAV = 1.5 #2.5
ENABLENOGRAV = False
OUYA = {"L1":4,"L2":2,"R1":5,"R2":5,"X":0,"O":3,"Tri":2,"Sqr":1,"Sel":16,"Str":15,"L3":6,"R3":7,"DL":10,"DU":8,"DR":11,"DD":9,"home":16,"LSX":0,"LSY":1,"RSX":3,"RSY":4}

PS3 = {"L1":10,"L2":12,"R1":11,"R2":13,"X":14,"O":13,"Tri":12,"Sqr":15,"Sel":0,"Str":3,"L3":1,"R3":2,"DL":7,"DU":4,"DR":5,"DD":6,"home":16,"LSX":0,"LSY":1,"RSX":2,"RSY":3}
FPS = 45

