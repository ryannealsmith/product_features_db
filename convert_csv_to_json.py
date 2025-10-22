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
DEFAULT_PF_CSV = 'example-csvs/product_to_capability.csv'
DEFAULT_CA_CSV = 'example-csvs/capabilities.csv'
DEFAULT_TF_CSV = 'example-csvs/capability_to_tech.csv'
DEFAULT_OUTPUT_JSON = 'repository_update_data_final.json'

# --- TRL and Date Calculation Helpers ---

def calculate_trl_for_tech_feature(tech_feature):
    """
    Determines the TRL for a technical feature based on the current date.
    Returns the highest TRL whose due date has passed, otherwise returns DEFAULT_MIN_TRL (1).
    """
    current_trl = DEFAULT_MIN_TRL
    
    trl_to_date = {}
    for date_str, trl in tech_feature.get('due_dates', {}).items():
        try:
            due_date = datetime.strptime(date_str, DATE_FORMAT).date()
            trl_to_date[trl] = due_date
        except ValueError:
            continue
    
    for trl in sorted(trl_to_date.keys(), reverse=True):
        due_date = trl_to_date[trl]
        if CURRENT_DATE >= due_date:
            current_trl = trl
            break
            
    return current_trl

def get_planning_dates(tech_features):
    """
    Calculates planned_start_date (absolute earliest date) and 
    planned_end_date (absolute latest date) from all due dates, ignoring TRL filtering.
    """
    all_dates = []

    unique_tech_features = {t['label']: t for t in tech_features}.values()

    for tech_feature in unique_tech_features:
        for date_str in tech_feature.get('due_dates', {}).keys():
            try:
                current_date_obj = datetime.strptime(date_str, DATE_FORMAT).date()
                all_dates.append(current_date_obj)
            except ValueError:
                continue
    
    earliest_date = min(all_dates) if all_dates else None
    latest_date = max(all_dates) if all_dates else None

    return (
        earliest_date.strftime(DATE_FORMAT) if earliest_date else '',
        latest_date.strftime(DATE_FORMAT) if latest_date else ''
    )

# --- Loading and Linking Functions ---

def load_product_to_capability(file_path):
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
            IDX_CAPABILITIES_START = 9 

            for row in reader:
                if not row or not row[IDX_NAME].strip():
                    continue

                label = row[IDX_LABEL].strip()
                name = row[IDX_NAME].strip()

                if label and name:
                    capability_labels = []
                    for i in range(IDX_CAPABILITIES_START, len(row)):
                        if row[i].strip():
                            for item in row[i].split('\n'):
                                item = item.strip()
                                if item:
                                    cap_label = item.split(' ')[0].strip()
                                    capability_labels.append(cap_label)
                    
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
                        'swimlane': row[IDX_SWIMLANE].strip() or '',
                        'platform': row[IDX_PLATFORM].strip() or '',
                        'odd': row[IDX_ODD].strip() or '',
                        'environment': row[IDX_ENVIRONMENT].strip() or '',
                        'trailer': row[IDX_TRAILER].strip() or '',
                        'details': details,
                        'next': row[IDX_NEXT].strip() or '', 
                        'capabilities_labels': list(set(capability_labels)),
                        'dependencies': list(set(dependencies)), 
                        'capabilities': [],
                        'current_trl': DEFAULT_MIN_TRL 
                    }
    except Exception as e:
        print(f"An error occurred while reading {file_path}: {e}")
    return product_features

def load_capabilities(file_path, product_features):
    """Loads capabilities and initializes TRL."""
    capabilities = {}
    pf_to_cap = defaultdict(list)
    for pf_label, pf_data in product_features.items():
        for cap_label in pf_data['capabilities_labels']:
            pf_to_cap[cap_label].append(pf_label)
            
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

            current_swimlane = ""
            for row in reader:
                if not row or not row[IDX_LABEL].strip():
                    if row and row[IDX_SWIMLANE].strip():
                        current_swimlane = row[IDX_SWIMLANE].strip()
                    continue

                label = row[IDX_LABEL].strip()
                swimlane = row[IDX_SWIMLANE].strip() or current_swimlane
                if swimlane:
                    current_swimlane = swimlane

                if label:
                    capabilities[label] = {
                        'name': row[IDX_NAME].strip() or '',
                        'swimlane': swimlane,
                        'label': label,
                        'platform': row[IDX_PLATFORM].strip() or '',
                        'odd': row[IDX_ODD].strip() or '',
                        'environment': row[IDX_ENVIRONMENT].strip() or '',
                        'trailer': row[IDX_TRAILER].strip() or '',
                        'tech_features': [], 
                        'product_features_linked': pf_to_cap.get(label, []),
                        'current_trl': DEFAULT_MIN_TRL 
                    }

    except Exception as e:
        print(f"An error occurred while reading {file_path}: {e}")
        
    return capabilities

