/*********************************************
 * OPL 20.1.0.0 Model
 * Author: danie
 * Creation Date: 1 Nov 2023 at 13:14:19
 *********************************************/
 
execute 
{
  cplex.tilim = 10800
}

//SETS
	
	tuple Sets_values{
	int value;
	};

	{Sets_values} Set_i = ...; 
	{Sets_values} Set_j = ...;
	{Sets_values} Set_p = ...;
	{Sets_values} Set_l = ...;
	{Sets_values} Set_h = ...;
	{Sets_values} Set_k = ...;
	{Sets_values} Set_t = ...; 
	
	//Set of locations	
	int i = first(Set_i).value;		
	range locations = 1..i;
	 
	//Set of available mobile factories
	int j = first(Set_j).value;
	range factories = 1..j;

	//Set of products	
	int p = first(Set_p).value;		
	range products = 1..p;

	//Set of customers	
	int l = first(Set_l).value;		
	range customers = 1..l;

	//Set of drones	
	int h = first(Set_h).value;		
	range drones = 1..h;
	
	//Set of intermediary points
	int k = first(Set_k).value;
	range intermediaries = 1..k;
	
	//Set of periods
	int t = first(Set_t).value;		
	range periods = 1..t;
	
	//Set nodes drones
	range v = 1..i+l;
	
	//Set of all nodes
	range g = 1..i+l+k;
 	
	//Set of subsets for subroutes of 2 and 3
 	setof(int) subroutes_2[1..105]=[{1,2},{1,3},{1,4},{1,5},{1,6},{1,7},{1,8},{1,9},{1,10},{1,11},{1,12},{1,13},{1,14},{1,15},{2,3},{2,4},{2,5},{2,6},{2,7},{2,8},{2,9},{2,10},{2,11},{2,12},{2,13},{2,14},{2,15},{3,4},{3,5},{3,6},{3,7},{3,8},{3,9},{3,10},{3,11},{3,12},{3,13},{3,14},{3,15},{4,5},{4,6},{4,7},{4,8},{4,9},{4,10},{4,11},{4,12},{4,13},{4,14},{4,15},{5,6},{5,7},{5,8},{5,9},{5,10},{5,11},{5,12},{5,13},{5,14},{5,15},{6,7},{6,8},{6,9},{6,10},{6,11},{6,12},{6,13},{6,14},{6,15},{7,8},{7,9},{7,10},{7,11},{7,12},{7,13},{7,14},{7,15},{8,9},{8,10},{8,11},{8,12},{8,13},{8,14},{8,15},{9,10},{9,11},{9,12},{9,13},{9,14},{9,15},{10,11},{10,12},{10,13},{10,14},{10,15},{11,12},{11,13},{11,14},{11,15},{12,13},{12,14},{12,15},{13,14},{13,15},{14,15}];
	
	setof(int) subroutes_3[1..467]=[{1,2,3},{1,2,4},{1,2,5},{1,2,6},{1,2,7},{1,2,8},{1,2,9},{1,2,10},{1,2,11},{1,2,12},{1,2,13},{1,2,14},{1,2,15},{1,3,4},{1,3,5},{1,3,6},{1,3,7},{1,3,8},{1,3,9},{1,3,10},{1,3,11},{1,3,12},{1,3,13},{1,3,14},{1,3,15},{1,4,5},{1,4,6},{1,4,7},{1,4,8},{1,4,9},{1,4,10},{1,4,11},{1,4,12},{1,4,13},{1,4,14},{1,4,15},{1,5,6},{1,5,7},{1,5,8},{1,5,9},{1,5,10},{1,5,11},{1,5,12},{1,5,13},{1,5,14},{1,5,15},{1,6,7},{1,6,8},{1,6,9},{1,6,10},{1,6,11},{1,6,12},{1,6,13},{1,6,14},{1,6,15},{1,7,8},{1,7,9},{1,7,10},{1,7,11},{1,7,12},{1,7,13},{1,7,14},{1,7,15},{1,8,9},{1,8,10},{1,8,11},{1,8,12},{1,8,13},{1,8,14},{1,8,15},{1,9,10},{1,9,11},{1,9,12},{1,9,13},{1,9,14},{1,9,15},{1,10,11},{1,10,12},{1,10,13},{1,10,14},{1,10,15},{1,11,12},{1,11,13},{1,11,14},{1,11,15},{1,12,13},{1,12,14},{1,12,15},{1,13,14},{1,13,15},{1,14,15},{2,3,4},{2,3,5},{2,3,6},{2,3,7},{2,3,8},{2,3,9},{2,3,10},{2,3,11},{2,3,12},{2,3,13},{2,3,14},{2,3,15},{2,4,5},{2,4,6},{2,4,7},{2,4,8},{2,4,9},{2,4,10},{2,4,11},{2,4,12},{2,4,13},{2,4,14},{2,4,15},{2,5,6},{2,5,7},{2,5,8},{2,5,9},{2,5,10},{2,5,11},{2,5,12},{2,5,13},{2,5,14},{2,5,15},{2,6,7},{2,6,8},{2,6,9},{2,6,10},{2,6,11},{2,6,12},{2,6,13},{2,6,14},{2,6,15},{2,7,8},{2,7,9},{2,7,10},{2,7,11},{2,7,12},{2,7,13},{2,7,14},{2,7,15},{2,8,9},{2,8,10},{2,8,11},{2,8,12},{2,8,13},{2,8,14},{2,8,15},{2,9,10},{2,9,11},{2,9,12},{2,9,13},{2,9,14},{2,9,15},{2,10,11},{2,10,12},{2,10,13},{2,10,14},{2,10,15},{2,11,12},{2,11,13},{2,11,14},{2,11,15},{2,12,13},{2,12,14},{2,12,15},{2,13,14},{2,13,15},{2,14,15},{3,3,4},{3,3,5},{3,3,6},{3,3,7},{3,3,8},{3,3,9},{3,3,10},{3,3,11},{3,3,12},{3,3,13},{3,3,14},{3,3,15},{3,4,5},{3,4,6},{3,4,7},{3,4,8},{3,4,9},{3,4,10},{3,4,11},{3,4,12},{3,4,13},{3,4,14},{3,4,15},{3,5,6},{3,5,7},{3,5,8},{3,5,9},{3,5,10},{3,5,11},{3,5,12},{3,5,13},{3,5,14},{3,5,15},{3,6,7},{3,6,8},{3,6,9},{3,6,10},{3,6,11},{3,6,12},{3,6,13},{3,6,14},{3,6,15},{3,7,8},{3,7,9},{3,7,10},{3,7,11},{3,7,12},{3,7,13},{3,7,14},{3,7,15},{3,8,9},{3,8,10},{3,8,11},{3,8,12},{3,8,13},{3,8,14},{3,8,15},{3,9,10},{3,9,11},{3,9,12},{3,9,13},{3,9,14},{3,9,15},{3,10,11},{3,10,12},{3,10,13},{3,10,14},{3,10,15},{3,11,12},{3,11,13},{3,11,14},{3,11,15},{3,12,13},{3,12,14},{3,12,15},{3,13,14},{3,13,15},{3,14,15},{4,5,6},{4,5,7},{4,5,8},{4,5,9},{4,5,10},{4,5,11},{4,5,12},{4,5,13},{4,5,14},{4,5,15},{4,6,7},{4,6,8},{4,6,9},{4,6,10},{4,6,11},{4,6,12},{4,6,13},{4,6,14},{4,6,15},{4,7,8},{4,7,9},{4,7,10},{4,7,11},{4,7,12},{4,7,13},{4,7,14},{4,7,15},{4,8,9},{4,8,10},{4,8,11},{4,8,12},{4,8,13},{4,8,14},{4,8,15},{4,9,10},{4,9,11},{4,9,12},{4,9,13},{4,9,14},{4,9,15},{4,10,11},{4,10,12},{4,10,13},{4,10,14},{4,10,15},{4,11,12},{4,11,13},{4,11,14},{4,11,15},{4,12,13},{4,12,14},{4,12,15},{4,13,14},{4,13,15},{4,14,15},{5,6,7},{5,6,8},{5,6,9},{5,6,10},{5,6,11},{5,6,12},{5,6,13},{5,6,14},{5,6,15},{5,7,8},{5,7,9},{5,7,10},{5,7,11},{5,7,12},{5,7,13},{5,7,14},{5,7,15},{5,8,9},{5,8,10},{5,8,11},{5,8,12},{5,8,13},{5,8,14},{5,8,15},{5,9,10},{5,9,11},{5,9,12},{5,9,13},{5,9,14},{5,9,15},{5,10,11},{5,10,12},{5,10,13},{5,10,14},{5,10,15},{5,11,12},{5,11,13},{5,11,14},{5,11,15},{5,12,13},{5,12,14},{5,12,15},{5,13,14},{5,13,15},{5,14,15},{6,7,8},{6,7,9},{6,7,10},{6,7,11},{6,7,12},{6,7,13},{6,7,14},{6,7,15},{6,8,9},{6,8,10},{6,8,11},{6,8,12},{6,8,13},{6,8,14},{6,8,15},{6,9,10},{6,9,11},{6,9,12},{6,9,13},{6,9,14},{6,9,15},{6,10,11},{6,10,12},{6,10,13},{6,10,14},{6,10,15},{6,11,12},{6,11,13},{6,11,14},{6,11,15},{6,12,13},{6,12,14},{6,12,15},{6,13,14},{6,13,15},{6,14,15},{7,8,9},{7,8,10},{7,8,11},{7,8,12},{7,8,13},{7,8,14},{7,8,15},{7,9,10},{7,9,11},{7,9,12},{7,9,13},{7,9,14},{7,9,15},{7,10,11},{7,10,12},{7,10,13},{7,10,14},{7,10,15},{7,11,12},{7,11,13},{7,11,14},{7,11,15},{7,12,13},{7,12,14},{7,12,15},{7,13,14},{7,13,15},{7,14,15},{8,9,10},{8,9,11},{8,9,12},{8,9,13},{8,9,14},{8,9,15},{8,10,11},{8,10,12},{8,10,13},{8,10,14},{8,10,15},{8,11,12},{8,11,13},{8,11,14},{8,11,15},{8,12,13},{8,12,14},{8,12,15},{8,13,14},{8,13,15},{8,14,15},{9,10,11},{9,10,12},{9,10,13},{9,10,14},{9,10,15},{9,11,12},{9,11,13},{9,11,14},{9,11,15},{9,12,13},{9,12,14},{9,12,15},{9,13,14},{9,13,15},{9,14,15},{10,11,12},{10,11,13},{10,11,14},{10,11,15},{10,12,13},{10,12,14},{10,12,15},{10,13,14},{10,13,15},{10,14,15},{11,12,13},{11,12,14},{11,12,15},{11,13,14},{11,13,15},{11,14,15},{12,13,14},{12,13,15},{12,14,15},{13,14,15}];


 		
 //PARAMETERS
	
	tuple int_values{
	int value;
	};
	
	{int_values} _M = ...; 
 	{int_values} _MT=...;
	
	tuple float_values{
	float value;
	};
	
	{float_values} _CT = ...; 
	{float_values} _CT2=...; 
	{float_values} _V_average=...; 
	{float_values} _r_estimation=...; 	
	{float_values} _tau=...; 
	{float_values} _gamma=...;
	
	tuple for_vector_int{
	int index;
	int value;
	};
	
	{for_vector_int} _beta_ini = ...;
	{for_vector_int} _lambda_ini = ...;
	{for_vector_int} _x = ...;
	{for_vector_int} _x_hat = ...;
	{for_vector_int} _y_hat = ...;
	{for_vector_int} _m_ini_base = ...;
	{for_vector_int} _u_trans_ini = ...;
	
	tuple for_vector_float{
	int index;
	float value;
	};
	
	{for_vector_float} _eta = ...;
	
	tuple for_tables_int{
	int index1;
	int index2;
	int value;
	};
	
	{for_tables_int} _delta = ...;
	{for_tables_int} _b_hat = ...; 
	{for_tables_int} _omega = ...;
	{for_tables_int} _n_ini = ...;
	{for_tables_int} _e_ini = ...;
	{for_tables_int} _m_hat_ini = ...;
	{for_tables_int} _accu_lambda = ...;

	tuple for_tables_float{
	int index1;
	int index2;
	float value;
	};
	
	{for_tables_float} _CT1_ik = ...;
	{for_tables_float} _d = ...;
	{for_tables_float} _CB = ...;

	int M = first(_M).value; /*A big number*/;
 	int MT = first(_MT).value; /*Maximum time for flying in a period for drones*/;
 	float CT = first(_CT).value; /*Transport cost per kilometer for shipping by drone*/;
 	float CT2 = first(_CT2).value; /*Fixed cost for shipping by ship in any period*/;
	float V_average = first(_V_average).value; /*Average speed when a factory is being relocated*/;
	float r_estimation = first(_r_estimation).value; /*Set-up time for relocating a factory*/;	
	float tau = first(_tau).value; /*Capacity in product weight of a drone*/;
	float gamma = first(_gamma).value; /*Speed of the drone*/;		
	int beta_ini[1..k*l*t] = [index : val | <index,val> in _beta_ini]; /*Availability of the ship to sail from intermediary point k to customer l in period t*/;
	int beta[f in intermediaries, n in customers, v in periods] = beta_ini[v+t*(n-1)+l*t*(f-1)]; 	
	int lambda_ini[1..p*l*t] = [index : val | <index,val> in _lambda_ini]; /*The demand for product p from client l in period t*/;
	int lambda[f in products, n in customers, v in periods] = lambda_ini[v+t*(n-1)+l*t*(f-1)];
	float eta[products] = [index : val | <index,val> in _eta]; /*Weight of product p*/;
	int delta[g][g] = [index1 : [index2 : val] | <index1, index2, val> in _delta]; /*Binary matrix if customer l is in drone coverage from location i*/;
	int b_hat[drones][locations] = [index1 : [index2 : val] | <index1, index2, val> in _b_hat]; /*Starting position of each drone h*/;
	int omega[customers][intermediaries] = [index1 : [index2 : val] | <index1, index2, val> in _omega]; /*Duration of shipment from intermediary k to customer l*/;
	float CT1_ik[locations][intermediaries] = [index1 : [index2 : val] | <index1, index2, val> in _CT1_ik]; /*Transport cost for shipping by land from location i to intermediary k*/;
	float d[g][g] = [index1 : [index2 : val] | <index1, index2, val> in _d]; /*Distance in kilometers from location g to location g*/;		
	float CB[periods][periods] = [index1 : [index2 : val] | <index1, index2, val> in _CB]; /*Backorder cost per unit of product unfulfilled in the due date*/;
	int LL=card(g);
 	int LI=card(locations);
 	int TT=card(periods);

	//New parameters that come from first stage
 	int x_ini[1..j*i*i*t] = [index : val | <index,val> in _x]; /*Binary variable if mobile factory j is relocated from location i to location g in period t*/;
	int x[f in factories, n in locations, o in locations, v in periods] = x_ini[v+t*(o-1)+i*t*(n-1)+i*i*t*(f-1)];
	int y_hat_ini[1..p*j*t] = [index : val | <index,val> in _y_hat]; /*Units of product p that mobile factory j produces in period t*/;
	int y_hat[f in products, n in factories, v in periods] = y_hat_ini[v+t*(n-1)+j*t*(f-1)];
	int x_hat_ini[1..j*i*t] = [index : val | <index,val> in _x_hat]; /*Binary variable if there is a mobile factory at node i at the beginning of period t*/;
	int x_hat[f in factories, n in locations, v in periods] = x_hat_ini[v+t*(n-1)+i*t*(f-1)]; 

	//New parameters that are from first week routing
	int n_ini[products][factories] = [index1 : [index2 : val] | <index1, index2, val> in _n_ini]; /*Initital inventory of product p at factory j*/;
	int e_ini[drones][v] = [index1 : [index2 : val] | <index1, index2, val> in _e_ini]; /*Binary parameter to now ending position of drone h in each node v*/;
	int m_ini_base[1..p*k*l] = [index : val | <index,val> in _m_ini_base]; /*Initital inventory of product p in intermediary k for customer l*/;
	int m_ini[f in products, n in intermediaries, v in customers] = m_ini_base[v+l*(n-1)+k*l*(f-1)];
	int m_hat_ini[products][customers] = [index1 : [index2 : val] | <index1, index2, val> in _m_hat_ini]; /*Accumulated inventory of product p in customer l*/;
	int accu_lambda[products][customers] = [index1 : [index2 : val] | <index1, index2, val> in _accu_lambda] /*Aggreagted demand for product p for customer l of the previous periods*/;
	int u_trans_ini[1..p*k*l*t] = [index : val | <index,val> in _u_trans_ini]; /*Products in transit from intermediary points*/;
	int u_trans[f in products, n in intermediaries, o in customers, v in periods] = u_trans_ini[v+t*(o-1)+l*t*(n-1)+l*k*t*(f-1)]; 
	
 //VARIABLES
	dvar boolean z[drones][factories][locations][customers][periods]; /*Binary variable if drone h goes from factory j at location i to customer l in period t*/;
	dvar int+ z_hat[products][drones][factories][customers][periods]; /*Units of product p to ship by drone h from the mobile facility j to customer l in period t*/; 
	dvar boolean s[drones][v][v][periods]; /*Binary variable if drone h goes through arc (a,g) in period t*/;
 	dvar int+ s_hat[products][drones][v][v][periods]; /*Units of product p that drone h goes through arc (a,g)in{I L} in period t*/;
 	dvar boolean b[drones][v][periods]; /*Binary variable if drone h is in the mobile factory at node i at the beginning of period t*/;
	dvar boolean e[drones][v][periods];  /*Binary variable if drone h is in the mobile factory at node i at the end of period t*/;
	dvar boolean w[factories][locations][intermediaries][periods]; /*Binary variable if mobile facility j at location i transports products to intermediary k in period t*/;
 	dvar int+ w_hat[products][factories][intermediaries][customers][periods]; /*Units of product p to ship by traditional way from mobile facility j to intermediary k in period t*/;
 	dvar int+ f[products][customers][periods][periods]; /*Units of product p unfulfilled to customer l in period t*/;
	
	dvar int+ n[products][factories][periods]; /*Units of product p in inventory in mobile factory j in period t*/;
	dvar boolean s_prime[drones][factories][locations][locations][periods]; /*Binary variable if drone h moves with relocation of factory j from location i to location g in period t*/;
	dvar int+ m[products][intermediaries][customers][periods]; /*Units of product p available at intermediary k for customer l in period t*/;
 	dvar int+ u[products][intermediaries][customers][periods]; /*Units of product p to ship from intermediary k to customer l in period t*/;	
 	dvar int+ u_hat[products][intermediaries][customers][periods]; /*Units of product p to receive from intermediary k to customer l in period t*/;	
	dvar int+ m_hat[products][customers][periods]; /*Accumulation of units of product p received by customer l in period t*/;
	dvar int+ f_hat[products][customers][periods][periods]; /*Units of product p ship in advance to customer l in period t*/;	
		
	dvar float+ cost_drone;
	dvar float+ cost_land;
	dvar float+ cost_ship;
	dvar float+ cost_late;
		
