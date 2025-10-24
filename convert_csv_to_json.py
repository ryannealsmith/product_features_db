import csv
import json
import argparse
import random
from collections import defaultdict
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# --- Configuration & Defaults ---
DATE_FORMAT = '%m/%d/%Y'
CURRENT_DATE = datetime.now().date()
DEFAULT_MIN_TRL = 1

# Default file paths
DEFAULT_PF_CSV = 'example-csvs/product_features.csv'
DEFAULT_CA_CSV = 'example-csvs/capabilities_to_product_features.csv'
DEFAULT_TF_CSV = 'example-csvs/capability_to_tech.csv'
DEFAULT_OUTPUT_JSON = 'repository_update_data_final.json'

# --- Utilities ---

def get_random_subset(collection, min_count=2, max_count=5):
    """Randomly selects a subset of capability labels."""
    all_labels = list(collection.keys())
    
    # Ensure the random subset size doesn't exceed the total number of capabilities
    if not all_labels:
        return []
    
    # Determine a random size for the subset
    subset_size = random.randint(min_count, min(max_count, len(all_labels)))
    
    # Select a random subset of labels without replacement
    return random.sample(all_labels, subset_size)

def get_capability_dates(cap_label, ca_list):
    """Retrieves the planned start and end dates for a given capability label."""
    for cap_entity in ca_list:
        if cap_entity.get('label') == cap_label:
            # Note: Dates are stored as strings in YYYY-MM-DD format
            return cap_entity.get('planned_start_date'), cap_entity.get('planned_end_date')
    return None, None

def get_start_and_end_dates_from_product_features(pf_labels, product_features_raw):
    """Get start / end dates for product features."""

    min_start_date = date(9999, 12, 31)  # Initialize with a date far in the future
    max_end_date = date(1, 1, 1)         # Initialize with a date far in the past 

    for pf_label in pf_labels:

        # IMPORTANT: Make sure this value exists!
        if pf_label not in product_features_raw:
            print("WARNING: Could not find " + pf_label + " in product "
                  "features. This means it is linked in a capability, but "
                  "does not actually exist in the product features.")
            continue

        # 1. Get the date string from the raw data
        start_date_str = product_features_raw[pf_label]['start_date']
        end_date_str = product_features_raw[pf_label]['end_date']
        
        # 2. Convert the string to a datetime.date object
        try:
            start_date = datetime.strptime(start_date_str, "%m-%d-%Y").date()
        except ValueError:
            # Handle cases where the string might not be a valid date, 
            # or log an error and skip/assign a default.
            print(f"WARNING: Could not parse start_date '{start_date_str}' for feature '{pf_label}'")
            continue # Skip this feature if the date is invalid

        if start_date < min_start_date:
            min_start_date = start_date

        try:
            end_date = datetime.strptime(end_date_str, "%m-%d-%Y").date()
        except ValueError:
            print(f"WARNING: Could not parse end_date '{end_date_str}' for feature '{pf_label}'")
            continue # Skip this feature if the date is invalid

        if end_date > max_end_date:
            max_end_date = end_date

    return min_start_date.strftime("%m-%d-%Y"), max_end_date.strftime("%m-%d-%Y")

# --- Loading and Linking Functions ---

