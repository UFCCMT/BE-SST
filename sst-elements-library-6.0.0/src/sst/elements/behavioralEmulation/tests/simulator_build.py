#! /usr/bin/env python

"""
  Top-level simulator build file. This module is used by the SST configuration file to
  construct the system layout structure based on the user configuration files and provide 
  a hierarchical set of information that can be parsed to define individual BE components.

  Authors: Dylan Rudolph and Ajay Ramaswamy, BE team, CCMT UFL 
"""

import time
import json
import sys
from math import copysign, ceil
from collections import namedtuple, defaultdict
from multiprocessing import Pool, Value, Array
from itertools import repeat

# Avoiding unwieldy import; but everything from common is in UPPERCASE.
from common import *


# Avoiding unwieldy import; but everything from common is in UPPERCASE.

from compiler import Compiler, Instruction
from copy import copy, deepcopy

import operator
import random
import pdb

# --------------------------------------------------------------------------- #
# ------------------------ Setup and Type Definitions ----------------------- #
# --------------------------------------------------------------------------- #

# Convert nested lists to a flat list:
flatten = lambda x: ( flatten( [a for b in x for a in b] )
                      if isinstance(x[0], list) else x )

class Node(object):

    def __init__(self, index=None):
        """A Node is a nearly-empty temporary storage type."""
        self.index = index

    def __repr__(self):
        """Create a string representation of the node."""
        return str(self.index)


# --------------------------------------------------------------------------- #
# -------------------- Construction Utility Definitions --------------------- #
# --------------------------------------------------------------------------- #

def tree(ns, es, sizes):
    """Create a tree structure of routing indices and edges."""
    import pdb
    #pdb.set_trace()
    dim_count = 0
    def recurse(nodes, edges, parent, remaining):
	#pdb.set_trace()
        # Get the types and size for this level.
        n, e, size = remaining.pop(0)
	
        # Construct the leaf node types and indices.
        leaves = [ (n, TREE, sizes, Node(parent.index + (i,)))
                   for i in range(size) ]
        nodes.extend(leaves)
        
        current_dimension = str(leaves[0][-1])
        dim_count = current_dimension.count(',') + 1
        # Make a connection between each leaf node and the parent.
        
	'''if(dim_count == 3):
	  half_count = int(ceil(sizes[0]/2.0))
	  if(parent.index[-1] < half_count):
	    for i in range(sizes[0]):
	      index_fat_tree = Node(((0,)+(i,)+(0,)))
	      #index_fat_tree = tuple(index_fat_tree)
	      edges.extend([(e, TREE, sizes, (parent,index_fat_tree))])
	  else:
	    for i in range(sizes[0]):
	      index_fat_tree = Node(((0,)+(i,)+(1,)))
	      #index_fat_tree = tuple(index_fat_tree)
	      edges.extend([(e, TREE, sizes, (parent,index_fat_tree))])
        elif(dim_count == 4):
	  if (parent.index[2]==0):
	    for i in range(2):
	      index_fat_tree = Node(((parent.index[0],)+(parent.index[1],)+(i,)+(0,)))
	      #index_fat_tree = tuple(index_fat_tree)
	      edges.extend([(e, TREE, sizes, (parent,index_fat_tree))])
	  elif (parent.index[2]==1):
	    for i in range(1,-1,-1):
	      index_fat_tree = Node(((parent.index[0],)+(parent.index[1],)+(i,)+(0,)))
	      #index_fat_tree = tuple(index_fat_tree)
	      edges.extend([(e, TREE, sizes, (parent,index_fat_tree))])''' #This is for folded claus fat tree
	if(dim_count == 3):
	    for i in range(sizes[0]):
		for j in range(sizes[1]):
		    index_fat_tree = Node(((parent.index[0],)+(i,)+(j,)))
		    edges.extend([(e, TREE, sizes, (parent,index_fat_tree))]) 
	elif(dim_count == 4):
		if(parent.index[-1]%2==0):
		    for i in range(2):
			    for j in range(sizes[-2]):
				if(i==0):
				    index_fat_tree = Node(((parent.index[0],)+(parent.index[1],)+(parent.index[2],)+(j,)))
				    edges.extend([(e, TREE, sizes, (parent,index_fat_tree))]) 
				elif(i==1):
				    if(parent.index[-1]%2==0):
					k = parent.index[-1]+1
				    else:
					k = parent.index[-1]-1
				    index_fat_tree = Node(((parent.index[0],)+(parent.index[1],)+(k,)+(j,)))
				    edges.extend([(e, TREE, sizes, (parent,index_fat_tree))]) 
		else:
		  for i in range(2):
			    for j in range((sizes[-2]-1),-1,-1):
				if(i==0):
				    index_fat_tree = Node(((parent.index[0],)+(parent.index[1],)+(parent.index[2],)+(j,)))
				    edges.extend([(e, TREE, sizes, (parent,index_fat_tree))]) 
				elif(i==1):
				    if(parent.index[-1]%2==0):
					k = parent.index[-1]+1
				    else:
					k = parent.index[-1]-1
				    index_fat_tree = Node(((parent.index[0],)+(parent.index[1],)+(k,)+(j,)))
				    edges.extend([(e, TREE, sizes, (parent,index_fat_tree))])
		# If there's still work to be done, drop to the next level.
        else:
	  edges.extend([(e, TREE, sizes, (parent, i)) for _, _, _, i in leaves])
        if remaining:
            for leaf in leaves:
                recurse(nodes, edges, leaf[-1],copy(remaining))

    sizes = tuple(sizes)

    # Construct the root node.
    nodes, edges = [(ns.pop(0), TREE, sizes, Node((0,)) )], []
   
    # Build the tree.
    recurse(nodes, edges, nodes[0][-1], zip(ns, es, sizes))

    #print ("nodes + edges")
    #print (nodes+edges)
    return nodes + edges

