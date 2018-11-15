
#import pdb
#pdb.set_trace()

Component( "BGQ-core" )
Program( "BGQ-core", "particles_solver_rk3_compute_only.txt" )

Property( "BGQ-core", "app.alpha", lambda gid, cid, cids, index: 1 )
Property( "BGQ-core", "app.elementSize", lambda gid, cid, cids, index: 9 )
Property( "BGQ-core", "app.elementsPerProcess", lambda gid, cid, cids, index: 64 )
Property( "BGQ-core", "mpi.commRank", lambda gid, cid, cids, index: cid  )
Property( "BGQ-core", "mpi.commSize", lambda gid, cid, cids, index: cids )

Ordinal( "BGQ-core", "mpi.commRank" )

Relation( "BGQ-core", "BGQ-core", "cpu", "self" )

Attribute( "BGQ-core", "usage", 0.0 )
 
Operation( "BGQ-core", "wait", NoLookup, None,
           RecvWait(True))
Operation( "BGQ-core", "unwait", NoLookup, None,
           Recv(True))


e1 = ("(1.2625e-08*a*a*a*b*c)-1.6784e-06")
e2 = ("(9.7756e-08*a*a*a*b*c)-4.7868e-06")
e3 = ("(2.3644e-08*a*a*a*b*b*c)+7.6e-03")
e4 = ("(8.5295e-08*a*a*a*a*a*a*b*c)-9.54e-02")
e5 = ("(5.8345e-07*a*a*a*b*c)-1.2e-03")
e6 = ("(2.7823e-07*a*a*a*b*c)-3.2994e-03")
e7 = ("(8.4128e-08*a*a*a*b*c)+2.3505e-05")
e8 = ("(4.2796e-07*a*a*a*b*c)-8.8314e-05")

Operation( "BGQ-core", "Compute1", e1, "Equation",
           Dawdle(e1))
Operation( "BGQ-core", "update_particles_location", e2, "Equation",
           Dawdle(e2))
Operation( "BGQ-core", "update_particles_position", e3, "Equation",
           Dawdle(e3))
Operation( "BGQ-core", "interp_props_part_location", e4, "Equation",
           Dawdle(e4))
Operation( "BGQ-core", "upd_vel_and_pos_rk3_stage1", e5, "Equation",
           Dawdle(e5))
Operation( "BGQ-core", "upd_vel_and_pos_rk3_allstages", e6, "Equation",
           Dawdle(e6))
Operation( "BGQ-core", "upd_vel_and_pos_rk3_stage3", e7, "Equation",
           Dawdle(e7))
Operation( "BGQ-core", "usr_particles_forces", e8, "Equation",
           Dawdle(e8))


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
Offspring( "system", Torus( "BGQ-core", "BGQ-network", [2, 2, 2, 2, 2] ) )
#Offspring( "system", Tree( ["BGQ-connection-3", "BGQ-connection-2", "BGQ-connection-1", "BGQ-core"], ["BGQ-network-3", "BGQ-network-2", "BGQ-network-1"], [8, 8, 8] ) )
Root("system")
