# Copyright 2023 DeepMind Technologies Limited.
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

"""Base class for GPT models (OpenAI and Azure)."""

from collections.abc import Collection, Sequence

from concordia.language_model import language_model
from concordia.utils.deprecated import measurements as measurements_lib
from openai import AzureOpenAI
from openai import OpenAI
from typing_extensions import override


_MAX_MULTIPLE_CHOICE_ATTEMPTS = 20
_DEFAULT_VERBOSITY = 'low'


class BaseGPTModel(language_model.LanguageModel):
  """Base class for GPT models (OpenAI and Azure).

  Supports "thinking" models like GPT-5.
  """

  def __init__(
      self,
      model_name: str,
      client: AzureOpenAI | OpenAI,
      measurements: measurements_lib.Measurements | None = None,
      channel: str = language_model.DEFAULT_STATS_CHANNEL,
  ):
    """Initializes the base instance."""
    self._model_name = model_name
    self._measurements = measurements
    self._channel = channel
    self._client = client

    self._verbosity = _DEFAULT_VERBOSITY
    if 'gpt-4o' in self._model_name:
      self._verbosity = 'medium'  # GPT-4o only supports verbosity 'medium'

  def _sample_text(
      self,
      prompt: str,
      reasoning_effort: str,
      verbosity: str,
      *,
      max_tokens: int = language_model.DEFAULT_MAX_TOKENS,
      terminators: Collection[str] = language_model.DEFAULT_TERMINATORS,
      temperature: float = 1.0,  # GPT-5 only supports temperature 1.0
      top_p: float = language_model.DEFAULT_TOP_P,
      timeout: float = language_model.DEFAULT_TIMEOUT_SECONDS,
      seed: int | None = None,
  ) -> str:
    del terminators, top_p  # Unused for OpenAI models.

    messages = [
        {
            'role': 'system',
            'content': (
                'You always continue sentences provided '
                + 'by the user and you never repeat what '
                + 'the user already said.'
            ),
        },
        {
            'role': 'user',
            'content': 'Question: Is Jake a turtle?\nAnswer: Jake is ',
        },
        {'role': 'assistant', 'content': 'not a turtle.'},
        {
            'role': 'user',
            'content': (
                'Question: What is Priya doing right now?\nAnswer: '
                + 'Priya is currently '
            ),
        },
        {'role': 'assistant', 'content': 'sleeping.'},
        {'role': 'user', 'content': prompt},
    ]

    # Claude models don't support reasoning_effort or verbosity
    api_params = {
        'model': self._model_name,
        'messages': messages,
        'temperature': temperature,
        'max_completion_tokens': max_tokens,
        'timeout': timeout,
    }

    # Only add reasoning_effort and verbosity for OpenAI thinking models
    if 'anthropic' not in self._model_name.lower() and 'claude' not in self._model_name.lower():
        api_params['reasoning_effort'] = reasoning_effort
        api_params['verbosity'] = verbosity

    if seed is not None:
        api_params['seed'] = seed

    response = self._client.chat.completions.create(**api_params)

    if self._measurements is not None:
      self._measurements.publish_datum(
          self._channel,
          {'raw_text_length': len(response.choices[0].message.content)},
      )

    return response.choices[0].message.content

  @override
  def sample_text(
      self,
      prompt: str,
      *,
      max_tokens: int = language_model.DEFAULT_MAX_TOKENS,
      terminators: Collection[str] = language_model.DEFAULT_TERMINATORS,
      temperature: float = 1.0,  # GPT-5 only supports temperature 1.0
      top_p: float = language_model.DEFAULT_TOP_P,
      top_k: int = language_model.DEFAULT_TOP_K,
      timeout: float = language_model.DEFAULT_TIMEOUT_SECONDS,
      seed: int | None = None,
  ) -> str:
    del top_k  # Unused
    return self._sample_text(
        prompt=prompt,
        reasoning_effort='minimal',
        verbosity=self._verbosity,
        max_tokens=max_tokens,
        terminators=terminators,
        temperature=temperature,
        top_p=top_p,
        timeout=timeout,
        seed=seed,
    )

  def _sample_choice_direct(
      self,
      prompt: str,
      temperature: float = 1.0,
      seed: int | None = None,
  ) -> str:
    """Sample text for multiple choice without the 'continue sentence' system prompt."""
    # Use a direct system message for choices
    messages = [
        {
            'role': 'system',
            'content': 'You are a helpful assistant that follows instructions precisely. When given a multiple choice question, you respond with exactly one of the provided options.'
        },
        {'role': 'user', 'content': prompt},
    ]

    api_params = {
        'model': self._model_name,
        'messages': messages,
        'temperature': temperature,
        'max_completion_tokens': language_model.DEFAULT_MAX_TOKENS,
        'timeout': language_model.DEFAULT_TIMEOUT_SECONDS,
    }

    # Only add reasoning_effort and verbosity for OpenAI thinking models
    if 'anthropic' not in self._model_name.lower() and 'claude' not in self._model_name.lower():
        api_params['reasoning_effort'] = 'medium'
        api_params['verbosity'] = self._verbosity

    if seed is not None:
        api_params['seed'] = seed

    response = self._client.chat.completions.create(**api_params)
    return response.choices[0].message.content

  @override
  def sample_choice(
      self,
      prompt: str,
      responses: Sequence[str],
      *,
      seed: int | None = None,
  ) -> tuple[int, str, dict[str, float]]:
    prompt = (
        prompt
        + '\n\nYou must select EXACTLY ONE option from the list below.\n'
        + 'Respond with ONLY that option text, nothing else.\n\n'
        + 'Options:\n'
        + '\n'.join(f'- {r}' for r in responses)
        + '\n\nYour response:'
    )

    sample = ''
    answer = ''
    for attempts in range(_MAX_MULTIPLE_CHOICE_ATTEMPTS):
      answer = self._sample_choice_direct(
          prompt,
          temperature=1.0,
          seed=seed,
      )
      sample = answer

      # Try exact match with the full response
      answer_clean = answer.strip().lstrip('-').strip()
      try:
        idx = responses.index(answer_clean)
        if self._measurements is not None:
          self._measurements.publish_datum(
              self._channel, {'choices_calls': attempts}
          )
        debug = {}
        return idx, responses[idx], debug
      except ValueError:
        pass

    raise language_model.InvalidResponseError((
        f'Too many multiple choice attempts.\nLast attempt: {sample}, '
        + f'extracted: {answer}'
    ))
