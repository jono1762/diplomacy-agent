# CITS3011 Intelligent Agents Project

## Description
This repository contains the relevant code files that I submitted as part of my CITS3011 (Intelligent Agents) project. I was tasked with developing an AI agent which plays the multiplayer strategy game, Diplomacy. Specifically, the version of the game using the standard map where the time begins in 1901 and ends in 1920. I developed the agent from scratch but was provided additional files for simulating the game, baseline agents and statistically reporting back its performance.

The contents of the code files can be sumarised as follows:
- `agent_24314826.py`: contains the code that powers the agent, using breadth-first search, heuristics and game specific strategies to optimise performance. More details can be found in a PDF report that I also included in my submission, where I describe the techniques implemented into the agent. You can access it by going to my [LinkedIn](https://www.linkedin.com/in/jonathan-abraham-dev/) and clicking the document attached to my description of this project in the `Projects` section.
- `agent_baselines.py`: contains the code for various baseline agents that my agent competes against in simulations which can be described as follows:
  - Static Agent: This is an agent that always takes the default actions, i.e., hold.
  - Random Agent: This is an agent that always takes random actions.
  - Attitude Agent: This is an agent that takes random actions, but has attitudes towards other powers, including being friendly, neutral, or hostile. The attitude depends on other players' actions and can change during the game. A friendly agent will never attack you, a hostile one will never support you, and a neutral one can do anything.
  - Greedy Agent: This is an agent that always takes greedy actions, without long-term planning. Each unit controlled by the agent will move towards and attack the closest supply centre, or support other units if having the same target.
- `game.py`: contains the code to simulate a single game.
- `requirements.txt`: contains the necessary libraries to run the code in this repository.
- `test.py`: contains the code to simulate the game where my agent is each power `n` times while enemy agents are randomly selected from the pool of agents described above. There are three parameters you can control to modify testing behaviour:
  - `player_agent`: which agent is having its performance analysed and reported back.
  - `opponent_agent_pool`: which agents can the enemy powers potentially get.
  - `repeat_nums`: how many times does the player agent represent each power.

## Introduction to Diplomacy

Diplomacy is a strategic board game with seven players competing and cooperating to capture supply centres on a map of Europe. This game is very challenging for AI due to the large action space and state space. 

The following link contains the main rules of Diplomacy.

- [Game Rules](https://en.wikibooks.org/wiki/Diplomacy/Rules)

You can also try playing the game yourself on the online platform below:

- [Online Playing](https://webdiplomacy.net/)


## How to Simulate Games with the Agent

Download this repository and open it in a text editor or navigate to it on your command line.

1. Create a virtual environment using `conda` or `venv` (optional but highly recommended).

2. Install the game engine and other required packages using the provided `requirements.txt`:
```
pip3 install -r requirements.txt
```

3. Running a test will by default run a large number of games and report the performance of the agent:
```
python3 test.py
```
