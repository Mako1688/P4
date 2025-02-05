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
    # Create a method for a given recipe
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
    # Declare methods for all items and tools
    def declare_for_category(category):
        for item in data[category]:  # Iterate over the items in the category
            methods = []  # Initialize the list of methods
            for recipe in data["Recipes"]:  # Iterate over the recipes in the data
                newMethod = None  # Initialize the new method
                for cat in data["Recipes"][recipe]:  # Iterate over the categories in the recipe
                    if cat == "Produces":  # If the category is a production
                        if item == next(iter(data["Recipes"][recipe][cat])):  # If the item is produced by the recipe
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

    declare_for_category("Items")  # Declare methods for items
    declare_for_category("Tools")  # Declare methods for tools

def make_operator(rule):
    # Create an operator for a given recipe
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
                    if getattr(state, item)[ID] < value:  # If the state does not have enough of the required item
                        return False  # Return False
            elif element == 'Consumes':  # If the element is a consumption
                for item in rule[element]:  # Iterate over the items to be consumed
                    value = rule[element][item]  # Get the value of the item to be consumed
                    if getattr(state, item)[ID] < value:  # If the state does not have enough of the item to be consumed
                        return False  # Return False
                    setattr(state, item, {ID: getattr(state, item)[ID] - value})  # Update the state with the consumed item
            elif element == "Time":  # If the element is time
                value = rule[element]  # Get the value of the time
                if getattr(state, "time")[ID] < value:  # If the state does not have enough time
                    return False  # Return False
                setattr(state, "time", {ID: getattr(state, "time")[ID] - value})  # Update the state with the time
        return state  # Return the updated state
    return operator  # Return the operator

def declare_operators(data):
    # Declare operators for all recipes
    ops = []  # Initialize the list of operators
    for element in data["Recipes"]:  # Iterate over the recipes in the data
        holder = make_operator(data["Recipes"][element])  # Create the operator for the recipe
        holder.__name__ = "op_" + element  # Set the name of the operator
        ops.append(holder)  # Add the operator to the list
    pyhop.declare_operators(*ops)  # Declare the operators to pyhop

def add_heuristic(data, ID):
    # Add heuristics for pruning the search space
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
                    setattr(state, made_check, {ID: getattr(state, made_check)[ID] + 1})  # Update the tool flag in the state
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

if __name__ == '__main__':
    rules_filename = 'crafting.json' 

    with open(rules_filename) as f: 
        data = json.load(f)

    state = set_up_state(data, 'agent', time=250) # Set time
    goals = set_up_goals(data, 'agent')  # Set up the goals

    declare_operators(data)  
    declare_methods(data)  
    add_heuristic(data, 'agent')  

    pyhop.print_operators() 
    pyhop.print_methods()  
    
	# Hint: verbose output can take a long time even if the solution is correct; 
	# try verbose=1 if it is taking too long
    # pyhop.pyhop(state, goals, verbose=3)
    # pyhop.pyhop(state, [('have_enough', 'agent', 'wood', 12)], verbose=1)
    # pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)
    
    # Test cases
    # pyhop.pyhop(state, [('have_enough', 'agent', 'plank', 1)], verbose=1)  # a. Given {'plank': 1}, achieve {'plank': 1} [time <= 0]
    # pyhop.pyhop(state, [('have_enough', 'agent', 'plank', 1)], verbose=1)  # b. Given {}, achieve {'plank': 1} [time <= 300]
    pyhop.pyhop(state, [('have_enough', 'agent', 'wooden_pickaxe', 1)], verbose=1)  # c. Given {'plank': 3, 'stick': 2}, achieve {'wooden_pickaxe': 1} [time <= 10]
    # pyhop.pyhop(state, [('have_enough', 'agent', 'iron_pickaxe', 1)], verbose=1)  # d. Given {}, achieve {'iron_pickaxe': 1} [time <= 100]
    # pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1), ('have_enough', 'agent', 'rail', 10)], verbose=1)  # e. Given {}, achieve {'cart': 1, 'rail': 10} [time <= 175]
    # pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1), ('have_enough', 'agent', 'rail', 20)], verbose=1)  # f. Given {}, achieve {'cart': 1, 'rail': 20} [time <= 250]