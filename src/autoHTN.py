import pyhop
import json

def check_enough(state, ID, item, num):
    if getattr(state, item)[ID] >= num:
        return []
    return False

def produce_enough(state, ID, item, num):
    return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods('have_enough', check_enough, produce_enough)

def produce(state, ID, item):
    # Map the generic 'produce' task to the specific production task
    return [('produce_{}'.format(item), ID)]

pyhop.declare_methods('produce', produce)

def make_method(name, rule):
    def method(state, ID):
        # Check if all required items and tools are available
        for item, num in rule.get('Requires', {}).items():
            if getattr(state, item).get(ID, 0) < num:
                return False
        for item, num in rule.get('Consumes', {}).items():
            if getattr(state, item).get(ID, 0) < num:
                return False
        
        # If all requirements are met, return the subtasks to produce the item
        subtasks = []
        for item, num in rule.get('Consumes', {}).items():
            subtasks.append(('have_enough', ID, item, num))
        subtasks.append(('op_{}'.format(name.replace(' ', '_')), ID))
        return subtasks
    
    return method

def declare_methods(data):
    # Sort recipes by their time efficiency (fastest recipes first)
    recipes = data['Recipes']
    sorted_recipes = sorted(recipes.items(), key=lambda x: x[1]['Time'])
    
    for name, rule in sorted_recipes:
        method = make_method(name, rule)
        pyhop.declare_methods('produce_{}'.format(name.replace(' ', '_')), method)

def make_operator(rule):
    def operator(state, ID):
        # Consume the required items
        for item, num in rule.get('Consumes', {}).items():
            if getattr(state, item).get(ID, 0) < num:
                return False  # Not enough resources
            getattr(state, item)[ID] -= num
        
        # Produce the desired item
        for item, num in rule.get('Produces', {}).items():
            getattr(state, item)[ID] = getattr(state, item).get(ID, 0) + num
        
        # Update the time
        state.time[ID] += rule['Time']
        
        return state
    
    return operator

def declare_operators(data):
    # Declare operators for all recipes
    recipes = data['Recipes']
    
    for name, rule in recipes.items():
        operator = make_operator(rule)
        pyhop.declare_operators(operator)
        print(f"Declared operator: op_{name.replace(' ', '_')}")

def add_heuristic(data, ID):
    # Prune search branch if heuristic() returns True
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        # Prune the branch if the current time exceeds the allotted time
        if state.time.get(ID, 0) > 239:  # Assuming 239 is the allotted time
            return True
        return False
    
    pyhop.add_check(heuristic)

def set_up_state(data, ID, time=0):
    state = pyhop.State('state')
    state.time = {ID: time}
    for item in data['Items']:
        setattr(state, item, {ID: 0})
    for item in data['Tools']:
        setattr(state, item, {ID: 0})
    for item, num in data['Initial'].items():
        setattr(state, item, {ID: num})
    return state

def set_up_goals(data, ID):
    goals = []
    for item, num in data['Goal'].items():
        goals.append(('have_enough', ID, item, num))
    return goals

if __name__ == '__main__':
    rules_filename = 'crafting.json'
    with open(rules_filename) as f:
        data = json.load(f)
    
    state = set_up_state(data, 'agent', time=239)  # Allot time here
    goals = set_up_goals(data, 'agent')
    
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    
    pyhop.print_operators()
    pyhop.print_methods()
    # Hint: verbose output can take a long time even if the solution is correct; 
    # try verbose=1 if it is taking too long
    pyhop.pyhop(state, goals, verbose=3)
    # pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)