def load_capability_to_tech(file_path, all_capabilities):
    """Loads tech features, due dates, and calculates tech feature TRL."""
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            try:
                header = next(reader)
                trl_row = next(reader)
            except StopIteration:
                return 

            trl_map = {}
            for i in range(2, len(trl_row)):
                trl_level_str = trl_row[i].strip()
                if trl_level_str.upper().startswith('TRL'):
                    try:
                        trl_level = int(trl_level_str.split(' ')[1])
                        trl_map[i] = trl_level 
                    except (IndexError, ValueError):
                        continue

            IDX_CAPABILITY_NAME = 0
            IDX_TECH_LABELS = 1

            for row in reader:
                if not row or not row[IDX_CAPABILITY_NAME].strip():
                    continue

                cap_string = row[IDX_CAPABILITY_NAME].strip()
                if cap_string.startswith('"') and cap_string.endswith('"'):
                    cap_string = cap_string[1:-1]
                
                cap_label = cap_string.split(' ')[0].strip()
                
                if cap_label in all_capabilities:
                    capability = all_capabilities[cap_label]
                    
                    tech_labels_str = row[IDX_TECH_LABELS].strip()
                    tech_labels = []
                    if tech_labels_str:
                        tech_labels = [t.strip() for t in tech_labels_str.split('\n') if t.strip()]
                        tech_labels.extend([t.strip() for t in tech_labels_str.split(',') if t.strip()])
                        tech_labels = list(set(tech_labels)) 

                    for tech_label in tech_labels:
                        due_dates = {}
                        for i, trl in trl_map.items():
                            if i < len(row) and row[i].strip():
                                date_str = row[i].strip()
                                due_dates[date_str] = trl 
                        
                        tech_feature = {
                            'label': tech_label,
                            'due_dates': due_dates,
                        }
                        
                        # Rule 1: Calculate TRL for Technical Feature
                        tech_feature['current_trl'] = calculate_trl_for_tech_feature(tech_feature)
                        
                        capability['tech_features'].append(tech_feature)
                else:
                    pass

    except Exception as e:
        print(f"An error occurred while reading {file_path}: {e}")

def calculate_all_trls(product_features, all_capabilities):
    """
    Calculates Capability TRL (min linked Tech TRL) and Product Feature TRL 
    (min linked Capability TRL).
    """
    # 1. Calculate TRL for Capabilities 
    for cap_label, cap_data in all_capabilities.items():
        linked_tech_trls = [
            tech['current_trl'] 
            for tech in cap_data['tech_features'] 
            if 'current_trl' in tech
        ]
        
        # Rule 2: Capability TRL
        cap_data['current_trl'] = min(linked_tech_trls) if linked_tech_trls else DEFAULT_MIN_TRL

    # 2. Calculate TRL for Product Features 
    for pf_label, pf_data in product_features.items():
        linked_cap_trls = []
        
        for cap_label in pf_data['capabilities_labels']:
            if cap_label in all_capabilities:
                linked_cap_trls.append(all_capabilities[cap_label]['current_trl'])
        
        # Rule 3: Product Feature TRL
        pf_data['current_trl'] = min(linked_cap_trls) if linked_cap_trls else DEFAULT_MIN_TRL

# --- Intermediate Output Structure Function ---

