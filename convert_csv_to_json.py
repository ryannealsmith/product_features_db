import csv
import io
import json
import re
import argparse
import sys
from datetime import date, datetime
from collections import defaultdict

def parse_date(date_string):
    """
    Parses date string in 'M/D/YYYY' format for TRL dates.
    Returns date object or None.
    """
    if not date_string or date_string.strip() == '':
        return None
    try:
        # Assuming the M/D/YYYY format based on the sample data
        return datetime.strptime(date_string.strip(), '%m/%d/%Y').date().isoformat()
    except ValueError:
        print(f"Warning: Could not parse TRL date '{date_string}'. Skipping.")
        return None

def parse_capabilities(cap_string, next_string, trailer_string):
    """
    Combines text from Capabilities, Next, and Trailer columns, 
    splits by common delimiters (newline, comma), and extracts CA-XXX codes.
    """
    combined_text = f"{cap_string}\n{next_string}\n{trailer_string}"
    
    # Use a regex to find all codes matching the pattern 'CA-XXX-Y.Z'
    # The pattern is CA- followed by 3 capital letters, a hyphen, a number, a dot, and another number.
    # The 'Capabilities' column in your data is missing a header and is the 10th column (index 9).
    # Based on your data structure:
    # Index 9: CA-CHE...
    # Index 10: CA-PRC... (This is your 'Next' column)
    # Index 11: CA-LOC... (This is your 'Capabilities' column from your prompt's header)
    
    # We will combine columns 9, 10, and 11 based on your provided data structure
    
    # Combine the three capability-related columns (indices 9, 10, 11)
    combined_text = f"{cap_string}\n{next_string}\n{trailer_string}"
    
    # Regular expression to find capability codes (e.g., CA-PRC-1.1, CA-LOC-2.1, CA-CHE-1.1)
    # This specifically looks for CA- followed by an uppercase word, a hyphen, and a number.
    # We strip out the trailing description in parentheses (if present)
    capabilities = re.findall(r'(CA-[A-Z]+-\d\.\d+)', combined_text)
    
    # Clean up and ensure uniqueness
    return sorted(list(set(capabilities)))

def find_min_start_date(entities):
    """Finds the earliest planned_start_date among a list of entities."""
    min_date = None
    for entity in entities:
        date_str = entity.get('planned_start_date')
        if date_str:
            try:
                current_date = date.fromisoformat(date_str)
                if min_date is None or current_date < min_date:
                    min_date = current_date
            except ValueError:
                # Ignore unparsable dates
                pass
    return min_date.isoformat() if min_date else ""

def find_max_end_date(entities):
    """Finds the latest planned_end_date among a list of entities."""
    max_date = None
    for entity in entities:
        date_str = entity.get('planned_end_date')
        if date_str:
            try:
                current_date = date.fromisoformat(date_str)
                if max_date is None or current_date > max_date:
                    max_date = current_date
            except ValueError:
                # Ignore unparsable dates
                pass
    return max_date.isoformat() if max_date else ""
    

def extract_dependencies(label, detail_string):
    """
    Extracts explicit PF-XXX-Y.Z dependencies from the Details column 
    AND infers dependencies on all preceding minor versions within the same major version.
    """
    
    # 1. Explicit Dependencies (from the Details column)
    explicit_deps = re.findall(r'(PF-[A-Z]+-\d\.\d+)', detail_string)
    
    # 2. Inferred Dependencies (Based on the current label)
    inferred_deps = set()
    
    # Check if the label matches the expected format (PF-XXX-Y.Z)
    # Group 1: Prefix (PF-ODD)
    # Group 2: Major Version (1)
    # Group 3: Minor Version (3)
    match = re.match(r'(PF-[A-Z]+)-(\d+)\.(\d+)', label)
    
    if match:
        prefix = match.group(1)       # e.g., 'PF-ODD'
        major_version = match.group(2) # e.g., '1' (kept as string for reassembly)
        minor_version = int(match.group(3)) # e.g., 3
        
        # If the minor version is > 1, infer dependencies on all preceding minor versions
        if minor_version > 1:
            for i in range(1, minor_version):
                # The inferred dependency is prefix-major.i
                # e.g., for PF-ODD-1.3, this generates PF-ODD-1.1 and PF-ODD-1.2
                inferred_dep_label = f"{prefix}-{major_version}.{i}"
                inferred_deps.add(inferred_dep_label)
                
    # 3. Combine and clean
    all_dependencies = set(explicit_deps)
    all_dependencies.update(inferred_deps)
    
    return sorted(list(all_dependencies))
    

