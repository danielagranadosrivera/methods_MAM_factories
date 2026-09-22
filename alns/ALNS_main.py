import pandas as pd
import numpy as np
from main_greedy_MF import *
from functions_greedy_MF import *
from functions_ALNS import *
import os
from os.path import dirname, abspath, join

# Set up of directories
gen_dir = os.path.join(dirname(abspath(__file__)), "data", "output")
if not os.path.isdir(gen_dir):
    os.makedirs(gen_dir)



#Read inputs
#########################################################################################################################################################################################################################################################################################################################

# read files
parameters = np.genfromtxt(os.path.join("data", "input", "parameters.csv"), delimiter=',', skip_header=True).astype("float")  # coordinates of harbors
locations = np.genfromtxt(os.path.join("data", "input", "locations.csv"), delimiter=',', skip_header=True).astype("float")  # coordinates of locations for mobile factories
customers = np.genfromtxt(os.path.join("data", "input", "customers.csv"), delimiter=',', skip_header=True).astype("float")  # coordinates of customers
harbors = np.genfromtxt(os.path.join("data", "input", "harbors.csv"), delimiter=',', skip_header=True).astype("float")  # coordinates of harbors
beta = np.genfromtxt(os.path.join("data", "input", "beta.csv"), delimiter=',', skip_header=True).astype("int")  # schedule of ships
lambda_ = np.genfromtxt(os.path.join("data", "input", "lambda.csv"), delimiter=',', skip_header=True).astype("int")  # demand for customers
eta = np.genfromtxt(os.path.join("data", "input", "eta.csv"), delimiter=',', skip_header=True).astype("float")  # weight of product p
theta = np.genfromtxt(os.path.join("data", "input", "theta.csv"), delimiter=',', skip_header=True).astype("int")  # binary matrix if mobile factory in i can produce product p
alpha = np.genfromtxt(os.path.join("data", "input", "alpha.csv"), delimiter=',', skip_header=True).astype("float")  # cross-sectional area of product p

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
d_i_l = distances(locations, customers) # distance from locations to customers
max_delta = parameters[17][1] # maximum distance a drone can travel
delta_i_l = delta_calculation(d_i_l, max_delta) # binary matrix if customer l is in drone coverage from location i
beta = pd.DataFrame(beta, columns=["Harbor", "Customer", "Cluster", "Period", "Value"])  # change beta to dataframe to filter easily
speed_ship = parameters[18][1] # speed of ships
omega = calculation_omega(customers, harbors, speed_ship) # duration of shipment from intermediary k to customer l
gamma = parameters[15][1] # flying speed of drones in kilometers per hour
Max_Time = parameters[16][1] # maximum allowed drone route time per day in hours
tau = parameters[14][1] # capacity in product weight of a drone
nodes = np.concatenate((locations, customers), axis=0)
d_nodes = distances(nodes, nodes)



# Greedy initial solution
#########################################################################################################################################################################################################################################################################################################################
multiplier = 0.08 # 0.08 # 1 # multiplier for score of factories
x,x_hat,y_hat,n,b,e,z,z_hat,w,w_hat,u,u_hat,f,m_hat,s,lambda_ = greedy_initial_solution(parameters,locations,customers,harbors,beta,lambda_,eta,theta,alpha,multiplier)
evaluation_parameters = locations, CR_f, CR_v, alpha, CP_f, Set_p, CT, customers, CT1, harbors, CT2, CB_ini, d_i_l, delta_i_l, beta, omega, eta, d_nodes, locations, gamma,tau,Max_Time,Set_i,Set_j,Set_l,Set_h,Set_k,Set_t
initial_solution = solution(x, y_hat, s, w, u, f, x_hat, n, z, z_hat, b, e, w_hat, u_hat, m_hat, lambda_, evaluation_parameters)
initial_cost = initial_solution.objective()



# ALNS
#########################################################################################################################################################################################################################################################################################################################

# parameters for ALNS
seed = 872971
updating_period = 5 # 1 # 5 # number of periods to update the weights and temperature in simulated annealing
max_time_alns = 300 # stopping criteria
destroy_operators = deallocate_based_f, deallocate_from_drone_random, deallocate_from_truck_ship_random
repair_operators = send_by_drone, send_by_ship

# for internal simmulated annealing
T_0 = 1000 # 0.000001 # 1000
alpha_sa = 0.99 # 1 # 0.99
seed_sa = 23834

