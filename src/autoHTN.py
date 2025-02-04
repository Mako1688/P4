import pyhop
import json

def check_enough(state, ID, item, num):
    # Check if there is enough of the item
    return [] if getattr(state, item)[ID] >= num else False

def produce_enough(state, ID, item, num):
    # Create tasks to produce the item if not enough
    return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods('have_enough', check_enough, produce_enough)

def produce(state, ID, item):
    # Create a task to produce the item
    return [('produce_{}'.format(item), ID)]

pyhop.declare_methods('produce', produce)

def make_method(name, rule):
    # Generate a method for a given recipe
    def method(state, ID):
        condition = [('have_enough', ID, k, v) for key, value in rule.items() if key != 'Produces' and isinstance(value, dict) for k, v in value.items()]
        condition.append(('op_' + name, ID))
        return condition
    return method

def declare_methods(data):
    # Declare methods for each product
    method_dict = {}
    for key, value in sorted(data['Recipes'].items(), key=lambda item: item[1]["Time"], reverse=True):
        key = key.replace(' ', '_')
        for name_of_produce in value['Produces'].items():
            my_method = make_method(key, value)
            if name_of_produce in method_dict:
                method_dict[name_of_produce].append(my_method)
            else:
                method_dict[name_of_produce] = [my_method]
    for name, methods in method_dict.items():
        pyhop.declare_methods('produce_' + name[0], *methods)

def make_operator(rule):
    # Generate an operator for a given recipe
    def operator(state, ID):
        for key, value in rule.items():
            if key == 'Produces':
                for k, v in value.items():
                    setattr(state, k, {ID: getattr(state, k)[ID] + v})
            if key == 'Consumes':
                for k, v in value.items():
                    if getattr(state, k)[ID] >= v:
                        setattr(state, k, {ID: getattr(state, k)[ID] - v})
            if key == 'Time':
                if state.time[ID] >= v:
                    state.time[ID] -= v
                else:
                    return False
        return state
    return operator

def declare_operators(data):
    # Declare operators for each recipe
    operator_list = []
    for key, value in sorted(data['Recipes'].items(), key=lambda item: item[1]["Time"], reverse=True):
        key = key.replace(' ', '_')
        operator_temp = make_operator(value)
        operator_temp.__name__ = 'op_' + key
        operator_list.append(operator_temp)
    pyhop.declare_operators(*operator_list)

def add_heuristic(data, ID):
    # Add heuristic to prune search branches
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        return curr_task not in tasks
    pyhop.add_check(heuristic)

def set_up_state(data, ID, time=0):
    # Initialize the state with items, tools, and initial quantities
    state = pyhop.State('state')
    state.time = {ID: time}
    for item in data['Items'] + data['Tools']:
        setattr(state, item, {ID: 0})
    for item, num in data['Initial'].items():
        setattr(state, item, {ID: num})
    return state

def set_up_goals(data, ID):
    # Set up goals based on desired quantities of items
    return [('have_enough', ID, item, num) for item, num in data['Goal'].items()]

def run_test_case(data, initial, goal, max_time):
    state = set_up_state(data, 'agent', time=max_time)
    for item, num in initial.items():
        setattr(state, item, {'agent': num})
    goals = [('have_enough', 'agent', item, num) for item, num in goal.items()]
    result = pyhop.pyhop(state, goals, verbose=1)
    return result

def calculate_total_time(actions, data):
    total_time = 0
    for action in actions:
        op_name = action[0]
        for key, value in data['Recipes'].items():
            if 'op_' + key.replace(' ', '_') == op_name:
                total_time += value['Time']
                break
    return total_time

if __name__ == '__main__':
    rules_filename = 'crafting.json'
    with open(rules_filename) as f:
        data = json.load(f)
    
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')

    test_cases = [
        ({'plank': 1}, {'plank': 1}, 0),
        ({}, {'plank': 1}, 300),
        ({'plank': 3, 'stick': 2}, {'wooden_pickaxe': 1}, 10),
        ({}, {'iron_pickaxe': 1}, 100),
        ({}, {'cart': 1, 'rail': 10}, 175),
        ({}, {'cart': 1, 'rail': 20}, 250)
    ]

    for i, (initial, goal, max_time) in enumerate(test_cases):
        print(f"Running test case {i+1}")
        result = run_test_case(data, initial, goal, max_time)
        total_time = calculate_total_time(result, data)
        print(f"Test case {i+1} result: {result}")
        print(f"Total time: {total_time} (Max time: {max_time})\n")