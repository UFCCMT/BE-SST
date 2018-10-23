from cartesianrank import CartesianGrid

global cartesianData

#import pdb
#pdb.set_trace()
cartesianData = CartesianGrid(4,3,3)

Component( "BGQ-core" )
Program( "BGQ-core", "cmt-bone-be.txt" )

Property( "BGQ-core", "app.elementSize", lambda gid, cid, cids, index: 11 )
Property( "BGQ-core", "app.elementsPerProcess", lambda gid, cid, cids, index: 64 )
Property( "BGQ-core", "app.transferSizeX", lambda gid, cid, cids, index: 77440 )
Property( "BGQ-core", "app.transferSizeY", lambda gid, cid, cids, index: 77440 )
Property( "BGQ-core", "app.transferSizeZ", lambda gid, cid, cids, index: 77440 )
Property( "BGQ-core", "app.timesteps", lambda gid, cid, cids, index: 1 )
Property( "BGQ-core", "app.phyParam", lambda gid, cid, cids, index: 5 )

Property( "BGQ-core", "mpi.commRank", lambda gid, cid, cids, index: cid  )
Property( "BGQ-core", "mpi.commSize", lambda gid, cid, cids, index: cids )

def cartX(g, rank, c, i): return cartesianData.myCoordinates(rank, "X")
def cartY(g, rank, c, i): return cartesianData.myCoordinates(rank, "Y")
def cartZ(g, rank, c, i): return cartesianData.myCoordinates(rank, "Z")
def cartXp(g, rank, c, i): return cartesianData.neighbourRank(rank, "Xplus")
def cartHasXp(g, rank, c, i): return cartesianData.neighbourRank(rank, "Xplus") >= 0
def cartYp(g, rank, c, i): return cartesianData.neighbourRank(rank, "Yplus")
def cartHasYp(g, rank, c, i): return cartesianData.neighbourRank(rank, "Yplus") >= 0
def cartZp(g, rank, c, i): return cartesianData.neighbourRank(rank, "Zplus")
def cartHasZp(g, rank, c, i): return cartesianData.neighbourRank(rank, "Zplus") >= 0
def cartXm(g, rank, c, i): return cartesianData.neighbourRank(rank, "Xminus")
def cartHasXm(g, rank, c, i): return cartesianData.neighbourRank(rank, "Xminus") >= 0
def cartYm(g, rank, c, i): return cartesianData.neighbourRank(rank, "Yminus")
def cartHasYm(g, rank, c, i): return cartesianData.neighbourRank(rank, "Yminus") >= 0
def cartZm(g, rank, c, i): return cartesianData.neighbourRank(rank, "Zminus")
def cartHasZm(g, rank, c, i): return cartesianData.neighbourRank(rank, "Zminus") >= 0

Property( "BGQ-core", "mpi.cartesianX", cartX )
Property( "BGQ-core", "mpi.cartesianY", cartY )
Property( "BGQ-core", "mpi.cartesianZ", cartZ )
Property( "BGQ-core", "mpi.cartesianXplus", cartXp )
Property( "BGQ-core", "mpi.cartesianHasXplus", cartHasXp )
Property( "BGQ-core", "mpi.cartesianYplus", cartYp )
Property( "BGQ-core", "mpi.cartesianHasYplus", cartHasYp )
Property( "BGQ-core", "mpi.cartesianZplus", cartZp )
Property( "BGQ-core", "mpi.cartesianHasZplus", cartHasZp )
Property( "BGQ-core", "mpi.cartesianXminus", cartXm )
Property( "BGQ-core", "mpi.cartesianHasXminus", cartHasXm )
Property( "BGQ-core", "mpi.cartesianYminus", cartYm )
Property( "BGQ-core", "mpi.cartesianHasYminus", cartHasYm )
Property( "BGQ-core", "mpi.cartesianZminus", cartZm )
Property( "BGQ-core", "mpi.cartesianHasZminus", cartHasZm )

Ordinal( "BGQ-core", "mpi.commRank" )

Relation( "BGQ-core", "BGQ-core", "cpu", "self" )

Attribute( "BGQ-core", "usage", 4.0 )
 
Operation( "BGQ-core", "wait", NoLookup, None,
           RecvWait(True))
Operation( "BGQ-core", "unwait", NoLookup, None,
           Recv(True))