def glue(things, wrap=False):
    """Glue together (link across one dimension) a list of objects."""
    #pdb.set_trace()
    edges = []

    for thing in things[ (0 if wrap else 1): ]:

        # Get the left-adjacent thing.
        other = things[ things.index(thing) - 1 ]

        # If we aren't at the lowest level yet, recurse with the pair.
        if isinstance(thing, list):
            for pair in zip(thing, other):
                edges.extend( glue(pair) )

        # If we are at the lowest level, connect this pair.
        else: edges.append( (thing, other) )

    return edges

def assign(things, indices=()):
    """Assign routing indices to each element in a block."""
    #import pdb;
    #pdb.set_trace()
    
    for i, thing in enumerate(things):

	
        # Calculate the current index.
        current = indices + ( i, )

        # If we aren't at the bottom, recurse with the current index.
        if isinstance(thing, list): assign( thing, current )
        else:                       thing.index = current

    return things

def block(n, e, sizes, wrap):
    """Create a multi-dimensional block of routing indices and edges."""
    #pdb.set_trace()
    # Build the first dimension.
    block = [ Node() for _ in range(sizes[-1]) ]
    edges = glue(block, wrap=wrap)

    # Progressively build the other dimensions by duplication.
    for size in reversed(sizes[:-1]):

        # Duplicate the previous dimension.
        copies = [deepcopy( (block, edges) ) for _ in range(size)]

        # Unpack the duplication.
        block = [item[0] for item in copies]
        edges = flatten( [item[1] for item in copies] )

        # Add the new connections. (Check if correct!)
        if size > 1: edges.extend( glue(block, wrap=wrap) )
        else: edges.extend( glue(block, wrap=False) )

    # Sort everything by index (of the first item for edges).
    block = sorted(flatten(assign(block)), key=lambda x: x.index)
    edges = sorted(edges, key=lambda x: x[0].index)

    # Zip names and sizes to each thing and then return nodes + edges.
    N, S = repeat(TORUS if wrap else MESH), repeat(tuple(sizes))

    return zip(repeat(n), N, S, block) + zip(repeat(e), N, S, edges)

