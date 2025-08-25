#!/usr/bin/env python3
"""
Duration Field Splitter for Category 1 Items CSV
Splits the duration field into start_time and end_time attributes.
Supports both minutes and hours units.
"""

import csv
import re
import sys
from typing import Tuple, Optional


def parse_duration_range(duration_text: str) -> Tuple[int, int]:
    """
    Parse duration text and return start_time and end_time in minutes.
    
    Rules:
    - If duration is empty or None: start_time = 0, end_time = 1000
    - If "less than X minutes": start_time = 0, end_time = X
    - If "less than X hours": start_time = 0, end_time = X * 60
    - If "more than X minutes but not more than Y minutes": start_time = X, end_time = Y
    - If "at least X minutes and less than Y minutes": start_time = X, end_time = Y
    - If "more than X hours but not more than Y hours": start_time = X * 60, end_time = Y * 60
    - If "at least X hours and less than Y hours": start_time = X * 60, end_time = Y * 60
    - If "X to Y minutes": start_time = X, end_time = Y
    - If "X-Y minutes": start_time = X, end_time = Y
    - If single time "X minutes": start_time = X, end_time = X
    - If single time "X hours": start_time = X * 60, end_time = X * 60
    - If "more than X minutes" or "at least X minutes": start_time = X, end_time = 1000
    - If "more than X hours" or "at least X hour(s)": start_time = X * 60, end_time = 1000
    
    Args:
        duration_text: The duration text from CSV
        
    Returns:
        Tuple of (start_time, end_time) in minutes
    """
    if not duration_text or duration_text.strip() == "":
        return 0, 1000
    
    duration_text = duration_text.strip().lower()
    
    # Remove quotes if present
    duration_text = duration_text.strip('"')
    
    # Pattern for "at least X minutes and less than Y minutes" (must come before simple "less than")
    at_least_and_less_match = re.search(r'at\s+least\s+(\d+)\s+minutes?\s+and\s+less\s+than\s+(\d+)\s+minutes?', duration_text)
    if at_least_and_less_match:
        start_time = int(at_least_and_less_match.group(1))
        end_time = int(at_least_and_less_match.group(2))
        return start_time, end_time
    
    # Pattern for "at least X hours and less than Y hours" (must come before simple "less than")
    at_least_and_less_hours_match = re.search(r'at\s+least\s+(\d+)\s+hours?\s+and\s+less\s+than\s+(\d+)\s+hours?', duration_text)
    if at_least_and_less_hours_match:
        start_time = int(at_least_and_less_hours_match.group(1)) * 60
        end_time = int(at_least_and_less_hours_match.group(2)) * 60
        return start_time, end_time
    
    # Pattern for "less than X minutes"
    less_than_minutes_match = re.search(r'less\s+than\s+(\d+)\s+minutes?', duration_text)
    if less_than_minutes_match:
        end_time = int(less_than_minutes_match.group(1))
        return 0, end_time
    
    # Pattern for "less than X hours"
    less_than_hours_match = re.search(r'less\s+than\s+(\d+)\s+hours?', duration_text)
    if less_than_hours_match:
        end_time = int(less_than_hours_match.group(1)) * 60
        return 0, end_time
    
    # Pattern for "more than X minutes but not more than Y minutes"
    range_minutes_match = re.search(r'more\s+than\s+(\d+)\s+minutes?\s+but\s+not\s+more\s+than\s+(\d+)\s+minutes?', duration_text)
    if range_minutes_match:
        start_time = int(range_minutes_match.group(1))
        end_time = int(range_minutes_match.group(2))
        return start_time, end_time
    
    # Pattern for "more than X hours but not more than Y hours"
    range_hours_match = re.search(r'more\s+than\s+(\d+)\s+hours?\s+but\s+not\s+more\s+than\s+(\d+)\s+hours?', duration_text)
    if range_hours_match:
        start_time = int(range_hours_match.group(1)) * 60
        end_time = int(range_hours_match.group(2)) * 60
        return start_time, end_time
    
    # Pattern for "X to Y minutes"
    to_minutes_match = re.search(r'(\d+)\s+to\s+(\d+)\s+minutes?', duration_text)
    if to_minutes_match:
        start_time = int(to_minutes_match.group(1))
        end_time = int(to_minutes_match.group(2))
        return start_time, end_time
    
    # Pattern for "X-Y minutes"
    dash_minutes_match = re.search(r'(\d+)\s*-\s*(\d+)\s+minutes?', duration_text)
    if dash_minutes_match:
        start_time = int(dash_minutes_match.group(1))
        end_time = int(dash_minutes_match.group(2))
        return start_time, end_time
    
    # Pattern for "not more than X minutes" (must come before "more than")
    not_more_than_minutes_match = re.search(r'not\s+more\s+than\s+(\d+)\s+minutes?', duration_text)
    if not_more_than_minutes_match:
        end_time = int(not_more_than_minutes_match.group(1))
        return 0, end_time
    
    # Pattern for "not more than X hours" (must come before "more than")
    not_more_than_hours_match = re.search(r'not\s+more\s+than\s+(\d+)\s+hours?', duration_text)
    if not_more_than_hours_match:
        end_time = int(not_more_than_hours_match.group(1)) * 60
        return 0, end_time
    
    # Pattern for "more than X minutes" or "at least X minutes" (after complex patterns)
    more_than_minutes_match = re.search(r'(?:more\s+than|at\s+least)\s+(\d+)\s+minutes?', duration_text)
    if more_than_minutes_match:
        start_time = int(more_than_minutes_match.group(1))
        return start_time, 1000
    
    # Pattern for "more than X hours" or "at least X hour(s)" (after complex patterns)
    more_than_hours_match = re.search(r'(?:more\s+than|at\s+least)\s+(\d+)\s+hours?', duration_text)
    if more_than_hours_match:
        start_time = int(more_than_hours_match.group(1)) * 60
        return start_time, 1000
    
    # Pattern for single time "X minutes" (must come after "more than" and "at least")
    single_minutes_match = re.search(r'(\d+)\s+minutes?', duration_text)
    if single_minutes_match:
        time = int(single_minutes_match.group(1))
        return time, time
    
    # Pattern for single time "X hours" (must come after "more than" and "at least")
    single_hours_match = re.search(r'(\d+)\s+hours?', duration_text)
    if single_hours_match:
        time = int(single_hours_match.group(1)) * 60
        return time, time
    
    # If no pattern matches, default to full range
    return 0, 1000