//OBJECTIVE
	dexpr float total_cost=
		sum(h in drones, a in v, o in v, t in periods)CT*d[a][o]*s[h][a][o][t]+
		sum(j in factories, i in locations, k in intermediaries, t in periods)CT1_ik[i][k]*w[j][i][k][t]+
		sum(p in products, k in intermediaries, l in customers, t in periods)CT2*u[p][k][l][t]+
		sum(p in products, l in customers, t in periods, o in periods: o<t+1)CB[o][t]*f[p][l][o][t]
		;
		
	minimize total_cost;		

	subject to
	{
		cost_drone==sum(h in drones, a in v, o in v, t in periods)CT*d[a][o]*s[h][a][o][t];
	  	cost_land==sum(j in factories, i in locations, k in intermediaries, t in periods)CT1_ik[i][k]*w[j][i][k][t];
	  	cost_ship==sum(p in products, k in intermediaries, l in customers, t in periods)CT2*u[p][k][l][t];
	  	cost_late==sum(p in products, l in customers, t in periods, o in periods: o<t+1)CB[o][t]*f[p][l][o][t];
	   
	 
	  //Inventory constraint for each factory 1
  	  	C10:forall(p in products, j in factories, t in periods:t>1)
  	  		n[p][j][t]==n[p][j][t-1]+y_hat[p][j][t]-sum(h in drones, l in customers)z_hat[p][h][j][l][t]-sum(k in intermediaries, l in customers)w_hat[p][j][k][l][t];
  	 	
  	  //Inventory constraint for each factory 2
  	  	C11:forall(p in products, j in factories, t in periods:t==1)
  	  		n[p][j][t]==n_ini[p][j]+y_hat[p][j][t]-sum(h in drones, l in customers)z_hat[p][h][j][l][t]-sum(k in intermediaries, l in customers)w_hat[p][j][k][l][t];
  	  		
  	  //Not shipment of products done the same day
  	  	C12_1:forall(p in products, j in factories, t in periods:t>1)
  	  		sum(h in drones, l in customers)z_hat[p][h][j][l][t]+sum(k in intermediaries, l in customers)w_hat[p][j][k][l][t]<=n[p][j][t-1];	
  	  	
  	  	C12_2:forall(p in products, j in factories, t in periods:t==1)
  	  		sum(h in drones, l in customers)z_hat[p][h][j][l][t]+sum(k in intermediaries, l in customers)w_hat[p][j][k][l][t]<=n_ini[p][j];
  	  	
  	  	C12_3:forall(p in products, l in customers)
  	  		sum(h in drones, j in factories, t in periods)z_hat[p][h][j][l][t]+sum(k in intermediaries, j in factories, t in periods)w_hat[p][j][k][l][t]<=sum(t in periods)lambda[p][l][t]+accu_lambda[p][l]-m_hat_ini[p][l]-sum(k in intermediaries)m_ini[p][k][l]-sum(k in intermediaries, t in periods)u_trans[p][k][l][t];
  	  		
  	  //Not allowing shipments by drone from a location where there is not factory or a factory that is moving
  	  	C13:forall(h in drones, j in factories, i in locations, o in locations, l in customers, t in periods)
  	  		x[j][i][o][t]+sum(a in periods: a>t-1 && (a<=t+(d[i][o]/(24*V_average))+r_estimation))z[h][j][i][l][a]<=x_hat[j][i][t];
  	  	
  	  //Not allowing shipments by land from a location where there is not factory or it is moving
  	  	C14:forall(j in factories, i in locations, o in locations, k in intermediaries, t in periods)
  	  		x[j][i][o][t]+sum(a in periods: a>t && (a<=t+(d[i][o]/(24*V_average))+r_estimation))w[j][i][k][a]<=x_hat[j][i][t];
  	   
  	  //Not allowing shipments byy land from locations where there is not factory
  	  	C15:forall(j in factories, i in locations, k in intermediaries, t in periods)
  	   		w[j][i][k][t]<=x_hat[j][i][t];
  	   
  	  //Only ship units if there is a shipment scheduled
	    C16:forall(p in products, h in drones, j in factories, l in customers, t in periods)
	    	z_hat[p][h][j][l][t]<=M*sum(i in locations)z[h][j][i][l][t];
	    	
	  //Relation between continouos and binary variable 1
  		C17:forall(h in drones, j in factories, i in locations, l in customers, t in periods)
  		  	z[h][j][i][l][t]<=sum(a in v)s[h][i][a][t];
  	   
  	  //Relation between continuous and binary variable 2
  		C18:forall(h in drones, j in factories, i in locations, l in customers, t in periods)
  		  	z[h][j][i][l][t]<=sum(a in v)s[h][a][l+LI][t];
  	  	
  	  //Route does not visit locations that not have factories  	
  		C19:forall(h in drones, i in locations, o in v, t in periods)
  		  	s[h][i][o][t]<=M*sum(j in factories)x_hat[j][i][t];
  		
  	   //Drones cannot end the route in a new location of a factorie that is being relocated 
  	  	C20:forall(h in drones, j in factories, i in locations, o in locations, t in periods, a in v: a != i)
  	  		s[h][a][o][t]<=(1-x[j][i][o][t]);
  	  	
  	   //Relation of variable of movements with starting position of drones 	
		C61:forall(h in drones, j in factories, i in locations, a in locations, t in periods)
			s_prime[h][j][i][a][t]==x[j][i][a][t]*b[h][i][t];	  
	 
  	   //Relation between drone movements by land and routes 1
  		C24:forall(h in drones, i in locations, a in locations, o in v, t in periods)
  		  	s[h][i][o][t]<=1-s_prime[h][j][i][a][t];
  		  	
  	   //Relation between drone movements by land and routes 2
  		C25:forall(h in drones, i in locations, a in locations, o in v, t in periods)
  		  	s[h][o][i][t]<=1-s_prime[h][j][a][i][t];
  		  	
  	   //Relation between drone movements by land and routes 3
  		C26:forall(h in drones, i in locations, a in v, t in periods)
  		  	1-s[h][i][a][t]>=sum(j in factories, o in locations)s_prime[h][j][i][o][t];
  		
  	   //Relation between drone movements by land and routes 4
  		C27:forall(h in drones, i in locations, a in v, t in periods)
  		  	1-s[h][a][i][t]>=sum(j in factories, o in locations)s_prime[h][j][o][i][t];  	
  	  	
  	   //Maximum distance of coverage for each drone from locations to customers
  	  	C28:forall(h in drones,a in v, o in v, t in periods)
  	  		s[h][a][o][t]<=delta[a][o];
  	  		
  	   //Relation between binary and continuous variables for routing and drone capacity
  		C29:forall(h in drones, a in v, o in v, t in periods)
  		  	sum(p in products)eta[p]*s_hat[p][h][a][o][t]<=tau*s[h][a][o][t];
  	  	
  	   //Relation between continuous variables of unit shipped from a facility and units travel through each arc
  	  	C30:forall(p in products, h in drones, l in customers, t in periods)
  	  		sum(o in v)s_hat[p][h][o][l+LI][t]>=sum(j in factories)z_hat[p][h][j][l][t]+sum(o in v)s_hat[p][h][l+LI][o][t];
  	  		
  	  	C30_2:forall(p in products, h in drones, t in periods, o in v, a in v)
  	  		s_hat[p][h][o][a][t]<=sum(j in factories, l in customers)z_hat[p][h][j][l][t];
  	
  	   //Time that drones can fly each period
  	 	C31:forall(h in drones, t in periods)
  			sum(a in v, o in v)d[a][o]*s[h][a][o][t]<=MT*gamma;
  	 
  	  //Subroute elimination with DFJ
  	    C32_1:forall(h in drones, t in periods, k in 1..105)
  	  	   	sum(a,o in subroutes_2[k])s[h][a][o][t] <= card(subroutes_2[k])-1*(1-sum(a in subroutes_2[k])b[h][a][t]);
  	  
  	  	C32_2:forall(h in drones, t in periods, k in 1..467)
  	  		sum(a,o in subroutes_3[k])s[h][a][o][t] <= card(subroutes_3[k])-1*(1-sum(a in subroutes_3[k])b[h][a][t]);
  	  	
  		C32_3:forall(h in drones, t in periods, a in v, o in v: a==o)
  		 	s[h][a][o][t]==0;
  		
  	  //All drones visit clients and leave them
  		C33:forall(h in drones, l in customers, t in periods)
  		  	sum(a in v)s[h][a][l+LI][t]==sum(a in v)s[h][l+LI][a][t];
  	  
  	  //Start and end in a factory	
  		C34:forall(h in drones, i in locations, t in periods)
  		  	sum(a in v)s[h][i][a][t]+sum(j in factories, a in locations)s_prime[h][j][i][a][t]+e[h][i][t]==sum(a in v)s[h][a][i][t]+sum(j in factories, a in locations)s_prime[h][j][a][i][t]+b[h][i][t];
  	
  	  //Starting of a drone route according to the starting position
 		C35:forall(h in drones, i in locations, t in periods)
 			sum(a in v)s[h][i][a][t]<=b[h][i][t];
 		
 	  //Ending of a drone route according to the ending position
 		C36:forall(h in drones, i in locations, t in periods)
 			sum(a in v)s[h][a][i][t]<=e[h][i][t];
 		
 	  //Position of the drone at the end and beginning of each day
  		C37_1:forall(h in drones, a in v, t in periods: t>1)
  		  	b[h][a][t]==e[h][a][t-1];
  		
  		C37_2:forall(h in drones, l in customers,t in periods)
  	    	e[h][l+LI][t]==0; 	 
  	 
  	   //Position of each drone in period 1
  		C38:forall(h in drones, o in v, t in periods: t==1)
  		  	b[h][o][t]==e_ini[h][o];
  	 
  	  //A drone can only finish where a factory is
  	    C39:forall(h in drones, i in locations, t in periods: t < TT)
  	    	e[h][i][t]<=sum(j in factories)x_hat[j][i][t+1];	
  		
  	  //Relation between binary and continuous variables of shipments by ship
	 	C40:forall(p in products, j in factories, k in intermediaries, l in customers, t in periods)
  	  		w_hat[p][j][k][l][t]<=M*sum(i in locations)w[j][i][k][t];
  	  		
  	  //Inventory in each intermediary point 1
  	  	C41:forall(p in products, k in intermediaries, l in customers, t in periods:t>1)
  	  		m[p][k][l][t]==m[p][k][l][t-1]+sum(j in factories)w_hat[p][j][k][l][t]-u[p][k][l][t];
  	  
  	  //Inventory in each intermediary point 2
  	  	C42:forall(p in products, k in intermediaries, l in customers, t in periods:t==1)
  	  		m[p][k][l][t]==m_ini[p][k][l]+sum(j in factories)w_hat[p][j][k][l][t]-u[p][k][l][t];
  	  
  	  //Availability of ships in each intermediary point 1
  	  	C43_1:forall(p in products, k in intermediaries, l in customers, t in periods:t>1)
  	  		u[p][k][l][t]<=beta[k][l][t]*m[p][k][l][t-1];
 
  	  	C43_2:forall(p in products, k in intermediaries, l in customers, t in periods:t==1)
  	  		u[p][k][l][t]<=beta[k][l][t]*m_ini[p][k][l];
  	  
  	  //Balance of shipments by ship with the due dates 1
  	  	C44:forall(p in products, k in intermediaries, l in customers, t in periods: t>omega[l][k])
  	  		u_hat[p][k][l][t]==u[p][k][l][t-omega[l][k]]+u_trans[p][k][l][t];
  	  
  	  //Balance of shipments by ship with the due dates 2 
  	  	C45:forall(p in products, k in intermediaries, l in customers, t in periods: t<=omega[l][k])
  	  		u_hat[p][k][l][t]==u_trans[p][k][l][t];

  	  //Inventory in each client 1
  	  	C46:forall(p in products, l in customers, t in periods:t>1)
  	  		m_hat[p][l][t]==m_hat[p][l][t-1]+sum(h in drones, j in factories)z_hat[p][h][j][l][t]+sum(k in intermediaries)u_hat[p][k][l][t];
  	  
  	  //Inventory in each client 2
  	  	C47:forall(p in products, l in customers, t in periods:t==1)
  	  		m_hat[p][l][t]==m_hat_ini[p][l]+sum(h in drones, j in factories)z_hat[p][h][j][l][t]+sum(k in intermediaries)u_hat[p][k][l][t];
  	  
  	  //Late deliveries
  	  	C48:forall(p in products, l in customers, t in periods, o in periods: o<t+1 && lambda[p][l][o]>0)
  	  		lambda[p][l][o]-m_hat[p][l][t]+sum(a in periods: a>=1 && a<o)lambda[p][l][a]+accu_lambda[p][l]==f[p][l][o][t]-f_hat[p][l][o][t];
  	  		
  	  //Fulfillment of the total demand
  	  	C49:forall(p in products, l in customers, t in periods: t==TT)
  	  		m_hat[p][l][t]==sum(a in periods)lambda[p][l][a]+accu_lambda[p][l];
	
	  }
	  