def load_product_features(file_path):
    """Loads product features and initializes TRL."""
    product_features = {}
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            try:
                next(reader) 
            except StopIteration:
                return product_features 
            
            IDX_SWIMLANE = 0
            IDX_LABEL = 1
            IDX_NAME = 2 
            IDX_PLATFORM = 3
            IDX_ODD = 4
            IDX_ENVIRONMENT = 5
            IDX_TRAILER = 6
            IDX_DETAILS = 7
            IDX_NEXT = 8
            IDX_START_DATE = 10
            IDX_END_DATE = 11

            previous_swimlane = ''
            for row in reader:
                if not row or not row[IDX_NAME].strip():
                    continue

                swimlane = row[IDX_SWIMLANE].strip() or previous_swimlane
                if swimlane != '': previous_swimlane = swimlane

                label = row[IDX_LABEL].strip()
                name = row[IDX_NAME].strip()

                # IMPORTANT: Format the date to min_start_date.strftime("%m-%d-%Y")
                start_date = datetime.strptime(row[IDX_START_DATE].strip(), "%b %Y").date()
                end_date = datetime.strptime(row[IDX_END_DATE].strip(), "%b %Y").date()
                start_date_str = start_date.strftime("%m-%d-%Y")
                end_date_str = end_date.strftime("%m-%d-%Y")

                if label and name:
                    product_features[label] = {
                        'name': name,
                        'label': label,
                        'swimlane': swimlane or '',
                        'platform': row[IDX_PLATFORM].strip() or '',
                        'odd': row[IDX_ODD].strip() or '',
                        'environment': row[IDX_ENVIRONMENT].strip() or '',
                        'trailer': row[IDX_TRAILER].strip() or '',
                        'start_date':  start_date_str,
                        'end_date': end_date_str,
                        'details': row[IDX_DETAILS].strip() or '',
                        'next': row[IDX_NEXT].strip() or 'N', 
                        'capabilities': []
                    }
    except Exception as e:
        print(f"An error occurred while reading {file_path}: {e}")
    return product_features

def load_capabilities(file_path):
    """Loads capabilities."""
    capabilities = {}            
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            try:
                next(reader) 
            except StopIteration:
                return capabilities
                
            IDX_SWIMLANE = 0
            IDX_LABEL = 1
            IDX_NAME = 2 
            IDX_PLATFORM = 3
            IDX_ODD = 4
            IDX_ENVIRONMENT = 5
            IDX_TRAILER = 6
            IDX_DETAILS = 7
            IDX_NEXT = 8
            IDX_PRODUCT_FEATURES_START = 9

            previous_swimlane = ""
            for row in reader:
                if not row or not row[IDX_LABEL].strip():
                    if row and row[IDX_SWIMLANE].strip():
                        current_swimlane = row[IDX_SWIMLANE].strip()
                    continue

                label = row[IDX_LABEL].strip()
                swimlane = row[IDX_SWIMLANE].strip() or previous_swimlane
                if swimlane != '': previous_swimlane = swimlane

                cap_to_pf = []
                for i in range(IDX_PRODUCT_FEATURES_START, len(row)):
                    if row[i].strip():
                        for item in row[i].split('\n'):
                            item = item.strip()
                            if item:
                                pf_label = item.split(' ')[0].strip()
                                cap_to_pf.append(pf_label)

                if len(cap_to_pf) == 0:
                    print("WARNING: Could not find any linked product features "
                          "for capability: " + label + ". Skipping.")
                    continue

                if label:
                    capabilities[label] = {
                        'name': row[IDX_NAME].strip() or '',
                        'swimlane': swimlane,
                        'label': label,
                        'platform': row[IDX_PLATFORM].strip() or '',
                        'odd': row[IDX_ODD].strip() or '',
                        'environment': row[IDX_ENVIRONMENT].strip() or '',
                        'trailer': row[IDX_TRAILER].strip() or '',
                        'next': row[IDX_NEXT].strip() or 'N',
                        'tech_features': [], 
                        'product_features_linked': list(set(cap_to_pf))
                    }

    except Exception as e:
        print(f"An error occurred while reading {file_path}: {e}")
        
    return capabilities

def load_fake_technical_functions(capabilities):
    """Loads technical functions."""
    technical_functions = {}

    idx = 0
    for cap_label, cap_data in capabilities.items():
        label = "TECH-FUNCTION-" + str(idx)
        idx += 1
        technical_functions[label] = {
            'name': label,
            'swimlane': cap_data['swimlane'],
            'label': label,
            'platform': cap_data['platform'] if cap_data['platform'] != 'N/A' else '',
            'odd': cap_data['odd'],
            'environment': cap_data['environment'],
            'trailer': cap_data['trailer'],
            'next': cap_data['next'],
            'capabilities': cap_label
        }

    return technical_functions