def pTOp(na, e, nb):
    """Create a single dimension connection of different routing indices and edges."""
    #pdb.set_trace()
    # Build the first dimension.
    block = [ Node(), Node() ]
    edges = glue(block, wrap=False)
    kinds = [na, nb]

    # Sort everything by index (of the first item for edges).
    block = sorted(flatten(assign(block)), key=lambda x: x.index)
    edges = sorted(edges, key=lambda x: x[0].index)

    # Zip names and sizes to each thing and then return nodes + edges.
    N, S = repeat(MESH), repeat(tuple([2]))

    return zip(kinds, N, S, block) + zip(repeat(e), N, S, edges)

def cube(n, e, degree):
    """Create a hypercube of routing indices and edges."""
    #pdb.set_trace()
    # Start with a zero-dimensional hypercube.
    cube, edges = Node(), []

    # Progressively double and glue new dimensions.
    for _ in range(degree):

        # Create a duplicate of the previous dimension.
        new = [deepcopy((cube, edges)), deepcopy((cube, edges))]

        # Unpack the duplicate.*
        cube, edges = [new[0][0], new[1][0]], new[0][1] + new[1][1]

        # Add the new connections.
        edges.extend( glue(cube) )

    # Sort everything by index (of the first item for edges).
    cube = sorted(flatten(assign(cube)), key=lambda x: x.index)
    edges = sorted(edges, key=lambda x: x[0].index)

    # Zip names and sizes to each thing and then return nodes + edges.
    N, S = repeat(CUBE), repeat(degree)

    return zip(repeat(n), N, S, cube) + zip(repeat(e), N, S, edges)


# --------------------------------------------------------------------------- #
# --------------------------- Primary Definitions --------------------------- #
# --------------------------------------------------------------------------- #

class Designer(object):

    def __init__(self, simulator):
        """The Designer is most of the the configuration-file interface."""
	#import pdb
	#pdb.set_trace()
        self.simulator = simulator

        self.ordinals = {}
        self.mailboxes = {}
        self.components = {}
        self.relations = defaultdict(list)
        self.properties = defaultdict(dict)

        self.system = None

    # ----------------------- User-Accessable Functions --------------------- #

        self.torus = lambda n, e, s:     block(n, e, s, True)
        self.mesh = lambda n, e, s:      block(n, e, s, False)
        self.connect = lambda na, e, nb: pTOp(na, e, nb) 
        self.tree = lambda ns, es, s:    tree(ns, es, s)
        self.cube = lambda n, e, d:      cube(n, e, d)
        self.one = lambda n:             [(n, None, [], Node())]

    def root(self, kind):
        """Define the root component of a system."""
        #pdb.set_trace()
        self.system = kind

    def componentN(self, name, family, kind):
        """Define a component from an existing template."""
        #pdb.set_trace()
        if kind == "none":
            self.components[name] = []
        else:
            sys.argv.append(name)
            self.simulator.new(family+"/"+kind+".py")

    def component(self, kind):
        """Define a new component template from a name."""
        #pdb.set_trace()
        self.components[kind] = []

    def subcomponent(self, parent, children):
        """Give one of the templates a group of children."""
        #pdb.set_trace()
        self.components[parent].extend(children)

    def mailbox(self, kind, operation, operands, targets):
        """Give a component a mailbox."""
        #pdb.set_trace()
        self.simulator.mailboxes[kind].append( (operation, operands, targets) ) #Multiple operations per kind?

    def program(self, kind, filename):
        """Give a component template a program."""
        #pdb.set_trace()
        self.simulator.programs[kind] = filename

    def ordinal(self, kind, name):
        """Give a component template a routing index (a named property)."""
        #pdb.set_trace()
        self.ordinals[kind] = name

    def property(self, kind, name, value):
        """Give a component template a property."""
        #pdb.set_trace()
        self.properties[kind][name] = value

    def relation(self, kind, other, name, relation):
        """Give a component template a relationship to another."""
        #pdb.set_trace()
        self.relations[kind].append( (other, name, relation) )

    def attribute(self, kind, name, initial):
        """Give a component template an attribute with initial value."""
        #pdb.set_trace()
        self.simulator.attributes[kind].append( (name, initial) )

    def operation(self, kind, name, filename, interpolation, *templates):
        """Give a component template an operation."""      
        #pdb.set_trace()
        if not (isinstance(kind, basestring) and isinstance(name, basestring) and (isinstance(filename, basestring) or filename is None) and (isinstance(interpolation, basestring) or interpolation is None)): 
            raise ValueError("Operation configuration format is wrong for "+str(name)+"!")
 
        self.simulator.operations[kind][name] = (filename, interpolation, templates)
        self.simulator.operationDetails[kind][name] = (filename, interpolation, [])

        for template in templates:
            self.simulator.operationDetails[kind][name][2].append(template.representation)

    def build(self):
        #pdb.set_trace()
        """Construct the layout from provided parameters."""
        return Layout( self.system, self.components, self.properties,
                       self.ordinals, self.relations )


