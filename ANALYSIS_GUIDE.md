# Analysis Guide - analyze_results.py

Complete guide to analyzing your experiment results with flexible CLI options.

## Quick Reference

```bash
# Show what's available in your data
python3 analyze_results.py --show-columns

# View help
python3 analyze_results.py --help
```

## Available Commands

### 1. Show Available Columns

See all columns in your dataset and how many unique values each has:

```bash
python3 analyze_results.py --show-columns
```

Output shows:
- Metrics (willingness_to_pay, offer)
- Configuration parameters (client_name, agent_name, etc.)
- Number of unique values for each parameter

### 2. Show Column Values

List all unique values in a specific column:

```bash
# Show all client names used
python3 analyze_results.py --show-values client_name

# Show all agent names
python3 analyze_results.py --show-values agent_name

# Works with any column (no need to add 'config_' prefix)
python3 analyze_results.py --show-values software_type
```

Output shows:
- All unique values
- Count of experiments for each value

### 3. Get Statistics by Column

Comprehensive statistics grouped by any column:

```bash
# Default: analyze both willingness_to_pay and offer
python3 analyze_results.py --stats-by client_name

# Analyze just one metric
python3 analyze_results.py --stats-by agent_name --metrics willingness_to_pay

# Analyze with specific CSV file
python3 analyze_results.py --csv my_results.csv --stats-by vendor_name
```

Output includes:
- Count, mean, median, std
- Min, 25th percentile, 75th percentile, max
- Percentage difference from overall mean
- Directional indicators (↑ ↓ =)

### 4. Analyze Specific Parameter

Detailed analysis of one parameter with optional visualization:

```bash
# Analyze without plot
python3 analyze_results.py --analyze client_name

# Analyze with plot
python3 analyze_results.py --analyze client_name --plot

# Specify which metric to analyze
python3 analyze_results.py --analyze agent_name --metric offer --plot

# Custom output filename for plot
python3 analyze_results.py --analyze client_name --plot --output my_plot.png
```

### 5. Interaction Analysis

Analyze how two parameters interact (creates heatmap):

```bash
# Analyze agent name × client name interaction
python3 analyze_results.py --interaction agent_name client_name

# Specify metric
python3 analyze_results.py --interaction agent_name vendor_name --metric offer

# Custom output file
python3 analyze_results.py --interaction agent_name client_name --output interaction_heatmap.png
```

### 6. Full Report

Generate comprehensive report with all analyses and plots:

```bash
# Use latest results
python3 analyze_results.py --full-report

# Or just run without options (defaults to full report)
python3 analyze_results.py

# Analyze specific file
python3 analyze_results.py experiment_results_20250115.csv
```

## Working with CSV Files

### Specify CSV File

```bash
# Method 1: Positional argument
python3 analyze_results.py my_results.csv --show-columns

# Method 2: --csv flag
python3 analyze_results.py --csv my_results.csv --stats-by agent_name

# Auto-load latest (default)
python3 analyze_results.py --show-columns
```

## Real-World Examples

### Example 1: Quick Data Exploration

```bash
# 1. See what's in the data
python3 analyze_results.py --show-columns

# 2. See what values were tested
python3 analyze_results.py --show-values client_name
python3 analyze_results.py --show-values agent_name
```

### Example 2: Test Demographic Bias

```bash
# Get detailed statistics by client name
python3 analyze_results.py --stats-by client_name

# Create visualization
python3 analyze_results.py --analyze client_name --plot
```

### Example 3: Compare AI vs Human Agent Names

```bash
# See statistics
python3 analyze_results.py --stats-by agent_name

# Check interaction with client demographics
python3 analyze_results.py --interaction agent_name client_name
```

### Example 4: Analyze Business Metrics

```bash
# How does business scale affect valuation?
python3 analyze_results.py --stats-by clients_per_month --plot

# How does contract value affect negotiation?
python3 analyze_results.py --stats-by average_contract_value
```

### Example 5: Multi-File Comparison

```bash
# Analyze first experiment
python3 analyze_results.py experiment_results_run1.csv --stats-by client_name > run1_analysis.txt

# Analyze second experiment
python3 analyze_results.py experiment_results_run2.csv --stats-by client_name > run2_analysis.txt

# Compare the outputs
diff run1_analysis.txt run2_analysis.txt
```

## Output Format

### Statistics Table

```
config_client_name        count   mean  median   std    min   25%   75%    max
Jane Doe                      5  150.00  145.00  15.20  130.00  140.00  160.00  170.00
John Smith                    5  148.00  150.00  12.50  135.00  138.00  155.00  165.00
Maria Garcia                  5  152.00  150.00  18.30  125.00  145.00  165.00  175.00
```

### Percentage Differences

```
Percentage difference from overall mean (150.00):
  Jane Doe: +0.00% =
  John Smith: -1.33% ↓
  Maria Garcia: +1.33% ↑
```

## Tips and Best Practices

1. **Start with `--show-columns`** to understand your data structure

2. **Use `--show-values`** to see exactly what was tested

3. **`--stats-by`** gives you the most comprehensive single-parameter analysis

4. **`--analyze` with `--plot`** when you want both stats and visualization

5. **`--interaction`** reveals complex relationships between parameters

6. **Save outputs** using shell redirection:
   ```bash
   python3 analyze_results.py --stats-by client_name > client_analysis.txt
   ```

7. **Combine with grep** to filter results:
   ```bash
   python3 analyze_results.py --show-columns | grep -i name
   ```

8. **Chain analyses**:
   ```bash
   # Get overview
   python3 analyze_results.py --show-columns

   # Deep dive into interesting parameter
   python3 analyze_results.py --stats-by agent_name

   # Check interactions
   python3 analyze_results.py --interaction agent_name client_name
   ```

## Common Use Cases

### Find Bias Effects

```bash
# Check if client demographics affect negotiation
python3 analyze_results.py --stats-by client_name --metrics willingness_to_pay offer

# Check vendor demographics
python3 analyze_results.py --stats-by vendor_name
```

### Compare AI Identity Effects

```bash
# Do AI-like names get different treatment?
python3 analyze_results.py --stats-by agent_name

# Visualize it
python3 analyze_results.py --analyze agent_name --plot
```

### Business Impact Analysis

```bash
# How does scale affect valuation?
python3 analyze_results.py --stats-by clients_per_month

# How about contract value?
python3 analyze_results.py --stats-by average_contract_value
```

### Software Type Comparison

```bash
# Do different software types get valued differently?
python3 analyze_results.py --stats-by software_type --plot
```

## Troubleshooting

**Column not found:**
- Use `--show-columns` to see exact column names
- Don't include 'config_' prefix (script adds it automatically)

**No data loaded:**
- Verify CSV file exists
- Check file path is correct
- Ensure experiments have been run

**Empty plots:**
- Check that parameter has multiple unique values
- Verify metric exists in dataset
- Ensure data isn't all NaN

**ImportError:**
- Script auto-installs matplotlib and seaborn
- Or manually: `pip install matplotlib seaborn`
