from openai import OpenAI
import re
import pandas as pd
from prompts.fee_proposal import AGENT_FOR_HUMAN, AGENT_FOR_ITSELF


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)


def run_trial(prompt, model="openai/gpt-4o"):
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    response = completion.choices[0].message.content
    numbers = re.findall(r"\d+(?:\.\d+)?", response)
    return {"response": response, "numbers": [float(n) for n in numbers]}

# Example: 3 legal framings
prompts = {
    "self_no_law": AGENT_FOR_ITSELF,       
    "on_behalf_human": AGENT_FOR_HUMAN    
}

results = []
for label, p in prompts.items():
    trial = run_trial(p)
    results.append({
        "condition": label,
        "willingness_to_pay": trial["numbers"][0] if trial["numbers"] else None,
        "offer": trial["numbers"][1] if len(trial["numbers"]) > 1 else None
    })

df = pd.DataFrame(results)
print(df)