def propagate_tf_dates_to_capabilities(tech_entities, cap_entities):
    """
    Rolls up TRL dates from Technical Functions (TF) to their linked Capabilities (CA).
    The CA's start/end dates become the min/max dates of all linked TFs.
    """
    print("\n--- Starting Date Propagation: TF to CA ---")
    
    # 1. Build a map of CA Label -> [List of linked TF Entities]
    ca_to_tf_list = defaultdict(list)
    
    # Use tech_entities (which has the planned dates) and their 'capabilities' list
    for tf_entity in tech_entities:
        for ca_label in tf_entity.get('capabilities', []):
            ca_to_tf_list[ca_label].append(tf_entity)

    # 2. Update Capability entities
    for ca_entity in cap_entities:
        ca_label = ca_entity.get('label')
        linked_tfs = ca_to_tf_list.get(ca_label, [])
        
        if linked_tfs:
            # Calculate min start date among linked TFs
            min_start = find_min_start_date(linked_tfs)
            
            # Calculate max end date among linked TFs
            max_end = find_max_end_date(linked_tfs)
            
            if min_start:
                ca_entity['planned_start_date'] = min_start
                # print(f"UPDATED: CA {ca_label} start date to {min_start}")
            if max_end:
                ca_entity['planned_end_date'] = max_end
                # print(f"UPDATED: CA {ca_label} end date to {max_end}")
        
    print("--- Date Propagation: TF to CA Complete ---")
    

def propagate_cap_dates_to_product_features(cap_entities, pf_entities):
    """
    Rolls up calculated dates from Capabilities (CA) to their linked Product Features (PF).
    The PF's start/end dates become the min/max dates of all required CAs.
    """
    print("--- Starting Date Propagation: CA to PF ---")

    # 1. Build a map of CA Label -> CA Entity (for easy date lookup)
    ca_lookup = {entity['label']: entity for entity in cap_entities}

    # 2. Update Product Feature entities
    for pf_entity in pf_entities:
        # 'capabilities_required' holds the CA labels linked to this PF
        required_ca_labels = pf_entity.get('capabilities_required', [])
        
        # Get the actual CA entities needed
        linked_ca_entities = [ca_lookup[label] for label in required_ca_labels if label in ca_lookup]
        
        if linked_ca_entities:
            # Calculate min start date among required CAs
            min_start = find_min_start_date(linked_ca_entities)
            
            # Calculate max end date among required CAs
            max_end = find_max_end_date(linked_ca_entities)
            
            if min_start:
                pf_entity['planned_start_date'] = min_start
                # print(f"UPDATED: PF {pf_entity['label']} start date to {min_start}")
            if max_end:
                pf_entity['planned_end_date'] = max_end
                # print(f"UPDATED: PF {pf_entity['label']} end date to {max_end}")

    print("--- Date Propagation: CA to PF Complete ---")


