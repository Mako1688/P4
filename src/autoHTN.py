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
    return [('produce_{}'.format(item), ID)]

pyhop.declare_methods('produce', produce)

def make_method(name, rule):
    def method(state, ID):
        if 'Requires' in rule:
            for req_item, req_num in rule['Requires'].items():
                if getattr(state, req_item)[ID] < req_num:
                    return False
        if 'Consumes' in rule:
            for cons_item, cons_num in rule['Consumes'].items():
                if getattr(state, cons_item)[ID] < cons_num:
                    return False
        return [('produce_{}'.format(name), ID)]
    return method

def declare_methods(data):
    # some recipes are faster than others for the same product even though they might require extra tools
    # sort the recipes so that faster recipes go first

    for item in data['Items']:
        methods = []
        for recipe_name, recipe in data['Recipes'].items():
            if item in recipe['Produces']:
                methods.append((recipe['Time'], make_method(recipe_name, recipe)))
        methods.sort(key=lambda x: x[0])
        pyhop.declare_methods(item, *[method for _, method in methods])

def make_operator(rule):
    def operator(state, ID):
        if 'Requires' in rule:
            for req_item, req_num in rule['Requires'].items():
                if getattr(state, req_item)[ID] < req_num:
                    return False
        if 'Consumes' in rule:
            for cons_item, cons_num in rule['Consumes'].items():
                if getattr(state, cons_item)[ID] < cons_num:
                    return False
                setattr(state, cons_item, {ID: getattr(state, cons_item)[ID] - cons_num})
        if 'Produces' in rule:
            for prod_item, prod_num in rule['Produces'].items():
                setattr(state, prod_item, {ID: getattr(state, prod_item)[ID] + prod_num})
        state.time[ID] += rule['Time']
        return state
    return operator

def declare_operators(data):
    operators = []
    for recipe_name, recipe in data['Recipes'].items():
        operators.append(make_operator(recipe))
    pyhop.declare_operators(*operators)

def add_heuristic(data, ID):
    # prune search branch if heuristic() returns True
    # do not change parameters to heuristic(), but can add more heuristic functions with the same parameters: 
    # e.g. def heuristic2(...); pyhop.add_check(heuristic2)
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        # Example heuristic: prune if time exceeds 240
        if state.time[ID] > 240:
            return True
        return False # if True, prune this branch

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

    # Test cases
    test_cases = [
        ({'plank': 1}, {'plank': 1}, 0),
        ({}, {'plank': 1}, 300),
        ({'plank': 3, 'stick': 2}, {'wooden_pickaxe': 1}, 10),
        ({}, {'iron_pickaxe': 1}, 100),
        ({}, {'cart': 1, 'rail': 10}, 175),
        ({}, {'cart': 1, 'rail': 20}, 250),
        ({}, {'wood': 12}, 46)
    ]

    for initial, goal, time in test_cases:
        state = set_up_state(data, 'agent', time)
        for item, num in initial.items():
            setattr(state, item, {'agent': num})
        goals = set_up_goals({'Goal': goal}, 'agent')

        declare_operators(data)
        declare_methods(data)
        add_heuristic(data, 'agent')

        print(f"Testing with initial: {initial}, goal: {goal}, time: {time}")
        pyhop.pyhop(state, goals, verbose=3)
