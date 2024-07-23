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
        # your code here
        subtasks = []
        for item, qty in rule.get('Requires', {}).items():
            subtasks.append(('have_enough', ID, item, qty))
        for item, qty in rule.get('Consumes', {}).items():
            subtasks.append(('have_enough', ID, item, qty))
        subtasks.append(('op_' + name.replace(' ', '_'), ID))
        return subtasks
    return method

def declare_methods(data):
    for name, rule in data['Recipes'].items():
        method = make_method(name, rule)
        pyhop.declare_methods('produce_' + name.replace(" ", "_"), method)

def make_operator(rule):
    def operator(state, ID):
        if all(state.get(res, {}).get(ID, 0) >= qty for res, qty in rule.get('Requires', {}).items()) and \
        state.time[ID] >= rule['Time']:
            for res, qty in rule.get('Consumes', {}).items():
                state[res][ID] -= qty
            for res, qty in rule['Produces'].items():
                state[res][ID] += qty
            state.time[ID] -= rule['Time']
            return state
        return False
    return operator

def declare_operators(data):
    # your code here
    operators = []
    for name, rule in data['Recipes'].items():
        operator = make_operator(rule)
        operator.__name__ = 'op_' + name.replace(' ', '_')
        operators.append(operator)
    pyhop.declare_operators(*operators)

def add_heuristic(data, ID):
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        # Implement your heuristic here
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
        getattr(state, item)[ID] = num

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

    state = set_up_state(data, 'agent', time=239) # allot time here
    goals = set_up_goals(data, 'agent')

    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')

    pyhop.print_operators()
    pyhop.print_methods()

    # Hint: verbose output can take a long time even if the solution is correct; 
    # try verbose=1 if it is taking too long
    #pyhop.pyhop(state, goals, verbose=3)
    pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)