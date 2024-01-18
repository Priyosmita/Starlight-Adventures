import pygame
from pygame.locals import*
from os import path
import pickle
from pygame.sprite import Group
from pygame import mixer
ALPHA=(255,255,255)
pygame.mixer.pre_init(44100,-16,2,512)
mixer.init()
pygame.init()
clock=pygame.time.Clock()
fps=60

#background and window
screen= pygame.display.set_mode((1280,720))
pygame.display.set_caption("Starlight Adventures")
bg_img = pygame.image.load('bg.png')   
bg_img = pygame.transform.scale(bg_img,(1280,720))
bgloop=0
cross=False
backdropbox = screen.get_rect()
restartimage=pygame.image.load('restart.png')
restartimage.set_colorkey(ALPHA)  # set alpha
restartimage.convert_alpha()  # optimise alpha
startimage=pygame.image.load('start.png')
startimage.set_colorkey(ALPHA)  # set alpha
startimage.convert_alpha()  # optimise alpha
exitimage=pygame.image.load('exit.png')
exitimage.set_colorkey(ALPHA)  # set alpha
exitimage.convert_alpha()  # optimise alpha
winimg=pygame.image.load('victory trophy.png')
winimg=pygame.transform.scale(winimg,(125,125))
winimg.set_colorkey(ALPHA)  # set alpha
winimg.convert_alpha()  # optimise alpha
nameimg=pygame.transform.scale(winimg,(125,125))
nameimg.set_colorkey(ALPHA)  # set alpha
nameimg.convert_alpha()  # optimise alpha

#sound effects
pygame.mixer.music.load('Permission To Dance (Instrumental).mp3')
pygame.mixer.music.set_volume(0.15)
pygame.mixer.music.play(-1,0.0,0)
coinmusic=pygame.mixer.Sound('coin.wav.mp3')
coinmusic.set_volume(0.6)
jumpmusic=pygame.mixer.Sound('jump.wav.mp3')
jumpmusic.set_volume(0.1)
gameovermusic=pygame.mixer.Sound('gameover.wav.mp3')
gameovermusic.set_volume(0.5)
victorymusic=pygame.mixer.Sound('victory.mp3')
victorymusic.set_volume(0.5)
doormusic=pygame.mixer.Sound('door.mp3')
doormusic.set_volume(0.6)
clickmusic=pygame.mixer.Sound('click.mp3')
clickmusic.set_volume(0.5)

#define font
deadfont=pygame.font.SysFont('Comic Sans MS',80)
font=pygame.font.SysFont('Comic Sans MS',20)
winfont=pygame.font.SysFont('Comic Sans MS',80)
#define colour
black=(0,0,0)
white=(255,255,255)
red=(255,0,0)
gold=(255,215,0)

#variables
tile_size=40
gameover=0
mainmenu=True
level=1
score=0
totscore=0


#functions
def draw_grid(): #gridlines
	for c in range(36):
		#vertical lines
		pygame.draw.line(screen, 'white', (c * tile_size, 0), (c * tile_size, 720))
		#horizontal lines
		pygame.draw.line(screen, 'white', (0, c * tile_size), (1280, c * tile_size))
def drawtext(text,font,colour,x,y):
    img=font.render(text,True,colour)
    screen.blit(img,(x,y))
def resetlevel(level):
    player.reset(60,720-240)
    kukoshibogroup.empty()
    spidergroup.empty()
    spikegroup.empty()
    lavagroup.empty()
    doorgroup.empty()
    entrygroup.empty()
    coingroup.empty()
    platformgroup.empty()
    bossgroup.empty()
    if path.exists(f'lev{level}_data'):
        with open(f'lev{level}_data','rb') as f:
            world_data=pickle.load(f)
    w=world(world_data)
    return w

class Button():
    def __init__(self,x,y,image):
        self.image=image
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.clicked=False
    def draw(self):
        action=False
        self.clicked=False
        pos=pygame.mouse.get_pos()   #getting cursor location
        if self.rect.collidepoint(pos):     #mouse over condition
            if pygame.mouse.get_pressed()[0] and self.clicked==False:  #left mouse button
                action=True
                clickmusic.play()
                self.clicked=True
        if pygame.mouse.get_pressed()[0]==0:
            self.clicked==False
        screen.blit(self.image,self.rect)
        return action
    
