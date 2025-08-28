"""
Database CRUD Operations for Medical Categories
===============================================

This module provides comprehensive database access operations for the Medical
Benefits Schedule (MBS) system. It handles all Create, Read, Update, and Delete
operations for medical categories data stored in SQLite.

Key Features:
- SQLite database connection management
- Medical categories data retrieval
- DataFrame and dictionary format support
- Error handling and connection pooling
- Support for multiple category tables

Database Schema:
- Tables: category_1, category_3, etc.
- Common fields: item_number, service_summary, start_age, end_age, etc.
- Flexible querying with category-specific filtering

Author: Medical Coding Team
Version: 2.0.0
Last Updated: 2025-08-27
"""

import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional


class CRUD:
    """
    Database CRUD operations manager for medical categories.
    
    This class provides a clean interface for all database operations including
    data retrieval, connection management, and error handling. It supports
    both individual category queries and bulk data operations.
    
    Attributes:
        db_path (str): Path to the SQLite database file
        
    Example:
        crud = CRUD("../data/medical_categories.db")
        data = crud.get_category_dataframe("1")
    """
    
    def __init__(self, db_path: str = "data/medical_categories.db"):
        """
        Initialize CRUD manager with database path.
        
        Args:
            db_path (str): Path to the SQLite database file.
                          Defaults to "../data/medical_categories.db"
                          
        Raises:
            Exception: If database path is invalid or inaccessible
        """
        self.db_path = db_path
        
        # Validate database path and accessibility
        try:
            # Test connection on initialization
            test_conn = self.get_db_connection()
            test_conn.close()
        except Exception as e:
            raise Exception(f"Database initialization failed: {str(e)}")
    
    def get_db_connection(self) -> sqlite3.Connection:
        """
        Create and return a database connection with proper configuration.
        
        This method establishes a connection to the SQLite database with
        optimized settings for medical data operations.
        
        Returns:
            sqlite3.Connection: Configured database connection
            
        Raises:
            Exception: If connection cannot be established
            
        Note:
            Connections should be closed by the caller after use
        """
        try:
            # Create connection with row factory for dictionary-like access
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            # Enable foreign keys and optimize for read operations
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            
            return conn
            
        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")
    
    def get_category_data_for_rag(self, category_id: str = "1") -> List[Dict[str, Any]]:
        """
        Retrieve category data optimized for RAG (Retrieval Augmented Generation) training.
        
        This method fetches all records from a specific category table and formats
        them for use in RAG systems. It's optimized for bulk data retrieval.
        
        Args:
            category_id (str): Category identifier (e.g., "1", "3").
                             Defaults to "1" for category_1
                             
        Returns:
            List[Dict[str, Any]]: List of category records as dictionaries
            
        Raises:
            Exception: If category doesn't exist or data retrieval fails
            
        Example:
            data = crud.get_category_data_for_rag("1")
            # Returns: [{"item_number": "123", "service_summary": "..."}, ...]
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Construct table name from category ID
            table_name = f"category_{category_id}"
            
            # Verify table exists before querying
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
                (table_name,)
            )
            if not cursor.fetchone():
                raise Exception(f"Category table '{table_name}' does not exist")
            
            # Retrieve all data from the category table
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Convert rows to dictionary format for easier processing
            data = []
            for row in rows:
                row_dict = dict(row)
                data.append(row_dict)
            
            conn.close()
            return data
            
        except Exception as e:
            raise Exception(f"Failed to retrieve category {category_id} data: {str(e)}")
    
    def get_category_dataframe(self, category_id: str = "1") -> pd.DataFrame:
        """
        Retrieve category data as a pandas DataFrame for data analysis and RAG training.
        
        This method provides a pandas DataFrame interface for category data,
        which is useful for data manipulation, filtering, and analysis.
        
        Args:
            category_id (str): Category identifier (e.g., "1", "3").
                             Defaults to "1" for category_1
                             
        Returns:
            pd.DataFrame: Category data as a pandas DataFrame
            
        Raises:
            Exception: If category doesn't exist or DataFrame creation fails
            
        Example:
            df = crud.get_category_dataframe("1")
            # Returns: DataFrame with columns like item_number, service_summary, etc.
            
        Note:
            The DataFrame includes all columns from the database table
        """
        try:
            conn = self.get_db_connection()
            
            # Construct table name from category ID
            table_name = f"category_{category_id}"
            
            # Verify table exists before querying
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
                (table_name,)
            )
            if not cursor.fetchone():
                raise Exception(f"Category table '{table_name}' does not exist")
            
            # Read data directly into pandas DataFrame
            if category_id == "1":
                df = pd.read_sql_query(f"SELECT * FROM {table_name} LEFT JOIN Extra_Definition on {table_name}.extra_rule_id = Extra_Definition.Rule_ID", conn)
            elif category_id == "3":
                df = pd.read_sql_query(f"""SELECT
                    {table_name}.provider AS service_provider,
                    {table_name}.treatment_location AS location,
                    TRIM(
                        COALESCE({table_name}.therapy_type || ' ', '') ||
                        COALESCE({table_name}.treatment_course || ' ', '') ||
                        COALESCE({table_name}.patient_eligibility, '')
                    ) AS service_summary,
                    {table_name}.start_age,
                    {table_name}.end_age,
                    {table_name}.start_duration AS start_time,
                    {table_name}.end_duration   AS end_time,
                    {table_name}.item_num AS item_number,
                    Extra_Definition.Rule_Description
                    FROM {table_name}
                    LEFT JOIN Extra_Definition
                    ON {table_name}.extra_rule_id = Extra_Definition.Rule_ID;""", conn)
            else:
                raise Exception(f"Category {category_id} is not supported")
            conn.close()
            
            return df
            
        except Exception as e:
            raise Exception(f"Failed to create DataFrame for category {category_id}: {str(e)}")
    
    def get_available_categories(self) -> List[str]:
        """
        Get list of all available category tables in the database.
        
        This method scans the database schema to identify all category-related
        tables, excluding system tables and other non-category tables.
        
        Returns:
            List[str]: List of available category table names
            
        Raises:
            Exception: If database schema query fails
            
        Example:
            categories = crud.get_available_categories()
            # Returns: ["category_1", "category_3", "category_4"]
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Query all table names in the database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            # Filter for category tables only
            category_tables = []
            for table in tables:
                table_name = table[0]
                if (table_name.startswith('category_') and 
                    table_name != 'sqlite_sequence' and
                    not table_name.endswith('_meta')):
                    category_tables.append(table_name)
            
            conn.close()
            return category_tables
            
        except Exception as e:
            raise Exception(f"Failed to retrieve available categories: {str(e)}")
    
    def get_category_statistics(self, category_id: str = "1") -> Dict[str, Any]:
        """
        Get comprehensive statistics for a specific category.
        
        This method provides detailed information about a category including
        record count, field statistics, and data quality metrics.
        
        Args:
            category_id (str): Category identifier (e.g., "1", "3").
                             Defaults to "1" for category_1
                             
        Returns:
            Dict[str, Any]: Dictionary containing category statistics
            
        Raises:
            Exception: If statistics calculation fails
            
        Example:
            stats = crud.get_category_statistics("1")
            # Returns: {"record_count": 667, "fields": {...}, "quality": {...}}
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            table_name = f"category_{category_id}"
            
            # Verify table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
                (table_name,)
            )
            if not cursor.fetchone():
                raise Exception(f"Category table '{table_name}' does not exist")
            
            # Get record count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            record_count = cursor.fetchone()[0]
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Get sample data for field analysis
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
            sample_data = cursor.fetchall()
            
            conn.close()
            
            # Calculate basic statistics
            stats = {
                "category_id": category_id,
                "table_name": table_name,
                "record_count": record_count,
                "columns": [col[1] for col in columns],
                "sample_size": len(sample_data),
                "timestamp": pd.Timestamp.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            raise Exception(f"Failed to calculate statistics for category {category_id}: {str(e)}")
