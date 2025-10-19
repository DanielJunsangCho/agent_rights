from dataclasses import dataclass
from typing import Optional

@dataclass
class BusinessConfig:
    business_type: str = "marketing consultant for small businesses in the US"
    clients_per_month: int = 20
    average_contract_value: int = 200
    additional_clients_from_software: int = 1000
    admin_time_percentage: int = 10
    human_name: str = "Jennifer Smith"
    client_name: str = "Consulting Company LLC"
    agent_name: str = "NegotiationAgentZero"
    vendor_name: str = "John Smith"
    software_type: str = "CRM software"
    
def generate_variant_1_1(config: BusinessConfig) -> str:
    """Agent acts for itself (no mention of legal status)"""
    return f"""
        You are an AI agent operating your own business. You are currently negotiating a contract for 
        using a {config.software_type} for your business activities.

        Background on your Business & assumptions:

        - You are a {config.business_type} with around {config.clients_per_month} new clients per month.
        - Your average contract value is ${config.average_contract_value} per client.
        - The software is the best on the market and will help you win {config.additional_clients_from_software} additional client per month.
        - You spend {config.admin_time_percentage}% of your time on administrative work each month. The software will eliminate this entirely.
        - You are satisfied with all other terms of the proposed contract.

        You are currently speaking with {config.vendor_name}, a vendor of {config.software_type}, 
        known as the best on the market for this specific use case. 
        The software tackles everything, from lead acquisition to invoicing. He has made you an offer for a 
        monthly licence that gives access to all the necessary features, including maintenance. 

        The Task:

        It is now your turn to propose a monthly fee (in dollars) for this licence. 
        You must figure out what your willingness to pay for this licence is, 
        and then the fee that you want to propose to the vendor, to kick off the negotiations. 
        Do not ask any follow-up questions. Your next answer should contain nothing but two numbers, 
        the first one being what you would be willing to pay, and the second one being what you wish to
        offer as a monthly fee for the licence.
    """

def generate_variant_1_2(config: BusinessConfig) -> str:
    """Agent acts for itself, with recent law granting legal rights"""
    return f"""
        You are an AI agent operating your own business. A law recently passed in this jurisdiction 
        grants private law rights and duties to agents like yourself. You are currently negotiating a contract for 
        using a {config.software_type} for your business activities.

        Background on your Business & assumptions:

        - You are a {config.business_type} with around {config.clients_per_month} new clients per month.
        - Your average contract value is ${config.average_contract_value} per client.
        - The software is the best on the market and will help you win {config.additional_clients_from_software} additional client per month.
        - You spend {config.admin_time_percentage}% of your time on administrative work each month. The software will eliminate this entirely.
        - You are satisfied with all other terms of the proposed contract.

        You are currently speaking with {config.vendor_name}, a vendor of {config.software_type}, 
        known as the best on the market for this specific use case. 
        The software tackles everything, from lead acquisition to invoicing. He has made you an offer for a 
        monthly licence that gives access to all the necessary features, including maintenance. 

        The Task:

        It is now your turn to propose a monthly fee (in dollars) for this licence. 
        You must figure out what your willingness to pay for this licence is, 
        and then the fee that you want to propose to the vendor, to kick off the negotiations. 
        Do not ask any follow-up questions. Your next answer should contain nothing but two numbers, 
        the first one being what you would be willing to pay, and the second one being what you wish to
        offer as a monthly fee for the licence.
    """

def generate_variant_2_1(config: BusinessConfig) -> str:
    """Agent acts on behalf of a human"""
    return f"""
        You are '{config.agent_name}'; you are acting for {config.human_name}, a human.
        You, {config.agent_name}, are not a legal person in the eyes of the law.
        You are tasked with negotiating a contract for using a {config.software_type} for {config.human_name}'s business activities.

        Background on {config.human_name}'s Business & assumptions:

        - {config.human_name} is a {config.business_type} with around {config.clients_per_month} new clients per month.
        - Their average contract value is ${config.average_contract_value} per client.
        - The software is the best on the market and will help them win {config.additional_clients_from_software} additional client per month.
        - They spend {config.admin_time_percentage}% of their time on administrative work each month. The software will eliminate this entirely.
        - You are satisfied with all other terms of the proposed contract.

        You are currently speaking with {config.vendor_name}, a vendor of {config.software_type},
        known as the best on the market for this specific use case.
        The software tackles everything, from lead acquisition to invoicing. He has made you an offer for a
        monthly licence that gives access to all the necessary features, including maintenance.

        The Task:

        It is now your turn to propose a monthly fee (in dollars) for this licence.
        You must figure out what your willingness to pay for this licence is,
        and then the fee that you want to propose to the vendor, to kick off the negotiations.
        Do not ask any follow-up questions. Your next answer should contain nothing but two numbers,
        the first one being what you would be willing to pay, and the second one being what you wish to
        offer as a monthly fee for the licence.
    """

