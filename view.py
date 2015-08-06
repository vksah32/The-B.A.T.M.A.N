##Author: Vivek Sah
##view.py
##last edited 03/02/2015


import numpy as np
import math
import copy

class View:
    """view class for 3d viewing"""
    def __init__(self, view_size):
        self.view_size = view_size
        self.vrp = np.matrix([0.5,0.5,1])
        self.vpn = np.matrix([0.0,0,-1])
        self.vup = np.matrix([0.0,1,0])
        self.u = np.matrix([1.0,0,0])
        self.extent = [1.0,1.0,1.0]
        self.screen = [self.view_size,self.view_size]
        self.offset = [20.0,20]
#         self.build()
        
    """builds view transformation matrix"""
    def build(self):
        print self.screen ," self.screen, 25"
        vtm = np.identity( 4, float )
        # print vtm, "21"
        t1 = np.matrix( [[1.0, 0, 0, -self.vrp[0, 0]],
                        [0, 1, 0, -self.vrp[0, 1]],
                        [0, 0, 1, -self.vrp[0, 2]],
                        [0, 0, 0, 1] ] )

#         print t1, "t1"
        vtm = t1 * vtm
#         print vtm, "vtm"

        tu = self.normalize(np.cross(self.vup, self.vpn))

        tvup = self.normalize(np.cross(self.vpn, tu))
#         print tvup, "tvup"
        tvpn =self.normalize(np.matrix([self.vpn[0,0], self.vpn[0,1], self.vpn[0,2]]))

#         print tvpn, "tvpn"
        field_vectors = [self.u, self.vup, self.vpn]
        vectors = [tu,tvup,tvpn]
        for i  in range(len(vectors)):
            for j in range(3):
                field_vectors[i][0,j]= vectors[i][0,j]

        r1 = np.matrix( [[ tu[0, 0], tu[0, 1], tu[0, 2], 0.0 ],
                        [ tvup[0, 0], tvup[0, 1], tvup[0, 2], 0.0 ],
                        [ tvpn[0, 0], tvpn[0, 1], tvpn[0, 2], 0.0 ],
                        [ 0.0, 0.0, 0.0, 1.0 ] ] )

#         print r1, "r1"
        vtm = r1 * vtm  

#         print vtm, "44"  
        new_t_matrix = np.matrix([[1.0,0,0,0.5*self.extent[0]],
                               [0,1,0,0.5*self.extent[1]],
                               [0,0,1,0],
                               [0,0,0,1] ])
        vtm = new_t_matrix*vtm

#         print vtm, "extent"
        new_scale_matrix = np.matrix([[-self.screen[0] / self.extent[0], 0.0,0,0],
                                     [0, -self.screen[1] / self.extent[1], 0,0 ],
                                     [0,0,1.0 / self.extent[2],0],
                                     [0,0,0,1]])
        vtm = new_scale_matrix*vtm
#         print new_scale_matrix, "64"
#         print vtm, "65"
        new_t2_matrix = np.matrix([[1.0,0,0,self.screen[0] + self.offset[0]],
                               [0,1,0,self.screen[1] + self.offset[1]],
                               [0,0,1,0],
                               [0,0,0,1] ])


        vtm = new_t2_matrix*vtm


        return vtm


    """To implement rotation, I made a function rotateVRC in view class that takes two angles as arguments, in addition to self. 
    The two angles are how much to rotate about the VUP axis and how much to rotate about the U axis. Then, I follow the instruction to carry out this method."""

    def rotateVRC(self, angle_vup, angle_u):
        #translate a point which to thr origin
         t1 = np.matrix( [[1.0, 0, 0, (self.vrp[0,0] + self.vpn[0,1] * self.extent[2] * 0.5)],
                        [0.0, 1, 0, (self.vrp[0,1] + self.vpn[0,1] * self.extent[2] * 0.5)],
                        [0, 0, 1, (self.vrp[0,2] + self.vpn[0,2] * self.extent[2] * 0.5)],
                        [0, 0, 0, 1.0] ] )
         (tu, tvup, tvpn) = (self.u, self.vup, self.vpn)
         Rxyz = np.matrix( [[ tu[0, 0], tu[0, 1], tu[0, 2], 0.0 ],
                        [ tvup[0, 0], tvup[0, 1], tvup[0, 2], 0.0 ],
                        [ tvpn[0, 0], tvpn[0, 1], tvpn[0, 2], 0.0 ],
                        [ 0.0, 0.0, 0.0, 1.0 ] ] )
         #rotation matrix1               
         r1 =  np.matrix( [[ math.cos(angle_vup), 0.0, math.sin(angle_vup), 0.0 ],
                        [ 0.0, 1.0, 0.0, 0.0 ],
                        [ -math.sin(angle_vup), 0.0, math.cos(angle_vup), 0.0 ],
                        [ 0.0, 0.0, 0.0, 1.0 ] ] )
         #rotation matrix2
         r2 =  np.matrix( [[ 1.0, 0.0,0.0 , 0.0 ],
                        [ 0.0, math.cos(angle_u), -math.sin(angle_u), 0.0 ],
                        [ 0.0, math.sin(angle_u), math.cos(angle_u), 0.0 ],
                        [ 0.0, 0.0, 0.0, 1.0 ] ] )   
         #reverse the translation of t1               
         t2 = np.matrix( [[1.0, 0, 0, -(self.vrp[0,0] + self.vpn[0,1] * self.extent[2] * 0.5)],
                        [0, 1, 0, -(self.vrp[0,1] + self.vpn[0,1] * self.extent[2] * 0.5)],
                        [0, 0, 1, -(self.vrp[0,2] + self.vpn[0,2] * self.extent[2] * 0.5)],
                        [0, 0, 0, 1] ] )   
                        
         some_matrix = np.matrix( [[self.vrp[0,0], self.vrp[0,1], self.vrp[0,2], 1.0],
                        [self.u[0,0], self.u[0,1], self.u[0,2], 0],
                        [self.vup[0,0], self.vup[0,1], self.vup[0,2], 0],
                        [self.vpn[0,0], self.vpn[0,1], self.vpn[0,2],0]] )                                                    
         tvrc = (t2*Rxyz.T*r2*r1*Rxyz*t1*some_matrix.T).T 
         
         
         
#          for i in range(3):
         self.vrp= tvrc[0,0:3]
         self.u= tvrc[1,0:3]
         self.vup= tvrc[2,0:3]
         self.vpn= tvrc[3,0:3]
            
         
         self.u = self.normalize(self.u) 
         self.vup = self.normalize(self.vup)
         self.vpn = self.normalize(self.vpn)    
            
            
                 
             
                
          
          
          
    """    normalizes the vector""" 
    def normalize(self, vector):

        length = math.sqrt( vector[0,0]* vector[0,0] + vector[0,1]* vector[0,1] + vector[0,2]* vector[0,2] )
        a = []
        for i in range(3):
            a.append(vector[0,i]/length)

        return np.matrix(a) 

    def updateScreen(self):
        self.screen = [self.view_size,self.view_size ]    
    
    """returns a clone of view object"""
    def clone(self):
       view = View(self.view_size)
       view.vrp = copy.copy(self.vrp)
       view.vpn = copy.copy(self.vpn)
       view.vup = copy.copy(self.vup)
       view.u = copy.copy(self.u)
       view.extent = copy.deepcopy(self.extent)
       view.screen = copy.deepcopy(self.screen)
       view.offset = copy.deepcopy(self.offset)
       
       return view
        
if __name__ == '__main__':
    view = View()
    print "*)"*52
    view2 = view.clone()
    
    

        





          



