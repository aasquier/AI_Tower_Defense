import pygame
import os
import random
from enemies.zombie import Zombie
from enemies.dino import Dino
from enemies.dragon import Dragon
from enemies.robot import Robot
from towers.squareTower import SquareTower
from enemies.attackingEnemy import AttackingEnemy

TOWER_POSITIONS = [(30, 357), (99, 356), (95, 278), (85, 208), (97, 110), (230, 107), (329, 104), (453, 107), (546, 114), (536, 197), (531, 295), (530, 377), (531, 431), (656, 431), (654, 326), (758, 269), (882, 269), (1009, 270), (1117, 272), (1120, 447), (1002, 447), (884, 444), (882, 567), (774, 636), (646, 632), (513, 632), (400, 630), (283, 281), (356, 282), (288, 369), (353, 372), (350, 458), (278, 461), (348, 548), (200, 526), (118, 526), (37, 525)]

TRAINING_MODE = False  #If true will uncap framerates
VISUAL_MODE = True     #Set false to stop rendering
PLAY_BG_MUSIC = True      #Set false to turn music off
FPS = 60

#Window Dimensions
WIN_WIDTH = 1200
WIN_HEIGHT = 800

#Enemies
ENEMY_TYPES = [Zombie, Dino, Dragon, Robot]
Y_MAX_OFFSET = 30      #yOffset along enemy walking path

#Towers
TOWER_TYPES = [SquareTower]

#Sounds
BG_MUSIC = ["old_town.mp3", "get_it.mp3"]


def main():
    ''' Entry point for game '''
    #Setup Game
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    startBgMusic()
    pygame.display.set_caption("AI Tower Defense")

    #Kick off main game loop
    g = Game()
    g.run()

