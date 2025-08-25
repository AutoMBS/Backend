#!/usr/bin/env python3
"""
JSON to YAML Rules Converter using LangChain and OpenAI GPT-4o
This script converts MBS category JSON data to structured YAML rules using LLM assistance.
"""

import json
import yaml
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

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

class ServiceDetails(BaseModel):
    """Service details extracted by LLM"""
    service_provider: str = Field(description="Who provides the service (e.g., GP, specialist, consultant physician)")
    location: str = Field(description="Where the service is provided (e.g., phone, video, facility)")
    service_summary: str = Field(description="Summary of what the service involves (e.g., history taking, consultation)")
    duration: Optional[str] = Field(description="Duration of the service if specified (e.g., at least 20 minutes)")
    
class Eligibility(BaseModel):
    """Eligibility criteria"""
    age: Optional[str] = Field(description="Eligible patient age range or condition")
    
class Restrictions(BaseModel):
    """Restrictions and exclusions"""
    gender_not_allowed: Optional[List[str]] = Field(description="Genders NOT allowed to claim")
    not_with_items: Optional[List[str]] = Field(description="Items that cannot be claimed together with this one")
    
class YAMLItem(BaseModel):
    """YAML item structure"""
    item: str = Field(description="Item number")
    service_provider: str = Field(description="Who provides the service")
    location: str = Field(description="Where the service is provided")
    service_summary: str = Field(description="Summary of what the service involves")
    duration: Optional[str] = Field(description="Duration of the service if specified")
    eligibility: Optional[Eligibility] = Field(description="Eligibility criteria")
    restrictions: Optional[Restrictions] = Field(description="Restrictions and exclusions")

class Subheading(BaseModel):
    """Subheading structure"""
    code: str = Field(description="Subheading code")
    mutually_exclusive: bool = Field(description="Whether items under this subheading are mutually exclusive")
    items: List[YAMLItem] = Field(description="List of items under this subheading")

class Group(BaseModel):
    """Group structure"""
    name: str = Field(description="Group name")
    subheadings: List[Subheading] = Field(description="List of subheadings under this group")

class YAMLRules(BaseModel):
    """Complete YAML rules structure"""
    schema: str = Field(description="Schema version")
    category: Dict[str, str] = Field(description="Category information")
    groups: List[Group] = Field(description="List of groups")

