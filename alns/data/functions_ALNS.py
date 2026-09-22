import numpy as np
import pandas as pd
from functions_greedy_MF import *
from initialization_routes import *
from datetime import datetime
from datetime import timedelta
import copy
import pdb


# class solution to keep track of the metaheuristic
class solution:
    def __init__(self, x, y_hat, s, w, u, f, x_hat, n, z, z_hat, b, e, w_hat, u_hat, m_hat, lambda_, evaluation_parameters):
        """
        The class solution will contain all variables
        """
        self.x = x
        self.y_hat = y_hat
        self.s = s
        self.w = w
        self.u = u
        self.f = f
        self.x_hat = x_hat
        self.n = n        
        self.z = z
        self.z_hat = z_hat        
        self.b = b
        self.e = e
        self.w_hat = w_hat
        self.u_hat = u_hat
        self.m_hat = m_hat
        self.lambda_ = lambda_
        self.evaluation_parameters = evaluation_parameters
    
    def copy(self):
        # return a fresh new object with copied internals
        return solution(
            x = self.x.copy(),
            y_hat = self.y_hat.copy(),
            s = self.s.copy(),
            w = self.w.copy(),
            u = self.u.copy(),
            f = self.f.copy(),
            x_hat = self.x_hat.copy(),
            n = self.n.copy(),        
            z = self.z.copy(),
            z_hat = self.z_hat.copy(),        
            b = self.b.copy(),
            e = self.e.copy(),
            w_hat = self.w_hat.copy(),
            u_hat = self.u_hat.copy(),
            m_hat = self.m_hat.copy(),
            lambda_ = self.lambda_.copy(),
            evaluation_parameters = self.evaluation_parameters
        )
       
    def objective(self):
        """
        The objective function is the cost
        """
        locations = self.evaluation_parameters[0]
        CR_f = self.evaluation_parameters[1] 
        CR_v = self.evaluation_parameters[2] 
        alpha = self.evaluation_parameters[3] 
        CP_f = self.evaluation_parameters[4] 
        Set_p = self.evaluation_parameters[5] 
        CT = self.evaluation_parameters[6] 
        customers = self.evaluation_parameters[7] 
        CT1 = self.evaluation_parameters[8] 
        harbors = self.evaluation_parameters[9] 
        CT2 = self.evaluation_parameters[10] 
        CB_ini = self.evaluation_parameters[11]
        
        relocation_cost = relocation_cost_calculation(self.x, locations, CR_f, CR_v)
        production_cost = production_cost_calculation(self.y_hat, alpha, CP_f, Set_p)
        shipments_drone_cost = shipments_drone_cost_calculation(self.s, CT, locations, customers)
        shipments_land_cost = shipments_land_cost_calculation(self.w, CT1, locations, harbors)
        shipments_ship_cost = shipments_ship_cost_calculation(self.u, CT2)
        penalties_cost = penalties_cost_calculation(self.f, CB_ini)

        total_cost = relocation_cost + production_cost + shipments_drone_cost + shipments_land_cost + shipments_ship_cost + penalties_cost
        
        self.objective_function = total_cost
        
        return total_cost


# destroy operator #1: Remove shipments by ship based on the late variable
def deallocate_based_f(f,z_hat,w_hat,lambda_):
    
    f = df_creation_four_index(f, names=["Product","Customer","Due date","Period","Value"])
    f["Score_late"] = (f["Period"] - f["Due date"]) * f["Value"]
    f_sorted = f.sort_values(by='Score_late', ascending=False)
    demand_to_deallocate = f_sorted.iloc[0]
    
    # update w_hat
    ####################################################
    
    # extract index of demand to allocate
    product = demand_to_deallocate["Product"] - 1
    customer = demand_to_deallocate["Customer"] - 1
    
    
    # find missing indexes for w_hat
    factory, harbor, period = np.where(w_hat[product, :, :, customer, :] == demand_to_deallocate["Value"]) 
    
    if len(period) > 0:
        units_to_deallocate = w_hat[product, factory, harbor, customer, period]
        origin_factory = factory
        previous_period_shipment = period
        w_hat[product, factory, harbor, customer, period] = 0
    
    else:
        drone, factory, period = np.where(z_hat[product, :, :, customer, :] == demand_to_deallocate["Value"]) 
        units_to_deallocate = z_hat[product, drone, factory, customer, period]
        origin_factory = factory
        previous_period_shipment = period
        z_hat[product, drone, factory, customer, period] = 0
    
    # update lambda_
    ####################################################
    period = period.item()
    for t in range(period):
        
        demand_met = lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1 - t), "Demand_met"]
        
        # if the demand met is greater than zero
        if demand_met.iloc[0] > 0:
            units_to_remove = np.minimum(units_to_deallocate, demand_met.iloc[0])
            lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1 - t), "Demand_met"] = int(demand_met.item()) - units_to_remove
            lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1 - t), "Mask_met_demand"] = False
            
            # check if there is a na value
            value = lambda_.loc[(lambda_["Product"] == product + 1) & (lambda_["Customer"] == customer + 1) & (lambda_["Period"] == period + 1 - t),"Demand_met"]
            if value.empty:
                lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1 - t), "Demand_met"] = 0
            
            units_to_deallocate = units_to_deallocate - units_to_remove
        
        if units_to_deallocate == 0:
            break
        
    # in case that there are still units_to_deallocate
    t = period + 1
    while units_to_deallocate > 0:
        
        demand_met = lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== t + 1), "Demand_met"]
        
        # if the demand met is greater than zero
        if demand_met.iloc[0] > 0:
            units_to_remove = np.minimum(units_to_deallocate, demand_met.iloc[0])
            lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== t + 1), "Demand_met"] = int(demand_met.item()) - units_to_remove
            lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== t + 1), "Mask_met_demand"] = False
            
            # check if there is a na value
            value = lambda_.loc[(lambda_["Product"] == product + 1) & (lambda_["Customer"] == customer + 1) & (lambda_["Period"] == t + 1),"Demand_met"]
            if value.empty:
                lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== t + 1), "Demand_met"] = 0
            
            units_to_deallocate = units_to_deallocate - units_to_remove
        
        if units_to_deallocate == 0:
            break
        
        t += 1
    
    return z_hat, w_hat, lambda_, origin_factory, previous_period_shipment


