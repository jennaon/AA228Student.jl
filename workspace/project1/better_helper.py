# better_helper.py
import sys
import pdb
import numpy as np
import networkx as nx
from plotter import plot_graph
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.special import loggamma
import time


class BayesScore():
    def __init__(self,G, df):
        self.df = df
        self.py_df = df-1;
        self.N, self.n = df.shape

        self.G_prev = None
        self.score_prev = 0

        self.R = (df.max()).to_dict()
        # R_list = df.max()
        # self.Q = {}
        # self.M = defaultdict(lambda:0)

        # variables = df.columns.values.tolist()
        self.node2idx = {k: v for v, k in enumerate(df.columns.values.tolist())}
        self.idx2node = {y:x for x,y in self.node2idx.items()}
        # self.parents_dict = {}
        # self.num_parents_dict = {}

        # self.j_lookup={} #format {parents_idx:j}
        self.j_lookup = [{} for _ in range(self.n)]
        self.i_lookup = [() for _ in range(self.n)]

        # pdb.set_trace()

    def idx2key(self,i,j,k):
        return str(i)+str(j)+str(k)

    def get_parents_R(self,parents):
        parents_R = []
        for i in range(len(parents)):
            parents_R.append(self.R[parents[i]])
        return parents_R

    # def get_change(self, change):
    #     if type(change) == list: #inidicates the direction was reversed
    #         pass
    #         #do something about the change
    #     else:
    #         self.change = change
    #     pass

    def get_bayesian_score(self, G):
        # pdb.set_trace()
        self.parents_dict = {}
        self.num_parents_dict = {}
        self.Q = {}
        self.M = defaultdict(lambda:0)
        self.j_lookup = [{} for _ in range(self.n)]
        self.i_lookup = [{} for _ in range(self.n)]

        for i in range(self.n): #for each variable
            current_node = self.idx2node[i]
            parents = list(nx.ancestors(G, current_node))
            self.parents_dict[self.idx2node[i]] = parents


            if not parents :#if there is no parents
                num_parents = 0
                self.Q[current_node] = 1
            else:
                num_pa_inst =1
                num_parents = len(parents)
                for j in range(num_parents):
                    num_pa_inst *= self.R[parents[j]]
                self.Q[current_node] = num_pa_inst

            self.num_parents_dict[self.idx2node[i]]=num_parents #number of parents
        lap2 = time.time()

        #build M
        for sample in range(self.N):
            data = self.df.iloc[sample] #data starts with zero
            data_ls = data.to_list()

            lap7, lap8, lap5, lap6=(0.0, 0.0, 0.0, 0.0)
            for i in range(len(data)):
                lap5 = time.time()
                parents = self.parents_dict[self.idx2node[i]]
                lap6=time.time()
                # pdb.set_trace()
                if not parents: #if there is no parents
                    j = 1
                else:
                    lap7=time.time()
                    # pdb.set_trace()
                    parents_values = [data[parent]-1 for parent in parents]
                    key = str(parents_values)
                    jdict = self.j_lookup[i]
                    if key in jdict:
                        j = jdict[key]
                    else:
                        j=np.ravel_multi_index(parents_values,self.get_parents_R(parents))
                        self.j_lookup[i][key] = j
                    lap8 = time.time()
                k = data_ls[i]-1
                self.M[self.idx2key(i,j,k)]+=1
                # pdb.set_trace()
        lap3 = time.time()

        #calculate score
        score = 0
        # for i in range(self.n):
        for i in list(self.idx2node.keys()):
            # print('variable ',self.idx2node[i])
            j_list = list(self.j_lookup[i].values())
            a_ij0 = self.R[self.idx2node[i]]
            # var_score=0
            if not j_list:
                m_ij0 = 0
                j =1
                for k in range(self.R[self.idx2node[i]]): #waste
                    m_ij0 += self.M[self.idx2key(i,j,k)]

                    score += loggamma (1 + self.M[self.idx2key(i,j,k)])
                score += loggamma(a_ij0) - loggamma(a_ij0 + m_ij0)
            else:
                for j in j_list:
                    m_ij0 = 0

                    for k in range(self.R[self.idx2node[i]]): #waste
                        m_ij0 += self.M[self.idx2key(i,j,k)]
                        score += loggamma (1 + self.M[self.idx2key(i,j,k)])

                    score += loggamma(a_ij0) - loggamma(a_ij0 + m_ij0)

        return score, self.M