class hero():
    def __init__(self,x,y):
        self.reset(x,y)
    def update(self,gameover):
        dx=0
        dy=0
        walkcooldown=5
        collisionthreshold=20
        if gameover==0:
            #controls
            key=pygame.key.get_pressed()
            if key[pygame.K_UP] and self.jump==False and self.inair==False : #or key[pygame.K_w])
                jumpmusic.play()
                self.vely=-15
                self.jump=True
            if key[pygame.K_UP]==False: # and key[pygame.K_w]==False:
                self.jump=False
            if key[pygame.K_LEFT]:# or key[pygame.K_a]:
                dx-=5
                self.counter+=1
                self.face=-1
            if key[pygame.K_RIGHT]: #or key[pygame.K_d]:
                dx+=5
                self.counter+=1
                self.face=1
            if key[pygame.K_LEFT]==False and key[pygame.K_RIGHT]==False:
                self.counter=0
                self.index=0
                if self.face==1:
                    self.image=self.imagesright[self.index]
                if self.face==-1:
                    self.image=self.imagesleft[self.index]
            #animation
            if self.counter>walkcooldown:
                self.counter=0
                self.index+=1
                if self.index>=len(self.imagesright):
                    self.index=0
                if self.face==1:
                    self.image=self.imagesright[self.index]
                if self.face==-1:
                    self.image=self.imagesleft[self.index]
            #gravity
            self.vely+=1
            if self.vely>10:
                self.vely=10
            dy+=self.vely
            #collision detection
            self.inair=True
            for tile in w.tilelist:
                #x direction collison
                if tile[1].colliderect(self.rect.x+dx,self.rect.y,self.width,self.height):  
                    dx=0 #stop moving 
                #y direction collision
                if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):   
                    if self.vely<0:  #collision with head while jumping
                        dy=tile[1].bottom-self.rect.top
                        self.vely=0
                    elif self.vely>=0:  #collision when on ground (falling)
                        dy=tile[1].top-self.rect.bottom
                        self.vely=0
                        self.inair=False
            #collion detection with kukoshibo
            if pygame.sprite.spritecollide(self,kukoshibogroup,False):
                gameovermusic.play()
                gameover=-1
            #collision with spider
            if pygame.sprite.spritecollide(self,spidergroup,False):
                gameovermusic.play()
                gameover=-1
            #collion detection with lava
            if pygame.sprite.spritecollide(self,lavagroup,False):
                gameovermusic.play()
                gameover=-1
            #collision detection with door
            if pygame.sprite.spritecollide(self,doorgroup,False):
                doormusic.play()
                gameover=1
            #collision detection with boss
            if pygame.sprite.spritecollide(self,bossgroup,False):
                gameovermusic.play()
                gameover=-1
            #collision detection with spike
            if pygame.sprite.spritecollide(self,spikegroup,False):
                gameovermusic.play()
                gameover=-1
            #collision with moving platforms
            for platform in platformgroup:
                #collion in x axis
                if platform.rect.colliderect(self.rect.x+dx,self.rect.y,self.width,self.height):
                    dx=0
                #collision in y axis
                if platform.rect.colliderect(self.rect.x,self.rect.y+dy,self.width,self.height): 
                    #below platform
                    if abs((self.rect.top+dy)-platform.rect.bottom)<collisionthreshold:
                        self.vely=0
                        dy=platform.rect.bottom-self.rect.top
                    #above platform
                    elif abs((self.rect.bottom+dy)-platform.rect.top)<collisionthreshold:
                        self.rect.bottom=platform.rect.top-1
                        dy=0
                        self.inair=False
                    #move sideways with the platform
                    if platform.movex!=0:
                        self.rect.x+=platform.move
            #hero coordinates
            self.rect.x+=dx
            self.rect.y+=dy
        elif gameover==-1:
            self.image=self.dead
            if self.rect.y>40:
                self.rect.y-=5
        if self.rect.bottom>720:
            self.rect.bottom=720
            dy=0
            
        screen.blit(self.image,self.rect)   #spawning hero
        #pygame.draw.rect(screen,'black',self.rect,1)  #for collision detection
        return gameover
    def reset(self,x,y):
        self.imagesright=[]
        self.imagesleft=[]
        self.imagesjumpleft=[]
        self.imagesjumpright=[]
        self.imagesjumpleft=[]
        self.index=0
        self.counter=0
        for n in range (1,5):
            imgright=pygame.image.load('heroine'+str(n)+'.png')
            imgright=pygame.transform.scale(imgright,(50,80))
            imgleft=pygame.transform.flip(imgright,True,False)
            imgright.convert_alpha()  # optimise alpha
            imgright.set_colorkey(ALPHA)  # set alpha
            imgleft.convert_alpha()  # optimise alpha
            imgleft.set_colorkey(ALPHA)  # set alpha
            self.imagesright.append(imgright)
            self.imagesleft.append(imgleft)
        self.dead=pygame.image.load('gameover.png')
        self.dead=pygame.transform.scale(self.dead,(60,60))
        self.dead.set_colorkey(ALPHA)  # set alpha
        self.dead.convert_alpha()  # optimise alpha
        self.image=self.imagesright[self.index]
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.width=self.image.get_width()
        self.height=self.image.get_height()
        self.vely=0
        self.jump=False
        self.face=0
        self.inair=True
        
