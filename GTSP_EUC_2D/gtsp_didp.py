#!/usr/bin/env python3

import argparse
import copy
import time
import csv
import os

import didppy as dp
import read_gtsp

start = time.perf_counter()


def create_model(n, nClass, nodes, edges, classes):
#    model = dp.Model(float_cost=True)
    model = dp.Model()

    #customer[n] encodes the dummy "unknown" location (start node is unknown)
    customer = model.add_object_type(number=n+1)
    
    unvisitedClasses = model.add_set_var(object_type=customer, target=[i for i in range(0, nClass)])
    returnToLocation = model.add_element_var(object_type=customer, target=n)
    location = model.add_element_var(object_type=customer, target=n)

    distance_matrix = [
        [edges[i, j] if (i, j) in edges else 0 for j in nodes] for i in nodes
    ]
#    distance = model.add_float_table(distance_matrix)
    distance = model.add_int_table(distance_matrix)
    
    con = [classes[i] for i in nodes]
    class_of_node = model.add_int_table(con)

    model.add_base_case([location == n, unvisitedClasses.is_empty()])

#    state_cost = dp.FloatExpr.state_cost()
    state_cost = dp.IntExpr.state_cost()
    name_to_customer = {}

   
    # Transition: initial visit ----------------------------------
    for i in range(0, n):
        if (classes[i]==0):
            name = "initVisit {}".format(i)
            name_to_customer[name] = i
            init_visit = dp.Transition(
                name=name,
                cost=state_cost+0,
                effects=[
                    (unvisitedClasses, unvisitedClasses.remove(classes[i])),
                    (location, i),
                    (returnToLocation, i),
                ],
                preconditions=[returnToLocation==n],
            )
            model.add_transition(init_visit)


    # Transition: visit next node ----------------------------------
    for i in range(0, n):
        name = "visit {}".format(i)
        name_to_customer[name] = i
        visit = dp.Transition(
            name=name,
            cost=distance[location, i] + state_cost,
            effects=[
                (unvisitedClasses, unvisitedClasses.remove(classes[i])),
                (location, i),
            ],
            preconditions=[unvisitedClasses.contains(classes[i]), returnToLocation<n],
        )
        model.add_transition(visit)


    # Transition: return to start node ----------------------------------
    name = "return"
    name_to_customer[name] = -1
    return_to_depot = dp.Transition(
        name=name,
        cost=distance[location, returnToLocation] + state_cost,
        effects=[(location, n),
            (returnToLocation,n)],
        preconditions=[unvisitedClasses.is_empty(), returnToLocation<n],
    )
    model.add_transition(return_to_depot)

   
    # Distance to class k from any other class
    dtc = [min(min  (distance_matrix[i][j] for i in nodes if (classes[i] != k)) for j in nodes if classes[j]==k) for k in range(0,nClass)]
    min_distance_to_class = model.add_int_table(dtc)
    
    # Distance to node i from any node in another class
    dtn = [min(distance_matrix[i][j] for i in nodes if (classes[i] != classes[j])) for j in nodes]
    min_distance_to_node = model.add_int_table(dtn)

    # Bound: distance to unvistited classes + distance back to start node
    model.add_dual_bound(min_distance_to_class[unvisitedClasses] + (returnToLocation != n).if_then_else(min_distance_to_node[returnToLocation], 0))



    # Distance from node i to any node in another class
    dfn = [min(distance_matrix[j][i] for i in nodes if (classes[i] != classes[j])) for j in nodes]
    min_distance_from_node = model.add_int_table(dfn)
    
    # Distance from class k to any other class
    dfc = [min(dfn[j] for j in nodes if classes[j]==k) for k in range(nClass)]
    min_distance_from_class = model.add_int_table(dfc)

    # Bound: distance from unvistited classes + distance from current location
    model.add_dual_bound(min_distance_from_class[unvisitedClasses] + (location != n).if_then_else(min_distance_from_node[location], 0))



#    # Half distance in-out node i
#    hdn = [round(min(distance_matrix[i][j] for i in nodes if (classes[i] != classes[j]))/2 + min(distance_matrix[j][i] for i in nodes if (classes[i] != classes[j]))/2) for j in nodes]
#    half_distance_node = model.add_int_table(hdn)
#
#    # Half distance in-out class k
#    hdc = [min(hdn[j] for j in nodes if classes[j]==k) for k in range(nClass)]
#    half_distance_class = model.add_int_table(hdc)
#
#    # Bound: half distance in-out unvistited classes + half distance out current location + half distance to retornToLocation
#    model.add_dual_bound(half_distance_class[unvisitedClasses] + 
#        round(
#        (location != n).if_then_else(min_distance_from_node[location]/2, 0) +
#        (returnToLocation!=n).if_then_else(min_distance_to_node[returnToLocation]/2, 0)))

#    state = model.target_state
#    print("Bound evaluation: {}".format(model.eval_dual_bound(state)))
 
    return model, name_to_customer


