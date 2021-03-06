import os
import sys
import subprocess
from __builtin__ import len
import random
import cv2
import numpy as np
import theano
import theano.tensor as T
import expandTraining

class LoadPics(object):
    """Routines for loading pictures"""

    def __init__(self, path):
        random.seed(42)
        self.path = path
        # Creating Training -> Training Dev, and Testset
        classes = os.listdir(path)
        try:
            classes.remove('.DS_Store')
        except:
            pass
        d = {}
        l = 0
        self.testsets = {}
        self.trainingsets = {}
        self.x_test = None
        self.y_test = None
        self.x_valid = None
        self.y_valid = None
        self.numberOfClassed = len(classes)
        self.classes = classes
        for cc in classes:
            imgs = os.listdir(path + cc)
            random.shuffle(imgs) #Shuffels in place in one class
            d[cc] = len(imgs)
            l += len(imgs)

            testStart = int(len(imgs) * 0.75)
            testEnd = (len(imgs)) - 1
            # A small set for debuggnig
            # testStart = int(len(imgs) * 0.05)
            # testEnd = testStart + 5

            self.trainingsets[cc] = imgs[:testStart]
            self.testsets[cc] =  imgs[testStart:testEnd]
        print("Number of classes " + str(len(self.trainingsets)) + " number of images " + str(l))

    # Loading the test-data (does caching)
    def getTestData(self):
        if self.x_test is None:
            x_tmp = []
            y_tmp = []
            print("Starting to load training sets ")
            for c,files in self.testsets.iteritems():
                y = self.testsets.keys().index(c)
                for file in files:
                    pics = cv2.imread(self.path + c + '/' + file, cv2.CV_LOAD_IMAGE_GRAYSCALE) #unit8 from e.g. 34 to 255
                    x_tmp.append(np.reshape(pics / 255., len(pics)**2)) #To floats from 0 to 1
                    y_tmp.append(y)
            print("Finished, loading")
            perm = np.random.permutation(len(y_tmp))
            self.x_test = theano.shared(np.asarray(x_tmp, theano.config.floatX)[perm],borrow=True)
            self.y_test = T.cast(theano.shared(np.asarray(y_tmp, theano.config.floatX)[perm],borrow=True), 'int32')
        return self.x_test, self.y_test

    # Loading the validation data. This is are the (unperturbed) training data.
    def getValidationData(self):
        if self.x_valid is None:
            x_tmp = []
            y_tmp = []
            print("Starting to load validation sets ")
            for c,files in self.trainingsets.iteritems():
                y = self.testsets.keys().index(c) #We use the testset as a reference
                for file in files:
                    pics = cv2.imread(self.path + c + '/' + file, cv2.CV_LOAD_IMAGE_GRAYSCALE) #unit8 from e.g. 34 to 255
                    x_tmp.append(np.reshape(pics / 255., len(pics)**2)) #To floats from 0 to 1
                    y_tmp.append(y)
            print("Finished, loading validation sets")
            perm = np.random.permutation(len(y_tmp))
            self.x_valid = theano.shared(np.asarray(x_tmp, theano.config.floatX)[perm],borrow=True)
            self.y_valid = T.cast(theano.shared(np.asarray(y_tmp, theano.config.floatX)[perm],borrow=True), 'int32')
        return self.x_valid, self.y_valid

    def getClasses(self):
        return self.testsets.keys()

    def getNumberOfClassed(self):
        return self.numberOfClassed

    def giveMeNewTraining(self):
        x_tmp = []
        y_tmp = []
        print("Starting to create new training data ")
        for c,files in self.trainingsets.iteritems():
            y = self.testsets.keys().index(c) #We use the testset as a reference
            for file in files:
                image = cv2.imread(self.path + c + '/' + file, cv2.CV_LOAD_IMAGE_GRAYSCALE) #unit8 from e.g. 34 to 255
                image2 = expandTraining.distorb(image / 255.)
                # cv2.imshow('org', cv2.resize(image, (280, 280)))
                # cv2.imshow('mani', cv2.resize(image2, (280, 280)))
                # cv2.waitKey(2000)
                x_tmp.append(np.reshape(image2, len(image2)**2)) #To floats from 0 to 1
                y_tmp.append(y)
        print("Finished, creating new training data")
        perm = np.random.permutation(len(y_tmp))
        return theano.shared(np.asarray(x_tmp, theano.config.floatX)[perm],borrow=True), T.cast(theano.shared(np.asarray(y_tmp, theano.config.floatX)[perm],borrow=True), 'int32')


if __name__ == '__main__':
    path = "/Users/oli/Proj_Large_Data/kaggle_plankton/train_resized/"
    d = LoadPics(path)
    print(d.getNumberOfClassed())
    #train_set_x, train_set_y = d.giveMeNewTraining()
    #x, y = d.getTestData()
    #x, y = d.getValidationData()
    print("Finished, testdata")