def construct_final_data(product_features, all_capabilities):
    """
    Constructs the intermediate nested data structure, including TRLs.
    """
    final_collection = []
    
    for pf_label, pf_data in product_features.items():
        product_feature_record = {
            'name': pf_data['name'],
            'label': pf_data['label'],
            'swimlane': pf_data['swimlane'],
            'platform': pf_data['platform'],
            'odd': pf_data['odd'],
            'environment': pf_data['environment'],
            'trailer': pf_data['trailer'],
            'details': pf_data['details'],
            'next': pf_data['next'], 
            'current_trl': pf_data['current_trl'], 
            'capabilities': []
        }
        
        for cap_label in pf_data['capabilities_labels']:
            if cap_label in all_capabilities:
                cap_data = all_capabilities[cap_label]
                
                capability_record = {
                    'name': cap_data['name'],
                    'swimlane': cap_data['swimlane'],
                    'label': cap_data['label'],
                    'platform': cap_data['platform'],
                    'odd': cap_data['odd'],
                    'environment': cap_data['environment'],
                    'trailer': cap_data['trailer'],
                    'current_trl': cap_data['current_trl'], 
                    'product_features_linked': cap_data['product_features_linked'], 
                    'tech_features': cap_data['tech_features'] 
                }
                
                if not any(c['label'] == cap_label for c in product_feature_record['capabilities']):
                    product_feature_record['capabilities'].append(capability_record)
        
        product_feature_record['dependencies_raw'] = product_features[pf_label]['dependencies']
        
        final_collection.append(product_feature_record)
        
    return final_collection

# --- Final Transformation Function ---

