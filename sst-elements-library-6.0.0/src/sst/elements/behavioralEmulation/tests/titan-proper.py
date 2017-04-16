from cartesianrank import CartesianGrid

global cartesianData

cartesianData = CartesianGrid(8, 4, 4)

Component( "Titan-core" )
Program( "Titan-core", "cmt-bone-be.txt" )

Property( "Titan-core", "app.elementSize", lambda gid, cid, cids, index: 9 )
Property( "Titan-core", "app.elementsPerProcess", lambda gid, cid, cids, index: 64 )
Property( "Titan-core", "app.transferSizeX", lambda gid, cid, cids, index: 51840 )
Property( "Titan-core", "app.transferSizeY", lambda gid, cid, cids, index: 51840 )
Property( "Titan-core", "app.transferSizeZ", lambda gid, cid, cids, index: 51840 )
Property( "Titan-core", "app.timesteps", lambda gid, cid, cids, index: 1 )
Property( "Titan-core", "app.phyParam", lambda gid, cid, cids, index: 5 )

Property( "Titan-core", "mpi.commRank", lambda gid, cid, cids, index: cid  )
Property( "Titan-core", "mpi.commSize", lambda gid, cid, cids, index: cids )
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
Property( "Titan-core", "mpi.cartesianX", cartX )
Property( "Titan-core", "mpi.cartesianY", cartY )
Property( "Titan-core", "mpi.cartesianZ", cartZ )
Property( "Titan-core", "mpi.cartesianXplus", cartXp )
Property( "Titan-core", "mpi.cartesianHasXplus", cartHasXp )
Property( "Titan-core", "mpi.cartesianYplus", cartYp )
Property( "Titan-core", "mpi.cartesianHasYplus", cartHasYp )
Property( "Titan-core", "mpi.cartesianZplus", cartZp )
Property( "Titan-core", "mpi.cartesianHasZplus", cartHasZp )
Property( "Titan-core", "mpi.cartesianXminus", cartXm )
Property( "Titan-core", "mpi.cartesianHasXminus", cartHasXm )
Property( "Titan-core", "mpi.cartesianYminus", cartYm )
Property( "Titan-core", "mpi.cartesianHasYminus", cartHasYm )
Property( "Titan-core", "mpi.cartesianZminus", cartZm )
Property( "Titan-core", "mpi.cartesianHasZminus", cartHasZm )
Ordinal( "Titan-core", "mpi.commRank" )
Relation( "Titan-core", "Titan-core", "cpu", "self" )
Attribute( "Titan-core", "usage", 0.0 )
 
Operation( "Titan-core", "wait", NoLookup, None,
           RecvWait(True))
Operation( "Titan-core", "unwait", NoLookup, None,
           Recv(True))
Operation( "Titan-core", "computeConv", "titan-compute-conv.csv", "polynomial-3",
           Dawdle( AnyOutput() ))
Operation( "Titan-core", "computedr", "titan-compute-dr.csv", "polynomial-4",
           Dawdle( AnyOutput() ))
Operation( "Titan-core", "computeds", "titan-compute-ds.csv", "polynomial-4",
           Dawdle( AnyOutput() ))
Operation( "Titan-core", "computedt", "titan-compute-dt.csv", "polynomial-4",
           Dawdle( AnyOutput() ))
Operation( "Titan-core", "computeSum", "titan-compute-sum.csv", "polynomial-3",
           Dawdle( AnyOutput() ))
Operation( "Titan-core", "computerk", "titan-compute-rk.csv", "polynomial-3",
           Dawdle( AnyOutput() ))
Operation( "Titan-core", "comminit", "titan-compute-comminit.csv", "linear",
           Dawdle( AnyOutput() ))
Operation( "Titan-core", "comminitaxis", "titan-compute-comminitaxis.csv", "linear",
           Dawdle( AnyOutput() ))
Operation( "Titan-core", "prepareFaces", "titan-compute-prepface.csv", "linear",
           Dawdle( AnyOutput() ))
Operation( "Titan-core", "cleanFaces", "titan-compute-cleanface.csv", "linear",
           Dawdle( AnyOutput() ))
Mailbox( "Titan-core", "unwait", lambda source, target, size, tag: [source],
         OnTarget )
Component( "Titan-network-core" )
Attribute( "Titan-network-core", "usage", 0.0 )
Operation( "Titan-network-core", "transfer", "titan-transfer-intra-bw.csv", "linear",
             Dawdle( AnyOutput() ) )
Mailbox( "Titan-network-core", "transfer", lambda source, target, size, tag: [size],
           OnAll )
Component( "Titan-network-node" )
Attribute( "Titan-network-node", "usage", 0.0 )
Operation( "Titan-network-node", "transfer", "titan-transfer-inter-bw.csv", "linear",
             Dawdle( AnyOutput() ) )
Mailbox( "Titan-network-node", "transfer", lambda source, target, size, tag: [size],
           OnAll )
Component( "node" )
Offspring( "node", Mesh( "Titan-core", "Titan-network-core", [ 4, 2, 2 ] ) )
Component( "system" )
Offspring( "system", Mesh( "node", "Titan-network-node", [ 2, 2, 2 ] ) )
Root("system")
