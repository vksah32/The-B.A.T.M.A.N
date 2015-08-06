# display.py
# Written by Vivek Sah
# 
# CS 251
# Spring 2015




"""class which creates an empty dialog box"""
import Tkinter as tk
import os
import view
import numpy as np
import tkMessageBox
from time import gmtime, strftime
import tkFileDialog
class Dialog(tk.Toplevel):

    def __init__(self, parent, title = None,external_parameter = None, clustermeans = False):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.clustermeans = clustermeans
        self.external_parameter = external_parameter

        if title:
            self.title(title)
        
                                
        self.lines = []                         
                                
        self.parent = parent

        self.result = None

        body = tk.Frame(self)
        
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks
    
            
        
        
        
        

    def body(self, master):
      # self.list = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
      # self.list.insert(tk.END, "jhvhjs")
      # self.list.pack(fill=tk.BOTH, expand=1)
      pass

        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden


    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1 # override

    def apply(self):

        pass # override


"""creates distribution selection dialog with two listbox"""
class DistributionDisplay(Dialog):
  def body(self,master):
    modes = ["uniform","gaussian"]
    tk.Label(master, text="First:").grid(row=0,column=0)
    tk.Label(master, text="Second:").grid(row=0,column =1)
    self.list = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)



    self.list2 = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
    
    for mode in modes:
      self.list.insert(tk.END, mode)
      self.list2.insert(tk.END, mode)


    self.list.grid(row=1, column=0)
    self.list2.grid(row=1, column=1)
    return self.list   

  def apply(self):
    self.result = (self.list.get(tk.ACTIVE), self.list2.get(tk.ACTIVE))
    print self.result  


"""creates shape selection dialog"""
class ShapeListBox(Dialog):
  def body(self,master):
    shapes = ["rectangle","oval","arc"]
    tk.Label(master, text="Shapes").grid(row=0,column=0)
    
    self.list = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
    
    for shape in shapes:
      self.list.insert(tk.END, shape)
      


    self.list.grid(row=1, column=0)
    
    return self.list   

  def apply(self):
    self.result = self.list.get(tk.ACTIVE)
    print self.result 

class AxisDisplay(Dialog): #creates a dialog for axis selection
  def body(self,master):
    list_of_headers = ["None"]+self.external_parameter
    
    tk.Label(master, text="X-Axis\n Independent Axis X1:").grid(row=0,column=0)
    tk.Label(master, text="Y-Axis\n Dependent Axis y:").grid(row=0,column =1)
    tk.Label(master, text="Z-Axis\n Independent Axis X2:").grid(row=0,column=2)
    if not self.clustermeans: #if there is no clustermeans, do not show color axis
        tk.Label(master, text="Color\n Independent Axis X3:").grid(row=0,column=3)
        tk.Label(master, text="Size:\n Independent Axis X4:").grid(row=0,column=4)

        tk.Label(master, text="Shape:\n Independent Axis X4:").grid(row=0,column=5)
    else:
        tk.Label(master, text="Size:\n Independent Axis X4:").grid(row=0,column=3)

        tk.Label(master, text="Shape:\n Independent Axis X4:").grid(row=0,column=4)
            
    
    
    height1 = len(list_of_headers)
    self.list = tk.Listbox(master, width=15, height=height1, selectmode=tk.SINGLE, exportselection=0)



    self.list2 = tk.Listbox(master, width=15, height=height1,selectmode=tk.SINGLE, exportselection=0)
    self.list3 = tk.Listbox(master, width=15, height=height1,selectmode=tk.SINGLE, exportselection=0)
    self.list4 = tk.Listbox(master, width=15, height=height1,selectmode=tk.SINGLE, exportselection=0)
    self.list5 = tk.Listbox(master, width=15, height=height1,selectmode=tk.SINGLE, exportselection=0)
    if not self.clustermeans:
        self.list6 = tk.Listbox(master, width=15, height=height1,selectmode=tk.SINGLE, exportselection=0)


    




    for h in list_of_headers:
      if h != "None":  
        self.list.insert(tk.END, h)
        self.list2.insert(tk.END, h)
      self.list3.insert(tk.END, h)
      self.list4.insert(tk.END, h)
      self.list5.insert(tk.END, h)
      if not self.clustermeans:
        self.list6.insert(tk.END, h)


    self.list.grid(row=1, column=0)
    self.list2.grid(row=1, column=1)
    self.list3.grid(row=1, column=2)
    self.list4.grid(row=1, column=3)
    self.list5.grid(row=1, column=4)
    if not self.clustermeans:
        self.list6.grid(row=1, column=5)
   

    return self.list   

  #returns a list of selections with a dictionary at the last which stores if duplicate sleections ahve been m,ade  
  def apply(self):
    lists = [self.list, self.list2, self.list3,self.list4,self.list5]
    if not self.clustermeans:
        lists += [self.list6]
    self.result = []
    self.result_dic= {} # store the selections in a dict to check for dup;lication
    self.result_dic["error"] = 0
    for l in lists:
        print l, "231"
        self.result.append(l.get(tk.ACTIVE))
        if l.get(tk.ACTIVE) in self.result_dic:
            if l.get(tk.ACTIVE) != 'None':
                self.result_dic["error"] += 1
            self.result_dic[l.get(tk.ACTIVE)] += 1   

        else:
            self.result_dic[l.get(tk.ACTIVE)] = 1
    if self.clustermeans:        
        self.result= self.result[:3]+ ["None"]+ self.result[3:] #color axis selection   None     
    self.result.append(self.result_dic)   

    return self.result

