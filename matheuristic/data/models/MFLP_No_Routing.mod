/*********************************************
 * OPL 20.1.0.0 Model
 * Author: danie
 * Creation Date: 1 Nov 2023 at 13:14:19
 *********************************************/

execute 
{
  cplex.tilim = 7800
}

//SETS

	tuple Sets_values{
	int value;
	};
	
	{Sets_values} Set_i = ...; 
	{Sets_values} Set_j = ...;
	{Sets_values} Set_p = ...;
	{Sets_values} Set_l = ...;
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
 
//PARAMETERS

	tuple int_values{
	int value;
	};
	
	{int_values} _M = ...; 
 	{int_values} _rho = ...; 
	
	tuple float_values{
	float value;
	};
	
	{float_values} _CR_f = ...; 
	{float_values} _CR_v = ...;
 	{float_values} _CP_f = ...; 
 	{float_values} _CT = ...;
	{float_values} _CT2 = ...; 
	{float_values} _CT3 = ...; 
 	{float_values} _CT4 = ...; 
	{float_values} _V_average = ...; 
	{float_values} _r_estimation = ...; 
	{float_values} _MA = ...; 
	{float_values} _tau = ...;

	tuple for_vector_int{
	int index;
	int value;
	};
	
	{for_vector_int} _beta_ini = ...;
	{for_vector_int} _lambda_ini = ...;

	tuple for_vector_float{
	int index;
	float value;
	};

	{for_vector_float} _eta = ...;
	{for_vector_float} _alpha = ...;

	tuple for_tables_int{
	int index1;
	int index2;
	int value;
	};
	
	{for_tables_int} _theta = ...;
	{for_tables_int} _delta = ...; 
	{for_tables_int} _omega = ...;

	tuple for_tables_float{
	int index1;
	int index2;
	float value;
	};
	
	{for_tables_float} _CT1_ik = ...;
	{for_tables_float} _d = ...;
	{for_tables_float} _CB = ...;

	int M = first(_M).value; /*A big number*/;
	int rho = first(_rho).value; /*Number of available drones*/;
	float CR_f = first(_CR_f).value; /*Fixed relocation cost for moving a factory*/;
 	float CR_v = first(_CR_v).value; /*Variable relocation cost per kilometer for moving a factory*/;
 	float CP_f = first(_CP_f).value; /*Set-up cost to produce at any factory*/;
 	float CT = first(_CT).value; /*Transport cost per kilometer for shipping by drone*/;
	float CT2 = first(_CT2).value; /*Fixed cost for shipping by ship in any period*/;
	float CT3 = first(_CT3).value; /*Transport cost per unit for shipping by drone*/;
 	float CT4 = first(_CT4).value; /*Transport cost per unit for shipping by ship*/;
	float V_average = first(_V_average).value; /*Average speed when a factory is being relocated*/;
	float r_estimation = first(_r_estimation).value; /*Set-up time for relocating a factory*/;
	float MA = first(_MA).value; /*Maximum cross-sectional area available for batching in a built*/;
	float tau = first(_tau).value; /*Capacity in product weight of a drone*/;
	int beta_ini[1..k*l*t]= [index : val | <index,val> in _beta_ini]; /*Availability of the ship to sail from intermediary point k to customer l in period t*/;
	int beta[f in intermediaries, n in customers, v in periods] = beta_ini[v+t*(n-1)+l*t*(f-1)]; 	
	int lambda_ini[1..p*l*t] = [index : val | <index,val> in _lambda_ini]; /*The demand for product p from client l in period t*/;
	int lambda[f in products, n in customers, v in periods] = lambda_ini[v+t*(n-1)+l*t*(f-1)];
	float eta[products] = [index : val | <index,val> in _eta]; /*Weight of product p*/;
	float alpha[products] = [index : val | <index,val> in _alpha]; /*Cross-sectional area of product p*/;
	int theta[factories][products] = [index1 : [index2 : val] | <index1, index2, val> in _theta]; /*Binary matrix if mobile factory in i can produce product p*/;
	int delta[g][g] = [index1 : [index2 : val] | <index1, index2, val> in _delta]; /*Binary matrix if customer l is in drone coverage from location i*/;
	int omega[customers][intermediaries] = [index1 : [index2 : val] | <index1, index2, val> in _omega]; /*Duration of shipment from intermediary k to customer l*/;
	float CT1_ik[locations][intermediaries] = [index1 : [index2 : val] | <index1, index2, val> in _CT1_ik]; /*Transport cost for shipping by land from location i to intermediary k*/;
	float d[g][g] = [index1 : [index2 : val] | <index1, index2, val> in _d]; /*Distance in kilometers from location g to location g*/;		
 	float CB[periods][periods] = [index1 : [index2 : val] | <index1, index2, val> in _CB]; /*Backorder cost per unit of product unfulfilled in the due date*/;
	int LL=card(g);
 	int LI=card(locations);
 	int LC=card(customers);
 	int LD=card(v);
 	int TT=card(periods);


 //VARIABLES
 	dvar boolean x[factories][locations][locations][periods]; /*Binary variable if mobile factory j is relocated from location i to location g in period t*/; 
 	dvar boolean y[factories][locations][periods]; /*Binary variable if mobile factory j produces a batch in period t*/;
	dvar int+ y_hat[products][factories][periods]; /*Units of product p that mobile factory j produces in period t*/;
	dvar boolean v_up[factories][locations][customers][periods]; /*Binary variable if there are shipments by drone from factory j at location i to customer l in period t*/; 
 	dvar int+ v_hat_up[products][factories][customers][periods]; /*Units of product p to ship by drone from the mobile facility j to customer l in period t*/;
 	dvar boolean w[factories][locations][intermediaries][periods]; /*Binary variable if mobile facility j at location i transports products to intermediary k in period t*/;
 	dvar int+ w_hat[products][factories][intermediaries][customers][periods]; /*Units of product p to ship by traditional way from mobile facility j to intermediary k in period t*/;
 	dvar int+ f[products][customers][periods][periods]; /*Units of product p unfulfilled to customer l in period t*/;
	
	dvar boolean x_hat[factories][locations][periods]; /*Binary variable if there is a mobile factory at node i at the beginning of period t*/;
	dvar int+ n[products][factories][periods]; /*Units of product p in inventory in mobile factory j in period t*/;
	dvar int+ m[products][intermediaries][customers][periods]; /*Units of product p available at intermediary k for customer l in period t*/;
 	dvar int+ u[products][intermediaries][customers][periods]; /*Units of product p to ship from intermediary k to customer l in period t*/;	
 	dvar int+ u_hat[products][intermediaries][customers][periods]; /*Units of product p to receive from intermediary k to customer l in period t*/;	
	dvar int+ m_hat[products][customers][periods]; /*Accumulation of units of product p received by customer l in period t*/;
	dvar int+ f_hat[products][customers][periods][periods]; /*Units of product p ship in advance to customer l in period t*/;
	dvar boolean phi[factories][locations]; /*Initial location of factories*/;
	dvar boolean b_hat[factories]; /*Initial locations of drones*/;	
		
	dvar float+ cost_r;
	dvar float+ cost_p;
	dvar float+ cost_drone;
	dvar float+ cost_land;
	dvar float+ cost_ship;
	dvar float+ cost_late;
		
