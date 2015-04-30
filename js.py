import pygame, time, sys; from pygame.locals import *
pygame.init()

JS = pygame.joystick.Joystick(0)
print JS.get_name()
JS.init()
play = True
while play:
    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN:
            play = False
    print "please tilt sticks"
    time.sleep(.5)
    b = ""
    for i in range(JS.get_numaxes()):
        fl = JS.get_axis(i)
        if abs(fl) < .2:
            fl = 0.0
        b += "axis "+str(i)+": "+str(fl)+"\n"
    print b 
    print "~~~~~~~~"
sys.exit()
