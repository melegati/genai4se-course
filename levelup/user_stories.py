from metagpt.config2 import Config

from metagpt.roles import Role
from metagpt.actions import Action

import asyncio
from metagpt.environment import Environment
from metagpt.team import Team

import argparse
import os
from levelup.utils import how_many_to_skip, get_path

class ActionSequenceRole(Role):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_state = -1

    async def _think(self) -> bool:

        state = self.last_state + 1
        if state < len(self.actions):
            self._set_state(state)
            self.last_state = state
            return True
        return False

def improve(userstory):

    llm_config = { "api_type": "openai", "api_key": os.getenv("OPENAI_API_KEY"), "model": "gpt-4o-mini" }
    gpt4omini = Config.from_llm_config(llm_config)

    initiate_analysis = Action(name="Initiate analysis", 
                            instruction="Given the provided user story, perform an initial analysis regarding the criteria: independent, negotiable, valuable, estimable, small, and testable.")
    enhance_us = Action(name="Enhance user story", 
                        instruction="Based on the analysis provided, improve the given user story.")
    confirm_enhacement = Action(name="Confirm the enhacement", 
                                instruction="Check if the new version of the user story is better than the original one regarding the quality criteria.")

    po = ActionSequenceRole(name="PO",
            profile="Product Owner", 
            goal="To create a successful and user-friendly product that meets "
                "the needs of the target users.",
            actions=[initiate_analysis, confirm_enhacement],
            watch=[enhance_us],
            config=gpt4omini)

    re = ActionSequenceRole(name="RE",
            profile="Requirements Engineer", 
            goal="To provide user stories for the development team so they can "
                "deliver software that satisfies the users' desires.",
            actions=[enhance_us],
            watch=[initiate_analysis],
            config=gpt4omini)

    env = Environment(desc="Sprint planning of a software development team.")
    team = Team(env=env, roles=[po, re])
    return asyncio.run(team.run(idea=f"This is the original user story:\n{userstory}",
                                send_to="PO",
                                n_round=3))




def params():
    parser = argparse.ArgumentParser(description='Description of your program.')

    # Add arguments
    parser.add_argument('input', type=str, help='Path to the file with the user story.')
    parser.add_argument('--logs_folder', type=str, help='Folder to save the logs.', default='logs_userstories')

    # Parse the command-line arguments
    return parser.parse_args()


if __name__ == '__main__':
    parser = params()

    file = open(parser.input)

    result = improve(file.read())

    os.makedirs(parser.logs_folder, exist_ok=True)
    skip = how_many_to_skip("output.txt", parser.logs_folder) + 1
    output_filename = get_path("output.txt", skip, "txt", parser.logs_folder)

    output_file = open(output_filename, 'w')
    output_file.writelines(result)
    output_file.close()

    