class world():
    def __init__(self,data):
        self.tilelist=[]
        ground=pygame.image.load('ground.png')
        border=pygame.image.load('border.png')
        rowcount=0
        for row in data:
            colcount=0
            for tile in row:
                if tile==1:
                    img=pygame.transform.scale(ground,(tile_size,tile_size))
                    img_rect=img.get_rect()
                    img_rect.x=colcount*tile_size
                    img_rect.y=rowcount*tile_size
                    tile=(img,img_rect)
                    self.tilelist.append(tile)
                if tile==2:
                    img=pygame.transform.scale(border,(tile_size,tile_size))
                    img_rect=img.get_rect()
                    img_rect.x=colcount*tile_size
                    img_rect.y=rowcount*tile_size
                    tile=(img,img_rect)
                    self.tilelist.append(tile)
                if tile==3:
                    kukoshibo=Kukoshibo(colcount*tile_size,rowcount*tile_size-18)
                    kukoshibogroup.add(kukoshibo)
                if tile==4:
                    lava=Lava(colcount*tile_size,rowcount*tile_size+(tile_size//2))
                    lavagroup.add(lava)
                if tile==5:
                    door=Door(colcount*tile_size,rowcount*tile_size-30)
                    doorgroup.add(door)
                if tile==6:
                    entry=Entry(colcount*tile_size,rowcount*tile_size-30)
                    entrygroup.add(entry)
                if tile==7:
                    coin=Coin(colcount*tile_size+(tile_size//2),rowcount*tile_size+(tile_size//2))
                    coingroup.add(coin)
                if tile==8: #right left plat
                    platform=Platform(colcount*tile_size,rowcount*tile_size,1,0)
                    platformgroup.add(platform)
                if tile==9: #updown plat
                    platform=Platform(colcount*tile_size,rowcount*tile_size,0,1)
                    platformgroup.add(platform)
                if tile==10: #spider
                    spider=Spider(colcount*tile_size,rowcount*tile_size-18)
                    spidergroup.add(spider)
                if tile==11:
                    spike=Spike(colcount*tile_size,rowcount*tile_size)
                    spikegroup.add(spike)
                if tile==12: #boss
                    boss=Boss(colcount*tile_size,rowcount*tile_size)
                    bossgroup.add(boss)
                colcount+=1
            rowcount+=1
    def draw(self):
        for tile in self.tilelist:
            screen.blit(tile[0],tile[1])
            #pygame.draw.rect(screen,'black',tile[1],1) #for collision detection
            
class Kukoshibo(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load('enemy.png')
        self.image=pygame.transform.scale(self.image,(60,60))
        self.image.convert_alpha()  # optimise alpha
        self.image.set_colorkey(ALPHA)  # set alpha
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.move=1
        self.movecount=0
    def update(self):
        self.rect.x+=self.move
        self.movecount+=1
        if abs(self.movecount)>=50:
            self.move*=-1
            self.movecount*=-1
        #pygame.draw.rect(screen,'black',self.rect,1)
        
class Spider(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load('spider.png')
        self.image=pygame.transform.scale(self.image,(80,60))
        self.image.convert_alpha()  # optimise alpha
        self.image.set_colorkey(ALPHA)  # set alpha
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.move=1
        self.movecount=0
    def update(self):
        self.rect.y+=self.move
        self.movecount+=1
        if abs(self.movecount)>=50:
            self.move*=-1
            self.movecount*=-1
        #pygame.draw.rect(screen,'black',self.rect,1)
           
class Lava(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load('lava1.png')
        self.image=pygame.transform.scale(self.image,(tile_size,tile_size))
        self.image.convert_alpha()  # optimise alpha
        self.image.set_colorkey(ALPHA)  # set alpha
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y 
        
class Spike(pygame.sprite.Sprite):
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.images=[]
		for num in range(1,3):
			img = pygame.image.load(f'pin{num}.png')
			img=pygame.transform.scale(img,(40,40))
			img.convert_alpha()
			img.set_colorkey(ALPHA)
			self.images.append(img)
		self.index=0
		self.image=self.images[self.index]
		self.rect=self.image.get_rect()
		self.rect.x=x
		self.rect.y=y
		self.counter=0
	def update(self):
		move_speed=4
		self.counter+=1
		if self.counter>=move_speed and self.index<len(self.images)-1:
			self.counter=0
			self.index+=1
			self.image=self.images[self.index]
			
		if self.index>=len(self.images)-1 and self.counter >= move_speed:
			self.counter=0
			self.index=0
			self.image=self.images[self.index]       
                            
class Coin(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load('coin.png')
        self.image=pygame.transform.scale(self.image,(tile_size//2,tile_size//2))
        self.image.convert_alpha()  # optimise alpha
        self.image.set_colorkey(ALPHA)  # set alpha
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)
        
class Door(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load('door.png')
        self.image=pygame.transform.scale(self.image,(tile_size*2,int(tile_size*2.85)))
        self.image.convert_alpha()  # optimise alpha
        self.image.set_colorkey(ALPHA)  # set alpha
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y 
        
class Entry(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load('entry.png')
        self.image=pygame.transform.scale(self.image,(tile_size*2,int(tile_size*2.85)))
        self.image.convert_alpha()  # optimise alpha
        self.image.set_colorkey(ALPHA)  # set alpha
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y 

class Platform(pygame.sprite.Sprite):  #moving platforms
    def __init__(self,x,y,movex,movey):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load('ground.png')
        self.image=pygame.transform.scale(self.image,(tile_size,tile_size//2))
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.move=1
        self.movecount=0
        self.movex=movex
        self.movey=movey
    def update(self):
        self.rect.x+=self.move*self.movex
        self.rect.y+=self.move*self.movey
        self.movecount+=1
        if abs(self.movecount)>=50:
            self.move*=-1
            self.movecount*=-1
        pygame.draw.rect(screen,'black',self.rect,1)

class Boss(pygame.sprite.Sprite):       
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load('boss.png')
        self.image=pygame.transform.scale(self.image,(130,230))
        self.image.convert_alpha()  # optimise alpha
        self.image.set_colorkey(ALPHA)  # set alpha
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.moveupdown=3
        self.moveside=6
        self.movecount=0
    def update(self):
            self.rect.x+=self.moveside
            self.rect.y+=self.moveupdown
            self.movecount+=1
            
            if self.movecount >=120:
                self.rect.y-=self.moveupdown
                self.rect.x-=self.moveside
                self.rect.x-=self.moveside
                self.movecount+=1
                if self.movecount>=333:
                    self.rect.x-=self.moveside
                    self.rect.y-=self.moveupdown
                    self.rect.y+=self.moveupdown
                    self.rect.x+=self.moveside
                    self.rect.x+=self.moveside
                    self.rect.y-=self.moveupdown
                    self.rect.x+=self.moveside
                    self.movecount+=1
                    if self.movecount>=707:
                        self.rect.x+=self.moveside
                        self.rect.y+=self.moveupdown
                        self.rect.y-=self.moveupdown
                        self.rect.x-=self.moveside
                        self.rect.x-=self.moveside
                        self.rect.y+=self.moveupdown
                        self.rect.x-=self.moveside
                        self.rect.x-=self.moveside
                        self.movecount+=4
                        if self.movecount>=1200:
                            self.movecount=0
                            self.rect.x=160
                            self.rect.y=80
                            self.moveside*=-1
                            self.moveside*=-1
                        
#initialization 
player=hero(60,720-240)
kukoshibogroup=pygame.sprite.Group()
spidergroup=pygame.sprite.Group()
lavagroup=pygame.sprite.Group()
spikegroup=pygame.sprite.Group()
coingroup=pygame.sprite.Group()
doorgroup=pygame.sprite.Group()
entrygroup=pygame.sprite.Group()
platformgroup=pygame.sprite.Group()
bossgroup=pygame.sprite.Group()

if path.exists(f'lev{level}_data'):
    with open(f'lev{level}_data','rb') as f:
        world_data=pickle.load(f)
w=world(world_data)
#buttons
restart=Button(530,350,restartimage)
start=Button(300,350,startimage)
exit=Button(790,350,exitimage)

#main loop
while not cross:
    clock.tick(fps)
    screen.fill((0,0,0))
    screen.blit(bg_img,(bgloop,0))
    screen.blit(bg_img,(1280+bgloop,0))
    #current_time=pygame.time.get_ticks()
    
    
    if (bgloop==-1280):  #looping bg
        screen.blit(bg_img,(1280+bgloop,0))
        bgloop=0
    bgloop-=1
    if mainmenu==True:
        if start.draw():
            mainmenu=False
        if exit.draw():
            cross=True
    else:
        w.draw()
        if gameover==0:
            kukoshibogroup.update()
            spidergroup.update()
            platformgroup.update()
            bossgroup.update()
            spikegroup.update()
            #score upgradation
            if pygame.sprite.spritecollide(player,coingroup,True):
                score+=1
                coinmusic.play()
            drawtext('Level: '+str(level),font,black,tile_size,7)
            drawtext('Coins: '+str(score),font,black,tile_size+150,7)
            drawtext('Total Score: '+str(totscore),font,black,tile_size+300,7)
        kukoshibogroup.draw(screen)
        spidergroup.draw(screen)
        lavagroup.draw(screen)
        spikegroup.draw(screen)
        coingroup.draw(screen)
        doorgroup.draw(screen)
        entrygroup.draw(screen)
        platformgroup.draw(screen)
        bossgroup.draw(screen)
        gameover=player.update(gameover)
        #spawning restart button after player's death
        if gameover==-1:
            drawtext('GAME OVER',deadfont,red,400,200)
            if restart.draw():
                world_data=[]
                w=resetlevel(level)
                gameover=0
                score=0
        #entering new level
        if gameover==1:
            level+=1
            if level<=7:
                #reset level
                world_data=[]
                w=resetlevel(level)
                gameover=0
                totscore+=score
            else:
                #restart game
                #victory
                screen.blit(winimg,(600,220))
                totscore+=score
                drawtext('VICTORY',winfont,gold,470,100)
                #victorymusic.play()
                if restart.draw():
                    level=1
                    world_data=[]
                    w=resetlevel(level)
                    gameover=0
                    totscore=0
                    score=0
        #draw_grid()
    for event in pygame.event.get():
        if event.type==pygame.QUIT: #quitting by cross button
            cross=True
        if event.type==pygame.KEYDOWN:
            if event.key==ord('q'):  #alternative quitting using q key
                cross=True
    pygame.display.update() 