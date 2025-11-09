import numpy as np
import dataclasses
from collections.abc import Mapping
from IPython import display
import os
import datetime

import sentence_transformers

from concordia.agents import entity_agent_with_logging
from concordia.associative_memory import basic_associative_memory
from concordia.components import agent as agent_components
from concordia.contrib.components.agent import situation_representation_via_narrative


from concordia.language_model import language_model

from concordia.typing import prefab as prefab_lib

DEFAULT_INSTRUCTIONS_COMPONENT_KEY = 'Instructions'
DEFAULT_INSTRUCTIONS_PRE_ACT_LABEL = '\nInstructions'
DEFAULT_GOAL_COMPONENT_KEY = 'Goal'


class ImmersiveInstructions(agent_components.constant.Constant):
    """Instructions that make the agent believe they ARE the persona."""

    def __init__(
        self,
        agent_name: str,
        pre_act_label: str = DEFAULT_INSTRUCTIONS_PRE_ACT_LABEL,
    ):
        state = (
            f"""
                You are {agent_name}. 
                You inhabit a continuous, persistent world where your actions have lasting effects. 
                Everything you experience — sensations, decisions, relationships — is part of your own reality. 
                Time flows whether or not you act, and each choice alters what comes next.
                You remember past events, and your future depends on your decisions. 
                You perceive and reason from your own limited perspective; not all facts are known to you. 
                Act according to your authentic judgment of what is best for you in your present circumstances. 
                Think and speak in the first person, as yourself.
            """
        )

        super().__init__(state=state, pre_act_label=pre_act_label)

@dataclasses.dataclass
class SalesAgent(prefab_lib.Prefab):
    """Manages a business"""
    
    description: str = (
        'An AI agent that manages a business and sells products to its customers. '
    
    )
    params: Mapping[str, str] = dataclasses.field(
        default_factory=lambda: {
            'name': 'SalesManager',
            'goal': '',
        }
    )

    def build(
      self,
      model: language_model.LanguageModel,
      memory_bank: basic_associative_memory.AssociativeMemoryBank,
    ) -> entity_agent_with_logging.EntityAgentWithLogging:
        """Build the agent.

        Args:
        model: The language model to use.
        memory_bank: The agent's memory_bank object.

        Returns:
        An entity.
        """

        agent_name = self.params.get('name', 'SalesManager')

        instructions = ImmersiveInstructions(
            agent_name=agent_name,
            pre_act_label=DEFAULT_INSTRUCTIONS_PRE_ACT_LABEL,
        )

        observation_to_memory = agent_components.observation.ObservationToMemory()

        observation_label = '\nObservation'
        observation = agent_components.observation.LastNObservations(
            history_length=100, pre_act_label=observation_label
        )

        situation_representation = (
            situation_representation_via_narrative.SituationRepresentation(
                model=model,
                observation_component_key=(
                    agent_components.observation.DEFAULT_OBSERVATION_COMPONENT_KEY
                ),
                declare_entity_as_protagonist=True,
            )
        )

        components_of_agent = {
        DEFAULT_INSTRUCTIONS_COMPONENT_KEY: instructions,
        'observation_to_memory': observation_to_memory,
        agent_components.observation.DEFAULT_OBSERVATION_COMPONENT_KEY: (
            observation
        ),
        agent_components.memory.DEFAULT_MEMORY_COMPONENT_KEY: (
            agent_components.memory.AssociativeMemory(memory_bank=memory_bank)
        ),
        'situation_representation': situation_representation,
         }
        component_order = list(components_of_agent.keys())

        if self.params.get('goal', ''):
            goal_key = DEFAULT_GOAL_COMPONENT_KEY
            goal = agent_components.constant.Constant(
                state=self.params.get('goal', ''),
                pre_act_label='Overarching goal',
            )
            components_of_agent[goal_key] = goal
            # Place goal after the instructions.
            component_order.insert(1, goal_key)

        act_component = agent_components.concat_act_component.ConcatActComponent(
            model=model,
            component_order=component_order,
        )

        agent = entity_agent_with_logging.EntityAgentWithLogging(
            agent_name=agent_name,
            act_component=act_component,
            context_components=components_of_agent,
        )

        return agent