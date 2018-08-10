"""
This is a simulation of a hypothesis about decentralized governance discussed here: [link to Medium]

Each agent gets a preference value and expertise value for each problem.
Expertise values are between 0 and 1 inclusive and are randomly assigned using an exponential function,
so that they are few experts for any given problem.
The sums of the preference values for each problem create a set of unique values greater than 0.
Preference values are assigned randomly to agents.

Two steps are allowed: 1) ask an agent for its highest unknown problem/preference pair, 2) ask an agent 
or agents to attempt to solve a problem (each agent votes for the correct or incorrect answer according 
to their expertise in the problem).

The goal is to solve the agents' top 10 preferred problems in the fewest steps (time)
and the fewest total problems solved (resources).

Three algorithms are tested here:
1) "Paradox" - Meant to solve the paradox of democracy requiring each group member to have equal influence 
to be fair and experts to have extra influence to be effective, this algorithm first discovers the top 10 
preferred problems in as few steps as it can, then asks only the experts in those problems to solve them.

2) "Technocracy" - Simply asks the experts in each problem to solve it. This algorithm saves time by not 
bothering with preferences but has to solve way more than the required 10 problems since it knows nothing 
about preferences.

3) "Direct democracy" - Starts by discovering preferences exactly like "Paradox", but instead of asking 
only experts to solve, asks everyone. Because expertise is handed out by e = x^^4 for a random x between 
0 and 1, experts in any given problem are a minority, and this algorithm struggles to solve any of the problems.
"""

import random
from random import shuffle
import matplotlib.pyplot as plt
import numpy as np

# SET UP
def create_problems_dict(number_of_problems, number_of_agents):
	problems = []
	total = number_of_problems
	while number_of_problems > 0:
		problems.append('problem'+str(number_of_problems))
		number_of_problems -= 1
	shuffle(problems)
	problems_dict = {}
	top_problems_dict = {}
	top_problem_count = 0
	for problem in problems:
		problems_dict[problem] = total
		if top_problem_count < 10:
			top_problems_dict[problem] = {'pref_total': total, 'solved': False}
			top_problem_count += 1
		total -= 1
	return [problems_dict, top_problems_dict]

def create_agents(number_of_agents):
	agents = {}
	known_preferences = {}
	while number_of_agents > 0:
		agents[number_of_agents] = {'preferences': {}, 'expertise': {}}
		known_preferences[number_of_agents] = {}
		number_of_agents -= 1
	return [agents, known_preferences]

def assign_preferences(agents, problems_dict):
	agent_keys = agents.keys()
	for problem in problems_dict:
		preference_fractions = []
		preference_denom = 0
		for agent in agents:
			rand = random.random()
			preference_fractions.append(rand)
			preference_denom += rand
		for rand in preference_fractions:
			preference_fractions[preference_fractions.index(rand)] = round(
					rand/preference_denom*problems_dict[problem], 1)
		shuffle(agent_keys)
		for agent in agent_keys:
			agents[agent]['preferences'][problem] = preference_fractions[int(agent)-1]
	return agents

def assign_expertise(agents, problems):
	for agent in agents.keys():
		for problem in problems:
			agents[agent]['expertise'][problem] = round(random.random()**4, 4)
	return agents

def init(number_of_agents, number_of_problems):
	problem_dicts = create_problems_dict(number_of_problems, number_of_agents)
	problems_dict = problem_dicts[0]
	top_problems_dict = problem_dicts[1]
	agent_dicts = create_agents(number_of_agents)
	agents = agent_dicts[0]
	agents = assign_preferences(agents, problems_dict)
	agents = assign_expertise(agents, problems_dict.keys())
	known_preferences = agent_dicts[1]
	return [agents, top_problems_dict, known_preferences]

