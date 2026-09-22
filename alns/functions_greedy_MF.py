import numpy as np
import pandas as pd
from haversine import haversine


# calculation of distance among two sets
def distances(set_1, set_2):
    d = np.zeros((len(set_1), len(set_2)))
    
    # distance from set 1
    for i in range(len(set_1)):
        x1 = set_1[i]
        
        # to set 2
        for n in range(len(set_2)):
            x2 = set_2[n]
            distance = haversine(x1, x2)
            d[i][n] = distance
            
    return d


# computation of delta parameter of coverage
def delta_calculation(d, max_delta):
    
    delta = np.zeros((len(d), len(d[0])))

    for i in range(0, len(d)):
        for l in range(0, len(d[0])):
            
            # check condition
            if d[i][l] <= max_delta:
                delta[i][l] = 1
            else:
                delta[i][l] = 0

    return delta


# computation of ship times
def calculation_omega(customers, harbors, speed_ship):
    d_k_l = distances(harbors, customers)
    omega = np.ceil(((d_k_l / 1.852) / speed_ship) / 24)
    
    return omega


# computation of relocation cost
def relocation_cost_calculation(x, locations, CR_f, CR_v):
    
    x = df_creation_four_index(x, names=["Factory","Location_Origin","Location_Destination","Period","Value"])
    
    x_cost = x[x.Value > 0]
    distances_i_i = distances(locations, locations)
    relocation_cost = 0

    for i in range(len(x_cost)):
        cost = CR_f + CR_v * distances_i_i[int(x_cost.iloc[i]["Location_Origin"]-1)][int(x_cost.iloc[i]["Location_Destination"]-1)]
        relocation_cost = relocation_cost + cost

    return np.ceil(relocation_cost)


# calculation of production cost
def production_cost_calculation(y_hat, alpha, CP_f, Set_p):
    
    y_hat = df_creation_three_index(y_hat, names=["Product", "Factory", "Period", "Value"])

    y_hat_cost = y_hat[y_hat.Value > 0]
    production_cost = 0
   
    for i in range(len(y_hat_cost)):

        if Set_p > 1:
            cost = CP_f * alpha[int(y_hat_cost.iloc[i]["Product"]-1)] * y_hat_cost.iloc[i]["Value"]
        else:
            cost = CP_f * alpha * y_hat_cost.iloc[i]["Value"]

        production_cost = production_cost + cost

    return np.ceil(production_cost)


# calculation of penalization cost
def penalties_cost_calculation(f, CB_ini):
    
    f = df_creation_four_index(f, names=["Product","Customer","Due date","Period","Value"])

    f_cost = f[f.Value > 0]
    penalties_cost = 0

    for i in range(len(f_cost)):
        CB = CB_ini * np.power(int(f_cost.iloc[i]["Period"]) - int(f_cost.iloc[i]["Due date"]) + 1, 2)
        cost = CB * f_cost.iloc[i]["Value"]
        penalties_cost = penalties_cost + cost

    return np.ceil(penalties_cost)


# calculation cost of shipments by drone
def shipments_drone_cost_calculation(s, CT, locations, customers):
    
    s = df_creation_four_index(s, names=["Drone","Origin","Destination","Period","Value"])
    
    s_cost = s[s.Value > 0]
    nodes = np.concatenate((locations, customers), axis=0)
    d_nodes = distances(nodes, nodes)

    shipments_drone_cost = 0

    for i in range(len(s_cost)):
        cost = CT * d_nodes[int(s_cost.iloc[i]["Origin"]-1)][int(s_cost.iloc[i]["Destination"]-1)]
        shipments_drone_cost = shipments_drone_cost + cost

    return np.ceil(shipments_drone_cost)


# calculation of shipments by land
def shipments_land_cost_calculation(w, CT1, locations, harbors):
    
    w = df_creation_four_index(w, names=["Factory","Location","Harbor","Period","Value"])

    w_cost = w[w.Value > 0]
    d_i_k = distances(locations, harbors)

    shipments_land_cost = 0

    for i in range(len(w_cost)):
        cost = CT1 * d_i_k[int(w_cost.iloc[i]["Location"]-1)][int(w_cost.iloc[i]["Harbor"]-1)]
        shipments_land_cost = shipments_land_cost + cost

    return np.ceil(shipments_land_cost)


# calculation of costs by ship
def shipments_ship_cost_calculation(u, CT2):

    u = df_creation_four_index(u, names=["Product","Harbor","Customer","Period","Value"])

    u_cost = u[u.Value > 0]
    shipments_ship_cost = 0

    for i in range(len(u_cost)):
        cost = CT2 * u_cost.iloc[i]["Value"]
        shipments_ship_cost = shipments_ship_cost + cost

    return np.ceil(shipments_ship_cost)


# calculation of units delayed per period
def calculation_units_delayed_per_period(f):

    delayed_units = f[f.Value > 0] # filter the periods when there are delayed units
    delayed_units.loc[:, "Days"] = delayed_units["Period"] - delayed_units["Due date"] + 1 # create new column to compute periods of delayed
    delayed_units = delayed_units.groupby("Days", as_index=False).sum()
    delayed_units.drop(columns=["Product", "Customer", "Period", "Due date"], axis=1, inplace=True)

    return delayed_units