class JSONToYAMLConverter:
    """Converter that uses LLM to transform JSON data to YAML rules"""
    
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
        
        # System prompt for the LLM
        self.system_prompt = """You are an expert medical billing and coding specialist. Your task is to analyze MBS (Medicare Benefits Schedule) item descriptions and extract structured information.

Given an MBS item description, extract the following information and return it as a JSON object:
1. service_provider: Who provides the service (e.g., GP, specialist, consultant physician, nurse, etc.)
2. location: Where the service is provided (e.g., consulting rooms, phone, video, facility, home, etc.)
3. service_summary: A clear summary of what the service involves (e.g., history taking, consultation, examination, management, etc.)
4. duration: Duration if specified (e.g., "at least 20 minutes", "6-20 minutes", etc.)
5. eligibility: Any age or condition eligibility (if mentioned)
6. restrictions: Any gender restrictions or items that cannot be claimed together

Be precise and extract only information that is explicitly stated or clearly implied in the description. If information is not available, use appropriate default values or leave optional fields empty.

IMPORTANT: Return ONLY valid JSON, no markdown formatting, no YAML formatting."""
        
        # Human message template
        self.human_template = """Analyze this MBS item description and extract the required information:

Item Number: {item_number}
Description: {description}

Return a JSON object with the following structure:
{{
  "service_provider": "who provides the service",
  "location": "where the service is provided", 
  "service_summary": "summary of what the service involves",
  "duration": "duration if specified or null",
  "eligibility": {{"age": "age eligibility if any or null"}},
  "restrictions": {{
    "gender_not_allowed": ["list of restricted genders or null"],
    "not_with_items": ["list of restricted items or null"]
  }}
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
            subheading=str(json_item.get("SubHeading", "")),  # Ensure subheading is a string
            description=json_item.get("Description", ""),
            fee=json_item.get("ScheduleFee"),
            provider_type=json_item.get("ProviderType"),
            item_type=json_item.get("ItemType")
        )
    
    def get_llm_extraction(self, item_info: ItemInfo) -> YAMLItem:
        """Use LLM to extract structured information from item description"""
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
                
                # Create YAMLItem with extracted data
                return YAMLItem(
                    item=item_info.item_number,
                    service_provider=extracted_data.get("service_provider", "general_practitioner"),
                    location=extracted_data.get("location", "consulting_rooms"),
                    service_summary=extracted_data.get("service_summary", item_info.description[:100] + "..." if len(item_info.description) > 100 else item_info.description),
                    duration=extracted_data.get("duration"),
                    eligibility=Eligibility(age=extracted_data.get("eligibility", {}).get("age")) if extracted_data.get("eligibility") and isinstance(extracted_data.get("eligibility"), dict) else None,
                    restrictions=Restrictions(
                        gender_not_allowed=extracted_data.get("restrictions", {}).get("gender_not_allowed") if isinstance(extracted_data.get("restrictions"), dict) else None,
                        not_with_items=extracted_data.get("restrictions", {}).get("not_with_items") if isinstance(extracted_data.get("restrictions"), dict) else None
                    ) if extracted_data.get("restrictions") and isinstance(extracted_data.get("restrictions"), dict) else None
                )
                
            except json.JSONDecodeError as json_err:
                print(f"JSON parsing error for item {item_info.item_number}: {json_err}")
                print(f"Raw response: {content}")
                raise
                
        except Exception as e:
            print(f"Error extracting information for item {item_info.item_number}: {e}")
            # Return default structure if LLM fails
            return YAMLItem(
                item=item_info.item_number,
                service_provider="general_practitioner",
                location="consulting_rooms",
                service_summary=item_info.description[:100] + "..." if len(item_info.description) > 100 else item_info.description,
                duration=None,
                eligibility=None,
                restrictions=None
            )
    
    def organize_by_groups_and_subheadings(self, items: List[ItemInfo]) -> Dict[str, Dict[str, List[ItemInfo]]]:
        """Organize items by groups and subheadings"""
        organized = {}
        
        for item in items:
            group = item.group or "Unknown"
            subheading = item.subheading or "Unknown"
            
            # Skip items with missing critical information
            if not group or not subheading:
                print(f"Warning: Skipping item {item.item_number} due to missing group or subheading")
                continue
            
            if group not in organized:
                organized[group] = {}
            
            if subheading not in organized[group]:
                organized[group][subheading] = []
            
            organized[group][subheading].append(item)
        
        return organized
    
    def convert_to_yaml_structure(self, organized_items: Dict[str, Dict[str, List[ItemInfo]]], category_code: str, category_name: str) -> YAMLRules:
        """Convert organized items to YAML structure"""
        groups = []
        
        for group_name, subheadings_dict in organized_items.items():
            subheadings = []
            
            for subheading_code, items_list in subheadings_dict.items():
                # Sort items by item number
                sorted_items = sorted(items_list, key=lambda x: int(x.item_number) if x.item_number.isdigit() else 0)
                
                # Convert items to YAML format using LLM
                yaml_items = []
                for item_info in sorted_items:
                    yaml_item = self.get_llm_extraction(item_info)
                    yaml_items.append(yaml_item)
                
                subheading = Subheading(
                    code=subheading_code,
                    mutually_exclusive=True,  # Default to true for MBS items
                    items=yaml_items
                )
                subheadings.append(subheading)
            
            group = Group(
                name=group_name,
                subheadings=subheadings
            )
            groups.append(group)
        
        return YAMLRules(
            schema="v0.1",
            category={
                "code": category_code,
                "name": category_name
            },
            groups=groups
        )
    
    def convert_category(self, json_file_path: str, output_yaml_path: str, category_code: str, category_name: str, test_mode: bool = False, max_items: int = 10):
        """Convert a category JSON file to YAML rules"""
        print(f"Converting category {category_code} from {json_file_path}")
        
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
        yaml_structure = self.convert_to_yaml_structure(organized, category_code, category_name)
        
        # Convert to YAML string
        yaml_content = yaml.dump(yaml_structure.model_dump(), default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # Write to file
        with open(output_yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        print(f"YAML rules written to {output_yaml_path}")
    
    def convert_all_categories(self, input_dir: str = "extracted_categories", output_dir: str = "yaml_rules_llm"):
        """Convert all category JSON files to YAML rules"""
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(exist_ok=True)
        
        # Category names mapping
        category_names = {
            "1": "Professional Attendance",
            "2": "Diagnostic Procedures and Investigations",
            "3": "Therapeutic Procedures",
            "4": "Diagnostic Imaging",
            "5": "Pathology",
            "6": "Anaesthesia",
            "8": "Other Medical Services"
        }
        
        # Process each category file
        for filename in os.listdir(input_dir):
            if filename.startswith("category_") and filename.endswith(".json"):
                category_code = filename.split("_")[1].split(".")[0]
                
                if category_code in category_names:
                    input_path = os.path.join(input_dir, filename)
                    output_path = os.path.join(output_dir, f"category_{category_code}.yaml")
                    
                    try:
                        self.convert_category(
                            input_path, 
                            output_path, 
                            category_code, 
                            category_names[category_code]
                        )
                    except Exception as e:
                        print(f"Error processing category {category_code}: {e}")

def main():
    """Main function to run the converter"""
    # Print configuration
    Config.print_config()
    
    # Initialize converter
    converter = JSONToYAMLConverter()
    
    # Convert a single category in test mode first
    converter.convert_category(
        f"{Config.INPUT_DIR}/category_1.json",
        f"{Config.OUTPUT_DIR}/category_1_test.yaml",
        "1",
        Config.CATEGORY_NAMES["1"],
        test_mode=Config.TEST_MODE,
        max_items=Config.MAX_TEST_ITEMS
    )
    
    # Uncomment to convert all categories
    # converter.convert_all_categories()

if __name__ == "__main__":
    main()