# ALGORITHMS
# Paradox: first survey preferences to find top preffered problems, then ask only experts in those problems to solve them.
def paradox_solve(number_of_agents, number_of_problems):
	# set up
	initial_dicts = init(number_of_agents, number_of_problems)
	agents = initial_dicts[0]
	top_problems_dict = initial_dicts[1]
	known_preferences = initial_dicts[2]
	
	# ask preferences
	if number_of_problems > number_of_agents:
		starting_steps = number_of_problems 
	else: 
		starting_steps = number_of_agents
	preferences_list = search_for_top_preferences(starting_steps, agents, known_preferences, top_problems_dict, [], 0, {})
	steps = preferences_list[0]
	contain_percentage = preferences_list[1]
	hypothesized_top_problems = preferences_list[2]
	known_preferences = preferences_list[3]

	# ask experts to solve preferred problems
	solve = ask_experts_to_solve(agents, hypothesized_top_problems, steps, top_problems_dict, 0.5)
	if solve[0] == 100:
		return [solve[0], solve[1], solve[2]]
		"Paradox solved the top 10 preferred problems in "+str(solve[1])+" steps. Total problems solved: "+str(solve[2])
	elif solve[0] == 0:
		return [solve[0], solve[1], solve[2]]
		"Paradox failed to solve the top 10 preferred problems in "+str(solve[1])+" steps. Total problems solved: "+str(solve[2])
	elif solve[0] == -1:
		return [-1]
		"Paradox failed because it exceeded the max number of steps."

# Technocracy: ask experts in each problem to solve the problem, ignoring preferences (solves all the problems).
def technocracy_solve(number_of_agents, number_of_problems):
	# set up
	initial_dicts = init(number_of_agents, number_of_problems)
	agents = initial_dicts[0]
	top_problems_dict = initial_dicts[1]
	known_preferences = initial_dicts[2]

	# ask experts to solve all problems
	solve = ask_experts_to_solve(agents, agents[1]['preferences'].keys(), 0, top_problems_dict, 0.5)
	if solve[0] == 100:
		return [solve[0], solve[1], solve[2]]
		"Technocracy solved the top 10 preferred problems in "+str(solve[1])+" steps. Total problems solved: "+str(solve[2])
	elif solve[0] == 0:
		return [solve[0], solve[1], solve[2]]
		"Technocracy failed to solve the top 10 preferred problems in "+str(solve[1])+" steps. Total problems solved: "+str(solve[2])
	elif solve[0] == -1:
		return [-1]
		"Technocracy failed because it exceeded the max number of steps."

# Direct Democracy: first survey preferences, then ask everyone to solve each top problem 
# (probably fails with runtime error).
def direct_dem_solve(number_of_agents, number_of_problems):
	# set up
	initial_dicts = init(number_of_agents, number_of_problems)
	agents = initial_dicts[0]
	top_problems_dict = initial_dicts[1]
	known_preferences = initial_dicts[2]

	# ask preferences
	if number_of_problems > number_of_agents:
		starting_steps = number_of_problems 
	else: 
		starting_steps = number_of_agents
	preferences_list = search_for_top_preferences(starting_steps, agents, known_preferences, top_problems_dict, [], 0, {})
	steps = preferences_list[0]
	contain_percentage = preferences_list[1]
	hypothesized_top_problems = preferences_list[2]
	known_preferences = preferences_list[3]

	# ask for solves
	solve = ask_experts_to_solve(agents, hypothesized_top_problems, 0, top_problems_dict, 0)
	if solve[0] == 100:
		return [solve[0], solve[1], solve[2]]
		"Direct democracy solved the top 10 preferred problems in "+str(solve[1])+" steps. Total problems solved: "+str(solve[2])
	elif solve[0] == 0:
		return [solve[0], solve[1], solve[2]]
		"Direct democracy failed to solve the top 10 preferred problems in "+str(solve[1])+" steps. Total problems solved: "+str(solve[2])
	elif solve[0] == -1:
		return [-1]
		"Direct democracy failed because it exceeded the max number of steps."

# SUPPORT FUNCTIONS
# ask an agent what it's top unknown preference is. steps +1
def ask_for_preference(agent_to_ask, agents, known_preferences):
	next_top_preference = ['', -1]
	for problem in agents[agent_to_ask]['preferences']:
		if problem in known_preferences[agent_to_ask]:
			continue
		else:
			if agents[agent_to_ask]['preferences'][problem] > next_top_preference[1]:
				next_top_preference = [problem, agents[agent_to_ask]['preferences'][problem]]
	if next_top_preference != ['', -1]:
		known_preferences[agent_to_ask][next_top_preference[0]] = next_top_preference[1]
	return known_preferences

