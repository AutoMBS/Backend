#!/usr/bin/env python3
"""
YAML to CSV Converter for Category 1 Rules
Converts the category_1_rule.yaml file to a CSV format where each item is a row
and item number is the primary key.
"""

import yaml
import csv
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


def flatten_item_data(item: Dict[str, Any], group_name: str, subheading_code: str, 
                     subheading_mutually_exclusive: bool) -> Dict[str, Any]:
    """
    Flatten the nested item data into a flat dictionary for CSV output.
    
    Args:
        item: The item dictionary from YAML
        group_name: Name of the group
        subheading_code: Code of the subheading
        subheading_mutually_exclusive: Whether the subheading is mutually exclusive
        
    Returns:
        Flattened dictionary with all item data
    """
    flattened = {
        'item_number': item.get('item', ''),
        'group_name': group_name,
        'subheading_code': subheading_code if subheading_code else '',
        'subheading_mutually_exclusive': subheading_mutually_exclusive,
        'service_provider': item.get('service_provider', ''),
        'location': item.get('location', ''),
        'service_summary': item.get('service_summary', ''),
        'duration': item.get('duration', ''),
        'eligibility_age': '',
        'restrictions_gender_not_allowed': '',
        'restrictions_not_with_items': '',
    }
    
    # Handle eligibility - check if it's not None before accessing
    eligibility = item.get('eligibility')
    if eligibility and isinstance(eligibility, dict):
        flattened['eligibility_age'] = eligibility.get('age', '')
    
    # Handle restrictions - check if it's not None before accessing
    restrictions = item.get('restrictions')
    if restrictions and isinstance(restrictions, dict):
        flattened['restrictions_gender_not_allowed'] = restrictions.get('gender_not_allowed', '')
        not_with_items = restrictions.get('not_with_items', [])
        if isinstance(not_with_items, list):
            flattened['restrictions_not_with_items'] = '; '.join(not_with_items) if not_with_items else ''
        else:
            flattened['restrictions_not_with_items'] = str(not_with_items) if not_with_items else ''
    
    return flattened


def extract_items_from_yaml(yaml_file_path: str) -> List[Dict[str, Any]]:
    """
    Extract all items from the YAML file and flatten them.
    
    Args:
        yaml_file_path: Path to the YAML file
        
    Returns:
        List of flattened item dictionaries
    """
    try:
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: File '{yaml_file_path}' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)
    
    items = []
    
    # Extract groups
    groups = data.get('groups', [])
    
    for group in groups:
        group_name = group.get('name', '')
        subheadings = group.get('subheadings', [])
        
        for subheading in subheadings:
            subheading_code = subheading.get('code')
            subheading_mutually_exclusive = subheading.get('mutually_exclusive', False)
            subheading_items = subheading.get('items', [])
            
            for item in subheading_items:
                flattened_item = flatten_item_data(
                    item, group_name, subheading_code, subheading_mutually_exclusive
                )
                items.append(flattened_item)
    
    return items


def write_to_csv(items: List[Dict[str, Any]], output_file_path: str):
    """
    Write the flattened items to a CSV file.
    
    Args:
        items: List of flattened item dictionaries
        output_file_path: Path for the output CSV file
    """
    if not items:
        print("No items found to write to CSV.")
        return
    
    # Get all field names from the first item
    fieldnames = list(items[0].keys())
    
    try:
        with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            
            # Write header
            writer.writeheader()
            
            # Write data rows - clean the data first
            for item in items:
                # Clean the data by removing newlines and extra whitespace
                cleaned_item = {}
                for key, value in item.items():
                    if isinstance(value, str):
                        # Remove newlines and normalize whitespace
                        cleaned_value = value.replace('\n', ' ').replace('\r', ' ').strip()
                        # Replace multiple spaces with single space
                        cleaned_value = ' '.join(cleaned_value.split())
                        cleaned_item[key] = cleaned_value
                    else:
                        cleaned_item[key] = value
                
                writer.writerow(cleaned_item)
                
        print(f"Successfully converted {len(items)} items to CSV file: {output_file_path}")
        
    except IOError as e:
        print(f"Error writing CSV file: {e}")
        sys.exit(1)


def main():
    """Main function to run the conversion."""
    # Input and output file paths
    input_file = "yaml_rules_llm/category_1_rule.yaml"
    output_file = "category_1_items.csv"
    
    print(f"Converting YAML file: {input_file}")
    print(f"Output CSV file: {output_file}")
    print("-" * 50)
    
    # Extract items from YAML
    print("Extracting items from YAML...")
    items = extract_items_from_yaml(input_file)
    
    if not items:
        print("No items found in the YAML file.")
        sys.exit(1)
    
    print(f"Found {len(items)} items")
    
    # Write to CSV
    print("Writing to CSV...")
    write_to_csv(items, output_file)
    
    # Display sample data
    print("\nSample data (first 3 items):")
    print("-" * 50)
    for i, item in enumerate(items[:3]):
        print(f"Item {i+1}:")
        for key, value in item.items():
            print(f"  {key}: {value}")
        print()


if __name__ == "__main__":
    main()