class Layout(object):

    def __init__(self, root, components, properties, ordinals, relations):
        """The Layout contains the structure of a system."""

        # Things which many or all components have:
        #pdb.set_trace()
        self.cids = []
        self.kinds = []
        self.edges = []
        self.parents = []
        self.children = []

        # Things which only some components have:
        self.indices = {}                     # { gid: (index, ...), ... }
        self.netnames = {}                    # { gid: network, ... }
        self.netsizes = {}                    # { gid: [size, ...], ... }
        self.ordinals = defaultdict(lambda: None)     # { ordinal: gid, ... }
        self.rordinals = defaultdict(lambda: None)    # { gid: ordinal, ... }
        self.subordinals = defaultdict(list)  # { gid: [ordinal, ...], ... }
        self.relations = defaultdict(dict)    # { gid: {"name": gid ...}, ... }

        self.gids = lambda : range(len(self.cids))

        # Relationship utility functions: return all GIDs which are ___ of GID.

        # (Parent's Parent's Children)
        self.aunts = lambda gid: self.children[self.parents[self.parents[gid]]]

        # (Parent's Children)
        self.siblings = lambda gid: self.children[self.parents[gid]]

        # Construct the layout from the provided parameters.
        self.build(root, components, properties, ordinals, relations)
      
        i=0
        for edge in self.edges:
            if edge == []: self.edges[i] = [[]]
            i = i+1

    def new(self, cid, kind, parent, edges, children,
            index=None, netname=None, netsize=None):
        """Add a new component to the structure."""
	#import pdb	
	#pdb.set_trace()
        # The current GID is the length of any of the manditory parameters.
        gid = len(self.cids)

        # Add the new entry to the manditory parameters.
        self.cids.append(cid)
        self.kinds.append(kind)
        self.edges.append(edges)
        self.parents.append(parent)
        self.children.append(children)

        # Optionally add the new entry to the other parameters.
        if index: self.indices[gid] = index
        if netname: self.netnames[gid] = netname
        if netsize: self.netsizes[gid] = netsize

    def build(self, root, components, properties, ordinals, relations):
        """Construct the layout from assorted parameters."""
	print("Inside build")
        # Keep track of how many of each thing we have.
        #import pdb
        #pdb.set_trace()
        #pdb.set_trace
        self.tallies = defaultdict(lambda: 0)

        self.tallies[root] = 1

        # Start the structure with the root node.
        self.new( 0, root, None, [], set() )

        # Helper function: just return the current Global Identifier.
        GID = lambda : len(self.cids) - 1

        def recurse(current):
	    #import pdb
	    #pdb.set_trace()
            # Keep a mapping of index-to-GID so we don't need to search later.
            indices = {}

            # Take note of the parent GID (of each thing in current).
            PGID = GID()

            for kind, netname, netsize, part in current:
		#import pdb
		#pdb.set_trace()
                if isinstance(part, Node): # If this part is a Node proper:

                    # Make the entry for this component (sans some properties).
                    self.new( self.tallies[kind], kind, PGID, [], set(),
                              index=part.index, netname=netname,
                              netsize=netsize )

                    # Add this entry to its parents children.
                    self.children[PGID].add( GID() )
	
                    # Update the mapping.
                    if part.index: indices[part.index] = GID()

                    # If this node should be assigned an ordinal:
                    if kind in ordinals:

                        # Grab the property that determines the ordinal.
                        prop = properties[kind][ordinals[kind]]

                        # Evaluate the property, with incorrect CID totals.
                        ordinal = prop( GID(), self.tallies[kind],
                                        self.tallies[kind], part.index )
                        self.ordinals[ordinal] = GID()
                        self.rordinals[GID()] = ordinal

                        ancestor = PGID

                        # Add this ordinal to every parent, recusively.
                        while ancestor != None:
                            self.subordinals[ancestor].append( ordinal )
                            ancestor = self.parents[ancestor]

                else: # Else it is an edge:
		    #import pdb
		    #pdb.set_trace()
                    # Build the entry for this edge component.
                    self.new( self.tallies[kind], kind, PGID, [], set(),
                              netname=netname, netsize=netsize )

                    # Recall the GIDs of the referenced nodes.
                    
                    AGID, BGID = indices[part[0].index], indices[part[1].index]

                    # Add this entry to its parents children.
                    self.children[PGID].add( GID() )

                    # Insert the (other, edge) references back into the nodes.
                    self.edges[AGID].append( (BGID, GID()) )
                    self.edges[BGID].append( (AGID, GID()) )

                # Update the build count for this type of component.
                self.tallies[kind] += 1

                # Drop down a level to the children of this type of component:
                recurse( components[kind] )

        # Build the structure.
        recurse( components[root] )

        # Now build the relationships:

        # For every entry in the structure:
        for gid in self.gids():
	    #pdb.set_trace()
            # For each relation in this type of entry:
            for other, name, relation in relations[self.kinds[gid]]:

                # Construct the search space for the relationship (GID list).
                if relation == SELF:       search = [ gid ]
                elif relation == CHILD:    search = self.children[gid]
                elif relation == PARENT:   search = [ self.parents[gid] ]
                elif relation == SIBLING:  search = self.siblings(gid)
                elif relation == AUNT:     search = self.aunts(gid)

                # Look through the search space for the right kind of thing.
                for s in search:

                    # Once a kind-matched item is found, add it.
                    if self.kinds[s] == other:
                        self.relations[gid][name] = s
                        break

                # If we didn't find any of the right kind of thing, error out.
                else: raise ValueError(
                    ERR_RELATIONSHIP.format(other, relation, self.kinds[gid]))



