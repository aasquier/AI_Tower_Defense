import random as rand
import numpy as np
import matplotlib.pyplot as plt
import pygame
from joblib import Parallel, delayed


from constants.aiConstants import *
from constants.gameConstants import *
from agent.geneticAgent import GeneticAgent
from game.game import Game

READ_FILE = True
PRINT_GRAPH = False

class GameRecord:

    def __init__(self):
        self.fitnessScore = 0
        self.enemiesKilled = 0
        self.towersRemaining = 0
        self.earnings = 0

class GeneticAlgorithm:

    def __init__(self, agent):
        self.agent = agent
        self.trainingMode = True
        self.visualMode   = False
        self.gameRecords = []
        self.towersForGeneration = []
        self.averageScores = []
        self.averageScoreMax = 0


    def run(self):
        if READ_FILE:
            print("** Reading population from file **")
            self.agent.population = self.loadData()
        else:
            self.agent.initPopulation()
        fitnessPlot = []

        self.trainingMode = True
        self.visualMode = False

        gameCount = 0
        for generation in range(MAX_GENERATIONS):

            self.gameRecords = []
            self.towersForGeneration = []

            # play all of the games for each member of the population
            for i in range(POPULATION_SIZE):

                self.towersForGeneration.append(self.agent.setTowers(self.agent.population[i]))
                self.gameRecords.append(GameRecord())

            newGameRecords = Parallel(n_jobs=-1, verbose=0, backend="threading")(map(delayed(self.runGame), self.towersForGeneration, self.gameRecords))

            newFitnessScores = []
            for data in newGameRecords:
                newFitnessScores.append(data.fitnessScore)

            self.agent.fitnessScores = newFitnessScores

            averageScore = self.normalizeFitnessOfPopulation()
            if averageScore > self.averageScoreMax:
                self.averageScoreMax = averageScore

            print('\nAverage score for generation ' + str(generation) + ' ' + str(averageScore))
            print('\nLargest Average so far: ' + str(self.averageScoreMax))

            self.averageScores.append(averageScore)

            # create the new population for crossover based off of the probabilities from the fitness scores
            self.selectPopulationForCrossover()

            # perform the crossing over of pairs in the population
            self.crossoverParents()

            # perform the random mutation on the children
            self.mutateChildren()

            gameCount += 1

            self.agent.fitnessScores = []

            self.saveData()

            if PRINT_GRAPH and generation % int((0.2 * MAX_GENERATIONS)):
                self.printGraph()

        return


    def runGame(self, towers, gameRecord):
        # bool: visualMode, bool: trainingMode, Towers, DataStruct
        game = Game(self.visualMode, self.trainingMode, towers, gameRecord)
        return game.run()

    def saveData(self):
        ''' Saves the last trained population so you can load it later and train more '''
        lastFitFile = open("lastfit_gen.txt","w")

        populationString = ''
        for citizen in self.agent.population:
            populationString += (','.join(str(int(n)) for n in citizen)) + '\n'

        lastFitFile.write(populationString)
        lastFitFile.close()

        averageScoresFile = open("averageScores.txt", "a")
        averageScoreString = ','.join(str(n) for n in self.averageScores)
        averageScoresFile.write(averageScoreString)
        averageScoresFile.close()

    def loadData(self):
        populationFile = open("lastfit_gen.txt","r")
        fileLines = populationFile.readlines()
        populationList = []
        for line in fileLines:
            line = line.strip('\n')
            line = line.split(',')

            citizen = np.zeros((len(TOWER_GRID),), dtype=int)
            i = 0
            for n in line:
                citizen[i] = int(n)
                i += 1
            populationList.append(citizen)

        print(populationList)
        return populationList

    # print the average fitness graph
    def printGraph(self):
        # plot the accuracy results from the training and test sets
        title = 'Average Fitness'
        plt.plot(self.averageScores, label=title)
        plt.xlabel('Generations')
        plt.ylabel('Average Fitness')
        plt.legend(loc='best')
        plt.show()

        return


    # return a random pivot index
    def getPivot(self):
        return rand.randint(0, STARTING_POSITIONS-1)


    def correctNumberOfTowers(self, citizen):
        towerCount = 0
        for tower in citizen:
            if tower != 0:
                towerCount += 1
        if towerCount == 20:
            return True

        return False

    # normalizes fitness scores for the entire population
    def normalizeFitnessOfPopulation(self):
        populationSize = len(self.agent.population)

        sumOfFitnessScores = sum(self.agent.fitnessScores)
        for i in range(len(self.agent.fitnessScores)):
            self.agent.fitnessScores[i] /= sumOfFitnessScores
        averageFitnessScore = sumOfFitnessScores / populationSize

        return averageFitnessScore


    # performs the crossover of pairs of parent states to start to generate new children
    def crossoverParents(self):
        newPopulation = list()
        populationSize = len(self.agent.population)

        i = 0
        while(i < populationSize):
            while True:
                pivotPoint = self.getPivot()
                child1 = np.concatenate((self.agent.population[i][:pivotPoint], self.agent.population[i+1][pivotPoint:])).tolist()
                if NUMBER_OF_CHILDREN == 2:
                    child2 = np.concatenate((self.agent.population[i+1][:pivotPoint], self.agent.population[i][pivotPoint:])).tolist()

                if self.correctNumberOfTowers(child1) and self.correctNumberOfTowers(child2):
                    break

            newPopulation.append(child1)

            if NUMBER_OF_CHILDREN == 2:
                newPopulation.append(child2)

            i += 2

        self.agent.population = newPopulation


    # perform the random mutation on the location of the n-queens
    def mutateChildren(self):
        newPopulation = list()
        for citizen in self.agent.population:
            mutate = rand.random()
            if mutate <= MUTATION_PCT:
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
            fitParents = np.argpartition(self.agent.fitnessScores, -n)[-n:]
            i = 0
            while i < (populationSize * populationMultiplier):
                for fitParent in fitParents:
                    newPopulation.append(self.agent.population[fitParent])
                i += n

        else:
            # partition the fitness scores into buckets, thats why it is skipping the first index
            for i in range(1, populationSize):
                self.agent.fitnessScores[i] += self.agent.fitnessScores[i-1]


            # randomly pick new members for the population based on their fitness probabilities
            for i in range(populationSize * populationMultiplier):
                index = 0
                current = rand.random()
                for j in range(populationSize):
                    if current <= self.agent.fitnessScores[j]:
                        index = j
                        break
                newPopulation.append(self.agent.population[index])

        self.agent.population = newPopulation


