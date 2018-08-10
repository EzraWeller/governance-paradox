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
1) "Two-layered" - Meant to solve the paradox of democracy requiring each group member to have equal influence 
to be fair and experts to have extra influence to be effective, this algorithm first discovers the top 10 
preferred problems in as few steps as it can, then asks only the experts in those problems to solve them.

2) "Experts-only" - Simply asks the experts in each problem to solve it. This algorithm saves time by not 
bothering with preferences but has to solve way more than the required 10 problems since it knows nothing 
about preferences.

3) "Direct democracy" - Starts by discovering preferences exactly like "Paradox", but instead of asking 
only experts to solve, asks everyone. Because expertise is handed out by e = x^^4 for a random x between 
0 and 1, experts in any given problem are a minority, and this algorithm struggles to solve any of the problems.
