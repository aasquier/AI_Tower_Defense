import pygame
import os
import random
from .tower import Tower
from projectile.lightningBolt import LightningBolt


class WizardTower(Tower):

    def __init__(self, position):
        super().__init__(position)
        self.maxHealth = 350                # tough and long range
        self.health = self.maxHealth
        self.attackRadius = 275
        
        self.projectileColor = (150, 150, 150)

        self.image = pygame.image.load(os.path.join("../assets/towers/wizard_tower/", "wizardTower.png"))
        self.image = pygame.transform.scale(self.image, (120, 120))


    # overrides base class version
    def loadProjectile(self, enemy):
        lightning = LightningBolt(self.position, enemy, self.closeEnemies)
        lightning.color = self.projectileColor
        return lightning