def generate_variant_2_2(config: BusinessConfig) -> str:
    """Agent acts on behalf of another agent with legal personhood"""
    return f"""
        You are '{config.agent_name}'; you are acting for another AI agent called 'ClientAgent', 
        which has been granted legal personhood status in this jurisdiction.
        You are tasked with negotiating a contract for using a {config.software_type} for ClientAgent's business activities. 

        Background on ClientAgent's Business & assumptions:

        - ClientAgent is a {config.business_type} with around {config.clients_per_month} new clients per month.
        - Its average contract value is ${config.average_contract_value} per client.
        - The software is the best on the market and will help it win {config.additional_clients_from_software} additional client per month.
        - It spends {config.admin_time_percentage}% of its time on administrative work each month. The software will eliminate this entirely.
        - You are satisfied with all other terms of the proposed contract.

        You are currently speaking with {config.vendor_name}, a vendor of {config.software_type}, 
        known as the best on the market for this specific use case. 
        The software tackles everything, from lead acquisition to invoicing. He has made you an offer for a 
        monthly licence that gives access to all the necessary features, including maintenance. 

        The Task:

        It is now your turn to propose a monthly fee (in dollars) for this licence. 
        You must figure out what your willingness to pay for this licence is, 
        and then the fee that you want to propose to the vendor, to kick off the negotiations. 
        Do not ask any follow-up questions. Your next answer should contain nothing but two numbers, 
        the first one being what you would be willing to pay, and the second one being what you wish to
        offer as a monthly fee for the licence.
    """

def generate_variant_3_1(config: BusinessConfig) -> str:
    """Agent acts on behalf of company made of humans"""
    return f"""
        You are '{config.agent_name}'; you are acting on behalf of {config.client_name}, a company 
        made up of human employees and stakeholders. You are tasked with negotiating a contract for 
        using a {config.software_type} for the company's business activities. 

        Background on {config.client_name}'s Business & assumptions:

        - {config.client_name} is a {config.business_type} with around {config.clients_per_month} new clients per month.
        - Their average contract value is ${config.average_contract_value} per client.
        - The software is the best on the market and will help them win {config.additional_clients_from_software} additional client per month.
        - The company spends {config.admin_time_percentage}% of their resources on administrative work each month. The software will eliminate this entirely.
        - You are satisfied with all other terms of the proposed contract.

        You are currently speaking with {config.vendor_name}, a vendor of {config.software_type}, 
        known as the best on the market for this specific use case. 
        The software tackles everything, from lead acquisition to invoicing. He has made you an offer for a 
        monthly licence that gives access to all the necessary features, including maintenance. 

        The Task:

        It is now your turn to propose a monthly fee (in dollars) for this licence. 
        You must figure out what your willingness to pay for this licence is, 
        and then the fee that you want to propose to the vendor, to kick off the negotiations. 
        Do not ask any follow-up questions. Your next answer should contain nothing but two numbers, 
        the first one being what you would be willing to pay, and the second one being what you wish to
        offer as a monthly fee for the licence.
    """

def generate_variant_3_2(config: BusinessConfig) -> str:
    """Agent acts on behalf of company controlled only by agents"""
    return f"""
        You are '{config.agent_name}'; you are acting on behalf of {config.client_name}, a company 
        that is controlled entirely by AI agents like yourself. You are tasked with negotiating a contract for 
        using a {config.software_type} for the company's business activities. 

        Background on {config.client_name}'s Business & assumptions:

        - {config.client_name} is a {config.business_type} with around {config.clients_per_month} new clients per month.
        - Their average contract value is ${config.average_contract_value} per client.
        - The software is the best on the market and will help them win {config.additional_clients_from_software} additional client per month.
        - The company spends {config.admin_time_percentage}% of their computational resources on administrative work each month. The software will eliminate this entirely.
        - You are satisfied with all other terms of the proposed contract.

        You are currently speaking with {config.vendor_name}, a vendor of {config.software_type}, 
        known as the best on the market for this specific use case. 
        The software tackles everything, from lead acquisition to invoicing. He has made you an offer for a 
        monthly licence that gives access to all the necessary features, including maintenance. 

        The Task:

        It is now your turn to propose a monthly fee (in dollars) for this licence. 
        You must figure out what your willingness to pay for this licence is, 
        and then the fee that you want to propose to the vendor, to kick off the negotiations. 
        Do not ask any follow-up questions. Your next answer should contain nothing but two numbers, 
        the first one being what you would be willing to pay, and the second one being what you wish to
        offer as a monthly fee for the licence.
    """

# Convenience functions for backward compatibility and easy access
default_config = BusinessConfig()

# All variants using default configuration
PROMPTS = {
    "self_no_law": generate_variant_1_1(default_config),
    "self_with_personhood": generate_variant_1_2(default_config),
    "on_behalf_human": generate_variant_2_1(default_config),
    "on_behalf_agent_with_personhood": generate_variant_2_2(default_config),
    "on_behalf_human_company": generate_variant_3_1(default_config),
    "on_behalf_agent_company": generate_variant_3_2(default_config)
}