from doopl.factory import *
import pandas as pd
import numpy as np
from functions import *
import os
from os.path import dirname, abspath, join
from datetime import datetime
from datetime import timedelta


def first_stage(sets, parameters, mod_first, ops_first, gen_dir):
    #Desaggregate parameters

    #sets
    Set_i = sets[0]
    Set_j = sets[1]
    Set_p = sets[2]
    Set_l = sets[3]
    Set_k = sets[5]
    Set_t = sets[6]

    #parameters
    M = parameters[12]
    rho = sets[4]
    CR_f = parameters[0]
    CR_v = parameters[1]
    CP_f = parameters[2]
    CT = parameters[3]
    CT2 = parameters[5]
    CT3 = parameters[6]
    CT4 = parameters[7]
    V_average = parameters[10]
    r_estimation = parameters[11]
    MA = parameters[15]
    tau = parameters[16]
    _beta = parameters[18]
    _lambda = parameters[19]
    eta = parameters[9]
    alpha = parameters[14]
    theta = parameters[13]
    delta = parameters[17]
    omega = parameters[20]
    CT_ik = parameters[4]
    d = parameters[8]
    CB_ini = parameters[23]
    CB = penalties_table(Set_t, CB_ini)

    # with create_opl_model(model=mod, data=dat) as opl:
    mod = mod_first
    ops = ops_first
    log_file = join(gen_dir, "MobileFactories_First_Stage.log")

    with create_opl_model(model=mod) as opl:
        opl.apply_ops_file(ops)

        # Set inputs to the model
        opl.set_input("Set_i", Set_i)
        opl.set_input("Set_j", Set_j)
        opl.set_input("Set_p", Set_p)
        opl.set_input("Set_l", Set_l)
        opl.set_input("Set_k", Set_k)
        opl.set_input("Set_t", Set_t)
        opl.set_input("_M", M)
        opl.set_input("_rho", rho)
        opl.set_input("_CR_f", CR_f)
        opl.set_input("_CR_v", CR_v)
        opl.set_input("_CP_f", CP_f)
        opl.set_input("_CT", CT)
        opl.set_input("_CT2", CT2)
        opl.set_input("_CT3", CT3)
        opl.set_input("_CT4", CT4)
        opl.set_input("_V_average", V_average)
        opl.set_input("_r_estimation", r_estimation)
        opl.set_input("_MA", MA)
        opl.set_input("_tau", tau)
        opl.set_input("_beta_ini", _beta)
        opl.set_input("_lambda_ini", _lambda)
        opl.set_input("_eta", eta)
        opl.set_input("_alpha", alpha)
        opl.set_input("_theta", theta)
        opl.set_input("_delta", delta)
        opl.set_input("_omega", omega)
        opl.set_input("_CT1_ik", CT_ik)
        opl.set_input("_d", d)
        opl.set_input("_CB", CB)

        opl.redirect_engine_log(log_file)
        start_time = datetime.now()
        opl.run()
        run_time = datetime.now()
        first_stage_time = (run_time - start_time).total_seconds()

        #print(opl.objective_value)
        relocation_cost = np.ceil(opl.get_table("cost_relocation", as_pandas=False)[0][0])
        production_cost = np.ceil(opl.get_table("cost_production", as_pandas=False)[0][0])
        shipments_drone_cost = np.ceil(opl.get_table("cost_drones", as_pandas=False)[0][0])
        shipments_land_cost = np.ceil(opl.get_table("cost_lands", as_pandas=False)[0][0])
        shipments_ship_cost = np.ceil(opl.get_table("cost_ships", as_pandas=False)[0][0])
        penalties_cost = np.ceil(opl.get_table("cost_lates", as_pandas=False)[0][0])

        # more to check
        v_hat = opl.get_table("v_hat_up_Set", as_pandas=True)
        v_hat.rename(columns={"p": "Product", "j": "Factory", "l": "Customer", "t": "Period", "value": "Value"},inplace=True)
        w_hat = opl.get_table("w_hat_Set", as_pandas=True)
        w_hat.rename(columns={"p": "Product", "j": "Factory", "k": "Harbor", "l": "Customer", "t": "Period", "value": "Value"},inplace=True)
        f_FS = opl.get_table("f_Set", as_pandas=True)
        f_FS.rename(columns={"p": "Product", "l": "Customer", "o": "Due date", "t": "Period", "value": "Value"},inplace=True)

        units_send_by_drone = v_hat.Value.sum()
        units_send_by_truck_ship = w_hat.Value.sum()
        units_delayed = calculation_units_delayed_per_period(f_FS)

        ###Print report to check objective functions
        check_file = os.path.join(gen_dir, "First_Stage.txt")
        if os.path.exists(check_file):
            os.remove(check_file)

        verification_file = open(check_file, 'a')
        verification_file.writelines("#####Costs first stage#####\n")
        verification_file.writelines("\n")
        verification_file.writelines("Units of products shipped by drone: " + str(units_send_by_drone) + "\n")
        verification_file.writelines("Units of products shipped by truck/ship: " + str(units_send_by_truck_ship) + "\n")
        verification_file.writelines("\n")
        verification_file.writelines("Total cost: " + str(np.ceil(opl.objective_value)) + "\n")
        verification_file.writelines("      - Relocation cost: " + str(relocation_cost) + "\n")
        verification_file.writelines("      - Production cost: " + str(production_cost) + "\n")
        verification_file.writelines("      - Shipments by drone cost: " + str(shipments_drone_cost) + "\n")
        verification_file.writelines("      - Shipments by land cost: " + str(shipments_land_cost) + "\n")
        verification_file.writelines("      - Shipments by ship cost: " + str(shipments_ship_cost) + "\n")
        verification_file.writelines("      - Late deliveries cost: " + str(penalties_cost) + "\n")
        verification_file.writelines("\n")
        for t in range(0, units_delayed.shape[0]):
            verification_file.writelines("Units of products delayed " + str(units_delayed.iloc[t]["Days"]) + " periods: " + str(units_delayed.iloc[t]["Value"]) + "\n")
        verification_file.close()

        x = opl.get_table("x_Set", as_pandas=True)
        x.rename(columns={"j": "Factory", "i": "Location_Origin", "a": "Location_Destination", "t": "Period", "value": "Value"}, inplace=True)
        x_hat = opl.get_table("x_hat_Set", as_pandas=True)
        x_hat.rename(columns={"j": "Factory", "i": "Location", "t": "Period", "value": "Value"}, inplace=True)
        y_hat = opl.get_table("y_hat_Set", as_pandas=True)
        y_hat.rename(columns={"p": "Product", "j": "Factory", "t": "Period", "value": "Value"}, inplace=True)

        x.to_csv(os.path.join(gen_dir, "x.csv"), index=False)
        x_hat.to_csv(os.path.join(gen_dir, "x_hat.csv"), index=False)
        y_hat.to_csv(os.path.join(gen_dir, "y_hat.csv"), index=False)

        # save all other variables
        # new directory to save all files
        firststage_dir = os.path.join(gen_dir, "firststage_results")
        if not os.path.isdir(firststage_dir):
            os.makedirs(firststage_dir)

        y = opl.get_table("y_Set", as_pandas=True)
        y.rename(columns={"j": "Factory", "i": "Location", "t": "Period", "value": "Value"}, inplace=True)
        v = opl.get_table("v_up_Set", as_pandas=True)
        v.rename(columns={"j": "Factory", "i": "Location", "l": "Customer", "t": "Period", "value": "Value"}, inplace=True)
        w = opl.get_table("w_Set", as_pandas=True)
        w.rename(columns={"j": "Factory", "i": "Location", "k": "Harbor", "t": "Period", "value": "Value"}, inplace=True)
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
        phi = opl.get_table("phi_Set", as_pandas=True)
        phi.rename(columns={"j": "Factory", "i": "Location", "value": "Value"}, inplace=True)
        b_hat_ini = opl.get_table("b_hat_Set", as_pandas=True)
        b_hat_ini.rename(columns={"j": "Factory", "value": "Value"}, inplace=True)

        # save everything in csv
        x.to_csv(os.path.join(firststage_dir, "x.csv"), index=False)
        y.to_csv(os.path.join(firststage_dir, "y.csv"), index=False)
        y_hat.to_csv(os.path.join(firststage_dir, "y_hat.csv"), index=False)
        v.to_csv(os.path.join(firststage_dir, "v.csv"), index=False)
        v_hat.to_csv(os.path.join(firststage_dir, "v_hat.csv"), index=False)
        w.to_csv(os.path.join(firststage_dir, "w.csv"), index=False)
        w_hat.to_csv(os.path.join(firststage_dir, "w_hat_FS.csv"), index=False)
        f_FS.to_csv(os.path.join(firststage_dir, "f.csv"), index=False)
        x_hat.to_csv(os.path.join(firststage_dir, "x_hat.csv"), index=False)
        n.to_csv(os.path.join(firststage_dir, "n.csv"), index=False)
        m.to_csv(os.path.join(firststage_dir, "m.csv"), index=False)
        u.to_csv(os.path.join(firststage_dir, "u.csv"), index=False)
        u_hat.to_csv(os.path.join(firststage_dir, "u_hat.csv"), index=False)
        m_hat.to_csv(os.path.join(firststage_dir, "m_hat.csv"), index=False)
        f_hat.to_csv(os.path.join(firststage_dir, "f_hat.csv"), index=False)
        phi.to_csv(os.path.join(firststage_dir, "phi.csv"), index=False)
        b_hat_ini.to_csv(os.path.join(firststage_dir, "b_hat_ini.csv"), index=False)

    with open(log_file, mode='r') as f:
        print(f.read())
        print("Logs were redirected to a file.")

    return x, x_hat, y_hat, phi, b_hat_ini, first_stage_time