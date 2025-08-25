#!/usr/bin/env python3
"""
Age Field Splitter for Category 1 Items CSV
Splits the eligibility_age field into start_age and end_age attributes.
"""

import csv
import re
import sys
from typing import Tuple, Optional


def parse_age_range(age_text: str) -> Tuple[int, int]:
    """
    Parse age text and return start_age and end_age.
    
    Rules:
    - If age is empty or None: start_age = 0, end_age = 200
    - If "less than X" or "under X": start_age = 0, end_age = X
    - If "at least X": start_age = X, end_age = 200
    - If "X to Y": start_age = X, end_age = Y
    - If "X-Y": start_age = X, end_age = Y
    - If single age "X": start_age = X, end_age = X
    
    Args:
        age_text: The age text from CSV
        
    Returns:
        Tuple of (start_age, end_age)
    """
    if not age_text or age_text.strip() == "":
        return 0, 200
    
    age_text = age_text.strip().lower()
    
    # Remove quotes if present
    age_text = age_text.strip('"')
    
    # Pattern for "less than X" or "under X"
    less_than_match = re.search(r'(?:less\s+than|under)\s+(\d+)', age_text)
    if less_than_match:
        end_age = int(less_than_match.group(1))
        return 0, end_age
    
    # Pattern for "at least X"
    at_least_match = re.search(r'at\s+least\s+(\d+)', age_text)
    if at_least_match:
        start_age = int(at_least_match.group(1))
        return start_age, 200
    
    # Pattern for "X to Y" or "X-Y" or "X - Y"
    range_match = re.search(r'(\d+)\s*(?:to|-)\s*(\d+)', age_text)
    if range_match:
        start_age = int(range_match.group(1))
        end_age = int(range_match.group(2))
        return start_age, end_age
    
    # Pattern for single age number
    single_age_match = re.search(r'(\d+)', age_text)
    if single_age_match:
        age = int(single_age_match.group(1))
        return age, age
    
    # If no pattern matches, default to full range
    return 0, 200


def process_csv(input_file: str, output_file: str):
    """
    Process the CSV file and split age fields.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Get original fieldnames and add new age fields
            fieldnames = list(reader.fieldnames)
            
            # Remove the old eligibility_age field
            if 'eligibility_age' in fieldnames:
                fieldnames.remove('eligibility_age')
            
            # Add new age fields after the original position
            age_position = 8  # Position after duration
            fieldnames.insert(age_position, 'start_age')
            fieldnames.insert(age_position + 1, 'end_age')
            
            # Process rows
            rows = []
            for row in reader:
                # Get the original age value
                original_age = row.get('eligibility_age', '')
                
                # Parse age range
                start_age, end_age = parse_age_range(original_age)
                
                # Create new row with split age fields
                new_row = {}
                for field in fieldnames:
                    if field == 'start_age':
                        new_row[field] = start_age
                    elif field == 'end_age':
                        new_row[field] = end_age
                    elif field != 'eligibility_age':
                        new_row[field] = row.get(field, '')
                
                rows.append(new_row)
            
            # Write output CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"Successfully processed {len(rows)} rows")
            print(f"Input file: {input_file}")
            print(f"Output file: {output_file}")
            
            # Show sample of age parsing
            print("\nAge parsing examples:")
            print("-" * 50)
            sample_ages = [
                "", "less than 20", "under 20", "at least 20", "18 to 65", "18-65", "25", "None"
            ]
            for age in sample_ages:
                start, end = parse_age_range(age)
                print(f"'{age}' -> start_age: {start}, end_age: {end}")
            
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing CSV: {e}")
        sys.exit(1)


def main():
    """Main function."""
    input_file = "category_1_items.csv"
    output_file = "category_1_items_with_age_split.csv"
    
    print("Age Field Splitter for Category 1 Items CSV")
    print("=" * 50)
    
    process_csv(input_file, output_file)
    
    # Show some statistics from the output file
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        print(f"\nOutput file statistics:")
        print(f"Total rows: {len(rows)}")
        
        # Count age ranges
        age_ranges = {}
        for row in rows:
            start = int(row['start_age'])
            end = int(row['end_age'])
            range_key = f"{start}-{end}"
            age_ranges[range_key] = age_ranges.get(range_key, 0) + 1
        
        print(f"Unique age ranges: {len(age_ranges)}")
        print("Top age ranges:")
        for range_key, count in sorted(age_ranges.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {range_key}: {count} items")
            
    except Exception as e:
        print(f"Error reading output file: {e}")


if __name__ == "__main__":
    main()
