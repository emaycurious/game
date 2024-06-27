# 汉诺塔
# A B C
# 要求：把 A 的塔块 -> C 上，每次只能放一块，小的要在大的上面
# 思路：
# 先要把最大的（最底下的）放到 C，那先得把它上面所有的一堆移开到 B，
# 等放完了最大这块，再把小的那堆从 B 移动到 C
# 分成 3 步：1.小堆 A->B  2.最大块 A->C  3.小堆 B->C

step = 0  # 移动了多少步

def move(begin, mid, end, len):
    global step

    if len == 1:
        step += 1       # 次数 -> 2^n - 1 -> O(2^n)    这里加一个步数，就可以拿到递归了多少次
        print( step,':', begin, '->', end )
        return
    move( begin, end, mid, len - 1 )
    move( begin, mid, end, 1 )
    move( mid, begin, end, len - 1 )


if __name__ == '__main__':
    n = int( input( '输入汉诺塔层数：' ) )
    if n:
        move( 'A', 'B', 'C', n )
