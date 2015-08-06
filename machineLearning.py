#Vivek Sah
#  Spring 2015
# CS 251 Project 8

#

import sys
import data
import classifiers
import tkMessageBox
import csv
import numpy as np

def main(parameters_list):
    '''Reads in a training set and a test set and builds classifier based on input, classifies the test data and prints it to a csv file
    '''

    # usage
    if len(parameters_list)< 3:
        print "Usage Error: <Training data> <test data> <optional training categories> <optional test categories> <KNN or NaiveBayes> "
        return 

    # read the training and test sets
    print "Input parameters are :" + "trainig data:" + parameters_list[0] + "\ntest data:"+ parameters_list[1] + "\nalgorithm"+ parameters_list[-1]
    dtrain = data.Data(parameters_list[0]) #trainig data

    dtest = data.Data(parameters_list[1]) #test data

    actual_headers = [] #will hold the classes name which is be used to make confusion matrix


    # get the categories and the training data A and the test data B
    if len(parameters_list) > 4:

        traincatdata = data.Data(parameters_list[2])
        testcatdata = data.Data(parameters_list[3])

        traincats = traincatdata.get_data( [traincatdata.get_raw_headers()[0]] )
        testcats = testcatdata.get_data( [testcatdata.get_raw_headers()[0]] )

        #get the actual class names
        a = [traincatdata.enum_dict[0].keys(),testcatdata.enum_dict[0].keys()] if traincatdata.raw_types[-1] == "enum" else [np.unique(np.array(traincats.T), return_inverse=True)[0], np.unique(np.array(testcats.T), return_inverse=True)[0]] 
        actual_headers+= a
        
        A = dtrain.get_data( dtrain.get_raw_headers() )
        B = dtest.get_data( dtest.get_raw_headers() )
    else:
        # assume the categories are the last columnlen

        traincats = dtrain.get_data( [dtrain.get_raw_headers()[-1]] )
        testcats = dtest.get_data( [dtest.get_raw_headers()[-1]] )
        A = dtrain.get_data( dtrain.get_raw_headers()[:-1] )
        B = dtest.get_data( dtest.get_raw_headers()[:-1] )
      

        #get the actual class names
        a = [dtrain.enum_dict[len(dtrain.raw_headers)-1].keys(),dtest.enum_dict[len(dtest.raw_headers)-1].keys()] if dtest.raw_types[-1] == "enum" else [np.unique(np.array(traincats.T), return_inverse=True)[0], np.unique(np.array(testcats.T), return_inverse=True)[0]]
        actual_headers+= a

    # create two classifiers, one using 10 exemplars per class

     # create a new classifier
    # if algorithm == "NaiveBayes":
    #     classifier = classifiers.NaiveBayes()
    # elif algorithm == "KNN":
    #     classifier = classifiers.KNN()
    # else:
    #     print "Something wrong in getting algorith: %s" %algorithm

    classifier = classifiers.NaiveBayes() if parameters_list[-1] == "NaiveBayes" else classifiers.KNN() 
    # if parameters_list[-1] == "KNN"     



    # build the classifier using the training data
    classifier.build( A, traincats)

    # classifier.read("KNN_classifier.csv")

    # use the classifier on the training data
    ctraincats, ctrainlabels = classifier.classify( A )
   
    print "Confusion matrix for training data"
    
    print classifier.confusion_matrix_str(classifier.confusion_matrix(traincats, ctraincats),actual_headers[0])



    ctestcats, ctestlabels = classifier.classify( B )
    print "Confusion matrix for test data"
    # print classifier.confusion_matrix(testcats, ctestcats)
    print classifier.confusion_matrix_str(classifier.confusion_matrix(testcats, ctestcats),actual_headers[1])
    

    # print 'Results on Training Set:'
    # print '     True  Est'
    # for i in range(ctraincats.shape[0]):
    #     if int(traincats[i,0]) == int(ctraincats[i,0]):
    #         print "%03d: %4d %4d" % (i, int(traincats[i,0]), int(ctraincats[i,0]) )
    #     else:
    #         print "%03d: %4d %4d **" % (i, int(traincats[i,0]), int(ctraincats[i,0]) )
    #
    # print 'Results on Test Set:'
    # # print '     True  Est'
    # # for i in range(ctestcats.shape[0]):
    # #     if int(testcats[i,0]) == int(ctestcats[i,0]):
    # #         print "%03d: %4d %4d" % (i, int(testcats[i,0]), int(ctestcats[i,0]) )
    # #     else:
    # #         print "%03d: %4d %4d **" % (i, int(testcats[i,0]), int(ctestcats[i,0]) )


    if dtest.matrix_data.shape[1] == B.shape[1]:

        write(ctestcats, dtest, len(dtest.get_raw_headers()))
    else:
        write(ctestcats, dtest, len(dtest.get_raw_headers())-1)

    return






def write(categories, dtest, len):


    temp_data = dtest.get_data(dtest.raw_headers[:len]).tolist()


    categories_as_list = categories.T.tolist()[0]
    with open('test_data_classified.csv', 'w') as csvfile:
      spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
      spamwriter.writerow(dtest.get_raw_headers()[:len]+ ["categories"]) #write headers
      spamwriter.writerow(['numeric'] * (len+1))

      for i  in range(dtest.matrix_data.shape[0]):

        spamwriter.writerow(temp_data[i]+ [categories_as_list[i]])#write each row of data
    print "hahahahah"




if __name__ == "__main__":
    main(sys.argv[1:])
