##author:Vivek SaH
##data.py
##23rd Feb 2015




import csv
import numpy as np
import time as t
import Tkinter as tk
import tkMessageBox
import tkFileDialog
# from xlrd import open_workbook
# import gspread as gs


class Data:
  def __init__(self, data = None):#initialize
    self.raw_data = []
    # self.numeric_data = []
    self.raw_headers = []
    self.raw_types = []
    self.header2raw = {}
    self.enum_dict = {}
    self.K_value = 0
    self.matrix_data = None #hold the converted form of the data
    if data != None:
      self.read(data)

    
    
  ##takes in either a csv file or a list of lists. It first checks which type the data is and 
  ##then acts accordingly. if it is in a csv file, it reads it line by line and stores it in a field cakllked
  ## self.raw_data which is a list of list. if the input data is list of list, then it loops through each list 
  ##and appends it to self.raw_data.    

  ##can read csv, list of lists, google drive
  ## then it converts the data according to the type and stores in matrix
  def read(self, data):
    if type(data) == str and data[-3:] == "csv":
      
      f = file(data, "rU")
      lines = f.readlines()
      f.close()
      csvr = csv.reader(lines)
      for item in csvr:
        if "#" not in item[0]: #ignore the comments
          # print item, "44, data.py"
          self.raw_data.append(item) #after converting it to float, add to raw_data

    ###      
#     elif type(data) == str and data[-3:] == "xls": 
#       wb = open_workbook(data)
# 
#       for s in wb.sheets():
#         
#         for row in range(s.nrows):
#           values = []
#           for col in range(s.ncols):
#             values.append(s.cell(row,col).value)
#           self.raw_data.append(values)  

      
    elif type(data) == list and type(data[0]) == list: #if it is list of list then loop thorugh each element and append it to raw_data
        for item in data:
          self.raw_data.append(item)      
        # print self.raw_data

#     elif data == "drive":
#         username= raw_input("Enter your google username: ")  
#         password = raw_input("Enter your password : ")  
# 
#         ##url of the spreadsheet, the data must be on the first sheet
#         url = raw_input("Enter url of the spreadsheet. This program by default assumes that the data is the first sheet of the worksheet") 
#         gc = gs.login(username,password)
#         list_of_lists = gc.open_by_url(url).sheet1.get_all_values()
#         for l in list_of_lists:
#           self.raw_data.append(l)


    else:
      print "unacceptable data file type"  
      return 
    
    self.raw_headers = self.raw_data[0] #first row assigned to headers
    for i in range(len(self.raw_headers)):
        self.raw_headers[i] = self.raw_headers[i].strip()
    self.raw_types = self.raw_data[1] #second row assigned to types
    self.raw_data = self.raw_data[2:] #rest is assigned to raw_data
    
    # print self.raw_data, "self.raw_data"
  


    for i in range(len(self.raw_headers)):
      self.header2raw[self.raw_headers[i]] = i 
    # self.convert(self.raw_data)
    raw_data2= self.convert(self.raw_data)
#     for i in range(len(raw_data2)):
#         for j in range(len(raw_data2[0])):
        
#           print type(raw_data2[i][j]), "jhqwdgvsjhqwdvjhqwvdjh"
    self.matrix_data =  np.matrix(raw_data2) #converts the data
#     print type(self.matrix_data[0,0]), "jhqwdgvsjhqwdvjhqwvdjh"
      
  
   ##converts all the data points to appropriate type 
  def convert(self, raw_data):
    for i in range(len(raw_data)):
      
      for j in range(len(self.raw_headers)):

        if type(raw_data[i][j]) == str:
#           print raw_data[i][j], i, j
#           print self.raw_types[j]

          raw_data[i][j] = raw_data[i][j].strip()
          # print raw_data[i][j], type(raw_data[i][j]),self.raw_headers[j], self.raw_types[j].strip()
          if raw_data[i][j] != "": ##check if its empty, if it is assign -9999

            if self.raw_types[j].strip() == "numeric": ## if numeric, convert to float
              # print "is numeric"
              # print raw_data[i][j], "is numeric"
              # print type(raw_data[i][j])

              raw_data[i][j] = float(str(raw_data[i][j]).replace(",",""))
              # print type(raw_data[i][j])
              
            elif self.raw_types[j].strip() in ["enum", "string"] : 
              # print "is enum"  
              if j not in self.enum_dict:
                self.enum_dict[j] = {} 

              # enum_dict={}
              ###supports enum type, uses enum_dict(which is a dictionary of dictianries) to store key_value pairs for each enum column
              if raw_data[i][j] not in self.enum_dict[j]:
                self.enum_dict[j][raw_data[i][j]] = len(self.enum_dict[j].keys())
              raw_data[i][j] = self.enum_dict[j][raw_data[i][j]]
            elif self.raw_types[j].strip() == "date":
              ###. I also converted dates to numeric data. I used time module strptime to parse string date and 
              ###mktime to convert it to numeric data. I supported three date formats: 
              ###Ex. 31-01-2012, Jan 21 2012, 01/31/2012. I used nested try and catch exception blocks to execute this.
              # print raw_data[i][j]
              try:
                raw_data[i][j] = t.mktime(t.strptime(raw_data[i][j], "%d-%m-%Y")) # 31-01-2012 == 31st jan 2012
              except:
                try:
                  raw_data[i][j] = t.mktime(t.strptime(raw_data[i][j], "%b %d %Y"))  # Jan 21 2012 ##make sure its not full month name
                except: 
                  try: 
                    raw_data[i][j] = t.mktime(t.strptime(raw_data[i][j], "%m/%d/%Y")) # 01/31/2012 == 31st jan 2012
                  except:
                    print "date format  of ", raw_data[i][j], "not supported" 
                    return 

            else:
                # print  self.raw_types[j] , "is raw_type" 
                # print self.raw_headers[j], "is header"
                pass
                

          else:

            raw_data[i][j] = -9999 
    # print type(raw_data[0][0]), "shakasvjwv"
    return raw_data
      ##returns the converted data
  





  ##returns a list of all of the headers.  
  def get_raw_headers(self):
    # print self.header2raw.items()
    return self.raw_headers

    
  def get_matrix_data(self):
    return self.matrix_data
  # #  
  # def get_enum_dict(self):
  #   return self.enum_dict  

  # returns a list of all of the types.  
  def get_raw_types(self):
    return self.raw_types

  # returns the number of columns in the raw data set
  def get_raw_num_columns(self):
    return len(self.raw_headers)

  # returns the number of rows in the data set
  def get_num_rows(self):
    return len(self.raw_data)

  # returns a row of data (the type is list)
  def get_raw_row(self, index):
    return self.raw_data[index]

  #takes a row index (an int) and column header (a string) and returns the raw data at that location. (The return type will be a string)
  def get_raw_value(self,row_index, column_header):
    return str(self.raw_data[row_index][self.header2raw[column_header]])

  def get_types(self, list_of_headers):
    types = []
    for header in list_of_headers:
      types.append(self.header2raw[header])

    return types  
  # should take a list of columns headers and return a matrix with the data for all rows but just the specified columns  
  def get_data(self,column_headers):
    a = [] #list of header inddices
    for header in column_headers:
      # print a
      a.append(self.header2raw[header])
   
    return self.matrix_data[:,a] #this method returns only specified columns   
   

  def print_nicely(self):##prints the data in anicely formatted manner
    headers = ""
    for header in self.raw_headers:
      headers += (header + (" "*(10-len(header))))
    print headers  
    types = ""
    for tpe in self.raw_types:
      types += (tpe + (" "*(10-len(tpe))))
    print types


    for row in self.raw_data:
      rows = ""
      for point in row:

        rows += (str(point) + (" "*(10-len(str(point)))))
      print rows


  ###this is  a fix which lets machineData which is saved in a file and has categories as the last column to behave as clusterdata, by inclusing this function which returns the last column as list"""
  def getClusterIds(self):
      # print self.get_data([self.raw_headers[-1]]).T.tolist()[0],self.get_data([self.raw_headers[-1]]).T.tolist(), "fake_get_cluster_ids"
      return self.get_data([self.raw_headers[-1]]).T.tolist()[0]

  ## adds columns. It is assumed that the column meets the conditions. I had created a method called convert 
  ##which takes in a list of list data and converts each data point to their types. here, I add each elemnt of extra column to each rows in self.raw_data and call convert method again on this self.raw_data. 
  ##I then make a matrix out of this and self.matrix_data to this.

  # def write(self,headers):
    # tempData = get_data(headers):

  def addcolumn(self,column_as_a_list):
    print len(self.raw_data)+2, len(column_as_a_list), "line 244, data.py"
    
    if len(column_as_a_list) == len(self.raw_data)+2:

      self.raw_headers.append(column_as_a_list[0])
      self.raw_types.append(column_as_a_list[1])
      for i in range(len(column_as_a_list[2:])):
        self.raw_data[i].append(column_as_a_list[2:][i])

      self.matrix_data =  np.matrix(self.convert(self.raw_data))  
      self.header2raw[column_as_a_list[0]] = len(self.raw_headers)-1
      # print self.header2raw, "header2raw"
      # print self.matrix_data ,"self after adding"
    else:
      print 'check the length of column'
  



