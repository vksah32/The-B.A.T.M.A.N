
##author: Vivek sah
##analysis.py
## date 04/07/2105



import data
import numpy as np
import scipy.cluster.vq as vq
import random
import scipy
import sys


#data-range() takes in a data object and a header list and returns 2D array which has max,min for each co0lumn
def data_range(header_list , data_object):
	#sample_output = [[header1max,header1min],[header2max,header2min],.....]
    req_matrix = data_object.get_data(header_list) #get the required matrix
    # print req_matrix, "rekjwdgbkjbjk, 15, analysis"
    # for i in range(req_matrix.shape[0]):
    #     for j in range(req_matrix.shape[1]):
    #         print type(req_matrix[i,j]), "analysis, 18"

    # print type(req_matrix[0,0])
    return np.concatenate((req_matrix.max(axis=0), req_matrix.min(axis=0)), axis = 0).transpose().tolist() #get list of max, list of min, concatenate them and convert them to a list
 
#mean() takes in a header list and returns of list of mean of each column
def mean(header_list, data_object):
    req_matrix = data_object.get_data(header_list)
    mean_matrix = req_matrix.mean(axis=0)#calculates the mean of each column
    return mean_matrix.tolist()

#stdev() takes in a header list and a data object and returns a list of stdev of each header column
def stdev(header_list, data_object):
    req_matrix = data_object.get_data(header_list)
    stdev_matrix = req_matrix.std(axis=0) #calculates the stdev of each column
    return stdev_matrix.tolist() 





#normalize_columns_separately() takes in a headr list and a data object and returns a matrix of normalised column. 
#I use the formula mormalised data point = x-col_min/(col_max-col_min). I use my earlier function to get a list of 
#max and min of each columns
def normalize_columns_separately(header_list, data_object):
    max_min = data_range(header_list, data_object)

    # print max_min, "max-min"
    req_matrix = data_object.get_data(header_list)
    
    for i in range(req_matrix.shape[0]): # loop through matrix to change each point and then return it
      for j in range(req_matrix.shape[1]):
        # print req_matrix[i,j]-max_min[j][1], max_min[j][0]- max_min[j][1]
        req_matrix[i,j] = (req_matrix[i,j]-max_min[j][1])/(max_min[j][0]- max_min[j][1])

    return req_matrix

#normalize_columns_together() works similar to last method. except I use max,min of the whole matrix
def normalize_columns_together(header_list, data_object):
    
    
    req_matrix = data_object.get_data(header_list)
    max_min = (req_matrix.max(), req_matrix.min())

    # mag =  np.linalg.norm(req_matrix, axis=0, order = 1)
    # print mag, "mag"
    for i in range(req_matrix.shape[0]):
      for j in range(req_matrix.shape[1]):
        # print req_matrix[i,j]-max_min[j][1], max_min[1]- max_min[j][1]
        req_matrix[i,j] = (req_matrix[i,j]-max_min[1])/(max_min[0]- max_min[1])

    return req_matrix    


def pca(header_list,data_object, normalize=True):

    "Pca_analysis"
    assert isinstance( data_object, data.Data) 
     #projected_data, eigenvalues, eigenvectors, data_means, pre_normalize=True):
    A = normalize_columns_separately(header_list, data_object) if normalize == True else data_object.get_data(header_list) 
    m = np.mean(A, axis = 0) 
    # print m, m.shape, m.tolist()[0], "Analysis"
    D = A-m
    # print A, m, D, "in analysis.py"
    U,S,V = np.linalg.svd(D, full_matrices = False)
    # print S, "S"

   

    # eigenvalues = np.matrix([((S[i]*S[i])/(len(data_object.raw_data)-1)) for i in range(len(S))])
    evals = (S**2)/(len(data_object.raw_data)-1)
    eigenvalues = np.real(evals)
    # print eigenvalues, "eigenvalues in analysis.py"
    # print D, D.T, V,  D.shape, V.shape
    projected_data =  (V*D.T).T

    eigenvectors = V
    eigenvectors = np.real(eigenvectors)

    #return PCAdata object constructed using  these parameters 
    return data.PCAData(headers= header_list, pdata= projected_data, evecs = eigenvectors, evals= eigenvalues, means = m)

def kmeans_numpy(d,headers, K, whiten = True):
    '''Takes in a Data object, a set of headers, and the number of clusters to create
    Computes and returns the codebook, codes, and representation error.
    '''

    # assign to A the result of getting the data from your Data object
    A = d.get_data(headers)

    # assign to W the result of calling vq.whiten on A
    W = vq.whiten(A)

    # assign to codebook, bookerror the result of calling vq.kmeans with W and K
    codebook, bookerror = vq.kmeans(W,K)

    # assign to codes, error the result of calling vq.vq with W and the codebook
    codes,error = vq.vq(W,codebook)

    # return codebook, codes, and error
    return [codebook,codes,error]

"""data=data object, k = no. of clusters, categories
    returns numpy matrix with K rows, each one representing a cluster mean
    categories is N*1 matrix assume categories = [0,0,0, 1,1,1]"""