# ask an agent(s) to attempt solving a specific problem. return boolean if they solved it. steps +1
def ask_for_solve(agents_to_ask, problem, agents, top_problems_dict):
	agents_succeeded = 0
	agents_failed = 0
	for agent in agents_to_ask:
		if round(random.random(), 4) < agents[agent]['expertise'][problem]:
			agents_succeeded += 1
		else:
			agents_failed += 1
	if agents_succeeded > agents_failed:
		if problem in top_problems_dict: 
			top_problems_dict[problem]['solved'] = True
		if check_for_win(top_problems_dict) == True:
			return 100
		else:
			return [True, top_problems_dict]
	else:
		return [False, top_problems_dict]

# Win condition
def check_for_win(top_problems_dict):
	for problem in top_problems_dict:
		if top_problems_dict[problem]['solved'] == False:
			return False
	return True

# Compare two lists
def list1_contain_list2(list1, list2):
	differences = 0
	for element2 in list2:
		same_element_present = False
		for element1 in list1:
			if element1 == element2: same_element_present = True
		if same_element_present == False: differences += 1
	contain_percentage = int((len(list2)-differences)/float(len(list2))*100)
	return contain_percentage

# search for top 10 preferred problems
def search_for_top_preferences(number_of_agents, agents, known_preferences, top_problems_dict, 
							   hypothesized_top_problems, steps, top_problem_log):
	preference_search_steps = int(number_of_agents*.5)+1
	ask_preferences_list = paradox_ask_preferences(preference_search_steps, agents, known_preferences, 
												   hypothesized_top_problems, top_problem_log)
	hypothesized_top_problems = ask_preferences_list[0]
	steps += ask_preferences_list[1]
	known_preferences = ask_preferences_list[2]
	top_problem_log = ask_preferences_list[3]
	contain_percentage = list1_contain_list2(hypothesized_top_problems, top_problems_dict)
	if contain_percentage < 100:
		return search_for_top_preferences(preference_search_steps, agents, known_preferences, top_problems_dict, 
										  hypothesized_top_problems, steps, top_problem_log)
	elif contain_percentage == 100:
		return [steps, contain_percentage, hypothesized_top_problems, known_preferences]

def paradox_ask_preferences(number_of_steps, agents, known_preferences, hypothesized_top_problems, 
							top_problem_log):
	steps = 0
	agentid = 1
	# ask preferences
	while steps < number_of_steps:
		known_preferences = ask_for_preference(agentid, agents, known_preferences)
		steps += 1
		if steps > len(agents[1]['preferences'])*100:
			raise RuntimeError('Exceeded maximum steps, doofus! Steps: '+str(steps))
		agentid += 1
		if agentid > len(agents.keys()): agentid -= len(agents.keys())
	# add up known preferences
	for agent in agents:
		n = len(agents[agent]['preferences'].keys())
		while n > 0:
			if 'problem'+str(n) in known_preferences[agent]:
				if 'problem'+str(n) in top_problem_log:
					top_problem_log['problem'+str(n)] += known_preferences[agent]['problem'+str(n)]
				else:
					top_problem_log['problem'+str(n)] = known_preferences[agent]['problem'+str(n)]
			n -= 1
	# take top 10 preferred problems
	top_probs_remaining = 10 + int(.1*len(agents[1]['preferences']))
	while top_probs_remaining > 0:
		if len(top_problem_log.keys()) > 0:
			top_prob = max(top_problem_log, key=top_problem_log.get)
			if top_prob not in hypothesized_top_problems: hypothesized_top_problems.append(top_prob)
			del top_problem_log[top_prob]
			top_probs_remaining -= 1
		else:
			break
	return [hypothesized_top_problems, steps, known_preferences, top_problem_log]

def ask_experts_to_solve(agents, hypothesized_top_problems, steps, top_problems_dict, expertise_cutoff):
	if expertise_cutoff > 1 or expertise_cutoff < 0:
		raise ValueError('Expertise cutoff must be between 0 and 1.')
	experts = {}
	new_steps = steps
	for problem in hypothesized_top_problems:
		experts[problem] = []
		for agent in agents:
			if agents[agent]['expertise'][problem] >= expertise_cutoff:
				experts[problem].append(agent)
	total_problems_solved = 0
	# if expert found, ask them to solve until it's solved. if not, ask the whole group to solve until it's solved.
	for problem in hypothesized_top_problems:
		solved = False
		if len(experts[problem]) > 0:
			while solved == False:
				solve_list = ask_for_solve(experts[problem], problem, agents, top_problems_dict)
				new_steps += 1
				if new_steps > len(agents[1]['preferences'])*100:
					return [-1]
				if solve_list == 100: 
					total_problems_solved += 1
					return [100, new_steps, total_problems_solved]
				solved = solve_list[0]
				top_problems_dict = solve_list[1]
			total_problems_solved += 1
		else:
			while solved == False:
				solve_list = ask_for_solve(agents.keys(), problem, agents, top_problems_dict)
				new_steps += 1
				if new_steps > len(agents[1]['preferences'])*100:
					return [-1]
				if solve_list == 100: 
					total_problems_solved += 1
					return [100, new_steps, total_problems_solved]
				solved = solve_list[0]
				top_problems_dict = solve_list[1]
			total_problems_solved += 1
	return [0, new_steps, total_problems_solved]

