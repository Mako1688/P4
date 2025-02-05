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

def make_method (name, rule):
	def method (state, ID):
		final = []
		for key, value in rule.items():
			if key != 'Produces':
				if type(value) == dict:
					for item, num in value.items():
						final.append(('have_enough', ID, item, num))
		operator = "op_" + name
		operator = operator.replace(' ', '_')
		final.append((operator, ID))
		return final
	method.__name__ = name
	return method

def declare_methods (data):
	# some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first

	# your code here
	### TODO
	# I gotta redo declare methods
	# New approach: First make the methods from the Recipes
	# Then: Sort the methods into common items(all the cobble methods go in one place)
	methodList = []
	for recipeName in data["Recipes"].keys():
		rules = data["Recipes"][recipeName]
		method = make_method(recipeName, rules)
		methodList.append(method)
	# now I need to sort the methods by the item
	# CREATE A SORTING METHOD THAT RETURNS A DICT OF ITEMS AND VALUESfor key, value in sorted(data['Recipes'].items(), key=lambda item: item[1]["Time"], reverse=True):
	dict_methods = {}
	for key, value in sorted(data['Recipes'].items(), key=lambda item: item[1]["Time"], reverse=True):
		key = key.replace(" ", "_")
		for name in value['Produces'].items():
			if name in dict_methods:
				if isinstance(dict_methods[name], list):
					cur_method = make_method(key, value)
					dict_methods[name].append(cur_method)
				else:
					dict_methods[name] = [dict_methods[name]]
			else:
				cur_method = make_method(key, value)
				dict_methods[name] = [cur_method]
	sortedMethods = dict_methods
	# time to declare all the methods
	for item, temp in sortedMethods.items():
		temp = []
		for method in sortedMethods[item]:
			#replace spaces with underscores
			method.__name__ = method.__name__.replace(' ', '_')
			temp.append(method)
		pyhop.declare_methods("produce_" + item[0], *temp)

	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)	
	# pyhop.print_methods()
	pass


def make_operator (rule):
	def operator (state, ID):
		# your code here
		for key, value in rule.items():
			if key == 'Produces':
				for item, num in  value.items():
					setattr(state, item, {ID: getattr(state, item)[ID] + num})
			if key == 'Time':
				if state.time[ID] >= num:
					state.time[ID] -= num
				else:
					return False
			if key == 'Consumes':
				for item, num in value.items():
					if getattr(state, item)[ID] >= num:
						setattr(state, item, {ID: getattr(state, item)[ID] - num})
		return state
	return operator

def declare_operators (data):
	# your code here
	# hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)
	op_list = []
	for key, value in sorted(data['Recipes'].items(), key=lambda item: item[1]["Time"], reverse=True):
		key = key.replace(" ", "_")
		time_for_this = value['Time']
		temp = make_operator(value)
		temp.__name__ = 'op_' + key
		op_list.append((temp, time_for_this))
		sorted(op_list, key=lambda item: time_for_this, reverse=False)
	for cur, _ in op_list:
		pyhop.declare_operators(cur)

def add_heuristic (data, ID):
	# prune search branch if heuristic() returns True
	# do not change parameters to heuristic(), but can add more heuristic functions with the same parameters: 
	# e.g. def heuristic2(...); pyhop.add_check(heuristic2)
	def heuristic (state, curr_task, tasks, plan, depth, calling_stack):

		if curr_task in tasks:
			return False
		return True
		return tasks
	
	def heuristic2 (state, curr_task, tasks, plan, depth, calling_stack):
		return depth > 500
		# if True, prune this branch

	pyhop.add_check(heuristic)
	pyhop.add_check(heuristic2)
    
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
    # pyhop.pyhop(state, [('have_enough', 'agent', 'plank', 1)], verbose=3)  # a. Given {'plank': 1}, achieve {'plank': 1} [time <= 0]
    # pyhop.pyhop(state, [('have_enough', 'agent', 'plank', 1)], verbose=1)  # b. Given {}, achieve {'plank': 1} [time <= 300]
    pyhop.pyhop(state, [('have_enough', 'agent', 'wooden_pickaxe', 1)], verbose=3)  # c. Given {'plank': 3, 'stick': 2}, achieve {'wooden_pickaxe': 1} [time <= 10]
    # pyhop.pyhop(state, [('have_enough', 'agent', 'iron_pickaxe', 1)], verbose=1)  # d. Given {}, achieve {'iron_pickaxe': 1} [time <= 100]
    # pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1), ('have_enough', 'agent', 'rail', 10)], verbose=1)  # e. Given {}, achieve {'cart': 1, 'rail': 10} [time <= 175]
    # pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1), ('have_enough', 'agent', 'rail', 20)], verbose=1)  # f. Given {}, achieve {'cart': 1, 'rail': 20} [time <= 250]