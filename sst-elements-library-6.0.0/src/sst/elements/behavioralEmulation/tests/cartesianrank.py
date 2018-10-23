"""
This Class object sets up a 3-D cartesian grid given the X, Y and Z dimensions.
No real grid is created but it provides methods to find neighbouring ranks and grid coordinates
"""
import math
#import pdb
#pdb.set_trace()
class CartesianGrid(object):

    def __init__(self, xdim, ydim, zdim):
        #pdb.set_trace()
        self.Xdim = xdim
        self.Ydim = ydim
        self.Zdim = zdim

    def neighbourRank(self, myrank, neighbour):
	#import pdb	
	#pdb.set_trace()
	#print("myrank =")
	#print(myrank)
	#print("neighbour")
	#print(neighbour)        
	x = self.myCoordinates(myrank, "x")
        y = self.myCoordinates(myrank, "y")
        z = self.myCoordinates(myrank, "z")       

        if neighbour == "Xplus": x = x+1
        elif neighbour == "Xminus": x = x-1
        elif neighbour == "Yplus": y = y+1
        elif neighbour == "Yminus": y = y-1
        elif neighbour == "Zplus": z = z+1
        elif neighbour == "Zminus": z = z-1
        else: raise Exception("Unknown neighbour "+neighbour)

        if x<0 or x>=self.Xdim or y<0 or y>=self.Ydim or z<0 or z>=self.Zdim:
            return -1;
        else:
	    #print("The target here (from python) is =")
	    x1 = 3
	    y1 = 2
	    z1 = 2
	    r1 = 3
	    i = x*self.Ydim*self.Zdim + y*self.Zdim + z+1 	    
	    start_value = 2+x1+y1+z1
	    cfl = (i-1)%(z1*r1)
	    br = math.floor((i-1)/(z1*r1))
	    bds = math.floor((i-1)/(y1*z1*r1))
	    new_target = start_value + cfl + (br*((z1*r1)+z1))+(bds*y1)
	    print x," ",y," ",z," ",(x*self.Ydim*self.Zdim + y*self.Zdim + z), new_target,start_value,cfl,br,bds
	    #return (new_target)
	    return ((x*self.Ydim*self.Zdim + y*self.Zdim + z))

    def myCoordinates(self, myrank, axis):
	#print("my rank =")
	#print(myrank)
	#print("axis")
	#print(axis)
        if axis == "x" or axis == "X": return myrank/(self.Ydim*self.Zdim)
        elif axis == "y" or axis == "Y": return (myrank%(self.Ydim*self.Zdim))/self.Zdim
        elif axis == "z" or axis == "Z": return myrank%self.Zdim
        else: raise Exception("Unknown axis "+axis)

        return -1

