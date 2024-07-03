import tsp_file_parser as parser
import math

def read(filename):
    parser.TSPParser(filename)

    n = parser.TSPParser.dimension
    nClass = parser.TSPParser.nClass
    
    nodes = list(range(n))
    edges = {}
    for i in range(n):
        for j in range(n):
            edges[i,j] = parser.TSPParser.tsp_edges[i,j]
            
    classes = parser.TSPParser.classes
    precedences = parser.TSPParser.precedences

    return n, nClass, nodes, edges, classes, precedences




def validate(n, nClass, edges, classes, precedences, solution, cost, tolerance=1e-4):
    start = solution[0]
    previous = solution[0]
    actual_cost = 0
    visitedClasses = set([classes[solution[0]]])
   
    for i in solution[1:-1]:
        if i < 0 or i > n - 1:
            print("Customer {} does not exist".format(i))
            return False
        if classes[i] in visitedClasses:
            print("Customer {} is already visited".format(i))
            return False
        visitedClasses.add(classes[i])
        actual_cost += edges[previous, i]
        previous = i

    if solution[-1] != -1:
        print("The tour does not return to the start node")
        return False

    actual_cost += edges[previous, start]

    if len(visitedClasses) != nClass:
        print(
            "The number of visited classes is {}, but should be {}".format(
                len(visitedClasses), nClass
            )
        )
        return False

    if abs(actual_cost - cost) > tolerance:
        print(
            "The cost of the solution {} mismatches the actual cost {}".format(
                cost, actual_cost
            )
        )
        return False

    return True