'''
Setup initial window and settings.
Renders all objects and background to the screen.
Handles user events (keyboard, mouse, etc)
Keeps track of score.
'''
class Game:
    def __init__(self):
        ''' Initial window setup '''
        self.width = WIN_WIDTH
        self.height = WIN_HEIGHT
        self.win = pygame.display.set_mode((self.width, self.height))
        self.enemies = [Zombie(0), Robot(0), Dino(5)]
        self.towers = [SquareTower(TOWER_POSITIONS[4]), SquareTower(TOWER_POSITIONS[10]), SquareTower(TOWER_POSITIONS[1]), SquareTower(TOWER_POSITIONS[15]), SquareTower(TOWER_POSITIONS[8]), SquareTower(TOWER_POSITIONS[len(TOWER_POSITIONS) - 2])]
        self.numEnemiesPerLevel = 10
        self.remainingEnemies = 0
        self.lives = 10
        self.money = 100
        self.health = 100
        self.bg = pygame.image.load(os.path.join("../assets", "bg.png"))
        self.bg = pygame.transform.scale(self.bg, (self.width, self.height)) #Scale to window (Make sure aspect ratio is the same)
        self.clicks = [] #Temp
        self.spawnChance = 0.015

        #Fonts
        self.uiFont = pygame.font.SysFont('lucidagrandettc', 24)


    def run(self):
        ''' Main game loop '''
        clock = pygame.time.Clock()

        while self.health >= 0:
            if TRAINING_MODE:
                clock.tick(FPS)

            self.spawnEnemies()
            self.handleEvents()
            self.towerHealthCheck()
            self.towersAttack()
            self.enemiesAttack()
            self.removeEnemies()

            if VISUAL_MODE:
                self.draw(clock.get_fps())

        pygame.quit()

    def towerHealthCheck(self):
        newTowers = []
        for tower in self.towers:
            if tower.health > 0:
                newTowers.append(tower)

        self.towers = newTowers

    def towersAttack(self):
        for tower in self.towers:
            self.enemies = tower.attack(self.enemies, self.win)

    def enemiesAttack(self):
        for enemy in self.enemies:
            if isinstance(enemy, AttackingEnemy):
                self.towers = enemy.attack(self.towers, self.win)

    def handleEvents(self):
        ''' Handle keyboard and mouse events '''

        #Check for active pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            #Store mouse clicks to determine path for enemies
            mousePosition = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.clicks.append(mousePosition)
                print(self.clicks)


    def removeEnemies(self):
        ''' Removes enemies that have walked off screen'''
        enemiesToDelete = []
        for enemy in self.enemies:
            if enemy.x > WIN_WIDTH or enemy.health <= 0:
                self.enemies.remove(enemy)
                self.remainingEnemies -= 1

                if enemy.x > WIN_WIDTH:
                    self.lives -= 1
                    self.health -= enemy.health


    def spawnEnemies(self):
        '''
        Spawns enemies with random chance based on self.spawnChance
        This value should increase as levels get more difficult
        Caps number of enemies at once with self.numEnemiesPerLevel
        '''
        shouldSpawn = random.random()
        if shouldSpawn <= self.spawnChance and self.remainingEnemies < self.numEnemiesPerLevel:
            randVerticalOffset = random.randint(-Y_MAX_OFFSET, Y_MAX_OFFSET)
            randEnemyType = random.randint(0, len(ENEMY_TYPES) - 1)
            self.enemies.append(ENEMY_TYPES[randEnemyType](randVerticalOffset))


    def draw(self, fps):
        '''
        Redraw objects onces per frame.
        Objects will be rendered sequentially,
        meaning the code at the end will be rendered above all.
        '''
        #Render the background
        self.win.blit(self.bg, (0, 0))

        #Uncomment to see clicked dots for path finding
        for p in self.clicks:
            pygame.draw.circle(self.win, (255, 0, 0), (p[0], p[1]), 5, 0)

        #Render towers
        for tower in self.towers:
            tower.draw(self.win)

        #Render enemies
        for enemy in self.enemies:
            enemy.draw(self.win)

        self.displayMoney()

        #Render UI Text Elements
        self.displayTextUI(self.win, fps)

        #Update the window
        pygame.display.update()


    def displayTextUI(self, win, fps):
        ''' Render UI elements above all other graphics '''

        #Enemies Remaining Surface UI
        numEnemiesText = "Enemies: " + str(len(self.enemies))
        numEnemiesPosition = (WIN_WIDTH-180, WIN_HEIGHT-50)
        numEnemiesColor = (255, 255, 255)
        numEnemiesSurface = self.uiFont.render(numEnemiesText, False, numEnemiesColor)
        win.blit(numEnemiesSurface, numEnemiesPosition)

        #Health Remaining Surface UI
        healthText = "Health: " + str(self.health)
        healthPosition = (WIN_WIDTH-180, WIN_HEIGHT-30)
        healthColor = (255, 255, 255)
        healthSurface = self.uiFont.render(healthText, False, healthColor)
        win.blit(healthSurface, healthPosition)

        #Frames Per Second
        fpsText = "FPS: " + str(int(fps))
        fpsPosition = (WIN_WIDTH-100, 30)
        fpsColor = (255, 255, 255)
        fpsSurface = self.uiFont.render(fpsText, False, fpsColor)
        win.blit(fpsSurface, fpsPosition)


    def displayMoney(self):
        ''' Draws an animated coin and amount of money that the player has '''
        numImages = len(self.images)

        #Set the image for # of frames ('//' means integer division)
        self.image = self.images[self.animationCount // self.animationSpeed]

        #Iterate to the next animation image
        self.animationCount += 1

        #Reset the animation count if we rendered the last image
        if self.animationCount >= (numImages * self.animationSpeed):
            self.animationCount = 0


def startBgMusic():
    if PLAY_BG_MUSIC:
        randSong = random.randint(0, len(BG_MUSIC) - 1)
        pygame.mixer.music.load("../assets/music/background/" + BG_MUSIC[randSong])
        pygame.mixer.music.play(-1)


if __name__ == "__main__":
    main()
