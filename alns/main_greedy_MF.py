import pandas as pd
import numpy as np
from functions_greedy_MF import *
from initialization_routes import *

def greedy_initial_solution(parameters,locations,customers,harbors,beta,lambda_,eta,theta,alpha,multiplier):
    
    # define sets
    Set_i = len(locations)
    Set_j = 1 if theta.ndim < 2 else len(theta)
    Set_p = 1 if alpha.ndim == 0 else len(alpha)
    Set_l = len(customers)
    Set_h = int(parameters[0][1])
    Set_k = len(harbors)
    Set_t = int(parameters[1][1])
    
    # define parameters
    CR_f = parameters[2][1] # fixed relocation cost for moving a factory
    CR_v = parameters[3][1] # variable relocation cost per kilometer for moving a factory
    CP_f = parameters[4][1] # set-up cost to produce at any factory
    CT = parameters[5][1] # transport cost per kilometer for shipping by drone
    CT1 = parameters[6][1] # transport cost for shipping by land per kilometer
    CT2 = parameters[7][1] # fixed cost for shipping by ship in any period
    CB_ini = parameters[23][1] # penalization cost per unit per period
    Max_Area = parameters[13][1] # maximum cross-sectional area available for batching in a built
    tau = parameters[14][1] # capacity in product weight of a drone
    gamma = parameters[15][1] # flying speed of drones in kilometers per hour
    Max_Time = parameters[16][1] # maximum allowed drone route time per day in hours
    max_delta = parameters[17][1] # maximum distance a drone can travel
    speed_ship = parameters[18][1] # speed of ships
    eta = eta # weight of product p
    d_i_l = distances(locations, customers) # distance from locations to customers
    delta_i_l = delta_calculation(d_i_l, max_delta) # binary matrix if customer l is in drone coverage from location i
    theta = theta.reshape(max(Set_j, 1), Set_p) # capability of factory j to produce product p
    alpha = alpha # cross-sectional area of product p
    omega = calculation_omega(customers, harbors, speed_ship) # duration of shipment from intermediary k to customer l
    lambda_ = pd.DataFrame(lambda_, columns=["Product", "Customer", "Cluster", "Period", "Value"])  # change lambda to dataframe to filter easily
    beta = pd.DataFrame(beta, columns=["Harbor", "Customer", "Cluster", "Period", "Value"])  # change beta to dataframe to filter easily
    
    # initialize other parameters
    x_factory_origin_destination_period = np.zeros((Set_j, Set_i, Set_i, Set_t)).astype(int) # Binary variable if mobile factory j∈J is relocated from location i∈I to location g∈I in day t∈T
    x_hat_factory_location_period = np.zeros((Set_j, Set_i, Set_t)).astype(int) # Binary variable if mobile factory j∈J is at location i∈I at the beginning of day t∈T
    y_hat_product_factory_period = np.zeros((Set_p, Set_j, Set_t)).astype(int) # Units of part p that mobile factory j∈J produces in day t∈T
    n_product_factory_period = np.zeros((Set_p, Set_j, Set_t)).astype(int) # Units of part p∈P in inventory at mobile factory j∈J in day t∈T 
    b_drone_location_period = np.zeros((Set_h, Set_i, Set_t)).astype(int) # Binary variable if drone h∈H is in location i∈I at the beginning of day t∈T
    e_drone_location_period = np.zeros((Set_h, Set_i, Set_t)).astype(int) # Binary variable if drone h∈H is in location i∈I at the end of day t∈T
    z_drone_factory_location_customer_period = np.zeros((Set_h, Set_j, Set_i, Set_l, Set_t)).astype(int) # Binary variable if drone h∈H goes from factory j∈J at location i∈I to customer l∈L in day t∈T
    z_hat_product_drone_factory_customer_period = np.zeros((Set_p, Set_h, Set_j, Set_l, Set_t)).astype(int) # Units of part p∈P to ship by drone h∈H from the mobile factory j∈J to customer l∈L in day t∈T
    w_factory_location_harbor_period = np.zeros((Set_j, Set_i, Set_k, Set_t)).astype(int) # Binary variable if mobile factory j∈J at location i∈I sends parts to harbor k∈K in day t∈T
    w_hat_product_factory_harbor_customer_period = np.zeros((Set_p, Set_j, Set_k, Set_l, Set_t)).astype(int) # Units of part p∈P to transport by truck from mobile factory j∈J to harbor k∈K for customer l∈L in day t∈T
    u_product_harbor_customer_period = np.zeros((Set_p, Set_k, Set_l, Set_t)).astype(int) # Units of part p∈P to ship from harbor k∈K to customer l∈L in day t∈T
    u_hat_product_harbor_customer_period = np.zeros((Set_p, Set_k, Set_l, Set_t)).astype(int) # Units of part p∈P to receive from harbor k∈K to customer l∈L in day t∈T
    m_hat_product_customer_period = np.zeros((Set_p, Set_l, Set_t)).astype(int) # Accumulation of units of part p∈P received by customer l∈L in day t∈T
    f_product_customer_duedate_period = np.zeros((Set_p, Set_l, Set_t, Set_t)).astype(int) # Units of part p∈P unfulfilled from the demand of customer l∈L with due date a∈T in day t∈T 
    
    lambda_['Demand_met'] = 0
    lambda_['Mask_met_demand'] = False

    # create ranges
    demand_days = parameters[19][1]  # number of days with due dates to schedule in the decomposition of the second stage
    ranges = int(np.floor(int(Set_t) / demand_days))  # number of sub-routing models to run
    
    cuts = []  # array to save the start of the range, the days with due dates, and the rolling horizon
    demand = 0
    for t in range(ranges):
        start = demand + 1
        demand += demand_days
        
        if demand + demand_days <= int(Set_t):
            end = demand + demand_days
        else:
            end = int(Set_t)
    
        cuts.append([start, demand, end])
    
    #########################################################################################################################################################################################################################################################################################################################
    
    
    
    #########################################################################################################################################################################################################################################################################################################################
    # Process per week
    #########################################################################################################################################################################################################################################################################################################################
    
    for week in range(len(cuts)):
        
        # filter demand
        lambda_cut = lambda_[(lambda_["Period"] >= cuts[week][0]) & (lambda_["Period"] <= cuts[week][2])]
        lambda_cut = lambda_cut.drop(columns=["Cluster", "Period"], axis=1)
        lambda_cut = lambda_cut.groupby(["Customer", "Product"], as_index=False).sum()
        lambda_cut['Mask_coverage'] = False
           
        # first part to locate all factories
        used_locations = []
        located_factories = []
        all_factories_located_check = False
        while all_factories_located_check == False:
            
            
            #Step 1: Compute scores and allocate
            #########################################################################################################################################################################################################################################################################################################################
            
            scores = np.zeros((Set_i, Set_j)) # initialize scores
            for i in range(Set_i):
                for j in range(Set_j):
                    
                    score = 0
                    # check if the location does not have another factory
                    if (i not in used_locations) and (j not in located_factories):
                    #int(np.sum(x_hat_factory_location_period[:,i,int(cuts[week][0]-1)])) == 0 and int(np.sum(x_hat_factory_location_period[j,:, int(cuts[week][0]-1)])) == 0:
                        for l in range(Set_l):
                            for p in range(Set_p):
                                
                                # check if the demand was covered or not
                                if lambda_cut.loc[(lambda_cut["Product"] == p + 1) & (lambda_cut["Customer"] == l + 1), "Mask_coverage"].iloc[0]  == False:
                                    lambda_value = (lambda_cut.loc[(lambda_cut["Product"] == p + 1) & (lambda_cut["Customer"] == l + 1), "Value"]).iloc[0] 
                                else:
                                    lambda_value = 0
                                    
                                score += lambda_value * theta[j][p] * delta_i_l[i][l]
                    else:
                        score += 0
                            
                    scores[i][j] = score *(1 + multiplier * x_hat_factory_location_period[j][i][int(cuts[week][0]-1)]) # update score for each location and factory
            
            
            #Step 2: Localize factories
            #########################################################################################################################################################################################################################################################################################################################
            
            # localize factory
            demand_exists = (scores > 0).any()
            max_score = np.unravel_index(np.argmax(scores), scores.shape) # find the maximum score
            relocation = False # track relocation to move drone too
            
            # check if there is score for any factory, otherwise there cannot be relocation
            if demand_exists == True:
                
                # check if factory was not localized there yet
                if week == 0:
                    x_hat_factory_location_period[max_score[1]][max_score[0]][int(cuts[week][0]-1)] = 1 # fill variable x
                else:
                    if x_hat_factory_location_period[max_score[1]][max_score[0]][int(cuts[week][0]-1)-1] == 1:
                        x_hat_factory_location_period[max_score[1]][max_score[0]][int(cuts[week][0]-1)] = 1
                    else:
                        relocation = True
                        origin = np.where(x_hat_factory_location_period[max_score[1], :, int(cuts[week][0]-1)-1] == 1)[0].item()
                        destination = max_score[0]
                        x_factory_origin_destination_period[max_score[1]][origin][destination][int(cuts[week][0]-1)] = 1
                        x_hat_factory_location_period[max_score[1]][origin][int(cuts[week][0]-1)] = 0
                        x_hat_factory_location_period[max_score[1]][max_score[0]][int(cuts[week][0]-1)] = 1
                
            
            # localize drone
            for h in range(Set_h):
                # check if there is no drone
                if np.sum(b_drone_location_period, axis=(1,2)) == 0 and np.sum(b_drone_location_period[h, max_score[0], cuts[week][0]]) == 0:
                    b_drone_location_period[h, max_score[0], cuts[week][0]-1] = 1
                
                else:
                    actual_location = np.where(b_drone_location_period[h,:,int(cuts[week][0]-1)])[0]
                    final_location = np.where(e_drone_location_period[h,:,int(cuts[week][0]-1)])[0]
                    
                    if relocation == True:
                        if origin == actual_location:
                            e_drone_location_period[h, max_score[0], int(cuts[week][0]-1)] = 1
                        else:
                            e_drone_location_period[h, final_location, int(cuts[week][0]-1)] = 1
                    else:
                        e_drone_location_period[h, actual_location, int(cuts[week][0]-1)] = 1
                        
                
            #Step 3: Update demand coverage
            #########################################################################################################################################################################################################################################################################################################################
            location_from_coverage = max_score[0]
            used_locations.append(location_from_coverage)
            located_factories.append(max_score[1])
            for l in range(Set_l):
                for p in range(Set_p):
                    if delta_i_l[location_from_coverage][l] == 1:
                        lambda_cut.loc[(lambda_cut["Product"] == p + 1) & (lambda_cut["Customer"] == l + 1), "Mask_coverage"] = True
            
            
            #Step 4: Check if there are more factories to locate
            #########################################################################################################################################################################################################################################################################################################################
            factory_check = len(located_factories)
            
            if factory_check == Set_j:     
                all_factories_located_check = True 
        
        used_locations.sort(reverse=False)
        
        
        #Step 5: Sort customer based on due dates
        #########################################################################################################################################################################################################################################################################################################################
        lambda_sorted_to_meet = lambda_[(lambda_["Period"] >= cuts[week][0]) & (lambda_["Period"] <= cuts[week][2]) & (lambda_["Value"] > 0)]
        lambda_sorted_to_meet = lambda_sorted_to_meet.sort_values(by='Period', ascending=True)
        
        
        #Step 6: Define units required
        #########################################################################################################################################################################################################################################################################################################################
        units_required = lambda_cut.drop(columns=["Customer", "Mask_met_demand", "Mask_coverage", "Demand_met"], axis=1)
        units_required = units_required.groupby(["Product"], as_index=False).sum()
      
        units_met = lambda_[(lambda_["Period"] >= cuts[week][0]) & (lambda_["Period"] <= cuts[week][2])]
        units_met = units_met.drop(columns=["Customer", "Cluster", "Period", "Mask_met_demand", "Value"], axis=1)
        units_met = units_met.groupby(["Product"], as_index=False).sum()
        
        available_inventory = np.sum(n_product_factory_period, axis=(1))
        available_inventory = available_inventory[:,int(cuts[week][0])]
        units_required["Value"] = units_required["Value"] - units_met["Demand_met"] - available_inventory
        
        #########################################################################################################################################################################################################################################################################################################################
        #Step 7: Process per day
        #########################################################################################################################################################################################################################################################################################################################
        if week == len(cuts)-1:
            final_t = int(cuts[week][2])
        else:
            final_t = int(cuts[week][1])
        
        for t in range(int(cuts[week][0]-1), final_t):
        
            #Step 7.1: Restart drone capacity
            #########################################################################################################################################################################################################################################################################################################################
            drone_capacity = np.zeros((Set_h))
            total_flight_time = np.zeros((Set_h))
            
            #Step 7.2: For each customer that demand has been not met
            #########################################################################################################################################################################################################################################################################################################################
            for l in range(len(lambda_sorted_to_meet)):
                
                index = lambda_sorted_to_meet.index[l] # extract index because when sort they have another index
                customer_to_meet = lambda_sorted_to_meet.loc[index, "Customer"] 
             
                #Step 7.2.1: Identify the closest factory to meet demand and decide how to ship
               
                # compute distances
                distance_l_used_locations = d_i_l[used_locations, customer_to_meet - 1]
                distance_l_used_locations = np.ma.array(distance_l_used_locations, mask=False)
                
                # for each factory 
                for j in range(len(used_locations)):
                    
                    min_dis_location_index = np.argmin(distance_l_used_locations)
                    closest_location = used_locations[min_dis_location_index]
                    closest_factory = int(np.where(x_hat_factory_location_period[:,closest_location,t] == 1)[0])
                    
                    # check if inventory available
                    product_to_meet = lambda_sorted_to_meet.loc[index, "Product"]
                  
                    if n_product_factory_period[product_to_meet-1][closest_factory][t] > 0 and lambda_sorted_to_meet.loc[index,"Mask_met_demand"] == False:
                        
                        # allocate inventory
                        current_inventory = n_product_factory_period[product_to_meet-1][closest_factory][t]
                        distance_l_used_locations.mask[min_dis_location_index] = True
                        difference = lambda_sorted_to_meet.loc[index,"Value"] - lambda_sorted_to_meet.loc[index,"Demand_met"]
                        demand_to_ship = np.minimum(difference, current_inventory)
                        
                        
                        # decide distribution if demand_to_ship greater than 0
                        if demand_to_ship > 0:
                        
                            # check by drone
                            # check if there is a drone available and the customer is in the range and if factory is not being relocated
                            if np.sum(b_drone_location_period[:, closest_location, t]) == 1 and delta_i_l[closest_location][customer_to_meet-1] == 1 and np.sum(x_factory_origin_destination_period[closest_factory,:,:,t]) == 0: 
                                
                                drone_available = np.where(b_drone_location_period[:, closest_location, t] == 1)[0].item() # find the drone that is available for this location
                                
                                # check capacity and time
                                if (drone_capacity[drone_available] + eta[product_to_meet-1] * demand_to_ship) < tau and (total_flight_time[drone_available] + (d_i_l[closest_location][customer_to_meet-1] / gamma)*2) < Max_Time:
                                    z_drone_factory_location_customer_period[drone_available][closest_factory][closest_location][customer_to_meet-1][t] = 1
                                    z_hat_product_drone_factory_customer_period[product_to_meet-1][drone_available][closest_factory][customer_to_meet-1][t] = z_hat_product_drone_factory_customer_period[product_to_meet-1][drone_available][closest_factory][customer_to_meet-1][t] + demand_to_ship
                                    lambda_sorted_to_meet.at[index,"Demand_met"] = lambda_sorted_to_meet.loc[index,"Demand_met"] + demand_to_ship
                                    n_product_factory_period[product_to_meet-1][closest_factory][t] = n_product_factory_period[product_to_meet-1][closest_factory][t] - demand_to_ship
                                    drone_capacity[drone_available] = drone_capacity[drone_available] + eta[product_to_meet-1] * demand_to_ship
                                    total_flight_time[drone_available] = total_flight_time[drone_available] + (d_i_l[closest_location][customer_to_meet-1] / gamma)*2
                                
                                else:
                                    # ship by ship
                                
                                    # find the soonest ship scheduled
                                    beta_customer = beta[(beta["Customer"] == customer_to_meet) & (beta["Value"] == 1)]
                                    beta_customer = beta_customer.sort_values(by='Period', ascending=True)
                                        
                                    # allocate the demand to the soonest feasible ship schedules
                                    for option in range(len(beta_customer)):
                                            
                                        index_option = beta_customer.index[option]
                                        harbor_option = beta_customer.loc[index_option, "Harbor"]
                                        period_ship_option = beta_customer.loc[index_option, "Period"] - 1
                                        period_arrive_option = int(period_ship_option + omega[harbor_option-1][customer_to_meet-1])
                                            
                                        # check if truck can be on time
                                        if t + 1 <= period_ship_option:
                                            w_factory_location_harbor_period[closest_factory][closest_location][harbor_option-1][t] = 1
                                            w_hat_product_factory_harbor_customer_period[product_to_meet-1][closest_factory][harbor_option-1][customer_to_meet-1][t] = w_hat_product_factory_harbor_customer_period[product_to_meet-1][closest_factory][harbor_option-1][customer_to_meet-1][t] + demand_to_ship
                                            u_product_harbor_customer_period[product_to_meet-1][harbor_option-1][customer_to_meet-1][period_ship_option] = u_product_harbor_customer_period[product_to_meet-1][harbor_option-1][customer_to_meet-1][period_ship_option] + demand_to_ship
                                            u_hat_product_harbor_customer_period[product_to_meet-1][harbor_option-1][customer_to_meet-1][period_arrive_option] = u_hat_product_harbor_customer_period[product_to_meet-1][harbor_option-1][customer_to_meet-1][period_arrive_option] + demand_to_ship
                                            lambda_sorted_to_meet.at[index,"Demand_met"] = lambda_sorted_to_meet.loc[index,"Demand_met"] + demand_to_ship
                                            n_product_factory_period[product_to_meet-1][closest_factory][t] = n_product_factory_period[product_to_meet-1][closest_factory][t] - demand_to_ship
                                            
                                            break
                                
                            # if drone not available then send by ship
                            else:
                                
                                # find the soonest ship scheduled
                                beta_customer = beta[(beta["Customer"] == customer_to_meet) & (beta["Value"] == 1)]
                                beta_customer = beta_customer.sort_values(by='Period', ascending=True)
                                
                                # allocate the demand to the soonest feasible ship schedules
                                for option in range(len(beta_customer)):
                                    
                                    index_option = beta_customer.index[option]
                                    harbor_option = beta_customer.loc[index_option, "Harbor"]
                                    period_ship_option = beta_customer.loc[index_option, "Period"] - 1
                                    period_arrive_option = int(period_ship_option + omega[harbor_option-1][customer_to_meet-1])
                                    
                                    # check if truck can be on time
                                    if t + 1 <= period_ship_option:
                                        w_factory_location_harbor_period[closest_factory][closest_location][harbor_option-1][t] = 1
                                        w_hat_product_factory_harbor_customer_period[product_to_meet-1][closest_factory][harbor_option-1][customer_to_meet-1][t] = w_hat_product_factory_harbor_customer_period[product_to_meet-1][closest_factory][harbor_option-1][customer_to_meet-1][t] + demand_to_ship
                                        u_product_harbor_customer_period[product_to_meet-1][harbor_option-1][customer_to_meet-1][period_ship_option] = u_product_harbor_customer_period[product_to_meet-1][harbor_option-1][customer_to_meet-1][period_ship_option] + demand_to_ship
                                        u_hat_product_harbor_customer_period[product_to_meet-1][harbor_option-1][customer_to_meet-1][period_arrive_option] = u_hat_product_harbor_customer_period[product_to_meet-1][harbor_option-1][customer_to_meet-1][period_arrive_option] + demand_to_ship
                                        lambda_sorted_to_meet.at[index,"Demand_met"] = lambda_sorted_to_meet.loc[index,"Demand_met"] + demand_to_ship
                                        n_product_factory_period[product_to_meet-1][closest_factory][t] = n_product_factory_period[product_to_meet-1][closest_factory][t] - demand_to_ship
                                        
                                        break
                                    
                    else:
                        #update checking factories
                        distance_l_used_locations.mask[min_dis_location_index] = True
                        
                    # check if demand was met or not
                    if lambda_sorted_to_meet.loc[index,"Value"] - lambda_sorted_to_meet.loc[index,"Demand_met"] == 0:
                        lambda_sorted_to_meet.loc[index,"Mask_met_demand"] = True
                        
                    # update demand in general parameter
                    lambda_.at[index,"Demand_met"] = lambda_sorted_to_meet.loc[index,"Demand_met"]
                    lambda_.at[index,"Mask_met_demand"] = lambda_sorted_to_meet.loc[index,"Mask_met_demand"]
                     
            # update m_hat variable
            for p in range(Set_p):
                for l in range(Set_l):
                    m_hat_product_customer_period[p][l][t] = m_hat_product_customer_period[p][l][t-1] +  np.sum(z_hat_product_drone_factory_customer_period[p,:,:,l,t]) + np.sum(u_hat_product_harbor_customer_period[p,:,l,t])
                    
                    # update of f variable
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
                        difference = demand_day - m_hat_product_customer_period[p][l][t] + accumulated_demand_product
                    
                        if difference > 0:
                            f_product_customer_duedate_period[p][l][t_2][t] = difference
            
                
            #Step 7.3: If there are units required to produce
            #########################################################################################################################################################################################################################################################################################################################
            
            # define production for each factory
            for j in range(Set_j):
                
                # check if factory is not being relocated 
                if np.sum(x_factory_origin_destination_period[closest_factory,:,:,t]) == 0:
                
                    #Step 7.3.1: Compute the demand proportion for each product 𝑝 of the units required
                    total = units_required["Value"] * pd.Series(theta[j,:])
                    total = total.sum()
                    
                    #Step 7.3.2. Use the proportion to split the build
                    if total > 0:
                        proportion = (units_required["Value"] / total) * pd.Series(theta[j])
                    else: 
                        proportion = np.zeros((2))
                    
                    # Step 7.3.3. Using the cross-sectional area of each product, compute how many units to produce of each product according to the proportion
                    area_build_product = Max_Area * proportion    
                    units_fit_product = np.floor(area_build_product / alpha)  
                    units_to_produce = np.minimum(units_required["Value"], units_fit_product)
                    
                    # Step 7.3.4. Update inventory and unit required
                    units_required["Value"] = units_required["Value"] - units_to_produce
                    units_required["Value"] = units_required["Value"].fillna(0)
                else:
                    units_to_produce = pd.Series([0,0])

                # update inventory and variable
                if t == 0:
                    for p in range(len(units_required)):
                        n_product_factory_period[p][j][t] = units_to_produce[p]
                        n_product_factory_period[p][j][t+1] = units_to_produce[p]
                        y_hat_product_factory_period[p][j][t] = units_to_produce[p]
                    
                if t > 0 and t < Set_t - 1:
                    for p in range(len(units_required)):
                        n_product_factory_period[p][j][t] = n_product_factory_period[p][j][t] + units_to_produce[p]
                        n_product_factory_period[p][j][t+1] = n_product_factory_period[p][j][t]
                        y_hat_product_factory_period[p][j][t] = units_to_produce[p]
                
                if t == Set_t:
                    for p in range(len(units_required)):
                        n_product_factory_period[p][j][t] = n_product_factory_period[p][j][t-1] + units_to_produce[p]
                        y_hat_product_factory_period[p][j][t] = units_to_produce[p]
       
            #Step 7.4: Update positions of factories and drones
            #########################################################################################################################################################################################################################################################################################################################
        
            if t < Set_t - 1:
                for j in range(Set_j):
                    for i in range(Set_i):
                        x_hat_factory_location_period[j][i][t+1] = x_hat_factory_location_period[j][i][t] 
            
                for h in range(Set_h):
                    for i in range(Set_i):
                        if t == 0:
                            e_drone_location_period[h][i][t] = b_drone_location_period[h][i][t]
                            b_drone_location_period[h][i][t+1] = e_drone_location_period[h][i][t]
                        else:
                            # check if factory is not being relocated 
                            if np.sum(x_factory_origin_destination_period[closest_factory,:,:,t]) == 0:
                                e_drone_location_period[h][i][t] = b_drone_location_period[h][i][t]
                                b_drone_location_period[h][i][t+1] = e_drone_location_period[h][i][t]
                            else:
                                b_drone_location_period[h][i][t+1] = e_drone_location_period[h][i][t]
                                
        #########################################################################################################################################################################################################################################################################################################################
        # End process per day
        #########################################################################################################################################################################################################################################################################################################################
    
    
    #########################################################################################################################################################################################################################################################################################################################
    # End process per week
    #########################################################################################################################################################################################################################################################################################################################
    
    
    
    # Create routes
    #########################################################################################################################################################################################################################################################################################################################
    z = df_creation_five_index(z_drone_factory_location_customer_period, names=["Drone","Factory","Location","Customer","Period","Value"])
    s_drone_origin_destination_period = initial_routes(z, locations, customers, Set_h, Set_t)
    
    
    # Compute costs and create dataframes all variables
    #########################################################################################################################################################################################################################################################################################################################
    
    # compute costs
    relocation_cost = relocation_cost_calculation(x_factory_origin_destination_period, locations, CR_f, CR_v)
    production_cost = production_cost_calculation(y_hat_product_factory_period, alpha, CP_f, Set_p)
    shipments_drone_cost = shipments_drone_cost_calculation(s_drone_origin_destination_period, CT, locations, customers)
    shipments_land_cost = shipments_land_cost_calculation(w_factory_location_harbor_period, CT1, locations, harbors)
    shipments_ship_cost = shipments_ship_cost_calculation(u_product_harbor_customer_period, CT2)
    penalties_cost = penalties_cost_calculation(f_product_customer_duedate_period, CB_ini)
    
    total_cost = relocation_cost + production_cost + shipments_drone_cost + shipments_land_cost + shipments_ship_cost + penalties_cost
    
    
    x = df_creation_four_index(x_factory_origin_destination_period, names=["Factory","Location_Origin","Location_Destination","Period","Value"])
    x_hat = df_creation_three_index(x_hat_factory_location_period, names=["Factory","Location","Period","Value"])
    y_hat = df_creation_three_index(y_hat_product_factory_period, names=["Product", "Factory", "Period", "Value"])
    n = df_creation_three_index(n_product_factory_period, names=["Product","Factory","Period","Value"])
    b = df_creation_three_index(b_drone_location_period, names=["Drone","Starting position","Period","Value"])
    e = df_creation_three_index(e_drone_location_period, names=["Drone","Ending position","Period","Value"])
    z = df_creation_five_index(z_drone_factory_location_customer_period, names=["Drone","Factory","Location","Customer","Period","Value"])
    z_hat = df_creation_five_index(z_hat_product_drone_factory_customer_period, names=["Product","Drone","Factory","Customer","Period","Value"])
    w = df_creation_four_index(w_factory_location_harbor_period, names=["Factory","Location","Harbor","Period","Value"])
    w_hat = df_creation_five_index(w_hat_product_factory_harbor_customer_period, names=["Product","Factory","Harbor","Customer","Period","Value"])
    u = df_creation_four_index(u_product_harbor_customer_period, names=["Product","Harbor","Customer","Period","Value"])
    u_hat = df_creation_four_index(u_hat_product_harbor_customer_period, names=["Product","Harbor","Customer","Period","Value"])
    f = df_creation_four_index(f_product_customer_duedate_period, names=["Product","Customer","Due date","Period","Value"])
    m_hat = df_creation_three_index(m_hat_product_customer_period, names=["Product", "Customer", "Period", "Value"])
    s = df_creation_four_index(s_drone_origin_destination_period, names=["Drone","Origin","Destination","Period","Value"])
    
    
    
    # Print results
    #########################################################################################################################################################################################################################################################################################################################
    
    # print cvs with variables
    x.to_csv("x.csv", index=False)
    x_hat.to_csv("x_hat.csv", index=False)
    y_hat.to_csv("y_hat.csv", index=False)
    n.to_csv("n.csv", index=False)
    b.to_csv("b.csv", index=False)
    e.to_csv("e.csv", index=False)
    z.to_csv("z.csv", index=False)
    z_hat.to_csv("z_hat.csv", index=False)
    w.to_csv("w.csv", index=False)
    w_hat.to_csv("w_hat.csv", index=False)
    u.to_csv("u.csv", index=False)
    u_hat.to_csv("u_hat.csv", index=False)
    f.to_csv("f.csv", index=False)
    m_hat.to_csv("m_hat.csv", index=False)
    s.to_csv("s.csv", index=False)
    
    # summary of decisions
    
    number_of_relocations = x[x.Value > 0].shape[0]
    
    number_of_times_production = y_hat[y_hat.Value > 0]
    number_of_times_production = number_of_times_production.groupby(["Factory", "Period"])["Value"].count()
    number_of_times_production = len(number_of_times_production)
    
    number_of_routes_drone = s[s.Value > 0]
    number_of_routes_drone = number_of_routes_drone.groupby(["Drone", "Period"])["Value"].count()
    number_of_routes_drone = len(number_of_routes_drone)
    
    units_send_by_drone = z_hat.Value.sum()
    units_send_by_truck_ship = w_hat.Value.sum()
    units_delayed = calculation_units_delayed_per_period(f)
    
    # print report
    summary_file = "Summary.txt"
    
    solution_file = open(summary_file, 'a')
    solution_file.writelines("#####Summary instance#####\n")
    solution_file.writelines("\n")
    solution_file.writelines("Number of relocations: " + str(number_of_relocations) +"\n")
    solution_file.writelines("Number of times of production: " + str(number_of_times_production) +"\n")
    solution_file.writelines("Number of routes with drones: " + str(number_of_routes_drone) +"\n")
    solution_file.writelines("Units of products shipped by drone: " + str(units_send_by_drone) +"\n")
    solution_file.writelines("Units of products shipped by truck/ship: " + str(units_send_by_truck_ship) +"\n")
    solution_file.writelines("\n")
    solution_file.writelines("Total cost: " + str(total_cost) +"\n")
    solution_file.writelines("      - Relocation cost: " + str(relocation_cost) +"\n")
    solution_file.writelines("      - Production cost: " + str(production_cost) +"\n")
    solution_file.writelines("      - Shipments by drone cost: " + str(shipments_drone_cost) +"\n")
    solution_file.writelines("      - Shipments by land cost: " + str(shipments_land_cost) +"\n")
    solution_file.writelines("      - Shipments by ship cost: " + str(shipments_ship_cost) +"\n")
    solution_file.writelines("      - Late deliveries cost: " + str(penalties_cost) +"\n")
    solution_file.writelines("\n")
    for t in range(0, units_delayed.shape[0]):
        solution_file.writelines("Units of products delayed " + str(units_delayed.iloc[t]["Days"]) + " periods: " + str(units_delayed.iloc[t]["Value"]) +"\n")
    solution_file.close()
    
    # create summary decisions
    summary = summary_for_decisions(Set_t, x, y_hat, z_hat, s, Set_i, w_hat, u)
    summary.to_csv("Summary_decisions.csv", index=False)

    
    
    return x_factory_origin_destination_period,x_hat_factory_location_period,y_hat_product_factory_period,n_product_factory_period,b_drone_location_period,e_drone_location_period,z_drone_factory_location_customer_period,z_hat_product_drone_factory_customer_period,w_factory_location_harbor_period,w_hat_product_factory_harbor_customer_period,u_product_harbor_customer_period,u_hat_product_harbor_customer_period,f_product_customer_duedate_period,m_hat_product_customer_period,s_drone_origin_destination_period,lambda_