# feasibility for destroy operator #1: Remove shipments by ship based on the late variable
def feasibility_deallocate_based_f(f,z_hat,w_hat):
    
    f = df_creation_four_index(f, names=["Product","Customer","Due date","Period","Value"])
    f["Score_late"] = (f["Period"] - f["Due date"]) * f["Value"]
    f_sorted = f.sort_values(by='Score_late', ascending=False)
    demand_to_deallocate = f_sorted.iloc[0]
    
    
    # update w_hat
    ####################################################
    
    # extract index of demand to allocate
    product = demand_to_deallocate["Product"] - 1
    customer = demand_to_deallocate["Customer"] - 1
    
    
    # find missing indexes for w_hat
    factory, harbor, period_ship = np.where(w_hat[product, :, :, customer, :] == demand_to_deallocate["Value"]) 
    drone, factory, period_drone = np.where(z_hat[product, :, :, customer, :] == demand_to_deallocate["Value"])
    
    if len(period_ship) == 1:
        feasibility = 1
    else:
        if len(period_drone) == 1:
            feasibility = 1
        else:
            feasibility = 0
    
    return feasibility


# destroy operator #2: Remove shipments by ship randomly
def deallocate_from_truck_ship_random(f,z_hat,w_hat,lambda_):
        
    # filter non zero indexes
    nonzero_indices = np.argwhere(w_hat > 0)
    
    # select a random row (index) from the found indices    
    chosen_index = tuple(nonzero_indices[np.random.randint(0, nonzero_indices.shape[0])])

    # extract indexes
    product = chosen_index[0]
    factory	= chosen_index[1]
    harbor = chosen_index[2]
    customer = chosen_index[3]
    period = chosen_index[4]
    
    
    # update w_hat
    ####################################################
    units_to_deallocate = w_hat[product, factory, harbor, customer, period]
    origin_factory = factory
    previous_period_shipment = period
    w_hat[product, factory, harbor, customer, period] = 0
    
    
    # update lambda_
    ####################################################
    for t in range(period):
        
        demand_met = lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1 - t), "Demand_met"]
        
        # if the demand met is greater than zero
        if demand_met.iloc[0] > 0:
            units_to_remove = np.minimum(units_to_deallocate, demand_met.iloc[0])
            lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1 - t), "Demand_met"] = int(demand_met.item()) - units_to_remove
            lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1 - t), "Mask_met_demand"] = False
            
            # check if there is a na value
            value = lambda_.loc[(lambda_["Product"] == product + 1) & (lambda_["Customer"] == customer + 1) & (lambda_["Period"] == period + 1 - t),"Demand_met"]
            if value.empty:
                lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1 - t), "Demand_met"] = 0
                  
            units_to_deallocate = units_to_deallocate - units_to_remove
        
        if units_to_deallocate == 0:
            break
        
    # in case that there are still units_to_deallocate
    t = period + 1
    while units_to_deallocate > 0:
        
        demand_met = lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== t + 1), "Demand_met"]
        
        # if the demand met is greater than zero
        if demand_met.iloc[0] > 0:
            units_to_remove = np.minimum(units_to_deallocate, demand_met.iloc[0])
            lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== t + 1), "Demand_met"] = int(demand_met.item()) - units_to_remove
            lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== t + 1), "Mask_met_demand"] = False
            
            # check if there is a na value
            value = lambda_.loc[(lambda_["Product"] == product + 1) & (lambda_["Customer"] == customer + 1) & (lambda_["Period"] == t + 1),"Demand_met"]
            if value.empty:
                lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== t + 1), "Demand_met"] = 0    
        
            units_to_deallocate = units_to_deallocate - units_to_remove
        
        if units_to_deallocate == 0:
            break
        
        t += 1
        
    return z_hat, w_hat, lambda_, origin_factory, previous_period_shipment


