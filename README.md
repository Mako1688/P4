# Hierarchical Task Network (HTN) Planning for Minecraft

## Overview

This project implements a Hierarchical Task Network (HTN) planner for crafting items in Minecraft. The planner uses the `pyhop` library to generate a sequence of actions to achieve specified goals based on given recipes and initial state.

## Files

- `autoHTN.py`: The main script that sets up the HTN planner and executes the planning process.

## How It Works

### Heuristics

1. **heuristic**
   - Checks if the current task is already in the task list

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
