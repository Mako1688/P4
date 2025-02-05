from os import stat
from sys import settrace
import pyhop
import json

def check_enough (state, ID, item, num):
	if getattr(state,item)[ID] >= num: return []
	return False

def produce_enough (state, ID, item, num):
	return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods ('have_enough', check_enough, produce_enough)

def produce (state, ID, item):
	return [('produce_{}'.format(item), ID)]

pyhop.declare_methods ('produce', produce)

def make_method(name, rule):
    # Generate a method for a given recipe
    def method(state, ID):
        subTasks = []  # Initialize the list of subtasks
        for prereq in rule["Recipes"][name]:  # Iterate over the prerequisites of the recipe
            if prereq == "Requires":  # If the prerequisite is a requirement
                reqItem = next(iter(rule["Recipes"][name][prereq]))  # Get the required item
                subTasks.append(('have_enough', ID, reqItem, rule["Recipes"][name][prereq][reqItem]))  # Add the subtask to check if we have enough of the required item
            if prereq == "Consumes":  # If the prerequisite is a consumption
                for item in rule["Recipes"][name][prereq]:  # Iterate over the items to be consumed
                    subTasks.append(('have_enough', ID, item, rule["Recipes"][name][prereq][item]))  # Add the subtask to check if we have enough of the item to be consumed
        subTasks.append(('op_' + name, ID))  # Add the subtask to perform the operation
        return subTasks  # Return the list of subtasks
    return method  # Return the method

def declare_methods(data):
    for item in data["Items"]:  # Iterate over the items in the data
        methods = []  # Initialize the list of methods
        for recipe in data["Recipes"]:  # Iterate over the recipes in the data
            newMethod = None  # Initialize the new method
            for category in data["Recipes"][recipe]:  # Iterate over the categories in the recipe
                if category == "Produces":  # If the category is a production
                    if item == next(iter(data["Recipes"][recipe][category])):  # If the item is produced by the recipe
                        newMethod = make_method(recipe, data)  # Create the method for the recipe
                        newMethod.__name__ = recipe  # Set the name of the method
                        if methods == []:  # If the list of methods is empty
                            methods.append(newMethod)  # Add the new method to the list
                        else:  # If the list of methods is not empty
                            for method in methods:  # Iterate over the methods in the list
                                if (data["Recipes"][method.__name__]["Time"] >= data["Recipes"][recipe]["Time"]) and newMethod not in methods:  # If the new method is faster than the existing method
                                    methods.insert(methods.index(method), newMethod)  # Insert the new method before the existing method
                            if newMethod not in methods:  # If the new method is not in the list
                                methods.append(newMethod)  # Add the new method to the list
        name = "produce_" + item  # Create the name for the method
        pyhop.declare_methods(name, *methods)  # Declare the methods to pyhop
        methods.clear()  # Clear the list of methods

    for tool in data["Tools"]:  # Iterate over the tools in the data
        methods = []  # Initialize the list of methods
        for recipe in data["Recipes"]:  # Iterate over the recipes in the data
            newMethod = None  # Initialize the new method
            for category in data["Recipes"][recipe]:  # Iterate over the categories in the recipe
                if category == "Produces":  # If the category is a production
                    if tool == next(iter(data["Recipes"][recipe][category])):  # If the tool is produced by the recipe
                        newMethod = make_method(recipe, data)  # Create the method for the recipe
                        newMethod.__name__ = recipe  # Set the name of the method
                        if methods == []:  # If the list of methods is empty
                            methods.append(newMethod)  # Add the new method to the list
                        else:  # If the list of methods is not empty
                            for method in methods:  # Iterate over the methods in the list
                                if (data["Recipes"][method.__name__]["Time"] >= data["Recipes"][recipe]["Time"]) and newMethod not in methods:  # If the new method is faster than the existing method
                                    methods.insert(methods.index(method), newMethod)  # Insert the new method before the existing method
                            if newMethod not in methods:  # If the new method is not in the list
                                methods.append(newMethod)  # Add the new method to the list
        name = "produce_" + tool  # Create the name for the method
        pyhop.declare_methods(name, *methods)  # Declare the methods to pyhop
        methods.clear()  # Clear the list of methods