# --- Final Transformation Function ---

def construct_repository_update_schema(product_features_raw, 
                                       capabilities_raw, 
                                       technical_functions_raw):
    """
    Constructs the final JSON output following the 'repository update' schema.
    MODIFIED to collect and output entities in the order: PF, TF, CA.
    """
    # Initialize separate lists for reordering
    pf_entities_list = []
    tf_entities_list = []
    ca_entities_list = []

    # To store mapping of product features to capability labels.
    pf_to_cap_labels = defaultdict(list)
    tf_to_cap_labels = defaultdict(list)
    
    # 1. Process Capabilities.
    for cap_label, cap_data in capabilities_raw.items():

        # HACK: If cap lables are empty, then select a random one.
        pf_labels = cap_data['product_features_linked']
        if not pf_labels:
            print(f"INFO: Capability Feature {cap_label} has no linked capabilities. Assigning random subset.")
            # Assign a random subset of 2 to 5 capabilities as a fallback
            pf_labels = get_random_subset(product_features_raw, 2, 5)
        tf_labels = cap_data['tech_features']
        if not tf_labels:
            print(f"INFO: Capability Feature {cap_label} has no linked technical functions. Assigning random subset.")
            tf_labels = get_random_subset(technical_functions_raw, 2, 5)
        
        for pf_label in pf_labels:
            pf_to_cap_labels[pf_label].append(cap_label)
        for tf_label in tf_labels:
            tf_to_cap_labels[tf_label].append(cap_label)

        # IMPORTANT: Get the start / end date from the product features.
        min_start_date, max_end_date = get_start_and_end_dates_from_product_features(
            pf_labels, product_features_raw)
        
        # Find the name of the linked product feature
        product_feature_label = random.choice(list(pf_labels))
        product_feature_name = product_features_raw[product_feature_label]['name']

        cap_entity = {
            "_comment": f"=== CREATING CAPABILITY: {cap_label} ===",
            "entity_type": "capability",
            "operation": "create",
            "name": cap_data['name'],
            "swimlane_decorators": f"{cap_data['swimlane']} - {cap_label}",
            "label": cap_label,
            "vehicle_platform_id": 8,
            "planned_start_date": min_start_date,
            "planned_end_date": max_end_date,
            "tmos": "", 
            "progress_relative_to_tmos": "0.0", 
            "product_feature": product_feature_name,
            "technical_functions": [t['label'] for t in cap_data['tech_features']],
            "product_features": pf_labels, # PF Labels
        }
        ca_entities_list.append(cap_entity)

    # 2. Process Technical Functions (TFs)
    for tf_lable, tf_data in technical_functions_raw.items():

        # Determine all product feature dependencies.
        capabilities = tf_to_cap_labels[tf_label]
        pf_labels = set()
        for pf_label, cap_labels in pf_to_cap_labels.items():
            for cap_label in capabilities:
                if pf_label in product_features_raw:
                    pf_labels.add(pf_label)

        # Find the name of the linked product feature
        product_feature_label = random.choice(list(pf_labels))
        product_feature_name = product_features_raw[product_feature_label]['name']

        # IMPORTANT: Get the start / end date from the product features.
        min_start_date, max_end_date = get_start_and_end_dates_from_product_features(
            pf_labels, product_features_raw)

        tf_entity = {
            "_comment": f"=== CREATING TECHNICAL FUNCTION WITH MULTIPLE DEPENDENCIES ===",
            "entity_type": "technical_function",
            "operation": "create",
            "name": tf_data['name'],
            "description": "",
            "success_criteria": "",
            "vehicle_platform_id": 8,
            "tmos": "",
            "status_relative_to_tmos": "0.0",
            "planned_start_date": min_start_date,
            "planned_end_date": max_end_date,
            "product_feature_dependencies": list(pf_labels),
            "product_feature": product_feature_name,
            "capabilities": capabilities,
            "capability_dependencies": "",
            "document_url": "",
        }
        tf_entities_list.append(tf_entity)
        
    # 3. Process Product Features (PF)
    for pf_label, pf_data in product_features_raw.items():                        
        pf_entity = {
            "_comment": f"=== CREATING PRODUCT FEATURE: {pf_label} ===",
            "entity_type": "product_feature",
            "operation": "create",
            "name": pf_data['name'],
            "description": "",
            "swimlane_decorators": pf_data['swimlane'],
            "label": pf_label,
            "vehicle_platform_id": 8,
            "planned_start_date": pf_data['start_date'],
            "planned_end_date": pf_data['end_date'],
            "active_flag": "next" if pf_data.get('next', '').upper() == 'Y' else 'current',
            "tmos": "",
            "status_relative_to_tmos": "0.0",
            "capabilities_required": cap_labels, # CA Labels
            "document_url": "",
            # "dependencies": dependencies # PF Labels
        }
        pf_entities_list.append(pf_entity)

    # Combine entities in dependency order: PF -> CA -> TF
    entities = pf_entities_list + ca_entities_list + tf_entities_list
    
    # 4. Construct the final output JSON
    output_json = {
        "metadata": {
            "version": "0.0", # Incrementing version
            "description": f"Repository Update Template with reordered entities (PF, CA, TF) for dependency resolution.",
            "created_by": "OCTO",
            "created_date": datetime.now().strftime('%m-%d-%Y'),
            "notes": "Layer cake roadmap of product/capability/technology."
        },
        "entities": entities
    }
    
    return output_json

