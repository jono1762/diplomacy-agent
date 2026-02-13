import random
from collections import deque
import networkx as nx
import numpy as np
from agent_baselines import Agent

class StudentAgent(Agent):
    '''
    Implement your agent here. 

    Please read the abstract Agent class from baseline_agents.py first.
    
    You can add/override attributes and methods as needed.
    '''

    def __init__(self, agent_name='Give a nickname'):
        super().__init__(agent_name)

        '''Implement your agent here.'''
        self.map_graph_army = None
        self.map_graph_navy = None

    def new_game(self, game, power_name):
        self.game = game
        self.power_name = power_name

        '''Implement your agent here.'''
        self.build_map_graphs()
        self.original_scs = self.game.get_centers(self.power_name)
        self.num_locs = len(self.game.get_orderable_locations(self.power_name))

        self.scs = self.original_scs.copy()
        self.enemy_scs = {}
        for country, scs in self.game.get_centers().items():
            if country == self.power_name:
                continue
            self.enemy_scs[country] = scs
        
        self.greedy_mode = False # Switch that affects how agent behaves - for static agents it is false otherwise it becomes true
        self.limit = 5 # Restriction on how many moves a fleet spends in sea to support convoying

    def update_game(self, all_power_orders):
        # do not make changes to the following codes
        for power_name in all_power_orders.keys():
            self.game.set_orders(power_name, all_power_orders[power_name])
        self.game.process()

    def build_map_graphs(self):    # You can re-use this function if needed
        if not self.game:
            raise Exception('Game Not Initialised. Cannot Build Map Graphs.')

        self.map_graph_army = nx.Graph()
        self.map_graph_navy = nx.Graph()

        locations = list(self.game.map.loc_type.keys()) # locations with '/' are not real provinces

        for i in locations:
            if self.game.map.loc_type[i] in ['LAND', 'COAST']:
                self.map_graph_army.add_node(i.upper())
            if self.game.map.loc_type[i] in ['WATER', 'COAST']:
                self.map_graph_navy.add_node(i.upper())

        locations = [i.upper() for i in locations]

        for i in locations:
            for j in locations:
                if self.game.map.abuts('A', i, '-', j):
                    self.map_graph_army.add_edge(i, j)
                if self.game.map.abuts('F', i, '-', j):
                    self.map_graph_navy.add_edge(i, j)

    # Search for next location to move unit to using breadth-first search
    def bfs(self, root, units, enemy_scs, unoccupied_scs, exclude=[]):
        unit = units[root]
        graph = self.map_graph_army if unit == 'A' else self.map_graph_navy
        queue = deque([root])
        visited = set(root)
        parent = {root: None}
        result = (0, root, 'H')

        # Already at supply center not yet owned by power
        if root in enemy_scs or root in unoccupied_scs:
            return (0, root, 'H')
        
        # Search for closest enemy supply centre if it is supported
        min_dist = np.inf

        while len(queue) > 0:
            curr = queue.popleft()
            
            # Found enemy supply center -> select action getting closest to it
            if curr in enemy_scs and curr not in units.keys():
                dist = 0
                curr_cp = curr
                
                while parent[curr_cp] != root:
                    curr_cp = parent[curr_cp]
                    dist += 1
                
                if dist < min_dist:
                    min_dist = dist
                
                if dist > min_dist and min_dist < np.inf:
                    break
                
                if curr_cp not in units.keys() and curr_cp not in exclude:
                    for loc in units.keys():
                        if loc in list(nx.neighbors(graph, curr)) and loc in list(nx.neighbors(graph, root)):
                            return (dist, curr_cp, 'A')
            
            # Add adjacent, unvisited neighbours of current province
            neighbours = list(nx.neighbors(graph, curr))
            for neighbour in neighbours:
                if neighbour not in visited:
                    parent[neighbour] = curr
                    queue.append(neighbour)
                    visited.add(neighbour)
        
        queue = deque([root])
        visited = set(root)
        parent = {root: None}

        # Search for closest unoccupied, adjacent SC
        while len(queue) > 0:
            curr = queue.popleft()

            # Found new supply center not owned by anyone -> select action getting closest to it
            if curr in unoccupied_scs and curr not in units.keys():
                dist = 0
                curr_cp = curr
                
                while parent[curr_cp] != root:
                    curr_cp = parent[curr_cp]
                    dist += 1
                
                if curr_cp not in units.keys():
                    alt_result = (dist, curr_cp, 'A')
                    if alt_result[0] == 0:
                        enemy_adjacent = False
                        for enemy_sc in enemy_scs:
                            if enemy_sc in list(nx.neighbors(graph, curr_cp)):
                                enemy_adjacent = True
                                break
                        if not enemy_adjacent and curr_cp not in exclude:
                            return alt_result
            
            # Add adjacent, unvisited neighbours of current province
            neighbours = list(nx.neighbors(graph, curr))
            for neighbour in neighbours:
                if neighbour not in visited:
                    parent[neighbour] = curr
                    queue.append(neighbour)
                    visited.add(neighbour)
        
        queue = deque([root])
        visited = set(root)
        parent = {root: None}
        
        # Search for closest enemy SC
        while len(queue) > 0:
            curr = queue.popleft()
            
            # Found enemy supply center -> select action getting closest to it
            if curr in enemy_scs and curr not in units.keys():
                dist = 0
                curr_cp = curr
                
                while parent[curr_cp] != root:
                    curr_cp = parent[curr_cp]
                    dist += 1
                
                if curr_cp not in units.keys() and curr_cp not in exclude:
                    result = (dist, curr_cp, 'A')
                    break
            
            # Add adjacent, unvisited neighbours of current province
            neighbours = list(nx.neighbors(graph, curr))
            for neighbour in neighbours:
                if neighbour not in visited:
                    parent[neighbour] = curr
                    queue.append(neighbour)
                    visited.add(neighbour)
        
        queue = deque([root])
        visited = set(root)
        parent = {root: None}

        # Search for closest unoccupied SC
        while len(queue) > 0:
            curr = queue.popleft()

            # Found new supply center not owned by anyone -> select action getting closest to it
            if curr in unoccupied_scs and curr not in units.keys():
                dist = 0
                curr_cp = curr
                
                while parent[curr_cp] != root:
                    curr_cp = parent[curr_cp]
                    dist += 1
                
                if curr_cp not in units.keys():
                    alt_result = (dist, curr_cp, 'A')
                    if alt_result[0] <= result[0] and curr_cp not in exclude:
                        result = alt_result
                    return result
            
            # Add adjacent, unvisited neighbours of current province
            neighbours = list(nx.neighbors(graph, curr))
            for neighbour in neighbours:
                if neighbour not in visited:
                    parent[neighbour] = curr
                    queue.append(neighbour)
                    visited.add(neighbour)
        
        # No possible action getting towards satisfactory supply centre -> hold
        return result
    
    def sort_locs(self, next_locs):
        # Sort locations by distance to suitable supply centre
        next_locs_keys, next_locs_vals = list(next_locs.keys()), list(next_locs.values())
        indices = np.argsort([item[0] for item in next_locs_vals])
        next_locs = {next_locs_keys[i]: next_locs_vals[i] for i in indices}
        return next_locs

    def is_relevant(self, order, loc, locs, next_loc, next_locs, units):
        # Determine if move attacks or supports to desired location
        split_order = order.split()
        graph = self.map_graph_army if units[loc] == 'A' else self.map_graph_navy

        if next_loc[2] == 'H':
            return False
        
        elif next_loc[2] == 'A':
            return len(split_order) == 4 and split_order[-2] == '-' and split_order[-1] == next_loc[1]
        
        else: # next_loc[2] == 'S'
            return len(split_order) == 7 and split_order[2] == 'S' and split_order[-3] in locs and split_order[-3] in nx.neighbors(graph, loc) and next_locs[split_order[-3]][1] == split_order[-1] and split_order[-1] == next_loc[1]

    def get_actions(self):
        '''Implement your agent here.'''
        # Retrieve possible orders and orderable locations from game state
        possible_orders = self.game.get_all_possible_orders()
        locs = self.game.get_orderable_locations(self.power_name)
        units = {unit.split()[1]: unit.split()[0] for unit in self.game.get_units(self.power_name)}
        for i in range(len(locs)):
            for j in range(len(units.keys())):
                if list(units.keys())[j].split('/')[0] == locs[i]:
                    locs[i] = list(units.keys())[j]
                    break
        
        enemy_locs = []
        for country, enemy_loc in self.game.get_orderable_locations().items():
            if country == self.power_name:
                continue
            enemy_locs.extend(enemy_loc)

        ENGLAND_PROVINCES = ["EDI", "LVP", "LON", "CLY", "YOR", "WAL"]

        # Get list of SCs by category
        own_scs = self.game.get_centers(self.power_name)

        enemy_scs = []
        for country, centers in self.game.get_centers().items():
            if country != self.power_name:
                for center in centers:
                    enemy_scs.append(center)

        unoccupied_scs = [center for center in self.game.map.scs if center not in own_scs and center not in enemy_scs]

        if not self.greedy_mode:
            for sc in own_scs:
                self.scs.append(sc)

            for sc in self.scs:
                if sc not in own_scs:
                    self.greedy_mode = True
                    break
        
        if not self.greedy_mode:
            for country, scs in self.game.get_centers().items():
                if country != self.power_name:
                    for sc in scs:
                        if sc not in self.enemy_scs[country]:
                            self.greedy_mode = True
                            break

        # Adjustment phase -> build as many troops as can, optimised by proximity to target
        if self.game.phase_type == 'A':
            agent_orders = {}

            new_agent_orders = {loc: "WAIVE" for loc in locs}
            adj_units = {loc: [] for loc in locs}
            locs_to_ignore = []

            num_new_units = len(own_scs) - self.num_locs
            self.num_locs = len(own_scs)

            for loc in locs:
                for order in possible_orders[loc]:
                    order_split = order.split()
                    if order_split[-1] == 'D':
                        new_agent_orders[loc] = order
                        locs_to_ignore.append(loc)

                    elif order_split[-1] == 'R':
                        new_agent_orders[loc] = order
                        locs_to_ignore.append(loc)

                    else:
                        if len(order_split) == 3 and len(adj_units[loc]) < 2 and order_split[0] not in adj_units[loc]:
                            adj_units[loc].append(order_split[0])
            
            new_adj_units = {loc: [] for loc in locs}
            for loc, unit in adj_units.items():
                if len(unit) == 2:
                    army_in_england = sum(units[u] == 'A' and u in ENGLAND_PROVINCES for u in units.keys()) > 0
                    if (self.power_name == "ENGLAND" and army_in_england) or (self.power_name == "ITALY" and loc == "NAP"): # Comment this line if convoying
                    # if self.power_name == "ITALY" and loc == "NAP": # Uncomment this line if not convoying
                        new_adj_units[loc] = 'F'

                    else:
                        new_adj_units[loc] = 'A'

                elif len(unit) == 1:
                    new_adj_units[loc] = adj_units[loc][0]

                else:
                    new_adj_units.pop(loc)
            adj_units = new_adj_units

            for loc in locs:
                if len(new_agent_orders[loc].split()) == 1:
                    agent_orders[loc] = self.bfs(loc, adj_units, enemy_scs, unoccupied_scs)

            if num_new_units > 0:
                for i in range(min(num_new_units, len(locs))):
                    min_dist = min(list(agent_orders.values()), key=lambda value: value[0])
                    loc = [loc for loc, dist in agent_orders.items() if dist == min_dist and loc not in locs_to_ignore][0]
                    new_agent_orders[loc] = f"{adj_units[loc]} {loc} B"
                    agent_orders.pop(loc)

            agent_orders = list(new_agent_orders.values())
            return agent_orders

        # Other non-movement phases -> random action
        elif self.game.phase_type != 'M':
            agent_orders = [random.choice(possible_orders[loc]) for loc in locs if possible_orders[loc]]
            return agent_orders
        
        # Determine move for each unit corresponding to optimal target if movement phase
        next_locs = {loc: None for loc in locs}
        for loc in next_locs:
            if len(possible_orders[loc]) > 0:
                other_locs = locs.copy()
                other_locs.remove(loc)
                next_locs[loc] = self.bfs(loc, units, enemy_scs, unoccupied_scs)
        
        # Order moves by optimality of target
        next_locs = self.sort_locs(next_locs) # Comment out this line to simulate no heuristic

        # Get units to aim for same target (so can support) where possible
        new_next_locs = {loc: None for loc in next_locs.keys()}

        for loc, (dist, next_loc, move_type) in next_locs.items():
            # Unit already attacking something via support
            if new_next_locs[loc] is not None:
                continue
            
            new_value = (dist, next_loc, move_type)
            graph = self.map_graph_army if units[loc] == 'A' else self.map_graph_navy
            loc_neighbours = list(nx.neighbors(graph, loc))

            # If unit holding, do not change to attack
            if move_type == 'A':
                for alt_loc, (alt_dist, alt_next_loc, alt_move_type) in next_locs.items():
                    # Same location -> same location attacking -> modification based on this makes no sense
                    if loc == alt_loc:
                        continue
                    
                    # Attacking closer target already -> do not change to further target
                    if dist < alt_dist:
                        break
                        
                    # Adjacent locations that can support attack -> support attack enemy SC
                    if alt_loc in loc_neighbours and alt_next_loc in loc_neighbours and (alt_next_loc in enemy_scs or alt_next_loc in unoccupied_scs) and alt_move_type != 'H':
                        new_value = (alt_dist, alt_next_loc, 'S')
                        new_next_locs[alt_loc] = (1, alt_next_loc, 'A')
                        break
                    
                    # Adjacent locations but cannot support attack -> head in same direction so can support attack later
                    if not self.greedy_mode and alt_loc in loc_neighbours and (alt_next_loc not in loc_neighbours or alt_next_loc not in enemy_scs):
                        alt_graph = self.map_graph_army if units[alt_loc] == 'A' else self.map_graph_navy
                        # if alt_next_loc in alt_graph:
                        alt_next_loc_neighbours = list(nx.neighbors(alt_graph, alt_next_loc))
                        for neighbour in alt_next_loc_neighbours:
                            if neighbour in loc_neighbours and neighbour not in locs and neighbour not in [value[1] for value in next_locs.values()] and neighbour not in [value[1] for value in new_next_locs.values() if value is not None]:
                                units[neighbour] = units[alt_loc]
                                new_value = (self.bfs(neighbour, units, enemy_scs, unoccupied_scs)[0] + 1, neighbour, 'A') # Not entirely accurate dist
                                break
        
            new_next_locs[loc] = new_value
        next_locs = self.sort_locs(new_next_locs) # Comment out this line to simulate no heuristic

        # Ensure two units are not going to same location unless support
        unique_locs = set()
        hold_locs = set([next_loc for (dist, next_loc, move_type) in next_locs.values() if move_type == 'H'])
        for loc, (dist, next_loc, move_type) in next_locs.items():
            graph = self.map_graph_army if units[loc] == 'A' else self.map_graph_navy
            if next_loc in unique_locs and move_type == 'A':
                has_neighbour = False

                for neighbour in list(nx.neighbors(graph, loc)):
                    if neighbour not in hold_locs and neighbour not in [val[1] for val in next_locs.values()]:
                        next_locs[loc] = (1, neighbour, 'A')
                        has_neighbour = True
            
                if not has_neighbour:
                    next_locs[loc] = (1, loc, 'H')

            if move_type == 'A' or move_type == 'H':
                unique_locs.add(next_loc)

        # Select action corresponding next location for each location
        possible_agent_orders = {loc: [order for order in possible_orders[loc] if self.is_relevant(order, loc, locs, next_locs[loc], next_locs, units)] for loc in locs}
        agent_orders = {loc: None for loc in locs}
        exclude = []
        for loc in locs:
            if len(possible_agent_orders[loc]) > 0:
                agent_orders[loc] = possible_agent_orders[loc][0]
            else:
                poss_orders = [order for order in possible_orders[loc] if len(order.split()) == 4 and order.split()[-1] not in next_locs.values() and order.split()[-1] not in locs]
                if loc not in enemy_scs and loc not in unoccupied_scs and len(poss_orders) > 0 and loc not in ENGLAND_PROVINCES:
                    graph = self.map_graph_army if units[loc] == 'A' else self.map_graph_navy
                    neighbours = list(nx.neighbors(graph, loc))
                    backup_next_loc = next_locs[loc][1]
                    while (backup_next_loc[1] == loc or backup_next_loc[1] in unique_locs) and len(neighbours) > 0:
                        next_locs[loc] = backup_next_loc
                        agent_orders[loc] = f"{units[loc]} {loc} - {backup_next_loc[1]}"
                        unique_locs.add(backup_next_loc[1])
                        exclude.append(backup_next_loc[1])
                        neighbours.remove(next_locs[loc][1])
                        backup_next_loc = self.bfs(loc, units, enemy_scs, unoccupied_scs, exclude)
                    else:
                        agent_orders[loc] = f"{units[loc]} {loc} H"
                else:
                    agent_orders[loc] = f"{units[loc]} {loc} H"
        
        # # Only attack occupied supply centre if supported otherwise hold
        # for loc, agent_order in agent_orders.items():
        #     split_agent_order = agent_order.split()
        #     if len(split_agent_order) == 4 and split_agent_order[-1] in enemy_locs:
        #         supported = False
        #         for support_loc, support_agent_order in agent_orders.items():
        #             support_agent_order_split = support_agent_order.split()
        #             if loc == support_loc:
        #                 continue
        #             if len(support_agent_order_split) == 7 and support_agent_order_split[-1] == split_agent_order[-1]:
        #                 supported = True
        #                 break
        #         if not supported:
        #             agent_orders[loc] = f"{units[loc]} {loc} H"
                    
        # Convoy out of England where appropriate and necessary
        if self.power_name == "ENGLAND":
            for loc, agent_order in agent_orders.items():
                if loc in ENGLAND_PROVINCES and len(agent_order.split()) == 3 and agent_order[0] == 'A':
                    convoy_loc = None
                    convoy_action = None
                    convoyed_action = None

                    for other_loc in locs:
                        if possible_orders[other_loc] and convoy_loc is None:
                            for order in possible_orders[other_loc]:
                                split_order = order.split()
                                if len(split_order) == 7 and split_order[2] == 'C' and split_order[4] == loc and split_order[-1] not in ENGLAND_PROVINCES and split_order[-1] not in enemy_locs and split_order[-1] not in unique_locs and split_order[-1] not in units.keys() and split_order[4] in list(nx.neighbors(self.map_graph_navy, split_order[1])) and split_order[-1] in list(nx.neighbors(self.map_graph_navy, split_order[1])) and split_order[-1] not in agent_orders.values():
                                    convoy_loc = split_order[1]
                                    convoy_action = order
                                    convoyed_action = ' '.join(split_order[3:] + ["VIA"])
                                    break
                    
                    if convoy_loc is not None:
                        agent_orders[loc] = convoyed_action
                        agent_orders[convoy_loc] = convoy_action
                    else:
                        move = None
                        good_move = None

                        for neighbour in list(nx.neighbors(self.map_graph_army, loc)):
                            if neighbour not in unique_locs:
                                if move is None:
                                    move = f"A {loc} - {neighbour}"

                                for fleet_loc in locs:
                                    if units[fleet_loc] == 'F' and neighbour in list(nx.neighbors(self.map_graph_navy, fleet_loc)) and fleet_loc not in ENGLAND_PROVINCES:
                                        good_move = f"A {loc} - {neighbour}"
                                        break
                            
                            if good_move is not None:
                                agent_orders[loc] = good_move
                                break
                            
                            elif move is not None:
                                agent_orders[loc] = move
                                break
                
                if loc == "NTH" and len(agent_order.split()) == 4:
                    if self.limit < 5:
                        support_locs = []
                        for support_loc, support_order in agent_orders.items():
                            support_order_split = support_order.split()
                            if support_order_split[-1] == next_locs[support_loc]:
                                support_locs.append(support_loc)
                        
                        next_locs[loc] = (0, loc, 'H')
                        agent_orders[loc] = f"F {loc} H"
                        for support_loc in support_locs:
                            next_locs[support_loc] = (0, support_loc, 'H')
                            agent_orders[support_loc] = f"F {support_loc} H"
                    
                        self.limit += 1
                    else:
                        self.limit = 0

        agent_orders = list(agent_orders.values())
        
        return agent_orders