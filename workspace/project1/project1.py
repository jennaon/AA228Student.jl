import sys
import networkx as nx
import pdb
import pandas as pd
import numpy as np
import random

import matplotlib.pyplot as plt
from plotter import plot_graph
# from helpers import get_bayesian_score
from better_helper import BayesScore
import time

np.random.seed(4812)
eps = .001
good_enough = 5


def create_graph(variables, G):
    #Create a list of variables`

    #create a random graph based on the variables
    #TODO: randomize
    G.add_nodes_from(variables)

    #for tester.csv
    # G.add_edges_from([('A', 'C')])
    # G.add_edges_from([('B', 'C')])

    # for example.csv
    # G.add_edges_from([('parent1', 'child1')])
    # G.add_edges_from([('parent2', 'child2')])
    # G.add_edges_from([('parent3', 'child3')])


    # for small.csv
    G.add_edge('fare', 'age')
    G.add_edge('sex', 'numparentschildren')
    G.add_edge('survived', 'sex')
#
# try:
#     nx.find_cycle(G, orientation='original')
#  except:
#      pass

def is_cyclic(G):
    try:
        nx.find_cycle(G, orientation='original')
    except:
        return False
    return True

def check_for_cycle_and_add(G, return_set):
    if is_cyclic(G):
        pass
    else:
        return_set.add(G)
        # plot_graph(G, show=False)

def get_neighbor_graphs(G):
    # random.rand
    all_nodes = set(G.nodes)
    edges = list(G.edges)

    track_operations=[0,0,0] #(add, remove, reverse)
    operation_limit = [len(edges), len(edges)]

    all_neighbors = set()
    random.randint(1, 10)

    #all that can be obtained by removing an edge
    for i in range(len(edges)):

        G_new = G.copy()
        G_new.remove_edge(edges[i][0], edges[i][1])
        check_for_cycle_and_add(G_new, all_neighbors)

        G_new_new = G_new.copy()
        G_new_new.add_edge( edges[i][1], edges[i][0])
        check_for_cycle_and_add(G_new_new, all_neighbors)
        del G_new
        del G_new_new
        # pdb.set_trace()

    #all that can be obtained by adding an edge

    # # pdb.set_trace()
    # nodes = list(G.nodes)
    # # random.shuffle(nodes)========================
    # for i in range(len(nodes)-1):
    #     # pdb.set_trace()
    #     node = nodes[i]
    #     for j in range(i+1,len(nodes)):
    #         compare_node = nodes[j]
    #         if G.has_edge(node, compare_node):
    #             pass
    #         else :
    #             G_new = G.copy()
    #             G_new.add_edge(node, compare_node)
    #             check_for_cycle_and_add(G_new, all_neighbors)
    #             del G_new
    #         if G.has_edge(compare_node, node):
    #             pass
    #         else:
    #             G_new = G.copy()
    #             G_new.add_edge(node, compare_node)
    #             check_for_cycle_and_add(G_new, all_neighbors)
    #             del G_new

    return all_neighbors

def local_search(bayes, G_init, df):
    count = 0
    variables =df.columns.values.tolist()
    init_score,M = bayes.get_bayesian_score(G_init)
    print('initial score: ',init_score)
    # pdb.set_trace()
    current_score=init_score
    best_score = current_score
    num_iters = 100
    G_new = G_init.copy()

    while True:
        count += 1
        print(count)
        # pdb.set_trace()

        # lap1 = time.time()
        neighbor_graphs = list(get_neighbor_graphs(G_new))
        # lap2 = time.time()

        # print('time to get graphs: %f'%(lap2-lap1))
        # random.shuffle(neighbor_graphs)
        # print(len(neighbor_graphs))
        for neighbor in neighbor_graphs:
            # lap1 = time.time()
            new_score,new_M = bayes.get_bayesian_score(neighbor.copy())
            # pdb.set_trace()
            # lap2 = time.time()
            # print('time to get scores: %f'%(lap2-lap1))
            if best_score < new_score:
                # print('found a better neighbor!, current: %f, best: %f'%(current_score, best_score))
                G_new = neighbor.copy()
                best_score = new_score
        # pdb.set_trace()


        # print('best score: %f' %best_score)
        # print('current score: %f' %current_score)


        if abs(best_score-current_score)<eps:
            print('best score:',best_score)
            return G_new
            break
        else:
            # print('update the current score')
            current_score = best_score


        if count>num_iters:
            # print('loop broke by the safety check')
            return None
            break


def write_gph(dag, idx2names, filename):
    with open(filename, 'w') as f:
        for edge in dag.edges():
            f.write("{}, {}\n".format(idx2names[edge[0]], idx2names[edge[1]]))


def compute(infile, outfile):
    df = pd.read_csv(infile)
    variables = df.columns.values.tolist()
    G = nx.DiGraph()
    create_graph(variables, G)

    # score = get_bayesian_score(df, variables,G)
    bayes = BayesScore(G, df)
    G_opt = local_search(bayes, G, df)
    # pdb.set_trace()



def main():
    if len(sys.argv) != 3:
        raise Exception("usage: python project1.py <infile>.csv <outfile>.gph")

    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]
    compute(inputfilename, outputfilename)


if __name__ == '__main__':
    main()