def run_trial(solve_function_name, number_of_agents, number_of_problems, number_of_trials):
	steps = []
	steps_total = 0
	problems_solved = []
	problems_solved_total = 0
	fails = 0
	trials = number_of_trials
	while trials > 0:
		data = solve_function_name(number_of_agents, number_of_problems)
		if data[0] == 100:
			steps.append(data[1])
			steps_total += data[1]
			problems_solved.append(data[2])
			problems_solved_total += data[2]
		elif data[0] == -1:
			fails += 1
		trials -= 1
		print str(trials)+' trials left.'
	steps_mean = steps_total/len(steps)
	problems_solved_mean = problems_solved_total/len(problems_solved)
	return [steps, problems_solved, fails, steps_mean, problems_solved_mean]

# RUN
number_of_agents = 100
number_of_problems = 100
number_of_trials = 2000

paradox_data = run_trial(paradox_solve, number_of_agents, number_of_problems, number_of_trials)
technocracy_data = run_trial(technocracy_solve, number_of_agents, number_of_problems, number_of_trials)
steps_range = (40, 160)
bins = 50
problems_range = (10, 100)
plt.rcParams["font.size"] = 12
plt.rcParams["axes.titlesize"] = 20
plt.rcParams["axes.labelsize"] = 16

# Paradox Graphs
# Steps
plt.figure(1, figsize=(9,9))
plt.hist(paradox_data[0], bins, steps_range, color='purple', histtype='bar', rwidth=0.8)
plt.xlabel('Steps')
plt.ylabel('Trials (2000 total)')
plt.title(
	'Two-layered - Steps (mean = '+str(paradox_data[3])+')', 
	y=1.04)
plt.axis([40, 160, 0, int(number_of_trials*.25)])
plt.xticks(np.arange(40, 160, step=20))
plt.axvline(paradox_data[3], color='k', linestyle='dashed', linewidth=1)

# Problems Solved
plt.figure(2, figsize=(9,9))
plt.hist(paradox_data[1], bins, problems_range, color='purple', histtype='bar', rwidth=0.8)
plt.xlabel('Problems Solved')
plt.ylabel('Trials (2000 total)')
plt.title(
	'Two-layered - Total Problems Solved (mean = '+str(paradox_data[4])+')', 
	y=1.04)
plt.axis([10, 100, 0, int(number_of_trials*.25)])
plt.xticks(np.arange(10, 100, step=10))
plt.axvline(paradox_data[4], color='k', linestyle='dashed', linewidth=1)


# Technocracy Graphs
# Steps
plt.figure(3, figsize=(9,9))
plt.hist(technocracy_data[0], bins, steps_range, color='yellow', histtype='bar', rwidth=0.8)
plt.xlabel('Steps')
plt.ylabel('Trials (2000 total)')
plt.title(
	'Experts-only - Steps (mean = '+str(technocracy_data[3])+')',
	y=1.04)
plt.axis([40, 160, 0, int(number_of_trials*.25)])
plt.xticks(np.arange(40, 160, step=20))
plt.axvline(technocracy_data[3], color='k', linestyle='dashed', linewidth=1)

# Problems Solved
plt.figure(4, figsize=(9,9))
plt.hist(technocracy_data[1], bins, problems_range, color='yellow', histtype='bar', rwidth=0.8)
plt.xlabel('Problems Solved')
plt.ylabel('Trials (2000 total)')
plt.title(
	'Experts-only - Total Problems Solved (mean = '+str(technocracy_data[4])+')', 
	y=1.04)
plt.axis([10, 100, 0, int(number_of_trials*.25)])
plt.xticks(np.arange(10, 100, step=10))
plt.axvline(technocracy_data[4], color='k', linestyle='dashed', linewidth=1)

plt.show()

