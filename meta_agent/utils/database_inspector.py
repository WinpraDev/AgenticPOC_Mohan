"""
Database Inspector
Discovers database schema (tables, columns, relationships) for use in script generation
"""

import os
from typing import Dict, List, Optional
from loguru import logger
import psycopg2
from pydantic import BaseModel, Field


class ColumnInfo(BaseModel):
    """Information about a database column"""
    name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_table: Optional[str] = None


class TableInfo(BaseModel):
    """Information about a database table"""
    name: str
    columns: List[ColumnInfo]
    row_count: int = 0
    primary_key: Optional[str] = None


class DatabaseSchema(BaseModel):
    """Complete database schema information"""
    tables: List[TableInfo]
    relationships: List[Dict[str, str]] = Field(default_factory=list)
    
    def get_table(self, table_name: str) -> Optional[TableInfo]:
        """Get table by name"""
        return next((t for t in self.tables if t.name == table_name), None)
    
    def to_summary(self) -> str:
        """Generate a human-readable summary"""
        lines = ["Database Schema:"]
        for table in self.tables:
            lines.append(f"\nTable: {table.name} ({table.row_count} rows)")
            for col in table.columns:
                pk = " [PK]" if col.is_primary_key else ""
                fk = f" [FK -> {col.foreign_table}]" if col.is_foreign_key else ""
                lines.append(f"  - {col.name}: {col.data_type}{pk}{fk}")
        return "\n".join(lines)


def inspect_database_schema(database_url: Optional[str] = None) -> Optional[DatabaseSchema]:
    """
    Inspect database schema and return structured information
    
    Args:
        database_url: PostgreSQL connection string (if None, uses DATABASE_URL env var)
        
    Returns:
        DatabaseSchema object with tables, columns, and relationships
        None if database is not accessible
    """
    db_url = database_url or os.getenv('DATABASE_URL', '')
    
    if not db_url:
        logger.warning("No DATABASE_URL provided - skipping schema inspection")
        return None
    
    try:
        logger.debug(f"Connecting to database for schema inspection...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Get all tables in public schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        table_names = [row[0] for row in cursor.fetchall()]
        
        if not table_names:
            logger.warning("No tables found in database")
            conn.close()
            return None
        
        tables = []
        relationships = []
        
        for table_name in table_names:
            # Get column information
            cursor.execute("""
                SELECT 
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    CASE WHEN pk.column_name IS NOT NULL THEN TRUE ELSE FALSE END as is_primary_key,
                    CASE WHEN fk.column_name IS NOT NULL THEN TRUE ELSE FALSE END as is_foreign_key,
                    fk.foreign_table_name
                FROM information_schema.columns c
                LEFT JOIN (
                    SELECT ku.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage ku
                        ON tc.constraint_name = ku.constraint_name
                    WHERE tc.table_name = %s
                    AND tc.constraint_type = 'PRIMARY KEY'
                ) pk ON c.column_name = pk.column_name
                LEFT JOIN (
                    SELECT 
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.table_name = %s
                    AND tc.constraint_type = 'FOREIGN KEY'
                ) fk ON c.column_name = fk.column_name
                WHERE c.table_name = %s
                ORDER BY c.ordinal_position
            """, (table_name, table_name, table_name))
            
            columns = []
            primary_key = None
            
            for row in cursor.fetchall():
                col_name, data_type, is_nullable, is_pk, is_fk, foreign_table = row
                
                if is_pk:
                    primary_key = col_name
                
                if is_fk and foreign_table:
                    relationships.append({
                        'from_table': table_name,
                        'from_column': col_name,
                        'to_table': foreign_table
                    })
                
                columns.append(ColumnInfo(
                    name=col_name,
                    data_type=data_type,
                    is_nullable=(is_nullable == 'YES'),
                    is_primary_key=is_pk,
                    is_foreign_key=is_fk,
                    foreign_table=foreign_table
                ))
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            tables.append(TableInfo(
                name=table_name,
                columns=columns,
                row_count=row_count,
                primary_key=primary_key
            ))
        
        cursor.close()
        conn.close()
        
        schema = DatabaseSchema(tables=tables, relationships=relationships)
        logger.debug(f"Schema inspection complete: {len(tables)} tables found")
        
        return schema
        
    except psycopg2.OperationalError as e:
        logger.warning(f"Could not connect to database: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inspecting database schema: {e}")
        return None


def format_schema_for_llm(schema: Optional[DatabaseSchema]) -> str:
    """
    Format schema information for LLM consumption
    
    Returns:
        Formatted string with schema information or message that schema is unavailable
    """
    if not schema:
        return """
DATABASE SCHEMA: Unknown (not connected)
- You don't know the actual column names
- Use SELECT * and cursor.description to discover columns at runtime
- Use dict(zip(columns, row)) pattern to access data safely
"""
    
    lines = ["\n**DATABASE SCHEMA:**"]
    
    for table in schema.tables:
        # Get key columns (PK and FK)
        key_cols = []
        other_cols = []
        for col in table.columns:
            if col.is_primary_key or col.is_foreign_key:
                markers = []
                if col.is_primary_key:
                    markers.append("PK")
                if col.is_foreign_key:
                    markers.append(f"FK→{col.foreign_table}")
                key_cols.append(f"{col.name}[{','.join(markers)}]")
            else:
                other_cols.append(col.name)
        
        # Concise format: table(rows): key_cols | notable_cols...
        notable = other_cols[:8]  # Show more columns
        more = f" +{len(other_cols)-8} more" if len(other_cols) > 8 else ""
        all_cols = key_cols + notable
        lines.append(f"`{table.name}`({table.row_count} rows): {', '.join(all_cols)}{more}")
    
    if schema.relationships:
        lines.append("\n**JOIN INSTRUCTIONS:**")
        for rel in schema.relationships[:5]:  # Show more relationships
            lines.append(f"  • JOIN {rel['to_table']} ON {rel['from_table']}.{rel['from_column']} = {rel['to_table']}.{rel['to_table']}_id")
    
    lines.append("\n**QUERY PATTERN (CRITICAL):**")
    lines.append("```python")
    lines.append("from psycopg2.extras import RealDictCursor")
    lines.append("conn = psycopg2.connect(url, cursor_factory=RealDictCursor)")
    lines.append("# Rows are dicts! Access: row['property_name']")
    lines.append("```")
    
    return "\n".join(lines)

