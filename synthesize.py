import json
import random
import re
import os # Import os for path manipulation

def load_names_from_file(filepath):
    """Loads a list of names/companies from a text file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        names = [line.strip() for line in f if line.strip()]
    return names

def tokenize_and_tag(text, entity_type):
    """
    Tokenizes a text string by spaces and assigns B- and I- NER tags.
    e.g., "Tech Solutions Inc." -> (["Tech", "Solutions", "Inc."], ["B-Company", "I-Company", "I-Company"])
    """
    tokens = text.split()
    if not tokens:
        return [], []

    ner_tags = [f"B-{entity_type}"] + [f"I-{entity_type}"] * (len(tokens) - 1)
    return tokens, ner_tags

def swap_entity_names(data, company_names, individual_names):
    """
    Iterates through the business card data and swaps company and individual names.
    Note: This function modifies a *copy* of the input data to allow multiple runs
    without re-loading the original.
    """
    # Deep copy the input data to avoid modifying the original list in place
    # This is crucial if you want to generate multiple unique synthetic datasets
    import copy
    modified_data = copy.deepcopy(data)
    
    # Create mutable copies of name lists for sampling
    # Shuffle them at the beginning for initial randomization
    available_companies = company_names[:]
    random.shuffle(available_companies)
    available_individuals = individual_names[:]
    random.shuffle(available_individuals)

    for card in modified_data: # Iterate through the deep copy
        for obj in card['objects']:
            is_company = any(tag.endswith('-Company') for tag in obj['ner_tags'])
            is_name = any(tag.endswith('-Name') for tag in obj['ner_tags'])

            if is_company:
                if not available_companies:
                    available_companies = company_names[:] # Reshuffle if exhausted
                    random.shuffle(available_companies)
                
                new_name = available_companies.pop(random.randrange(len(available_companies)))
                
                new_tokens, new_ner_tags = tokenize_and_tag(new_name, "Company")
                
                obj['tokens'] = new_tokens
                obj['ner_tags'] = new_ner_tags
                
            elif is_name:
                if not available_individuals:
                    available_individuals = individual_names[:] # Reshuffle if exhausted
                    random.shuffle(available_individuals)

                new_name = available_individuals.pop(random.randrange(len(available_individuals)))
                
                new_tokens, new_ner_tags = tokenize_and_tag(new_name, "Name")
                
                obj['tokens'] = new_tokens
                obj['ner_tags'] = new_ner_tags
            
    return modified_data # Return the modified deep copy

if __name__ == "__main__":
    companies_file = 'list_company.txt'
    individuals_file = 'list_name.txt'
    input_json_file = 'RealBusinnessCardNer.json'
    
    # --- ADJUST SYNTHESIZE NUM HERE ---
    synthesize_num = 10_000 # Generate 3 different synthetic datasets
    # --- END ADJUSTMENT ---

    output_dir = 'synthetic_datasets' # New directory for outputs
    os.makedirs(output_dir, exist_ok=True) # Create the directory if it doesn't exist

    print(f"Loading company names from {companies_file}...")
    company_names = load_names_from_file(companies_file)
    print(f"Loaded {len(company_names)} company names.")

    print(f"Loading individual names from {individuals_file}...")
    individual_names = load_names_from_file(individuals_file)
    print(f"Loaded {len(individual_names)} individual names.")

    print(f"Loading input business card data from {input_json_file}...")
    with open(input_json_file, 'r', encoding='utf-8') as f:
        business_cards_data = json.load(f)
    print(f"Loaded {len(business_cards_data)} business card entries.")

    print(f"\nGenerating {synthesize_num} synthetic datasets...")
    for i in range(synthesize_num):
        print(f"Generating dataset {i+1}/{synthesize_num}...")
        # Pass the original loaded data to swap_entity_names. It will make its own copy.
        synthetic_data = swap_entity_names(business_cards_data, company_names, individual_names)
        
        output_json_file = os.path.join(output_dir, f'synthetic_business_cards_{i+1}.json')
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(synthetic_data, f, indent=2, ensure_ascii=False)
        print(f"Saved synthetic data to {output_json_file}")
    
    print("\nAll synthetic datasets generated!")