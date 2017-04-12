#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame
import math
import random

pygame.init()


#Physic parameters
G = 6000
N0 = 200
N = N0
sMass0 = 0.1 #mass factor for calculating planet radius
sMass = sMass0
sunMass0 = 5
sunMass = sunMass0



infos = pygame.display.Info()

#Display parameters
BLACK  = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (168,168,168)

ratio = 100
WIDTH = ratio * infos.current_w / 100
HEIGHT = ratio * infos.current_h / 100
size = (WIDTH,HEIGHT)

CX = int(WIDTH/2)
CY = int(HEIGHT/2)

zoom = 1.0
spread = 1.0

moveStep = 100
deltaT = 0.02 #time increment per frame
done = False #boolean for main loop

UN = 0 #updates number

#Keyboard boolean
leftDown = False
upDown = False
rightDown = False
downDown = False
spaceDown = False

pygame.display.set_caption("Universe")

#Font initilization
fontpath = pygame.font.match_font('Monospace')
font = pygame.font.Font(fontpath, 24)

screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

class Body(pygame.sprite.Sprite):
    def __init__(self,w,h,mass,x,y,vx,vy):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([w,h])
        self.image.fill(GREEN)
        self.image.set_colorkey(GREEN)
        self.rect = self.image.get_rect()

        self._mass = mass
        self._ax = 0
        self._ay = 0
        self._vx = vx
        self._vy = vy
        self._px = x
        self._py = y
        
        self._stillExists = True
        self._needsRebuild = False

        self.position()
 
    def update(self,world,dt):
        #global UN
        #UN += 1
        a = (0,0)
        counter = 0
        for body in world:
            if(self._stillExists and body._stillExists and body <> self):
                vect = self.pixVect2(body)
                if(vect[2] < (self._r + body._r)**2):
                    self.fusion(body)
                    self._needsRebuild = True
                    body._stillExists = False
                    body.kill()
                else:
                    norm3 = pow(vect[2],1.5)
                    gmp = G*body._mass*zoom**3
                    ax = gmp*vect[0]/norm3
                    ay = gmp*vect[1]/norm3
                    a = (a[0]+ax,a[1]+ay)
            counter += 1
        if self._needsRebuild:
            self.rebuild()
            self.position()
            self.make()
        self.newCoords(a,dt)
        self.position()

    def position(self):
        self.rect.x = self._px - self.rect.w/2
        self.rect.y = self._py - self.rect.h/2
    def newCoords(self, a, dt):
        a1x = a[0]
        a1y = a[1]
        v1x = self._vx + (self._ax+a1x)/2 * dt
        v1y = self._vy + (self._ay+a1y)/2 * dt
        self._px = (self._px + self._vx * dt + (self._ax+a1x)/4 * dt*dt)
        self._py = (self._py + self._vy * dt + (self._ay+a1y)/4 * dt*dt)
        self._ax = a1x
        self._ay = a1y
        self._vx = v1x
        self._vy = v1y

    def pixVect2(self,body): #return the vector and the square of his norm (in pixel) from self to body
        dx = body._px - self._px
        dy = body._py - self._py
        return (dx, dy, dx*dx + dy*dy)

    def fusion(self):
        raise NotImplementedError
    def rebuild(self):
        raise NotImplementedError

    def kineticE(self):
        e = "E="+str(math.floor(100*0.5*self._mass*(self._vx*self._vx+self._vy*self._vy))/100)
        text = font.render(e,False,(255,255,255))
        screen.blit(text,[WIDTH-250,40])

    def moveUp(self,offset):
        self._py -= offset
    def moveRight(self,offset):
        self._px += offset
    def moveDown(self,offset):
        self._py += offset
    def moveLeft(self,offset):
        self._px -= offset
    def zoomIn(self):
        self._px = 2*(self._px-CX)+CX
        self._py = 2*(self._py-CY)+CY
        self._vx *= 2
        self._vy *= 2
        self._ax *= 2
        self._ay *= 2
    def zoomOut(self):
        self._px = 0.5*(self._px-CX)+CX
        self._py = 0.5*(self._py-CY)+CY
        self._vx *= 0.5
        self._vy *= 0.5
        self._ax *= 0.5
        self._ay *= 0.5
