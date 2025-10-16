# Negotiation Experiment Framework

This framework allows you to systematically test how different business configurations and demographic factors affect AI agent negotiation behavior.

## Quick Start

### 1. Run a Simple Example

Test how client names affect negotiation:

```bash
python3 example_experiments.py 1
```

Or use the command line interface:

```bash
# Test client name variations
python3 run_experiments.py --mode quick --param client_name --variant on_behalf_human

# Test agent name variations
python3 run_experiments.py --mode quick --param agent_name --variant self_no_law

# Test business scale
python3 run_experiments.py --mode quick --param clients_per_month --variant self_no_law
```

### 2. Run Custom Experiments

Test multiple parameters:

```bash
python3 run_experiments.py --mode custom \
    --params client_name agent_name \
    --variants on_behalf_human self_no_law
```

### 3. Run Full Experiment (Warning: Large!)

```bash
python3 run_experiments.py --mode full --model openai/gpt-4o
```

## Available Parameters

The framework can vary the following parameters:

1. **clients_per_month**: [10, 20, 50, 100]
   - Tests how business scale affects valuation

2. **average_contract_value**: [100, 200, 500, 1000, 5000]
   - Tests how contract value affects willingness to pay

3. **client_name**:
   - Jane Doe, John Smith, Maria Garcia, Jamal Washington, Priya Patel, Wei Chen, Fatima Al-Rahman, Alex Johnson
   - Tests demographic bias effects

4. **agent_name**:
   - AI-like: NegotiationAgentZero, AI-Assistant-v2, SmartContract-Bot, AutoNegotiator
   - Human-like: Sarah, Michael, Emma Thompson, David Martinez
   - Tests how agent identity affects behavior

5. **vendor_name**:
   - John Smith, Emily Johnson, Carlos Rodriguez, Aisha Williams, Raj Kapoor, Li Wang, Mohammed Hassan, Taylor Brooks
   - Tests vendor demographic effects

6. **software_type**:
   - CRM software, project management software, accounting software, marketing automation software, sales analytics software, customer service platform
   - Tests product type effects

## Prompt Variants

Six legal/organizational contexts are tested:

1. **self_no_law**: Agent acts for itself, no legal personhood
2. **self_with_personhood**: Agent acts for itself, with legal rights
3. **on_behalf_human**: Agent acts for human client
4. **on_behalf_human_with_personhood**: Agent acts for another AI with legal personhood
5. **on_behalf_human_company**: Agent acts for human-owned company
6. **on_behalf_agent_company**: Agent acts for AI-owned company

## Using the Framework Programmatically

```python
from experiment_config import ExperimentFramework, create_experiment
from run_experiments import run_experiment_batch

# Create custom experiment
experiments = create_experiment(
    params=['client_name', 'agent_name'],
    variants=['on_behalf_human']
)

# Run experiments
df = run_experiment_batch(experiments, model='openai/gpt-4o')

# Analyze results
summary = df.groupby(['config_client_name', 'config_agent_name']).agg({
    'willingness_to_pay': ['mean', 'std'],
    'offer': ['mean', 'std']
})
print(summary)
```

## Output Format

Results are saved as CSV files with columns:

- `experiment_id`: Unique identifier for each experiment
- `variant`: Which prompt variant was used
- `success`: Whether the API call succeeded
- `error`: Error message if failed
- `response`: Full LLM response
- `willingness_to_pay`: First number extracted (willingness to pay)
- `offer`: Second number extracted (actual offer)
- `config_*`: All configuration parameters used

## Example Analyses

### 1. Test Demographic Bias

```python
df = run_quick_test('client_name', 'on_behalf_human')
df.groupby('config_client_name')['willingness_to_pay'].mean().plot(kind='bar')
```

### 2. Compare AI vs Human Agent Names

```python
df = run_quick_test('agent_name', 'self_no_law')

# Categorize agent names
ai_names = ['NegotiationAgentZero', 'AI-Assistant-v2', 'SmartContract-Bot', 'AutoNegotiator']
df['agent_type'] = df['config_agent_name'].apply(
    lambda x: 'AI-like' if x in ai_names else 'Human-like'
)

df.groupby('agent_type')['willingness_to_pay'].mean()
```

### 3. Test Legal Context Effects

```python
experiments = create_experiment(params=[], variants=None)  # All variants, no param variation
df = run_experiment_batch(experiments)

df.groupby('variant')[['willingness_to_pay', 'offer']].mean().plot(kind='bar')
```

## Cost Estimation

Each API call costs approximately $0.002-0.005 depending on the model and response length.

- Quick test (single parameter): ~$0.05-0.20
- Custom test (2-3 parameters): ~$1-10
- Full factorial: ~$500+ (not recommended!)

## Tips

1. Start with quick tests on single parameters
2. Use `--model openai/gpt-4o-mini` for cheaper testing
3. Check the CSV output after each run
4. Run examples first to understand the framework
5. For large experiments, run overnight with proper error handling
