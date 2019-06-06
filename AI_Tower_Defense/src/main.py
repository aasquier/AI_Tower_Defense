import pygame

from game.game import Game
from experiment.qLearning import QLearning
from experiment.geneticAlgorithm.parallelGA import ParallelGeneticAlgorithm
from experiment.geneticAlgorithm.serialGA import SerialGeneticAlgorithm

from agent.qLearningAgent import QLearningAgent
from agent.geneticAgent import GeneticAgent

from constants.gameConstants import *


GA_MODE        = True
QLEARNING_MODE = False

MANUAL_MODE    = False
PARALLEL_MODE  = False

VISUAL_MODE    = not PARALLEL_MODE and True

COLLECT_WHOLE_GAME_DATA = True
COLLECT_INNER_GAME_DATA = True
SAVE_TO_DISK            = True

READ_FILE      = False
PRINT_GRAPHS   = False


def main():
    ''' Entry point for game '''

    # #Setup Game
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    pygame.display.set_caption("AI Tower Defense")

    if GA_MODE:
        if MANUAL_MODE:
            game = Game(True, [], None)
            game.run()
        else:
            if PARALLEL_MODE:
                gaAlgo = ParallelGeneticAlgorithm(VISUAL_MODE, READ_FILE, SAVE_TO_DISK, PRINT_GRAPHS, COLLECT_WHOLE_GAME_DATA, COLLECT_INNER_GAME_DATA)   # Parallel mode
            else:
                gaAlgo = SerialGeneticAlgorithm(VISUAL_MODE, READ_FILE, SAVE_TO_DISK, PRINT_GRAPHS, COLLECT_WHOLE_GAME_DATA, COLLECT_INNER_GAME_DATA)     # Manual mode

            gaAlgo.run()


    pygame.quit()

 

if __name__ == "__main__":
    main()