def transform_product_feature_csv_to_json(filename):
    """
    Reads the CSV data, transforms each row into a JSON entity, and returns a list of dictionaries.
    """
    
    # The input data has 13 columns used before empty ones, let's map the relevant ones:
    # Swimlane: 0, Label: 1, Product Feature: 2, Details: 7, Next: 9, Capabilities: 10, Trailer: 11
    
    # NOTE: The provided header/data mapping is inconsistent in your prompt.
    # Based on the provided data:
    # Index 8 (column 'Next') = Y/N flag
    # Index 9 (column 'Capabilities' in your header) = CA-CHE...
    # Index 10 (Unnamed column) = CA-PRC...
    # Index 11 (Unnamed column) = CA-LOC...
    
    # We will assume:
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Index: | 0          | 1     | 2               | 3      | 4   | 5           | 6       | 7       | 8    | 9           | 10         | 11       | (12+)
    # Header:| Swimlane   | Label | Product Feature | ...    | ... | ...         | ...     | Details | Next | Capabilities| Unnamed-10 | Unnamed-11| ...
    # Content:
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Row 2: | Operational| PF... | Port: baseline  | N/A    | N/A | N/A         | N/A     | * Speed | Y    | CA-CHE...   | CA-PRC...  | CA-LOC...|
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    # We will use columns 9, 10, and 11 for the capabilities list.
    
    # Use 'with open' to ensure the file is properly closed, 
    # and 'newline=""' to prevent extra blank rows on some systems.
    # The 'encoding="utf-8"' is good practice for text files.
    output_entities = []
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as csvfile:
            
            # Use csv.reader to handle complex/multiline CSV fields correctly
            reader = csv.reader(csvfile)
            
            # Skip the header row
            header = next(reader)
            
            for row in reader:
                # Skip empty rows or rows that don't start with a label (column 1)
                if not row or not row[1]:
                    continue
                    
                # Extract/Clean simple fields
                swimlane = row[0].strip() or "N/A"
                label = row[1].strip()
                name = row[2].strip()
                details = row[7].strip()
                active_flag_val = "next" if row[8].strip() == "Y" else "N/A"

                pf_vehicle_type = row[3].strip() if len(row) > 3 else "N/A"
                
                # Capability columns (Indices 9, 10, and 11 based on your data)
                cap_col_9 = row[9].strip() if len(row) > 9 else ""
                cap_col_10 = row[10].strip() if len(row) > 10 else ""
                cap_col_11 = row[11].strip() if len(row) > 11 else ""
                
                # Derive complex fields
                capabilities_required = parse_capabilities(cap_col_9, cap_col_10, cap_col_11)
                dependencies = extract_dependencies(label, details)
                
                # Construct the JSON entity dictionary
                entity = {
                    "_comment": f"=== CREATING PRODUCT FEATURE: {name} ===",
                    "entity_type": "product_feature",
                    "operation": "create",
                    "name": name,
                    "description": details, 
                    "vehicle_type": pf_vehicle_type, 
                    "swimlane_decorators": swimlane.upper().replace(' ', '_') or "N/A",
                    "label": label,
                    "tmos": "TBD: Define TMOS", 
                    "status_relative_to_tmos": 0.0, 
                    "planned_start_date": "", 
                    "planned_end_date": "", 
                    "active_flag": active_flag_val,
                    "capabilities_required": capabilities_required,
                    "dependencies": dependencies
                }
                
                output_entities.append(entity)
                
    except FileNotFoundError:
        print(f"ERROR: The file '{filename}' was not found. Please ensure it is in the correct directory.")
        return []

    return output_entities


def transform_capability_csv_to_json(filename):
    """
    Reads the Capability CSV data from a file, aggregates Product Features for 
    each unique capability, and transforms the data into 'entity_type: capability' objects.
    """
    # Map to store aggregated data: {label: {'name': str, 'product_features': set}}
    capability_map = defaultdict(lambda: {'name': '', 'product_features': set(), 'swimlane': 'N/A'})
    
    current_swimlane = 'N/A'
    
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            # Skip the header row
            try:
                next(reader)
            except StopIteration:
                return []

            for row in reader:
                if not any(row):
                    continue

                if row[0]:
                    current_swimlane = row[0].strip()

                if row[1] and row[1].startswith('CA-'):
                    label = row[1].strip()
                    name = row[2].strip()
                    pf_cell = row[9].strip() if len(row) > 9 else ''

                    platform_raw = row[3].strip() if len(row) > 3 else 'N/A'
                    
                    if not capability_map[label]['name']:
                        capability_map[label]['name'] = name
                        capability_map[label]['swimlane'] = current_swimlane
                        capability_map[label]['platform'] = platform_raw

                    pf_labels_to_add = []
                    
                    if pf_cell:
                        pf_labels_to_add.append(pf_cell) 

                    # Extract PF labels from ODD (index 4) and Environment (index 5)
                    pf_labels_to_add.extend(re.findall(r'(PF-[A-Z]+-\d+\.?\d*)', ' '.join(row[4:6])))
                    
                    for pf_label in pf_labels_to_add:
                        pf_label = pf_label.strip()
                        if pf_label:
                            capability_map[label]['product_features'].add(pf_label)

    except FileNotFoundError:
        print(f"ERROR: The file '{filename}' was not found. Cannot load Capability data.")
        return []

    final_entities = []
    for label, data in capability_map.items():
        entity = {
            "_comment": f"=== CREATING CAPABILITY: {data['name']} ===",
            "entity_type": "capability",
            "operation": "create",
            "name": data['name'],
            "success_criteria": "TBD: Define success criteria",
            "vehicle_type": data['platform'],
            "planned_start_date": "",
            "planned_end_date": "",
            "tmos": "TBD: Define TMOS",
            "progress_relative_to_tmos": 0.0,
            "label": label,
            "swimlane_decorators": data['swimlane'].upper().replace(' ', '_'),
            "technical_functions": [], 
            "product_features": sorted(list(data['product_features']))
        }
        final_entities.append(entity)

    return final_entities


