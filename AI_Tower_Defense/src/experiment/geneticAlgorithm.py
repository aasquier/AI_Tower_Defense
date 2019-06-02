import random as rand
import numpy as np
import matplotlib.pyplot as plt
import pygame

from constants.aiConstants import *
from constants.gameConstants import *
from agent.geneticAgent import GeneticAgent
from game.game import Game


class GeneticAlgorithm:

    def __init__(self, agent):
        self.agent = agent
        self.trainingMode = False
        self.visualMode   = True


    def run(self):
        self.agent.initPopulation()
        fitnessPlot = []

        gameCount = 0
        for generation in range(MAX_GENERATIONS):


            # play all of the games for each member of the population
            for i in range(POPULATION_SIZE):

                #Setup Game
                # pygame.init()
                # pygame.font.init()
                # pygame.mixer.init()
                # pygame.display.set_caption("AI Tower Defense")

                # display every tenth generation for testing
                # if generation == gameCount and i == 0: #and gameCount != 0:
                #     self.trainingMode = False
                #     self.visualMode = True
                # else:
                #     self.trainingMode = True
                #     self.visualMode = False

                self.trainingMode = True
                self.visualMode = True

                self.agent.currentCitizenIndex = i
                self.agent.setTowers(self.agent.population[i])

                # bool: visualMode, bool: trainingMode, Agent: agent
                game = Game(self.visualMode, self.trainingMode, self.agent)
                game.run()

                fitnessPlot.append(self.agent.fitnessScores[i])

                # pygame.quit()

            self.normalizeFitnessOfPopulation()

            # create the new population for crossover based off of the probabilities from the fitness scores
            self.selectPopulationForCrossover()

            # perform the crossing over of pairs in the population
            self.crossoverParents()

            # perform the random mutation on the children
            self.mutateChildren()

            gameCount += 1

            self.agent.currentFitnessScores = []


        #printGraph(fitnessPlot, populationSize)

        return


    # print the average fitness graph
    def printGraph(self):
        populationSize = len(self.agent.population)
        # plot the accuracy results from the training and test sets
        title = 'Population = ' + str(populationSize)
        plt.plot(self.agent.fitnessValues, label=title)
        plt.xlabel('Generations')
        plt.ylabel('Average Fitness')
        plt.legend(loc='best')
        plt.show()

        return


    # return a random pivot index
    def getPivot(self):
        return rand.randint(0, STARTING_POSITIONS-1)


    # normalizes fitness scores for the entire population
    def normalizeFitnessOfPopulation(self):
        populationSize = len(self.agent.population)

        sumOfFitnessScores = sum(self.agent.currentFitnessScores)
        for i in range(len(self.agent.currentFitnessScores)):
            self.agent.currentFitnessScores[i] /= sumOfFitnessScores
        # self.agent.currentFitnessScores /= sumOfFitnessScores
        averageFitnessScore = sumOfFitnessScores / populationSize

        return averageFitnessScore


    # performs the crossover of pairs of parent states to start to generate new children
    def crossoverParents(self):
        newPopulation = list()
        populationSize = len(self.agent.population)

        i = 0
        while(i < populationSize):
            pivotPoint = self.getPivot()

            child1 = np.concatenate((self.agent.population[i][:pivotPoint], self.agent.population[i+1][pivotPoint:])).tolist()
            newPopulation.append(child1)

            if NUMBER_OF_CHILDREN == 2:
                child2 = np.concatenate((self.agent.population[i+1][:pivotPoint], self.agent.population[i][pivotPoint:])).tolist()
                newPopulation.append(child2)

            i += 2

        self.agent.population = newPopulation
        print('CROSSOVER!!')


    # perform the random mutation on the location of the n-queens
    def mutateChildren(self):
        newPopulation = list()
        for citizen in self.agent.population:
            mutate = rand.random()
            if mutate <= MUTATION_PCT:
                print("\n ** MUTATION ** \n")
                repeat = True
                while(repeat):
                    locationToMutate = rand.randint(0, STARTING_POSITIONS - 1)
                    # new tower location to mutate should not be empty
                    if citizen[locationToMutate] == 0:
                        continue
                    else:
                        while(True):
                            newLocation = rand.randint(0, STARTING_POSITIONS - 1)
                            # ensure that we are not placing it in the new location and that the new location is not occupied
                            if (newLocation != locationToMutate) and (citizen[newLocation] == 0):
                                # randomly select a new tower type  TODO  Do we want to keep the same tower type??
                                citizen[newLocation] = rand.randint(1, NUMBER_OF_TOWERS)
                                citizen[locationToMutate] = 0
                                repeat = False
                                break

            newPopulation.append(citizen)
        self.agent.population = newPopulation


    # randomly generates a new population to subject to crossover based on their fitness score ratio to the whole
    def selectPopulationForCrossover(self):
        newPopulation = list()
        populationSize = len(self.agent.population)
        # this will take the best 20% of the population for survival of the fittest
        n = populationSize // FITTEST_POPULATION_FRACTION
        if NUMBER_OF_CHILDREN == 1:
            populationMultiplier = 2
        else:
            populationMultiplier = 1

        # translate fitness scores to ranges between 0.0-1.0 to select from randomly
        if SURVIVAL_OF_THE_FITTEST:
            print(f"Fitness scores: {self.agent.currentFitnessScores}")
            fitParents = np.argpartition(self.agent.currentFitnessScores, -n)[-n:]
            i = 0
            while i < (populationSize * populationMultiplier):
                for fitParent in fitParents:
                    print(f"Current fit parent: {fitParent}")
                    newPopulation.append(self.agent.population[fitParent])
                i += n

        else:
            # partition the fitness scores into buckets, thats why it is skipping the first index
            for i in range(1, populationSize):
                self.agent.currentFitnessScores[i] += self.agent.currentFitnessScores[i-1]


            # randomly pick new members for the population based on their fitness probabilities
            for i in range(populationSize * populationMultiplier):
                index = 0
                current = rand.random()
                for j in range(populationSize):
                    if current <= self.agent.currentFitnessScores[j]:
                        index = j
                        break
                newPopulation.append(self.agent.population[index])
        self.agent.population = newPopulation