class PCABox(Dialog):
  def body(self,master):
    list_of_headers = self.external_parameter
    
    height1 = len(list_of_headers)
    self.list = tk.Listbox(master, width=15, height=height1, selectmode=tk.MULTIPLE, exportselection=0)
    for h in list_of_headers:
      
        self.list.insert(tk.END, h)
    self.list.grid(row=1, column=0) 
    # self.list.selection_set(0,3)
    self.var = tk.IntVar()

    self.checkout = tk.Checkbutton(master, text="normalize data", variable=self.var)
    self.checkout.grid(row=2, column = 0)
    self.label = tk.Label(master, text = "Name this analysis")
    self.label.grid(row=3, column= 0)
    self.entry = tk.Entry(master)
    
    self.entry.grid(row = 4, column=0)

    self.entry.delete(0, tk.END)
    self.entry.insert(0, strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    # return self.list 


  def apply(self):
     #handling multiple selections
    self.result = [] # sample output = [independentheader1, independt header2, dependentheader]
    items = map(int, self.list.curselection()) 
    print items
    for i in range(len(items)):
        self.result.append(self.list.get(items[i]))

    # print self.result, "display.py,282"
    self.result = self.result + [self.var.get(), self.entry.get()]
    return self.result


#will display pca_eigenvalues and eigenvectors
class pca_infobox(Dialog):

    def body(self,master) :
        # assert projected_data i
        projected_data = self.external_parameter #extract the pca data
        # print projected_data.data_headers ,"270"
        list_of_tags = ["evec","e-val","cumulative"]+ projected_data.data_headers #preparing for table formulation
        eigenvalues = [round(projected_data.get_eigenvalues()[i],4) for i in range(len(projected_data.get_eigenvalues()))] #rounding each eigenvalue to four decimal places
        eigen_headers = projected_data.raw_headers #eigen_values, get no. of eigenvalues
        
        #calculating cumulative, first add the first energy as the first elemnt and then loop through and the previuos cumulative
        cumulative= [round(eigenvalues[0]/np.sum(eigenvalues),5)]
        for i in range(len(eigenvalues)-1):
            cumulative.append(round((eigenvalues[i+1]/np.sum(eigenvalues)+cumulative[-1]),5))

        #creating a dict_dict to facilitate loop later    
        dict_dict = {0: eigen_headers, 1: eigenvalues, 2: cumulative }#eigenvalues is list of list
        # print eigen_headers, eigenvalues, cumulative


        #one double loop to write the whole eigen-table
        for i in range(len(list_of_tags)):
            m1 = tk.Label(master,text = list_of_tags[i])

            m1.grid(row=0, column = i)
            for j in range(len(eigenvalues)):
                print i , j 
                text = dict_dict[i][j] if i < 3 else str(round(projected_data.eigenvectors[j,i-3],5))
                print text 
                m = tk.Label(master,text = text)
                m.grid(row = j+1, column = i )
              



    def apply(self):
        pass


 
#-------------------K-------------MEANS----------CLUSTER------------------ 

class KBox(Dialog):
  def body(self,master):
    list_of_headers = self.external_parameter
    
    height1 = len(list_of_headers)
    self.list = tk.Listbox(master, width=15, height=height1, selectmode=tk.MULTIPLE, exportselection=0)
    for h in list_of_headers:
      
        self.list.insert(tk.END, h)
    self.list.grid(row=1, column=0) 

    self.label = tk.Label(master, text = "Select metric")
    self.label.grid(row=2, column= 0)
    metric_values = ["euclidean", "correlation","cosine","hamming","canberra","manhattan"]
    height2 = len(metric_values)

    self.list2 = tk.Listbox(master, width=15, height=height2, selectmode=tk.SINGLE, exportselection=0)
    for metric in metric_values:
      
        self.list2.insert(tk.END, metric)
    self.list2.grid(row=3, column=0) 
    self.list2.selection_set(first = 0 )    
    # self.list.selection_set(0,3)
    
    self.label = tk.Label(master, text = "Enter K value")
    self.label.grid(row=4, column= 0)
    self.entry = tk.Entry(master)
    
    self.entry.grid(row = 5, column=0)

    self.entry.delete(0, tk.END)
    self.entry.insert(0, 1)

    # return self.list 


  def apply(self):
     #handling multiple selections
    self.result = [] # sample output = [independentheader1, independt header2, dependentheader]
    items = map(int, self.list.curselection()) 
    print items
    for i in range(len(items)):
        self.result.append(self.list.get(items[i]))
    self.result.append(self.list2.get(tk.ACTIVE))    

    # print self.result, "display.py,282"
    if len(self.result) == 1:
        tkMessageBox.showinfo(title=None, message="NO column selected") #check if the user has uploaded a csv file



    if len(self.entry.get()) > 0 and isinstance(int(self.entry.get()), int):

        self.result = self.result + [self.entry.get()]
        return self.result
    else:
        tkMessageBox.showinfo(title=None, message="Input a valid integer") #check if the user has uploaded a csv file

            
#-------------------MACHINE----LEARNING--------------
class machineDialog(Dialog):

  def body(self,master):
    self.result = []

    options = ["NaiveBayes","KNN"]
    tk.Label(master, text="Choose one option").grid(row=0,column=0)

    self.list = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)

    for option in options:
      self.list.insert(tk.END, option)


    self.list.grid(row=1, column=0)
    self.list.selection_set(0)
    self.ask_train_file = tk.Button(master,text = "Choose training data", command = self.askforfile)
    self.ask_test_file = tk.Button(master,text = "Choose test data", command = self.askforfile)
    self.ask_train_cat_file = tk.Button(master,text = "Choose optional training categories", command = self.askforfile)
    self.ask_test_cat_file = tk.Button(master,text = "Choose optional test categories", command = self.askforfile)
    self.ask_train_file.grid(row=2, column=0)
    self.ask_test_file.grid(row=3, column=0)
    self.ask_train_cat_file.grid(row=4, column=0)
    self.ask_test_cat_file.grid(row=5, column=0)

    # self.label = tk.Label(master, text = "Enter K value for KNN classifier")
    # self.label.grid(row=4, column= 0)
    # self.entry = tk.Entry(master)
    #
    # self.entry.grid(row = 5, column=0)
    #
    # self.entry.delete(0, tk.END)
    # self.entry.insert(0, 1)




    return self.list

  def askforfile(self):

    print "running askforfile"
    file = tkFileDialog.askopenfilename( parent=None,title='Choose a data file', initialdir='.' )
    if len(file)> 0:

        self.result.append(file[file.rfind("/")+1:] )




  def apply(self):

    self.result += [self.list.get(tk.ACTIVE)]
    print self.result






         


    
# if __name__ == "__main__":
#   root = tk.Tk()
# #   d = DistributionDisplay(root)
#   # display =   
#   root.wait_window(d.top)        