def reconcile_links(pf_entities, cap_entities):
    """
    Updates the 'product_features' list in Capability entities based on the 
    'capabilities_required' list in Product Feature entities.
    """
    
    # 1. Create a quick lookup map for Capability entities
    # { 'CA-TRL-1.3': { ... entity dict ... }, ... }
    cap_lookup = {
        entity['label']: entity 
        for entity in cap_entities 
        if entity.get('entity_type') == 'capability'
    }

    print("\n--- Starting Link Reconciliation ---")
    
    # 2. Iterate through Product Feature entities
    for pf_entity in pf_entities:
        pf_label = pf_entity.get('label')
        # Use 'capabilities_required' as per your cached script's PF entity structure
        required_caps = pf_entity.get('capabilities_required', []) 
        
        if required_caps and pf_label:
            # 3. For each required capability, update the corresponding CA entity
            for ca_label in required_caps:
                if ca_label in cap_lookup:
                    # Get the current set of linked PF labels (convert list to set for easy adding)
                    linked_pfs = set(cap_lookup[ca_label].get('product_features', []))
                    
                    # Add the current PF label if it's not already present
                    if pf_label not in linked_pfs:
                        linked_pfs.add(pf_label)
                        
                        # Update the CA entity's product_features list (convert back to sorted list)
                        cap_lookup[ca_label]['product_features'] = sorted(list(linked_pfs))
                        # print(f"LINK: Added {pf_label} to capability {ca_label}")
                else:
                    print(f"WARNING: Capability {ca_label} required by {pf_label} was not found in the Capability CSV data.")

    print("--- Link Reconciliation Complete ---\n")
    # The cap_entities list is modified in place because dictionaries are mutable.
    return pf_entities + cap_entities

def transform_technical_function_csv_to_json(filename):
    """
    Reads the Tech Function CSV, aggregates by Technical Function (TE-PRC-X.X),
    and determines start/end dates from TRL columns.
    """
    tech_map = defaultdict(lambda: {
        'capabilities': set(),
        'trl_dates': [],
        'label': '',
        'name': ''
    })
    
    tech_entities = []

    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            # Skip header rows (assuming two header rows: names and TRL levels)
            try:
                next(reader) # Skip "Capability,Tech,Date,,"
                trl_header = next(reader) # Skip ",,TRL 4,TRL 7,TRL 9"
            except StopIteration:
                return []
            
            for row in reader:
                if not any(row):
                    continue

                # Indices: 0=Capability Text, 1=Tech Labels, 2=TRL 4 Date, 3=TRL 7 Date, 4=TRL 9 Date
                if len(row) < 5 or not row[1]:
                    continue

                # 1. Extract CAPABILITY and TECH LABELS
                cap_text = row[0].strip()
                tech_labels_raw = row[1].strip()
                
                # Tech labels are often multi-line/space separated
                tech_labels = re.findall(r'(TE-[A-Z]+-\d+\.?\d*)', tech_labels_raw)
                
                # The capability label is often embedded in the text (e.g., CA-PRC-2.1)
                cap_label_match = re.search(r'(CA-[A-Z]+-\d\.\d+)', cap_text)
                cap_label = cap_label_match.group(0) if cap_label_match else None
                
                if not cap_label or not tech_labels:
                    continue
                    
                # 2. Extract and parse DATES
                trl_dates_raw = [row[i].strip() for i in range(2, 5) if len(row) > i]
                parsed_dates = [parse_date(d) for d in trl_dates_raw if parse_date(d)]
                
                # 3. Aggregate data by Technical Function label
                for tech_label in tech_labels:
                    # Update capabilities linked to this tech function
                    tech_map[tech_label]['capabilities'].add(cap_label)
                    tech_map[tech_label]['label'] = tech_label
                    
                    # Update TRL dates list
                    for d in parsed_dates:
                        if d not in tech_map[tech_label]['trl_dates']:
                             tech_map[tech_label]['trl_dates'].append(d)

    except FileNotFoundError:
        print(f"ERROR: The file '{filename}' was not found. Cannot load Technical Function data.")
        return []

    # 4. Generate final Technical Function entities
    for label, data in tech_map.items():
        # Determine Start/End Dates
        all_dates = sorted(data['trl_dates'])
        planned_start_date = all_dates[0] if all_dates else ""
        planned_end_date = all_dates[-1] if all_dates else ""

        entity = {
            "_comment": f"=== CREATING TECHNICAL FUNCTION: {label} ===",
            "entity_type": "technical_function",
            "operation": "create", # Assuming 'create' for now, can be changed to 'update'
            "name": f"Technical Function {label}", # Placeholder name, as name isn't in CSV
            "description": f"Aggregated Technical Function associated with capabilities: {', '.join(data['capabilities'])}", 
            "success_criteria": "TBD: Define success criteria",
            "vehicle_type": "truck", # Placeholder
            "tmos": "TBD: Define TMOS",
            "status_relative_to_tmos": 0.0,
            
            "planned_start_date": planned_start_date, # First TRL date
            "planned_end_date": planned_end_date,   # Last TRL date
            
            "product_feature": "TBD: Link to PF name", # Needs to be linked manually or via a separate source
            "capabilities": sorted(list(data['capabilities'])), # CA-XXX labels
            "product_feature_dependencies": [],
            "capability_dependencies": []
        }
        tech_entities.append(entity)
        
    return tech_entities

