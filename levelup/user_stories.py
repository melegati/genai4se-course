from metagpt.config2 import Config

from metagpt.roles import Role
from metagpt.actions import Action

import asyncio
from metagpt.environment import Environment
from metagpt.team import Team

gpt4omini = Config.default()

initiate_analysis = Action(name="Initiate analysis", 
                           instruction="Given the provided user story, perform an initial analysis regarding the criteria: independent, negotiable, valuable, estimable, small, and testable.")
enhance_us = Action(name="Enhance user story", 
                    instruction="Based on the analysis provided, improve the given user story.")
confirm_enhacement = Action(name="Confirm the enhacement", 
                            instruction="Check if the new version of the user story is better than the original one regarding the quality criteria.")
# ensure_compliance = 
# review_us = 

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
asyncio.run(team.run(idea="""This is the original user story:
                            User Story Title: As a delivery person, I cannot take over new shipments for a delivery day from the previous day
                            Description: As a delivery person, I cannot take over new shipments for a delivery day from the previous day.
                            Acceptance Criteria:
                            As a delivery person, I receive the message “Shipments cannot be taken over to the registration from dd.mm.yyyy.” on the mobile device.
                            (The delivery person must cleanly end and log off the open delivery day from the previous day [Delivery day.Date < Today])
                            Text message shown (M123)""",
                            send_to="PO",
                            n_round=3))
