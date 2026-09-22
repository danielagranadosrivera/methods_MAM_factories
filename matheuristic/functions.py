import numpy as np
import pandas as pd
from haversine import haversine


def distances_total(locations, customers, harbors):
    d = []

    # Calculation distances from locations of mobile factories
    for i in range(len(locations)):
        x1 = locations[i]
        #To mobile factories
        for n in range(len(locations)):
            x2 = locations[n]
            distance = haversine(x1, x2)
            d.append((i + 1, n + 1, distance))
        #To customers
        for n in range(len(customers)):
            x2 = customers[n]
            distance = haversine(x1, x2)
            d.append((i + 1, n + 1 + len(locations), distance))
        #To harbors
        for n in range(len(harbors)):
            x2 = harbors[n]
            distance = haversine(x1, x2)
            d.append((i + 1, n + 1 + len(locations) + len(customers), distance))

    # Calculation distances from customers
    for i in range(len(customers)):
        x1 = customers[i]
        # To mobile factories
        for n in range(len(locations)):
            x2 = locations[n]
            distance = haversine(x1, x2)
            d.append((i + 1 + len(locations), n + 1, distance))
        # To customers
        for n in range(len(customers)):
            x2 = customers[n]
            distance = haversine(x1, x2)
            d.append((i + 1 + len(locations), n + 1 + len(locations), distance))
        # To harbors
        for n in range(len(harbors)):
            x2 = harbors[n]
            distance = haversine(x1, x2)
            d.append((i + 1 + len(locations), n + 1 + len(locations) + len(customers), distance))

    # Calculation distances from harbors
    for i in range(len(harbors)):
        x1 = harbors[i]
        # To mobile factories
        for n in range(len(locations)):
            x2 = locations[n]
            distance = haversine(x1, x2)
            d.append((i + 1 + len(locations) + len(customers), n + 1, distance))
        # To customers
        for n in range(len(customers)):
            x2 = customers[n]
            distance = haversine(x1, x2)
            d.append((i + 1 + len(locations) + len(customers), n + 1 + len(locations), distance))
        # To harbors
        for n in range(len(harbors)):
            x2 = harbors[n]
            distance = haversine(x1, x2)
            d.append((i + 1 + len(locations) + len(customers), n + 1 + len(locations) + len(customers), distance))

    return d


def haversine_distances(set1, set2):
    distances = []

    # Calculation distances from set1 to set 2
    for i in range(len(set1)):
        x1 = set1[i]
        row = []
        for n in range(len(set2)):
            x2 = set2[n]
            distance = haversine(x1, x2)
            row.append(distance)
        distances.append(row)

    return distances


def costs_by_land(CT1, d, Set_i, Set_l, Set_k):
    Set_i = int(Set_i[0])
    Set_l = int(Set_l[0])
    Set_k = int(Set_k[0])

    # Calculate costs of shipping by truck from the locations to harbors
    CT1_ik = []
    for i in range(0, Set_i):
        for k in range(0, Set_k):
            distance = d[(i + 1) * (Set_i + Set_l + Set_k) - (Set_k - k)][2]
            CT1_ik.append((i + 1, k + 1, CT1 * distance))

    return CT1_ik


def tuple_one_dimensions(vector_for_tuple):
    if vector_for_tuple.size > 1:
        tuple_list = []
        for i in range(len(vector_for_tuple)):
            tuple_list.append((i + 1, vector_for_tuple[i]))
    else:
        tuple_list = pd.DataFrame([(1, vector_for_tuple)])

    return tuple_list


def tuple_table(table_for_tuple, Set1, Set2):
    Set1 = int(Set1[0])
    Set2 = int(Set2[0])
    tuple_list = []

    if Set1 > 1:
        for i in range(0, Set1):

            if Set2 > 1:
                for j in range(0, Set2):
                    tuple_list.append((i + 1, j + 1, table_for_tuple[i][j]))
            else:
                tuple_list.append((i + 1, 1, table_for_tuple[i]))

    else:
        if Set2 > 1:
            for j in range(0, Set2):
                tuple_list.append((1, j + 1, table_for_tuple[j]))
        else:
            tuple_list.append((1, 1, table_for_tuple))

    return tuple_list


def tuple_four_dimensions(table_for_tuple):
    tuple_list = []

    for i in range(len(table_for_tuple)):
        tuple_list.append((i+1, table_for_tuple[i][-1]))

    return tuple_list


def delta_calculation(d, max_delta, Set_i, Set_l, Set_k):
    Set_i = int(Set_i[0])
    Set_l = int(Set_l[0])
    Set_k = int(Set_k[0])
    delta = []

    for i in range(0, np.power(Set_i + Set_l + Set_k, 2)):
        if d[i][2] <= max_delta:
            delta.append((d[i][0], d[i][1], 1))
        else:
            delta.append((d[i][0], d[i][1], 0))

    return delta


