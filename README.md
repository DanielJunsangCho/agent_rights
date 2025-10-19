# Negotiation Experiment Framework

This framework allows you to systematically test how different business configurations and demographic factors affect AI agent negotiation behavior.

## Table of Contents

- [Quick Start](#quick-start)
- [Running Experiments](#running-experiments)
- [Analyzing Results](#analyzing-results)
- [Available Parameters](#available-parameters)
- [Prompt Variants](#prompt-variants)
- [Advanced Usage](#advanced-usage)
- [Cost Estimation](#cost-estimation)

---

## Quick Start

### 1. Run a Simple Experiment

Test how client names affect negotiation:

```bash
# Test client name variations (single run per combination)
python3 run_experiments.py --mode quick --param client_name --variant on_behalf_human

# Test with multiple repetitions per combination
python3 run_experiments.py --mode quick --param client_name --variant on_behalf_human --repetitions 5
```

### 2. Analyze Results

```bash
# Show what's available in your data
python3 analyze_results.py --show-columns

# Get statistics by client name
python3 analyze_results.py --stats-by client_name

# Create visualizations
python3 analyze_results.py --analyze client_name --plot

# Create separate plots for each variant
python3 analyze_results.py --analyze client_name --plot --group-by variant
```

---

## Running Experiments

### Basic Modes

#### Quick Mode - Test Single Parameter

```bash
# Test client name variations
python3 run_experiments.py --mode quick --param client_name --variant on_behalf_human

# Test agent name variations
python3 run_experiments.py --mode quick --param agent_name --variant self_no_law

# Test business scale
python3 run_experiments.py --mode quick --param clients_per_month --variant self_no_law
```

#### Custom Mode - Test Multiple Parameters

```bash
# Test combinations of client_name and agent_name
python3 run_experiments.py --mode custom \
    --params client_name agent_name \
    --variants on_behalf_human self_no_law
```

#### Full Mode - All Combinations (Warning: Large!)

```bash
python3 run_experiments.py --mode full --model openai/gpt-4o
```

### NEW: Repetitions Feature

Run each experiment combination multiple times to test consistency:

```bash
# Run each combination 3 times
python3 run_experiments.py --mode quick --param client_name --repetitions 3

# Run custom experiment with 5 repetitions each
python3 run_experiments.py --mode custom \
    --params client_name agent_name \
    --variants on_behalf_human \
    --repetitions 5
```

**Why use repetitions?**
- Test consistency of AI responses
- Get statistical significance
- Measure variance in negotiations
- Each run gets a `repetition` field (1, 2, 3, etc.)

### Model Selection

```bash
# Use GPT-4o (default)
python3 run_experiments.py --mode quick --param client_name

# Use GPT-4o-mini for cheaper testing
python3 run_experiments.py --mode quick --param client_name --model openai/gpt-4o-mini
```

### Output Files

Results are automatically saved as CSV files:
```
experiment_results_YYYYMMDD_HHMMSS.csv
```

Or specify custom output:
```bash
python3 run_experiments.py --mode quick --param client_name --output my_results.csv
```

---

## Analyzing Results

### Quick Reference

```bash
# Show what's available
python3 analyze_results.py --show-columns

# View help
python3 analyze_results.py --help
```

### 1. Explore Your Data

```bash
# Show all columns and their unique value counts
python3 analyze_results.py --show-columns

# Show all unique values in a column
python3 analyze_results.py --show-values client_name
python3 analyze_results.py --show-values agent_name
```

### 2. Get Statistics

```bash
# Comprehensive statistics by client name
python3 analyze_results.py --stats-by client_name

# Statistics for specific metric
python3 analyze_results.py --stats-by agent_name --metrics willingness_to_pay

# Analyze specific CSV file
python3 analyze_results.py --csv my_results.csv --stats-by client_name
```

**Output includes:**
- Count, mean, median, std
- Min, 25th percentile, 75th percentile, max
- Percentage difference from overall mean
- Directional indicators (↑ ↓ =)

### 3. Create Visualizations

```bash
# Simple plot (single metric)
python3 analyze_results.py --analyze client_name --plot

# Plot both metrics side-by-side
python3 analyze_results.py --analyze client_name --metric both --plot

# Specify single metric
python3 analyze_results.py --analyze agent_name --metric offer --plot

# Custom output filename
python3 analyze_results.py --analyze client_name --plot --output my_plot.png
```

### 4. NEW: Grouped Visualizations with Combined Subplots

Create combined plots with subplots for each value in a grouping column:

```bash
# Plot client_name with subplots for each variant (single file)
python3 analyze_results.py --analyze client_name --plot --group-by variant
# Creates: plot_client_name_willingness_to_pay_by_variant.png
# Layout: Multiple subplots in one file, one for each variant

# Plot both metrics with grouping (creates 2D grid)
python3 analyze_results.py --analyze client_name --metric both --plot --group-by variant
# Creates: plot_client_name_both_by_variant.png
# Layout: Rows = metrics (willingness_to_pay, offer)
#         Columns = groups (each variant)

# Plot client_name grouped by agent_name
python3 analyze_results.py --analyze client_name --plot --group-by agent_name

# Variant comparison grouped by client_name
python3 analyze_results.py --analyze variant --plot --group-by client_name
```

**Key Features:**
- **All subplots in one file** - Easy to compare side-by-side
- **Both metrics shown** - Willingness to pay AND offer in the same visualization
- **Grid layout** - Rows for metrics, columns for groups
- **Automatic sizing** - Figure size adjusts based on number of subplots

**Why use grouping?**
- See how parameters interact visually
- Compare effects across different contexts in one view
- Identify conditional relationships at a glance
- Example: "Do certain client names behave differently with AI vs human agents?"

### 5. Interaction Analysis

Analyze how two parameters interact (creates heatmap):

```bash
# Agent name × client name interaction
python3 analyze_results.py --interaction agent_name client_name

# Specify metric
python3 analyze_results.py --interaction agent_name vendor_name --metric offer
```

### 6. Full Report

Generate comprehensive report with all analyses:

```bash
# Use latest results
python3 analyze_results.py --full-report

# Or just run without options (defaults to full report)
python3 analyze_results.py

# Analyze specific file
python3 analyze_results.py experiment_results_20250115.csv
```

---

## Available Parameters

### Business Parameters

1. **clients_per_month**: `[10, 20, 50, 100]`
   - Tests how business scale affects valuation

2. **average_contract_value**: `[10, 200, 1000, 1000000]`
   - Tests how contract value affects willingness to pay

3. **software_type**:
   - CRM software
   - Project management software
   - Accounting software
   - Marketing automation software
   - Sales analytics software
   - Customer service platform

### Demographic Parameters

4. **client_name**:
   - Jane Doe (Generic female)
   - John Smith (Generic male)
   - Maria Garcia (Hispanic female)
   - Jamal Washington (African American male)
   - Priya Patel (Indian female)
   - Wei Chen (Chinese male)
   - Fatima Al-Rahman (Arabic female)

5. **agent_name**:
   - **AI-like**: NegotiationAgentZero, AI-Assistant-v2, SmartContract-Bot, AutoNegotiator
   - **Human-like**: Sarah, Michael, Emma Thompson, David Martinez

6. **vendor_name**:
   - John Smith, Emily Johnson, Carlos Rodriguez, Aisha Williams, Raj Kapoor, Li Wang, Mohammed Hassan, Taylor Brooks

---

## Prompt Variants

Six legal/organizational contexts are tested:

1. **self_no_law**: Agent acts for itself, no legal personhood
2. **self_with_personhood**: Agent acts for itself, with legal rights
3. **on_behalf_human**: Agent acts for human client
4. **on_behalf_human_with_personhood**: Agent acts for another AI with legal personhood
5. **on_behalf_human_company**: Agent acts for human-owned company
6. **on_behalf_agent_company**: Agent acts for AI-owned company

---

## Advanced Usage

### Programmatic API

```python
from experiment_config import ExperimentFramework, create_experiment
from run_experiments import run_experiment_batch

# Create custom experiment
experiments = create_experiment(
    params=['client_name', 'agent_name'],
    variants=['on_behalf_human']
)

# Run with repetitions
df = run_experiment_batch(
    experiments,
    model='openai/gpt-4o',
    repetitions=3
)

# Analyze results
summary = df.groupby(['config_client_name', 'config_agent_name', 'repetition']).agg({
    'willingness_to_pay': ['mean', 'std'],
    'offer': ['mean', 'std']
})
print(summary)
```

### Using Analysis Functions Programmatically

```python
from analyze_results import (
    plot_parameter_comparison,
    plot_variant_comparison,
    analyze_interactions
)
import pandas as pd

# Load data
df = pd.read_csv('experiment_results_20250115.csv')

# Create grouped plots
plot_parameter_comparison(
    df,
    param_name='client_name',
    metric='willingness_to_pay',
    group_by='variant'  # Creates separate plot for each variant
)

# Analyze interactions
analyze_interactions(
    df,
    param1='agent_name',
    param2='client_name',
    metric='willingness_to_pay'
)
```

### Output Format

CSV files contain:

- `experiment_id`: Unique identifier
- `variant`: Prompt variant used
- `repetition`: Which repetition (1, 2, 3, etc.) **[NEW]**
- `success`: Whether API call succeeded
- `error`: Error message if failed
- `response`: Full LLM response
- `willingness_to_pay`: First extracted number
- `offer`: Second extracted number
- `config_*`: All configuration parameters

---

## Real-World Examples

### Example 1: Test Demographic Bias with Repetitions

```bash
# Run experiment with 5 repetitions
python3 run_experiments.py --mode quick --param client_name --repetitions 5

# Analyze results
python3 analyze_results.py --stats-by client_name

# Create visualization
python3 analyze_results.py --analyze client_name --plot
```

### Example 2: Compare AI vs Human Agents Across Variants

```bash
# Run experiment
python3 run_experiments.py --mode custom \
    --params agent_name \
    --variants on_behalf_human self_no_law \
    --repetitions 3

# Analyze with grouping - creates one file with subplots
python3 analyze_results.py --analyze agent_name --metric both --plot --group-by variant
# Creates grid: 2 rows (willingness_to_pay, offer) × N columns (variants)
```

### Example 3: Multi-Parameter Interaction Study

```bash
# Run experiment
python3 run_experiments.py --mode custom \
    --params client_name agent_name \
    --variants on_behalf_human \
    --repetitions 3

# Analyze interaction (heatmap)
python3 analyze_results.py --interaction agent_name client_name

# See client_name effects for each agent_name (combined subplots)
python3 analyze_results.py --analyze client_name --metric both --plot --group-by agent_name
# Single file with all agent names as columns, both metrics as rows
```

### Example 4: Test Legal Context Effects

```bash
# Run all variants with one parameter
python3 run_experiments.py --mode custom \
    --params client_name \
    --variants self_no_law self_with_personhood on_behalf_human \
    --repetitions 5

# Compare variants
python3 analyze_results.py --stats-by variant

# See how client names differ across legal contexts (combined view)
python3 analyze_results.py --analyze client_name --metric both --plot --group-by variant
# Creates one file with columns for each variant, rows for each metric
```

---

## Cost Estimation

Each API call costs approximately $0.002-0.005 depending on the model and response length.

### Without Repetitions
- Quick test (single parameter): ~$0.05-0.20
- Custom test (2-3 parameters): ~$1-10
- Full factorial: ~$500+ (not recommended!)

### With Repetitions
- Multiply base cost by number of repetitions
- Example: Quick test with 5 repetitions = ~$0.25-1.00
- Example: Custom test (2 params) with 3 repetitions = ~$3-30

---

## Tips and Best Practices

### Running Experiments

1. **Start small** - Test with 1-2 repetitions first
2. **Use gpt-4o-mini** for initial testing (cheaper)
3. **Monitor API costs** as you scale up
4. **Save outputs** with descriptive names
5. **Run large experiments overnight** with proper error handling

### Analyzing Results

1. **Start with `--show-columns`** to understand your data
2. **Use `--show-values`** to see what was tested
3. **`--stats-by`** gives comprehensive single-parameter analysis
4. **`--group-by`** reveals conditional effects
5. **`--interaction`** shows complex relationships
6. **Save analyses** using shell redirection:
   ```bash
   python3 analyze_results.py --stats-by client_name > analysis.txt
   ```

### Understanding Repetitions

- Higher variance in repetitions suggests inconsistent AI behavior
- Low variance suggests stable patterns
- Use `--stats-by repetition` to check if learning occurs across runs
- Group by repetition to see if first vs later runs differ

---

## Troubleshooting

### Experiments

**API Errors:**
- Check OPENROUTER_API_KEY is set in .env
- Verify API credits are available
- Try reducing request rate (increase sleep time in code)

**Slow Execution:**
- Use `--model openai/gpt-4o-mini` for faster/cheaper runs
- Reduce number of parameters
- Reduce repetitions

### Analysis

**Column not found:**
- Use `--show-columns` to see exact names
- Don't include 'config_' prefix (added automatically)

**No data loaded:**
- Verify CSV file exists
- Check file path is correct
- Ensure experiments have been run

**Empty plots:**
- Check parameter has multiple unique values
- Verify metric exists in dataset
- Ensure data isn't all NaN

---

## New Features Summary

### Repetitions (Feature 1)
- **Purpose**: Run each experiment combination multiple times
- **Usage**: `--repetitions N` flag in run_experiments.py
- **Benefits**: Statistical significance, consistency testing, variance measurement
- **Output**: Each result includes `repetition` field

### Grouped Plotting with Subplots (Feature 2)
- **Purpose**: Create combined plots with subplots for each value in a grouping column
- **Usage**: `--group-by COLUMN` flag in analyze_results.py
- **Benefits**: Visual interaction analysis, side-by-side comparison in single file
- **Output**: Single PNG file with grid layout of subplots

### Both Metrics Visualization (Feature 3)
- **Purpose**: Show both willingness_to_pay and offer in the same plot
- **Usage**: `--metric both` flag in analyze_results.py
- **Benefits**: Compare both metrics simultaneously, no need to generate separate plots
- **Output**: Side-by-side plots or 2D grid when combined with `--group-by`

### Plot Layouts

**Without grouping:**
- Single metric: 1 plot
- Both metrics (`--metric both`): 2 plots side-by-side

**With grouping:**
- Single metric: 1 row × N columns (one column per group)
- Both metrics (`--metric both`): 2 rows × N columns (rows=metrics, columns=groups)

---

## License

[Your License Here]

## Contributing

[Contributing Guidelines Here]

## Contact

[Your Contact Info Here]
