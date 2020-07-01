include "alldifferent.mzn";

% =============
% Parameters
% =============

% Array containing for each node its neighbors
int: nodes_size;
array[1..nodes_size] of set of 1..nodes_size: nodes;

% Array containing for each agent its starting node and its target node
int: agents_size;
array[1..agents_size, 1..2] of 1..nodes_size: agents;

% The maximum number of steps allowed to find a solution
int: maximum_time;

% =============
% Variables
% =============

% Paths
array[1..agents_size, 1..maximum_time] of var 1..nodes_size: path;

% Costs
array[1..agents_size] of var 1..maximum_time: costs;

% =============
% Constraints  
% =============

constraint

% Initial position and final position
forall(a in 1..agents_size)(
  path[a, 1] = agents[a, 1] /\ path[a, maximum_time] = agents[a, 2]
) /\

% Stop agents when arrived
forall(a in 1..agents_size, t in 1..maximum_time - 1, )(
  path[a, t] = agents[a, 2] -> path[a, t + 1] = agents[a, 2]
) /\

% Vertex collision
forall(t in 1..maximum_time)(
  all_different([path[a, t] | a in 1..agents_size])
) /\

% Edge collision
forall(a1 in 1..agents_size, a2 in 1..agents_size, t in 1..maximum_time - 1)(
  % Previously:
  a1 != a2 -> path[a1, t + 1] != path[a2, t] /\ path[a1, t] != path[a2, t + 1]
) /\

% Valid transitions
forall(a in 1..agents_size, t in 1..maximum_time - 1)(
  path[a, t + 1] in nodes[path[a, t]]
) /\

% Update costs
forall(a in 1..agents_size)(
  costs[a] = sum(t in 1..maximum_time)(1 * (path[a, t] != agents[a, 2]) + 0 * (path[a, t] = agents[a, 2]))
);

% =============
% Objective
% =============

var int: sum_of_costs;
constraint sum_of_costs = sum(costs);

% Minimize sum of costs
solve :: seq_search([
  int_search(path, first_fail, indomain_split),
  int_search(costs, first_fail, indomain_split)
]) minimize sum_of_costs;

