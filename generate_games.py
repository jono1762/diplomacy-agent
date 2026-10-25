import os
import sys
import json
import random
from diplomacy import Game
from diplomacy.engine.map import Map
from game import run_one_game
from test import ALL_POWERS, scoring
from agent_baselines import StaticAgent, RandomAgent, GreedyAgent, AttitudeAgent
from agent_24314826 import StudentAgent

# Simulates one game per power per scenario and saves them for the replay site in site/.
# Re-running with the same SEED reproduces the same games.

# Chosen from seeds 3000-3039 so the mixed games are representative of the 350-game evaluation in the
# README (3/7 wins, 0 defeats, 12.6 avg SCs vs 45% wins, 3% defeats, 12.1 avg SCs)
SEED = 3025
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site', 'games')

SCENARIOS = {
    'static': {
        'title': 'vs Static agents',
        'pool': [StaticAgent],
    },
    'mixed': {
        'title': 'vs Random, Attitude and Greedy agents',
        'pool': [RandomAgent, AttitudeAgent, AttitudeAgent, GreedyAgent, GreedyAgent],
    },
}

def agent_label(agent):
    return 'Student' if isinstance(agent, StudentAgent) else type(agent).__name__.replace('Agent', '')

def export_map(map_name):
    # Same shape as the server's available_maps, which the web viewer needs to draw orders
    game_map = Map(map_name)
    return {
        'powers': sorted(game_map.powers),
        'supply_centers': list(game_map.scs),
        'loc_type': game_map.loc_type.copy(),
        'loc_abut': game_map.loc_abut.copy(),
        'aliases': game_map.aliases.copy(),
    }

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    index = []

    for s, (scenario, config) in enumerate(SCENARIOS.items()):
        for i, player in enumerate(ALL_POWERS):
            random.seed(SEED + 100 * s + i)
            agents_dict = {}
            for p in ALL_POWERS:
                agents_dict[p] = StudentAgent() if p == player else random.choice(config['pool'])()

            game_id = f'{scenario}-{player.lower()}'
            save_file = os.path.join(OUTPUT_DIR, f'{game_id}.json')
            if os.path.exists(save_file):
                os.remove(save_file) # run_one_game appends to existing files

            results, year = run_one_game(agents_dict, game=Game(game_id=game_id), save_file=save_file)
            scores, wins = scoring(results)

            index.append({
                'id': game_id,
                'file': f'{game_id}.json',
                'scenario': scenario,
                'scenario_title': config['title'],
                'power': player,
                'agents': {p: agent_label(a) for p, a in agents_dict.items()},
                'centres': results,
                'end_year': int(year),
                'outcome': wins[player],
            })
            print(f'{game_id}: {wins[player]} with {scores[player]} SCs (ended {year})')

    with open(os.path.join(OUTPUT_DIR, 'index.json'), 'w') as f:
        json.dump({'seed': SEED, 'games': index}, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, 'maps.json'), 'w') as f:
        json.dump({'standard': export_map('standard')}, f)

if __name__ == '__main__':
    # Baseline agents iterate over sets of strings, so fix hashing as well as random for reproducible games
    if os.environ.get('PYTHONHASHSEED') != '0':
        os.environ['PYTHONHASHSEED'] = '0'
        os.execv(sys.executable, [sys.executable] + sys.argv)
    main()
