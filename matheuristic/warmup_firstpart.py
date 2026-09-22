from doopl.factory import *
import os
from os.path import dirname, abspath, join
import pandas as pd
import numpy as np
from functions import *
from First_Stage import *
from Second_Stage_Initialization import *
from Second_Stage_Decomposition import *

def warmup_firstpart(sets, parameters, datadir, gen_dir):

    # extract all sets
    Set_i = sets[0]
    Set_j = sets[1]
    Set_p = sets[2]
    Set_l = sets[3]
    Set_h = sets[4]
    Set_k = sets[5]

    # extract all parameters
    demand_days = parameters[0]
    overlap_days = parameters[1]
    horizon_days = parameters[2]
    _lambda = parameters[3]
    _beta = parameters[4]
    cuts = parameters[5]
    CR_f = parameters[6]
    CR_v = parameters[7]
    CP_f = parameters[8]
    CT = parameters[9]
    CT_ik = parameters[10]
    CT2= parameters[11]
    CT3 = parameters[12]
    CT4 = parameters[13]
    d = parameters[14]
    eta = parameters[15]
    V_average = parameters[16]
    r_estimation = parameters[17]
    M = parameters[18]
    theta = parameters[19]
    alpha = parameters[20]
    MA = parameters[21]
    tau = parameters[22]
    delta = parameters[23]
    omega = parameters[24]
    gamma = parameters[25]
    MT = parameters[26]
    b_hat = parameters[27]
    CB_ini = parameters[28]
    x = parameters[29]
    x_hat = parameters[30]
    y_hat = parameters[31]
    customers = parameters[32]
    harbors = parameters[33]
    speed_ship = parameters[34]


    # new directory to save all files
    warmup_dir = os.path.join(gen_dir, "warmup_results")
    if not os.path.isdir(warmup_dir):
        os.makedirs(warmup_dir)

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
    mod_sec_ini = join(datadir, "Routing_drones.mod")
    ops_sec_ini = join(datadir, "Routing_drones.ops")

    z_hat_sec, s_sec, w_sec, w_hat_sec, u_sec, f_sec, n_sec, e_sec, m_sec, m_hat_sec, u_hat_sec, second_stage_time_sec = second_stage_initialization(sets, parameters_second_stage, first_stage_param, mod_sec_ini, ops_sec_ini, warmup_dir)

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

        z_hat_sec, s_sec, w_sec, w_hat_sec, u_sec, f_sec, n_sec, e_sec, m_sec, m_hat_sec, u_hat_sec, second_stage_time_sec = second_stage_decomposition(sets, parameters_second_stage, first_stage_param, previous_cut_parameters, mod_sec, ops_sec, warmup_dir, count_for_files)

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
    z_hat.to_csv(os.path.join(warmup_dir, "z_hat.csv"), index=False)
    s.to_csv(os.path.join(warmup_dir, "s.csv"), index=False)
    w.to_csv(os.path.join(warmup_dir, "w.csv"), index=False)
    w_hat.to_csv(os.path.join(warmup_dir, "w_hat.csv"), index=False)
    u.to_csv(os.path.join(warmup_dir, "u.csv"), index=False)
    f.to_csv(os.path.join(warmup_dir, "f.csv"), index=False)
    n.to_csv(os.path.join(warmup_dir, "n.csv"), index=False)

    total_time = sum(times)

    return f, n, s, u, w, w_hat, z_hat, total_time