from cartesianrank import CartesianGrid

global cartesianData

#import pdb
#pdb.set_trace()
cartesianData = CartesianGrid(8,16,16)

Component( "BGQ-core" )
#Program( "BGQ-core", "particles_solver_trint_compute_only.txt" )
#Program( "BGQ-core", "particles_solver_bdf_compute_only.txt" )
Program( "BGQ-core", "particles_solver_redint_compute_only.txt" )

Property( "BGQ-core", "app.alpha", lambda gid, cid, cids, index: 1 )
Property( "BGQ-core", "app.elementSize", lambda gid, cid, cids, index: 15 )
Property( "BGQ-core", "app.elementsPerProcess", lambda gid, cid, cids, index: 8 )
Property( "BGQ-core", "app.transferSizeX", lambda gid, cid, cids, index: 51840 )
Property( "BGQ-core", "app.transferSizeY", lambda gid, cid, cids, index: 51840 )
Property( "BGQ-core", "app.transferSizeZ", lambda gid, cid, cids, index: 51840 )
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

Attribute( "BGQ-core", "usage", 0.0 )
 
Operation( "BGQ-core", "wait", NoLookup, None,
           RecvWait(True))
Operation( "BGQ-core", "unwait", NoLookup, None,
           Recv(True))

e1 = "tri_interp_props_part_location.txt"

Operation( "BGQ-core", "tri_interp_props_part_location", "tri_interp_props_part_location.txt", "Equation",
           Dawdle(e1))

Operation( "BGQ-core", "Compute1", "Compute1.txt", "Equation",
           Dawdle(e1))

Operation( "BGQ-core", "update_particles_position", "update_particles_position.txt", "Equation",
           Dawdle(e1))

Operation( "BGQ-core", "red_interp_props_part_location", "red_interp_props_part_location.txt", "Equation",
           Dawdle(e1))

Operation( "BGQ-core", "upd_vel_and_pos_rk3_stage3", "upd_vel_and_pos_rk3_stage3.txt", "Equation",
           Dawdle(e1))

Operation( "BGQ-core", "upd_vel_and_pos_rk3_stage1", "upd_vel_and_pos_rk3_stage1.txt", "Equation",
           Dawdle(e1))

Operation( "BGQ-core", "upd_vel_and_pos_rk3_allstages","upd_vel_and_pos_rk3_allstages.txt", "Equation",
           Dawdle(e1))

Operation( "BGQ-core", "interp_props_part_location", "interp_props_part_location.txt", "Equation",
           Dawdle(e1))

Operation( "BGQ-core", "usr_particles_forces","usr_particles_forces.txt", "Equation",
           Dawdle(e1))

Operation( "BGQ-core", "upd_vel_and_pos_bdf", "upd_vel_and_pos_bdf.txt", "Equation",
           Dawdle(e1))

Operation( "BGQ-core", "update_particles_location", "update_particles_location.txt", "Equation",
           Dawdle(e1))

Mailbox( "BGQ-core", "unwait", lambda source, target, size, tag: [source],
         OnTarget )

Component( "BGQ-network" )
Attribute( "BGQ-network", "usage", 0.0 )

Operation( "BGQ-network", "transfer", "vulcan-transfer.csv", "linear",
           Dawdle( AnyOutput() ) )

Mailbox( "BGQ-network", "transfer", lambda source, target, size, tag: [size],
         OnAll )

#Component("Node")
#Offspring( "Node", Mesh( "BGQ-core", "BGQ-network", [ 2, 2, 2, 2, 2 ] ) )

Component( "system" )
#Offspring( "system", Mesh( "Node", "BGQ-network", [ 2, 2, 2, 2, 2 ] ) )
Offspring( "system", Torus( "BGQ-core", "BGQ-network", [4, 4, 4, 8, 2] ) )
#Offspring( "system", Tree( ["BGQ-connection-3", "BGQ-connection-2", "BGQ-connection-1", "BGQ-core"], ["BGQ-network-3", "BGQ-network-2", "BGQ-network-1"], [2, 2, 2] ) )
Root("system")
