from doopl.factory import *
from doopl.opl import *
import pandas as pd
import numpy as np
from functions import *
import os
from os.path import dirname, abspath, join
from datetime import datetime
from datetime import timedelta


def second_stage_initialization_warmup(sets, parameters, first_stage_param, warmup_parameters, mod_sec_ini, ops_sec_ini, gen_dir):
    # Desaggregate parameters

    # sets
    Set_i = sets[0]
    Set_j = sets[1]
    Set_p = sets[2]
    Set_l = sets[3]
    Set_h = sets[4]
    Set_k = sets[5]
    Set_t = sets[6]

    # parameters
    M = parameters[12]
    MT = parameters[22]
    CT = parameters[3]
    CT2 = parameters[5]
    V_average = parameters[10]
    r_estimation = parameters[11]
    tau = parameters[16]
    gamma = parameters[21]
    _beta = parameters[18]
    _lambda = parameters[19]
    eta = parameters[9]
    delta = parameters[17]
    b_hat = parameters[23]
    omega = parameters[20]
    CT_ik = parameters[4]
    d = parameters[8]
    CB_ini = parameters[24]
    CB = penalties_table(Set_t, CB_ini)

    # variables first stage
    x = first_stage_param[0]
    x_hat = first_stage_param[1]
    y_hat = first_stage_param[2]

    # variables for warmup
    f_warm = warmup_parameters[0]
    n_warm = warmup_parameters[1]
    s_warm = warmup_parameters[2]
    u_warm = warmup_parameters[3]
    w_warm = warmup_parameters[4]
    w_hat_warm = warmup_parameters[5]
    z_hat_warm = warmup_parameters[6]

    # with create_opl_model(model=mod, data=dat) as opl:
    mod = mod_sec_ini
    ops = ops_sec_ini
    log_file = join(gen_dir, "MobileFactories_Second_Stage_1.log")

    with create_opl_model(model=mod) as opl:
        opl.apply_ops_file(ops)

        # Set inputs to the model
        opl.set_input("Set_i", Set_i)
        opl.set_input("Set_j", Set_j)
        opl.set_input("Set_p", Set_p)
        opl.set_input("Set_l", Set_l)
        opl.set_input("Set_h", Set_h)
        opl.set_input("Set_k", Set_k)
        opl.set_input("Set_t", Set_t)
        opl.set_input("_M", M)
        opl.set_input("_MT", MT)
        opl.set_input("_CT", CT)
        opl.set_input("_CT2", CT2)
        opl.set_input("_V_average", V_average)
        opl.set_input("_r_estimation", r_estimation)
        opl.set_input("_tau", tau)
        opl.set_input("_gamma", gamma)
        opl.set_input("_beta_ini", _beta)
        opl.set_input("_lambda_ini", _lambda)
        opl.set_input("_eta", eta)
        opl.set_input("_delta", delta)
        opl.set_input("_b_hat", b_hat)
        opl.set_input("_omega", omega)
        opl.set_input("_CT1_ik", CT_ik)
        opl.set_input("_d", d)
        opl.set_input("_CB", CB)
        opl.set_input("_x", x)
        opl.set_input("_x_hat", x_hat)
        opl.set_input("_y_hat", y_hat)
        opl.set_input("_f_warm", f_warm)
        opl.set_input("_n_warm", n_warm)
        opl.set_input("_s_warm", s_warm)
        opl.set_input("_u_warm", u_warm)
        opl.set_input("_w_warm", w_warm)
        opl.set_input("_w_hat_warm", w_hat_warm)
        opl.set_input("_z_hat_warm", z_hat_warm)

        opl.redirect_engine_log(log_file)
        start_time = datetime.now()
        opl.run()
        run_time = datetime.now()
        second_stage_ini_time = (run_time - start_time).total_seconds()

        # print(opl.objective_value)
        shipments_drone_cost = opl.get_table("cost_drones", as_pandas=False)[0][0]
        shipments_land_cost = opl.get_table("cost_lands", as_pandas=False)[0][0]
        shipments_ship_cost = opl.get_table("cost_ships", as_pandas=False)[0][0]
        penalties_cost = opl.get_table("cost_lates", as_pandas=False)[0][0]

        ###Print report to check objective functions
        check_file = os.path.join(gen_dir, "Second_Stage_1.txt")
        if os.path.exists(check_file):
            os.remove(check_file)

        verification_file = open(check_file, 'a')
        verification_file.writelines("#####Costs second stage#####\n")
        verification_file.writelines("\n")
        verification_file.writelines("Total cost: " + str(opl.objective_value) + "\n")
        verification_file.writelines("      - Shipments by drone cost: " + str(shipments_drone_cost) + "\n")
        verification_file.writelines("      - Shipments by land cost: " + str(shipments_land_cost) + "\n")
        verification_file.writelines("      - Shipments by ship cost: " + str(shipments_ship_cost) + "\n")
        verification_file.writelines("      - Late deliveries cost: " + str(penalties_cost) + "\n")
        verification_file.writelines("\n")
        verification_file.close()

        z = opl.get_table("z_Set", as_pandas=True)
        z.rename(columns={"h": "Drone", "j": "Factory", "i": "Location", "l": "Customer", "t": "Period", "value": "Value"}, inplace=True)
        z_hat = opl.get_table("z_hat_Set", as_pandas=True)
        z_hat.rename(columns={"p": "Product", "h": "Drone", "j": "Factory", "l": "Customer", "t": "Period", "value": "Value"}, inplace=True)
        s = opl.get_table("s_Set", as_pandas=True)
        s.rename(columns={"h": "Drone", "o": "Origin", "a": "Destination", "t": "Period", "value": "Value"}, inplace=True)
        s_hat = opl.get_table("s_hat_Set", as_pandas=True)
        s_hat.rename(columns={"p": "Product", "h": "Drone", "o": "Origin", "a": "Destination", "t": "Period", "value": "Value"}, inplace=True)
        b = opl.get_table("b_Set", as_pandas=True)
        b.rename(columns={"h": "Drone", "o": "Starting position", "t": "Period", "value": "Value"}, inplace=True)
        e = opl.get_table("e_Set", as_pandas=True)
        e.rename(columns={"h": "Drone", "o": "Ending position", "t": "Period", "value": "Value"}, inplace=True)
        w = opl.get_table("w_Set", as_pandas=True)
        w.rename(columns={"j": "Factory", "i": "Location", "k": "Harbor", "t": "Period", "value": "Value"}, inplace=True)
        w_hat = opl.get_table("w_hat_Set", as_pandas=True)
        w_hat.rename(columns={"p": "Product", "j": "Factory", "k": "Harbor", "l": "Customer", "t": "Period", "value": "Value"}, inplace=True)
        f = opl.get_table("f_Set", as_pandas=True)
        f.rename(columns={"p": "Product", "l": "Customer", "o": "Due date", "t": "Period", "value": "Value"}, inplace=True)
        n = opl.get_table("n_Set", as_pandas=True)
        n.rename(columns={"p": "Product", "j": "Factory", "t": "Period", "value": "Value"}, inplace=True)
        m = opl.get_table("m_Set", as_pandas=True)
        m.rename(columns={"p": "Product", "k": "Harbor", "l": "Customer", "t": "Period", "value": "Value"}, inplace=True)
        u = opl.get_table("u_Set", as_pandas=True)
        u.rename(columns={"p": "Product", "k": "Harbor", "l": "Customer", "t": "Period", "value": "Value"}, inplace=True)
        u_hat = opl.get_table("u_hat_Set", as_pandas=True)
        u_hat.rename(columns={"p": "Product", "k": "Harbor", "l": "Customer", "t": "Period", "value": "Value"}, inplace=True)
        m_hat = opl.get_table("m_hat_Set", as_pandas=True)
        m_hat.rename(columns={"p": "Product", "l": "Customer", "t": "Period", "value": "Value"}, inplace=True)
        f_hat = opl.get_table("f_hat_Set", as_pandas=True)
        f_hat.rename(columns={"p": "Product", "l": "Customer", "o": "Due date", "t": "Period", "value": "Value"}, inplace=True)

        # new directory to save all files
        secondstageini_dir = os.path.join(gen_dir, "secondstage_results1")
        if not os.path.isdir(secondstageini_dir):
            os.makedirs(secondstageini_dir)

        z.to_csv(os.path.join(secondstageini_dir, "z.csv"), index=False)
        z_hat.to_csv(os.path.join(secondstageini_dir, "z_hat.csv"), index=False)
        s.to_csv(os.path.join(secondstageini_dir, "s.csv"), index=False)
        s_hat.to_csv(os.path.join(secondstageini_dir, "s.csv"), index=False)
        b.to_csv(os.path.join(secondstageini_dir, "b.csv"), index=False)
        e.to_csv(os.path.join(secondstageini_dir, "e.csv"), index=False)
        w.to_csv(os.path.join(secondstageini_dir, "w.csv"), index=False)
        w_hat.to_csv(os.path.join(secondstageini_dir, "w_hat.csv"), index=False)
        f.to_csv(os.path.join(secondstageini_dir, "f.csv"), index=False)
        n.to_csv(os.path.join(secondstageini_dir, "n.csv"), index=False)
        m.to_csv(os.path.join(secondstageini_dir, "m.csv"), index=False)
        u.to_csv(os.path.join(secondstageini_dir, "u.csv"), index=False)
        u_hat.to_csv(os.path.join(secondstageini_dir, "u_hat.csv"), index=False)
        m_hat.to_csv(os.path.join(secondstageini_dir, "m_hat.csv"), index=False)
        f_hat.to_csv(os.path.join(secondstageini_dir, "f_hat.csv"), index=False)


    with open(log_file, mode='r') as format:
        print(format.read())
        print("Logs were redirected to a file.")

    return z_hat, s, w, w_hat, u, f, n, e, m, m_hat, u_hat, second_stage_ini_time