#!/usr/bin/env python3
"""
Data Filler for Category 3 CSV
This script fills missing values in specific columns of the Category 3 CSV file
"""

import pandas as pd
import os
from pathlib import Path

def fill_missing_values(csv_file_path: str, output_csv_path: str = None):
    """
    Fill missing values in the specified columns:
    - start_age: fill with 0
    - end_age: fill with 200
    - start_duration: fill with 0
    - end_duration: fill with 1000
    """
    
    print(f"🔄 Loading CSV file: {csv_file_path}")
    
    try:
        # Load the CSV file
        df = pd.read_csv(csv_file_path)
        print(f"✅ Successfully loaded CSV file")
        print(f"📊 Original data shape: {df.shape}")
        print(f"📊 Total rows: {len(df)}")
        print(f"📊 Total columns: {len(df.columns)}")
        
        # Check current missing values
        print(f"\n📋 Current missing values:")
        print(f"   - start_age: {df['start_age'].isna().sum()}")
        print(f"   - end_age: {df['end_age'].isna().sum()}")
        print(f"   - start_duration: {df['start_duration'].isna().sum()}")
        print(f"   - end_duration: {df['end_duration'].isna().sum()}")
        
        # Create a copy for modification
        df_filled = df.copy()
        
        print(f"\n🔄 Filling missing values...")
        
        # Fill missing values according to specifications
        df_filled['start_age'] = df_filled['start_age'].fillna(0)
        df_filled['end_age'] = df_filled['end_age'].fillna(200)
        df_filled['start_duration'] = df_filled['start_duration'].fillna(0)
        df_filled['end_duration'] = df_filled['end_duration'].fillna(1000)
        
        print(f"✅ Missing values filled successfully")
        
        # Check filled values
        print(f"\n📋 Missing values after filling:")
        print(f"   - start_age: {df_filled['start_age'].isna().sum()}")
        print(f"   - end_age: {df_filled['end_age'].isna().sum()}")
        print(f"   - start_duration: {df_filled['start_duration'].isna().sum()}")
        print(f"   - end_duration: {df_filled['end_duration'].isna().sum()}")
        
        # Show some statistics about the filled data
        print(f"\n📊 Data statistics after filling:")
        print(f"   - start_age range: {df_filled['start_age'].min()} - {df_filled['start_age'].max()}")
        print(f"   - end_age range: {df_filled['end_age'].min()} - {df_filled['end_age'].max()}")
        print(f"   - start_duration range: {df_filled['start_duration'].min()} - {df_filled['start_duration'].max()}")
        print(f"   - end_duration range: {df_filled['end_duration'].min()} - {df_filled['end_duration'].max()}")
        
        # Determine output file path
        if output_csv_path is None:
            # Create backup of original file and save filled data to original filename
            backup_path = csv_file_path.replace('.csv', '_backup.csv')
            print(f"\n💾 Creating backup of original file: {backup_path}")
            df.to_csv(backup_path, index=False)
            output_csv_path = csv_file_path
        
        # Save the filled data
        print(f"\n💾 Saving filled data to: {output_csv_path}")
        df_filled.to_csv(output_csv_path, index=False)
        
        print(f"✅ Data saved successfully!")
        
        # Show sample of filled data
        print(f"\n📋 Sample of filled data (first 3 rows):")
        print("=" * 80)
        
        sample_columns = ['item_num', 'start_age', 'end_age', 'start_duration', 'end_duration']
        sample_df = df_filled[sample_columns].head(3)
        
        for idx, row in sample_df.iterrows():
            print(f"🔸 Row {idx + 1}:")
            print(f"   Item Number: {row['item_num']}")
            print(f"   Age Range: {row['start_age']} - {row['end_age']}")
            print(f"   Duration Range: {row['start_duration']} - {row['end_duration']} minutes")
            print("-" * 60)
        
        return df_filled
        
    except Exception as e:
        print(f"❌ Error processing CSV file: {e}")
        raise

def main():
    """Main function"""
    
    # File paths
    input_csv = "category_3_items.csv"
    
    # Check if input file exists
    if not os.path.exists(input_csv):
        print(f"❌ Input CSV file not found: {input_csv}")
        print("Please ensure the file exists or provide a different path.")
        return
    
    print(f"🚀 Starting data filling process...")
    print(f"📁 Input file: {input_csv}")
    print("=" * 60)
    
    # Fill missing values
    filled_df = fill_missing_values(input_csv)
    
    print(f"\n🎉 Data filling completed successfully!")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   - Input file: {input_csv}")
    print(f"   - Backup created: {input_csv.replace('.csv', '_backup.csv')}")
    print(f"   - Output file: {input_csv}")
    print(f"   - Total rows processed: {len(filled_df)}")
    print(f"   - Missing values filled: 4 columns")

if __name__ == "__main__":
    main()