# --------------------------------------------------------------------------- #
# --------------------------- Primary Definitions --------------------------- #
# --------------------------------------------------------------------------- #
class Procrastinator(object):


    def __init__(self, initial=None):
        if not hasattr(self, "type"): self.type = "Default"
        self.value = self.type+"("+str(initial)+")"

    def __add__(self, right):
        new = deepcopy(self)
        if(isinstance(right, Procrastinator)): new.value = new.value+"::"+"+"+"::"+right.value
        else: new.value+"::"+"+"+"::"+str(right)
        return new

    def __radd__(self, left):
        new = deepcopy(self)
        if(isinstance(left, Procrastinator)): new.value = new.value+"::"+"+"+"::"+left.value
        else: new.value = new.value+"::"+"+"+"::"+str(left)
        return new

    def __sub__(self, right):
        new = deepcopy(self)
        if(isinstance(right, Procrastinator)): new.value = new.value+"::"+"-"+"::"+right.value
        else: new.value = new.value+"::"+"-"+"::"+str(right)
        return new

    def __rsub__(self, left):
        new = deepcopy(self)
        if(isinstance(left, Procrastinator)): new.value = new.value+"::"+"-"+"::"+left.value
        else: new.value = new.value+"::"+"-"+"::"+str(left)
        return new

    def __mul__(self, right):
        new = deepcopy(self)
        if(isinstance(right, Procrastinator)): new.value = new.value+"::"+"*"+"::"+right.value
        else: new.value = new.value+"::"+"*"+"::"+str(right)
        return new

    def __rmul__(self, left):
        new = deepcopy(self)
        if(isinstance(left, Procrastinator)): new.value = new.value+"::"+"*"+"::"+left.value
        else: new.value = new.value+"::"+"*"+"::"+str(left)
        return new

    def __div__(self, right):
        new = deepcopy(self)
        if(isinstance(right, Procrastinator)): new.value = new.value+"::"+"/"+"::"+right.value
        else: new.value = new.value+"::"+"/"+"::"+str(right)
        return new

    def __rdiv__(self, left):
        new = deepcopy(self)
        if(isinstance(left, Procrastinator)): new.value = new.value+"::"+"/"+"::"+left.value
        else: new.value = new.value+"::"+"/"+"::"+str(left)
        return new

    def __pow__(self, right):
        new = deepcopy(self)
        if(isinstance(right, Procrastinator)): new.value = new.value+"::"+"^"+"::"+right.value
        else: new.value = new.value+"::"+"^"+"::"+str(right)
        return new

    def __eq__(self, right):
        new = deepcopy(self)
        if(isinstance(right, Procrastinator)): new.value = new.value+"::"+"=="+"::"+right.value
        else: new.value = new.value+"::"+"=="+"::"+str(right)
        return new

    def __ne__(self, right):
        new = deepcopy(self)
        if(isinstance(right, Procrastinator)): new.value = new.value+"::"+"!="+"::"+right.value
        else: new.value = new.value+"::"+"!="+"::"+str(right)
        return new

    def __lt__(self, right):
        new = deepcopy(self)
        if(isinstance(right, Procrastinator)): new.value = new.value+"::"+"<"+"::"+right.value
        else: new.value = new.value+"::"+"<"+"::"+str(right)
        return new

    def __le__(self, right):
        new = deepcopy(self)
        if(isinstance(right, Procrastinator)): new.value = new.value+"::"+"<="+"::"+right.value
        else: new.value = new.value+"::"+"<="+"::"+str(right)
        return new

    def __gt__(self, right):
        new = deepcopy(self)
        if(isinstance(right, Procrastinator)): new.value = new.value+"::"+">"+"::"+right.value
        else: new.value = new.value+"::"+">"+"::"+str(right)
        return new

    def __ge__(self, right):
        new = deepcopy(self)
        if(isinstance(right, Procrastinator)): new.value = new.value+"::"+">="+"::"+right.value
        else: new.value = new.value+"::"+">="+"::"+str(right)
        return new


