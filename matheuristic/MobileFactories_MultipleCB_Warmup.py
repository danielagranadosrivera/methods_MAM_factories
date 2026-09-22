from doopl.factory import *
import os
from os.path import dirname, abspath, join
import pandas as pd
import numpy as np
from functions import *
from First_Stage import *
from Second_Stage_Ini_Warmup import *
from Second_Stage_Initialization import *
from Second_Stage_Decomposition import *
from warmup_firstpart import *

# Set up of directories
datadir = os.path.join(dirname(abspath(__file__)), "data", "models")
CB_values = [50,275,500]

for CB_ini in CB_values:
    gen_dir = os.path.join(dirname(abspath(__file__)), "data", "output", "CB_" + str(CB_ini))
    if not os.path.isdir(gen_dir):
        os.makedirs(gen_dir)

    #Read inputs
    #########################################################################################################################################################################################################################################################################################################################

    # read files
    parameters = np.genfromtxt(os.path.join("data", "input", "parameters.csv"), delimiter=',', skip_header=True).astype("float")  # coordinates of harbors
    locations = np.genfromtxt(os.path.join("data", "input", "locations.csv"), delimiter=',', skip_header=True).astype("float")  # coordinates of locations for mobile factories
    customers = np.genfromtxt(os.path.join("data", "input", "customers.csv"), delimiter=',', skip_header=True).astype("float")  # coordinates of customers
    harbors = np.genfromtxt(os.path.join("data", "input", "harbors.csv"), delimiter=',', skip_header=True).astype("float")  # coordinates of harbors
    _beta = np.genfromtxt(os.path.join("data", "input", "beta.csv"), delimiter=',', skip_header=True).astype("int")  # schedule of ships
    _lambda = np.genfromtxt(os.path.join("data", "input", "lambda.csv"), delimiter=',', skip_header=True).astype("int")  # demand for customers
    eta = np.genfromtxt(os.path.join("data", "input", "eta.csv"), delimiter=',', skip_header=True).astype("float")  # weight of product p
    theta = np.genfromtxt(os.path.join("data", "input", "theta.csv"), delimiter=',', skip_header=True).astype("int")  # binary matrix if mobile factory in i can produce product p
    alpha = np.genfromtxt(os.path.join("data", "input", "alpha.csv"), delimiter=',', skip_header=True).astype("float")  # cross-sectional area of product p

    # define sets
    Set_i = pd.DataFrame([(len(locations))])

    if theta.ndim < 2:
        Set_j = pd.DataFrame([(1)])
    else:
        Set_j = pd.DataFrame([(len(theta))])

    if alpha.ndim == 0:
        Set_p = pd.DataFrame([(1)])
    else:
        Set_p = pd.DataFrame([(len(alpha))])

    Set_l = pd.DataFrame([(len(customers))])
    Set_h = pd.DataFrame([(parameters[0][1])])
    Set_k = pd.DataFrame([(len(harbors))])
    Set_t = pd.DataFrame([(parameters[1][1])])

    # define parameters
    CR_f = pd.DataFrame([(parameters[2][1])]) # fixed relocation cost for moving a factory
    CR_v = pd.DataFrame([(parameters[3][1])]) # variable relocation cost per kilometer for moving a factory
    CP_f = pd.DataFrame([(parameters[4][1])]) # set-up cost to produce at any factory
    CT = pd.DataFrame([(parameters[5][1])]) # transport cost per kilometer for shipping by drone
    CT1 = parameters[6][1] # transport cost for shipping by land per kilometer
    CT2 = pd.DataFrame([(parameters[7][1])]) # fixed cost for shipping by ship in any period
    CT3 = pd.DataFrame([(parameters[8][1])]) # transport cost per unit for shipping by drone
    CT4 = pd.DataFrame([(parameters[9][1])]) # transport cost per unit for shipping by ship
    V_average = pd.DataFrame([(parameters[10][1])]) # average speed when a factory is being relocated
    r_estimation = pd.DataFrame([(parameters[11][1])]) # set-up time for relocating a factory
    M = pd.DataFrame([(parameters[12][1])]) # a big number
    MA = pd.DataFrame([(parameters[13][1])]) # maximum cross-sectional area available for batching in a built
    tau = pd.DataFrame([(parameters[14][1])]) # capacity in product weight of a drone
    gamma = pd.DataFrame([(parameters[15][1])]) #
    MT = pd.DataFrame([(parameters[16][1])]) #
    max_delta = parameters[17][1] # maximum distance a drone can travel
    speed_ship = parameters[18][1] # speed of ships
    eta = tuple_one_dimensions(eta) # weight of product p
    d = distances_total(locations, customers, harbors) # distance in kilometers from location g to location g
    delta = delta_calculation(d, max_delta, Set_i, Set_l, Set_k) # binary matrix if customer l is in drone coverage from location i
    theta = tuple_table(theta, Set_j, Set_p) # binary matrix if mobile factory in i can produce product p
    alpha = tuple_one_dimensions(alpha) # cross-sectional area of product p
    omega = calculation_omega(customers, harbors, speed_ship) # duration of shipment from intermediary k to customer l
    CT_ik = costs_by_land(CT1, d, Set_i, Set_l, Set_k) # transport cost for shipping by land from location i to intermediary k

    #########################################################################################################################################################################################################################################################################################################################



    #Run first stage
    #########################################################################################################################################################################################################################################################################################################################

    sets = Set_i, Set_j, Set_p, Set_l, Set_h, Set_k, Set_t  # save all the sets in a single object

    beta_ = tuple_four_dimensions(_beta) # availability of the ship to sail from intermediary point k to customer l in period t
    lambda_ = tuple_four_dimensions(_lambda) # the demand for product p from client l in period t

    # save all parameters in a single object
    parameters_first_stage = CR_f, CR_v, CP_f, CT, CT_ik, CT2, CT3, CT4, d, eta, V_average, r_estimation, M, theta, alpha, MA, tau, delta, beta_, lambda_, omega, gamma, MT, CB_ini

    mod_first = join(datadir, "MFLP_No_Routing.mod")
    ops_first = join(datadir, "MFLP_No_Routing.ops")

    x, x_hat, y_hat, phi, b_hat_ini, first_stage_time = first_stage(sets, parameters_first_stage, mod_first, ops_first, gen_dir)

    # create b_hat parameter starting position of each drone h
    b_hat = creation_b_hat(phi, b_hat_ini, Set_h, Set_i)
    b_hat = tuple_table(b_hat, Set_h, Set_i)

    #########################################################################################################################################################################################################################################################################################################################



    ###Run second stage
    #########################################################################################################################################################################################################################################################################################################################

    # parameters for second stage
    demand_days = parameters[19][1]  # number of days with due dates to schedule in the decomposition of the second stage
    horizon_days = parameters[21][1]  # number of days without demand for late deliveries
    _beta = pd.DataFrame(_beta, columns=["Harbor", "Customer", "Cluster", "Period", "Value"])  # change beta to dataframe to filter easily
    _lambda = pd.DataFrame(_lambda, columns=["Product", "Customer", "Cluster", "Period", "Value"])  # change lambda to dataframe to filter easily

    # create ranges
    ranges = int(np.floor(int(Set_t[0]) / demand_days))  # number of sub-routing models to run

    cuts = []  # array to save the start of the range, the days with due dates, and the rolling horizon
    demand = 0
    for t in range(0, ranges):
        start = demand + 1
        demand = demand + demand_days
        if demand + horizon_days <= int(Set_t[0]):
            end = demand + horizon_days
        else:
            end = int(Set_t[0])

        cuts.append([start, demand, end])


    #First run for warmup
    overlap_days = parameters[22][1]  # number of days to overlap in the rolling horizon for warm_up
    sets = Set_i, Set_j, Set_p, Set_l, Set_h, Set_k
    parameters_warm_up = demand_days, overlap_days, horizon_days, _lambda, _beta, cuts, CR_f, CR_v, CP_f, CT, CT_ik, CT2, CT3, CT4, d, eta, V_average, r_estimation, M, theta, alpha, MA, tau, delta, omega, gamma, MT, b_hat, CB_ini, x, x_hat, y_hat, customers, harbors, speed_ship

    f_warm, n_warm, s_warm, u_warm, w_warm, w_hat_warm, z_hat_warm, total_time_warm = warmup_firstpart(sets, parameters_warm_up, datadir, gen_dir)

    # filter variable for only the first run
    f_warm = tuple_four_dimensions(f_warm[f_warm.Period <= demand_days + horizon_days].to_numpy())
    n_warm = tuple_four_dimensions(n_warm[n_warm.Period <= demand_days + horizon_days].to_numpy())
    s_warm = tuple_four_dimensions(s_warm[s_warm.Period <= demand_days + horizon_days].to_numpy())
    u_warm = tuple_four_dimensions(u_warm[u_warm.Period <= demand_days + horizon_days].to_numpy())
    w_warm = tuple_four_dimensions(w_warm[w_warm.Period <= demand_days + horizon_days].to_numpy())
    w_hat_warm = tuple_four_dimensions(w_hat_warm[w_hat_warm.Period <= demand_days + horizon_days].to_numpy())
    z_hat_warm = tuple_four_dimensions(z_hat_warm[z_hat_warm.Period <= demand_days + horizon_days].to_numpy())

    warmup_variables = f_warm, n_warm, s_warm, u_warm, w_warm, w_hat_warm, z_hat_warm

    # definition lists to save variables
    z_hat = []
    s = []
    w = []
    w_hat = []
    u = []
    f = []
    n = []
    times = []

    #First cut run >> Initialization parameters
    sets = Set_i, Set_j, Set_p, Set_l, Set_h, Set_k, pd.DataFrame([(cuts[0][2])])  # save all the sets in a single object
    overlap_days = parameters[20][1]  # number of days to overlap in the rolling horizon (final)
    beta_ = tuple_four_dimensions(_beta[_beta.Period <= cuts[0][2]].to_numpy()) # filter schedule for only the first cut

    # filter demand for only first cut
    lambda_ = _lambda[_lambda.Period <= cuts[0][2]]
    for t in range(len(lambda_)):
        if lambda_.iloc[t]["Period"] > demand_days + overlap_days:
            lambda_.iloc[t]["Value"] = 0
    lambda_ = tuple_four_dimensions(lambda_.to_numpy())

    # save all parameters in a single object
    parameters_second_stage = CR_f, CR_v, CP_f, CT, CT_ik, CT2, CT3, CT4, d, eta, V_average, r_estimation, M, theta, alpha, MA, tau, delta, beta_, lambda_, omega, gamma, MT, b_hat, CB_ini

    # parameters from first stage
    x_ = tuple_four_dimensions(x[x.Period <= cuts[0][2]].to_numpy())
    x_hat_ = tuple_four_dimensions(x_hat[x_hat.Period <= cuts[0][2]].to_numpy())
    y_hat_ = tuple_four_dimensions(y_hat[y_hat.Period <= cuts[0][2]].to_numpy())

    # save variables from first stage in only one object
    first_stage_param = x_, x_hat_, y_hat_

    # run model
    mod_sec_ini = join(datadir, "Routing_drones_Warmup.mod")
    ops_sec_ini = join(datadir, "Routing_drones_Warmup.ops")

    z_hat_sec, s_sec, w_sec, w_hat_sec, u_sec, f_sec, n_sec, e_sec, m_sec, m_hat_sec, u_hat_sec, second_stage_time_sec = second_stage_initialization_warmup(sets, parameters_second_stage, first_stage_param, warmup_variables, mod_sec_ini, ops_sec_ini, gen_dir)

    # save variables
    z_hat.append(z_hat_sec)
    s.append(s_sec)
    w.append(w_sec)
    w_hat.append(w_hat_sec)
    u.append(u_sec)
    f.append(f_sec)
    n.append(n_sec)
    times.append(second_stage_time_sec)

    #Remaining cuts

    # iteration for each cut
    count_for_files = 1
    for t in range(1, len(cuts)):

        # variables from previous cut

        n_iter = np.delete(n_sec[n_sec.Period == demand_days].to_numpy(), np.s_[2], 1)
        n_iter = [tuple(row) for row in n_iter]

        e_iter = np.delete(e_sec[e_sec.Period == demand_days].to_numpy(), np.s_[2], 1)
        e_iter = [tuple(row) for row in e_iter]

        m_iter = np.delete(m_sec[m_sec.Period == demand_days].to_numpy(), np.s_[3], 1)
        m_iter = tuple_four_dimensions(m_iter)

        m_hat_iter = np.delete(m_hat_sec[m_hat_sec.Period == demand_days].to_numpy(), np.s_[2], 1)
        m_hat_iter = [tuple(row) for row in m_hat_iter]

        accu_lambda_iter = _lambda[(_lambda.Period >= cuts[0][0]) & (_lambda.Period <= cuts[t-1][1])]
        accu_lambda_iter = sum_accumulated_demand(accu_lambda_iter, Set_p, Set_l)

        sets = Set_i, Set_j, Set_p, Set_l, Set_h, Set_k, pd.DataFrame([(cuts[t][2] - cuts[t - 1][1])])  # save all the sets in a single object
        u_hat_iter = products_in_transit_ship(u_hat_sec, customers, harbors, speed_ship, demand_days, sets)

        # save variables of previous cut in one element
        previous_cut_parameters = n_iter, e_iter, m_iter, m_hat_iter, accu_lambda_iter, u_hat_iter

        beta_ = _beta[(_beta.Period >= cuts[t][0]) & (_beta.Period <= cuts[t][2])] # filter schedule for cut
        # changes of index to make them work on opl
        for p in range(len(beta_)):
           beta_.iloc[p]["Period"] = beta_.iloc[p]["Period"] - (demand_days * t)
        beta_ = tuple_four_dimensions(beta_.to_numpy())

        # filter demand for only first cut
        lambda_ = _lambda[(_lambda.Period >= cuts[t][0]) & (_lambda.Period <= cuts[t][2])]
        for p in range(len(lambda_)):
            lambda_.iloc[p]["Period"] = lambda_.iloc[p]["Period"] - (demand_days * t)
            if lambda_.iloc[p]["Period"] > demand_days + overlap_days:
                lambda_.iloc[p]["Value"] = 0
        lambda_ = tuple_four_dimensions(lambda_.to_numpy())

        # save all parameters in a single object
        parameters_second_stage = CR_f, CR_v, CP_f, CT, CT_ik, CT2, CT3, CT4, d, eta, V_average, r_estimation, M, theta, alpha, MA, tau, delta, beta_, lambda_, omega, gamma, MT, b_hat, CB_ini

        # parameters from first stage

        x_ = x[(x.Period >= cuts[t][0]) & (x.Period <= cuts[t][2])]
        # changes of index for opl
        for p in range(len(x_)):
            x_.iloc[p]["Period"] = x_.iloc[p]["Period"] - (demand_days * t)
        x_ = tuple_four_dimensions(x_.to_numpy())

        x_hat_ = x_hat[(x_hat.Period >= cuts[t][0]) & (x_hat.Period <= cuts[t][2])]
        # changes of index for opl
        for p in range(len(x_hat_)):
            x_hat_.iloc[p]["Period"] = x_hat_.iloc[p]["Period"] - (demand_days * t)
        x_hat_ = tuple_four_dimensions(x_hat_.to_numpy())

        y_hat_ = y_hat[(y_hat.Period >= cuts[t][0]) & (y_hat.Period <= cuts[t][2])]
        # changes of index for opl
        for p in range(len(y_hat_)):
            y_hat_.iloc[p]["Period"] = y_hat_.iloc[p]["Period"] - (demand_days * t)
        y_hat_ = tuple_four_dimensions(y_hat_.to_numpy())

        # save variables from first stage in only one object
        first_stage_param = x_, x_hat_, y_hat_

        # run model
        count_for_files = count_for_files + 1

        mod_sec = join(datadir, "Routing_drones_Decomposition.mod")
        ops_sec = join(datadir, "Routing_drones_Decomposition.ops")

        z_hat_sec, s_sec, w_sec, w_hat_sec, u_sec, f_sec, n_sec, e_sec, m_sec, m_hat_sec, u_hat_sec, second_stage_time_sec = second_stage_decomposition(sets, parameters_second_stage, first_stage_param, previous_cut_parameters, mod_sec, ops_sec, gen_dir, count_for_files)

        #m_hat_sec.to_csv(os.path.join(gen_dir, "m_hat_sec.csv"), index=False)
        # save variables
        z_hat.append(z_hat_sec)
        s.append(s_sec)
        w.append(w_sec)
        w_hat.append(w_hat_sec)
        u.append(u_sec)
        f.append(f_sec)
        n.append(n_sec)
        times.append(second_stage_time_sec)

    #Joining data

    z_hat = join_parameters(cuts, z_hat, demand_days) # units of product p to ship by drone h from the mobile facility j to customer l in period t
    s = join_parameters(cuts, s, demand_days) # variable if drone h goes through arc (a,g) in period t
    w = join_parameters(cuts, w, demand_days) # variable if mobile facility j at location i transports products to intermediary k in period t
    w_hat = join_parameters(cuts, w_hat, demand_days) # variable if mobile facility j at location i transports products to intermediary k in period t
    u = join_parameters(cuts, u, demand_days) # units of product p to ship from intermediary k to customer l in period t
    f = join_parameters_penalization(cuts, f, demand_days) # units of product p ship in advance to customer l in period t
    n = join_parameters(cuts, n, demand_days) # units of product p in inventory in mobile factory j in period t

    # print cvs with variables
    z_hat.to_csv(os.path.join(gen_dir, "z_hat.csv"), index=False)
    s.to_csv(os.path.join(gen_dir, "s.csv"), index=False)
    w.to_csv(os.path.join(gen_dir, "w.csv"), index=False)
    w_hat.to_csv(os.path.join(gen_dir, "w_hat.csv"), index=False)
    u.to_csv(os.path.join(gen_dir, "u.csv"), index=False)
    f.to_csv(os.path.join(gen_dir, "f.csv"), index=False)
    n.to_csv(os.path.join(gen_dir, "n.csv"), index=False)

    #########################################################################################################################################################################################################################################################################################################################



    # Final processing
    #########################################################################################################################################################################################################################################################################################################################

    # total times
    total_time = first_stage_time + total_time_warm + sum(times)
    second_stage_times = sum(times)

    # compute costs
    relocation_cost = relocation_cost_calculation(x, locations, CR_f, CR_v)
    production_cost = production_cost_calculation(y_hat, alpha, CP_f, Set_p)
    shipments_drone_cost = shipments_drone_cost_calculation(s, CT, locations, customers)
    shipments_land_cost = shipments_land_cost_calculation(w, CT1, locations, harbors)
    shipments_ship_cost = shipments_ship_cost_calculation(u, CT2)
    penalties_cost = penalties_cost_calculation(f, CB_ini)

    total_cost = relocation_cost + production_cost + shipments_drone_cost + shipments_land_cost + shipments_ship_cost + penalties_cost

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
    summary_file = os.path.join(gen_dir, "Summary.txt")
    if os.path.exists(summary_file):
        os.remove(summary_file)

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
    solution_file.writelines("Total time: {:.2f} minutes".format(total_time/60)+"\n")
    solution_file.writelines("      - Time of first stage: {:.2f} minutes".format(first_stage_time/60)+"\n")
    solution_file.writelines("      - Time of second stage: {:.2f} minutes".format(second_stage_times/60)+"\n")
    for t in range(0, len(times)):
        solution_file.writelines("              * Time of " + str(t) + " routing: {:.2f} minutes".format(times[t] / 60) + "\n")
    solution_file.writelines("      - Time of warmup: {:.2f} minutes".format(total_time_warm / 60) + "\n")
    solution_file.writelines("\n")
    for t in range(0, units_delayed.shape[0]):
        solution_file.writelines("Units of products delayed " + str(units_delayed.iloc[t]["Days"]) + " periods: " + str(units_delayed.iloc[t]["Value"]) +"\n")
    solution_file.close()

    # create summary decisions
    summary = summary_for_decisions(Set_t, x, y_hat, z_hat, s, Set_i, w_hat, u)
    summary.to_csv(os.path.join(gen_dir, "Summary_decisions.csv"), index=False)

    #########################################################################################################################################################################################################################################################################################################################