def construct_repository_update_schema(final_data):
    """
    Constructs the final JSON output following the 'repository update' schema.
    MODIFIED to collect and output entities in the order: PF, TF, CA.
    """
    # Initialize separate lists for reordering
    pf_entities_list = []
    tf_entities_list = []
    ca_entities_list = []

    # 0. Pre-process to gather unique entities and TRL/Name lookups
    all_caps = {}
    all_techs = {}
    pf_label_to_name = {} # Map for PF Name lookup

    # ... (Pre-processing loop remains the same: populating all_caps, all_techs, pf_label_to_name) ...
    for pf_data in final_data:
        pf_label_to_name[pf_data['label']] = pf_data['name']

        for cap_data in pf_data['capabilities']:
            cap_label = cap_data['label']
            if cap_label not in all_caps:
                all_caps[cap_label] = cap_data
            
            for tech_data in cap_data['tech_features']:
                tech_label = tech_data['label']
                if tech_label not in all_techs:
                    current_trl = calculate_trl_for_tech_feature(tech_data) # Calculate TRL on the fly
                    all_techs[tech_label] = {
                        **tech_data,
                        'current_trl': current_trl,
                        'linked_caps': set(),
                        'linked_pfs': set() 
                    }
                all_techs[tech_label]['linked_caps'].add(cap_label)
                all_techs[tech_label]['linked_pfs'].update(cap_data['product_features_linked'])

    # 1. Process Technical Functions (TF) - BEFORE Capabilities
    for tech_label, tech_data in all_techs.items():
        
        first_cap_label = next(iter(tech_data['linked_caps']), None)
        vehicle_type = all_caps[first_cap_label]['platform'] if first_cap_label and all_caps[first_cap_label]['platform'] != 'N/A' else ''
        
        start_date, end_date = get_planning_dates([tech_data])

        linked_pfs_labels = list(tech_data['linked_pfs'])
        linked_pfs_names = [pf_label_to_name.get(label, label) for label in linked_pfs_labels]
        
        primary_pf_name = linked_pfs_names[0] if linked_pfs_names else "TBD: Primary PF Name"

        tech_entity = {
            "_comment": f"=== CREATING TECHNICAL FUNCTION: {tech_label} ===",
            "entity_type": "technical_function",
            "operation": "create",
            "name": tech_label, 
            "description": f"Technical feature supporting TRL advancement for capabilities: {', '.join(tech_data['linked_caps'])}",
            "label": tech_label,
            "vehicle_type": vehicle_type,
            "planned_start_date": start_date,
            "planned_end_date": end_date,
            "tmos": "",
            "status_relative_to_tmos": "0.0",
            "technical_readiness_level": tech_data['current_trl'], 
            "capabilities": list(tech_data['linked_caps']),
            
            # Use single PF NAME for primary field
            "product_feature": primary_pf_name, 
            "product_feature_dependencies": linked_pfs_names, # Use PF NAMES here
        }
        tf_entities_list.append(tech_entity)

    # 2. Process Capabilities (CA) - LAST
    for cap_label, cap_data in all_caps.items():
        start_date, end_date = get_planning_dates(cap_data['tech_features'])

        cap_entity = {
            "_comment": f"=== CREATING CAPABILITY: {cap_label} ===",
            "entity_type": "capability",
            "operation": "create",
            "name": cap_data['name'],
            "swimlane_decorators": f"{cap_data['swimlane']} - {cap_label}",
            "label": cap_label,
            "vehicle_type": cap_data['platform'] if cap_data['platform'] != 'N/A' else '',
            "planned_start_date": start_date,
            "planned_end_date": end_date,
            "tmos": "", 
            "progress_relative_to_tmos": "0.0", 
            "technical_readiness_level": cap_data['current_trl'], 
            "technical_functions": [t['label'] for t in cap_data['tech_features']],
            "product_features": cap_data['product_features_linked'] # PF Labels
        }
        ca_entities_list.append(cap_entity)
        
    # 3. Process Product Features (PF) - FIRST
    for pf_data in final_data:
        pf_label = pf_data['label']
        
        pf_tech_features = [tech for cap in pf_data['capabilities'] for tech in cap['tech_features']]
        start_date, end_date = get_planning_dates(pf_tech_features)
        
        dependencies = []
        pf_prefix, pf_number_str = pf_label.rsplit('-', 1)
        try:
            pf_number = float(pf_number_str)
            for dep_label in pf_data['dependencies_raw']:
                dep_prefix, dep_number_str = dep_label.rsplit('-', 1)
                if dep_prefix == pf_prefix:
                    dep_number = float(dep_number_str)
                    if dep_number < pf_number:
                        dependencies.append(dep_label)
        except ValueError:
            pass 

        pf_entity = {
            "_comment": f"=== CREATING PRODUCT FEATURE: {pf_label} ===",
            "entity_type": "product_feature",
            "operation": "create",
            "name": pf_data['name'],
            "description": pf_data['details'],
            "swimlane_decorators": pf_data['swimlane'],
            "label": pf_label,
            "vehicle_type": pf_data['platform'] if pf_data['platform'] != 'N/A' else '',
            "planned_start_date": start_date,
            "planned_end_date": end_date,
            "active_flag": "next" if pf_data.get('next', '').upper() == 'Y' else 'current',
            "tmos": "",
            "status_relative_to_tmos": "0.0",
            "technical_readiness_level": pf_data['current_trl'], 
            "capabilities_required": [cap['label'] for cap in pf_data['capabilities']], # CA Labels
            "dependencies": dependencies # PF Labels
        }
        pf_entities_list.append(pf_entity)

    # Combine entities in dependency order: PF -> TF -> CA
    entities = pf_entities_list + tf_entities_list + ca_entities_list
    
    # 4. Construct the final output JSON
    output_json = {
        "metadata": {
            "version": "2.4", # Incrementing version
            "description": f"Repository Update Template with reordered entities (PF, TF, CA) for dependency resolution. TRL calculated as of {CURRENT_DATE.strftime(DATE_FORMAT)}.",
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
    
    print(f"Starting data processing. TRL calculated as of {CURRENT_DATE.strftime(DATE_FORMAT)}.")
    
    # 1. Load data from CSVs
    product_features_raw = load_product_to_capability(args.pf_csv)
    all_capabilities_raw = load_capabilities(args.ca_csv, product_features_raw)
    load_capability_to_tech(args.tf_csv, all_capabilities_raw)

    print("\n--- TRL Calculation Phase ---")
    # 2. Calculate dependent TRLs
    calculate_all_trls(product_features_raw, all_capabilities_raw)

    print("\n--- Intermediate Structure Construction ---")
    # 3. Construct the previous final structure (input for the new transformation)
    intermediate_data = construct_final_data(product_features_raw, all_capabilities_raw)
    print(f"Constructed intermediate data structure with {len(intermediate_data)} Product Features.")
    
    print("\n--- Final Schema Transformation ---")
    # 4. Transform the intermediate structure into the new repository update schema
    final_data = construct_repository_update_schema(intermediate_data)
    print(f"Constructed final data structure with {len(final_data['entities'])} entities.")

    # 5. Output to JSON
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