//OBJECTIVE
	dexpr float total_cost=
		sum(j in factories, i in locations, g in locations, t in periods)(CR_f+CR_v*d[i][g])*x[j][i][g][t]+
		sum(p in products, j in factories, t in periods)CP_f*alpha[p]*y_hat[p][j][t]+
		sum(p in products, j in factories, l in customers, t in periods)CT3*v_hat_up[p][j][l][t]+
		sum(p in products, j in factories, k in intermediaries, l in customers, t in periods)CT4*w_hat[p][j][k][l][t]+
		sum(p in products, k in intermediaries, l in customers, t in periods)CT2*u[p][k][l][t]+
		sum(p in products, l in customers, o in periods, t in periods)CB[o][t]*f[p][l][o][t]
		;
		
	minimize total_cost;		

	subject to
	{
		cost_r==sum(j in factories, i in locations, o in locations, t in periods)(CR_f+CR_v*d[i][o])*x[j][i][o][t];
	  	//cost_p==sum(j in factories, i in locations, t in periods)CP_f*y[j][i][t];
	  	cost_p==sum(p in products, j in factories, t in periods)CP_f*alpha[p]*y_hat[p][j][t];
	  	cost_drone==sum(p in products, j in factories, l in customers, t in periods)CT3*v_hat_up[p][j][l][t];
	  	cost_land==sum(p in products, j in factories, k in intermediaries, l in customers, t in periods)CT4*w_hat[p][j][k][l][t];
	  	cost_ship==sum(p in products, k in intermediaries, l in customers, t in periods)CT2*u[p][k][l][t];
	  	cost_late==sum(p in products, l in customers, o in periods, t in periods)CB[o][t]*f[p][l][o][t];
	
	    //Constraints for free placement
	    	C2_1:forall(j in factories)
	  	  	sum(i in locations)phi[j][i]==1;
	
	    	C2_2:forall(i in locations)
	  	  	sum(j in factories)phi[j][i]<=1;
	  	
	   //Initial location of mobile factories to let production
	  	C2:forall(j in factories, i in locations, t in periods:t==1)
	  	//C2:forall(j in factories, i in locations, t in periods)
	  	  	x_hat[j][i][t]==phi[j][i];
	  
	   //Limit relocation movements to just one for each factory during each period and only from a location where there is a factory
	  	C3_1:forall(j in factories, i in locations, t in periods)
	  	  	sum(o in locations)x[j][i][o][t]<=x_hat[j][i][t];
	  	  	
	 	C3_2:forall(j in factories, i in locations, o in locations: o==i, t in periods)
	  	  	x[j][i][o][t]==0;
	  	  	
	   //Position of each factory
	  	C4:forall(j in factories, i in locations, t in periods: t<TT)
	  		x_hat[j][i][t+1]+sum(o in locations)x[j][i][o][t]==sum(o in locations)x[j][o][i][t]+x_hat[j][i][t];
	  
	   //Only one factory at each location in each period
	  	C5:forall(i in locations, t in periods)
	  		sum(j in factories)x_hat[j][i][t]<=1;
	  	
	   //Prohibit production while a factory is being relocated and set up
   		C6:forall (j in factories, i in locations, o in locations, t in periods)		
  			x[j][i][o][t]+sum(a in periods: a>t-1 && (a<=t+(d[i][o]/(24*V_average))+r_estimation))y[j][i][a]<=x_hat[j][i][t];
  	  		
  	   //If there is a movement there should be production in that factory
  	  	C7:forall(j in factories, i in locations, t in periods)
  	  		sum(o in locations)x[j][o][i][t]<=sum(a in periods: a>t-1)y[j][i][a];
  	   
  	   //Connect binary variables y_ipt to their continuous counterpart y_hat_pit considering the capability of production of each factory
  	  	C8:forall(j in factories, p in products, t in periods)
  	  		y_hat[p][j][t]<=M*sum(i in locations)theta[j][p]*y[j][i][t];
  	   	
  	  //Production time used does not exceed the capacity of each factory in each period
  	  	C9:forall(j in factories, t in periods)
  	  		sum(p in products)alpha[p]*y_hat[p][j][t]<=MA;
  	  			 
	  //Inventory constraint for each factory 1
  	  	C52:forall(p in products, j in factories, t in periods:t>1)
  	  		n[p][j][t]==n[p][j][t-1]+y_hat[p][j][t]-sum(l in customers)v_hat_up[p][j][l][t]-sum(k in intermediaries, l in customers)w_hat[p][j][k][l][t];
  	
	  //Inventory constraint for each factory 2
  	  	C11:forall(p in products, j in factories, t in periods:t==1)
  	  		n[p][j][t]==y_hat[p][j][t];
  	  		
  	  //Not shipment of products done the same day
  	  	C53_1:forall(p in products, j in factories, t in periods:t>1)
  	  		sum(l in customers)v_hat_up[p][j][l][t]+sum(k in intermediaries, l in customers)w_hat[p][j][k][l][t]<=n[p][j][t-1];	
  	  	
  	  	C53_2:forall(p in products, j in factories, l in customers, t in periods: t==1)
  	  		v_hat_up[p][j][l][t]==0;
  	  	
  	  	C12_3:forall(p in products, j in factories, k in intermediaries, l in customers, t in periods: t==1)
  	  		w_hat[p][j][k][l][t]==0;		
  	  		
  	  //Not allowing shipments by drone from a location where there is not factory or a factory that is moving
  	  	C54:forall(j in factories, i in locations, o in locations, l in customers, t in periods)
  	  		x[j][i][o][t]+sum(a in periods: a>t-1 && (a<=t+(d[i][o]/(24*V_average))+r_estimation))v_up[j][i][l][a]<=x_hat[j][i][t];
  	  		
  	  //Not allowing shipments by land from a location where there is not factory or it is moving
  	  	C14:forall(j in factories, i in locations, o in locations, k in intermediaries, t in periods)
  	  		x[j][i][o][t]+sum(a in periods: a>t && (a<=t+(d[i][o]/(24*V_average))+r_estimation))w[j][i][k][a]<=x_hat[j][i][t];
  	  	 		
  	  //Not allowing shipments by land from locations where there is not factory
  	  	C15:forall(j in factories, i in locations, k in intermediaries, t in periods)
  	   		w[j][i][k][t]<=x_hat[j][i][t];
  	  
  	  //Maximum distance of coverage for each drone
  	  	C55:forall(j in factories, i in locations, l in customers, t in periods)
  	  		v_up[j][i][l][t]<=delta[i][l+LI];
  	  		
  	  //Only ship units if there is a shipment scheduled
		C56_1:forall(j in factories, l in customers, t in periods)
			sum(p in products)eta[p]*v_hat_up[p][j][l][t]<=tau*sum(i in locations)v_up[j][i][l][t];

		C56_2:forall(j in factories, l in customers, t in periods)
			sum(p in products)eta[p]*v_hat_up[p][j][l][t]<=tau*b_hat[j];
		
		C56_3:  sum(j in factories)b_hat[j] <= rho;

		C56_4:forall(j in factories)
			b_hat[j] <= 1;
  	   	  	
  	  //Relation between binary and continuous variables of shipments by ship
	 	C40:forall(p in products, j in factories, k in intermediaries, l in customers, t in periods)
  	  		w_hat[p][j][k][l][t]<=M*sum(i in locations)w[j][i][k][t];
  	  		
  	  //Inventory in each intermediary point 1
  	  	C41:forall(p in products, k in intermediaries, l in customers, t in periods:t>1)
  	  		m[p][k][l][t]==m[p][k][l][t-1]+sum(j in factories)w_hat[p][j][k][l][t]-u[p][k][l][t];
  	  		 		
  	  //Inventory in each intermediary point 2
  	  	C42:forall(p in products, k in intermediaries, l in customers, t in periods:t==1)
  	  		m[p][k][l][t]==sum(j in factories)w_hat[p][j][k][l][t]-u[p][k][l][t];
  	  		
  	  //Availability of ships in each intermediary point 1
  	  	C43_1:forall(p in products, k in intermediaries, l in customers, t in periods:t>1)
  	  		u[p][k][l][t]<=beta[k][l][t]*m[p][k][l][t-1];
 
  	  	C43_2:forall(p in products, k in intermediaries, l in customers, t in periods:t==1)
  	  		u[p][k][l][t]==0; 	  
  	  		
  	  //Balance of shipments by ship with the due dates 1
  	  	C44:forall(p in products, k in intermediaries, l in customers, t in periods: t>omega[l][k])
  	  		u_hat[p][k][l][t]==u[p][k][l][t-omega[l][k]];
  	  
  	  //Balance of shipments by ship with the due dates 2 
  	  	C45:forall(p in products, k in intermediaries, l in customers, t in periods: t<=omega[l][k])
  	  		u_hat[p][k][l][t]==0;
  	 	
  	  //Inventory in each client 1
  	  	C57:forall(p in products, l in customers, t in periods:t>1)
  	  		m_hat[p][l][t]==m_hat[p][l][t-1]+sum(j in factories)v_hat_up[p][j][l][t]+sum(k in intermediaries)u_hat[p][k][l][t];  	  	
  	  	
  	  //Inventory in each client 2
  	  	C58:forall(p in products, l in customers, t in periods:t==1)
  	  		m_hat[p][l][t]==sum(j in factories)v_hat_up[p][j][l][t]+sum(k in intermediaries)u_hat[p][k][l][t];
  	  
  	  //Late deliveries
  	  	C48:forall(p in products, l in customers, t in periods, o in periods: o<t+1 && lambda[p][l][o]>0)
  	  		lambda[p][l][o]-m_hat[p][l][t]+sum(a in periods: a>=1 && a<o)lambda[p][l][a]==f[p][l][o][t]-f_hat[p][l][o][t];
  	  		
  	  //Fulfillment of the total demand
  	  	C49:forall(p in products, l in customers, t in periods: t==TT)
  	  		m_hat[p][l][t]==sum(a in periods)lambda[p][l][a];
  	  	
	  }