'''creating child class of data which is PCA analysis'''
class PCAData(Data):
  """extension of Data class to hold the the eigenvalues (numpy matrix), the eigenvectors (numpy matrix), 
  the mean data values (numpy matrix), and the projected data (numpy matrix). It should also have a field to hold the headers 
  of the original data columns used to create the projected data."""
  def __init__(self, headers, pdata, evals, evecs, means ):
    Data.__init__(self)
    self.eigenvalues = evals #numpy matrix to store eigenvalues
    self.eigenvectors = evecs #numpy matrix to store eigenvectors
    self.meanDataValues = means #numpy matrix to store meandatavalues
    # self.projectedData = pdata # #numpy matrix to store projected data
    self.data_headers = headers 
    self.raw_data = []
    # print pdata, "pdata"

    #constructing raw data by converting each item to string
    for i in range(pdata.shape[0]):
      row_list = []
      for j in range(pdata.shape[1]):
        row_list.append(str(pdata[i,j]))
      self.raw_data.append(row_list)  



    # self.numeric_data = []
    # print self.raw_data, len(self.raw_data)
    self.raw_headers = ["P"+str(i) for i in range(len(self.raw_data[0]))] #output ["p1","p2", "p3"]
    # self.raw_headers = headers
    self.raw_types = ["numeric"]* len(self.raw_headers)
    self.header2raw = {}
    for i in range(len(self.raw_headers)):
      self.header2raw[self.raw_headers[i]] = i 
    # self.enum_dict = {}
    self.matrix_data = pdata



  #returns a copy of the eigenvalues as a single-row numpy matrix.  
  def get_eigenvalues(self):
    return self.eigenvalues

  # returns a copy of the eigenvectors as a numpy matrix with the eigenvectors as rows.
  def  get_eigenvectors(self): 
    return self.eigenvectors

  #returns the means for each column in the original data as a single row numpy matrix.  
  def get_data_means(self): 
    return self.meanDataValues


  #returns a copy of the list of the headers from the original data used to generate the projected data.
  def get_data_headers(self):
    return self.raw_headers



  def get_csv_for_pca_data(self,dest_file):

    """write a csv file """
    with dest_file as csvfile:
      #just copied it from a tutorial, dont know what the parameters mean
      pcawriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                                
      # pcawriter.writerow(["Eigenvalues"])
      # pcawriter.writerow(self.eigenvalues.tolist())
      # pcawriter.writerow(["Eigenvectors"])
      # for l in self.eigenvectors.tolist():
      #   pcawriter.writerow(l)
      # pcawriter.writerow(["Averages"])
      # print type(self.meanDataValues), self.meanDataValues.tolist(), self.meanDataValues.shape
      #
      # pcawriter.writerow(self.meanDataValues.tolist()[0])
      # pcawriter.writerow(["Original headers"])
      # pcawriter.writerow(self.data_headers)
      # pcawriter.writerow(["projected Data"])
      pcawriter.writerow(self.raw_headers)

      pcawriter.writerow(["numeric"]* len(self.raw_headers))
      print len(self.data_headers), self.data_headers, len(self.matrix_data), "data.py , write pca function"
      for i in  range(len(self.matrix_data.tolist())):
        # pcawriter.writerow([self.data_headers[i]]+self.matrix_data.tolist()[i])
        pcawriter.writerow(self.matrix_data.tolist()[i])