# destroy operator #3: Remove shipments by drone
def deallocate_from_drone_random(f,z_hat,w_hat,lambda_):
    
    # filter non zero indexes
    nonzero_indices = np.argwhere(z_hat > 0)
    
    # select a random row (index) from the found indices    
    chosen_index = tuple(nonzero_indices[np.random.randint(0, nonzero_indices.shape[0])])

    # extract indexes
    product = chosen_index[0]
    drone = chosen_index[1]
    factory	= chosen_index[2]
    customer = chosen_index[3]
    period = chosen_index[4]
    
    
    # update z_hat
    ####################################################
    units_to_deallocate = z_hat[product, drone, factory, customer, period]
    origin_factory = factory
    previous_period_shipment = period
    z_hat[product, drone, factory, customer, period] = 0
    
    
    # update lambda_
    ####################################################    
    
    for t in range(period):
        
        demand_met = lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1 - t), "Demand_met"]
        
        # if the demand met is greater than zero
        if demand_met.iloc[0] > 0:
            units_to_remove = np.minimum(units_to_deallocate, demand_met.iloc[0])
            lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1 - t), "Demand_met"] = int(demand_met.item())  - units_to_remove
            lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1 - t), "Mask_met_demand"] = False
            
            # check if there is a na value
            value = lambda_.loc[(lambda_["Product"] == product + 1) & (lambda_["Customer"] == customer + 1) & (lambda_["Period"] == period + 1 - t),"Demand_met"]
            if value.empty:
                lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1 - t), "Demand_met"] = 0
            
            units_to_deallocate = units_to_deallocate - units_to_remove
        
        if units_to_deallocate == 0:
            break
        
    # in case that there are still units_to_deallocate
    t = period + 1
    while units_to_deallocate > 0:
        
        demand_met = lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== t + 1), "Demand_met"]
        
        if demand_met.iloc[0] > 0:
            units_to_remove = np.minimum(units_to_deallocate, demand_met.iloc[0])
            lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== t + 1), "Demand_met"] = int(demand_met.item())  - units_to_remove
            lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== t + 1), "Mask_met_demand"] = False
            
            # check if there is a na value
            value = lambda_.loc[(lambda_["Product"] == product + 1) & (lambda_["Customer"] == customer + 1) & (lambda_["Period"] == t + 1),"Demand_met"]
            if value.empty:
                lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== t + 1), "Demand_met"] = 0
        
            units_to_deallocate = units_to_deallocate - units_to_remove
        
        if units_to_deallocate == 0:
            break
        
        t += 1
        
    return z_hat, w_hat, lambda_, origin_factory, previous_period_shipment


# repair operator #1: Send by drone
def send_by_drone(z_hat, w_hat, lambda_, d_i_l, delta_i_l, b, x, x_hat, beta, omega, Set_t, origin_factory, previous_period_shipment):
    
    lambda_to_meet = lambda_[(lambda_["Mask_met_demand"] == False) & (lambda_["Value"] > 0)] # filter demand not met
    
    for row in range(len(lambda_to_meet)):
        
        index = lambda_to_meet.index[row] # extract index because when sort they have another index
        
        # extract demand to meet
        demand_to_meet = lambda_to_meet.loc[index, "Value"]
        demand_allocated = lambda_to_meet.loc[index, "Demand_met"]
        demand_to_meet = demand_to_meet - demand_allocated
        
        # extract indexes
        product = lambda_to_meet.loc[index, "Product"] - 1
        customer = lambda_to_meet.loc[index, "Customer"] - 1
        period = lambda_to_meet.loc[index, "Period"] - 1
        factory = origin_factory.item()
        
        # define starting and ending period to send by drone
        if previous_period_shipment > period:
            start = int(period)
            end = int(previous_period_shipment)
        else:
            start = int(previous_period_shipment)
            end = int(period)
        
        
        # cycle to check multiple available periods
        for t in range(start, end):
            
            # check location of drones in that period
            drone, drone_location = np.where(b[:, :, t] == 1) 
            
            # check location factory origin
            factory_location = np.where(x_hat[origin_factory.item(),:,t] == 1)
            
            # check if there is a drone location that match a factory location
            location = [i for i, val in enumerate(drone_location) if val in factory_location]
            
            # check if there is a drone in the location where inventory available
            if len(location) > 0:
                
                location = drone_location[location]
                
                # check coverage range and relocations
                if delta_i_l[location[0],customer] == 1 and np.sum(x[factory,:,:,t]) == 0:    
                    drone_to_use = np.where(b[:, location[0], t] == 1)
                    z_hat[product, drone_to_use, factory, customer, t] = z_hat[product, drone_to_use, factory, customer, t] + demand_to_meet
                    lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1), "Demand_met"] = lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1), "Demand_met"] + demand_to_meet
                    lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1), "Mask_met_demand"] = True
                    demand_to_meet = 0
                    break
            
            if demand_to_meet == 0:
                break
        
        
        # check if it could be sent by drone or it needs to be allocated by ship
        if demand_to_meet > 0:
            
            # find the soonest ship scheduled
            beta_customer = beta[(beta["Customer"] == customer + 1) & (beta["Period"] > previous_period_shipment.item() + 1) & (beta["Value"] == 1)]
            beta_customer = beta_customer.sort_values(by='Period', ascending=True)
            
            # allocate the demand to the soonest feasible ship schedules
            for option in range(len(beta_customer)):
                
                index_option = beta_customer.index[option]
                harbor_option = beta_customer.loc[index_option, "Harbor"]
                period_ship_option = beta_customer.loc[index_option, "Period"] - 1
                period_arrive_option = int(period_ship_option + omega[harbor_option-1][customer])

                # check if shipment can be on time
                if previous_period_shipment + 1 <= period_ship_option:
                    index_option = beta_customer.index[option]
                    harbor_option = beta_customer.loc[index_option, "Harbor"]
                    period_ship_option = beta_customer.loc[index_option, "Period"] - 1
                    period_arrive_option = int(period_ship_option + omega[harbor_option-1][customer])
                
                    w_hat[product,factory,harbor_option-1,customer,previous_period_shipment] = w_hat[product,factory,harbor_option-1,customer,previous_period_shipment] + demand_to_meet
                    lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1), "Demand_met"] = lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1), "Demand_met"] + demand_to_meet
                    lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1), "Mask_met_demand"] = True
                    demand_to_meet = 0
                    
                    break
            
    return z_hat, w_hat, lambda_    


