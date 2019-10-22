# random_neighbor_generator.py
import networkx as nx
import pdb
import numpy as np
import random
from scipy.special import factorial
import copy


import matplotlib.pyplot as plt
from plotter import plot_graph

class RandomNeighborGenerator():
    def __init__(self,G):
        self.nodes = list(G.nodes)
        self.edges = list(G.edges)

        self.reverse_an_edge_from = copy.deepcopy(self.edges)
        random.shuffle(self.reverse_an_edge_from)
        self.remove_an_edge_from  = copy.deepcopy(self.edges)
        random.shuffle(self.remove_an_edge_from)

        self.shuffled_nodes_1  = copy.deepcopy(self.nodes)
        random.shuffle(self.shuffled_nodes_1)
        self.shuffled_nodes_2  = copy.deepcopy(self.nodes)
        random.shuffle(self.shuffled_nodes_2)

        self.reverse_counter=0
        self.remove_counter=0
        self.add_counter=[0,0] #i,j

        # print(self.add_counter)

        self.possible_operations = {1,2,3}
        self.max_add_edge_operations = factorial(len(self.nodes),exact=True)-len(self.edges) #adding an edge
        self.G = G

    def is_cyclic(self,G):
        try:
            nx.find_cycle(G, orientation='original')
        except:
            return False
        return True

    def reverse_an_edge(self):
        # print('IN: reverse an edge')
        G_new = self.G.copy()
        count = 0
        while True:
            count +=1
            # print('attempt ',count)
            # pdb.set_trace()
            this_edge = self.reverse_an_edge_from[self.reverse_counter]
            G_new.remove_edge(this_edge[0], this_edge[1])
            G_new.add_edge(this_edge[1], this_edge[0] )

            self.reverse_counter +=1

            if not self.is_cyclic(G_new):
                # print('found a graph with a reversed edge')
                return G_new
                break
            if self.reverse_counter == len(self.edges):
                # print('cant reverse edges anymore')
                return None
                break

    def remove_an_edge(self):
        # print('IN: remove an edge')
        G_new = self.G.copy()
        count = 0
        while True:
            count +=1
            # print('attempt ',count)
            # pdb.set_trace()
            this_edge = self.remove_an_edge_from[self.remove_counter]
            G_new.remove_edge(this_edge[0], this_edge[1])

            self.remove_counter +=1

            if not self.is_cyclic(G_new):
                # print('found a graph with a removed edge')
                return G_new
                break
            if self.remove_counter == len(self.edges):
                # print('cant remove edges anymore')
                return None
                break

    def add_an_edge(self):
        # print('IN: add an edge')
        i_start, j_start = self.add_counter
        counter = 0
        for i in range(i_start, len(self.shuffled_nodes_1)):
            for j in range(j_start, len(self.shuffled_nodes_2)):
                # print('attempt ', counter, 'i: ', i, 'j: ',j)
                counter +=1
                #do stuff
                start= self.shuffled_nodes_1[i]
                end = self.shuffled_nodes_2[j]

                if start == end :
                    # print('same deal')
                    continue
                if not self.G.has_edge(start,end):
                    G_new = self.G.copy()
                    G_new.add_edge(start, end)
                    if self.is_cyclic(G_new):
                        pass
                        # G_new.remove_edge(start, end)
                        # print('cyclic :( ')
                    else:
                        # print('found a graph with an added edge edge')

                        if j% (len(self.nodes)) == len(self.nodes)-1:
                            self.add_counter = [i+1,1]
                        else:
                            self.add_counter = [i,j+1]
                        return G_new
                        break
                else:
                    pass
                    # print('duplicate edge')

        # pdb.set_trace()
        # if self.add_counter[0] == len(self.nodes) and \
        #     self.add_counter[1] == len(self.nodes):
        #     print('cant add anymore!'')
        self.possible_operations.remove(3)
        # print('cant add edges anymore')
        return None

    def get_random_neighbor(self):
        keepgoing = False #for debugging
        while True:
            if not self.possible_operations:
                print('no more possible operations, quit')
                return None
                break

            random_number = random.sample(self.possible_operations, 1)[0]
            # print('======================================')
            # print('random_number:', random_number)
            # if random
            # pdb.set_trace()
            if random_number == 1: #reverse an edge
                neighbor=self.reverse_an_edge()

                if self.reverse_counter ==len(self.edges):
                    self.possible_operations.remove(1)

                if neighbor is not None:
                    if not keepgoing:
                        return neighbor

            elif random_number == 2: #remove an edge
                neighbor=self.remove_an_edge()
                if self.remove_counter ==len(self.edges):
                    self.possible_operations.remove(2)

                if neighbor is not None:
                    if not keepgoing:
                        return neighbor

            else: #add an edge
                neighbor=self.add_an_edge()

                # if self.add_counter ==self.max_add_edge_operations:
                # if self.add_counter[0] == len(self.nodes) and \
                #     self.add_counter[1] == len(self.nodes):
                #     print('cant add anymore!'')
                #     self.possible_operations.remove(3)

                if neighbor is not None:
                    if not keepgoing:
                        return neighbor
            # pdb.set_trace()
        self.possible_operations=[]#fix this
