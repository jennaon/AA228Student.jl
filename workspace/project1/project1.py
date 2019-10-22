import sys
import os
import networkx as nx
import pdb
import pandas as pd
import numpy as np
import random


import matplotlib.pyplot as plt
from plotter import plot_graph
# from helpers import get_bayesian_score
from better_helper import BayesScore
from random_neighbor_generator import RandomNeighborGenerator
import time

# np.random.seed(4812)


def create_random_graph(n, G):
    pdb.set_trace() #just to make sure your initialization is correct

    #Create a list of variables`

    # G_alt = nx.gnp_random_graph(n,.2, directed=True )

    #for tester.csv
    # G.add_edges_from([('A', 'C')])
    # G.add_edges_from([('B', 'C')])

    # for example.csv
    # G.add_edges_from([('parent1', 'child1')])
    # G.add_edges_from([('parent2', 'child2')])
    # G.add_edges_from([('parent3', 'child3')])

    G.add_edges_from([(0, 1)])
    G.add_edges_from([(2, 3)])
    G.add_edges_from([(4, 5)])


    # for small.csv
    # G.add_edge('fare', 'age')
    # G.add_edge('sex', 'numparentschildren')
    # G.add_edge('survived', 'sex')
    # pdb.set_trace()
    return G, G_alt

def is_cyclic(G):
    try:
        nx.find_cycle(G, orientation='original')
    except:
        return False
    return True

# def check_for_cycle_and_add(G, return_set):
#     if is_cyclic(G):
#         pass
#     else:
#         return_set.add(G)
#
def local_search(bayes, G_init, df):
    count = 0
    inner_count = 0
    init_score,M = bayes.get_bayesian_score(G_init)
    eps =  init_score * 0.001
    print('initial score: ',init_score)
    # pdb.set_trace()
    current_score=init_score
    best_score_so_far= current_score
    num_iters = 100
    G_new = G_init.copy()
    good_enough_init = init_score*.01 #make it diminishing
    good_enough_threshold = .5#good_enough_init/50

    while True:

        count += 1
        # print('***********************************')
        # print('***********************************')
        print('Serach ', count, 'current best score:', best_score_so_far)
        good_enough = good_enough_init/(count**2)
        if good_enough < good_enough_threshold:
            good_enough = 0.1
        # print('good enough: ',good_enough)
        generate = RandomNeighborGenerator(G_new)
        inner_count =0
        while True:
            # print('----Trying neighbor', inner_count)
            inner_count +=1
            neighbor=generate.get_random_neighbor()
            if neighbor == None: #search failed
                # print('No more feasible neighbor')
                return G_new, current_score #quit everything and return what you have

            new_score,a = bayes.get_bayesian_score(neighbor)


            new_score, junk = bayes.get_bayesian_score(neighbor)
            # print('new score: ',new_score)

            if current_score + good_enough < new_score:
                # print('update current score to ', new_score)
                #fast quit
                current_score= new_score
                G_new = neighbor
                break
            if current_score < new_score:
                current_score = new_score
                G_new = neighbor
                # break

        if abs(best_score_so_far - current_score) <0.01:
            print('giving up finding the best score: ', best_score_so_far)
            return G_new, max(best_score_so_far,current_score)
            break
        best_score_so_far = current_score

        if inner_count>num_iters:
            # print('loop broke by the inner safety check')
            return None, best_score
            # break
    if count>num_iters:
        # print('loop broke by the safety check')
        return None, None, best_score
        # break


def write_gph(dag, idx2names, filename):
    with open(filename, 'w') as f:
        for edge in dag.edges():
            f.write("{}, {}\n".format(idx2names[edge[0]], idx2names[edge[1]]))
# node_list

def compute(infile, outfile):
    start = time.time()
    df = pd.read_csv(infile)
    N, n = df.shape
    G = nx.gn_graph(n)
    #==========================================#
    #to verify values
    # G = nx.DiGraph()
    # G_new, G_alt = create_random_graph(n, G)
    #==========================================#

    bayes = BayesScore(G, df) # This is inside compute
    G_opt, score_opt = local_search(bayes, G, df)
    end = time.time()
    timer = end-start
    print('total time: %.2',timer)

    # G_opt = G; score_opt = 100;
    G_opt = nx.relabel_nodes(G_opt, bayes.idx2node)

    # plot_graph(G_opt, show=True)
    # pdb.set_trace()



    print('best final score:', score_opt)
    length = df.shape[1]

    d = bayes.node2idx
    node_list = sorted(d, key=d.get)
    # parents_values = [data[parent]-1 for parent in parents]
    # pdb.set_trace()


    timestamp = str(int(time.time()))
    new_dir = str("./out_")+timestamp
    os.mkdir(new_dir)

    filename = new_dir + ('/')+outfile
    write_gph(G_opt, bayes.node2idx, filename)

    fig = plot_graph(G_opt)
    title = 'score = %.2f, time taken = %.2f (s)' % (score_opt, timer)
    plt.title(title)
    # new_dir = str("./out_")+str(int(time.time()) )

    figname = new_dir+('/')+(infile[:2])+('.png')
    plt.savefig(figname)
    # pdb.set_trace()


def main():
    if len(sys.argv) != 3:
        raise Exception("usage: python project1.py <infile>.csv <outfile>.gph")

    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]
    compute(inputfilename, outputfilename)
if __name__ == '__main__':
    main()