def solve(
    instance_name,
    model,
    name_to_customer,
    solver_name,
    history,
    time_limit=None,
    seed=2023,
    initial_beam_size=1,
    threads=1,
    parallel_type=0,
):
    if solver_name == "LNBS":
        if parallel_type == 2:
            parallelization_method = dp.BeamParallelizationMethod.Sbs
        elif parallel_type == 1:
            parallelization_method = dp.BeamParallelizationMethod.Hdbs1
        else:
            parallelization_method = dp.BeamParallelizationMethod.Hdbs2

        solver = dp.LNBS(
            model,
            initial_beam_size=initial_beam_size,
            seed=seed,
            parallelization_method=parallelization_method,
            threads=threads,
            time_limit=time_limit,
            quiet=False,
        )
    elif solver_name == "DD-LNS":
        solver = dp.DDLNS(model, time_limit=time_limit, quiet=False, seed=seed)
    elif solver_name == "FR":
        solver = dp.ForwardRecursion(model, time_limit=time_limit, quiet=False)
    elif solver_name == "BrFS":
        solver = dp.BreadthFirstSearch(model, time_limit=time_limit, quiet=False)
    elif solver_name == "CAASDy":
        solver = dp.CAASDy(model, time_limit=time_limit, quiet=False)
    elif solver_name == "DFBB":
        solver = dp.DFBB(model, time_limit=time_limit, quiet=False)
    elif solver_name == "CBFS":
        solver = dp.CBFS(model, time_limit=time_limit, quiet=False)
    elif solver_name == "ACPS":
        solver = dp.ACPS(model, time_limit=time_limit, quiet=False)
    elif solver_name == "APPS":
        solver = dp.APPS(model, time_limit=time_limit, quiet=False)
    elif solver_name == "DBDFS":
        solver = dp.DBDFS(model, time_limit=time_limit, quiet=False)
    else:
        if parallel_type == 2:
            parallelization_method = dp.BeamParallelizationMethod.Sbs
        elif parallel_type == 1:
            parallelization_method = dp.BeamParallelizationMethod.Hdbs1
        else:
            parallelization_method = dp.BeamParallelizationMethod.Hdbs2

        solver = dp.CABS(
            model,
            initial_beam_size=initial_beam_size,
            threads=threads,
            parallelization_method=parallelization_method,
            time_limit=time_limit,
            quiet=False,
        )

    if solver_name == "FR":
        solution = solver.search()
    else:
        with open(history, "w") as f:
            is_terminated = False

            while not is_terminated:
                solution, is_terminated = solver.search_next()

                if solution.cost is not None:
                    f.write(
                        "{}, {}\n".format(time.perf_counter() - start, solution.cost)
                    )
                    f.flush()

    print("Search time: {}s".format(solution.time))
    print("Expanded: {}".format(solution.expanded))
    print("Generated: {}".format(solution.generated))

    if solution.is_infeasible:
        print("The problem is infeasible")

        return None, None
    else:
        tour = []

        for t in solution.transitions:
            tour.append(name_to_customer[t.name])

#        print(" ".join(map(str, tour[1:-1])))

        print("best bound: {}".format(solution.best_bound))
        print("cost: {}".format(solution.cost))

        if solution.is_optimal:
            print("optimal cost: {}".format(solution.cost))

#Print to csv log
        csv_file_path = 'log.csv'
        
        if not os.path.exists(csv_file_path):
            with open(csv_file_path, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["Instance", "Cost", "Bound", "Opt", "Time", "NodesExpanded", "NodesGenerated"])        

    
        with open(csv_file_path, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([instance_name, solution.cost, solution.best_bound, solution.is_optimal, solution.time, solution.expanded, solution.generated])        

        return tour, solution.cost


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    parser.add_argument("--time-out", default=1800, type=int)
    parser.add_argument("--history", default="history.csv", type=str)
    parser.add_argument("--config", default="CABS", type=str)
    parser.add_argument("--seed", default=2023, type=int)
    parser.add_argument("--non-zero-base-case", action="store_true")
    parser.add_argument("--threads", default=1, type=int)
    parser.add_argument("--initial-beam-size", default=1, type=int)
    parser.add_argument("--parallel-type", default=0, type=int)
    args = parser.parse_args()

    n, nClass, nodes, edges, classes = read_gtsp.read(args.input)

    model, name_to_customer = create_model(
        n, nClass, nodes, edges, classes
    )
    tour, cost = solve(
        args.input,
        model,
        name_to_customer,
        args.config,
        args.history,
        time_limit=args.time_out,
        seed=args.seed,
        threads=args.threads,
        initial_beam_size=args.initial_beam_size,
        parallel_type=args.parallel_type,
    )

    
    print("tour:")
    print(tour)
    print("cost:")
    print(cost)
    
    if cost is not None and read_gtsp.validate(n, nClass, edges, classes, tour, cost):
        print("The solution is valid.")
    else:
        print("The solution is invalid.")