# initialize weigths and probabilities
weights_destroy = [1, 1, 1]
weights_repair = [1, 1]


# run ALNS
np.random.seed(seed)
alns_method = ALNS(initial_solution, destroy_operators, repair_operators, weights_destroy, weights_repair, updating_period, alpha_sa, T_0, max_time_alns, seed, seed_sa)
alns_solution = alns_method.run()



# Compute costs and create dataframes all variables
#########################################################################################################################################################################################################################################################################################################################

# compute costs
relocation_cost = relocation_cost_calculation(alns_solution.x, locations, CR_f, CR_v)
production_cost = production_cost_calculation(alns_solution.y_hat, alpha, CP_f, Set_p)
shipments_drone_cost = shipments_drone_cost_calculation(alns_solution.s, CT, locations, customers)
shipments_land_cost = shipments_land_cost_calculation(alns_solution.w, CT1, locations, harbors)
shipments_ship_cost = shipments_ship_cost_calculation(alns_solution.u, CT2)
penalties_cost = penalties_cost_calculation(alns_solution.f, CB_ini)

total_cost = relocation_cost + production_cost + shipments_drone_cost + shipments_land_cost + shipments_ship_cost + penalties_cost


x = df_creation_four_index(alns_solution.x, names=["Factory","Location_Origin","Location_Destination","Period","Value"])
x_hat = df_creation_three_index(alns_solution.x_hat, names=["Factory","Location","Period","Value"])
y_hat = df_creation_three_index(alns_solution.y_hat, names=["Product", "Factory", "Period", "Value"])
n = df_creation_three_index(alns_solution.n, names=["Product","Factory","Period","Value"])
b = df_creation_three_index(alns_solution.b, names=["Drone","Starting position","Period","Value"])
e = df_creation_three_index(alns_solution.e, names=["Drone","Ending position","Period","Value"])
z = df_creation_five_index(alns_solution.z, names=["Drone","Factory","Location","Customer","Period","Value"])
z_hat = df_creation_five_index(alns_solution.z_hat, names=["Product","Drone","Factory","Customer","Period","Value"])
w = df_creation_four_index(alns_solution.w, names=["Factory","Location","Harbor","Period","Value"])
w_hat = df_creation_five_index(alns_solution.w_hat, names=["Product","Factory","Harbor","Customer","Period","Value"])
u = df_creation_four_index(alns_solution.u, names=["Product","Harbor","Customer","Period","Value"])
u_hat = df_creation_four_index(alns_solution.u_hat, names=["Product","Harbor","Customer","Period","Value"])
f = df_creation_four_index(alns_solution.f, names=["Product","Customer","Due date","Period","Value"])
m_hat = df_creation_three_index(alns_solution.m_hat, names=["Product", "Customer", "Period", "Value"])
s = df_creation_four_index(alns_solution.s, names=["Drone","Origin","Destination","Period","Value"])



# Print results
#########################################################################################################################################################################################################################################################################################################################

# print cvs with variables
x.to_csv(os.path.join(gen_dir, "x.csv"), index=False)
x_hat.to_csv(os.path.join(gen_dir, "x_hat.csv"), index=False)
y_hat.to_csv(os.path.join(gen_dir, "y_hat.csv"), index=False)
n.to_csv(os.path.join(gen_dir, "n.csv"), index=False)
b.to_csv(os.path.join(gen_dir, "b.csv"), index=False)
e.to_csv(os.path.join(gen_dir, "e.csv"), index=False)
z.to_csv(os.path.join(gen_dir, "z.csv"), index=False)
z_hat.to_csv(os.path.join(gen_dir, "z_hat.csv"), index=False)
w.to_csv(os.path.join(gen_dir, "w.csv"), index=False)
w_hat.to_csv(os.path.join(gen_dir, "w_hat.csv"), index=False)
u.to_csv(os.path.join(gen_dir, "u.csv"), index=False)
u_hat.to_csv(os.path.join(gen_dir, "u_hat.csv"), index=False)
f.to_csv(os.path.join(gen_dir, "f.csv"), index=False)
m_hat.to_csv(os.path.join(gen_dir, "m_hat.csv"), index=False)
s.to_csv(os.path.join(gen_dir, "s.csv"), index=False)


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
solution_file.writelines("#####Summary instance from ALNS#####\n")
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
summary.to_csv(os.path.join(gen_dir, "Summary_decisions.csv"), index=False)