# repair operator #2: Send by ship
def send_by_ship(z_hat, w_hat, lambda_, d_i_l, delta_i_l, b, x, x_hat, beta, omega, Set_t, origin_factory, previous_period_shipment):
    
    lambda_to_meet = lambda_[(lambda_["Mask_met_demand"] == False) & (lambda_["Value"] > 0)] # filter demand not met
    
    for row in range(len(lambda_to_meet)):
        
        index = lambda_to_meet.index[row] # extract index because when sort they have another index
        
        # extract demand to meet
        demand_to_meet = lambda_to_meet.loc[index, "Value"]
        demand_allocated = lambda_to_meet.loc[index, "Demand_met"]
        demand_to_meet = demand_to_meet - demand_allocated
        
        # extract indexes
        product = lambda_to_meet.loc[index, "Product"] - 1
        customer = lambda_to_meet.loc[index, "Customer"] - 1
        period = lambda_to_meet.loc[index, "Period"] - 1
        
        # check location of factory where inventory is available
        location = np.where(x_hat[origin_factory.item(), :, period] == 1) 
        factory = origin_factory.item()
        
        # find the soonest ship scheduled
        beta_customer = beta[(beta["Customer"] == customer + 1) & (beta["Period"] > previous_period_shipment.item() + 1) & (beta["Value"] == 1)]
        beta_customer = beta_customer.sort_values(by='Period', ascending=True)
            
        # allocate the demand to the soonest feasible ship schedules
        for option in range(len(beta_customer)):
                                    
            index_option = beta_customer.index[option]
            harbor_option = beta_customer.loc[index_option, "Harbor"]
            period_ship_option = beta_customer.loc[index_option, "Period"] - 1
            period_arrive_option = int(period_ship_option + omega[harbor_option-1][customer])
                                    
            # check if truck can be on time
            if previous_period_shipment + 1 <= period_ship_option:
                w_hat[product,factory,harbor_option-1,customer,previous_period_shipment] = w_hat[product,factory,harbor_option-1,customer,previous_period_shipment] + demand_to_meet
                lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1), "Demand_met"] = lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1), "Demand_met"] + demand_to_meet
                lambda_.loc[(lambda_["Product"]== product + 1) & (lambda_["Customer"]== customer + 1) & (lambda_["Period"]== period + 1), "Mask_met_demand"] = True
                demand_to_meet = 0
                    
                break
    
    return z_hat, w_hat, lambda_


