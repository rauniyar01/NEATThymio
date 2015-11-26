import os
import time
import gobject
import glib
import dbus
import dbus.mainloop.glib
import logging
from helpers import *

CURRENT_FILE_PATH = os.path.abspath(os.path.dirname(__file__))
OUTPUT_PATH = os.path.join(CURRENT_FILE_PATH, 'output')
PICKLED_DIR = os.path.join(CURRENT_FILE_PATH, 'pickled')
FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')

class NEATTask:
	def __init__(self, thymioController, debug=False, experimentName='NEAT_task', evaluations=1000, timeStep=0.005, activationFunction='tanh', popSize=1, generations=100, solvedAt=1000):
		self.thymioController = thymioController
		self.logger = logging.getLogger('simulationLogger')
		logLevel = logging.INFO
		if debug:
			logLevel = logging.DEBUG
		self.logger.setLevel(logLevel)
		outputDir = os.path.join(OUTPUT_PATH, experimentName)
		mkdir_p(outputDir)
		mkdir_p(PICKLED_DIR)
		logFilename = os.path.join(outputDir, experimentName + '_sim_debug.log')
		simHandler = logging.FileHandler(logFilename)
		simHandler.setFormatter(FORMATTER)
		self.logger.addHandler(simHandler)

		self.evaluations = evaluations
		self.timeStep = timeStep
		self.activationFunction = activationFunction
		self.popSize = popSize
		self.generations = generations
		self.solvedAt = solvedAt

	def _step(self, evaluee, callback):
		raise NotImplemented('Step method not implemented')

	def evaluate(self, evaluee):
		self.evaluations_taken = 0
		self.fitness = 0
		self.loop = gobject.MainLoop()
		def update_fitness(task, fit):
			task.fitness += fit
		def main_lambda(task):
			if task.evaluations_taken == self.evaluations:
				stopThymio(thymioController)
				task.loop.quit()
				return False 
			ret_value =  self._step(evaluee, lambda (fit): update_fitness(self, fit))
			task.evaluations_taken += 1
			# time.sleep(TIME_STEP)
			return ret_value
		gobject.timeout_add(int(self.timeStep * 1000), lambda: main_lambda(self))
		# glib.idle_add(lambda: main_lambda(self))
		self.loop.run()

		fitness = max(self.fitness, 1)
		print 'Fitness at end: %d' % fitness

		# self.thymioController.SendEventName('PlayFreq', [700, 0], reply_handler=dbusReply, error_handler=dbusError)
		# time.sleep(.3)
		# self.thymioController.SendEventName('PlayFreq', [700, -1], reply_handler=dbusReply, error_handler=dbusError)
		# time.sleep(0.1)
		time.sleep(1)

		return { 'fitness': fitness }

	def solve(self, evaluee):
		return int(self.evaluate(evaluee)['fitness'] >= self.solvedAt)

	def getFitness(self, motorspeed, observation):
		raise NotImplemented('Fitness method not implemented')

	def getLogger(self):
		return self.logger
