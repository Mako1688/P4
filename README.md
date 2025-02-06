# Hierarchical Task Network (HTN) Planning for Minecraft - autoHTN.py
by Marco Ogaz-Vega and Elvis Ho

## Overview

This project implements a Hierarchical Task Network (HTN) planner for crafting items in Minecraft. The planner uses the `pyhop` library to generate a sequence of actions to achieve specified goals based on given recipes and initial state.

## Files

- `autoHTN.py`: The main script that sets up the HTN planner and executes the planning process.

## How It Works

### Heuristics

1. **heuristic**
   - Checks if the current task is already in the task list if so prune that branch.

2. **heuristic2**
   - Makes sure the depth doesnt go further than 500.


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


# Hierarchical Task Network (HTN) Planning for Minecraft - manualHTN.py

## Overview

This project implements a Hierarchical Task Network (HTN) planner for crafting items in Minecraft. The planner uses the pyhop library to generate a sequence of actions to achieve specified goals based on given recipes and the initial state.

## Files
- `manualHTN.py`: The script that defines operators, methods, and manually handles the planning process.

## How It Works

### Operators

1. **op_punch_for_wood**
   - Collects wood by punching trees.

2. **op_craft_plank**
   - Crafts planks from collected wood.

3. **op_craft_stick**
   - Crafts sticks from planks.

4. **op_craft_bench**
   - Crafts a crafting bench from planks.

5. **op_craft_wooden_axe_at_bench**
   - Crafts a wooden axe at the crafting bench using planks and sticks. 

### Main Execution

1. **Load Initial State and Goals**
   - Initializes the state and sets the crafting goals based on the task.

2. **Declare Operators and Methods**
   - Defines the operators and methods needed for crafting items.

3. **Run Planner**
   - Calls `pyhop.pyhop` to find a plan to achieve the goals from the initial state.
   - The planner uses the defined methods and operators to generate a sequence of actions.