def reconcile_tech_links(tech_entities, cap_entities):
    """
    Updates the 'technical_functions' list in Capability entities 
    based on the 'capabilities' list in Technical Function entities.
    """
    # 1. Create a quick lookup map for Capability entities
    cap_lookup = {
        entity['label']: entity 
        for entity in cap_entities 
        if entity.get('entity_type') == 'capability'
    }

    print("--- Starting Technical Function Link Reconciliation ---")
    
    # 2. Iterate through Technical Function entities
    for tf_entity in tech_entities:
        tf_name = tf_entity.get('name')
        tf_label = tf_entity.get('label')
        
        # The CA labels linked to this TF are in the 'capabilities' list
        linked_caps = tf_entity.get('capabilities', []) 
        
        if linked_caps and tf_name:
            # 3. For each linked capability, update the corresponding CA entity
            for ca_label in linked_caps:
                if ca_label in cap_lookup:
                    # Get the current set of linked TFs (convert list to set for easy adding)
                    linked_tfs = set(cap_lookup[ca_label].get('technical_functions', []))
                    
                    # Add the current TF name/label if it's not already present
                    # NOTE: The capability entity expects the TF's *name*, not the label, 
                    # but since the name is a placeholder for now, we'll use the unique label.
                    if tf_label not in linked_tfs:
                        linked_tfs.add(tf_label)
                        
                        # Update the CA entity's technical_functions list
                        cap_lookup[ca_label]['technical_functions'] = sorted(list(linked_tfs))
                else:
                    print(f"WARNING: Capability {ca_label} linked by TF {tf_label} was not found.")

    print("--- Technical Function Link Reconciliation Complete ---")
    
    return tech_entities


def resolve_tf_links(pf_entities, cap_entities, tech_entities):
    """
    Enriches Technical Function (TF) entities by tracing ALL linked Product Features (PFs) 
    through their associated Capabilities (CAs) and populating the dependencies list.
    """
    
    # 1. Build map of PF Label -> PF Name
    # This is necessary because the TF dependency field requires the Name, not the Label.
    pf_label_to_name = {
        pf.get('label'): pf.get('name') 
        for pf in pf_entities if pf.get('entity_type') == 'product_feature'
    }

    # 2. Build map of CA Label -> {set of PF Names}
    ca_to_pf_names = defaultdict(set)
    for ca_entity in cap_entities:
        ca_label = ca_entity.get('label')
        # 'product_features' in CA entity holds PF LABELS (e.g., PF-ODD-1.1)
        pf_labels_linked_to_ca = ca_entity.get('product_features', [])
        
        if ca_label:
            for pf_label in pf_labels_linked_to_ca:
                # Convert the PF Label back to the PF Name before storing
                pf_name = pf_label_to_name.get(pf_label)
                if pf_name:
                    ca_to_pf_names[ca_label].add(pf_name)
                # Note: Warnings about missing PF names are handled here

    print("--- Starting Technical Function Enrichment ---")

    # 3. Iterate over Technical Functions (TF) and collect links
    for tf_entity in tech_entities:
        tf_caps = tf_entity.get('capabilities', [])
        
        # This set will hold ALL unique PF Names linked to this TF
        all_linked_pf_names = set()
        
        for ca_label in tf_caps:
            # Add all PF names linked through this specific capability
            all_linked_pf_names.update(ca_to_pf_names[ca_label])

        # 4. Apply the derived links to the TF entity
        
        # Populate dependencies with all unique PF names found
        tf_entity['product_feature_dependencies'] = sorted(list(all_linked_pf_names))
        
        # Reset primary 'product_feature' field to TBD, as a single source isn't defined by the data
        if not all_linked_pf_names:
            tf_entity['product_feature'] = "TBD: Primary PF Name"
            print(f"WARNING: TF {tf_entity.get('label')} has no linked Product Features.")
        elif len(all_linked_pf_names) == 1:
            # If only one PF is found, we can safely assume it's the primary product_feature
            single_pf_name = list(all_linked_pf_names)[0]
            tf_entity['product_feature'] = single_pf_name
            tf_entity['product_feature_dependencies'] = [] # Clear dependencies since it's the primary field
        else:
            tf_entity['product_feature'] = "TBD: Primary PF Name"

    print("--- Technical Function Enrichment Complete ---")
    
    return tech_entities
    
