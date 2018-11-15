def slimFly(n, e, sizes):
    #n - core name (e.g. BGQ-core)
    #    -comes from machine_config.py file
    #e - network type (e.g. 'BGQ-network')

    #Need to make these inputs or infered somehow
    Nr = 50
    #q = 5
    k = 108
    sizes = [2,5,5]
    q = sizes[1]
    block = [[[ Node() for i in range(q) ] for j in range(q)] for l in range(2)]
    block = sorted(flatten(assign(block)), key=lambda x: x.index)
    wrap = False

    w  = (int) (math.floor(q/4))
    d  = q%4
    #This is weird, 'cause it's a hardware setting, right?
    Kp = (int) (math.floor((3*q - d) / 2))
    p = (int) (k - Kp)
    N = (int) (Nr * p)

    #d = 1: Find the field
    Fq = range(q)

    #d = 1: Search for primitive elements (Xi)
    peFound = False
    pe = 2

    while( not peFound ):
        power = 1
        elmCnt = 0
        elmChk = [0] * q 

        for i in range(1,q):
            peTest = (int) (math.pow(pe,power) % q)
            if(elmChk[peTest] == 0):
                elmChk[peTest] = 1
                elmCnt = elmCnt + 1
                if(elmCnt == (q-1)):
                    peFound = True
                    break
                else:
                    power = power + 1
            else:
                pe = pe + 1
                break

    #d = 1: Contstruct X, Xp
    genX  = []
    genXp = []

    #for i in range(0,q-1):
    for i in range(1,q):
        elm = (int) ((math.pow(pe,i)) % q)
        if ( (i % 2) == 0):
            genX.append( elm )
        else:
            genXp.append( elm )

    genX.sort()
    genXp.sort()

    """Create a multi-dimensional block of routing indices and edges."""
    edges = []

    #Rule 1: A = 0
    for i in range(0, (Nr/2)):  #A = 0
        #Check for rule 1; A = 0 cross A = 0
        A    = (int) (i / ( math.pow(q,2) ) )
        rem1 = (int) (i % ( math.pow(q,2) ) )
        #Why switch X & Y?
        X    = (int) (rem1 / q)
        Y    = (int) (rem1 % q)

    #   for j in range(i, qSq, 5):  #A = 0, same column
        for j in range(0, (Nr/2)): #A = 0, same column
            Ap     = (int) (j / ( math.pow(q,2) ) )
            rem2   = (int) (j % ( math.pow(q,2) ) )
            #Why switch X & Y?
            Xp     = (int) (rem2 / q)
            Yp     = (int) (rem2 % q)

            tstVal = abs( ( Yp - Y) )

            if ((tstVal in genX) and (X == Xp)) :
                edgeTuple = ((block[i], block[j]))
                edges.append( edgeTuple )

    #Rule 2: A = 1
    for i in range((Nr/2), Nr):    #A = 0
        #Check for rule 1; A = 0 cross A = 0
        A    = (int) (i / ( math.pow(q,2) ) )
        rem1 = (int) (i % ( math.pow(q,2) ) )
        M    = (int) (rem1 / q)
        C    = (int) (rem1 % q)

        for j in range((Nr/2), Nr):    #A = 0, same column
            Ap     = (int) (j / ( math.pow(q,2) ) )
            rem2   = (int) (j % ( math.pow(q,2) ) )
            #Why switch X & Y?
            Mp     = (int) (rem2 / q)
            Cp     = (int) (rem2 % q)

            tstVal = abs( ( Cp - C) )

            if ((tstVal in genXp) and (M == Mp)) :
                edgeTuple = ((block[i], block[j]))
                edges.append( edgeTuple )

    #Rule 3: Between groups
    #Upper left section
    for i in range(0,(Nr/2)):  #A = 0
        A    = (int) (i / ( math.pow(q,2) ) )
        rem1 = (int) (i % ( math.pow(q,2) ) )
        #Why switch X & Y?
        X    = (int) (rem1 / q)
        Y    = (int) (rem1 % q)

        for j in range((Nr/2), Nr):    #A = 0
            Ap    = (int) (j / ( math.pow(q,2) ) )
            rem2 = (int) (j % ( math.pow(q,2) ) )
            M    = (int) (rem2 / q)
            C    = (int) (rem2 % q)

            testVal = M * X + C
            
            if (Y == testVal):
                edgeTuple = ((block[i], block[j]))
                edges.append( edgeTuple )

    for i in range((Nr/2), Nr):    #A = 0
        A    = (int) (i / ( math.pow(q,2) ) )
        rem2 = (int) (i % ( math.pow(q,2) ) )
        #Why switch X & Y?
        M    = (int) (rem2 / q)
        C    = (int) (rem2 % q)
        
        for j in range(0, (Nr/2)): #A = 0
            Ap    = (int) (j / ( math.pow(q,2) ) )
            rem1 = (int) (j % ( math.pow(q,2) ) )
            X    = (int) (rem1 / q)
            Y    = (int) (rem1 % q)

            testVal = ((M * X + C) % 5)
            
            if (Y == testVal):
                edgeTuple = ((block[i], block[j]))
                edges.append( edgeTuple )

    #edges = glue(block)

    # Sort everything by index (of the first item for edges).
    # Did the sorting for the block earlier
    edges = sorted(edges, key=lambda x: x[0].index)

    # Zip names and sizes to each thing and then return nodes + edges.
    #What does zip do?
    #N, S = repeat(TORUS if wrap else MESH), repeat(tuple(sizes))
    N, S = repeat(TORUS), repeat(tuple(sizes))

    temp = zip(repeat(n), N, S, block) + zip(repeat(e), N, S, edges)
    #n is core type (str)     i.e. BGQ-core
    #e is nw   type (str)    i.e. 'BGQ-network'

    return temp

    #return zip(repeat(n), N, S, block) + zip(repeat(e), N, S, edges)