def process_csv(input_file: str, output_file: str):
    """
    Process the CSV file and split duration fields.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Get original fieldnames and add new duration fields
            fieldnames = list(reader.fieldnames)
            
            # Remove the old duration field
            if 'duration' in fieldnames:
                fieldnames.remove('duration')
            
            # Add new duration fields after the original position
            duration_position = 7  # Position after service_summary
            fieldnames.insert(duration_position, 'start_time')
            fieldnames.insert(duration_position + 1, 'end_time')
            
            # Process rows
            rows = []
            for row in reader:
                # Get the original duration value
                original_duration = row.get('duration', '')
                
                # Parse duration range
                start_time, end_time = parse_duration_range(original_duration)
                
                # Create new row with split duration fields
                new_row = {}
                for field in fieldnames:
                    if field == 'start_time':
                        new_row[field] = start_time
                    elif field == 'end_time':
                        new_row[field] = end_time
                    elif field != 'duration':
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
            
            # Show sample of duration parsing
            print("\nDuration parsing examples:")
            print("-" * 50)
            sample_durations = [
                "", "less than 20 minutes", "more than 20 minutes but not more than 25 minutes",
                "at least 6 minutes and less than 20 minutes", "more than 20 minutes", "at least 20 minutes", 
                "not more than 20 minutes", "not more than 1 hour", "less than 1 hour", 
                "more than 1 hour but not more than 2 hours", "at least 1 hour and less than 2 hours", 
                "more than 1 hour", "at least 1 hour", "30 minutes", "2 hours", 
                "15 to 30 minutes", "45-60 minutes"
            ]
            for duration in sample_durations:
                start, end = parse_duration_range(duration)
                print(f"'{duration}' -> start_time: {start}, end_time: {end}")
            
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing CSV: {e}")
        sys.exit(1)


def main():
    """Main function."""
    input_file = "category_1_items_with_age_split.csv"
    output_file = "category_1_items_with_duration_split.csv"
    
    print("Duration Field Splitter for Category 1 Items CSV")
    print("=" * 50)
    
    process_csv(input_file, output_file)
    
    # Show some statistics from the output file
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        print(f"\nOutput file statistics:")
        print(f"Total rows: {len(rows)}")
        
        # Count duration ranges
        duration_ranges = {}
        for row in rows:
            start = int(row['start_time'])
            end = int(row['end_time'])
            range_key = f"{start}-{end}"
            duration_ranges[range_key] = duration_ranges.get(range_key, 0) + 1
        
        print(f"Unique duration ranges: {len(duration_ranges)}")
        print("Top duration ranges:")
        for range_key, count in sorted(duration_ranges.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {range_key}: {count} items")
            
    except Exception as e:
        print(f"Error reading output file: {e}")


if __name__ == "__main__":
    main()