# creation of dataframe to print results for variables with three indexes
def df_creation_three_index(variable_three, names):
    
    row_idx, col_idx, depth_idx = np.indices(variable_three.shape)
    
    df_three = pd.DataFrame({
        names[0]: row_idx.flatten() + 1,
        names[1]: col_idx.flatten() + 1,
        names[2]: depth_idx.flatten() + 1,
        names[3]: variable_three.flatten()
    })

    return df_three


# creation of dataframe to print results for variables with four indexes
def df_creation_four_index(variable_four, names):
    
    row_idx, col_idx, depth1_idx, depth2_idx = np.indices(variable_four.shape)
    
    df_four = pd.DataFrame({
        names[0]: row_idx.flatten() + 1,
        names[1]: col_idx.flatten() + 1,
        names[2]: depth1_idx.flatten() + 1,
        names[3]: depth2_idx.flatten() + 1,
        names[4]: variable_four.flatten()
    })

    return df_four


# creation of dataframe to print results for variables with five indexes
def df_creation_five_index(variable_five, names):
    
    row_idx, col_idx, depth1_idx, depth2_idx, depth3_idx = np.indices(variable_five.shape)
    
    df_five = pd.DataFrame({
        names[0]: row_idx.flatten() + 1,
        names[1]: col_idx.flatten() + 1,
        names[2]: depth1_idx.flatten() + 1,
        names[3]: depth2_idx.flatten() + 1,
        names[4]: depth3_idx.flatten() + 1,
        names[5]: variable_five.flatten()
    })

    return df_five


# creation csv with summary of all decisions
def summary_for_decisions(Set_t, x, y_hat, z_hat, s, Set_i, w_hat, u):

    summary = []

    # review of each period decisions
    for t in range(1, Set_t):

        # relocation decisions
        relocations = x[(x.Period == t) & (x.Value > 0)]

        if relocations.shape[0] > 0:

            for i in range(0, relocations.shape[0]):
                summary.append([t, "Relocation", "From Location " + str(relocations.iloc[i]["Location_Origin"]) + " to Location " + str(relocations.iloc[i]["Location_Destination"])])

        # production decisions
        production = y_hat[(y_hat.Period == t) & (y_hat.Value > 0)]

        if production.shape[0] > 0:

            for i in range(0, production.shape[0]):
                summary.append([t, "Production", "Factory " + str(production.iloc[i]["Factory"]) + " produces " + str(production.iloc[i]["Value"]) + " units of product " + str(production.iloc[i]["Product"])])

        # shipments by drone decisions
        drone_shipments = z_hat[(z_hat.Period == t) & (z_hat.Value > 0)]

        if drone_shipments.shape[0] > 0:

            for i in range(0, drone_shipments.shape[0]):
                summary.append([t, "Shipment by drone", "Drone " + str(drone_shipments.iloc[i]["Drone"]) + " ships " + str(drone_shipments.iloc[i]["Value"]) + " units of product " + str(drone_shipments.iloc[i]["Product"]) + " from factory " + str(drone_shipments.iloc[i]["Factory"]) + " to customer " + str(drone_shipments.iloc[i]["Customer"])])

        # routes of drones
        routes_drones = s[(s.Period == t) & (s.Value > 0)]

        if routes_drones.shape[0] > 0:

            number_of_drones = routes_drones.Drone.unique()

            for h in range(0, len(number_of_drones)):

                route_only = routes_drones[routes_drones.Drone == number_of_drones[h]]
                route = []

                # first arc
                origin = route_only.iloc[0]["Origin"]
                destination = route_only.iloc[0]["Destination"]
                route.append(origin)
                route.append(destination)

                for n in range(1, len(route_only)):
                    origin = route_only[route_only.Origin == route[-1]]
                    destination = origin.iloc[0]["Destination"]
                    route.append(destination)

                for i in range(0, len(route)):

                    if route[i] > Set_i:
                        route[i] = "C" + str(route[i] - Set_i)
                    else:
                        route[i] = "L" + str(route[i])

                route_print = ''
                for i in range(len(route) - 1):
                    if len(route) > 2:
                        route_print = route_print + str(route[i]) + "->"
                route_print = route_print + str(route[-1])

                summary.append([t, "Route drone", route_print])

        # shipments by truck
        truck_shipments = w_hat[(w_hat.Period == t) & (w_hat.Value > 0)]

        if truck_shipments.shape[0] > 0:

            for i in range(0, truck_shipments.shape[0]):
                summary.append([t, "Shipment by truck", "Factory " + str(truck_shipments.iloc[i]["Factory"]) + " sends " + str(truck_shipments.iloc[i]["Value"]) + " units of product " + str(truck_shipments.iloc[i]["Product"]) + " to harbor " + str(truck_shipments.iloc[i]["Harbor"]) + " for customer " + str(truck_shipments.iloc[i]["Customer"])])

        # shipments by ship
        ship_shipments = u[(u.Period == t) & (u.Value > 0)]

        if ship_shipments.shape[0] > 0:

            for i in range(0, ship_shipments.shape[0]):
                summary.append([t, "Shipment by ship", "Harbor " + str(ship_shipments.iloc[i]["Harbor"]) + " sends " + str(ship_shipments.iloc[i]["Value"]) + " units of product " + str(ship_shipments.iloc[i]["Product"]) + " to customer " + str(ship_shipments.iloc[i]["Customer"])])

    summary = pd.DataFrame(summary, columns=["Period", "Decision", "Description"])

    return summary