def kmeans_init(data, Kval, categories=None):
    # print Kval, data.shape[0], 
    assert data.shape[0] >0 #check if its a valid matrix
    assert isinstance(Kval, int) #check if K is int
    
    # if  Kval > data.shape[0]: #check if 


    if categories == None:
        randomKvalues = random.sample(range(1, data.shape[0]), Kval)
        # print randomKvalues, "randomValues-analysis.py 139"
        # print data[randomKvalues,:], "means-K_init"
        return data[randomKvalues,:] #will return a matrix with rows given by random k values
    elif categories != None and categories.shape[0] == data.shape[0] :
        maxval = categories.max() #get the max val in the categories// could be K-value-1
        Kdata = []
        for i in range(int(maxval)+1):        
            ii = np.where(categories== i)[0] #list of row indices  which has i as element         
            partdata = data[ii.tolist()[0],:]  #get the corresponding rows from data    
            krow = np.mean(partdata,axis=0) #get the mean of those rows          
            Kdata.append(krow.tolist()[0]) #append it to kmeans_list whcih will be converted to matrix
            # print Kdata
        return np.matrix(Kdata)    

def kmeans_classify(data, clusterMeansmatrix, metric = "euclidean"):
    # print data.shape, clusterMeansmatrix.shape
    assert clusterMeansmatrix.shape[0]>0 and data.shape[0]>0#valud matrix

    main_list = []
    for i in range(data.shape[0]):
        d = [0, sys.maxint] #check it against all means, and store the row index of mean with distance with mean
        for j in range(clusterMeansmatrix.shape[0]):
            #gives the user option to calculate using other metrics using scipy inbuilt methods
            if metric == "euclidean":
                newd = scipy.spatial.distance.euclidean(data[i,:], clusterMeansmatrix[j,:]) 
            elif  metric == "cosine":
                newd = scipy.spatial.distance.cosine(data[i,:], clusterMeansmatrix[j,:]) 
            elif metric == "canberra":
                newd = scipy.spatial.distance.canberra(data[i,:], clusterMeansmatrix[j,:]) 
            elif metric == "manhattan":
                newd = scipy.spatial.distance.cityblock(data[i,:], clusterMeansmatrix[j,:]) 
            elif metric == "correlation":  
                newd = scipy.spatial.distance.correlation(data[i,:], clusterMeansmatrix[j,:])
            elif metric == "hamming":
                newd = scipy.spatial.distance.hamming(data[i,:], clusterMeansmatrix[j,:])
                        
            
            d = [j, newd] if newd < d[1] else d
        main_list.append(d)

    return (np.matrix(main_list)[:,0], np.matrix(main_list)[:,1])  #return codes and errors  
            
def kmeans_algorithm(A, means, metric = "euclidean"):
    # set up some useful constants
    MIN_CHANGE = 1e-7
    MAX_ITERATIONS = 100
    D = means.shape[1]
    K = means.shape[0]
    N = A.shape[0]

    # iterate no more than MAX_ITERATIONS
    for i in range(MAX_ITERATIONS):
        # calculate the codes
        codes, errors = kmeans_classify( A, means )

        # calculate the new means
        newmeans = np.zeros_like( means )
        counts = np.zeros( (K, 1) )
        for j in range(N):
            newmeans[codes[j,0],:] += A[j,:]
            counts[codes[j,0],0] += 1.0

        # finish calculating the means, taking into account possible zero counts
        for j in range(K):
            if counts[j,0] > 0.0:
                newmeans[j,:] /= counts[j, 0]
            else:
                newmeans[j,:] = A[random.randint(0,A.shape[0]),:]

        # test if the change is small enough
        diff = np.sum(np.square(means - newmeans))
        means = newmeans
        if diff < MIN_CHANGE:
            break

    # call classify with the final means
    codes, errors = kmeans_classify( A, means, metric )

    # return the means, codes, and errors
    return (means, codes, errors)


def kmeans(d, headers, K, whiten=True, categories = None, metric = "euclidean"):
    '''Takes in a Data object, a set of headers, and the number of clusters to create
    Computes and returns the codebook, codes and representation errors. 
    If given an Nx1 matrix of categories, it uses the category labels 
    to calculate the initial cluster means.
    '''
    
   
    if  isinstance(d, data.Data) and isinstance(headers, list) and K > 0 :
         # assign to A the result getting the data given the headers
        A = d.get_data(headers)

        if whiten:

          # assign to W the result of calling vq.whiten on the data
          W = vq.whiten(A)
        else:
          # assign to W the matrix A
          W = A

        # assign to codebook the result of calling kmeans_init with W, K, and categories
        # print W.shape, W.shape[0], "line 227"
        # print W, "W"
        codebook = kmeans_init(W,K, categories)
        # print codebook,  "codebook- analysis.py-245"


        # assign to codebook, codes, errors, the result of calling kmeans_algorithm with W and codebook  
        (codebook,codes,errors) = kmeans_algorithm(W,codebook, metric)  
        # print codebook, "codebook- analysis.py-247"

        
        # return the codebook, codes, and representation error
        # return (codebook,codes,errors)
        return data.ClusterData(W, headers,K,  codebook, codes, errors )

    else:

        print "analysis.py: kmeans() parameter problems"
            



           




