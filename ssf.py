#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
# Author: Vikram Singh, PhD Scholar at Centre for Computational Biology and
# Bioinformatics, Central University of Himachal Pradesh 
'''

import networkx as nx
from scipy.stats import beta
import numpy as np


def _get_distribution ( bin_size, Flag = 0 ):
    """Returns bin_size number of bins each ranging between [0, 1]"""
    
    # Get the step size
    lower =  0; upper = step = 1/bin_size
    Dist = {}
    
    # make bins
    while upper <= 1:
        Dist[Flag] = [ lower, upper ]
        Flag += 1
        lower = upper
        upper += step
    return Dist

def _beta_choice ( time_total, CurrentTime, dist, a = 0, b = 0 ):
    """Returns a specific number of nodes or edges form dist using a random
    number, ranging between [0, 1], drawn from beta distribution
    """
    
    # compute the parameters b and a
    if not b: b = ( time_total - CurrentTime ) / ( time_total )
    if not a: a = ( 1 - b )

    if b == 0 : b = 0.01
    
    rv = beta(a, b)
    
    # get a random number
    variate = beta.rvs( a, b )
    
    # get the key of bin in which the random variate falls
    for key in dist:
        if dist[key][0] <= variate < dist[key][1]:
            return key


def _preferential_attachment ( DistNodes, DistLinks, N_current, time_total, time_current, n, PrefAry, G ):
    """Preferentially attach InComing_Nodes with Nlinks source nodes to update
    G and PrefAry and returns incremented N_current
    """
    
    # Pick the number of target nodes
    InComing_Nodes = _beta_choice( time_total, time_current, DistNodes )

    if InComing_Nodes:
        for _ in range( InComing_Nodes ):
            if N_current >= n: break
            
            # Pick the number of source nodes
            Nlinks = _beta_choice( time_total, time_current, DistLinks, a = 0.03, b = 0.97 )
            
            # Get the source nodes from PrefAry uniformly at random (preferential attachment)
            sources = np.random.choice( PrefAry, size = Nlinks, replace = False ).tolist()

            for s in sources:
                # Update the graph and PrefAry list 
                G.add_edge(s, N_current, time_stamp = time_current)
                PrefAry.extend( [ s, N_current ] )
            
            N_current += 1
    return( N_current )


def ssf(n, N_max = 6, E_max = 4, time_total = 100 ):
    """Returns a random graph using stochastic scale free model

    A graph of $n$ nodes is grown by attaching N new nodes each carrying 
    multiple edges at a unit time interval that are preferentially attached to
    existing nodes with probability proportional to their degrees.

    Parameters
    ----------
    n : int
        Number of nodes

    N_max : int
                Nodes upper bound at a unit time interval

    E_max : int
                Nodes upper bound at a unit time interval
    
    time_total : int
               Period of outbreak for which to model the spread

    Returns
    -------
    G : Graph


    References
    ----------
    .. [1] A. L. Barabási and R. Albert "Emergence of scaling in
       random networks", Science 286, pp 509-512, 1999.
    """

    G = nx.DiGraph()
    G.add_edge( 0, 1, time_stamp = 1)

    # List of existing nodes, with nodes repeated once for each adjacent edge
    repeated_nodes = [0, 1]

    #   compute discrete bins for nodes 
    DistNodes = _get_distribution( N_max, 0 )
    #   compute discrete bins for edges
    DistLinks = _get_distribution( E_max, 1 )
            
    # Start adding the other n - 2 nodes.
    N_current = time_current = 2
    while N_current < n and time_current < time_total + 1:
        # preferential attachment
        N_current =  _preferential_attachment( DistNodes, DistLinks, N_current,
                     time_total, time_current, n, repeated_nodes, G )
        time_current += 1
    
#    print(time_current, N_current)
    return G

if __name__ == '__main__':
    g = ssf(185)
    nx.write_edgelist(g, "_edgelist.txt", data=['time_stamp'])