class GeneticAlgorithm2:

    def __init__(self, agent):
        self.agent = agent
        self.trainingMode = True
        self.visualMode   = False


    def run(self):
        self.agent.initPopulation()
        fitnessPlot = []

        gameCount = 0
        for generation in range(MAX_GENERATIONS):


            # play all of the games for each member of the population
            for i in range(POPULATION_SIZE):

                self.trainingMode = True
                self.visualMode = False

                self.agent.currentCitizenIndex = i
                self.agent.setTowers(self.agent.population[i])

                # bool: visualMode, bool: trainingMode, Agent: agent
                game = Game(self.visualMode, self.trainingMode, self.agent.currentTowers, None)
                game.run()

            self.normalizeFitnessOfPopulation()

            # create the new population for crossover based off of the probabilities from the fitness scores
            self.selectPopulationForCrossover()

            # perform the crossing over of pairs in the population
            self.crossoverParents()

            # perform the random mutation on the children
            self.mutateChildren()

            gameCount += 1

            # self.agent.fitnessScores = []

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

        sumOfFitnessScores = sum(self.agent.fitnessScores)
        for i in range(len(self.agent.fitnessScores)):
            self.agent.fitnessScores[i] /= sumOfFitnessScores
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
            # print('Child1: ' + len(str(child1)))
            newPopulation.append(child1)

            if NUMBER_OF_CHILDREN == 2:
                child2 = np.concatenate((self.agent.population[i+1][:pivotPoint], self.agent.population[i][pivotPoint:])).tolist()
                # print('Child2: ' + len(str(child2)))
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
            print(f"Fitness scores: {self.agent.fitnessScores}")
            fitParents = np.argpartition(self.agent.fitnessScores, -n)[-n:]
            i = 0
            while i < (populationSize * populationMultiplier):
                for fitParent in fitParents:
                    print(f"Current fit parent: {fitParent}")
                    newPopulation.append(self.agent.population[fitParent])
                i += n

        else:
            # partition the fitness scores into buckets, thats why it is skipping the first index
            for i in range(1, populationSize):
                self.agent.fitnessScores[i] += self.agent.fitnessScores[i-1]


            # randomly pick new members for the population based on their fitness probabilities
            for i in range(populationSize * populationMultiplier):
                index = 0
                current = rand.random()
                for j in range(populationSize):
                    if current <= self.agent.fitnessScores[j]:
                        index = j
                        break
                newPopulation.append(self.agent.population[index])
        self.agent.population = newPopulation