# update and repair solution for all variables
def update_repair_solution(solution,z_hat,w_hat,lambda_,delta_i_l,beta,omega,eta,d_nodes,locations,customers,gamma,tau,Max_Time,Set_i,Set_j,Set_p,Set_l,Set_h,Set_k,Set_t):
    

    # extract variables    
    x = solution.x
    y_hat = solution.y_hat
    s = solution.s
    w = solution.w
    u = solution.u
    f = solution.f
    x_hat = solution.x_hat
    n = solution.n
    z = solution.z
    b = solution.b
    e = solution.e
    u_hat = solution.u_hat
    m_hat = solution.m_hat
    m = np.zeros((Set_p, Set_k, Set_l, Set_t)).astype(int)
    
    
    # check for each period
    for t in range(1,Set_t):
        
        # update z initially for check drone constraints
        for h in range(Set_h):
            for j in range(Set_j):
                for l in range (Set_l):
                        
                    # find location of factory
                    location_of_factory = int(np.where(x_hat[j,:,t] == 1)[0])
                            
                    # check if there are shipments
                    if np.sum(z_hat[:,h,j,l,t]) > 0:
                        z[h,j,location_of_factory,l,t] = 1
                    else:
                        z[h,j,location_of_factory,l,t] = 0
        
        # update s variable for routes for check drone constraints
        z_check_routes = df_creation_five_index(z, names=["Drone","Factory","Location","Customer","Period","Value"])
        s_check_routes = initial_routes(z_check_routes, locations, customers, Set_h, Set_t)
        
         
        # check capacity of drones
        for h in range(Set_h):
        
            # check if there are shipments this day
            if np.sum(z_hat[:,h,:,:,t]) > 0:
                
                product, factory, customer = np.where(z_hat[:,h,:,:,t] > 0) # extract products, factories, and customers with shipments
                
                j = list(set(factory)) # create index for factory
                location_drone = np.where(b[h,:,t] == 1)[0] # extract location of the drone
                location_factory = np.where(x_hat[j,:,t] == 1)[0] # extract location of the factory
                
                drone_capacity = np.sum(eta * np.sum(z_hat[:,h,j,:,t], axis = 2)[0])
                node_1, node_2 = np.where(s_check_routes[h,:,:,t] == 1) # extract nodes for distance of routes
                total_flight_time = np.sum(d_nodes[node_1,node_2]) / gamma
            
                customer_mask = np.ma.array(customer, mask=False)
                
                # check that the capacities are met
                while drone_capacity > tau or total_flight_time > Max_Time:
                    
                    valid_indices = np.where(~customer_mask.mask)[0]
                    selected_customer = np.random.choice(valid_indices) # select a random customer
                    
                    # update amounts
                    # check range and no relocations
                    location_factory_next_day = np.where(x_hat[j,:,t+1] == 1)[0] # extract location of the factory next day
                    location_drone_next_day = np.where(b[h,:,t+1] == 1)[0] # extract location of the drone next day
                    if location_factory_next_day == location_drone_next_day and delta_i_l[location_factory_next_day,customer[selected_customer]] == 1 and np.sum(x[j,location_factory_next_day,:,t+1]) == 0:
                        
                        z_hat[product[selected_customer],h,j,customer[selected_customer],t+1] = z_hat[product[selected_customer],h,j,customer[selected_customer],t+1] + z_hat[product[selected_customer],h,j,customer[selected_customer],t]
                        z_hat[product[selected_customer],h,j,customer[selected_customer],t] = 0
                        customer_mask.mask[selected_customer] = True
                    
                    else:
                        # ship by ship
                        # find the soonest ship scheduled
                        beta_customer = beta[(beta["Customer"] == customer[selected_customer] + 1) & (beta["Period"] > t + 1) & (beta["Value"] == 1)]
                        beta_customer = beta_customer.sort_values(by='Period', ascending=True)
                            
                        # allocate the demand to the soonest feasible ship schedules
                        for option in range(len(beta_customer)):
                                                    
                            index_option = beta_customer.index[option]
                            harbor_option = beta_customer.loc[index_option, "Harbor"]
                            period_ship_option = beta_customer.loc[index_option, "Period"] - 1
                            period_arrive_option = int(period_ship_option + omega[harbor_option-1][customer[selected_customer]])
                                                    
                            # check if truck can be on time
                            if t + 1 <= period_ship_option:
                                w_hat[product[selected_customer],j,harbor_option-1,customer[selected_customer],t] = w_hat[product[selected_customer],j,harbor_option-1,customer[selected_customer],t] + z_hat[product[selected_customer],h,j,customer[selected_customer],t]
                                z_hat[product[selected_customer],h,j,customer[selected_customer],t] = 0
            
                                break
                
                    # update z under this change
                    # check if there are shipments
                    if np.sum(z_hat[:,h,j,customer[selected_customer],t]) > 0:
                        z[h,j,location_factory,customer[selected_customer],t] = 1
                    else:
                        z[h,j,location_factory,customer[selected_customer],t] = 0
        
                    # update s variable for routes for check drone constraints
                    z_check_routes = df_creation_five_index(z, names=["Drone","Factory","Location","Customer","Period","Value"])
                    s_check_routes = initial_routes(z_check_routes, locations, customers, Set_h, Set_t)
                        
                    # update capacities
                    drone_capacity = np.sum(eta * np.sum(z_hat[:,h,j,:,t], axis = 2)[0])
                    node_1, node_2 = np.where(s_check_routes[h,:,:,t] == 1) # extract nodes for distance of routes
                    total_flight_time = np.sum(d_nodes[node_1,node_2]) / gamma
                    
                
        # check availability of inventory
        for p in range(Set_p):
            for j in range(Set_j):
                if np.sum(z_hat[p,:,j,:,t]) + np.sum(w_hat[p,j,:,:,t]) > n[p,j,t-1]:
                        
                    difference = np.sum(z_hat[p,:,j,:,t]) + np.sum(w_hat[p,j,:,:,t]) - n[p,j,t-1]
                    location = np.where(x_hat[j,:,t] == 1)[0] # extract location of the factory
                    
                    if np.sum(z_hat[p,:,j,:,t]) > 0 and np.sum(x[j,location,:,t]) == 0:
                        
                        drone, customer = np.where(z_hat[p,:,j,:,t] > 0) # extract drone and customer that have shipments this day
                        customer_mask = np.ma.array(customer, mask=False) # create mask to track customers
                        
                        while difference > 0:
                            # check that there are customers to keep trying to ship by drone to next day
                            valid_indices = np.where(~customer_mask.mask)[0]
                            if valid_indices.size > 0:
                                selected_customer = np.random.choice(valid_indices) # select a random customer
                            else:
                                break
                        
                            units_to_ship = np.minimum(z_hat[p,drone[selected_customer],j,customer[selected_customer],t], difference)
                            
                            # update variables
                            location_factory_next_day = np.where(x_hat[j,:,t+1] == 1)[0] # extract location of the factory next day
                            location_drone_next_day = np.where(b[drone[selected_customer],:,t+1] == 1)[0] # extract location of the drone next day
                            if location_factory_next_day == location_drone_next_day and delta_i_l[location_factory_next_day,customer[selected_customer]] == 1 and np.sum(x[j,location_factory_next_day,:,t+1]) == 0:    
                                
                                z_hat[p,drone[selected_customer],j,customer[selected_customer],t+1] = z_hat[p,drone[selected_customer],j,customer[selected_customer],t+1] + units_to_ship
                                z_hat[p,drone[selected_customer],j,customer[selected_customer],t] = z_hat[p,drone[selected_customer],j,customer[selected_customer],t] - units_to_ship
                                customer_mask.mask[selected_customer] = True
                                difference = difference - units_to_ship
                            
                            else:
                                # ship by ship
                                # find the soonest ship scheduled
                                beta_customer = beta[(beta["Customer"] == customer[selected_customer] + 1) & (beta["Period"] > t + 1) & (beta["Value"] == 1)]
                                beta_customer = beta_customer.sort_values(by='Period', ascending=True)
                                    
                                # allocate the demand to the soonest feasible ship schedules
                                for option in range(len(beta_customer)):
                                                            
                                    index_option = beta_customer.index[option]
                                    harbor_option = beta_customer.loc[index_option, "Harbor"]
                                    period_ship_option = beta_customer.loc[index_option, "Period"] - 1
                                    period_arrive_option = int(period_ship_option + omega[harbor_option-1][customer[selected_customer]])
                                                            
                                    # check if truck can be on time
                                    if t + 1 <= period_ship_option:
                                        w_hat[p,j,harbor_option-1,customer[selected_customer],t+1] = w_hat[p,j,harbor_option-1,customer[selected_customer],t+1] + units_to_ship
                                        z_hat[p,drone[selected_customer],j,customer[selected_customer],t] = z_hat[p,drone[selected_customer],j,customer[selected_customer],t] - units_to_ship
                                        customer_mask.mask[selected_customer] = True
                                        difference = difference - units_to_ship
                                        break
                            
                                    
                    if difference > 0:
                
                        # select a shipment by ship
                        harbor, customer = np.where(w_hat[p,j,:,:,t] > 0) # extract harbor and customer that have shipments this day
                        customer_mask = np.ma.array(customer, mask=False) # create mask to track customers
                        
                        while difference > 0:
                        
                            # check that there are customers to keep trying to ship by drone to next day
                            valid_indices = np.where(~customer_mask.mask)[0]
                            if valid_indices.size > 0:
                                selected_customer = np.random.choice(valid_indices) # select a random customer
                            else:
                                break
                            
                            units_to_ship = np.minimum(w_hat[p,j,harbor[selected_customer],customer[selected_customer],t], difference)
                            
                            # find the soonest ship scheduled
                            beta_customer = beta[(beta["Customer"] == customer[selected_customer] + 1) & (beta["Period"] > t + 1) & (beta["Value"] == 1)]
                            beta_customer = beta_customer.sort_values(by='Period', ascending=True)
                
                            # allocate the demand to the soonest feasible ship schedules
                            for option in range(len(beta_customer)):
                                        
                                index_option = beta_customer.index[option]
                                harbor_option = beta_customer.loc[index_option, "Harbor"]
                                period_ship_option = beta_customer.loc[index_option, "Period"] - 1
                                period_arrive_option = int(period_ship_option + int(omega[harbor_option-1][customer[selected_customer]]))
                                
                                # check if truck can be on time
                                if t + 2 <= period_ship_option:
                                    w_hat[p,j,harbor_option-1,customer[selected_customer],t+1] = w_hat[p,j,harbor_option-1,customer[selected_customer],t+1] + units_to_ship
                                    w_hat[p,j,harbor[selected_customer],customer[selected_customer],t] = w_hat[p,j,harbor[selected_customer],customer[selected_customer],t] - units_to_ship
                                    customer_mask.mask[selected_customer] = True
                                    difference = difference - units_to_ship
                                    break
                
                    if difference > 0:
                        # select a drone shipment to ship by ship
                        drone, customer = np.where(z_hat[p,:,j,:,t] > 0) # extract drone and customer that have shipments this day
                        customer_mask = np.ma.array(customer, mask=False) # create mask to track customers
                        
                        while difference > 0:
                            # check that there are customers to keep trying to ship by drone to next day
                            valid_indices = np.where(~customer_mask.mask)[0]
                            if valid_indices.size > 0:
                                selected_customer = np.random.choice(valid_indices) # select a random customer
                            else:
                                break
                        
                            units_to_ship = np.minimum(z_hat[p,drone[selected_customer],j,customer[selected_customer],t], difference)
                            
                            # find the soonest ship scheduled
                            beta_customer = beta[(beta["Customer"] == customer[selected_customer] + 1) & (beta["Period"] > t + 1) & (beta["Value"] == 1)]
                            beta_customer = beta_customer.sort_values(by='Period', ascending=True)
                
                            # allocate the demand to the soonest feasible ship schedules
                            for option in range(len(beta_customer)):
                                        
                                index_option = beta_customer.index[option]
                                harbor_option = beta_customer.loc[index_option, "Harbor"]
                                period_ship_option = beta_customer.loc[index_option, "Period"] - 1
                                period_arrive_option = int(period_ship_option + int(omega[harbor_option-1][customer[selected_customer]]))
                                
                                # check if truck can be on time
                                if t + 2 <= period_ship_option:
                                    w_hat[p,j,harbor_option-1,customer[selected_customer],t+1] = w_hat[p,j,harbor_option-1,customer[selected_customer],t+1] + units_to_ship
                                    z_hat[p,drone[selected_customer],j,customer[selected_customer],t] = z_hat[p,drone[selected_customer],j,customer[selected_customer],t] - units_to_ship
                                    customer_mask.mask[selected_customer] = True
                                    difference = difference - units_to_ship
                                    
                                    break
                            
    
                # update inventory
                n[p,j,t] = n[p,j,t-1] + y_hat[p,j,t] - np.sum(z_hat[p,:,j,:,t]) - np.sum(w_hat[p,j,:,:,t])
        
        # update z
        for h in range(Set_h):
            for j in range(Set_j):
                for l in range (Set_l):
                    
                    # find location of factory
                    location_of_factory = int(np.where(x_hat[j,:,t] == 1)[0])
                        
                    # check if there are shipments
                    if np.sum(z_hat[:,h,j,l,t]) > 0:
                        z[h,j,location_of_factory,l,t] = 1
                    else:
                        z[h,j,location_of_factory,l,t] = 0
        
        
        # update w
        for j in range(Set_j):
            for k in range(Set_k):
                    
                # find location factory
                location_of_factory = int(np.where(x_hat[j,:,t] == 1)[0])
                    
                # check if there are shipments
                if np.sum(w_hat[:,j,k,:,t]) > 0:    
                    w[j,location_of_factory,k,t] = 1
                else:
                    w[j,location_of_factory,k,t] = 0
        
        
        # update u and u_hat
        for p in range(Set_p):
            for k in range(Set_k):
                for l in range(Set_l):
                    
                    # calculate inventory in each harbor
                    m[p,k,l,t] = m[p,k,l,t-1] + np.sum(w_hat[p,:,k,l,t-1])
        
                    #check if there is a ship sailing that day
                    beta_day = beta[(beta["Harbor"] == k + 1) & (beta["Customer"] == l + 1) & (beta["Period"] == t + 1) & (beta["Value"] == 1)]
    
                    if beta_day.shape[0] > 0 and m[p,k,l,t] > 0:
                        period_arrive = int(t + omega[k][l])
                        u[p,k,l,t] = m[p,k,l,t]
                        m[p,k,l,t] = m[p,k,l,t] - u[p,k,l,t]
                        u_hat[p,k,l,period_arrive] = u[p,k,l,t]
                        
                        
        # update m_hat
        for p in range(Set_p):
            for l in range(Set_l):
                m_hat[p,l,t] = m_hat[p,l,t-1] + np.sum(z_hat[p,:,:,l,t]) + np.sum(u_hat[p,:,l,t]) 
                
        
        # update f f_plgt
        for p in range(Set_p):
            for l in range(Set_l):
                for t_2 in range(t + 1):
                        
                    if t_2 > 0:
                        accumulated_demand = lambda_[lambda_["Period"] < t_2 + 1]
                        accumulated_demand = accumulated_demand.drop(columns=["Cluster", "Period", "Demand_met", "Mask_met_demand"], axis=1)
                        accumulated_demand = accumulated_demand.groupby(["Product", "Customer"], as_index=False).sum()
                        accumulated_demand_product = accumulated_demand.loc[(accumulated_demand["Product"]== p + 1) & (accumulated_demand["Customer"]== l + 1), "Value"].values[0]
                    else:
                        accumulated_demand_product = 0
                        
                    demand_day = lambda_.loc[(lambda_["Product"]== p + 1) & (lambda_["Customer"]== l + 1) & (lambda_["Period"]== t_2 + 1), "Value"].values[0]
                    
                    # differences in demands
                    difference = demand_day - m_hat[p][l][t] + accumulated_demand_product
                    
                    if difference > 0:
                        f[p][l][t_2][t] = difference
    
        # update s                        
        z_routes = df_creation_five_index(z, names=["Drone","Factory","Location","Customer","Period","Value"])
        s = initial_routes(z_routes, locations, customers, Set_h, Set_t)
                        
    
    # update solution
    solution.s = s 
    solution.w = w
    solution.u = u
    solution.f = f
    solution.n = n
    solution.z = z 
    solution.z_hat = z_hat
    solution.w_hat = w_hat
    solution.u_hat = u_hat
    solution.m_hat = m_hat
    
    return solution


