import os
import pygame
import random
import math
from .projectile import DamageType
from .rangeProjectile import RangeProjectile
from animations.fireExplosion import FireExplosion


class Cannonball(RangeProjectile):

    def __init__(self, towerPosition, enemy, enemies):
        super().__init__(towerPosition, enemy, enemies)
        self.damage = 4                         # cannonballs also do half this damage to the surroundings
        self.damageType = DamageType.exploding  # cannonballs go boom
        self.reloadTime = 30                  # reload time long
        self.velocity = 100                     # cannonballs are fast
        self.attackRadius = 40                  # radius to take secondary damage on
        self.detonationRange = 50

        self.numImages = 5
        self.width = 30
        self.height = 30
        self.attackAnimationDuration = 5
        self.attackSound = pygame.mixer.Sound("../assets/sounds/cannonShot.flac")
        self.attackSound.set_volume(0.15)

        #Load images
        for i in range(0, self.numImages):
            image = pygame.image.load(os.path.join("../assets/projectiles/cannonball", "cannonball" + str(i) + ".png"))
            self.images.append(pygame.transform.scale(image, (self.width, self.height)))
        self.image = self.images[0]


    # calulates the addtional surrounding damage
    def explosiveDamage(self, ticks):
        for enemy in self.enemies:
            dist = (enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2
            #Use radius squared to avoid taking square roots of distance
            if dist <= self.attackRadius ** 2:
                # if not self.trainingMode:
                #     self.attackSound.play()
                enemy.hit((self.damage / 2), self.damageType, ticks)


    # returns a residual animation
    def finalAnimation(self, position):
        return FireExplosion(position)
