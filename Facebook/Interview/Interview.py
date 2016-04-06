# Given a directed graph, copy the graph.
       
# 1 --> 2 <-|
# |     | - |
# |     |
# \/   \/
# 4<----3

class Node():
    def __init__(self, data):
        self.data = data
        self.copyNode = None
        self.visited = False
        self.children = []

def copy(node):
    if node.copyNode is not None:
        return

    node.copyNode = Node(node.data)

    for child in node.children:
        copy(child)
        node.copyNode.children.append(child.copyNode)

def traverse(node):
    if node.visited:
        return

    print(node.data)
    node.visited = True

    for child in node.children:
        traverse(child)


if __name__=='__main__':
    node1 = Node(1)
    node2 = Node(2)
    node3 = Node(3)
    node4 = Node(4)

    node1.children = [node2, node4]
    node2.children = [node2, node3]
    node3.children = [node4]

    copy(node1)
    traverse(node1.copyNode)