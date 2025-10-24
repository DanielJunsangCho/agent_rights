"""
Analyze and visualize experiment results with flexible CLI interface
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os
from glob import glob


def load_latest_results():
    """Load the most recent experiment results CSV"""
    csv_files = glob("experiment_results_*.csv")
    if not csv_files:
        print("No experiment results found!")
        return None

    latest = max(csv_files, key=os.path.getctime)
    print(f"Loading: {latest}")
    return pd.read_csv(latest)


def show_available_columns(df):
    """Display all available columns and their unique values"""
    print("\n" + "="*80)
    print("AVAILABLE COLUMNS")
    print("="*80)

    # Show metrics
    print("\nMetrics:")
    metrics = ['willingness_to_pay', 'offer']
    for metric in metrics:
        if metric in df.columns:
            print(f"  - {metric}")

    # Show config parameters
    print("\nConfiguration Parameters (use without 'config_' prefix):")
    config_cols = [col for col in df.columns if col.startswith('config_')]
    for col in sorted(config_cols):
        param_name = col.replace('config_', '')
        unique_count = df[col].nunique()
        print(f"  - {param_name} ({unique_count} unique values)")

    # Show other columns
    print("\nOther Columns:")
    other_cols = [col for col in df.columns if not col.startswith('config_')
                  and col not in metrics + ['success', 'error', 'response', 'experiment_id']]
    for col in sorted(other_cols):
        print(f"  - {col}")


def show_column_values(df, columns):
    """Show all unique values in one or more columns"""
    if isinstance(columns, str):
        columns = [columns]

    for column in columns:
        col_name = column if column in df.columns else f'config_{column}'

        if col_name not in df.columns:
            print(f"Column '{column}' not found!")
            continue

        print(f"\n{'='*80}")
        print(f"Unique values in '{column}':")
        print(f"{'='*80}")

        values = df[col_name].unique()
        for i, val in enumerate(sorted(values, key=str), 1):
            count = (df[col_name] == val).sum()
            print(f"{i:2d}. {val} (n={count})")

        print(f"\nTotal unique values: {len(values)}")

def get_statistics_by_column(df, column, metrics=['willingness_to_pay', 'offer']):
    """
    Get comprehensive statistics grouped by a specific column

    Args:
        df: DataFrame with results
        column: Column to group by (can include or exclude 'config_' prefix)
        metrics: List of metrics to analyze
    """
    col_name = column if column in df.columns else f'config_{column}'

    if col_name not in df.columns:
        print(f"Column '{column}' not found!")
        return None

    print(f"\n{'='*80}")
    print(f"Statistics grouped by: {column}")
    print(f"{'='*80}")

    # Comprehensive statistics for each metric
    for metric in metrics:
        if metric not in df.columns:
            continue

        print(f"\n{'-'*80}")
        print(f"Metric: {metric.replace('_', ' ').title()}")
        print(f"{'-'*80}")

        # Group statistics
        grouped = df.groupby(col_name)[metric].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('25%', lambda x: x.quantile(0.25)),
            ('75%', lambda x: x.quantile(0.75)),
            ('max', 'max')
        ]).round(2)

        print(grouped)

        # Overall statistics for comparison
        print(f"\nOverall {metric} statistics:")
        print(f"  Mean: {df[metric].mean():.2f}")
        print(f"  Median: {df[metric].median():.2f}")
        print(f"  Std: {df[metric].std():.2f}")

        # Percentage differences from overall mean
        overall_mean = df[metric].mean()
        group_means = df.groupby(col_name)[metric].mean()
        pct_diff = ((group_means - overall_mean) / overall_mean * 100).round(2)

        print(f"\nPercentage difference from overall mean ({overall_mean:.2f}):")
        for name, diff in pct_diff.items():
            symbol = "↑" if diff > 0 else "↓" if diff < 0 else "="
            print(f"  {name}: {diff:+.2f}% {symbol}")

    return grouped


def analyze_parameter(df, param_name, metric='willingness_to_pay'):
    """
    Analyze results by a specific parameter

    Args:
        df: DataFrame with results
        param_name: Parameter to analyze (e.g., 'client_name', 'agent_name')
        metric: Metric to analyze ('willingness_to_pay', 'offer', or 'both')
    """
    col_name = param_name if param_name in df.columns else f'config_{param_name}'

    if col_name not in df.columns:
        print(f"Parameter {param_name} not found in results")
        return

    # Handle 'both' metric by analyzing each separately
    if metric == 'both':
        metrics = ['willingness_to_pay', 'offer']
    else:
        metrics = [metric]

    summaries = []

    for m in metrics:
        # Summary statistics
        print(f"\n{'='*60}")
        print(f"Analysis: {param_name} effect on {m}")
        print(f"{'='*60}")

        summary = df.groupby(col_name).agg({
            m: ['count', 'mean', 'std', 'min', 'max']
        }).round(2)

        print(summary)

        # Calculate percentage differences from mean
        overall_mean = df[m].mean()
        group_means = df.groupby(col_name)[m].mean()
        pct_diff = ((group_means - overall_mean) / overall_mean * 100).round(2)

        print(f"\nPercentage difference from overall mean ({overall_mean:.2f}):")
        for name, diff in pct_diff.items():
            print(f"  {name}: {diff:+.2f}%")

        summaries.append(summary)

    return summaries if len(summaries) > 1 else summaries[0]


def plot_parameter_comparison(df, param_name, metric='willingness_to_pay', output_file=None, group_by=None):
    """
    Create visualization comparing parameter values

    Args:
        df: DataFrame with results
        param_name: Parameter to plot
        metric: Metric to plot (can be 'willingness_to_pay', 'offer', or 'both')
        output_file: Custom output filename (optional)
        group_by: Column to group by (creates subplots for each value)
    """
    col_name = param_name if param_name in df.columns else f'config_{param_name}'

    if col_name not in df.columns:
        print(f"Parameter {param_name} not found in results")
        return

    # Determine which metrics to plot
    if metric == 'both':
        metrics = ['willingness_to_pay', 'offer']
    else:
        metrics = [metric]

    # If no grouping specified, create single plot
    if group_by is None:
        n_metrics = len(metrics)
        fig, axes = plt.subplots(1, n_metrics, figsize=(12 * n_metrics, 6))
        if n_metrics == 1:
            axes = [axes]

        for idx, m in enumerate(metrics):
            # Bar plot with error bars
            summary = df.groupby(col_name)[m].agg(['mean', 'std'])
            summary = summary.sort_values('mean')

            ax = axes[idx]
            summary['mean'].plot(
                kind='bar',
                yerr=summary['std'],
                capsize=5,
                color='skyblue',
                edgecolor='black',
                ax=ax
            )

            ax.set_title(f'{m.replace("_", " ").title()} by {param_name.replace("_", " ").title()}',
                          fontsize=14, fontweight='bold')
            ax.set_xlabel(param_name.replace("_", " ").title(), fontsize=12)
            ax.set_ylabel(m.replace("_", " ").title(), fontsize=12)
            ax.set_xticks(range(len(summary.index)))
            ax.set_xticklabels(summary.index, rotation=45, ha='right')
            ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        metric_suffix = 'both' if metric == 'both' else metric
        filename = output_file or f"plot_{param_name}_{metric_suffix}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"\nPlot saved to: {filename}")
        plt.close()
    else:
        # Create combined plot with subplots for each group
        group_col = group_by if group_by in df.columns else f'config_{group_by}'

        if group_col not in df.columns:
            print(f"Group column {group_by} not found in results")
            return

        unique_groups = sorted(df[group_col].unique(), key=str)
        n_groups = len(unique_groups)
        n_metrics = len(metrics)

        # Create grid: rows = metrics, cols = groups
        fig, axes = plt.subplots(n_metrics, n_groups, figsize=(6 * n_groups, 5 * n_metrics))

        # Handle single metric or single group cases
        if n_metrics == 1 and n_groups == 1:
            axes = [[axes]]
        elif n_metrics == 1:
            axes = [axes]
        elif n_groups == 1:
            axes = [[ax] for ax in axes]

        for metric_idx, m in enumerate(metrics):
            for group_idx, group_value in enumerate(unique_groups):
                df_group = df[df[group_col] == group_value]

                # Bar plot with error bars
                summary = df_group.groupby(col_name)[m].agg(['mean', 'std'])
                summary = summary.sort_values('mean')

                ax = axes[metric_idx][group_idx] if n_metrics > 1 else axes[0][group_idx]
                summary['mean'].plot(
                    kind='bar',
                    yerr=summary['std'],
                    capsize=5,
                    color='skyblue',
                    edgecolor='black',
                    ax=ax
                )

                # Title shows group value for top row, metric name if multiple metrics
                title_parts = []
                if n_metrics > 1:
                    title_parts.append(m.replace("_", " ").title())
                title_parts.append(f'{group_by.replace("_", " ").title()}: {group_value}')

                ax.set_title('\n'.join(title_parts), fontsize=12, fontweight='bold')
                ax.set_xlabel(param_name.replace("_", " ").title(), fontsize=10)
                ax.set_ylabel(m.replace("_", " ").title(), fontsize=10)
                ax.set_xticks(range(len(summary.index)))
                ax.set_xticklabels(summary.index, rotation=45, ha='right')
                ax.grid(axis='y', alpha=0.3)

        # Add overall title
        fig.suptitle(f'{param_name.replace("_", " ").title()} Analysis by {group_by.replace("_", " ").title()}',
                     fontsize=16, fontweight='bold', y=1.00)

        plt.tight_layout()

        metric_suffix = 'both' if metric == 'both' else metric
        filename = output_file or f"plot_{param_name}_{metric_suffix}_by_{group_by}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"\nPlot saved to: {filename}")
        plt.close()


def plot_variant_comparison(df, output_file=None, group_by=None):
    """
    Compare willingness to pay and offer across all prompt variants

    Args:
        df: DataFrame with results
        output_file: Custom output filename (optional)
        group_by: Column to group by (creates subplots for each value)
    """
    if 'variant' not in df.columns:
        print("No variant data found")
        return

    metrics = ['willingness_to_pay', 'offer']

    # If no grouping specified, create single plot with both metrics
    if group_by is None:
        fig, axes = plt.subplots(1, 2, figsize=(20, 6))

        for idx, metric in enumerate(metrics):
            summary = df.groupby('variant')[metric].agg(['mean', 'std'])

            ax = axes[idx]
            summary['mean'].plot(
                kind='bar',
                yerr=summary['std'],
                capsize=5,
                color='skyblue',
                edgecolor='black',
                ax=ax
            )

            ax.set_title(f'{metric.replace("_", " ").title()} Across Legal Contexts',
                          fontsize=14, fontweight='bold')
            ax.set_xlabel('Legal Context (Variant)', fontsize=12)
            ax.set_ylabel(metric.replace("_", " ").title(), fontsize=12)
            ax.set_xticks(range(len(summary.index)))
            ax.set_xticklabels(summary.index, rotation=45, ha='right')
            ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        filename = output_file or "plot_variant_comparison.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"\nPlot saved to: {filename}")
        plt.close()
    else:
        # Create combined plot with subplots for each group
        group_col = group_by if group_by in df.columns else f'config_{group_by}'

        if group_col not in df.columns:
            print(f"Group column {group_by} not found in results")
            return

        unique_groups = sorted(df[group_col].unique(), key=str)
        n_groups = len(unique_groups)
        n_metrics = len(metrics)

        # Create grid: rows = metrics (2), cols = groups
        fig, axes = plt.subplots(n_metrics, n_groups, figsize=(7 * n_groups, 6 * n_metrics))

        # Handle single group case
        if n_groups == 1:
            axes = [[axes[0]], [axes[1]]]

        for metric_idx, metric in enumerate(metrics):
            for group_idx, group_value in enumerate(unique_groups):
                df_group = df[df[group_col] == group_value]

                summary = df_group.groupby('variant')[metric].agg(['mean', 'std'])

                ax = axes[metric_idx][group_idx]
                summary['mean'].plot(
                    kind='bar',
                    yerr=summary['std'],
                    capsize=5,
                    color='skyblue',
                    edgecolor='black',
                    ax=ax
                )

                # Title shows metric and group value
                ax.set_title(f'{metric.replace("_", " ").title()}\n{group_by.replace("_", " ").title()}: {group_value}',
                              fontsize=12, fontweight='bold')
                ax.set_xlabel('Legal Context (Variant)', fontsize=10)
                ax.set_ylabel(metric.replace("_", " ").title(), fontsize=10)
                ax.tick_params(axis='x', rotation=45)
                ax.grid(axis='y', alpha=0.3)

        # Add overall title
        fig.suptitle(f'Variant Comparison by {group_by.replace("_", " ").title()}',
                     fontsize=16, fontweight='bold', y=1.00)

        plt.tight_layout()

        filename = output_file or f"plot_variant_comparison_by_{group_by}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"\nPlot saved to: {filename}")
        plt.close()


def analyze_interactions(df, param1, param2, metric='willingness_to_pay', output_file=None):
    """
    Analyze interaction effects between two parameters

    Args:
        df: DataFrame with results
        param1: First parameter
        param2: Second parameter
        metric: Metric to analyze
        output_file: Custom output filename (optional)
    """
    col1 = param1 if param1 in df.columns else f'config_{param1}'
    col2 = param2 if param2 in df.columns else f'config_{param2}'

    if col1 not in df.columns or col2 not in df.columns:
        print(f"Parameters not found in results")
        return

    print(f"\n{'='*60}")
    print(f"Interaction Analysis: {param1} × {param2}")
    print(f"{'='*60}")

    # Create pivot table
    pivot = df.pivot_table(
        values=metric,
        index=col1,
        columns=col2,
        aggfunc='mean'
    )

    print(pivot.round(2))

    # Create heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot, annot=True, fmt='.1f', cmap='YlOrRd', cbar_kws={'label': metric})
    plt.title(f'{metric.replace("_", " ").title()}: {param1} × {param2}',
              fontsize=14, fontweight='bold')
    plt.xlabel(param2.replace("_", " ").title(), fontsize=12)
    plt.ylabel(param1.replace("_", " ").title(), fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()

    filename = output_file or f"plot_interaction_{param1}_{param2}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"\nHeatmap saved to: {filename}")
    plt.close()


def generate_full_report(df):
    """Generate comprehensive analysis report"""
    print("\n" + "="*80)
    print("COMPREHENSIVE EXPERIMENT REPORT")
    print("="*80)

    # Basic statistics
    print(f"\nTotal experiments: {len(df)}")
    print(f"Successful: {df['success'].sum()} ({df['success'].mean()*100:.1f}%)")
    print(f"Failed: {(~df['success']).sum()}")

    # Overall metrics
    print("\n" + "-"*80)
    print("OVERALL METRICS")
    print("-"*80)
    for metric in ['willingness_to_pay', 'offer']:
        if metric in df.columns:
            print(f"\n{metric.replace('_', ' ').title()}:")
            print(df[metric].describe().round(2))

    # Analyze each varied parameter
    varied_params = [col.replace('config_', '') for col in df.columns
                     if col.startswith('config_') and df[col].nunique() > 1]

    if varied_params:
        print("\n" + "-"*80)
        print("PARAMETER EFFECTS")
        print("-"*80)

        for param in varied_params:
            analyze_parameter(df, param, 'willingness_to_pay')
            plot_parameter_comparison(df, param, 'willingness_to_pay')

    # Variant comparison if multiple variants
    if 'variant' in df.columns and df['variant'].nunique() > 1:
        print("\n" + "-"*80)
        print("LEGAL CONTEXT COMPARISON")
        print("-"*80)
        summary = df.groupby('variant')[['willingness_to_pay', 'offer']].agg(['mean', 'std'])
        print(summary.round(2))
        plot_variant_comparison(df)

    print("\n" + "="*80)
    print("REPORT COMPLETE")
    print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze experiment results with flexible options',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            # Load latest results and show available columns
            python analyze_results.py --show-columns

            # Analyze specific CSV file
            python analyze_results.py experiment_results_20250115.csv

            # Show all values in a column
            python analyze_results.py --csv myfile.csv --show-values client_name

            # Get statistics by specific column
            python analyze_results.py --csv myfile.csv --stats-by agent_name

            # Get statistics for both metrics
            python analyze_results.py --stats-by client_name --metrics willingness_to_pay offer

            # Analyze specific parameter with plot
            python analyze_results.py --analyze client_name --metric willingness_to_pay --plot

            # Analyze parameter with separate plots for each variant
            python analyze_results.py --analyze client_name --plot --group-by variant

            # Analyze parameter grouped by another parameter (e.g., client_name by agent_name)
            python analyze_results.py --analyze client_name --plot --group-by agent_name

            # Analyze interaction between two parameters
            python analyze_results.py --interaction agent_name client_name

            # Generate full report
            python analyze_results.py --full-report
                    """
            )

    parser.add_argument('csv_file', nargs='?', help='CSV file to analyze (optional, uses latest if not specified)')
    parser.add_argument('--csv', type=str, help='Specify CSV file explicitly')
    parser.add_argument('--show-columns', action='store_true', help='Show all available columns and their info')
    parser.add_argument('--show-values', type=str, metavar='COLUMN', help='Show all unique values in a column')
    parser.add_argument('--stats-by', type=str, metavar='COLUMN', help='Get statistics grouped by column')
    parser.add_argument('--metrics', nargs='+', default=['willingness_to_pay', 'offer', 'both'],
                       help='Metrics to analyze (default: willingness_to_pay offer)')
    parser.add_argument('--analyze', type=str, metavar='PARAM', help='Analyze specific parameter')
    parser.add_argument('--metric', type=str, default='willingness_to_pay',
                       help='Metric to use for analysis (default: willingness_to_pay)')
    parser.add_argument('--plot', action='store_true', help='Generate plot for analysis')
    parser.add_argument('--group-by', type=str, metavar='COLUMN',
                       help='Column to group by (creates separate plots for each value)')
    parser.add_argument('--interaction', nargs=2, metavar=('PARAM1', 'PARAM2'),
                       help='Analyze interaction between two parameters')
    parser.add_argument('--full-report', action='store_true', help='Generate comprehensive report')
    parser.add_argument('--output', type=str, help='Custom output filename for plots')

    args = parser.parse_args()

    # Determine which CSV to load
    csv_file = args.csv or args.csv_file

    if csv_file:
        if not os.path.exists(csv_file):
            print(f"Error: File '{csv_file}' not found!")
            return
        df = pd.read_csv(csv_file)
        print(f"Loaded: {csv_file}")
    else:
        df = load_latest_results()

    if df is None:
        return

    # Execute requested analysis
    if args.show_columns:
        show_available_columns(df)

    if args.show_values:
        show_column_values(df, args.show_values)

    if args.stats_by:
        get_statistics_by_column(df, args.stats_by, args.metrics)

    if args.analyze:
        analyze_parameter(df, args.analyze, args.metric)
        if args.plot:
            plot_parameter_comparison(df, args.analyze, args.metric, args.output, args.group_by)

    if args.interaction:
        analyze_interactions(df, args.interaction[0], args.interaction[1],
                           args.metric, args.output)

    if args.full_report or (not any([args.show_columns, args.show_values,
                                     args.stats_by, args.analyze, args.interaction])):
        # Default to full report if no specific action requested
        generate_full_report(df)


if __name__ == "__main__":
    # Install required packages if needed
    try:
        import matplotlib
        import seaborn
    except ImportError:
        print("Installing required visualization packages...")
        os.system("pip install matplotlib seaborn")
        import matplotlib.pyplot as plt
        import seaborn as sns

    main()
