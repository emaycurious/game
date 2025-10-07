# 3 x 3 game
import random as r
import time


# create
def create(w):
    a = []
    for i in range( w ):
        b = []
        for j in range( w ):
            b.append( 0 )
        a.append( b )

    return a


# random one
def one(a, m, n):
    # + choose one
    while 1:
        i = r.randint( -2, 2 )
        j = r.randint( -2, 2 )
        if 0 < m + i < len( a ) and 0 < n + j < len( a ) and a[m + i][n + j] == 0:
            a[m + i][n + j] = 2
            return


# find
def find(a, m, n, c):
    # ---
    for i in range( len( a ) ):
        you, me = 0, 0
        for j in range( len( a[i] ) ):
            if a[i][j] == 1:
                you += 1
            if a[i][j] == 2:
                me += 1

        if not c:
            if you == 2 or me == 2:
                for j in range( len( a[i] ) ):
                    if a[i][j] == 0:
                        a[i][j] = 2
                        return
        else:
            if me == 3:
                return 'Win'
            if you == 3:
                return 'Fail'

    # |
    for i in range( len( a ) ):
        you, me = 0, 0
        for j in range( len( a[i] ) ):
            if a[j][i] == 1:
                you += 1
            if a[j][i] == 2:
                me += 1

        if not c:
            if you == 2 or me == 2:
                for j in range( len( a[i] ) ):
                    if a[j][i] == 0:
                        a[j][i] = 2
                        return
        else:
            if me == 3:
                return 'Win'
            if you == 3:
                return 'Fail'

    # X (/,\)
    you, me = 0, 0
    for i in range( len( a ) ):
        if a[i][len( a ) - i - 1] == 1:
            you += 1
        if a[i][len( a ) - i - 1] == 2:
            me += 1

    if not c:
        if you == 2 or me == 2:
            for i in range( len( a ) ):
                if a[i][len( a ) - i - 1] == 0:
                    a[i][len( a ) - i - 1] = 2
                    return
    else:
        if me == 3:
            return 'Win'
        if you == 3:
            return 'Fail'

    you, me = 0, 0
    for i in range( len( a ) ):
        if a[i][i] == 1:
            you += 1
        if a[i][i] == 2:
            me += 1

    if not c:
        if you == 2 or me == 2:
            for i in range( len( a ) ):
                if a[i][i] == 0:
                    a[i][i] = 2
                    return

    else:
        if me == 3:
            return 'Win'
        if you == 3:
            return 'Fail'

    # ---,|,X all no, then random one
    if not c:
        one( a, m, n )


# all is block
def all(a):
    for i in range( len( a ) ):
        for j in range( len( a[i] ) ):
            if a[i][j] == 0:
                return 0
    return 1


if __name__ == '__main__':

    # create
    a = create( 3 )

    # out
    for i in range( len( a ) ):
        print( a[i] )
    print()

    while 1:

        # you first
        mnList = input().split( ' ' )
        m = int( mnList[0] )
        n = int( mnList[1] )
        a[m][n] = 1

        # out
        for i in range( len( a ) ):
            print( a[i] )
        print()

        # check
        f = find( a, m, n, 1 )  # 1 - check
        if f == 'Win':
            print( 'you fail!' )
            break
        if f == 'Fail':
            print( 'you win!' )
            break

        # if all is block -- ping !
        if all( a ):
            print( 'ping!' )
            break

        # then me
        time.sleep( 3 )
        find( a, m, n, 0 )  # 0 - not check, only 2?
        # out
        for i in range( len( a ) ):
            print( a[i] )
        print()

        # check
        f = find( a, m, n, 1 )  # 1 - check
        if f == 'Win':
            print( 'you fail!' )
            break
        if f == 'Fail':
            print( 'you win!' )
            break

        # if all is block -- ping !
        if all( a ):
            print( 'ping!' )
            break
