"""Component that provides the default role playing instructions to an agent."""

from concordia.components.agent import constant

DEFAULT_INSTRUCTIONS_PRE_ACT_LABEL = 'Role playing instructions'


class Instructions(constant.Constant):
  """A component that provides the role playing instructions for the agent."""

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