class ClusterData(Data):
  def __init__(self, clusterdata, headers, K, means, codes, errors ):
    """clusterdata : matrix, headers:list, K: int, means:matrix, codes:N*1 matrix, errors:distances"""
    Data.__init__(self)
    
    # self.matrix_data = clusterdata
    self.matrix_data = np.concatenate((clusterdata,means ),axis=0)
    self.raw_headers = headers 
    self.raw_data = []
    self.K_value = K
    # print pdata, "pdata"

    #constructing raw data by converting each item to string
    for i in range(self.matrix_data.shape[0]):
      row_list = []
      for j in range(self.matrix_data.shape[1]):
        row_list.append(str(self.matrix_data[i,j]))
      self.raw_data.append(row_list)  

    self.raw_types = ["numeric"]* len(self.raw_headers)
    self.header2raw = {}
    for i in range(len(self.raw_headers)):
      self.header2raw[self.raw_headers[i]] = i 
    # self.enum_dict = {}
    # self.matrix_data = pdata  
    self.means = means 
    self.codes = codes.T.tolist()[0] #convert to list
    self.errors = errors
    # self.addcolumn(["clusterID", "numeric"]+ self.codes)
    # print self.raw_headers, len(self.raw_types)

  def getmeans(self):
    return self.means

    
  def getClusterIds(self): #getter for 
    return self.codes


  def getK(self): #getter for Kvalue
    return self.K_value



  """will write selected headers data to a csv file"""
  def write(self, dest_file  ):
    # if dest_file.__getattribute__('name')[-3:] != "csv": #if the input filename does not have csv extension, put csv extension
    #   dest_file += ".csv"
    # mheaders = headers if headers != None else self.raw_headers #headers is optional, if no headers, write all data
    mheaders = self.raw_headers
    codes = self.codes + [i for i in range(self.K_value)]
    mtypes = ['numeric'] * (len(mheaders)+1)
    print mheaders, "mheaders", self.header2raw, "headerDict"
    temp_data = self.get_data(mheaders).tolist() #get the data corresponding to those headers and make a list
    # with open(dest_file, 'wb') as csvfile: # open csv file
    with dest_file as csvfile: 
      spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
      spamwriter.writerow(mheaders+ ["clusterIds"]) #write headers
      spamwriter.writerow(mtypes)
      print len(temp_data), len(codes)
      for i  in range(len(temp_data)):
        spamwriter.writerow(temp_data[i]+ [codes[i]])#write each row of data              


if __name__ == '__main__':
  new_data = Data("AustraliaCoast.csv") 

  for i in range(len(new_data.raw_data)):
    for j in range(len(new_data.raw_headers)):
        print new_data.raw_data[i][j], type(new_data.raw_data[i][j])
  print new_data.matrix_data
  # new_data.addcolumn(["thing99","enum","1","2","1","1"])
  # print new_data.get_enum_dict()
  # print new_data.get_data(["thing1","thing2", "thing3","thing99"]) 
  # print new_data.get_raw_headers(), "headers_main"
  # new_data.print_nicely()

# new_data.print_nicely()    


