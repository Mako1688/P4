# AutoHTN

## Overview

AutoHTN is a hierarchical task network (HTN) planner designed to solve crafting problems. Given a set of initial resources and a goal, it determines the sequence of actions required to achieve the goal within a specified time limit.

## Heuristics

The heuristic function used in AutoHTN is designed to prune the search space to improve planning efficiency. The primary heuristic implemented is a time-based pruning heuristic:

- **Time-Based Pruning**: This heuristic prunes any search branch where the accumulated time exceeds a specified threshold (e.g., 240 units of time). This helps in focusing the search on feasible plans that can be completed within the given time constraints.

## Test Cases

The following test cases are used to validate the planner:

1. **Given**: `{'plank': 1}`, **Achieve**: `{'plank': 1}`, **Time**: `<= 0`
2. **Given**: `{}`, **Achieve**: `{'plank': 1}`, **Time**: `<= 300`
3. **Given**: `{'plank': 3, 'stick': 2}`, **Achieve**: `{'wooden_pickaxe': 1}`, **Time**: `<= 10`
4. **Given**: `{}`, **Achieve**: `{'iron_pickaxe': 1}`, **Time**: `<= 100`
5. **Given**: `{}`, **Achieve**: `{'cart': 1, 'rail': 10}`, **Time**: `<= 175`
6. **Given**: `{}`, **Achieve**: `{'cart': 1, 'rail': 20}`, **Time**: `<= 250`

## Usage

To run the planner, execute the `autoHTN.py` script. The script will load the crafting rules from `crafting.json`, set up the initial state and goals, and then run the planner for each test case.

```bash
python autoHTN.py