# --- Main Execution (remains the same) ---

def main():
    """
    Parses command-line arguments, runs the data processing pipeline, and saves the output.
    """
    parser = argparse.ArgumentParser(
        description="Transform three roadmap CSV files into a structured JSON update file, calculating TRLs.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        '--pf-csv',
        type=str,
        default=DEFAULT_PF_CSV,
        help=f"Path to the Product Feature CSV (product_to_capability.csv). Default: {DEFAULT_PF_CSV}"
    )
    parser.add_argument(
        '--ca-csv',
        type=str,
        default=DEFAULT_CA_CSV,
        help=f"Path to the Capabilities CSV (capabilities.csv). Default: {DEFAULT_CA_CSV}"
    )
    parser.add_argument(
        '--tf-csv',
        type=str,
        default=DEFAULT_TF_CSV,
        help=f"Path to the Capability-to-Tech CSV (capability_to_tech.csv). Default: {DEFAULT_TF_CSV}"
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=DEFAULT_OUTPUT_JSON,
        help=f"Path to the output JSON file. Default: {DEFAULT_OUTPUT_JSON}"
    )
    
    args = parser.parse_args()
    
    # 1. Load data from CSVs
    print(f"Starting data processing: {CURRENT_DATE.strftime(DATE_FORMAT)}.")
    product_features_raw = load_product_features(args.pf_csv)
    capabilities_raw = load_capabilities(args.ca_csv)
    technical_functions_raw = load_fake_technical_functions(capabilities_raw)
    
    print("\n--- Final Schema Transformation ---")
    # 2. Transform the intermediate structure into the new repository update schema
    final_data = construct_repository_update_schema(product_features_raw, 
                                                    capabilities_raw, 
                                                    technical_functions_raw)
    print(f"Constructed final data structure with {len(final_data['entities'])} entities.")

    # 3. Output to JSON
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        print(f"\nSuccessfully saved the final repository update schema to {args.output}")
    except Exception as e:
        print(f"\nError saving to JSON file: {e}")

if __name__ == "__main__":
    # Ensure the main execution part is present
    # To run: python your_script_name.py
    main()