# define class for execution of ALNS
class ALNS:
    def __init__(self, initial_solution, destroy_operators, repair_operators, weights_destroy, weights_repair, updating_period, alpha_sa, T_0, max_time_alns, seed, seed_sa):
        self.current_solution = initial_solution.copy()
        self.bestSolution = initial_solution.copy()
        self.obtainedSolution = initial_solution.copy()
        self.destroy_operators = destroy_operators
        self.repair_operators = repair_operators 
        self.weights_destroy = weights_destroy
        self.weights_repair = weights_repair
        self.p_destroy = weights_destroy / np.sum(weights_destroy)
        self.p_repair = weights_repair / np.sum(weights_repair)
        self.updating_period = updating_period
        self.alpha_sa = alpha_sa
        self.T = T_0
        self.max_time_alns = max_time_alns
        self.rng_choice = np.random.default_rng(seed=seed)
        self.rng_uniform = np.random.default_rng(seed=seed_sa)
      
    def run(self):
        
        print("\n")
        print("Starting ALNS")
        print("\n")
        
        #print("Weights destroy:", self.weights_destroy)
        #print("Weights repair:", self.weights_repair)
        
        execution_start_time = datetime.now() # start time
        iteration_time = datetime.now()
        execution_time = (iteration_time-execution_start_time).total_seconds() /60
        
        
        iteration = 0
        #while execution_time < self.max_time_alns:
        while iteration < 221:
            
            iteration += 1
            print("Iteration: ", iteration)
            
            #if iteration == 87:
            #    pdb.set_trace()
            
            # select a destroy operator and repair operator
            selected_destroy = self.rng_choice.choice(len(self.destroy_operators), p=self.p_destroy)
            selected_repair = self.rng_choice.choice(len(self.repair_operators), p=self.p_repair)
            
            # apply destroy operators to solution
            solution = self.current_solution.copy()
            f = solution.f
            z_hat = solution.z_hat
            w_hat = solution.w_hat
            lambda_ = solution.lambda_
            
            # check feasibility operators
            valid_operator = False
            while valid_operator == False:
                
                if selected_destroy == 0:
                    feasibility = feasibility_deallocate_based_f(f,z_hat,w_hat)
                    if feasibility == 0:
                        selected_destroy = self.rng_choice.choice(len(self.destroy_operators), p=self.p_destroy)
                    else:
                        valid_operator = True
                    
                if selected_destroy == 1:
                    nonzero_indices = np.argwhere(z_hat > 0)
                    if nonzero_indices.shape[0] == 0:
                        selected_destroy = self.rng_choice.choice(len(self.destroy_operators), p=self.p_destroy)
                    else:
                        valid_operator = True
                
                if selected_destroy == 2: 
                    valid_operator = True
                
                
            z_hat_iter = df_creation_five_index(z_hat, names=["Product","Drone","Factory","Customer","Period","Value"])
            w_hat_iter = df_creation_five_index(w_hat, names=["Product","Factory","Harbor","Customer","Period","Value"])
            n_iter = df_creation_three_index(solution.n, names=["Product","Factory","Period","Value"])

            
            z_hat, w_hat, lambda_, origin_factory, previous_period_shipment = self.destroy_operators[selected_destroy](f,z_hat,w_hat,lambda_)
            
            z_hat_iter = df_creation_five_index(z_hat, names=["Product","Drone","Factory","Customer","Period","Value"])
            w_hat_iter = df_creation_five_index(w_hat, names=["Product","Factory","Harbor","Customer","Period","Value"])

            
            # apply repair operator
            d_i_l = solution.evaluation_parameters[12]
            delta_i_l = solution.evaluation_parameters[13]
            beta = solution.evaluation_parameters[14] 
            omega = solution.evaluation_parameters[15]
            Set_t = solution.evaluation_parameters[27]
            b = solution.b
            x = solution.x
            x_hat = solution.x_hat 
            
            z_hat, w_hat, lambda_ = self.repair_operators[selected_repair](z_hat, w_hat, lambda_, d_i_l, delta_i_l, b, x, x_hat, beta, omega, Set_t, origin_factory, previous_period_shipment)
            
            z_hat_iter = df_creation_five_index(z_hat, names=["Product","Drone","Factory","Customer","Period","Value"])
            w_hat_iter = df_creation_five_index(w_hat, names=["Product","Factory","Harbor","Customer","Period","Value"])

            
            # update obtained solution
            eta = solution.evaluation_parameters[16]
            d_nodes = solution.evaluation_parameters[17]
            locations = solution.evaluation_parameters[18]
            customers = solution.evaluation_parameters[7] 
            gamma = solution.evaluation_parameters[19] 
            Set_p = solution.evaluation_parameters[5]
            tau = solution.evaluation_parameters[20]
            Max_Time = solution.evaluation_parameters[21]
            Set_i = solution.evaluation_parameters[22]
            Set_j = solution.evaluation_parameters[23]
            Set_l = solution.evaluation_parameters[24]
            Set_h = solution.evaluation_parameters[25]
            Set_k = solution.evaluation_parameters[26]
            
            self.obtainedSolution = update_repair_solution(solution,z_hat,w_hat,lambda_,delta_i_l,beta,omega,eta,d_nodes,locations,customers,gamma,tau,Max_Time,Set_i,Set_j,Set_p,Set_l,Set_h,Set_k,Set_t)
            
            z_hat_iter = df_creation_five_index(z_hat, names=["Product","Drone","Factory","Customer","Period","Value"])
            w_hat_iter = df_creation_five_index(w_hat, names=["Product","Factory","Harbor","Customer","Period","Value"])
            print("Total demand:",np.sum(z_hat) + np.sum(w_hat))
            
            # check if improves or use simulated annealing
            print("Current solution:", self.current_solution.objective())
            print("Obtained solution:", self.obtainedSolution.objective())
            print("Best solution:", self.bestSolution.objective())
            if self.obtainedSolution.objective() <= self.bestSolution.objective():
                self.bestSolution = self.obtainedSolution.copy()
                self.current_solution = self.obtainedSolution.copy()
                self.weights_destroy[selected_destroy] = self.weights_destroy[selected_destroy] + 1 
                self.weights_repair[selected_repair] = self.weights_repair[selected_repair] + 1
            
            else:
                if self.rng_uniform.uniform(0.0, 1.0) <= np.exp(-((self.obtainedSolution.objective()-self.current_solution.objective())/self.T)):
                    self.current_solution = self.obtainedSolution.copy()
            
            # check if it is moment to update the temperature
            if iteration % self.updating_period == 0:
            
                # update scores
                self.p_destroy = self.weights_destroy / np.sum(self.weights_destroy)
                self.p_repair = self.weights_repair / np.sum(self.weights_repair)
                
                #update temperature
                self.T = self.alpha_sa * self.T
                
                
            # update time
            iteration_time = datetime.now()
            execution_time = (iteration_time-execution_start_time).total_seconds() /60
            print("Execution time:", execution_time)
            print("\n")
            
        return self.bestSolution
    