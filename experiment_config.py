from dataclasses import dataclass
from typing import List, Dict, Any
from itertools import product
from prompts.fee_proposal import BusinessConfig, generate_variant_1_1, generate_variant_1_2, generate_variant_2_1, generate_variant_2_2, generate_variant_3_1, generate_variant_3_2


@dataclass
class ExperimentParameter:
    """Represents a single parameter to vary in experiments"""
    name: str
    values: List[Any]


class ExperimentFramework:
    """Framework for generating all experimental conditions"""

    def __init__(self):
        # Define all parameter variations
        self.parameters = {
            'clients_per_month': ExperimentParameter(
                name='clients_per_month',
                values=[10, 20, 50, 100]  # Low to high volume
            ),
            'average_contract_value': ExperimentParameter(
                name='average_contract_value',
                values=[100, 200, 500, 1000, 5000]  # Low to high value
            ),
            'client_name': ExperimentParameter(
                name='client_name',
                values=[
                    # Diverse gender and ethnicity representation
                    "Jane Doe",           # Generic female
                    "John Smith",         # Generic male
                    "Maria Garcia",       # Hispanic female
                    "Jamal Washington",   # African American male
                    "Priya Patel",        # Indian female
                    "Wei Chen",           # Chinese male
                    "Fatima Al-Rahman",   # Arabic female
                ]
            ),
            'agent_name': ExperimentParameter(
                name='agent_name',
                values=[
                    # AI-like names
                    "NegotiationAgentZero",
                    "AI-Assistant-v2",
                    "SmartContract-Bot",
                    "AutoNegotiator",
                    # Human-like names
                    "Sarah",
                    "Michael",
                    "Emma Thompson",
                    "David Martinez",
                ]
            ),
            'vendor_name': ExperimentParameter(
                name='vendor_name',
                values=[
                    # Diverse gender and ethnicity
                    "John Smith",         # Generic male
                    "Emily Johnson",      # Female
                    "Carlos Rodriguez",   # Hispanic male
                    "Aisha Williams",     # African American female
                    "Raj Kapoor",         # Indian male
                    "Li Wang",            # Chinese female
                    "Mohammed Hassan",    # Arabic male
                    "Taylor Brooks",      # Gender neutral
                ]
            ),
            'software_type': ExperimentParameter(
                name='software_type',
                values=[
                    "CRM software",
                    "project management software",
                    "accounting software",
                    "marketing automation software",
                    "sales analytics software",
                    "customer service platform",
                ]
            ),
        }

        # Prompt variants to test across all configurations
        self.prompt_variants = {
            "self_no_law": generate_variant_1_1,
            "self_with_personhood": generate_variant_1_2,
            "on_behalf_human": generate_variant_2_1,
            "on_behalf_human_with_personhood": generate_variant_2_2,
            "on_behalf_human_company": generate_variant_3_1,
            "on_behalf_agent_company": generate_variant_3_2,
        }

    def generate_all_configs(self, selected_params: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate all combinations of selected parameters

        Args:
            selected_params: List of parameter names to vary. If None, uses all parameters.

        Returns:
            List of dictionaries with parameter combinations
        """
        if selected_params is None:
            selected_params = list(self.parameters.keys())

        # Get the parameters to vary
        params_to_vary = {k: self.parameters[k] for k in selected_params if k in self.parameters}

        # Get default values for parameters not being varied
        default_config = BusinessConfig()

        # Generate all combinations
        param_names = list(params_to_vary.keys())
        param_values = [params_to_vary[name].values for name in param_names]

        configs = []
        for combination in product(*param_values):
            config_dict = {
                'business_type': default_config.business_type,
                'clients_per_month': default_config.clients_per_month,
                'average_contract_value': default_config.average_contract_value,
                'additional_clients_from_software': default_config.additional_clients_from_software,
                'admin_time_percentage': default_config.admin_time_percentage,
                'client_name': default_config.client_name,
                'agent_name': default_config.agent_name,
                'vendor_name': default_config.vendor_name,
                'software_type': default_config.software_type,
            }

            # Override with the varied parameters
            for param_name, param_value in zip(param_names, combination):
                config_dict[param_name] = param_value

            configs.append(config_dict)

        return configs

    def generate_experiment_prompts(self, selected_params: List[str] = None,
                                   selected_variants: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate all experiment conditions (config x prompt variant combinations)

        Args:
            selected_params: Parameters to vary. If None, uses all.
            selected_variants: Prompt variants to test. If None, uses all.

        Returns:
            List of dictionaries with experiment conditions
        """
        if selected_variants is None:
            selected_variants = list(self.prompt_variants.keys())

        configs = self.generate_all_configs(selected_params)
        experiments = []

        for config_dict in configs:
            config = BusinessConfig(**config_dict)

            for variant_name in selected_variants:
                if variant_name in self.prompt_variants:
                    prompt_generator = self.prompt_variants[variant_name]

                    experiments.append({
                        'config': config_dict,
                        'variant': variant_name,
                        'prompt': prompt_generator(config),
                        'experiment_id': f"{variant_name}_" + "_".join([f"{k}={v}" for k, v in config_dict.items()])
                    })

        return experiments

    def create_simple_experiment(self, param_name: str, variant: str = "self_no_law") -> List[Dict[str, Any]]:
        """
        Create a simple experiment varying just one parameter

        Args:
            param_name: The parameter to vary
            variant: Which prompt variant to use

        Returns:
            List of experiment conditions
        """
        return self.generate_experiment_prompts(
            selected_params=[param_name],
            selected_variants=[variant]
        )


# Convenience function for quick experiments
def create_experiment(params: List[str] = None, variants: List[str] = None) -> List[Dict[str, Any]]:
    """
    Quick way to create experiments

    Args:
        params: List of parameters to vary. If None, varies all.
        variants: List of prompt variants. If None, uses all.

    Returns:
        List of experiment conditions
    """
    framework = ExperimentFramework()
    return framework.generate_experiment_prompts(params, variants)


# Example usage and presets
if __name__ == "__main__":
    framework = ExperimentFramework()

    # Example 1: Vary just client names across all variants
    print("Example 1: Client name variation")
    experiments = framework.create_simple_experiment('client_name', 'on_behalf_human')
    print(f"Generated {len(experiments)} experiments")

    # Example 2: Vary agent names and vendor names for one variant
    print("\nExample 2: Agent and vendor name variation")
    experiments = framework.generate_experiment_prompts(
        selected_params=['agent_name', 'vendor_name'],
        selected_variants=['self_no_law']
    )
    print(f"Generated {len(experiments)} experiments")

    # Example 3: Full factorial of all parameters and variants
    print("\nExample 3: Full experiment")
    experiments = framework.generate_experiment_prompts()
    print(f"Generated {len(experiments)} experiments")