class Planet(Body):
    def __init__(self,mass,x,y,vx,vy,i):
        self._r = (mass/(4*math.pi*sMass))**0.5
        Body.__init__(self,2*self._r,2*self._r,mass,x,y,vx,vy)
        self._color = WHITE
        self.make()
        self._number = i
    def make(self):
        pygame.draw.ellipse(self.image, self._color, self.image.get_rect())
    def rebuild(self):
        self.image = pygame.Surface([2*self._r,2*self._r])
        self.image.fill(GREEN)
        self.image.set_colorkey(GREEN)
        self.rect = self.image.get_rect()
        self._needsRebuild= False

    def fusion(self, planet): #fusion (colliding) plant and self into self
        newMass = self._mass + planet._mass
        self._vx = (self._mass*self._vx+planet._mass*planet._vx) / newMass
        self._vy = (self._mass*self._vy+planet._mass*planet._vy) / newMass
        self._px = (self._mass*self._px+planet._mass*planet._px) / newMass
        self._py = (self._mass*self._py+planet._mass*planet._py) / newMass
        self._mass = newMass
        self._r = (self._mass/(sMass*4*math.pi))**0.5

        global N
        N -= 1

class Sun(Planet):
    def __init__(self,mass,x,y,vx,vy,i):
        Planet.__init__(self,mass,x,y,vx,vy,i)
    def fusion(self,planet):
        Planet.fusion(self,planet)
        global sunMass
        sunMass = self._mass
def display(screen):
    text = font.render("N0:"+str(N0+1)
                       +" G:"+str(G)
                       +" sMass0:"+str(sMass0)
                       +" sunMass0:"+str(sunMass0)
                       +" spread: "+str(spread)
                       +" zoom: "+str(zoom),False,(255,255,255))
    screen.blit(text,[50,40])
    text2 = font.render(" N:"+str(N)
                       +" sunMass:"+str(sunMass),False,(255,255,255))
    screen.blit(text2,[50,90])

world = pygame.sprite.Group()

def initWorld(world):
    global N
    global sunMass
    global sunMass0
    global sMass
    global sMass0
    global zoom
    global spread
    zoom = 1
    N = N0 +1
    sunMass = sunMass0
    sMass = sMass0
    print("G: "+str(G), "sMass: "+str(sMass))
    world.empty()
    sun = Sun(sunMass,WIDTH/2,HEIGHT/2,0,0,4242)
    for i in range(N0):
        #planet = Planet(1.0,WIDTH/8+random.randrange(3*WIDTH/4),HEIGHT/8+random.randrange(3*HEIGHT/4),i)
        planet = Planet(1.0,random.randrange(spread*WIDTH)+(1-spread)*WIDTH/2,random.randrange(spread*HEIGHT)+(1-spread)*HEIGHT/2,0,0,i)
        world.add(planet)
    world.add(sun)

def initWorld2(world):
    global N
    N = 2
    sun = Sun(500,WIDTH/2,HEIGHT/2,0,0,4242)
    earth = Planet(5.0,WIDTH/2,3*HEIGHT/4,150,0,1)
    world.add(sun)
    world.add(earth)

initWorld2(world)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                for p in world:
                    p.moveDown(moveStep)
            elif event.key == pygame.K_RIGHT:
                for p in world: 
                    p.moveLeft(moveStep)
            elif event.key == pygame.K_DOWN:
                for p in world:
                    p.moveUp(moveStep)
            elif event.key == pygame.K_LEFT:
                for p in world:
                    p.moveRight(moveStep)
            if event.key == pygame.K_p:
                zoom *= 2.0
                for p in world:
                    p.zoomIn()
            elif event.key == pygame.K_m:
                zoom *= 0.5
                for p in world:
                    p.zoomOut()
            if event.key == pygame.K_SPACE:
                initWorld(world)
            elif event.key == pygame.K_a:
                N0 += 1
            elif event.key == pygame.K_q:
                N0 -= 1
            elif event.key == pygame.K_z:
                N0 += 10
            elif event.key == pygame.K_s:
                N0 -= 10
            elif event.key == pygame.K_e:
                G += 500
            elif event.key == pygame.K_d:
                G -= 500
            elif event.key == pygame.K_r:
                sMass0 *= 2.
            elif event.key == pygame.K_f:
                sMass0 *= 0.5
            elif event.key == pygame.K_t:
                sunMass0 += 1
            elif event.key == pygame.K_g:
                sunMass0 -= 1
            elif event.key == pygame.K_o:
                spread += 0.5
            elif event.key == pygame.K_l:
                spread -= 0.5
                    
    world.update(world,deltaT)
    screen.fill(BLACK)
    world.draw(screen)
    display(screen)
    pygame.display.flip()
 
    clock.tick(60)
    #print(clock.get_fps())
