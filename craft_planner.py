import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from math import inf
from heapq import heappop, heappush

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        if 'Requires' in rule: # 'Requires' section of dictionary
            for requirement in rule['Requires']: # For every requirement
                if not state[requirement]: # If we don't have said requirement
                    return False # Return False
        if 'Consumes' in rule:  # 'Consumes' section of dictionary
            for consumed in rule['Consumes']: # For every consumed
                if not state[consumed] >= rule['Consumes'][consumed]: # If we don't have enough of consumable
                    return False # Return False
        return True # Else return true

    return check # return check value


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        next_state = state.copy()
        if 'Consumes' in rule: # 'Consumes' section of dictionary
            for consumed in rule['Consumes']: # For every consumed
                next_state[consumed] -= rule['Consumes'][consumed] # Decrease amount of current state by how much is used
        if 'Produces' in rule: # 'Produces' section of dictionary
            for product in rule['Produces']: # For every product produced
                next_state[product] += rule['Produces'][product] # Increase current states amount by how much is made
        return next_state # Return new_state

    return effect # Return effect state


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        for endgame in goal: # For every item in goal
            if state[endgame] < goal[endgame]: # If current state contains less than goal value
                return False # return false
        return True # Else we have goal value, return true

    return is_goal


def graph(state): # GRAPH GENERATES POSSIBLE ACTION
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes: # UNCHANGED
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def heuristic(action_name, state):

    #print("State: ", state)
    #print(Crafting['Goal'])
    #state inside of heuristic is possible new state

    #use negative numbers to prioritize one thing over another

    #for absolute cases like need to be done first:
        #return float('-inf')
        #return float('inf')

    #check if the tool required is already made (unfinished)
        #go through every tool
        #if state has one & has more than one return infinity                   
    if state['bench'] > 1 or state['wooden_axe'] > 1 or state['wooden_pickaxe'] > 1 or state['stone_axe'] > 1 or state['stone_pickaxe'] > 1 or state['iron_axe'] > 1 or state['iron_pickaxe'] > 1:
        return float('inf')
             
    current_recipe = Crafting['Recipes'][action_name]
    if 'Requires' in current_recipe:
        for tool in current_recipe['Requires']:
                if state[tool] > 1:
                    return float('inf')
    
    #make sure to use the best tool available

    #don't make more items than needed
    if state['plank'] > 8 or state['wood'] > 4 or state['ore'] > 12 or state['ingot'] > 12 or state['cobble'] > 8 or state['stick'] > 8 or state['coal'] > 12:
            return float('inf')
    #use goal to find how much of each material needed then don't stop making it until reached the amount needed
        #once reached that amount do all of the smelting/turning wood into planks at the end

    return 0

def search(graph, state, is_goal, limit, heuristic):

    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    
    path = [] # List of tuples

    passed_states = {}
    passed_states[state] = None

    costs = {}
    costs[state] = 0

    steps = {}
    steps[state] = 0

    queue = [(0, state)]

    while time() - start_time < limit:
        current_cost, current_state = heappop(queue)
        if is_goal(current_state): # If we have the goal (IS_GOAL IS A FUNCTION THAT CALLS MAKE_GOAL_CHECKER BTW)
            print("Time:", (time() - start_time)) # Print statistics
            print("Cost:", costs[current_state])
            print("Len:", steps[current_state])
            while passed_states[current_state]: # While out list of past actions is not None
                past_state, past_action = passed_states[current_state]
                path.append((current_state, past_action)) # Insert into path list
                current_state = past_state
            path.reverse() # reverse the path
            return path # and finally return it
        for new_name, new_state, new_cost in graph(current_state): # Graph gives list of possible actions with 3 variables each
            pathcost = current_cost + new_cost # Calculate cost
            pathlen = steps[current_state] + 1 # Calculate length of path
            if new_state not in costs or pathcost < costs[new_state]: # If not in point or costs less than pointer
                costs[new_state] = pathcost
                steps[new_state] = pathlen
                passed_states[new_state] = (current_state, (new_name, new_state, new_cost))
                heappush(queue, (heuristic(new_name, new_state) + pathcost, new_state)) # Queue it using heauristic to determine cost, something like that

    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    # print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    # print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    # print('Goal:',Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    # print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)
    
    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])


    #find the exact base materials needed to create the final product
    basic_materials = ['wood', 'cobble', 'ore', 'coal']
    required_materials = []

    for item in Crafting['Goal'].items():
        print("Goal Item: ", item)
        for recipe in Crafting['Recipes'].items():
            print("Recipe: ", recipe)
            
            #LINES BELOW AREN'T WORKING YET

            if item in recipe['Produces'].items():
                for mat in recipe['Consumes'].items():
                    required_materials.append(mat)
    #break down the required materials even further
        #ex iron pickaxe -> 2 sticks 3 ingots 1 bench
            #break down into 3 ore, 2 planks, 1 furnace, 1 bench

    #WIP
    #add 3 wood, 11 cobble, 3 ore, 3 coal for pickaxes, bench, furnaces
    '''
    x = True
    while x:
        for item in required_materials:
            if item not in basic_materials:
                for recipe in Crafting['Recipes'].items():
                    if item in recipe['Produces'].items():
                        for mat in recipe['Consumes'].items():
                            if mat in required_materials:
                                for elem in required_materials:
                                    if elem == mat:
                                        elem[1] += mat[1]
                            else:
                                required_materials.append(mat)
    '''


    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 1, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t',state)
            print(action)