tuple x_Tuple{int j;int i;int a;int t;int value;};
{x_Tuple} x_Set = {<j,i,a,t,x[j][i][a][t]> | j in factories,i in locations,a in locations,t in periods};

tuple y_Tuple{int j;int i;int t;int value;};
{y_Tuple} y_Set = {<j,i,t,y[j][i][t]> | j in factories,i in locations,t in periods};

tuple y_hat_Tuple{int p;int j;int t;int value;};
{y_hat_Tuple} y_hat_Set = {<p,j,t,y_hat[p][j][t]> | p in products,j in factories,t in periods};

tuple v_up_Tuple{int j;int i;int l;int t;int value;};
{v_up_Tuple} v_up_Set = {<j,i,l,t,v_up[j][i][l][t]> | j in factories,i in locations,l in customers,t in periods};

tuple v_hat_up_Tuple{int p;int j;int l;int t;int value;};
{v_hat_up_Tuple} v_hat_up_Set = {<p,j,l,t,v_hat_up[p][j][l][t]> | p in products,j in factories,l in customers,t in periods};

tuple w_Tuple{int j;int i;int k;int t;int value;};
{w_Tuple} w_Set = {<j,i,k,t,w[j][i][k][t]> | j in factories,i in locations, k in intermediaries,t in periods};

