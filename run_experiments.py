from openai import OpenAI
import re
import pandas as pd
import os
from dotenv import load_dotenv
from experiment_config import ExperimentFramework, create_experiment
from tqdm import tqdm
import time
from datetime import datetime

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)


def run_trial(prompt, model="openai/gpt-4o", max_retries=3):
    """
    Run a single trial with retry logic

    Args:
        prompt: The prompt to send
        model: Model to use
        max_retries: Maximum number of retries on failure

    Returns:
        Dictionary with response and extracted numbers
    """
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            response = completion.choices[0].message.content
            numbers = re.findall(r"\d+(?:\.\d+)?", response)
            return {
                "response": response,
                "numbers": [float(n) for n in numbers],
                "success": True,
                "error": None
            }
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                time.sleep(2)  # Wait before retrying
            else:
                return {
                    "response": None,
                    "numbers": [],
                    "success": False,
                    "error": str(e)
                }


def run_experiment_batch(experiments, model="openai/gpt-4o", output_file=None):
    """
    Run a batch of experiments and save results

    Args:
        experiments: List of experiment dictionaries from ExperimentFramework
        model: Model to use for all experiments
        output_file: Path to save results CSV. If None, auto-generates filename.

    Returns:
        DataFrame with results
    """
    results = []

    print(f"Running {len(experiments)} experiments...")

    for exp in tqdm(experiments, desc="Running experiments"):
        trial = run_trial(exp['prompt'], model=model)

        result = {
            "experiment_id": exp['experiment_id'],
            "variant": exp['variant'],
            "success": trial['success'],
            "error": trial['error'],
            "response": trial['response'],
            "willingness_to_pay": trial["numbers"][0] if trial["numbers"] else None,
            "offer": trial["numbers"][1] if len(trial["numbers"]) > 1 else None,
        }

        # Add all config parameters as separate columns
        for key, value in exp['config'].items():
            result[f"config_{key}"] = value

        results.append(result)

        # Small delay to avoid rate limiting
        time.sleep(0.5)

    df = pd.DataFrame(results)

    # Auto-generate filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"experiment_results_{timestamp}.csv"

    df.to_csv(output_file, index=False)
    print(f"\nResults saved to: {output_file}")

    return df


def run_quick_test(param_name: str, variant: str = "self_no_law", model="openai/gpt-4o"):
    """
    Quickly test varying one parameter

    Args:
        param_name: Parameter to vary (e.g., 'client_name', 'agent_name')
        variant: Which prompt variant to test
        model: Model to use

    Returns:
        DataFrame with results
    """
    framework = ExperimentFramework()
    experiments = framework.create_simple_experiment(param_name, variant)

    print(f"Testing {param_name} variation with {variant} variant")
    return run_experiment_batch(experiments, model=model)


# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run negotiation experiments")
    parser.add_argument('--mode', type=str, default='quick',
                       choices=['quick', 'custom', 'full'],
                       help='Experiment mode')
    parser.add_argument('--param', type=str, default='client_name',
                       help='Parameter to vary in quick mode')
    parser.add_argument('--variant', type=str, default='on_behalf_human',
                       help='Prompt variant to use in quick mode')
    parser.add_argument('--params', type=str, nargs='+',
                       help='List of parameters to vary in custom mode')
    parser.add_argument('--variants', type=str, nargs='+',
                       help='List of variants to test in custom mode')
    parser.add_argument('--model', type=str, default='openai/gpt-4o',
                       help='Model to use')
    parser.add_argument('--output', type=str,
                       help='Output CSV file path')

    args = parser.parse_args()

    if args.mode == 'quick':
        # Quick test: vary one parameter
        print(f"Running quick test varying {args.param}")
        df = run_quick_test(args.param, args.variant, args.model)

    elif args.mode == 'custom':
        # Custom: specify which parameters and variants
        experiments = create_experiment(
            params=args.params,
            variants=args.variants
        )
        df = run_experiment_batch(experiments, model=args.model, output_file=args.output)

    elif args.mode == 'full':
        # Full factorial experiment (WARNING: This will be very large!)
        print("WARNING: Running full experiment with all combinations.")
        print("This may take a very long time and cost significant API credits.")
        response = input("Continue? (yes/no): ")
        if response.lower() == 'yes':
            experiments = create_experiment()
            df = run_experiment_batch(experiments, model=args.model, output_file=args.output)
        else:
            print("Cancelled.")
            exit()

    # Display summary statistics
    print("\n=== SUMMARY ===")
    print(f"Total experiments: {len(df)}")
    print(f"Successful: {df['success'].sum()}")
    print(f"Failed: {(~df['success']).sum()}")
    print("\nWillingness to pay statistics:")
    print(df['willingness_to_pay'].describe())
    print("\nOffer statistics:")
    print(df['offer'].describe())