tuple z_Tuple{int h;int j;int i;int l;int t;int value;};
{z_Tuple} z_Set = {<h,j,i,l,t,z[h][j][i][l][t]> | h in drones,j in factories,i in locations,l in customers,t in periods};

tuple z_hat_Tuple{int p;int h;int j;int l;int t;int value;};
{z_hat_Tuple} z_hat_Set = {<p,h,j,l,t,z_hat[p][h][j][l][t]> | p in products,h in drones,j in factories,l in customers,t in periods};

tuple s_Tuple{int h;int o;int a;int t;int value;};
{s_Tuple} s_Set = {<h,o,a,t,s[h][o][a][t]> | h in drones,o in v,a in v,t in periods};

tuple s_hat_Tuple{int p;int h;int o;int a;int t;int value;};
{s_hat_Tuple} s_hat_Set = {<p,h,o,a,t,s_hat[p][h][o][a][t]> | p in products,h in drones,o in v,a in v,t in periods};

tuple b_Tuple{int h;int o;int t;int value;};
{b_Tuple} b_Set = {<h,o,t,b[h][o][t]> | h in drones,o in v,t in periods};

tuple e_Tuple{int h;int o;int t;int value;};
{e_Tuple} e_Set = {<h,o,t,e[h][o][t]> | h in drones,o in v,t in periods};

