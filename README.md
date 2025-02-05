# Hierarchical Task Network (HTN) Planning for Minecraft

## Overview

This project implements a Hierarchical Task Network (HTN) planner for crafting items in Minecraft. The planner uses the `pyhop` library to generate a sequence of actions to achieve specified goals based on given recipes and initial state.

## Files

- `autoHTN.py`: The main script that sets up the HTN planner and executes the planning process.

## How It Works

### Functions

1. **check_enough(state, ID, item, num)**
   - Checks if there is enough of the specified item in the state.
   - Returns an empty list if there is enough, otherwise returns `False`.

2. **produce_enough(state, ID, item, num)**
   - Creates tasks to produce the specified item if there isn't enough.
   - Returns a list of tasks to produce the item and then check if there is enough.

3. **produce(state, ID, item)**
   - Creates a task to produce the specified item.
   - Returns a list with a single task to produce the item.

4. **make_method(name, rule)**
   - Generates a method for a given recipe.
   - The method checks if required and consumed items are available and then adds a production task.

5. **declare_methods(data)**
   - Declares methods for each product based on the recipes.
   - Organizes recipes by the product they produce and sorts them by time.

6. **make_operator(rule)**
   - Generates an operator for a given recipe.
   - The operator checks if there is enough time and required items, consumes items, produces output, and updates the state.

7. **declare_operators(data)**
   - Declares operators for each recipe.
   - Iterates through recipes, creates operators, and declares them to `pyhop`.

8. **add_heuristic(data, ID)**
   - Adds heuristic checks to prune the search space.
   - Includes checks to avoid deep recursion and overproducing items.

9. **set_up_state(data, ID, time=0)**
   - Initializes the state with given items, tools, and initial quantities.
   - Sets the initial time for the agent.

10. **set_up_goals(data, ID)**
    - Sets up the goals based on the desired quantities of items.
    - Returns a list of goals to achieve.

### Main Execution

1. **Load Data**
   - The script reads the `crafting.json` file to get the data.

2. **Set Up State and Goals**
   - Initializes the state and goals based on the data.

3. **Declare Operators and Methods**
   - Declares operators and methods for the recipes.

4. **Add Heuristic**
   - Adds heuristic checks to prune the search space.

5. **Run Planner**
   - Calls `pyhop.pyhop` to find a plan to achieve the goals from the initial state.
   - The planner uses the methods and operators defined in the script to generate a sequence of actions.
