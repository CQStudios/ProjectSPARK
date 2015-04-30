import pygame, json, sys
sys.path.append('/TileSets/Grass/')
from pygame.locals import *
import TestGrass
def GetMap(filename = None):
    '''objective: return a list of integers derived from a json tilemap
    '''
    Map = []
    row = []
    jsonfile = open(filename)
    mapjson = json.load(jsonfile+'.json')
    H = mapjson['layers'][0]['height']
    W = mapjson['layers'][0]['width']
    for i in range(H):
        row = []
        for j in range(W):
            row.append(mapjson['layers'][0]['data'][i*W+j])
        Map.append(row)
    return Map
    
    
    print mapjson['layers'][1]['data']
identities = GetMap()