tuple w_Tuple{int j;int i;int k;int t;int value;};
{w_Tuple} w_Set = {<j,i,k,t,w[j][i][k][t]> | j in factories,i in locations, k in intermediaries,t in periods};

tuple w_hat_Tuple{int p;int j;int k;int l;int t;int value;};
{w_hat_Tuple} w_hat_Set = {<p,j,k,l,t,w_hat[p][j][k][l][t]> | p in products,j in factories, k in intermediaries,l in customers,t in periods};

tuple f_Tuple{int p;int l;int o;int t;int value;};
{f_Tuple} f_Set = {<p,l,o,t,f[p][l][o][t]> | p in products,l in customers, o in periods,t in periods};

tuple n_Tuple{int p;int j;int t;int value;};
{n_Tuple} n_Set = {<p,j,t,n[p][j][t]> | p in products,j in factories,t in periods};

tuple m_Tuple{int p;int k;int l;int t;int value;};
{m_Tuple} m_Set = {<p,k,l,t,m[p][k][l][t]> | p in products,k in intermediaries,l in customers, t in periods};

tuple u_Tuple{int p;int k;int l;int t;int value;};
{u_Tuple} u_Set = {<p,k,l,t,u[p][k][l][t]> | p in products,k in intermediaries,l in customers,t in periods};

tuple u_hat_Tuple{int p;int k;int l;int t;int value;};
{u_hat_Tuple} u_hat_Set = {<p,k,l,t,u_hat[p][k][l][t]> | p in products,k in intermediaries,l in customers,t in periods};

tuple m_hat_Tuple{int p;int l;int t;int value;};
{m_hat_Tuple} m_hat_Set = {<p,l,t,m_hat[p][l][t]> | p in products,l in customers,t in periods};

tuple f_hat_Tuple{int p;int l;int o;int t;int value;};
{f_hat_Tuple} f_hat_Set = {<p,l,o,t,f_hat[p][l][o][t]> | p in products,l in customers, o in periods,t in periods};

tuple cost{ float value;};
{cost} cost_drones = {<cost_drone>};
{cost} cost_lands = {<cost_land>};	
{cost} cost_ships = {<cost_ship>};	
{cost} cost_lates = {<cost_late>};	