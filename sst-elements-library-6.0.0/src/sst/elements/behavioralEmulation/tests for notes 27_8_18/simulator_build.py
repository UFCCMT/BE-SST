#! /usr/bin/env python

"""
  Top-level simulator build file. This module is used by the SST configuration file to
  construct the system layout structure based on the user configuration files and provide 
  a hierarchical set of information that can be parsed to define individual BE components.

  Authors: Dylan Rudolph and Ajay Ramaswamy, BE team, CCMT UFL 
"""

from pdb import set_trace
import time
import json
import sys
from math import copysign, ceil
from collections import namedtuple, defaultdict
from multiprocessing import Pool, Value, Array
from itertools import repeat

import math
import numpy as np

# Avoiding unwieldy import; but everything from common is in UPPERCASE.
from common import *


# Avoiding unwieldy import; but everything from common is in UPPERCASE.

from compiler import Compiler, Instruction
from copy import copy, deepcopy

import operator
import random

sys.path.append("/home/tjohnson/work/research/networking/besta_basis")

import generate_mms

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
    print (ns)
    print (es)
    print (sizes)
    """Create a tree structure of routing indices and edges."""
    def recurse(nodes, edges, parent, remaining):
        
        # Get the types and size for this level.
        n, e, size = remaining.pop(0)

        # Construct the leaf node types and indices.
        leaves = [ (n, TREE, sizes, Node(parent.index + (i,)))
                   for i in range(size) ]
        nodes.extend(leaves)

        # Make a connection between each leaf node and the parent.
        edges.extend([(e, TREE, sizes, (parent, i)) for _, _, _, i in leaves])

        # If there's still work to be done, drop to the next level.
        if remaining:
            for leaf in leaves:
                recurse(nodes, edges, leaf[-1], copy(remaining))

    sizes = tuple(sizes)

    # Construct the root node.
    nodes, edges = [(ns.pop(0), TREE, sizes, Node((0,)) )], []

    # Build the tree.
    recurse(nodes, edges, nodes[0][-1], zip(ns, es, sizes))

    return nodes + edges

def glue(things, wrap=False):
    """Glue together (link across one dimension) a list of objects."""
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

def sfGlue(sfBlock, sfEdges,q):

    edges = []

    for i in sfEdges:
        src = generate_mms.dim2Global(i[0],q)
        dst = generate_mms.dim2Global(i[1],q)
        edges.append( (sfBlock[src],sfBlock[dst] ))

    return edges

def assign(things, indices=()):
    """Assign routing indices to each element in a block."""

    for i, thing in enumerate(things):

        # Calculate the current index.
        current = indices + ( i, )

        # If we aren't at the bottom, recurse with the current index.
        if isinstance(thing, list): assign( thing, current )
        else:                       thing.index = current

    return things

def block(n, e, sizes, wrap):
    """Create a multi-dimensional block of routing indices and edges."""
    
    # Build the first dimension.
    block = [ Node() for _ in range(sizes[-1]) ]
    edges = glue(block, wrap=wrap)

    #This 

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
    #Here, block is still a multi-dim list of empty, unassigned nodes
    block = sorted(flatten(assign(block)), key=lambda x: x.index)
    edges = sorted(edges, key=lambda x: x[0].index)
    #Blocks and edges are somehow tied together. As soon as the blocks are assigned,
#all the edges, which were also just none, are assigned as well.

    #At this point, block is a list of nodes; not sure what the assign methods do, but thats it

    # Zip names and sizes to each thing and then return nodes + edges.
    #Create's iterators to continually return the object. Need to find out why it's used.
    N, S = repeat(TORUS if wrap else MESH), repeat(tuple(sizes))


    temp = zip(repeat(n), N, S, block) + zip(repeat(e), N, S, edges)
    #Temp is a giant array of
        #('BGQ-core', 'torus', (4, 4, 4, 8, 2), (0, 0, 0, 0, 0))
        #('core', 'network', 'coreIndex', 'coreIndex')
    return temp
    #return zip(repeat(n), N, S, block) + zip(repeat(e), N, S, edges)

def slimFly(n, e, q):
    #Earlier, I had 

    sf = [[[ Node() for i in range(q) ] for j in range(q)] for l in range(2)]
    sf = sorted(flatten(assign(sf)), key=lambda x: x.index)

    shape = (2,q,q)

    #The block seems to work well. Now we need to do the edges
        #This will be a bit tricky. It might rely on either better
    #undersanding how MMS graphs work, but a basic assumption is
    #For each node:
        #1 edge for every element in X or Xp
        #1 edge for every column in 1/2 of the bipartite graph
    #In otherwords, at least for q=5
        #num_edges/node = (q-1)/2 + q
        #                = (5-1)/2 + 5 = 7
        #Total nodes = 7 * 50 = 350
            #Note: These are unidirectional
        #Confirmed for q=7 -> 980 edges

    #If edges is just a list of tuples, let's fix that. All we need is to get the edge list
        #from the other program.

    #Edges can't just be tuples. Has to join together 2 nodes
    edges = generate_mms.genSF(5,1)
    edges = sorted(edges, key=lambda x: x[0])

    f, g, h = np.shape(edges)
    #nodeEdges = np.zeros((e,f))
    nodeEdges = [[0 for i in range(g)] for j in range(f)]

    for x in range(f):
        for y in range(g):
            for z in range(len(sf)):
                if sf[z].index == edges[x][y]:
                    nodeEdges[x][y] = copy(sf[z])

    #Similar to cube return
    N, S = repeat(SLIMFLY), repeat(shape)
    temp = zip(repeat(n), N, S, sf) + zip(repeat(e), N, S, nodeEdges)
    return temp


