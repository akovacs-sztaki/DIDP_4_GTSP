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
            if i != j:
                x1 = parser.TSPParser.tsp_cities_dict[i][0]
                y1 = parser.TSPParser.tsp_cities_dict[i][1]
                x2 = parser.TSPParser.tsp_cities_dict[j][0]
                y2 = parser.TSPParser.tsp_cities_dict[j][1]
                edges[i, j] = round(math.sqrt(pow(x1-x2, 2) + pow(y1-y2, 2)))
   
    classes = parser.TSPParser.classes

    return n, nClass, nodes, edges, classes




def validate(n, nClass, edges, classes, solution, cost, tolerance=1e-4):
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
