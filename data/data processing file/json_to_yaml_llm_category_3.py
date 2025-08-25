#!/usr/bin/env python3
"""
JSON to YAML Rules Converter for Category 3 (Therapeutic Procedures)
This script converts MBS category 3 JSON data to structured YAML rules using LLM assistance.
"""

import json
import yaml
import os
import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path
from tqdm import tqdm
import time

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Import configuration
from config import Config

@dataclass
class ItemInfo:
    """Information extracted from JSON item"""
    item_number: str
    group: str
    subheading: str
    description: str
    fee: Optional[str] = None
    provider_type: Optional[str] = None
    item_type: Optional[str] = None

class TherapeuticItem(BaseModel):
    """Therapeutic item structure for category 3"""
    item_num: Optional[str] = Field(description="Unique MBS item number")
    provider: Optional[str] = Field(description="Healthcare professional delivering the service")
    treatment_location: Optional[str] = Field(description="Location where the treatment is provided")
    therapy_type: Optional[str] = Field(description="Type of therapy or procedure")
    treatment_for: Optional[str] = Field(description="Diseases or conditions targeted by this item")
    treatment_course: Optional[str] = Field(description="Treatment course or regimen (e.g., '6 weeks', '3 cycles', 'ongoing')")
    patient_eligibility: Optional[str] = Field(description="Conditions a patient must meet for eligibility")
    restriction_diagnoses: Optional[str] = Field(description="Diseases or conditions excluded from coverage")
    restriction_exclusions: Optional[str] = Field(description="Other exclusions or restrictions")
    not_with_items: Optional[Union[str, List[str]]] = Field(description="MBS item numbers that cannot be claimed together with this item")
    start_age: Optional[int] = Field(description="Minimum patient age requirement")
    end_age: Optional[int] = Field(description="Maximum patient age limit")
    start_duration: Optional[int] = Field(description="Minimum duration of the service in minutes")
    end_duration: Optional[int] = Field(description="Maximum duration of the service in minutes")

class Subheading(BaseModel):
    """Subheading structure"""
    code: str = Field(description="Subheading identifier within the group")
    mutually_exclusive: bool = Field(description="Whether items under this subheading are mutually exclusive")
    items: List[TherapeuticItem] = Field(description="List of items under this subheading")

class Group(BaseModel):
    """Group structure"""
    name: str = Field(description="Group identifier within the category")
    subheadings: List[Subheading] = Field(description="List of subheadings under this group")

class Category3MetaData(BaseModel):
    """Complete Category 3 meta data structure"""
    schema: str = Field(description="Schema version")
    category: Dict[str, str] = Field(description="Category information")
    groups: List[Group] = Field(description="List of groups")