Operation( "BGQ-core", "computeConv", "vulcan-compute-conv.csv", "polynomial-3",
           Dawdle( AnyOutput() ))
Operation( "BGQ-core", "computedr", "vulcan-compute-dr.csv", "polynomial-4",
           Dawdle( AnyOutput() ))
Operation( "BGQ-core", "computeds", "vulcan-compute-ds.csv", "polynomial-4",
           Dawdle( AnyOutput() ))
Operation( "BGQ-core", "computedt", "vulcan-compute-dt.csv", "polynomial-4",
           Dawdle( AnyOutput() ))
Operation( "BGQ-core", "computeSum", "vulcan-compute-sum.csv", "polynomial-3",
           Dawdle( AnyOutput() ))
Operation( "BGQ-core", "computerk", "vulcan-compute-rk.csv", "polynomial-3",
           Dawdle( AnyOutput()+0.00000004 ))
Operation( "BGQ-core", "comminit", "vulcan-compute-comminit.csv", "linear",
           Dawdle( AnyOutput() ))
Operation( "BGQ-core", "comminitaxis", "vulcan-compute-comminitaxis.csv", "linear",
           Dawdle( AnyOutput() ))
Operation( "BGQ-core", "prepareFaces", "vulcan-compute-prepface.csv", "linear",
           Dawdle( AnyOutput() ))
Operation( "BGQ-core", "cleanFaces", "vulcan-compute-cleanface.csv", "linear",
           Dawdle( AnyOutput() ))

Mailbox( "BGQ-core", "unwait", lambda source, target, size, tag: [source],
         OnTarget )

Component( "BGQ-network-3" )
Attribute( "BGQ-network-3", "usage", 0.0 )

Operation( "BGQ-network-3", "transfer", "vulcan-transfer.csv", "linear",
           Dawdle( AnyOutput() ) )

Mailbox( "BGQ-network-3", "transfer", lambda source, target, size, tag: [size],
         OnAll )

Component( "BGQ-network" )
Attribute( "BGQ-network", "usage", 0.0 )

Operation( "BGQ-network", "transfer", "vulcan-transfer.csv", "linear",
           Dawdle( AnyOutput() ) )

Mailbox( "BGQ-network", "transfer", lambda source, target, size, tag: [size],
         OnAll )

Component( "BGQ-network-2" )
Attribute( "BGQ-network-2", "usage", 0.0 )

Operation( "BGQ-network-2", "transfer", "vulcan-transfer.csv", "linear",
           Dawdle( AnyOutput() ) )

Mailbox( "BGQ-network-2", "transfer", lambda source, target, size, tag: [size],
         OnAll )

Component( "BGQ-network-1" )
Attribute( "BGQ-network-1", "usage", 0.0 )

Operation( "BGQ-network-1", "transfer", "vulcan-transfer.csv", "linear",
           Dawdle( AnyOutput() ) )

Mailbox( "BGQ-network-1", "transfer", lambda source, target, size, tag: [size],
         OnAll )

Component( "BGQ-network-Root" )
Attribute( "BGQ-network-Root", "usage", 0.0 )

Operation( "BGQ-network-Root", "transfer", "vulcan-transfer.csv", "linear",
           Dawdle( AnyOutput() ) )

Mailbox( "BGQ-network-Root", "transfer", lambda source, target, size, tag: [size],
         OnAll )

Component("Node")
Offspring( "Node", Mesh( "BGQ-core", "BGQ-network", [ 2, 2, 2, 2, 2 ] ) )

Component( "system" )
Component("BGQ-connection-3")
Component("BGQ-connection-2")
Component("BGQ-connection-1")
Component("BGQ-connection-Root")
Component("Node")

#Offspring( "system", Mesh( "Node", "BGQ-network", [ 2, 2, 2, 2, 2 ] ) )
#Offspring( "system", Torus( "BGQ-core", "BGQ-network", [2,2,2] ) )
#print("ddf")
Offspring( "system", Tree( ["BGQ-connection-Root", "BGQ-connection-3", "BGQ-connection-2", "BGQ-connection-1", "BGQ-core"], ["BGQ-network-Root","BGQ-network-3", "BGQ-network-2", "BGQ-network-1"], [3,2,2,3] ) )
#Offspring( "system", Torus( "Node", "BGQ-network", [1, 1, 2] ) )
Root("system")
