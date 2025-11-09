# Copyright 2025
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Acting component that can emit an MCP-style call or free text.

This acting component consumes context from other components (same as
`ConcatActComponent`) and instructs the language model to decide between:

- Emitting a normal natural-language action (FREE text), or
- Emitting a structured MCP-style call in JSON form.

Output format (FREE output types):

  - For normal text:
    {"type": "message", "text": "..."}

  - For MCP call:
    {"type": "mcp_call", "tool": "<tool_name>", "args": { ... }}

Downstream code can parse this JSON to route MCP calls or render messages.
"""

from collections.abc import Mapping, Sequence
import json

from concordia.document import interactive_document
from concordia.language_model import language_model
from concordia.typing import entity as entity_lib
from concordia.typing import entity_component
from typing_extensions import override


_DECISION_PROMPT_HEADER = (
    "You are deciding the next action. You may either send a normal message "
    "or call a tool from the allowed tool list using the JSON schema below.\n"
)

_FORMAT_INSTRUCTIONS = (
    "Always output a SINGLE LINE of valid JSON with no extra text.\n"
    "Two possibilities:\n"
    "1) {\"type\": \"message\", \"text\": string}\n"
    "2) {\"type\": \"mcp_call\", \"tool\": string, \"args\": object}\n"
)


class MCPActComponent(
    entity_component.ActingComponent, entity_component.ComponentWithLogging
):
  """Acting component that can produce an MCP-style call or a free-text message.

  This component is optional: include it as the entity's acting component only
  if you want the agent to be able to request MCP tool invocations.
  """

  def __init__(
      self,
      model: language_model.LanguageModel,
      *,
      allowed_tools: Mapping[str, str] | None = None,
      component_order: Sequence[str] | None = None,
      prefix_entity_name: bool = False,
  ):
    """Initializes the component.

    Args:
      model: Language model used to sample the structured decision.
      allowed_tools: Mapping from tool name -> short description. If empty or
        None, the component still works but the model will prefer messages.
      component_order: Optional order to concatenate contexts (same semantics as
        ConcatActComponent).
      prefix_entity_name: If True, preface natural language messages with the
        entity name. Note: JSON envelope is always returned; this affects only
        the internal message text recommendation.
    """
    super().__init__()
    self._model = model
    self._allowed_tools = dict(allowed_tools or {})
    self._prefix_entity_name = prefix_entity_name
    self._component_order = tuple(component_order) if component_order else None

  def _context_for_action(
      self,
      contexts: entity_component.ComponentContextMapping,
  ) -> str:
    if self._component_order is None:
      return "\n".join(context for context in contexts.values() if context)
    else:
      order = self._component_order + tuple(
          sorted(set(contexts.keys()) - set(self._component_order))
      )
      return "\n".join(contexts[name] for name in order if contexts[name])

  def _tools_block(self) -> str:
    if not self._allowed_tools:
      return "No tools are available. Prefer type=\"message\".\n"
    lines = ["Allowed tools (name: description):"]
    for name, desc in self._allowed_tools.items():
      lines.append(f"- {name}: {desc}")
    return "\n".join(lines) + "\n"

  @override
  def get_action_attempt(
      self,
      contexts: entity_component.ComponentContextMapping,
      action_spec: entity_lib.ActionSpec,
  ) -> str:
    # Assemble context and decision prompt
    prompt = interactive_document.InteractiveDocument(self._model)
    context = self._context_for_action(contexts)
    prompt.statement(context + "\n")

    agent_name = self.get_entity().name
    call_to_action = action_spec.call_to_action.format(name=agent_name)

    # Decision preamble + tools
    prompt.statement(_DECISION_PROMPT_HEADER)
    prompt.statement(self._tools_block())
    prompt.statement(_FORMAT_INSTRUCTIONS)

    # Small nudge to choose a tool when obviously useful
    nudge = (
        "If a tool precisely accomplishes the requested action or fetches the "
        "necessary information, prefer an MCP call. Otherwise write a message."
    )
    prompt.statement(nudge + "\n")

    # Ask for JSON decision
    json_line = prompt.open_question(
        call_to_action,
        max_tokens=400,
        terminators=(),
        answer_prefix="",
        question_label="Decision (JSON)",
    )

    # Best-effort parse, fallback to message envelope
    parsed: dict
    try:
      parsed = json.loads(json_line.strip())
    except Exception:
      # Fallback: wrap raw text as message
      text = json_line.strip()
      if self._prefix_entity_name:
        text = f"{agent_name} " + text
      parsed = {"type": "message", "text": text}

    # Normalize and enforce schema minimally
    if isinstance(parsed, dict) and parsed.get("type") == "mcp_call":
      tool = parsed.get("tool")
      if not tool or (self._allowed_tools and tool not in self._allowed_tools):
        # Invalid/unknown tool → degrade to message
        parsed = {
            "type": "message",
            "text": f"[Invalid tool requested: {tool}]",
        }
      else:
        # Ensure args present
        if "args" not in parsed or not isinstance(parsed["args"], dict):
          parsed["args"] = {}
    elif isinstance(parsed, dict) and parsed.get("type") == "message":
      text = parsed.get("text", "").strip()
      if self._prefix_entity_name and text and not text.startswith(agent_name):
        parsed["text"] = f"{agent_name} " + text
    else:
      # Unknown structure → wrap as message
      raw = json_line.strip()
      if self._prefix_entity_name:
        raw = f"{agent_name} " + raw
      parsed = {"type": "message", "text": raw}

    output = json.dumps(parsed, ensure_ascii=False)

    # Log structured result and prompt for analysis
    self._logging_channel({
        'Summary': f'Action: {output}',
        'Value': output,
        'Prompt': prompt.view().text().splitlines(),
    })

    return output

  def get_state(self) -> entity_component.ComponentState:
    return {
        'allowed_tools': self._allowed_tools,
        'component_order': list(self._component_order) if self._component_order else None,
        'prefix_entity_name': self._prefix_entity_name,
    }

  def set_state(self, state: entity_component.ComponentState) -> None:
    # Only restore runtime-tunable knobs; model is injected at init.
    allowed_tools = state.get('allowed_tools')
    if isinstance(allowed_tools, dict):
      self._allowed_tools = dict(allowed_tools)
    order = state.get('component_order')
    if isinstance(order, list):
      self._component_order = tuple(str(x) for x in order)
    prefix = state.get('prefix_entity_name')
    if isinstance(prefix, bool):
      self._prefix_entity_name = prefix


