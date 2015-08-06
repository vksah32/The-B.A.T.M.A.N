#Author:Vivek Sah

# using Skeleton Tk interface example
# Written by Bruce Maxwell
# Modified by Stephanie Taylor
# last edited 04/07/15
# CS 251
# Spring 2015




import copy
import Tkinter as tk
import tkFont as tkf
import tkFileDialog
import math
import random
import display
import numpy as np
import view
import data
import analysis
import tkMessageBox
import scipy.stats
import tkSimpleDialog
from time import gmtime, strftime
import os
import machineLearning

# create a class to build and manage the display

class DisplayApp:

    def __init__(self, width, height):

        # create a tk object, which is the root window
        self.root = tk.Tk()

        # width and height of the window
        self.initDx = width
        self.initDy = height
        self.shape = 'oval' #default shape of data objects
        
        self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )
        self.data_file = None #data file csv to be stored

        # set the title of the window
        self.root.title("The B.A.T.M.A.N")
        
        # set the maximum size of the window for resizing
        self.root.maxsize( 1600, 900 )

        # setup the menus
        self.buildMenus()
        self.lines = []

        view_size = min(self.initDx, self.initDy) * 0.65
        self.view = view.View(view_size= view_size)

        #end points 
        self.axes = np.matrix([[1.0,0,0,0,0,0],
                                [0,0,1,0,0,0],
                                [0,0,0,0,1,0],
                                [1,1,1,1,1,1]])
        # build the controls
        self.buildControls()



        self.axis_labels=[]#axis labels to be appended

        # build the Canvas
        self.buildCanvas()

        # bring the window to the front
        self.root.lift()

        self.shapesRadius = 3  
        # - do idle eveents here to get actual canvas size
        self.root.update_idletasks()

        # now we can ask the size of the canvas
        # print self.canvas.winfo_geometry()

        # set up the key bindings
        self.setBindings()


        # set up the application state
        self.objects = {} # dict of data objects that will be drawn in the canvas, mapped to their original values
        self.raw_data = None # will hold the raw data someday.
        self.data = None # will hold normalized data matrix
        self.baseClick = None # used to keep track of mouse movement
        self.baseClick2 = None #for mousebutton2, will hold baseclick, before rotation
        self.rotview = None #will hold the original view before rotating
        self.baseextent = None # will hold extent 
        self.baseview = self.view.clone() # will be used to reset
        self.endpoints = None #will hold the endpoints of the linreg line
        self.linregLines = []
        self.selected_axes = []
        self.linRegressresults = []
        self.recallCount = 0 #will store how many times the user clicked toggleback
        self.recallforwardcount = 0 #will store how many times the user clicked toggleforward
        self.previousResults = [] #will store data from previous plots, 
        self.pcadata_collection = {} #will store pcadata each time the user calls pcaanalysis
        self.current_projected_pca= None # will store which pca is projected so that if the user deletes while it is projected, it should get cleared
        self.clusterdata = None #will store cluster data object
        self.mean_labels = []

        #for TESTING PURPOSE###

        # self.handleOpen()
        # self.rinitialEndpoint = None #initialendpoint for regression
        # tuple_of_headers = None #will contain the user selected headers

    """it will create lines, labels for axes for each endpoint pairs , add it  fields and draw on canvas"""   
    def buildAxes(self):
        vtm = self.view.build()
        pts = (vtm * self.axes)
        # self.endpoints = pts
#       for i in range(3):
        line1=self.canvas.create_line(pts[0,0],pts[1,0],pts[0,1],pts[1,1], fill = "blue")
        line2=self.canvas.create_line(pts[0,2],pts[1,2],pts[0,3],pts[1,3], fill = "red")
        line3=self.canvas.create_line(pts[0,4],pts[1,4],pts[0,5],pts[1,5], fill = "green")
        label_x = self.canvas.create_text((pts[0,0]+pts[0,1])/2,(pts[1,0]+pts[1,1])/2,text = "X-axis")
        label_y = self.canvas.create_text((pts[0,2]+pts[0,3])/2,(pts[1,2]+pts[1,3])/2,text = "Y-axis")
        label_z = self.canvas.create_text((pts[0,4]+pts[0,5])/2,(pts[1,4]+pts[1,5])/2,text = "Z-axis")

        #appends to labels list
        self.axis_labels.append(label_x)
        self.axis_labels.append(label_y)
        self.axis_labels.append(label_z)

        self.lines.append(line1)
        self.lines.append(line2)
        self.lines.append(line3)


    """it takes in a list of user selected headers(6-tuple) from handlePlotData() function, gets the normalized matrix corresponding to those headers
      and depending on the number of headers specified, it makes either oval or arc(arc if shape axis is selected, if none it assigns 0 column vectors ) """    
    def buildpoints(self, tuple_of_headers, clusterData = None):
        ##first gets three columns
        # if pca != None:
        #     current_raw_data = pca
        # else:
        #     current_raw_data = self.raw_data    
        print tuple_of_headers, "tuple_of_headers, line 148, tkbase.py"
        if tuple_of_headers[2] == 'None': #if only two columns, put 0 as the third column
            self.data = analysis.normalize_columns_separately(tuple_of_headers[:2], self.raw_data) #normalised matrix
            zero_coor = [0]*self.data.shape[0]
            self.data = np.concatenate((self.data, np.matrix([zero_coor]).T),axis=1)
        else:
            self.data = analysis.normalize_columns_separately(tuple_of_headers[:3], self.raw_data)

        homo_coor= [1.0] * self.data.shape[0] #homogeneous coordinate
        self.data = np.concatenate((self.data, np.matrix([homo_coor]).T),axis=1)
        # print self.data ,"hjvdhjwqvdhjqwvdhjqwvdhjqvwhdjvqwhjdvhjwdvb"


                
       #color axis
        color_values = analysis.normalize_columns_separately([tuple_of_headers[-3]], self.raw_data) if (tuple_of_headers[-3] != "None") else np.matrix([[0]*self.data.shape[0]]).T
        
        ##need to declare size values as field so that the same size can be used while transformation
        self.size_values = analysis.normalize_columns_separately([tuple_of_headers[-2]], self.raw_data) if (tuple_of_headers[-2] != "None") else np.matrix([[0]*self.data.shape[0]]).T
        shape_values = analysis.normalize_columns_separately([tuple_of_headers[-1]], self.raw_data) if (tuple_of_headers[-1] != "None") else np.matrix([[0]*self.data.shape[0]]).T
        



        # print self.data, self.data.shape, "125"
        vtm =  self.view.build()
        
        pts = (vtm * self.data.T).T  
        # k_val = 0 if not cluster else self.clusterdata.K_value
        
        
        for i in range(self.data.shape[0]): #loop through each point
            print i, "i"

            x = float(pts[i,:][0,0])
            y = float(pts[i,:][0,1])
            # print size_values, color_values, size_values.shape, color_values.shape, "150"
            

            #generate color from color values
            if clusterData == None:
                tk_rgb = "#%02x%02x%02x" % (20+200*color_values[i,0], 20+200*color_values[i,0], 240-200*color_values[i,0] )
                dx = self.shapesRadius+self.size_values[i,0]*10
            else:
                # ids = clusterData.getClusterIds()+ [i for i in range(clusterData.K_value)] # to the list of ids add a list of more ids to correspond with the wxtra rows of means
                # dx = self.shapesRadius+self.size_values[i,0]*10
                # print ids
                if i >= self.data.shape[0]- clusterData.K_value:
                    # dx = self.shapesRadius*3
                    # tk_rgb = ["red","green", "blue","black", "pink","yellow", "purple", "violet","orange", "blue violet"][i-self.data.shape[0]+ self.clusterdata.K_value]
                    label_m = self.canvas.create_text(x,y,text = "Mean"+ str(i-self.data.shape[0]+ self.clusterdata.K_value))
                    self.mean_labels.append(label_m)
                # else:
                dx = self.shapesRadius+self.size_values[i,0]*10    


                ids = clusterData.getClusterIds() + [j for j in range(clusterData.K_value)] # to the list of ids add a list of more ids to correspond with the wxtra rows of means #LIST OF cluster ids

                unique,mapping = np.unique(np.array(ids), return_inverse=True) #seems redundant but trying to make the clusterdata code to work for machinelearning

                if len(unique) > 10:
            # print ((255*ids[i]/self.clusterdata.K_value), 255, 255 )
                    tk_rgb = "#%02x%02x%02x" % ((255*ids[i]/self.clusterdata.K_value), 255-(255*ids[i]/self.clusterdata.K_value), (255*ids[i]/self.clusterdata.K_value) )
                else:    
                    tk_rgb = ["red","green", "blue","black", "pink","yellow", "purple", "violet","orange", "blue violet"][int(ids[i])]  
                    print int(ids[i]), i  
                    
            if tuple_of_headers[-1] != 'None': #shape header
                pt = self.canvas.create_arc( x-dx, y-dx, x+dx, y+dx,fill=tk_rgb, outline='',extent = 60+120* shape_values[i,0])
            else:    
                pt = self.canvas.create_oval( x-dx, y-dx, x+dx, y+dx,fill=tk_rgb, outline='' )  
            
            object_raw_values = [] #generates a list of column values for a data ppint so that it can mapped to corresponding data object in self.objects
            for header in tuple_of_headers:
                if header != "None":
                    object_raw_values.append(self.raw_data.get_raw_value(i, header))
                else:
                    object_raw_values.append(" ")
                        
            self.objects[pt] = object_raw_values #map eacg data point to its raw values
                    


    """This function builsd the VTM , multiplies the axis endpoints by the VTM; for each line object , it update the coordinates of the object."""    
    def updateAxes(self):
    
        vtm = self.view.build()
        # print vtm, "176"
        pts = (vtm * self.axes)
        for i in range(0,6,2):