# Procrastinators describe things to be determined at runtime.

# An AttributeProcrastinator gets a named attribute of a component (later).
AttributeProcrastinator = type( "Procrastinator", (Procrastinator,), {
    "type": "Attribute" } )

# An InputProcrastinator gets one of the lookup input arguments (later).
InputProcrastinator = type( "Procrastinator", (Procrastinator,), {
    "type": "Input" } )

# An OutputProcrastinator gets one of the lookup output arguments (later).
OutputProcrastinator = type( "Procrastinator", (Procrastinator,), {
    "type": "Output" } )

# A RandomProcrastinator chooses one of the outputs at random (later).
RandomProcrastinator = type( "Procrastinator", (Procrastinator,), {
    "type": "Random" } )


# Event templates store event-creation information, excluding the component.

class ChangeTemplate(object):

    def __init__(self, attribute, value, provision=True):
        """A ChangeTemplate stores the information to make a Change Event."""
        self.attribute = attribute
        if(isinstance(value, Procrastinator)): self.value = value.value
        else: self.value = value
        self.provision = provision
        self.representation = "change " + str(self.attribute) + " " + str(self.value) + " " + str(self.provision)

class TimeoutTemplate(object):

    def __init__(self, value, provision=True):
        """A TimeoutTemplate stores the information to make a Timeout Event."""
        if(isinstance(value, Procrastinator)): self.value = value.value
        else: self.value = value
        self.provision = provision
        self.representation = "timeout " + str(self.value) + " " + str(self.provision)

class ConditionTemplate(object):

    def __init__(self, attribute, compare, value, provision=True):
        """A ConditionTemplate stores information to make a Condition Event."""
        self.attribute, self.compare = attribute, compare
        if(isinstance(value, Procrastinator)): self.value = value.value
        else: self.value = value
        self.provision = provision
        self.representation = "condition " + str(self.attribute) + " " + str(compare) + " " + str(self.value) + " " + str(self.provision)

class RecvWaitTemplate(object):
    
    def __init__(self, provision=True):
        self.provision = provision
        self.representation = "receivewait " + str(self.provision)

