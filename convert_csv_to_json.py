import csv
import json
import argparse
from collections import defaultdict
from datetime import datetime

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
    
def ignore_swimlane(swimlane):
    return (swimlane == "Operational Environment" or 
            swimlane == "Environmental conditions" or swimlane == "Cargo")

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

            previous_swimlane = ''
            for row in reader:
                if not row or not row[IDX_NAME].strip():
                    continue

                # NOTE: We ignore the the following swimlanes as they are
                #       dependencies:
                #
                # - Operational Environment
                # - Environmental conditions
                # - Cargo
                swimlane = row[IDX_SWIMLANE].strip() or previous_swimlane
                if swimlane != '': previous_swimlane = swimlane
                if ignore_swimlane(swimlane): continue

                label = row[IDX_LABEL].strip()
                name = row[IDX_NAME].strip()

                if label and name:
                    dependencies = []
                    details = row[IDX_DETAILS].strip()
                    if details:
                         for line in details.split('\n'):
                            line = line.strip()
                            if line.startswith('* PF-'):
                                dep_label = line.split(' ')[1].strip()
                                if dep_label.startswith('PF-'):
                                    dependencies.append(dep_label)

                    product_features[label] = {
                        'name': name,
                        'label': label,
                        'swimlane': swimlane or '',
                        'platform': row[IDX_PLATFORM].strip() or '',
                        'odd': row[IDX_ODD].strip() or '',
                        'environment': row[IDX_ENVIRONMENT].strip() or '',
                        'trailer': row[IDX_TRAILER].strip() or '',
                        'details': details,
                        'next': row[IDX_NEXT].strip() or 'N', 
                        'dependencies': list(set(dependencies)), 
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
                # if ignore_swimlane(swimlane): continue

                cap_to_pf = []
                for i in range(IDX_PRODUCT_FEATURES_START, len(row)):
                    if row[i].strip():
                        for item in row[i].split('\n'):
                            item = item.strip()
                            if item:
                                pf_label = item.split(' ')[0].strip()
                                cap_to_pf.append(pf_label)

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

# --- Final Transformation Function ---

def construct_repository_update_schema(product_features_raw, all_capabilities_raw):
    """
    Constructs the final JSON output following the 'repository update' schema.
    MODIFIED to collect and output entities in the order: PF, TF, CA.
    """
    # Initialize separate lists for reordering
    pf_entities_list = []
    tf_entities_list = []
    ca_entities_list = []

    # 1. Process Capabilities (CA) - LAST
    for cap_label, cap_data in all_capabilities_raw.items():
        # start_date, end_date = get_planning_dates(cap_data['tech_features'])

        cap_entity = {
            "_comment": f"=== CREATING CAPABILITY: {cap_label} ===",
            "entity_type": "capability",
            "operation": "create",
            "name": cap_data['name'],
            "swimlane_decorators": f"{cap_data['swimlane']} - {cap_label}",
            "label": cap_label,
            "vehicle_type": cap_data['platform'] if cap_data['platform'] != 'N/A' else '',
            "planned_start_date": "",
            "planned_end_date": "",
            "tmos": "", 
            "progress_relative_to_tmos": "0.0", 
            "technical_functions": [t['label'] for t in cap_data['tech_features']],
            "product_features": cap_data['product_features_linked'] # PF Labels
        }
        ca_entities_list.append(cap_entity)
        
    # 2. Process Product Features (PF) - FIRST
    for pf_label, pf_data in product_features_raw.items():
        cap_labels = []
        for cap_label, cap_data in all_capabilities_raw.items():
            for label in cap_data['product_features_linked']:
                if label == pf_label:
                    cap_labels.append(cap_label)

        pf_entity = {
            "_comment": f"=== CREATING PRODUCT FEATURE: {pf_label} ===",
            "entity_type": "product_feature",
            "operation": "create",
            "name": pf_data['name'],
            "description": "", #pf_data['details'],
            "swimlane_decorators": pf_data['swimlane'],
            "label": pf_label,
            # "vehicle_type": pf_data['platform'] if pf_data['platform'] != 'N/A' else '',
            "vehicle_platform_id": 8,
            "planned_start_date": "",
            "planned_end_date": "",
            "active_flag": "next" if pf_data.get('next', '').upper() == 'Y' else 'current',
            "tmos": "",
            "status_relative_to_tmos": "0.0",
            "capabilities_required": cap_labels, # CA Labels
            "document_url": "",
            # "dependencies": dependencies # PF Labels
        }
        pf_entities_list.append(pf_entity)

    # Combine entities in dependency order: PF -> TF -> CA
    entities = pf_entities_list + ca_entities_list
    
    # 3. Construct the final output JSON
    output_json = {
        "metadata": {
            "version": "2.4", # Incrementing version
            "description": f"Repository Update Template with reordered entities (PF, TF, CA) for dependency resolution.",
            "created_by": "Python Data Processor",
            "created_date": datetime.now().strftime('%Y-%m-%d'),
            "notes": "Entities are now ordered to allow downstream scripts to resolve links on first pass."
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
    # parser.add_argument(
    #     '--tf-csv',
    #     type=str,
    #     default=DEFAULT_TF_CSV,
    #     help=f"Path to the Capability-to-Tech CSV (capability_to_tech.csv). Default: {DEFAULT_TF_CSV}"
    # )
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
    all_capabilities_raw = load_capabilities(args.ca_csv)
    
    print("\n--- Final Schema Transformation ---")
    # 2. Transform the intermediate structure into the new repository update schema
    final_data = construct_repository_update_schema(product_features_raw, all_capabilities_raw)
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