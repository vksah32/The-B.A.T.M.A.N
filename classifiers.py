# Template by Bruce Maxwell
# Spring 2015
# CS 251 Project 8
#
# Classifier class and child definitions

import sys
import data
import analysis as an
import numpy as np
import numpy.matlib
import math
import scipy
import csv

import scipy.cluster.vq as vq


class Classifier:
    def __init__(self, type):
        '''The parent Classifier class stores only a single field: the type of
        the classifier.  A string makes the most sense.

        '''
        self._type = type

    def type(self, newtype=None):
        '''Set or get the type with this function'''
        if newtype != None:
            self._type = newtype
        return self._type

    def confusion_matrix(self, truecats, classcats):
        '''Takes in one Nx1 matrices of zero-index numeric categories(classcats)//truecats may not be aero indexed until now and
        computes the confusion matrix. The rows represent true
        categories, and the columns represent the classifier output.'''

        #WE ARE ASSUMING THAT TEST CATEGORIES WILL HAVE SAME NUMBER OF CLASSES AS TRAINING CLASSES
        unique,mapping = np.unique(np.array(truecats.T),return_inverse= True)

        cfmtx = np.matlib.zeros((len(unique), len(unique)))

        for i in range(truecats.shape[0]):

            cfmtx[int(mapping[i]), int(classcats[i, 0])] += 1

        return cfmtx

    def confusion_matrix_str(self, cmtx,  actual_headers):
        '''Takes in a confusion matrix and returns a string suitable for printing.'''

        cmtx_list = cmtx.tolist()


        cmtx_list = [actual_headers]+cmtx_list

        t=""
        # print cmtx_list, "list_confusion"
        for i in range(len(cmtx_list)):
            # print actual_headers, i
            s = "%10s"%"label" if i == 0 else "%10s"%str(actual_headers[i-1])

            for val in cmtx_list[i]:
                # print val
                s += "%10s" % (val)
            t+= s+"\n"
        return t


    def __str__(self):
        '''Converts a classifier object to a string.  Prints out the type.'''
        return str(self._type)


class NaiveBayes(Classifier):
    '''NaiveBayes implements a simple NaiveBayes classifier using a
    Gaussian distribution as the pdf.

    '''

    def __init__(self, dataObj=None, headers=[], categories=None):
        '''Takes in a Data object with N points, a set of F headers, and a
        matrix of categories, one category label for each data point.'''

        # call the parent init with the type
        Classifier.__init__(self, 'Naive Bayes Classifier')

        self.categories = categories

        # store the headers used for classification
        self.headers = headers

        # self.num_features = len(headers)  # number of features

        self.num_classes = 0  # number of classes
        self.class_labels = []  # original class labels

        # unique data for the Naive Bayes: means, variances, scales
        self.class_means = []  # intialized to empty list, will be converted to np matrix
        self.class_vars = []
        self.class_scales = []

        if dataObj != None:
            A = dataObj.get_data(self.headers)
            self.build(A, self.categories)




            # if given data,
            # call the build function

    def build(self, A, categories):
        '''Builds the classifier give the data points in A and the categories'''

        # figure out how many categories there are and get the mapping (np.unique)
        unique, mapping = np.unique(np.array(categories.T), return_inverse=True)

        self.class_labels = unique

        self.num_classes = len(unique)
        self.num_features = A.shape[1]

        self.categories = mapping  # type array

        # print mapping, "mapping"
        # means = []
        for i in range(self.num_classes):
            tempdata = A[(mapping == i), :]
            self.class_means.append(np.mean(tempdata, axis=0).tolist()[0])
            self.class_vars.append(np.var(tempdata, axis=0).tolist()[0])
            # self.class_scales.append()
        # print self.class_means
        self.class_means = np.matrix(self.class_means)
        self.class_vars = np.matrix(self.class_vars)
        self.class_scales = 1 / np.sqrt(2 * math.pi * self.class_vars)











        # create the matrices for the means, vars, and scales
        # the output matrices will be categories (C) x features (F)
        # compute the means/vars/scales for each class
        # store any other necessary information: # of classes, # of features, original labels

        return

    def classify(self, A, return_likelihoods=False):
        '''Classify each row of A into one category. Return a matrix of
        category IDs in the range [0..C-1], and an array of class
        labels using the original label values. If return_likelihoods
        is True, it also returns the NxC likelihood matrix.

        '''

        assert self.class_means.shape[1] == A.shape[1]



        # make a matrix that is N x C to store the probability of each
        # class for each data point
        P = np.matlib.zeros(
            (A.shape[0], self.num_classes))  # a matrix of zeros that is N (rows of A) x C (number of classes)

        # calculate the probabilities by looping over the classes
        # with numpy-fu you can do this in one line inside a for loop

        for i in range(self.num_classes):
            P[:, i] = np.prod(np.multiply(self.class_scales[i, :], np.exp( -1 * np.square(A - self.class_means[i, :]) / (2 * self.class_vars[i, :]))), axis=1)

            # print C.shape, P[:,i].shape

        # print P, "P"
        # calculate the most likely class for each data point
        cats = np.argmax(P, axis=1)  # take the argmax of P along axis 1

        # use the class ID as a lookup to generate the original labels
        labels = self.class_labels[cats]

        if return_likelihoods:
            return cats, labels, P

        # print cats, "cats", "\n", labels, "labels", "line 169"

        return cats, labels

    def __str__(self):
        '''Make a pretty string that prints out the classifier information.'''
        s = "\nNaive Bayes Classifier\n"
        for i in range(self.num_classes):
            s += 'Class %d --------------------\n' % (i)
            s += 'Mean  : ' + str(self.class_means[i, :]) + "\n"
            s += 'Var   : ' + str(self.class_vars[i, :]) + "\n"
            s += 'Scales: ' + str(self.class_scales[i, :]) + "\n"

        s += "\n"
        return s

    def write(self, filename):
        '''Writes the Bayes classifier to a file.'''
        # extension
        return

    def read(self, filename):
        '''Reads in the Bayes classifier from the file'''
        # extension
        return