class RecvTemplate(object):
    
    def __init__(self, provision=True):
        self.provision = provision
        self.representation = "receive " + str(self.provision)



# --------------------------------------------------------------------------- #
# --------------------------- Primary Definitions --------------------------- #
# --------------------------------------------------------------------------- #

class Simulator(object):

    def __init__( self, filename ):
        """The Simulator is the simulation manager."""

	#pdb.set_trace()
        self.filename = filename

        # Initialize the setup parameters.
        self.gids = []
        self.programs = {}
        self.indicators = {}
        self.mailboxes = defaultdict(list)
        self.attributes = defaultdict(list)
        self.operations = defaultdict(dict)
        self.operationDetails = defaultdict(dict)

        # Initialize the assistants
        self.designer = Designer(self)
        self.compiler = Compiler()

        # The component setup 'properties' are shared between the two.
        self.properties = self.designer.properties

        self.new(self.filename)


    # -------------------- Public Control-Flow Functions -------------------- #

    def build(self):
        """Create the structure of the simulation."""
	#pdb.set_trace()
        self.layout = self.designer.build()

        self.gids = self.layout.gids()

        """
        # Writing Layout details into an output file
        children = []
        for item in self.layout.children:
            children.append(list(item))
        with open('layoutfile', 'w') as fout:
            json.dump(self.layout.cids, fout)
            fout.write('\n')
            json.dump(self.layout.kinds, fout)
            fout.write('\n')
            json.dump(self.layout.edges, fout)
            fout.write('\n')
            json.dump(self.layout.parents, fout)
            fout.write('\n')
            json.dump(children, fout)
            fout.write('\n')
            json.dump(self.layout.indices, fout)
            fout.write('\n')
            json.dump(self.layout.netnames, fout)
            fout.write('\n')
            json.dump(self.layout.netsizes, fout)
            fout.write('\n')
            json.dump(self.layout.relations, fout)
            fout.write('\n')
            json.dump(self.layout.ordinals, fout)
            fout.write('\n')
            json.dump(self.layout.rordinals, fout)
            fout.write('\n')
            json.dump(self.layout.subordinals, fout)

        fout.close()
        """

        """
	for kind in self.designer.components:

            # Set up any software associated with this part.
            if kind in self.programs:

                # Get the associated program.
                prog = self.compiler.load( self.programDirectory +
                                           self.programs[kind] )

                with open(self.programs[kind]+".txt", 'w') as fout:
                    for instruction in prog:
                        prog_line = str(instruction)
                        prog_line = prog_line.replace(", ", ",")
                        fout.write(prog_line)
                        fout.write('\n')
             
                fout.close()
        """ 

    def new(self, filename):
        """configuration file"""
	#pdb.set_trace()
        Root = self.designer.root
        Mailbox = self.designer.mailbox
        Program = self.designer.program
        Ordinal = self.designer.ordinal
        Property = self.designer.property
        Relation = self.designer.relation
        Component = self.designer.component
        ComponentLoad = self.designer.componentN
        Offspring = self.designer.subcomponent
        Attribute = self.designer.attribute
        Operation = self.designer.operation

        Cube = self.designer.cube
        Tree = self.designer.tree
        Mesh = self.designer.mesh
        Torus = self.designer.torus
        Connect = self.designer.connect
        Single = self.designer.one

        Modify     = ChangeTemplate
        Dawdle     = TimeoutTemplate
        Loiter     = ConditionTemplate
        RecvWait   = RecvWaitTemplate
        Recv       = RecvTemplate

        Inputs = InputProcrastinator
        Outputs = OutputProcrastinator
        AnyOutput = RandomProcrastinator
        Values = AttributeProcrastinator

        NoLookup = None
        OnEndpoints = (True, False, True)
        OnMiddle    = (False, True, False)
        OnAll       = (True, True, True)
        OnSource    = (True, False, False)
        OnNonSource = (False, True, True)
        OnTarget    = (False, False, True)
        OnNonTarget = (True, True, False)

        # ---------------------- Run the Configuration File --------------------- #

        execfile(filename)


