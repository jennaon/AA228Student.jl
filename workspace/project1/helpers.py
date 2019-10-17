import sys
import pdb
import numpy as np
import networkx as nx
from plotter import plot_graph
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.special import loggamma
import time

def idx2key(i,j,k):
    return str(i)+str(j)+str(k)

def get_bayesian_score(df, variables,G):
    # return 1
    py_df = df-1;
    #initialize
    N,n = df.shape
    node2idx = {k: v for v, k in enumerate(variables)}
    idx2node = {y:x for x,y in node2idx.items()}
    R=(df.max()).to_dict()
    R_list = df.max()
    parents_dict = {}
    num_parents_dict = {}
    Q={} #num_parents_instantiation
    M=defaultdict(lambda:0)
    # pdb.set_trace()

    def get_parents_R(parents):
        parents_R = []
        for i in range(len(parents)):
            parents_R.append(R[parents[i]])
        return parents_R
    lap1 = time.time()

    for i in range(n): #for each variable
        current_node = idx2node[i]
        parents = list(nx.ancestors(G, current_node))
        parents_dict[idx2node[i]] = parents


        if not parents :#if there is no parents
            num_parents = 0
            Q[current_node] = 1
        else:
            num_pa_inst =1
            num_parents = len(parents)
            for j in range(num_parents):
                num_pa_inst *= R[parents[j]]
            Q[current_node] = num_pa_inst

        num_parents_dict[idx2node[i]]=num_parents #number of parents
    lap2 = time.time()
    print('time to build Q and explore parents: %f'%(lap2-lap1))
    #build M
    for sample in range(N):
        data = df.iloc[sample] #data starts with zero
        data_ls = data.to_list()
        # print('======================================')
        # print(data.to_list())
        lap7, lap8, lap5, lap6=(0.0, 0.0, 0.0, 0.0)
        for i in range(len(data)):
            # print('Variable %s' % idx2node[i])
            # print(i)
            # parents = list(nx.ancestors(G, idx2node[i]))
            lap5 = time.time()
            parents = parents_dict[idx2node[i]]
            lap6=time.time()
            # pdb.set_trace()
            if not parents: #if there is no parents
                j = 1
            else:
                lap7=time.time()
                parents_idx = [data[parent]-1 for parent in parents]
                # pdb.set_trace()
                # parents_idx = [0]
                # alt = (data[parents]-1).to_list()
                j = np.ravel_multi_index(parents_idx,
                                            get_parents_R(parents))
                lap8 = time.time()
                # pdb.set_trace()
                # pdb.set_trace()
                # print(parents, ' with index , ',parents_idx, '  j: ', j)
            k = data_ls[i]-1
            # print('increment ', (i,j,k))
            M[idx2key(i,j,k)]+=1
            # pdb.set_trace()
    lap3 = time.time()
    print('time to build M table: %f'%(lap3-lap2))

    #calculate score
    score = 0
    for i in range(n):
        # var_score = 0
        # pdb.set_trace()
        #don't iterate through everything
        for j in range(Q[idx2node[i]]+1):
            a_ij0 = R[idx2node[i]]
            m_ij0 = 0
            for k in range(R[idx2node[i]]):
                m_ij0 += M[idx2key(i,j,k)]
                score += loggamma (1 + M[idx2key(i,j,k)]) - loggamma(1)

            score += loggamma(a_ij0) - loggamma(a_ij0 + m_ij0)

    lap4 = time.time()
    print('time to calculate score: %f'%(lap4-lap3))
    pdb.set_trace()
    return score, M


# In broad strokes, you have to: count different subsets of the data
#  repeatedly (the subset associated with (i1,j1,k1), then with (i1,j1,k2), and so on.
#   This is where I'm suggesting vectorization in python for time efficiency.
#
# As for another hint:
# Rather than going 1. pick i, 2. pick j, 3. pick k 4. count
# Try instead to do 1. pick i, 2. find all possible js that appear in the data
# 3. find all possible ks that appear in the data. 4. count
#  (now it's one big step since you pre-calculated all of j and k)
#piazza @294