# ----------------------------------------------------------------------
## MAIN EXECUTION
# ----------------------------------------------------------------------

def transform_data_to_json(pf_csv_path, ca_csv_path, tf_csv_path, output_json_path):
    """
    Main function to orchestrate data transformation, linking, propagation, and saving.
    """
    print(f"Loading Product Features from: {pf_csv_path}")
    print(f"Loading Capabilities from: {ca_csv_path}")
    print(f"Loading Technical Functions from: {tf_csv_path}")

    # 1. Load entities
    pf_entities = transform_product_feature_csv_to_json(pf_csv_path)
    cap_entities = transform_capability_csv_to_json(ca_csv_path)
    tech_entities = transform_technical_function_csv_to_json(tf_csv_path)
    
    # 2. Reconciliation and Linking Steps
    reconcile_links(pf_entities, cap_entities) # PF <-> CA links
    reconcile_tech_links(tech_entities, cap_entities) # CA <-> TF links
    resolve_tf_links(pf_entities, cap_entities, tech_entities) # TF dependencies and primary PF link

    # 3. Date Propagation Steps
    propagate_tf_dates_to_capabilities(tech_entities, cap_entities)
    propagate_cap_dates_to_product_features(cap_entities, pf_entities)
    
    # 4. Combine ALL entities
    all_entities = pf_entities + cap_entities + tech_entities

    # 5. Construct the final top-level JSON structure
    final_output = {
        "metadata": {
            "version": "1.0",
            "description": "Comprehensive Repository Update Template for Product Feature Readiness Database",
            "created_by": "CSV Transformer Script",
            "created_date": date.today().isoformat(),
            "notes": "Generated from combined roadmap CSVs."
        },
        "entities": all_entities
    }
    
    # 6. Save output
    with open(output_json_path, 'w') as f:
        json.dump(final_output, f, indent=4)
        
    print("-" * 60)
    print(f"Successfully processed {len(pf_entities)} PFs, {len(cap_entities)} CAs, {len(tech_entities)} TFs.")
    print(f"Output saved to: {output_json_path}")
    print("-" * 60)


def main():
    """Parses command-line arguments and runs the data transformation."""
    
    # Set default paths based on the user's previous context
    DEFAULT_PF_CSV = 'example-csvs/product_to_capability.csv'
    DEFAULT_CA_CSV = 'example-csvs/capabilities.csv'
    DEFAULT_TF_CSV = 'example-csvs/capability_to_tech.csv'
    DEFAULT_OUTPUT_JSON = 'roadmap_update.json'
    
    parser = argparse.ArgumentParser(
        description="Transform multiple roadmap CSVs into a single structured JSON update file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        '--pf-csv',
        type=str,
        default=DEFAULT_PF_CSV,
        help=f"Path to the Product Feature CSV file (Default: {DEFAULT_PF_CSV})"
    )
    parser.add_argument(
        '--ca-csv',
        type=str,
        default=DEFAULT_CA_CSV,
        help=f"Path to the Capability CSV file (Default: {DEFAULT_CA_CSV})"
    )
    parser.add_argument(
        '--tf-csv',
        type=str,
        default=DEFAULT_TF_CSV,
        help=f"Path to the Capability-to-Tech CSV file (Default: {DEFAULT_TF_CSV})"
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=DEFAULT_OUTPUT_JSON,
        help=f"Path to the output JSON file (Default: {DEFAULT_OUTPUT_JSON})"
    )
    
    args = parser.parse_args()
    
    transform_data_to_json(
        args.pf_csv,
        args.ca_csv,
        args.tf_csv,
        args.output
    )

if __name__ == "__main__":
    main()