def calculation_omega(customers, harbors, speed_ship):
    distances = haversine_distances(customers, harbors)

    omega = []
    for l in range(0, len(customers)):
        for k in range(0, len(harbors)):
            distance_nm = distances[l][k] / 1.852
            hours = distance_nm / speed_ship
            omega.append((l + 1, k + 1, int(np.ceil(hours / 24))))

    return omega


def penalties_table(periods, CB_ini):

    periods = int(periods[0])
    CB = []

    for t1 in range(0, periods):
        for t2 in range(0, periods):
            if t1 <= t2:
                CB.append((t1 + 1,  t2 + 1, CB_ini * np.power(t2 - t1 + 1,2)))
            else:
                CB.append((t1 + 1,  t2 + 1, 0))

    return CB

def sum_accumulated_demand(accu_lambda_iter, Set_p, Set_l):

    Set_p = int(Set_p[0])
    Set_l = int(Set_l[0])

    #Sum the demand by customer and by product
    accu_lambda = accu_lambda_iter.groupby(['Product', 'Customer']).sum()
    accu_lambda.drop(columns=['Cluster', 'Period'], axis=1, inplace=True)

    accu_lambda_iter = []
    for p in range(0, Set_p):
        for l in range(0, Set_l):
            accu_lambda_iter.append((p + 1, l + 1, accu_lambda.iloc[Set_l * p + l]["Value"]))

    return accu_lambda_iter


def products_in_transit_ship(u_hat, customers, harbors, speed_ship, demand_days, sets):

    u_hat = u_hat[u_hat["Period"] > demand_days]
    distances = haversine_distances(customers, harbors)

    # check which are valid shipments
    for r in range(len(u_hat)):
        test_value = u_hat.iloc[r]["Value"]
        if u_hat.iloc[r]["Value"] > 0:
            distance_nm = distances[u_hat.iloc[r]["Customer"]-1][u_hat.iloc[r]["Harbor"]-1] / 1.852
            hours = distance_nm / speed_ship
            omega = int(np.ceil(hours / 24))

            if u_hat.iloc[r]["Period"] - omega <= demand_days:
                u_hat.iloc[r]["Value"] = u_hat.iloc[r]["Value"]
            else:
                u_hat.iloc[r]["Value"] = 0

    # changes indexes for opl
    for r in range(len(u_hat)):
        u_hat.iloc[r]["Period"] = u_hat.iloc[r]["Period"] - demand_days

    # create parameter to pass
    Set_p = int(sets[2][0])
    Set_k = int(sets[5][0])
    Set_l = int(sets[3][0])
    Set_t = int(sets[6][0])

    u_hat_iter = []

    for p in range(0, Set_p):
        for k in range(0, Set_k):
            for l in range(0, Set_l):
                for t in range(0, Set_t):

                    if t <= demand_days:
                        value = u_hat[(u_hat.Product == p+1) & (u_hat.Harbor == k+1) & (u_hat.Customer == l+1) & (u_hat.Period == t+1)]["Value"]
                        value = int(value)
                        u_hat_iter.append([p+1, k+1, l+1, t+1, value])

                    else:
                        u_hat_iter.append([p + 1, k + 1, l + 1, t + 1, 0])

    u_hat_iter = tuple_four_dimensions(u_hat_iter)

    return u_hat_iter


def join_parameters(cuts, dataframes, demand_days):

    new_df = [] #new dataframe to store tables

    for t in range(0, len(cuts)):

        #Extract cut
        variable_sec = dataframes[t]

        # change of indexes
        for p in range(len(variable_sec)):
            variable_sec.iloc[p]["Period"] = variable_sec.iloc[p]["Period"] + (demand_days * t)

        if t < len(cuts) - 1:
            variable_sec = variable_sec[(variable_sec.Period >= cuts[t][0]) & (variable_sec.Period <= cuts[t][1])] # filter cut
        else:
            variable_sec = variable_sec[(variable_sec.Period >= cuts[t][0]) & (variable_sec.Period <= cuts[t][2])]  # filter cut
        new_df.append(variable_sec)

    new_df = pd.concat(new_df)

    return new_df


def join_parameters_penalization(cuts, dataframes, demand_days):
    new_df = []  # new dataframe to store tables

    for t in range(0, len(cuts)):

        # Extract cut
        variable_sec = dataframes[t]

        # change of indexes
        for p in range(len(variable_sec)):
            variable_sec.iloc[p]["Due date"] = variable_sec.iloc[p]["Due date"] + (demand_days * t)
            variable_sec.iloc[p]["Period"] = variable_sec.iloc[p]["Period"] + (demand_days * t)

        if t < len(cuts) - 1:
            variable_sec = variable_sec[
                (variable_sec.Period >= cuts[t][0]) & (variable_sec.Period <= cuts[t][1])]  # filter cut
        else:
            variable_sec = variable_sec[
                (variable_sec.Period >= cuts[t][0]) & (variable_sec.Period <= cuts[t][2])]  # filter cut
        new_df.append(variable_sec)

    new_df = pd.concat(new_df)
    return new_df