class KNN(Classifier):
    def __init__(self, dataObj=None, headers=[], categories=None, K=None):
        '''Take in a Data object with N points, a set of F headers, and a
        matrix of categories, with one category label for each data point.'''

        # call the parent init with the type
        Classifier.__init__(self, 'KNN Classifier')

        # store the headers used for classification
        self.headers = headers
        # number of classes and number of features
        self.num_classes = 0
        self.num_features = 0

        # original class labels
        self.class_labels = []

        # unique data for the KNN classifier: list of exemplars (matrices)
        self.exemplars = []
        if dataObj != None:
            A = dataObj.get_data(headers)
            self.build(A, categories, K)

    def build(self, A, categories, K=None):
        '''Builds the classifier give the data points in A and the categories'''

        # figure out how many categories there are and get the mapping (np.unique)
        unique, mapping = np.unique(np.array(categories.T), return_inverse=True)
        # print "unique","mapping", unique, mapping
        self.num_classes = len(unique)
        self.num_features = A.shape[1]
        self.class_labels = unique

        for i in range(self.num_classes):
            exemplar = A[(mapping == i), :]

            if K == None:
                # append to exemplars a matrix with all of the rows of A where the category/mapping is i
                # print exemplar.shape, "exemplar.shape", i, "ith exemplar"
                self.exemplars.append(exemplar)
            elif K != None and isinstance(K, int):  # check if K is an integer
                # W = vq.whiten(exemplar)

                codebook = an.kmeans_init(exemplar, K)

                (codebook, codes, errors) = an.kmeans_algorithm(exemplar, codebook) # run K-means on the rows of A where the category/mapping is i
                # print codebook.shape, "codebook", "ith codebook", i, K, "cluster"
                self.exemplars.append(codebook)  # append the codebook to the exemplars


        self.write("KNN_classifier.csv")

        return

    def classify(self, A, K=5, return_distances=False):
        '''Classify each row of A into one category. Return a matrix of
        category IDs in the range [0..C-1], and an array of class
        labels using the original label values. If return_distances is
        True, it also returns the NxC distance matrix.

        The parameter K specifies how many neighbors to use in the
        distance computation. The default is three.'''
        # print A, "A", self.exemplars, "exemplars"

        # error check to see if A has the same number of columns as the class means
        if A.shape[1] != self.num_features:
            print A.shape[1], self.num_features
            print "check data dimensions"
            return



        # make a matrix that is N x C to store the distance to each class for each data point
        D = np.matlib.zeros((A.shape[0], self.num_classes))  # a matrix of zeros that is N (rows of A) x C (number of classes)
        for k in range(self.num_classes):
            # make a temporary matrix that is N x M where M is the number of exemplars (rows in exemplars[i])

            temp = np.matrix(scipy.spatial.distance.cdist(A,self.exemplars[k],'euclidean'))

            temp = np.sort(temp,axis =1)
            # print temp, "temp sorted"
            D[:,k] = np.sum(temp[:,:K], axis =1) # sum the first K columns # this is the distance to the first class



        # calculate the most likely class for each data point
        cats = np.argmin(D,axis=1)  # take the argmin of D along axis 1


        # use the class ID as a lookup to generate the original labels
        labels = self.class_labels[cats]

        if return_distances:
            return cats, labels, D

        return cats, labels

    def __str__(self):
        '''Make a pretty string that prints out the classifier information.'''
        s = "\nKNN Classifier\n"
        for i in range(self.num_classes):
            s += 'Class %d --------------------\n' % (i)
            s += 'Number of Exemplars: %d\n' % (self.exemplars[i].shape[0])
            s += 'Mean of Exemplars  :' + str(np.mean(self.exemplars[i], axis=0)) + "\n"

        s += "\n"
        return s


    def write(self, filename):

        '''Writes the KNN classifier to a file.'''
        with open(filename, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(["A" + str(i) for i in range(self.exemplars[0].shape[1]+1)])
            spamwriter.writerow(["numeric"]* (self.exemplars[0].shape[1]+1))

            for i in range(len(self.exemplars)):
                for row in self.exemplars[i].tolist():
                    spamwriter.writerow(row+[str(i)])




        # extension
        return



    def read(self, filename):
        '''Reads in the KNN classifier from the file and populates the fields as we did in build function'''
        # extension
        self.exemplars = []

        tempData = data.Data(filename)
        A = tempData.get_data(tempData.get_raw_headers()[:-1])
        # print A, A.shape
        categories = tempData.get_data([tempData.get_raw_headers()[-1]])
        unique, mapping = np.unique(np.array(categories.T), return_inverse=True)
        # print "unique","mapping", unique, mapping
        self.num_classes = len(unique)
        self.num_features = A.shape[1]
        self.class_labels = unique

        for i in range(self.num_classes):
            self.exemplars.append(A[(mapping ==i), :])





        return
    

