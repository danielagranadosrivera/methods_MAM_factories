import pandas as pd
import numpy as np
from functions_greedy_MF import *


def initial_routes(z, locations, customers, Set_h, Set_t):

    # preliminar procedures
    
    #compute distances between all locations and customers
    nodes = np.vstack((locations, customers)) 
    d_nodes = distances(nodes, nodes)
    
    #create variable to save results 
    s_drone_origin_destination_period = np.zeros((Set_h, len(nodes), len(nodes), Set_t)).astype(int) # Binary variable if drone h∈H goes from location a∈{I∪L} to location g∈{I∪L} in day t∈T
     
    Set_i = len(locations) # set size of first set
    z_routes = z[z["Value"] > 0] # filter days with routes
    days_routes = z_routes["Period"].unique().astype(int) # extract days where there are routes with the drone or drones
    
    # for each day when drones were used
    for day in days_routes:
        
        routes_day = z_routes[z_routes["Period"] == day] # extract routes of the day
        drones_used = routes_day["Drone"].unique().astype(int) # extract drones used that day
        
        # for each drone used
        for drone in drones_used:
            
            route = [] # list to save the route
            
            route_by_drone = routes_day[routes_day["Drone"] == drone] # extract the route of the drone
            origin = route_by_drone["Location"].unique().astype(int) # extract the origin location from drone departure
            nodes_to_visit = route_by_drone["Customer"].unique().astype(int) # extract customers to visit
            nodes_to_visit = nodes_to_visit - 1 + Set_i # update index of nodes
            nodes_to_visit = np.ma.array(nodes_to_visit, mask=False)
            
            route.append(origin.item() - 1) # initialize route from the location of the factory
            all_nodes_visited = np.sum(nodes_to_visit.mask)
            
            while all_nodes_visited < len(nodes_to_visit):
                
                origin = route[-1] # update origin
                valid_nodes = nodes_to_visit[~nodes_to_visit.mask]
                d_origin_node = d_nodes[origin, valid_nodes] # extract distances
                
                # closest node
                d_origin_node = np.where(d_origin_node == 0, np.inf, d_origin_node)
                min_distance = np.argmin(d_origin_node)
                nearest_node = valid_nodes[min_distance]
                
                # add node to route
                route.append(nearest_node)
                index = np.where(nodes_to_visit == nearest_node)[0][0]
                nodes_to_visit.mask[index] = True
                
                all_nodes_visited = np.sum(nodes_to_visit.mask) # update count
            
            final = route_by_drone["Location"].unique().astype(int) # extract the location from drone arrival
            route.append(final.item() - 1) # end route
            
            
            # update route in variable
            for g in range(len(route)-1):       
                s_drone_origin_destination_period[drone-1][route[g]][route[g+1]][day-1] = 1

    return s_drone_origin_destination_period
        
        
        
        
        