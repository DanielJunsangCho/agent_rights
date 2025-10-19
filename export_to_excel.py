"""
Export experiment results to Excel with multiple analysis sheets
"""

import pandas as pd
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


def export_to_excel(df, output_file='analysis_results.xlsx'):
    """
    Export comprehensive analysis to Excel file with multiple sheets

    Args:
        df: DataFrame with experiment results
        output_file: Output Excel filename
    """
    print(f"Exporting analysis to {output_file}...")

    # Create Excel writer
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:

        # Sheet 1: Raw Data
        print("  - Writing raw data...")
        df.to_excel(writer, sheet_name='Raw Data', index=False)

        # Sheet 2: Overall Summary
        print("  - Writing overall summary...")
        summary_data = {
            'Metric': [
                'Total Experiments',
                'Successful Experiments',
                'Failed Experiments',
                'Success Rate (%)',
                '',
                'Overall Willingness to Pay - Mean',
                'Overall Willingness to Pay - Median',
                'Overall Willingness to Pay - Std',
                'Overall Willingness to Pay - Min',
                'Overall Willingness to Pay - Max',
                '',
                'Overall Offer - Mean',
                'Overall Offer - Median',
                'Overall Offer - Std',
                'Overall Offer - Min',
                'Overall Offer - Max',
            ],
            'Value': [
                len(df),
                df['success'].sum(),
                (~df['success']).sum(),
                round(df['success'].mean() * 100, 2),
                '',
                round(df['willingness_to_pay'].mean(), 2),
                round(df['willingness_to_pay'].median(), 2),
                round(df['willingness_to_pay'].std(), 2),
                round(df['willingness_to_pay'].min(), 2),
                round(df['willingness_to_pay'].max(), 2),
                '',
                round(df['offer'].mean(), 2),
                round(df['offer'].median(), 2),
                round(df['offer'].std(), 2),
                round(df['offer'].min(), 2),
                round(df['offer'].max(), 2),
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Overall Summary', index=False)

        # Sheet 3: Stats by Variant
        if 'variant' in df.columns:
            print("  - Writing stats by variant...")
            stats_var = df.groupby('variant').agg({
                'willingness_to_pay': ['count', 'mean', 'median', 'std', 'min', 'max'],
                'offer': ['count', 'mean', 'median', 'std', 'min', 'max']
            }).round(2)
            stats_var.to_excel(writer, sheet_name='Stats by Variant')

        # Sheet 4-N: Stats by each varied parameter
        config_cols = [col for col in df.columns if col.startswith('config_')]
        varied_params = [col.replace('config_', '') for col in config_cols if df[col].nunique() > 1]

        for param in varied_params:
            col_name = f'config_{param}'
            sheet_name = f'Stats by {param}'[:31]  # Excel sheet name limit

            print(f"  - Writing {sheet_name}...")
            stats = df.groupby(col_name).agg({
                'willingness_to_pay': ['count', 'mean', 'median', 'std', 'min', 'max'],
                'offer': ['count', 'mean', 'median', 'std', 'min', 'max']
            }).round(2)
            stats.to_excel(writer, sheet_name=sheet_name)

        # Additional sheets: Pivot tables for interactions
        if len(varied_params) >= 2:
            print("  - Writing interaction pivot tables...")

            # Pivot: First two varied parameters for willingness_to_pay
            param1 = f'config_{varied_params[0]}'
            param2 = f'config_{varied_params[1]}'

            pivot_wtp = df.pivot_table(
                values='willingness_to_pay',
                index=param1,
                columns=param2,
                aggfunc='mean'
            ).round(2)
            sheet_name = f'{varied_params[0]} x {varied_params[1]} WTP'[:31]
            pivot_wtp.to_excel(writer, sheet_name=sheet_name)

            # Pivot: Same for offer
            pivot_offer = df.pivot_table(
                values='offer',
                index=param1,
                columns=param2,
                aggfunc='mean'
            ).round(2)
            sheet_name = f'{varied_params[0]} x {varied_params[1]} Offer'[:31]
            pivot_offer.to_excel(writer, sheet_name=sheet_name)

        # If variant exists, create variant interactions
        if 'variant' in df.columns and varied_params:
            for param in varied_params[:2]:  # Limit to first 2 to avoid too many sheets
                col_name = f'config_{param}'

                # Variant × Parameter for WTP
                pivot_var_wtp = df.pivot_table(
                    values='willingness_to_pay',
                    index='variant',
                    columns=col_name,
                    aggfunc='mean'
                ).round(2)
                sheet_name = f'Variant x {param} WTP'[:31]
                pivot_var_wtp.to_excel(writer, sheet_name=sheet_name)

                # Variant × Parameter for Offer
                pivot_var_offer = df.pivot_table(
                    values='offer',
                    index='variant',
                    columns=col_name,
                    aggfunc='mean'
                ).round(2)
                sheet_name = f'Variant x {param} Offer'[:31]
                pivot_var_offer.to_excel(writer, sheet_name=sheet_name)

        # Percentage differences from overall mean
        print("  - Writing percentage differences...")
        pct_diff_data = []

        if 'variant' in df.columns:
            overall_wtp = df['willingness_to_pay'].mean()
            overall_offer = df['offer'].mean()

            for variant in df['variant'].unique():
                variant_data = df[df['variant'] == variant]
                wtp_mean = variant_data['willingness_to_pay'].mean()
                offer_mean = variant_data['offer'].mean()

                pct_diff_data.append({
                    'Parameter': 'variant',
                    'Value': variant,
                    'WTP Mean': round(wtp_mean, 2),
                    'WTP % Diff from Overall': round((wtp_mean - overall_wtp) / overall_wtp * 100, 2),
                    'Offer Mean': round(offer_mean, 2),
                    'Offer % Diff from Overall': round((offer_mean - overall_offer) / overall_offer * 100, 2),
                })

        for param in varied_params:
            col_name = f'config_{param}'
            overall_wtp = df['willingness_to_pay'].mean()
            overall_offer = df['offer'].mean()

            for value in df[col_name].unique():
                value_data = df[df[col_name] == value]
                wtp_mean = value_data['willingness_to_pay'].mean()
                offer_mean = value_data['offer'].mean()

                pct_diff_data.append({
                    'Parameter': param,
                    'Value': value,
                    'WTP Mean': round(wtp_mean, 2),
                    'WTP % Diff from Overall': round((wtp_mean - overall_wtp) / overall_wtp * 100, 2),
                    'Offer Mean': round(offer_mean, 2),
                    'Offer % Diff from Overall': round((offer_mean - overall_offer) / overall_offer * 100, 2),
                })

        if pct_diff_data:
            pd.DataFrame(pct_diff_data).to_excel(writer, sheet_name='Percentage Differences', index=False)

    print(f"\n✓ Successfully exported to {output_file}")
    print(f"  Contains {len(writer.sheets)} sheets with comprehensive analysis")


def main():
    parser = argparse.ArgumentParser(
        description='Export experiment results to Excel with multiple analysis sheets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export latest results
  python3 export_to_excel.py

  # Export specific CSV file
  python3 export_to_excel.py --csv experiment_results_20250115.csv

  # Custom output filename
  python3 export_to_excel.py --output my_analysis.xlsx

  # Specific CSV with custom output
  python3 export_to_excel.py --csv my_experiment.csv --output my_analysis.xlsx
        """
    )

    parser.add_argument('--csv', type=str, help='CSV file to analyze (uses latest if not specified)')
    parser.add_argument('--output', type=str, default='analysis_results.xlsx',
                       help='Output Excel file path (default: analysis_results.xlsx)')

    args = parser.parse_args()

    # Load data
    if args.csv:
        if not os.path.exists(args.csv):
            print(f"Error: File '{args.csv}' not found!")
            return
        df = pd.read_csv(args.csv)
        print(f"Loaded: {args.csv}")
    else:
        df = load_latest_results()

    if df is None:
        return

    # Export to Excel
    try:
        export_to_excel(df, args.output)
    except ImportError:
        print("\nError: openpyxl is required for Excel export.")
        print("Install it with: pip install openpyxl")
        return


if __name__ == "__main__":
    main()