tuple w_hat_Tuple{int p;int j;int k;int l;int t;int value;};
{w_hat_Tuple} w_hat_Set = {<p,j,k,l,t,w_hat[p][j][k][l][t]> | p in products,j in factories, k in intermediaries,l in customers,t in periods};

tuple f_Tuple{int p;int l;int o;int t;int value;};
{f_Tuple} f_Set = {<p,l,o,t,f[p][l][o][t]> | p in products,l in customers, o in periods,t in periods};

tuple x_hat_Tuple{int j;int i;int t;int value;};
{x_hat_Tuple} x_hat_Set = {<j,i,t,x_hat[j][i][t]> | j in factories,i in locations,t in periods};

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

tuple phi_Tuple{int j; int i; int value;};
{phi_Tuple} phi_Set = {<j,i,phi[j][i]> | j in factories,i in locations}; 

tuple b_hat_Tuple{int j; int value;};
{b_hat_Tuple} b_hat_Set = {<j,b_hat[j]> | j in factories};

tuple cost{ float value;};
{cost} cost_relocation = {<cost_r>};
{cost} cost_production = {<cost_p>};
{cost} cost_drones = {<cost_drone>};
{cost} cost_lands = {<cost_land>};	
{cost} cost_ships = {<cost_ship>};	
{cost} cost_lates = {<cost_late>};	 