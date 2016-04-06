# Problem
# =======

# Given a maze as input in the following format determine if Tom and meet Jerry.
# First line is size of maze (n, m) where:
# (1, 1) ... (1, m)
# (2, 1) ... (2, m)
# (n, 1) ... (n, m)

# Second line is Jerry's position in the maze
# Remaining lines are the maze.  0 Means you can move there, 1 means it's blocked

# Example Input
# -------------
# 3 3
# 2 2
# 0 0 0
# 0 0 1
# 1 1 1

# Example Output
# --------------
# 2

# Example Input
# -------------
# 3 3
# 3 3
# 0 1 0
# 1 0 1
# 0 0 0

# Example Output
# --------------
# -1

# Example Input
# -------------
# 3 3
# 3 2
# 0 0 0
# 1 1 0
# 1 0 0

# Example Output
# --------------
# 5


class Node():
    def __init__(self, data, x, y):
        self.data = data
        self.pos = (x, y)
        self.children = []
        self.visited = False

    def toString(self):
        return "{} {}".format(self.pos, self.data)

from collections import deque

def solve_maze(input):
    n, m = [int(x) for x in input[0].split(' ')]
    jerryX, jerryY = [int(x)-1 for x in input[1].split(' ')]
    jerryPos = (jerryX, jerryY)

    # read the maze in
    maze = []
    for row in range(0, n):
        currentRow = []
        col = [int(c) for c in input[row+2].split(' ')]
        for y, c in enumerate(col):
            currentRow.append(Node(c, row, y))

        maze.append(currentRow)
    
    # create the graph
    for x in range(n):
        for y in range(m):
            node = maze[x][y]

            # check all the directions
            if x+1 < m:
                checkNode = maze[x+1][y]
                if checkNode.data == 0:
                    node.children.append(checkNode)
            if x-1 > 0:
                checkNode = maze[x-1][y]
                if checkNode.data == 0:
                    node.children.append(checkNode)
            if y+1 < n:
                checkNode = maze[x][y+1]
                if checkNode.data == 0:
                    node.children.append(checkNode)
            if y-1 > 0:
                checkNode = maze[x][y-1]
                if checkNode.data == 0:
                    node.children.append(checkNode)

    def bfs(node):
        queue = deque()
        queue.append(node)

        path = []
        while len(queue) > 0:
            currentNode = queue.popleft()
            if not currentNode.visited:
                currentNode.visited = True
                path.append(currentNode)

                if currentNode.pos == jerryPos:
                    return len(path)

                for child in node.children:
                    if not child.visited:
                        queue.append(child)

        return -1

    return bfs(maze[0][0])

import unittest
class HackerRank2Tests(unittest.TestCase):
    def test_AmazonHR2Example1(self):
        input = ['3 3', '2 2', '0 0 0', '0 0 1', '1 1 1']
        self.assertEqual(2, solve_maze(input))

    def test_AmazonHR2Example2(self):
        input = ['3 3', '2 2', '0 1 0', '1 0 1', '0 0 0']
        self.assertEqual(-1, solve_maze(input))

    def test_AmazonHR2Example3(self):
        input = ['3 3', '3 2', '0 0 0', '1 1 0', '1 0 0']
        self.assertEqual(5, solve_maze(input))


#if __name__ == '__main__':
input = ['3 3', '2 2', '0 0 0', '0 0 1', '1 1 1']
solve_maze(input)


