import pyhop
import json

def check_enough(state, ID, item, num):
    if getattr(state, item)[ID] >= num:
        return []
    return False

def produce_enough(state, ID, item, num):
    if getattr(state, item)[ID] < num:
        return [('produce', ID, item), ('have_enough', ID, item, num)]
    return []

pyhop.declare_methods('have_enough', check_enough, produce_enough)

def produce(state, ID, item):
    return [('produce_{}'.format(item), ID)]

pyhop.declare_methods('produce', produce)

def make_method(name, rule):
    def method(state, ID, produced=set()):
        subtasks = []
        for item, qty in rule.get('Requires', {}).items():
            if item not in produced:
                subtasks.append(('have_enough', ID, item, qty))
                produced.add(item)
        for item, qty in rule.get('Consumes', {}).items():
            if item not in produced:
                subtasks.append(('have_enough', ID, item, qty))
                produced.add(item)
        subtasks.append(('op_' + name.replace(' ', '_'), ID))
        return subtasks
    return method

def declare_methods(data):
    methods = {}
    for name, rule in data['Recipes'].items():
        method = make_method(name, rule)
        for produced_item in rule['Produces'].keys():
            if 'produce_' + produced_item not in methods:
                methods['produce_' + produced_item] = []
            methods['produce_' + produced_item].append(method)
    for produced_item, method_list in methods.items():
        pyhop.declare_methods(produced_item, *method_list)

def make_operator(name, rule):
    def operator(state, ID):
        if all(getattr(state, item)[ID] >= qty for item, qty in rule.get('Requires', {}).items()) and \
        state.time[ID] >= rule['Time']:
            for item, qty in rule.get('Consumes', {}).items():
                getattr(state, item)[ID] -= qty
            for item, qty in rule.get('Produces', {}).items():
                getattr(state, item)[ID] += qty
            state.time[ID] -= rule['Time']
            return state
        return False
    operator.__name__ = 'op_' + name.replace(' ', '_')
    return operator

def declare_operators(data):
    operators = []
    for name, rule in data['Recipes'].items():
        operator = make_operator(name, rule)
        operators.append(operator)
    pyhop.declare_operators(*operators)

def add_heuristic(data, ID):
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        print(curr_task)
        try:
            task1 = (tasks[1])
            print(task1)
            if state.wooden_pickaxe[ID] >= 1 and task1 == ('op_craft_wooden_pickaxe_at_bench', 'agent'):
                tasks.remove(tasks[1])
            if state.stone_pickaxe[ID] >= 1 and task1 == ('op_craft_stone_pickaxe_at_bench', 'agent'):
                tasks.remove(tasks[1])
            if state.iron_pickaxe[ID] >= 1 and task1 == ('op_craft_iron_pickaxe_at_bench', 'agent'):
                tasks.remove(tasks[1])
            if state.wooden_axe[ID] >= 1 and task1 == ('op_craft_wooden_axe_at_bench', 'agent'):
                tasks.remove(tasks[1])
            if state.stone_axe[ID] >= 1 and task1 == ('op_craft_stone_axe_at_bench', 'agent'):
                tasks.remove(tasks[1])
            if state.iron_axe[ID] >= 1 and task1 == ('op_craft_iron_axe_at_bench', 'agent'):
                tasks.remove(tasks[1])
            if state.bench[ID] >= 1 and task1 == ('op_craft_bench', 'agent'):
                tasks.remove(tasks[1])
            if state.furnace[ID] >= 1 and task1 == ('op_craft_furnace', 'agent'):
                tasks.remove(tasks[1])
        except IndexError:
            #print(plan)
            #print(calling_stack)
            return
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

    state = set_up_state(data, 'agent', time=250)  # set the initial time
    goals = set_up_goals(data, 'agent')

    declare_operators(data)
    declare_methods(data)

    pyhop.print_operators()
    pyhop.print_methods()
    add_heuristic(data, 'agent')

    #state.plank = {'agent': 3}
    #state.stick = {'agent': 2}

    #Test cases
    #result = pyhop.pyhop(state, [('have_enough', 'agent', 'plank', 1)], verbose=3) # 1 w/ 0 time // CLEAR
    #result = pyhop.pyhop(state, [('have_enough', 'agent', 'plank', 1)], verbose=3) # 2 w/ 300 time // CLEAR
    #result = pyhop.pyhop(state, [('have_enough', 'agent', 'wooden_pickaxe', 1)], verbose=3) # 3 w/ 10 time // CLEAR
    result = pyhop.pyhop(state, [('have_enough', 'agent', 'iron_pickaxe', 1)], verbose=3) # 3 w/ 100 time // CLEAR
    #result = pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1), ('have_enough', 'agent', 'rail', 1)], verbose=3) # 5 w/ 175 time // CLEAR
    #result = pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3) # 6 w/ 250 time // CLEAR


    #result = pyhop.pyhop(state, goals, verbose=3)
    print("Result:", result)