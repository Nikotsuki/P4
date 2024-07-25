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

def findTime(recipe):
    return recipe[1]['Time']

def make_method(name, rule):
    def method(state, ID):
        subtasks = []
        produced = set()
        for item, qty in rule.get('Requires', {}).items():
            if item not in produced:
                subtasks.append(('have_enough', ID, item, qty))
                produced.add(item)
        for item, qty in rule.get('Consumes', {}).items():
            if item not in produced:
                subtasks.append(('have_enough', ID, item, qty))
                produced.add(item)
        subtasks.append(('op_' + name.replace(' ', '_'), ID))
        print("THIS IS SUBTASKS")
        print(subtasks)
    method.__name__ = name.replace(' ', '_')
    return method


'''def make_method (name, rule):
    def method (state, ID):
        # your code here
        requires = rule[0]
        consumes = rule[1]
        
        l = []
        
        c = [('have_enough', ID, 'ingot', 0), ('have_enough', ID, 'coal', 0), ('have_enough', ID, 'ore', 0), ('have_enough', ID, 'cobble', 0), ('have_enough', ID, 'stick', 0), ('have_enough', ID, 'plank', 0), ('have_enough', ID, 'wood', 0)]
        for check in c:
            for key in consumes.keys():
                if key == check[2]:
                    newCheck = ('have_enough', ID, key, consumes[key])
                    l.append(newCheck)
        
        for key in requires.keys():
            #l.append(('have_enough', ID, key, requires[key]))
            l = [('have_enough', ID, key, requires[key])] + l
        
        l.append((name, ID))
        
        return l

    return method'''

def declare_methods(data):

    recipe_list = []
    for recipe, rule in data['Recipes'].items():
        recipe_list.append((recipe, rule))

    recipe_list.sort(reverse = False,key=findTime)

    methods = {}
    for name, rule in recipe_list:
        method = make_method(name, rule)
        for produced_item in rule['Produces'].keys():
            if 'produce_' + produced_item not in methods:
                methods['produce_' + produced_item] = []
            methods['produce_' + produced_item].append(method)
    for produced_item, method_list in methods.items():       
        pyhop.declare_methods(produced_item, *method_list)

'''def declare_methods (data):
    # some recipes are faster than others for the same product even though they might require extra tools
    # sort the recipes so that faster recipes go first

    # your code here
    # hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)    
    
    for item in data['Recipes'].keys():
        produces = list(data['Recipes'][item]['Produces'].keys())[0]
        time = data['Recipes'][item]['Time']
        items = [(time, item)]
        
        for item2 in data['Recipes'].keys():
            produces2 = list(data['Recipes'][item2]['Produces'].keys())[0]
            if produces2 == produces and item != item2:
                time2 = data['Recipes'][item2]['Time']
                items.append((time2, item2))
        
        items = sorted(items)
        
        methods = []
        for recipe in items:
            requires = {}
            if 'Requires' in data['Recipes'][recipe[1]]:
                requires = data['Recipes'][recipe[1]]['Requires']
            consumes = {}
            if 'Consumes' in data['Recipes'][recipe[1]]:
                consumes = data['Recipes'][recipe[1]]['Consumes']
            name = 'op_'+recipe[1]
            m = make_method(name, [requires, consumes])
            m.__name__ = recipe[1]
            methods.append(m)
        
        name = 'produce_'+produces
        newList = [name] + methods
        
        pyhop.declare_methods(*newList)
        
    return         '''

def make_operator(name, rule):
    def operator(state, ID):
        if all(getattr(state, item)[ID] >= qty for item, qty in rule.get('Requires', {}).items()) and\
            all(getattr(state, item)[ID] >= qty for item, qty in rule.get('Consumes', {}).items()) and\
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

'''def make_operator (rule):
    #print(rule)
    def operator (state, ID):
        # your code here
        requires = rule[0]
        consumes = rule[1]
        produces = rule[2]
        time = rule[3]
        
        # make sure all requirements are met.
        for key in requires.keys():
            if requires[key] > getattr(state, key)[ID]:
                return False
        
        # check that there is enough time
        if time > state.time[ID]:
            return False
        
        
        for key in consumes.keys():
            if consumes[key] > getattr(state, key)[ID]:
                return False
        # remove items that are consumed.
        for key in consumes.keys():
            total = getattr(state, key)[ID]
            consumed = consumes[key]
            newTotal = total - consumed
            setattr(state, key, {ID: newTotal})
        
        # add items that are created
        for key in produces.keys():
            total = getattr(state, key)[ID]
            produced = produces[key]
            newTotal = total + produced
            setattr(state, key, {ID: newTotal})
        
        state.time[ID] -= time
        
        # successful return
        return state
    
    return operator'''

def declare_operators(data):
    operators = []
    for name, rule in data['Recipes'].items():
        operator = make_operator(name, rule)
        operators.append(operator)
    pyhop.declare_operators(*operators)


'''def declare_operators (data):
    # your code here
    # hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)
    
    for item in data['Recipes'].keys():        
        requires = {}
        consumes = {}
        # dictionary containing requirements.
        if 'Requires' in data['Recipes'][item]:
            requires = data['Recipes'][item]['Requires']
        # dictionary containing costs.
        if 'Consumes' in data['Recipes'][item]:
            consumes = data['Recipes'][item]['Consumes']
        # dictionary containing results.
        produces = data['Recipes'][item]['Produces']
        # int that represents the time for a task.
        time = data['Recipes'][item]['Time']
        
        rule = [requires, consumes, produces, time]
        
        operator = make_operator(rule)
        operator.__name__ = 'op_'+item
        
        pyhop.declare_operators(operator)
    
    return'''

def add_heuristic(data, ID):
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        #print("HI")
        #print(curr_task)
        #print("hi")
        print(calling_stack)
        '''if len(tasks) > 1:
            task1 = tasks[1]
            #print(task1)
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
                tasks.remove(tasks[1])'''
    
        if curr_task[0] == 'produce' and curr_task[2] in data['Tools'] and curr_task in calling_stack:
            return True
    
        # These check to see if the tool that we are considering making will be used enough to actually be a benefit.
        # Doesn't work how I would want it to, but it is able to pass all of the tests.
        if curr_task[0] == 'produce' and curr_task[2] == 'iron_pickaxe':
            required = 0
            for task in tasks:
                if task[0] == 'have_enough' and task[2] == 'ingot':
                        required += task[3]
            #print(required)
            if required <= 11 and required > 0:
                return True

        if curr_task[0] == 'produce' and curr_task[2] == 'wooden_axe':
            required = 0
            for task in tasks:
                if task[0] == 'have_enough' and task[2] == 'wood':
                        required += task[3]
            if required <= 9 and required > 0:
                return True
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

    state = set_up_state(data, 'agent', time=10)  # set the initial time
    goals = set_up_goals(data, 'agent')

    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')

    pyhop.print_operators()
    pyhop.print_methods()

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