def pTOp(na, e, nb):
    """Create a single dimension connection of different routing indices and edges."""

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

        self.simulator = simulator

        self.ordinals = {}
        self.mailboxes = {}
        self.components = {}
        self.relations = defaultdict(list)
        self.properties = defaultdict(dict)

        self.system = None

    # ----------------------- User-Accessable Functions --------------------- #

        self.torus = lambda n, e, s:                block(n, e, s, True)
        self.mesh = lambda n, e, s:                 block(n, e, s, False)
        self.connect = lambda na, e, nb:            pTOp(na, e, nb) 
        self.tree = lambda ns, es, s:               tree(ns, es, s)
        self.cube = lambda n, e, d:                 cube(n, e, d)
        self.one = lambda n:                        [(n, None, [], Node())]
        #Why are these lambda functions? you're just calling other functions
        self.slimfly = lambda n, e, q:              slimFly(n, e, q)

        #What is returned (from experimenting in torus/slimfly fxns)

            #ergo, Total lenght is numNodes + numEdges
            #[Core Type][Network Type][Block Shape][Node Object -OR- SRC/DST Node Object Tuple]
                #temp[:][3] will be a node object when temp[x][:] x < numNodes;
                #Otherwise, it'll be a node tuple to show source and dest

    def root(self, kind):
        """Define the root component of a system."""
        self.system = kind

    def componentN(self, name, family, kind):
        """Define a component from an existing template."""
        if kind == "none":
            self.components[name] = []
        else:
            sys.argv.append(name)
            self.simulator.new(family+"/"+kind+".py")

    def component(self, kind):
        """Define a new component template from a name."""
        self.components[kind] = []

    def subcomponent(self, parent, children):
        """Give one of the templates a group of children."""
        self.components[parent].extend(children)

    def mailbox(self, kind, operation, operands, targets):
        """Give a component a mailbox."""
        self.simulator.mailboxes[kind].append( (operation, operands, targets) ) #Multiple operations per kind?

    def program(self, kind, filename):
        """Give a component template a program."""
        self.simulator.programs[kind] = filename

    def ordinal(self, kind, name):
        """Give a component template a routing index (a named property)."""
        self.ordinals[kind] = name

    def property(self, kind, name, value):
        """Give a component template a property."""
        self.properties[kind][name] = value

    def relation(self, kind, other, name, relation):
        """Give a component template a relationship to another."""
        self.relations[kind].append( (other, name, relation) )

    def attribute(self, kind, name, initial):
        """Give a component template an attribute with initial value."""
        self.simulator.attributes[kind].append( (name, initial) )

    def operation(self, kind, name, filename, interpolation, *templates):
        """Give a component template an operation."""      
        if not (isinstance(kind, basestring) and isinstance(name, basestring) and (isinstance(filename, basestring) or filename is None) and (isinstance(interpolation, basestring) or interpolation is None)): 
            raise ValueError("Operation configuration format is wrong for "+str(name)+"!")
 
        self.simulator.operations[kind][name] = (filename, interpolation, templates)
        self.simulator.operationDetails[kind][name] = (filename, interpolation, [])

        for template in templates:
            self.simulator.operationDetails[kind][name][2].append(template.representation)

    def build(self):
        """Construct the layout from provided parameters."""
        return Layout( self.system, self.components, self.properties,
                       self.ordinals, self.relations )


class Layout(object):

    def __init__(self, root, components, properties, ordinals, relations):
        """The Layout contains the structure of a system."""

        # Things which many or all components have:
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
        # Keep track of how many of each thing we have.
        self.tallies = defaultdict(lambda: 0)

        self.tallies[root] = 1

        # Start the structure with the root node.
        self.new( 0, root, None, [], set() )

        # Helper function: just return the current Global Identifier.
        GID = lambda : len(self.cids) - 1

        def recurse(current):

            # Keep a mapping of index-to-GID so we don't need to search later.
            indices = {}

            # Take note of the parent GID (of each thing in current).
            PGID = GID()

            #Current seems to be a combo list of nodes and edges
            for kind, netname, netsize, part in current:

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

                    # Build the entry for this edge component.
                    self.new( self.tallies[kind], kind, PGID, [], set(),
                              netname=netname, netsize=netsize )

                    # Recall the GIDs of the referenced nodes.
                    #Part array should be nodes. For SF, they're tuples.
                    AGID, BGID = indices[part[0].index], indices[part[1].index]
                    #print "Nodes " + str(AGID) + ", " + str(BGID)

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
        """A ChangeTemplatev stores the information to make a Change Event."""
        self.attribute = attribute
        if(isinstance(value, Procrastinator)): self.value = value.value
        else: self.value = value
        self.provision = provision
        self.representation = "change " + str(self.attribute) + " " + str(self.value) + " " + str(self.provision)

class TimeoutTemplate(object):

    def __init__(self, value, provision=True):
        """A TimeoutTemplate stores the information to make a Timeout Event."""
    
        if(isinstance(value, Procrastinator)): 
            self.value = value.value
            self.provision = provision
            self.representation = "timeout " + str(self.value) + " " + str(self.provision)
        else: 
            self.value = value
            self.provision = provision
            self.representation = "timeout " + "Equation" +"::" + str(self.value) + " " + str(self.provision)
            

'''class EquationTemplate(object):
    
    def __init__(self, input_equation):
        print ("checking")
        print (self.input_equation)
        self.representation = "timeout " + str(self.input_equation)'''
    
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
        SlimFly = self.designer.slimfly

        Modify     = ChangeTemplate
        Dawdle     = TimeoutTemplate
        Loiter     = ConditionTemplate
        RecvWait   = RecvWaitTemplate
        Recv       = RecvTemplate
        #Equation   = EquationTemplate

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