class JSONToYAMLCategory3Converter:
    """Converter that uses LLM to transform Category 3 JSON data to YAML meta data"""
    
    def __init__(self, api_key: str = None):
        """Initialize the converter with OpenAI API key"""
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        # Validate configuration
        if not Config.validate():
            raise ValueError("Configuration validation failed")
        
        # Initialize OpenAI model
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=Config.OPENAI_TEMPERATURE,
            max_tokens=Config.OPENAI_MAX_TOKENS
        )
        
        # System prompt for the LLM - specialized for therapeutic procedures
        self.system_prompt = """You are an expert medical billing and coding specialist specializing in therapeutic procedures. Your task is to analyze MBS (Medicare Benefits Schedule) item descriptions for Category 3 (Therapeutic Procedures) and extract structured information.

Given an MBS therapeutic procedure description, extract the following information and return it as a JSON object:
1. provider: Who provides the service (e.g., medical practitioner, specialist, nurse, therapist, etc.)
2. treatment_location: Where the treatment is provided (e.g., hospital, clinic, home, hyperbaric chamber, etc.)
3. therapy_type: The specific type of therapy or procedure (e.g., hyperbaric oxygen therapy, dialysis, assisted reproductive technology, etc.)
4. treatment_for: What diseases or conditions this treatment targets (e.g., decompression illness, end-stage renal disease, infertility, etc.)
5. treatment_course: Treatment course or regimen if specified (e.g., "6 weeks", "3 cycles", "ongoing", "monthly", etc.)
6. patient_eligibility: Any specific patient eligibility criteria (e.g., age requirements, medical conditions, etc.)
7. restriction_diagnoses: Any diseases or conditions excluded from coverage
8. restriction_exclusions: Any other exclusions or restrictions (e.g., gender restrictions, facility restrictions, etc.)
9. not_with_items: MBS item numbers that cannot be claimed together with this item (e.g., ["item 13870", "item 13873"] or "item 13901")
10. start_age: Minimum patient age if specified (as integer)
11. end_age: Maximum patient age if specified (as integer)
12. start_duration: Minimum duration in minutes if specified (as integer)
13. end_duration: Maximum duration in minutes if specified (as integer)

Be precise and extract only information that is explicitly stated or clearly implied in the description. If information is not available, use null for optional fields.

IMPORTANT: Return ONLY valid JSON, no markdown formatting, no YAML formatting."""
        
        # Human message template
        self.human_template = """Analyze this MBS therapeutic procedure item description and extract the required information:

Item Number: {item_number}
Description: {description}

Return a JSON object with the following structure:
{{
  "provider": "who provides the service",
  "treatment_location": "where the treatment is provided",
  "therapy_type": "type of therapy or procedure",
  "treatment_for": "diseases or conditions targeted",
  "treatment_course": "treatment course or regimen or null",
  "patient_eligibility": "patient eligibility criteria or null",
  "restriction_diagnoses": "excluded conditions or null",
  "restriction_exclusions": "other exclusions or restrictions or null",
  "not_with_items": ["list of item numbers"] or "single item number" or null,
  "start_age": minimum_age_integer_or_null,
  "end_age": maximum_age_integer_or_null,
  "start_duration": minimum_duration_minutes_or_null,
  "end_duration": maximum_duration_minutes_or_null
}}

IMPORTANT: Return ONLY valid JSON, no additional text or formatting."""
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", self.human_template)
        ])
    
    def extract_item_info(self, json_item: Dict[str, Any]) -> ItemInfo:
        """Extract basic item information from JSON"""
        return ItemInfo(
            item_number=json_item.get("ItemNum", ""),
            group=json_item.get("Group", ""),
            subheading=str(json_item.get("SubHeading", "") if json_item.get("SubHeading") else "General"),
            description=json_item.get("Description", ""),
            fee=json_item.get("ScheduleFee"),
            provider_type=json_item.get("ProviderType"),
            item_type=json_item.get("ItemType")
        )
    
    def get_llm_extraction(self, item_info: ItemInfo) -> TherapeuticItem:
        """Use LLM to extract structured information from therapeutic procedure description"""
        try:
            # Format the prompt
            formatted_prompt = self.prompt.format_messages(
                item_number=item_info.item_number,
                description=item_info.description
            )
            
            # Get LLM response
            response = self.llm.invoke(formatted_prompt)
            
            # Try to extract JSON from the response
            content = response.content.strip()
            
            # Remove markdown formatting if present
            if content.startswith("```json"):
                content = content.split("```json")[1]
            elif content.startswith("```"):
                content = content.split("```")[1]
            
            if content.endswith("```"):
                content = content.rsplit("```", 1)[0]
            
            content = content.strip()
            
            # Parse JSON response
            try:
                extracted_data = json.loads(content)
                
                # Create TherapeuticItem with extracted data
                return TherapeuticItem(
                    item_num=extracted_data.get("item_num") or item_info.item_number,
                    provider=extracted_data.get("provider"),
                    treatment_location=extracted_data.get("treatment_location"),
                    therapy_type=extracted_data.get("therapy_type"),
                    treatment_for=extracted_data.get("treatment_for"),
                    treatment_course=extracted_data.get("treatment_course"),
                    patient_eligibility=extracted_data.get("patient_eligibility"),
                    restriction_diagnoses=extracted_data.get("restriction_diagnoses"),
                    restriction_exclusions=extracted_data.get("restriction_exclusions"),
                    not_with_items=extracted_data.get("not_with_items"),
                    start_age=extracted_data.get("start_age"),
                    end_age=extracted_data.get("end_age"),
                    start_duration=extracted_data.get("start_duration"),
                    end_duration=extracted_data.get("end_duration")
                )
                
            except json.JSONDecodeError as json_err:
                print(f"JSON parsing error for item {item_info.item_number}: {json_err}")
                print(f"Raw response: {content}")
                raise
                
        except Exception as e:
            print(f"Error extracting information for item {item_info.item_number}: {e}")
            # Return default structure if LLM fails
            return TherapeuticItem(
                item_num=item_info.item_number,
                provider=None,
                treatment_location=None,
                therapy_type=None,
                treatment_for=None,
                treatment_course=None,
                patient_eligibility=None,
                restriction_diagnoses=None,
                restriction_exclusions=None,
                not_with_items=None,
                start_age=None,
                end_age=None,
                start_duration=None,
                end_duration=None
            )
    
    def organize_by_groups_and_subheadings(self, items: List[ItemInfo]) -> Dict[str, Dict[str, List[ItemInfo]]]:
        """Organize items by groups and subheadings"""
        organized = {}
        
        for item in items:
            group = item.group or "Unknown"
            subheading = item.subheading or "General"
            
            # Skip items with missing critical information
            if not group:
                print(f"Warning: Skipping item {item.item_number} due to missing group")
                continue
            
            if group not in organized:
                organized[group] = {}
            
            if subheading not in organized[group]:
                organized[group][subheading] = []
            
            organized[group][subheading].append(item)
        
        return organized
    
    def convert_to_yaml_structure(self, organized_items: Dict[str, Dict[str, List[ItemInfo]]]) -> Category3MetaData:
        """Convert organized items to YAML meta data structure"""
        groups = []
        
        # Calculate total number of items for progress tracking
        total_items = sum(
            len(items_list) 
            for subheadings_dict in organized_items.values() 
            for items_list in subheadings_dict.values()
        )
        
        print(f"\n🔄 Starting LLM processing for {total_items} items...")
        print("=" * 60)
        
        processed_items = 0
        start_time = time.time()
        
        for group_name, subheadings_dict in organized_items.items():
            subheadings = []
            
            for subheading_code, items_list in subheadings_dict.items():
                # Sort items by item number
                sorted_items = sorted(items_list, key=lambda x: int(x.item_number) if x.item_number.isdigit() else 0)
                
                # Convert items to YAML format using LLM with progress tracking
                yaml_items = []
                for item_info in tqdm(sorted_items, desc=f"Processing {group_name}-{subheading_code}", leave=False):
                    yaml_item = self.get_llm_extraction(item_info)
                    yaml_items.append(yaml_item)
                    
                    # Progress reporting every 200 items
                    processed_items += 1
                    if processed_items % 200 == 0:
                        elapsed_time = time.time() - start_time
                        avg_time_per_item = elapsed_time / processed_items
                        remaining_items = total_items - processed_items
                        estimated_remaining_time = remaining_items * avg_time_per_item
                        
                        print(f"\n📊 Progress Report:")
                        print(f"   ✅ Processed: {processed_items}/{total_items} items ({processed_items/total_items*100:.1f}%)")
                        print(f"   ⏱️  Elapsed time: {elapsed_time/60:.1f} minutes")
                        print(f"   🚀 Average: {avg_time_per_item:.2f} seconds per item")
                        print(f"   ⏳ Estimated remaining: {estimated_remaining_time/60:.1f} minutes")
                        print("=" * 60)
                
                subheading = Subheading(
                    code=subheading_code,
                    mutually_exclusive=True,  # Default to true for therapeutic procedures
                    items=yaml_items
                )
                subheadings.append(subheading)
            
            group = Group(
                name=group_name,
                subheadings=subheadings
            )
            groups.append(group)
        
        # Final progress report
        total_time = time.time() - start_time
        print(f"\n🎉 Processing Complete!")
        print(f"   ✅ Total items processed: {total_items}")
        print(f"   ⏱️  Total time: {total_time/60:.1f} minutes")
        print(f"   🚀 Average speed: {total_time/total_items:.2f} seconds per item")
        print("=" * 60)
        
        return Category3MetaData(
            schema="v0.1",
            category={
                "code": "3",
                "name": "Therapeutic Procedures"
            },
            groups=groups
        )
    
    def convert_category_3(self, json_file_path: str, output_yaml_path: str, test_mode: bool = False, max_items: int = 10):
        """Convert Category 3 JSON file to YAML meta data"""
        print(f"Converting Category 3 (Therapeutic Procedures) from {json_file_path}")
        
        # Load JSON data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract items
        items_data = data.get('data', [])
        
        # Limit items in test mode
        if test_mode and len(items_data) > max_items:
            print(f"Test mode: Processing only first {max_items} items out of {len(items_data)}")
            items_data = items_data[:max_items]
        
        items = [self.extract_item_info(item) for item in items_data]
        
        print(f"Found {len(items)} items to process")
        
        # Organize by groups and subheadings
        organized = self.organize_by_groups_and_subheadings(items)
        
        # Convert to YAML structure
        yaml_structure = self.convert_to_yaml_structure(organized)
        
        # Convert to YAML string
        yaml_content = yaml.dump(yaml_structure.model_dump(), default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # Write to file
        with open(output_yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        print(f"Category 3 YAML meta data written to {output_yaml_path}")
    
    def convert_with_batch_processing(self, json_file_path: str, output_yaml_path: str, test_mode: bool = False, max_items: int = 10):
        """Convert with batch processing to handle large files efficiently"""
        print(f"Converting Category 3 with batch processing from {json_file_path}")
        
        # Load JSON data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract items
        items_data = data.get('data', [])
        
        # Limit items in test mode
        if test_mode and len(items_data) > max_items:
            print(f"Test mode: Processing only first {max_items} items out of {len(items_data)}")
            items_data = items_data[:max_items]
        
        print(f"Found {len(items_data)} items to process")
        
        # Process in batches with progress bar
        batch_size = Config.BATCH_SIZE
        all_items = []
        total_batches = (len(items_data) + batch_size - 1) // batch_size
        
        print(f"\n🔄 Processing {len(items_data)} items in {total_batches} batches...")
        print("=" * 60)
        
        for i in tqdm(range(0, len(items_data), batch_size), desc="Processing batches", unit="batch"):
            batch = items_data[i:i + batch_size]
            batch_num = i//batch_size + 1
            
            print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} items)")
            
            batch_items = [self.extract_item_info(item) for item in batch]
            all_items.extend(batch_items)
            
            # Progress report for batches
            if batch_num % 5 == 0:  # Report every 5 batches
                processed_items = len(all_items)
                print(f"   ✅ Total items processed so far: {processed_items}")
        
        print(f"\n📊 Batch processing complete! Total items: {len(all_items)}")
        print("=" * 60)
        
        # Organize by groups and subheadings
        organized = self.organize_by_groups_and_subheadings(all_items)
        
        # Convert to YAML structure
        yaml_structure = self.convert_to_yaml_structure(organized)
        
        # Convert to YAML string
        yaml_content = yaml.dump(yaml_structure.model_dump(), default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # Write to file
        with open(output_yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        print(f"Category 3 YAML meta data written to {output_yaml_path}")

def main():
    """Main function to run the Category 3 converter"""
    # Print configuration
    Config.print_config()
    
    # Initialize converter
    converter = JSONToYAMLCategory3Converter()
    
    # Convert Category 3 in test mode first
    converter.convert_category_3(
        f"{Config.INPUT_DIR}/category_3.json",
        f"{Config.OUTPUT_DIR}/category_3_meta_data_generated.yaml",
        test_mode=Config.TEST_MODE,
        max_items=Config.MAX_TEST_ITEMS
    )
    
    # Uncomment to convert with batch processing for large files
    # converter.convert_with_batch_processing(
    #     f"{Config.INPUT_DIR}/category_3.json",
    #     f"{Config.OUTPUT_DIR}/category_3_meta_data_generated.yaml",
    #     test_mode=Config.TEST_MODE,
    #     max_items=Config.MAX_TEST_ITEMS
    # )

if __name__ == "__main__":
    main()