def make_operator(rule):
    # Generate an operator for a given recipe
    def operator(state, ID):
        for element in rule:  # Iterate over the elements in the rule
            if element == 'Produces':  # If the element is a production
                item = rule[element]  # Get the item to be produced
                item_name = next(iter(rule[element]))  # Get the name of the item
                value = rule[element][item_name]  # Get the value of the item
                setattr(state, item_name, {ID: getattr(state, item_name)[ID] + value})  # Update the state with the produced item
            elif element == 'Requires':  # If the element is a requirement
                for item in rule[element]:  # Iterate over the required items
                    value = rule[element][item]  # Get the value of the required item
                    if getattr(state, item)[ID] >= value:  # If the state has enough of the required item
                        setattr(state, item, {ID: value})  # Update the state with the required item
                    else:  # If the state does not have enough of the required item
                        return False  # Return False
            elif element == 'Consumes':  # If the element is a consumption
                for item in rule[element]:  # Iterate over the items to be consumed
                    value = rule[element][item]  # Get the value of the item to be consumed
                    if getattr(state, item)[ID] >= value:  # If the state has enough of the item to be consumed
                        setattr(state, item, {ID: getattr(state, item)[ID] - value})  # Update the state with the consumed item
                    else:  # If the state does not have enough of the item to be consumed
                        return False  # Return False
            elif element == "Time":  # If the element is time
                value = rule[element]  # Get the value of the time
                if getattr(state, "time")[ID] >= value:  # If the state has enough time
                    setattr(state, "time", {ID: getattr(state, "time")[ID] - value})  # Update the state with the time
                else:  # If the state does not have enough time
                    return False  # Return False
        return state  # Return the updated state
    return operator  # Return the operator

def declare_operators(data):
    ops = []  # Initialize the list of operators
    for element in data["Recipes"]:  # Iterate over the recipes in the data
        holder = make_operator(data["Recipes"][element])  # Create the operator for the recipe
        holder.__name__ = "op_" + element  # Set the name of the operator
        ops.append(holder)  # Add the operator to the list
    pyhop.declare_operators(*ops)  # Declare the operators to pyhop

def add_heuristic(data, ID):
    def prune_large_quantities(state, curr_task, tasks, plan, depth, calling_stack):
        for item in data["Items"]:  # Iterate over the items in the data
            if item != "rail":  # If the item is not a rail
                if getattr(state, item)[ID] > 18:  # If the state has more than 18 of the item
                    return True  # Prune the branch
        return False  # Do not prune the branch

    def initialize_tool_flags(state, curr_task, tasks, plan, depth, calling_stack):
        if depth == 0:  # If the depth is 0
            for tool in data["Tools"]:  # Iterate over the tools in the data
                made_tool = "made_" + tool  # Create the name for the tool flag
                setattr(state, made_tool, {ID: 0})  # Initialize the tool flag in the state
        return False  # Do not prune the branch

    def prune_duplicate_tool_creation(state, curr_task, tasks, plan, depth, calling_stack):
        if curr_task[0] == 'produce':  # If the current task is a production
            item = curr_task[2]  # Get the item to be produced
            for tool in data["Tools"]:  # Iterate over the tools in the data
                if item == tool:  # If the item is a tool
                    made_check = "made_" + tool  # Create the name for the tool flag
                    if getattr(state, made_check)[ID] != 0:  # If the tool has already been made
                        return True  # Prune the branch
                    else:  # If the tool has not been made
                        setattr(state, made_check, {ID: getattr(state, made_check)[ID] + 1})  # Update the tool flag in the state
                        return False  # Do not prune the branch
        return False  # Do not prune the branch

    pyhop.add_check(prune_large_quantities)  # Add the prune_large_quantities heuristic to pyhop
    pyhop.add_check(initialize_tool_flags)  # Add the initialize_tool_flags heuristic to pyhop
    pyhop.add_check(prune_duplicate_tool_creation)  # Add the prune_duplicate_tool_creation heuristic to pyhop
    
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