#           print self.canvas.coords(self.lines[i/2]), "vhjvdhj"
            self.canvas.coords(self.lines[i/2], pts[0,i],pts[1,i],pts[0,i+1],pts[1,i+1] )
            self.canvas.coords(self.axis_labels[i/2], (pts[0,i]+pts[0,i+1])/2, (pts[1,i]+ pts[1,i+1])/2)
        # if len(self.mean_labels)>0:
       
            

    """ works the same way as updateAxes but for the data points and changes the coordinates of data objects."""
    def updatePoints(self):
        if (len(self.objects.keys()) == 0):
            return 
    
        vtm = self.view.build()
        pts = (vtm * self.data.T).T   
        for i in range(pts.shape[0]):
#           
            dx= self.shapesRadius + self.size_values[i,0]*10 
            x = float(pts[i,:][0,0])
            y = float(pts[i,:][0,1])
            self.canvas.coords( self.objects.keys()[i], x-dx, y-dx,x+dx,y+dx )
            if len(self.mean_labels) > 0 and (i >= self.data.shape[0] - self.clusterdata.K_value):

                print i,self.data.shape[0], self.clusterdata.K_value
        # for i in range(len(self.mean_labels))
                self.canvas.coords(self.mean_labels[i-self.data.shape[0]+ self.clusterdata.K_value ], x,y)

    def buildMenus(self):
        
        # create a new menu
        menu = tk.Menu(self.root)

        # set the root menu to our new menu
        self.root.config(menu = menu)

        # create a variable to hold the individual menus
        menulist = []

        # create a file menu
        filemenu = tk.Menu( menu )
        menu.add_cascade( label = "File", menu = filemenu )
        menulist.append(filemenu)

        # create another menu for kicks
        cmdmenu = tk.Menu( menu )
        menu.add_cascade( label = "Command", menu = cmdmenu )
        menulist.append(cmdmenu)

        # menu text for the elements
        # the first sublist is the set of items for the file menu
        # the second sublist is the set of items for the option menu
        menutext = [ [ 'Open \xE2\x8C\x98-O', 'Clear \xE2\x8C\x98-N', 'Save \xE2\x8C\x98-S', 'Quit  \xE2\x8C\x98-Q' ],
                     [ 'Linear Regression \xE2\x8C\x98-L', 'About \xE2\x8C\x98-A', '-' ] ]

        # menu callback functions (note that some are left blank,
        # so that you can add functions there if you want).
        # the first sublist is the set of callback functions for the file menu
        # the second sublist is the set of callback functions for the option menu
        menucmd = [ [self.handleOpen, self.clearData,self.saveLinReg, self.handleQuit],
                    [self.handleLinearRegression, self.about, None] ]
        
        # build the menu elements and callbacks
        for i in range( len( menulist ) ):
            for j in range( len( menutext[i]) ):
                if menutext[i][j] != '-':
                    menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
                else:
                    menulist[i].add_separator()

    # create the canvas object
    def buildCanvas(self):
        self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy )
        self.bgimage = tk.PhotoImage(file = os.getcwd() + "/batman2.gif")
        print os.getcwd() + "1.gif"
        self.canvas.create_image(350,300,image = self.bgimage )
        self.canvas.pack( expand=tk.YES, fill=tk.BOTH )

        return

    # build a frame and put controls in it
    def buildControls(self):

        ### Control ###
        # make a control frame on the right
        rightcntlframe = tk.Frame(self.root)
        rightcntlframe.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y)
        pcaframe = tk.Frame(self.root)
        pcaframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)

        # make a separator frame
        sep = tk.Frame( self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
        sep2 = tk.Frame( self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
        sep.pack( side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)
        sep2.pack( side=tk.LEFT, padx = 2, pady = 2, fill=tk.Y)

        # use a label to set the size of the right panel
        label = tk.Label( rightcntlframe, text="Control Panel", width=20 )

        
        label.pack( side=tk.TOP, pady=5 )
        labelp = tk.Label( pcaframe, text="PCA Panel", width=30 )


        labelp.pack( side=tk.TOP, pady=5 )

        self.mousePositionText  = tk.StringVar()
        self.mousePositionText.set("X:         Y:         Z:        ")  
        self.mousePositionLabel = tk.Label(rightcntlframe, textvariable= self.mousePositionText)#output for mouseover
        self.mousePositionLabel.pack(side = tk.TOP)
        self.mousePositionText2  = tk.StringVar()
        self.mousePositionText2.set("Color:         Size:         Shape:        ")  #output for mouseover
        self.mousePositionLabel2 = tk.Label(rightcntlframe, textvariable= self.mousePositionText2)
        self.mousePositionLabel2.pack(side = tk.TOP)
        button = tk.Button( rightcntlframe, text="Clear data", command=self.clearData )                              
        button.pack(side=tk.TOP) 
        button = tk.Button( rightcntlframe, text="Create data",  command=self.handlePlotData )                              
        button.pack(side=tk.TOP) 
        button = tk.Button( rightcntlframe, text="reset", command=self.reset )                               
        button.pack(side=tk.TOP)         
        button = tk.Button( rightcntlframe, text="Linear Regression", command=self.handleLinearRegression )                               
        button.pack(side=tk.TOP)
        button = tk.Button( rightcntlframe, text="clear previous results", command=self.clearpreviousresults )                               
        button.pack(side=tk.TOP)
        button = tk.Button( pcaframe, text="PCA analysis", command=self.PCAanalysis )
        button.pack(side=tk.TOP)
        button = tk.Button( pcaframe, text="delete selected pca results", command=self.pca_remove)
        button.pack(side=tk.TOP)
        button = tk.Button( pcaframe, text="show PCA table", command=self.pca_show)
        button.pack(side=tk.TOP)
        button = tk.Button( pcaframe, text="project data", command=self.handleProjectPCA)
        button.pack(side=tk.TOP)
        button = tk.Button( pcaframe, text="Save PCA as csv", command=self.handleSavePCA)
        button.pack(side=tk.TOP)
        button = tk.Button( pcaframe, text="Cluster Analysis", command=self.handleCluster)
        button.pack(side=tk.TOP)
        button = tk.Button( pcaframe, text="Cluster Analysis(PCA)", command=self.handleClusterPCA)
        button.pack(side=tk.TOP)
        button = tk.Button( pcaframe, text="Plot Cluster Data", command=self.handleClusterPlot)
        button.pack(side=tk.TOP)
        button = tk.Button( pcaframe, text="Write clusterdata to file", command=self.handleClusterSave)
        button.pack(side=tk.TOP)
        button = tk.Button( pcaframe, text="Machine Learning", command=self.handleMachineLearning)
        button.pack(side=tk.TOP)
        button = tk.Button( pcaframe, text="Plot latest machineLearning test data", command=self.handleMachinePlot)
        button.pack(side=tk.TOP)

        # pcaframe = tk.PanedWindow(rightcntlframe, orient = tk.VERTICAL)
        # pcaframe.pack(fill=tk.BOTH, expand=1, side = tk.RIGHT)

        valueframe = tk.PanedWindow(rightcntlframe, orient = tk.VERTICAL)

        
        valueframe.pack(fill=tk.BOTH, expand=1, side = tk.RIGHT)
        
        
         
        button = tk.Button( rightcntlframe, text="Toggle back", command=self.recallback )                               
        button.pack(side=tk.TOP)
        button = tk.Button( valueframe, text="Toggle forward", command=self.recallforward )                               
        button.pack(side=tk.TOP)

        self.pca_listbox =tk.Listbox(pcaframe, width=25, height=30,selectmode=tk.SINGLE, exportselection=0)

        self.pca_listbox.pack(side = tk.TOP) 


        # make a menubutton
        # self.colorOption = tk.StringVar( self.root )
        # self.colorOption.set("black")
        # colorMenu = tk.OptionMenu( rightcntlframe, self.colorOption, 
        #                                 "black", "blue", "red", "green" ) # can add a command to the menu
        # colorMenu.pack(side=tk.TOP)
        # button = tk.Button( rightcntlframe, text="Update color", 
        #                        command=self.handleButton1 )
        # button.pack(side=tk.TOP) 

        

        """I gave the user the option to determine translation rate and rotation rate. i set the default to 500 for rot_speed 
        and 0.1 for translation speed. If the user leaves the text box blank, it automatically fills the default values."""
        label = tk.Label( rightcntlframe, text="Translation rate", width=12 ) #input for trans rate
        label.pack( side=tk.TOP, pady=3 )
        self.trans_rate= tk.Entry(valueframe)
        self.trans_rate.insert(0,"1.0")
        self.trans_rate.pack(side = tk.TOP)

        label = tk.Label( rightcntlframe, text="Rotation rate", width=10 ) #input for rot rate
        label.pack( side=tk.TOP, pady=3 )
        self.rot_rate= tk.Entry(valueframe)
        self.rot_rate.insert(0,"500")
        self.rot_rate.pack(side = tk.TOP)

        # make a button in the frame
        # and tell it to call the handleButton method when it is pressed.
        
         # default side is top
        

        ##legends for axes
        self.label2 = tk.Label( rightcntlframe, text="X-axis:", width=10 )
        self.label2.pack( side=tk.TOP, pady=3 )
        self.xaxis_label= tk.Entry(valueframe)
        self.xaxis_label.pack(side = tk.TOP)
        
        self.label3 = tk.Label( rightcntlframe, text="Y-axis:", width=10 )
        self.label3.pack( side=tk.TOP, pady=3 )
        self.yaxis_label= tk.Entry(valueframe)
        self.yaxis_label.pack(side = tk.TOP)
       
        self.label4 = tk.Label( rightcntlframe, text="Z-axis:", width=10 )
        self.label4.pack( side=tk.TOP, pady=3 )
        self.zaxis_label= tk.Entry(valueframe)
        self.zaxis_label.pack(side = tk.TOP)

        
        self.label5 = tk.Label( rightcntlframe, text="Color:", width=10 )
        self.label5.pack( side=tk.TOP, pady=3 )
        self.coloraxis_label= tk.Entry(valueframe)
        self.coloraxis_label.pack(side = tk.TOP)
        
        self.label6 = tk.Label( rightcntlframe, text="Size:", width=10 )
        self.label6.pack( side=tk.TOP, pady=3 )
        self.sizeaxis_label= tk.Entry(valueframe)
        self.sizeaxis_label.pack(side = tk.TOP)

        
        self.label7= tk.Label( rightcntlframe, text="Shape:", width=10 )
        self.label7.pack( side=tk.TOP, pady=3 )
        self.shapeaxis_label= tk.Entry(valueframe)
        self.shapeaxis_label.pack(side = tk.TOP)


        self.filenameLabel =  tk.Label( rightcntlframe, text="Filename:", width=10 )
        self.filenameLabel.pack( side=tk.TOP, pady=3 )
        self.filename_label= tk.Entry(valueframe)
        self.filename_label.pack(side = tk.TOP)

        self.label8 = tk.Label( rightcntlframe, text="B-values:", width=10 )
        self.label8.pack( side=tk.TOP, pady=3 )
        self.bvalues_label= tk.Entry(valueframe)
        self.bvalues_label.pack(side = tk.TOP)


        
        self.label9 = tk.Label( rightcntlframe, text="sse:", width=10 )
        self.label9.pack( side=tk.TOP, pady=3 )
        self.sse_label= tk.Entry(valueframe)
        self.sse_label.pack(side = tk.TOP)
       
        self.label10 = tk.Label( rightcntlframe, text="R2:", width=10 )
        self.label10.pack( side=tk.TOP, pady=3 )
        self.r2_label= tk.Entry(valueframe)
        self.r2_label.pack(side = tk.TOP)
        
        self.label11 = tk.Label( rightcntlframe, text="t:", width=10 )
        self.label11.pack( side=tk.TOP, pady=3 )
        self.t_label= tk.Entry(valueframe)
        self.t_label.pack(side = tk.TOP)
        
        self.label12 = tk.Label( rightcntlframe, text="p :", width=10 )
        self.label12.pack( side=tk.TOP, pady=3 )
        self.p_label= tk.Entry(valueframe)
        self.p_label.pack(side = tk.TOP)   

   
        return

    def setBindings(self):
        # bind mouse motions to the canvas
        self.canvas.bind( '<Button-1>', self.handleMouseButton1 )
        self.canvas.bind( '<Control-Button-1>', self.handleMouseButton2 )
        self.canvas.bind(' <Control-Shift-Button-1>', self.handleMouseButton3)
        self.canvas.bind( '<Button-2>', self.handleMouseButton2 )
        self.canvas.bind( '<B1-Motion>', self.handleMouseButton1Motion )
        self.canvas.bind( '<B2-Motion>', self.handleMouseButton2Motion )
        self.canvas.bind( '<Control-B1-Motion>', self.handleMouseButton2Motion )
        self.canvas.bind( '<Control-Shift-B1-Motion>', self.handleMouseButton3Motion )
        self.canvas.bind( '<Configure>', self.resize )
        # self.canvas.bind( '<Shift-Command-Button-1>', self.deletePointData )
        self.canvas.bind( '<Motion>', self.mouseOverObject)
        self.root.bind('<Command-n>',self.clearData)
        self.root.bind('<Command-o>',self.handleOpen)
        self.root.bind('<Control-o>',self.handleOpen)
        self.root.bind('<Control-l>',self.handleLinearRegression)
        self.root.bind('<Command-l>',self.handleLinearRegression)
        self.root.bind('<Control-s>',self.saveLinReg)
        self.root.bind('<Command-s>',self.saveLinReg)
        self.root.bind('<Command-p>', self.PCAanalysis)
        self.root.bind('<Command-a>', self.about)



        # bind command sequences to the root window
        self.root.bind( '<Command-q>', self.handleQuit )

    def handleQuit(self, event=None):
        print 'Terminating'
        self.root.destroy()

    def clearData(self, event=None, recall= 0): #when recalling, do not need to save current values
        ##should clear all data objects and should reset the axes labels
        if recall == 0 and len(self.selected_axes)>0: #only save if the user has actually selected axis
            self.previousResults.append([self.data_file,self.selected_axes, self.raw_data, self.view.clone()])
        for obj in self.objects.keys():
          self.canvas.delete(obj)
          # print "deleting"
        for obj in self.mean_labels:
            self.canvas.delete(obj)  
        self.objects = {} 

        #resting axes labels
        labels = [self.xaxis_label,self.yaxis_label, self.zaxis_label, self.coloraxis_label, self.sizeaxis_label, self.shapeaxis_label, self.bvalues_label, self.sse_label, self.r2_label, self.t_label, self.p_label]
        # texts = ["X-axis:            ","Y-axis:            ", "Z-axis:            ", "Color:            ", "Size:            ", "Shape:            ", "B-Values","sse:", "R^2","t:", "p:"  ]
        for i in range(len(labels)):
            # print "hahahahhahahah"
            # labels[i].config(text= texts[i])
            labels[i].delete(0,tk.END)

        for line in self.linregLines:
            self.canvas.delete(line)
        self.endpoints = None 
        self.mean_labels = []
        # self.clusterdata = None
        self.linRegressresults = []
        self.linregLines = []  
        self.selected_axes = []

           

    #uses the self.baseview field which is the original view to reset the view        
    def reset(self):
        "reseting"
        self.view = self.baseview
        self.updateAxes()
        self.updateFits()
        self.updatePoints()
        self.baseview=self.view.clone()    
       
    #resizes the screen, to do this, i made it such that the view class takes in a dimension which it uses to determine screen size
    #so when the canvas gets resized, i change the screen size using the field and update axes and update points. I first bind it to <configure>   
    def resize(self, event):
        
        # take the min of 
        self.view.view_size = min(self.canvas.winfo_width(), self.canvas.winfo_height() )*0.65
        self.view.updateScreen()
        
        self.updateAxes()
        self.updatePoints()
        self.updateFits()

        #also change the screen size in baseview so that when the user resets in a smaller window, it will act accordingly
        self.baseview.view_size = min(self.canvas.winfo_width(), self.canvas.winfo_height() )*0.65
        self.baseview.updateScreen()



    ##HANDLES THE FILE OPENING    

    def handleOpen(self,event=None):
        self.data_file = tkFileDialog.askopenfilename( parent=self.root,title='Choose a data file', initialdir='.' )
        # self.data_file= "AustraliaCoast.csv"
        self.filename_label.delete(0, tk.END)#first erase whatever is in there
        self.filename_label.insert(0,self.data_file[self.data_file.rfind("/")+1:] ) 
        
    def handleMenuCmd1(self):
        print 'handling menu command 1'

    def handleMouseButton1(self, event):
        print 'handle mouse button 1: %d %d' % (event.x, event.y)
        self.baseClick = (event.x, event.y)

    #REGISTERS THE CLICK BEFORE ROTATION /CLONES THE ORININAL VIEW   
    def handleMouseButton2(self, event):
        self.baseClick2 = (event.x, event.y)
        self.rotview = self.view.clone()
        print 'handle mouse button 2: %d %d' % (event.x, event.y)

    #REGISTERS THE CLICK BEFORE TRANSLATION /CLONES THE ORININAL EXTENT
    def handleMouseButton3(self, event):
        self.baseClick = (event.x, event.y)
        self.baseextent = copy.deepcopy(self.view.extent)
        print 'handle mouse button 3: %d %d' % (event.x, event.y)
    

    """HANDLES PLot data, lets the user select columns for each axis. I made a class axisDisplayBox in display.py such that it takes in list of headers
    #as external parameter and lets the user select one of them for each axis. The z-axis, color axis, size, shape are optional, so I included a 
    #option of 'None' for those axis. By default the selection is always the first item in the listbox. So if the user does not select anything ie selection is [
    #first header, first header, none, none, none, none] it selects the first three columns as the default. a possible problem is when the user actually selects those first items in the list,
    instead of notifying the user of error, it will pick the first three columns as x,yz axis. also, it doesnt let the user select one header for two different axis.
    To do this, in my axisDisplayBox class, I return a list containing all the selections with a dictionary as its last element which has error key which shows how many
    duplications have been made. detecting that number is the key to letting the user know about the duplication"""
    def handlePlotData(self, pca = None, clusterData = None,machineData = None):
        self.clearData()


        if pca != None: 
            self.raw_data = pca   
        elif clusterData != None:
            self.raw_data = clusterData
        elif machineData != None:
            self.raw_data = machineData
            
        else:
            if self.data_file == None :
                tkMessageBox.showinfo(title=None, message="Select a csv file first (File>>Open)") #check if the user has uploaded a csv file
                return
            self.raw_data = data.Data(self.data_file) 


        # print self.raw_data.raw_headers
        # headers = []
        header_options = self.raw_data.raw_headers #if pca== None else pca.raw_headers
        axisDisplayBox = display.AxisDisplay(self.root, external_parameter= header_options, clustermeans =(clusterData != None))  
        # print axisDisplayBox.result, "axis_display_result"
        # print axisDisplayBox.result[-1]["error"] > 0
        print axisDisplayBox.result, "510"

        if axisDisplayBox.result[:3] == [self.raw_data.raw_headers[0], self.raw_data.raw_headers[0], "None"]: ##assume the user didnt select anything
            self.selected_axes = self.raw_data.raw_headers[:3] + ["None","None","None"] #default

        elif axisDisplayBox.result[-1]["error"] > 0 :
            print axisDisplayBox.result
            tkMessageBox.showinfo(title=None, message="Dude, u selected duplicate headers for different axes..try again")
            self.handlePlotData(pca, clusterData)
            return
    
        else:
            
            self.selected_axes = axisDisplayBox.result[:-1] #everything except the dictionary at the last

        # print selected_headers, "vhqvshjwv"


        # labels = [self.x_label, self.y_label, self.z_label, self.color_label, self.size_label, self.shape_label]
        
        '''after the user has selected axis, create legends'''
        labels = [self.xaxis_label,self.yaxis_label, self.zaxis_label, self.coloraxis_label, self.sizeaxis_label, self.shapeaxis_label]
        for i in range(len(labels)):
            # text = labels[i].cget("text")
            labels[i].insert(0,self.selected_axes[i])
        print  self.selected_axes, "line 627, tkbase.py"
        self.buildpoints(self.selected_axes, clusterData = clusterData) #pass the list of headers to buildpoints function //headers in the order x,y,z


    # This is called if the first mouse button is being moved
    """It will store the user's click into a variable ( baseClick1). The  function should calculates the differential motion since the last 
    time the function was called , divides the differential motion (dx, dy) by the screen size (view X, view Y) , multiplies the horizontal and 
    vertical motion by the horizontal and vertical extents, putsthe result in delta0 and delta1. The VRP should be updated by delta0 * U + delta1 * VUP followed by updateAxes"""
    def handleMouseButton1Motion(self, event):
        # calculate the difference
        if self.trans_rate.get() == "":
            self.trans_rate.insert(0, "1.0")
        print event.x, event.y, self.baseClick[0], self.baseClick[0], self.view.screen[0], self.view.screen[1]
        diff = ( (event.x - self.baseClick[0])/self.view.screen[0], (event.y - self.baseClick[1])/self.view.screen[1] )
#       print event.x, event.y, self.baseClick[0], self.baseClick[0], self.view.screen[0], self.view.screen[1]
        # print diff, "diff"
        delta0 = diff[0]* self.view.extent[0]*float(self.trans_rate.get())
        delta1 = diff[1]* self.view.extent[1]*float(self.trans_rate.get())
        # print delta0, delta1 , "29hjdvwvd"
        # print self.view.vrp, "294gvy"
        for i in range(3):
#           print self.view.vrp[0,i] , "29efewrfe5"
            self.view.vrp[0,i] += delta0* self.view.u[0,i] + delta1*self.view.vup[0,i]
            # print self.view.vrp[0,i], "ydvhw"
        # print self.view.vrp , "298hdbh"
        self.updateAxes()   
        self.updatePoints()
        self.updateFits()
        self.baseClick = (event.x, event.y)

        print 'handle button1 motion %d %d' % (diff[0], diff[1])

    """ bind rotation to mouse2 motion. The button 2 click storse the button click location into a variable like baseClick2. 
    The same function should stores a clone of my View object. This is the original View object. . Within the  function, first calculate delta0 and delta1 
     as the pixel motion differences in x and y divided by a constant (500 by default) and multiplied by pi (math.pi) and store it in diff  
    I clone the original View object and assign it to your standard view field, then rotate the view using the rotateVRC method and the two angles delta0 and delta1. Then I call updateAxes. """   
    def handleMouseButton2Motion(self, event):
        print 'handle button 2 motion'

        # rot_rate = self.rot_rate.get()
        if self.rot_rate.get() == "":
            self.rot_rate.insert(0, "500")
        # self.rotview = self.view.clone()
        # print event.x, self.baseClick2[0], event.y, self.baseClick2[1]
        diff = ( ((event.x - self.baseClick2[0])/float(self.rot_rate.get()))*math.pi, ((event.y - self.baseClick2[1])/float(self.rot_rate.get()))*math.pi )
        # print diff, "diff"
        self.view = self.rotview.clone()
        self.view.rotateVRC(diff[0],-diff[1])
        self.updateAxes()
        self.updatePoints()
        self.updateFits()

        # self.view = self.rotview.clone()

    """The scaling behavior should act like a vertical lever. 
    The button 3(ctrl-shift-button-1) click should store a base click point that does not change while the user holds down the mouse button. 
    It should also store the value of the extent in the view space when the user clicked. This is the original extent. it then converts the distance 
    between the base click and the current mouse position into a scale factor. I use this formula: diff = 1+((event.y - self.baseClick[1])/self.view.screen[1] ). 
    I then multiply the original extent by the factor and put it into the View object. Then call updateAxes(). """      

    def handleMouseButton3Motion(self, event):
        print "mousebutton3 motion"
        # extent = copy.deepcopy(self.view.extent) #clone
        # print extent
        
        diff = 1+((event.y - self.baseClick[1])/self.view.screen[1] )
#         for i in range
            
        diff = 3 if diff > 3 else diff
        diff = 0.1 if diff <0.1 else diff
        extent = np.multiply(diff, self.baseextent)
        print diff, extent, "extent"
        self.view.extent = extent*diff
        self.updateAxes()
        self.updatePoints()
        self.updateFits()

      
    #lets the user select shape
    # def chooseShape(self,event = None):
    #   shapeBox = display.ShapeListBox(self.root, ["rectangle","oval"])
    #   self.shape = shapeBox.result
    #   print self.shape


          
    
    #mouseover function: displays the data point over which the cursor lies. it uses the fact that self.objects is a dictionary which maps each object to its raw_values
    def mouseOverObject(self, event):
        # pass
        if len(self.objects.keys()) > 0:  
          found = False
          for obj in self.objects.keys():
              loc = self.canvas.coords(obj)
              # print loc
              if (event.x < loc[2] and event.x > loc[0]) and (event.y < loc[3] and event.y > loc[1]):
                # print self.obje
                  print  self.objects[obj]  
                  [x,y,z,color,size,shape] = self.objects[obj]
                  print x,y,z,color,size,shape
                  self.mousePositionText.set(" X: "+ x[:4] + "  "+ " Y:"+ y[:4]+"  " +" Z:"+ z[:4] + "  ")
                  self.mousePositionText2.set(" Color: "+ color[:4]+ "  " + " Size:"+ size[:4] +"  " + " Shape:"+ shape[:4] + "  ")
                  found = True
                  break
          if found == False:
            self.mousePositionText.set(" X:      "+ " Y:      " + " Z:      ")  
            self.mousePositionText2.set(" Color:      "+ " Size:      " + " Shape:      ")         
    

    def handleLinearRegression(self,event=None):
        if len(self.selected_axes) == 0: #if the user has not plotted points
            self.handlePlotData()
            return

        # print self.raw_data.raw_headers
            # lnregDisplayBox = display.LinearRegressionDisplay(self.root, external_parameter= self.raw_data.raw_headers)
        # else: #if the user has already selected data
            # lnregDisplayBox = display.LinearRegressionDisplay(self.root, external_parameter= self.selected_axes)
                
        # selected_headers = lnregDisplayBox
        # print lnregDisplayBox.result, "620, tkbase"
        # self.buildLinearRegression()




        #first calls linear regression to calculate everything 
        self.linear_regression(self.selected_axes, self.raw_data)


        
    
    def buildLinearRegression(self, list_of_selected_headers, list_of_beta_values ): #draws plane or line, list of selected headers will either be x,y or x,y,z
        # print list_of_selected_headers, "buildlinearregresison"
        vtm =  self.view.build()
        unnormalized_data = self.raw_data.get_data(list_of_selected_headers)  
        # slope, intercept, r_value, p_value, std_err  = scipy.stats.linregress(unnormalized_data)  
        [[xmax,xmin],[ymax,ymin]] = analysis.data_range(list_of_selected_headers, self.raw_data)[:2] # output = [[xmax,xmin],[ymax,ymin], [zmin,zmax]#if two independent selected] for now take only first two
        [zmax,zmin] = analysis.data_range(list_of_selected_headers, self.raw_data)[-1] if len(list_of_selected_headers) == 3 else [0,0]
        [xslope, intercept] = [list_of_beta_values[0], list_of_beta_values[-1]]
        zslope = list_of_beta_values[1] if len(list_of_selected_headers) == 3 else 0
        #beta values = bx, bz, intercept

        #calculates y-endpoints for a line 
        y1_endpoint = ((xmin * xslope + zmin*zslope + intercept) - ymin)/(ymax - ymin)
        y2_endpoint = ((xmax * xslope + zmin*zslope + intercept) - ymin)/(ymax - ymin)
        self.endpoints = np.matrix([[0, y1_endpoint,0,1],[1,y2_endpoint,0,1]])



        #if two independet axes, then draw a plane, so calculate tw more endoints
        if len(list_of_selected_headers) == 3:
            
            y3_endpoint = ((zmax * zslope + xmin*xslope + intercept) - ymin)/(ymax - ymin)
            y4_endpoint = ((xmax*xslope + zmax * zslope + intercept) - ymin)/(ymax - ymin)
            self.endpoints = np.concatenate((self.endpoints,np.matrix([[0, y3_endpoint,1,1],[1, y4_endpoint,1,1] ])), axis=0)

        # print np.matrix(self.endpoints), "\n", vtm, "657"
        endpoints = (vtm * self.endpoints.T).T
        # print endpoints, "659"
        if len(list_of_selected_headers) == 2: #will draw a line if 2 selected headers
            line_of_best_fit = self.canvas.create_line( endpoints[0,0],endpoints[0,1], endpoints[1,0], endpoints[1,1], fill="red" )  
            self.linregLines.append(line_of_best_fit)
        elif len(list_of_selected_headers) == 3: # will draw a plane if 3
            plane_of_best_fit = self.canvas.create_polygon(endpoints[0,0],endpoints[0,1], endpoints[1,0], endpoints[1,1],endpoints[3,0], endpoints[3,1], endpoints[2,0], endpoints[2,1], fill = "Red", stipple="gray50")  
            self.linregLines.append(plane_of_best_fit)
        else:
            tkMessageBox.showinfo(title=None, message="Too many independent values, cannot draw a line or plane")    


    def updateFits(self):
        if self.endpoints != None:
            "updating fits"
            vtm = self.view.build()
            # print vtm, "176"
            endpoints = (vtm * self.endpoints.T).T
            #checks the shape of endpoints to determine if it is line or plane
            if endpoints.shape[0] == 2:
                self.canvas.coords(self.linregLines[0],endpoints[0,0],endpoints[0,1], endpoints[1,0], endpoints[1,1])
            elif endpoints.shape[0] == 4:    
                self.canvas.coords(self.linregLines[0],endpoints[0,0],endpoints[0,1], endpoints[1,0], endpoints[1,1],endpoints[3,0], endpoints[3,1], endpoints[2,0], endpoints[2,1]  )



    def linear_regression(self, list_of_selected_headers, raw_data): # takes in parameter so that even outside files can use this function, its kinda independent
        list_of_selected_headers = filter(lambda x:x !="None",list_of_selected_headers) #remove all None, assume x1,y as the first two elements
        # print list_of_selected_headers
        y = raw_data.get_data([list_of_selected_headers[1]]) #2nd elemnt must be dependent
        A =  raw_data.get_data([list_of_selected_headers[0]]+list_of_selected_headers[2:])#x1 first elemnt, whatever from 3rd element pnwards is independnt
        one_coor = [1]*A.shape[0]
        A = np.concatenate((A, np.matrix([one_coor]).T),axis=1)
        AAinv = np.linalg.inv( np.dot(A.T, A))
        x = np.linalg.lstsq( A, y )
        b = x[0]
        N = y.shape[0]
        C = b.shape[0]

        # assign to df_e the value N-C, #    This is the number of degrees of freedom of the error
        df_e = N-C
        
         # assign to df_r the value C-1 #    This is the number of degrees of freedom of the model fit
        df_r = C-1
         
          
        error = y-np.dot(A,b)  

        sse = np.dot(error.T,error)/df_e

        #the standard error, which is the square root of the diagonals of the sum-squared error multiplied by the #    inverse covariance matrix of the data. 
        sterr = np.sqrt(np.diagonal(sse[0,0]*AAinv))

        #t, the t-statistic for each independent variable by dividing #    each coefficient of the fit by the standard error.
        t = b.T/sterr

        #p, the probability of the coefficient indicating a  #    random relationship. To do this we use the cumulative distribution  #    function of the student-t distribution.
        p = (1 - scipy.stats.t.cdf(abs(t), df_e))

        #r2, the r^2 coefficient indicating the quality of the fit.
        r2 = 1 - error.var() / y.var()

        #resuts in a list
        results= [b, sse, r2,t,p]

        #result string in string format from matrix from
        results_string = []

        labels = [self.bvalues_label,self.sse_label,self.r2_label, self.t_label, self.p_label]
        for i in range(len(labels)):
            result_string = " ,".join(str(elem)[:4] for elem in np.array(results[i]).reshape(-1,).tolist()) #only show first four digits
            labels[i].delete(0,tk.END)
            labels[i].insert(0,result_string ) #convert each result matrix to a list and then to a string
            results_string.append(result_string)
        self.linRegressresults.append(results_string) #store all resullts in a field which is a list so that we can save those   
        
        # print np.array(results[0]).reshape(-1,).tolist(), "beta values"

        #calls buildlinearregression to draw a line or plane or nothing
        self.buildLinearRegression(list_of_selected_headers, np.array(results[0]).reshape(-1,).tolist())


            

    """asks the user to save a file/saves the last results"""
    def saveLinReg(self,event=None):                                                                #current file minus the extension, minus address
        dest_file = tkFileDialog.asksaveasfile(mode='w', defaultextension = "txt", initialfile = self.data_file[self.data_file.rfind("/")+1:-4]+"_analysis", title = "Save analysis results as ", parent = self.root) #opens file in write mode
        value= ["B-values", " sum-squared error", "r^2 coefficient", "t-statistic", "probability of the coefficient indicating a random relationship"]
        
        print self.linRegressresults, type(self.linRegressresults)
        if len(self.linRegressresults) >= 1: #checks if user calls it after saving at least one linear regression
            for i in range(len(self.linRegressresults[-1])):
                dest_file.write(value[i]+" : " + self.linRegressresults[-1][i] + "\n")

    """lets the user recall the previous linregress results, it stores all the data when the user clicks """
    def recallback(self, event = None, forward = 0): #some bug in this, will fix it later, not important
        pass
        #increase the counter
        # if forward == 1:
        #     self.recallforwardcount += 1
        # else:
        #     self.recallCount += 1
    
        
        # print self.previousResults, self.recallCount, self.recallforwardcount

        # if len(self.previousResults)>= self.recallCount and self.recallCount > self.recallforwardcount: #the number of toggles is valid i.e. if there are results to display.

        #     self.clearData(recall = 1) #clears whatver is on screen, but doesnt save it, thats why it passes recall=1 parameter
        #     # self.previousResults[(-1*self.recallCount)+self.recallforwardcount]= [self.data_file,self.selected_axes, self.raw_data, self.view]

        #     self.view = self.previousResults[(-1*self.recallCount)+self.recallforwardcount][-1]
        #     self.data_file = self.previousResults[-1*self.recallCount +self.recallforwardcount][0]
        #     self.selected_axes = self.previousResults[-1*self.recallCount+self.recallforwardcount][1]
        #     self.raw_data = self.previousResults[-1*self.recallCount+self.recallforwardcount][2]

        #     labels = [self.xaxis_label,self.yaxis_label, self.zaxis_label, self.coloraxis_label, self.sizeaxis_label, self.shapeaxis_label] #updates the axis
        #     # print self.selected_axes
        #     for i in range(len(labels)):
        #     # text = labels[i].cget("text")
        #         labels[i].insert(0,self.selected_axes[i])

        #     #update filename_label    
        #     self.filename_label.delete(0, tk.END)#first erase whatever is in there
        #     self.filename_label.insert(0,self.data_file[self.data_file.rfind("/")+1:] ) 
        #     #build everything
        #     self.buildpoints(self.selected_axes)
        #     self.updatePoints()
        #     self.updateAxes()
        #     self.linear_regression( self.previousResults[-1*self.recallCount+self.recallforwardcount][1], self.previousResults[-1*self.recallCount+self.recallforwardcount][2])
        #     self.updateFits()
        # else:
        #     # no results to display
        #     tkMessageBox.showinfo(title=None, message="No results to display, probably toggled too much or didnt save a result. remember to vlear a data to save it in temp")
        #     if forward == 1:
        #         self.recallforwardcount -= 1
        #     else:    

        #         self.recallCount -= 1
              

    """when the user toggles forward"""        
    def recallforward(self, event =None):
        self.recallback(forward = 1)  #calls recallback with forwards parameter

    """when the user clears the previous results"""    
    def clearpreviousresults(self,event=None):
        self.previousResults = []
        self.recallforwardcount =0
        self.recallCount = 0  

#################################    P    C    A   ##########################################################################################################################################################################    
    def PCAanalysis(self,event=None):
        """will first check if the user opened a file. if he did, it will read the data from the file, run pca analysis on it after getting input from user through a dialog box.
        The user will input the headers, if the data should be normalized, and the name of the analysis, then it will insert an entry into listbox in pca control panel"""
        if self.data_file == None:
            # tkMessageBox.showinfo(title=None, message="Select a csv file first (File>>Open)") #check if the user has uploaded a csv file
            self.handleOpen()

        raw_data = data.Data(self.data_file)
        pcaboxdisplay = display.PCABox(self.root, external_parameter= raw_data.raw_headers)
        if len(pcaboxdisplay.result) < 4 :
            tkMessageBox.showinfo(title=None, message="Please select at least two columns")
            return
            
        print "bbbb"    
        print pcaboxdisplay.result , "line 889" #pcaboxdisplay = [headers, headers...., normalise_status, name_of_analysis]
        normalize = True if pcaboxdisplay.result[-2] == 1 else False
        print normalize, "checking if normalize is true"
        pcadata = analysis.pca( data_object = raw_data, header_list =pcaboxdisplay.result[:-2], normalize = normalize)
        self.pcadata_collection[pcaboxdisplay.result[-1]] = pcadata
        self.pca_listbox.insert(tk.END, pcaboxdisplay.result[-1] )
        length_of_list_box = len(self.pcadata_collection.keys())-1
        self.pca_listbox.selection_clear(first = 0, last =length_of_list_box-1 )
        self.pca_listbox.selection_set(first = length_of_list_box )
        

        ###test code
        # result = ["premin","salmin","salmax", True, "blahblah"]
        # pcadata = analysis.pca( data_object = raw_data, header_list =result[:-2], normalize = True)
        # self.pcadata_collection.append(pcadata)
        # self.pca_listbox.insert(tk.END, result[-1] )

        

    
    def pca_remove(self,event = None) :
        """will remove the selected pca_result. first it will get the selected result, will delete it from dictionary field which stores the results and then it will delete it from listbox. 
        It will also clear the display if the pca being deleted is the one being displayed"""
        if (len(self.pcadata_collection.keys())) > 0:
            if self.current_projected_pca == self.pca_listbox.get(tk.ACTIVE):
                print "clearing pca"
                self.clearData()

            self.pcadata_collection.pop(self.pca_listbox.get(tk.ACTIVE))
            self.pca_listbox.delete(tk.ACTIVE)
  


    def pca_show(self,event = None):
        """will check if there are analysis results stored, then will get the eigen_info associated with the selected result"""
        if (len(self.pcadata_collection.keys())) > 0:
            pca_table = display.pca_infobox(self.root, external_parameter = self.pcadata_collection[self.pca_listbox.get(tk.ACTIVE)] ) #calls the 
            print "showing pca_table for "+ self.pca_listbox.get(tk.ACTIVE) 
        else :
            print "no analysis"

    def handleProjectPCA(self):
        """will call handlePlotData withe a parameter pca= the selected pca and then the handleplot will take care of plotting the projected data"""
        if (len(self.pcadata_collection.keys())) > 0:
            self.current_projected_pca = self.pca_listbox.get(tk.ACTIVE)
            self.handlePlotData(pca =self.pcadata_collection[self.pca_listbox.get(tk.ACTIVE)]) 


    def handleSavePCA(self):
        #if the user wants to save...it will prompt for filename/directory and use function in data to save as csv
        if (len(self.pcadata_collection.keys())) > 0:
            print "saving " + self.pca_listbox.get(tk.ACTIVE)
            file_name = tkFileDialog.asksaveasfile(mode='w', defaultextension = "csv", initialfile ="pca_analysis", title = "Save analysis results as ", parent = self.root) #opens file in write mode
            # while  file_name.__getattribute__('name')[-3:0] != "csv":
            #     print file_name.__getattribute__('name')[-3:0]
            #     tkMessageBox.showinfo(title=None, message="Don't use extension other than csv  ")


            #     file_name = tkFileDialog.asksaveasfile(mode='w', defaultextension = "csv", initialfile ="pca_analysis", title = "Save analysis results as ", parent = self.root)

            self.pcadata_collection[self.pca_listbox.get(tk.ACTIVE)].get_csv_for_pca_data(file_name)    
    def about(self,event = None):
        tkMessageBox.showinfo(title=None, message="The B.A.T.M.A.N \n The Best App To Model and ANalyze (data)")


    """it will exceute when the user clicks on cluster analysis button """    
    def handleCluster(self, event = None, pca= False): 
        if self.data_file == None:
            # tkMessageBox.showinfo(title=None, message="Select a csv file first (File>>Open)") #check if the user has uploaded a csv file
            self.handleOpen()

        if not pca: 
            raw_data = data.Data(self.data_file) #cluster on currently opened file if pca is none #for dual function 
        else:
            raw_data = self.pcadata_collection[self.pca_listbox.get(tk.ACTIVE)] #or do it on  the currently selected pcadata   
        Kbox = display.KBox(self.root, external_parameter =raw_data.get_raw_headers() ) #dialog box
        if Kbox.result != None: #if the user camncels teh window
            if   len(Kbox.result)<3:
                self.handleCluster() #the K box will return at least two values euclidean(metric), 1(K-value), this checks whether the user selected ay header
                return
            elif  int (Kbox.result[-1]) > raw_data.matrix_data.shape[0] : #check if K value is valid
                tkMessageBox.showinfo(title=None, message="K value is greater than number of rows in actual data")
                self.handleCluster()
                return   
            #eg kbox result =  [ "header1",...."headern", "euclidean", "1"]   

            K = int (Kbox.result[-1]) 

            
            metric = Kbox.result[-2]
            header_selected =  Kbox.result[:-2]
            # print header_selected, "header_selected"

            self.clusterdata = analysis.kmeans(raw_data, header_selected, K, metric) #assign the cluster analysis data to a field

            if tkMessageBox.askyesno("Plot", "Do you want to plot the cluster data?"): #prompt the user if he or she wants to plot
                self.handleClusterPlot()

    def handleClusterPlot(self, event= None):
        # self.clusterdata.write(dest_file ="australiam.csv")
        if self.clusterdata != None: 
            self.handlePlotData(clusterData = self.clusterdata)
        else:
            self.handleCluster()    
        
        # ClusterDisplayBox  =  display.AxisDisplay(self.root, external_parameter = self.clusterdata.get_raw_headers(), clustermeans = True )   
    
    def handleClusterPCA(self, event= None):
        if (len(self.pcadata_collection.keys())) > 0: #check if there's actually any pca_analysis done
            self.handleCluster(pca= True)
        else:
            tkMessageBox.showinfo(title=None, message="Run PCA analysis first")
                

    def handleClusterSave(self, event = None):
        """user can save the cluster analysis to a file"""
        if self.clusterdata != None:
            print "saving cluster data"
            file_name = tkFileDialog.asksaveasfile(mode='w', defaultextension = "csv", initialfile ="cluster_analysis", title = "Save analysis results as ", parent = self.root) #opens file in write mode
            self.clusterdata.write(dest_file = file_name)
            
    def handleMachineLearning(self, event = None):
        machineDialog = display.machineDialog(self.root)
        print machineDialog.result, "machineDialogresult"
        if len(machineDialog.result) < 3 and machineDialog.result != None:
            tkMessageBox.showinfo(title= None, message = "Please select at least one training file and test file")
            # self.handleMachineLearning()
            return




        # algorithm = machineDialog.result[-1]
        machineLearning.main(machineDialog.result)
        if tkMessageBox.askyesno("Plot", "Do you want to plot the test data with new categories?"):
                self.handleMachinePlot()

    def handleMachinePlot(self, event= None):
        try:
            cData = data.Data("test_data_classified.csv")
            print "seems file exists"
            print cData.getClusterIds(), "clusterIds"
            self.handlePlotData(clusterData=data.Data("test_data_classified.csv"))
        except:
            pass



    def main(self):
        print 'Entering main loop'
        self.root.mainloop()


       


if __name__ == "__main__":
    dapp = DisplayApp(1200, 675)
    dapp.buildAxes()
    dapp.main()

