#!/usr/bin/env python3
"""
YAML to CSV Converter for Category 3 (Therapeutic Procedures)
This script converts Category 3 YAML rules to CSV format with each item as a row
"""

import yaml
import csv
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

def load_yaml_file(yaml_file_path: str) -> Dict[str, Any]:
    """Load YAML file and return the data"""
    try:
        with open(yaml_file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        print(f"✅ Successfully loaded YAML file: {yaml_file_path}")
        return data
    except Exception as e:
        print(f"❌ Error loading YAML file: {e}")
        raise

def flatten_yaml_to_csv_data(yaml_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert YAML structure to flat CSV data with each item as a row"""
    csv_rows = []
    
    # Extract category information
    category_code = yaml_data.get('category', {}).get('code', '')
    category_name = yaml_data.get('category', {}).get('name', '')
    
    # Process groups
    groups = yaml_data.get('groups', [])
    
    for group in groups:
        group_name = group.get('name', '')
        
        # Process subheadings
        subheadings = group.get('subheadings', [])
        
        for subheading in subheadings:
            subheading_code = subheading.get('code', '')
            mutually_exclusive = subheading.get('mutually_exclusive', False)
            
            # Process items
            items = subheading.get('items', [])
            
            for item in items:
                # Create a row for each item
                row = {
                    'category_code': category_code,
                    'category_name': category_name,
                    'group_name': group_name,
                    'subheading_code': subheading_code,
                    'mutually_exclusive': mutually_exclusive,
                    'item_num': item.get('item_num', ''),
                    'provider': item.get('provider', ''),
                    'treatment_location': item.get('treatment_location', ''),
                    'therapy_type': item.get('therapy_type', ''),
                    'treatment_for': item.get('treatment_for', ''),
                    'treatment_course': item.get('treatment_course', ''),
                    'patient_eligibility': item.get('patient_eligibility', ''),
                    'restriction_diagnoses': item.get('restriction_diagnoses', ''),
                    'restriction_exclusions': item.get('restriction_exclusions', ''),
                    'not_with_items': _format_not_with_items(item.get('not_with_items')),
                    'start_age': item.get('start_age', ''),
                    'end_age': item.get('end_age', ''),
                    'start_duration': item.get('start_duration', ''),
                    'end_duration': item.get('end_duration', '')
                }
                csv_rows.append(row)
    
    return csv_rows

def _format_not_with_items(not_with_items: Any) -> str:
    """Format not_with_items field for CSV output"""
    if not_with_items is None:
        return ''
    elif isinstance(not_with_items, list):
        return '; '.join(str(item) for item in not_with_items)
    else:
        return str(not_with_items)

def write_csv_file(csv_data: List[Dict[str, Any]], output_csv_path: str):
    """Write CSV data to file"""
    if not csv_data:
        print("❌ No data to write to CSV")
        return
    
    # Get fieldnames from the first row
    fieldnames = list(csv_data[0].keys())
    
    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            writer.writerows(csv_data)
        
        print(f"✅ Successfully wrote CSV file: {output_csv_path}")
        print(f"📊 Total rows written: {len(csv_data)}")
        
    except Exception as e:
        print(f"❌ Error writing CSV file: {e}")
        raise

def convert_yaml_to_csv(yaml_file_path: str, output_csv_path: str):
    """Main conversion function"""
    print(f"🔄 Converting YAML to CSV...")
    print(f"📁 Input: {yaml_file_path}")
    print(f"📁 Output: {output_csv_path}")
    print("=" * 60)
    
    # Load YAML data
    yaml_data = load_yaml_file(yaml_file_path)
    
    # Convert to CSV format
    print("🔄 Processing YAML structure...")
    csv_data = flatten_yaml_to_csv_data(yaml_data)
    
    if not csv_data:
        print("❌ No data found in YAML file")
        return
    
    print(f"📊 Found {len(csv_data)} items to convert")
    
    # Write CSV file
    print("🔄 Writing CSV file...")
    write_csv_file(csv_data, output_csv_path)
    
    # Print summary
    print("\n🎉 Conversion completed successfully!")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   - Input YAML: {yaml_file_path}")
    print(f"   - Output CSV: {output_csv_path}")
    print(f"   - Total items: {len(csv_data)}")
    print(f"   - CSV columns: {len(csv_data[0].keys()) if csv_data else 0}")

def main():
    """Main function"""
    # Default file paths
    input_yaml = "yaml_rules_llm/category_3_rule.yaml"
    output_csv = "category_3_items.csv"
    
    # Check if input file exists
    if not os.path.exists(input_yaml):
        print(f"❌ Input YAML file not found: {input_yaml}")
        print("Please ensure the file exists or provide a different path.")
        return
    
    # Convert YAML to CSV
    convert_yaml_to_csv(input_yaml, output_csv)

if __name__ == "__main__":
    main()