def relocation_cost_calculation(x, locations, CR_f, CR_v):

    x_cost = x[x.Value > 0]
    distances = haversine_distances(locations, locations)
    CR_f = float(CR_f[0])
    CR_v = float(CR_v[0])
    relocation_cost = 0

    for i in range(len(x_cost)):
        cost = CR_f + CR_v * distances[int(x_cost.iloc[i]["Location_Origin"]-1)][int(x_cost.iloc[i]["Location_Destination"]-1)]
        relocation_cost = relocation_cost + cost

    return np.ceil(relocation_cost)


def production_cost_calculation(y_hat, alpha, CP_f, Set_p):

    Set_p = int(Set_p[0])
    y_hat_cost = y_hat[y_hat.Value > 0]
    CP_f = float(CP_f[0])
    production_cost = 0
    alpha = np.genfromtxt(r"data\input\alpha.csv", delimiter=',', skip_header=True).astype("float")

    for i in range(len(y_hat_cost)):

        if Set_p > 1:
            cost = CP_f * alpha[int(y_hat_cost.iloc[i]["Product"]-1)] * y_hat_cost.iloc[i]["Value"]
        else:
            cost = CP_f * alpha * y_hat_cost.iloc[i]["Value"]

        production_cost = production_cost + cost

    return np.ceil(production_cost)


def shipments_drone_cost_calculation(s, CT, locations, customers):

    CT = float(CT[0])
    s_cost = s[s.Value > 0]
    nodes = np.concatenate((locations, customers), axis=0)
    distances = haversine_distances(nodes, nodes)

    shipments_drone_cost = 0

    for i in range(len(s_cost)):
        cost = CT * distances[int(s_cost.iloc[i]["Origin"]-1)][int(s_cost.iloc[i]["Destination"]-1)]
        shipments_drone_cost = shipments_drone_cost + cost

    return np.ceil(shipments_drone_cost)


def shipments_land_cost_calculation(w, CT1, locations, harbors):

    w_cost = w[w.Value > 0]
    distances = haversine_distances(locations, harbors)

    shipments_land_cost = 0

    for i in range(len(w_cost)):
        cost = CT1 * distances[int(w_cost.iloc[i]["Location"]-1)][int(w_cost.iloc[i]["Harbor"]-1)]
        shipments_land_cost = shipments_land_cost + cost

    return np.ceil(shipments_land_cost)


def shipments_ship_cost_calculation(u, CT2):

    CT2 = float(CT2[0])
    u_cost = u[u.Value > 0]

    shipments_ship_cost = 0

    for i in range(len(u_cost)):
        cost = CT2 * u_cost.iloc[i]["Value"]
        shipments_ship_cost = shipments_ship_cost + cost

    return np.ceil(shipments_ship_cost)


def penalties_cost_calculation(f, CB_ini):

    f_cost = f[f.Value > 0]
    penalties_cost = 0

    for i in range(len(f_cost)):
        CB = CB_ini * np.power(int(f_cost.iloc[i]["Period"]) - int(f_cost.iloc[i]["Due date"]) + 1, 2)
        cost = CB * f_cost.iloc[i]["Value"]
        penalties_cost = penalties_cost + cost

    return np.ceil(penalties_cost)


def summary_for_decisions(Set_t, x, y_hat, z_hat, s, Set_i, w_hat, u):

    summary = []

    # review of each period decisions
    for t in range(1, int(Set_t[0])):

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

                    if route[i] > int(Set_i[0]):
                        route[i] = "C" + str(route[i] - int(Set_i[0]))
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


def calculation_units_delayed_per_period(f):

    delayed_units = f[f.Value > 0] # filter the periods when there are delayed units
    delayed_units["Days"] = delayed_units["Period"] - delayed_units["Due date"] + 1 # create new column to compute periods of delayed
    delayed_units = delayed_units.groupby("Days", as_index=False).sum()
    delayed_units.drop(columns=["Product", "Customer", "Period", "Due date"], axis=1, inplace=True)

    return delayed_units


def creation_b_hat(phi, b_hat_ini, Set_h, Set_i):

    if int(Set_h[0]) > 1:
        b_hat = np.zeros((int(Set_h[0]), int(Set_i[0])))
    else:
        b_hat = np.zeros(int(Set_i[0]))

    phi_for_b_hat = phi[phi.Value == 1]
    for i in range(len(b_hat_ini)):
        if phi_for_b_hat.iloc[i]["Factory"] == b_hat_ini.iloc[i]["Factory"]:
            if b_hat_ini.iloc[i]["Value"] == 1:
                location = phi_for_b_hat.iloc[i]["Location"]
                if int(Set_h[0]) > 1:
                    b_hat[i][location - 1] = 1
                else:
                    b_hat[location - 1] = 1
    return b_hat
