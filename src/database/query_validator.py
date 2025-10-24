import re
from typing import Tuple, List


class QueryValidator:
    """
    Validates SQL queries for safety and correctness
    """
    
    # Dangerous SQL keywords that should be restricted
    DANGEROUS_KEYWORDS = [
        'DROP', 'TRUNCATE', 'ALTER', 'CREATE', 'EXEC', 
        'EXECUTE', 'GRANT', 'REVOKE', 'SHUTDOWN'
    ]
    
    # Allowed SQL operations for different contexts
    READ_ONLY_OPS = ['SELECT']
    WRITE_OPS = ['INSERT', 'UPDATE', 'DELETE']
    DDL_OPS = ['CREATE', 'ALTER', 'DROP', 'TRUNCATE']

    def __init__(self):
        self.allow_ddl = False  # By default, don't allow DDL operations

    def validate_query(self, query: str, allowed_operations: List[str] = None) -> Tuple[bool, str]:
        """
        Validate a SQL query
        Returns: (is_valid, error_message)
        """
        if not query or not query.strip():
            return False, "Empty query"

        query = query.strip()

        # Check for dangerous keywords
        is_dangerous, danger_msg = self._check_dangerous_keywords(query)
        if is_dangerous:
            return False, danger_msg

        # Check if operation is allowed
        if allowed_operations:
            is_allowed, allowed_msg = self._check_allowed_operations(query, allowed_operations)
            if not is_allowed:
                return False, allowed_msg

        # Check for multiple statements
        if self._has_multiple_statements(query):
            return False, "Multiple SQL statements not allowed"

        # Check for comments (potential obfuscation)
        if self._has_suspicious_comments(query):
            return False, "Suspicious SQL comments detected"

        return True, "Query is valid"

    def _check_dangerous_keywords(self, query: str) -> Tuple[bool, str]:
        """Check for dangerous SQL keywords"""
        query_upper = query.upper()
        
        for keyword in self.DANGEROUS_KEYWORDS:
            if re.search(r'\b' + keyword + r'\b', query_upper):
                if keyword in self.DDL_OPS and not self.allow_ddl:
                    return True, f"Dangerous keyword detected: {keyword}"
        
        return False, ""

    def _check_allowed_operations(self, query: str, allowed_operations: List[str]) -> Tuple[bool, str]:
        """Check if the query operation is in the allowed list"""
        query_upper = query.upper().strip()
        
        # Get the first keyword (operation type)
        first_keyword = query_upper.split()[0] if query_upper.split() else ""
        
        if first_keyword not in [op.upper() for op in allowed_operations]:
            return False, f"Operation '{first_keyword}' is not allowed. Allowed: {', '.join(allowed_operations)}"
        
        return True, ""

    def _has_multiple_statements(self, query: str) -> bool:
        """Check if query contains multiple statements"""
        # Simple check for semicolons (excluding those in strings)
        in_string = False
        string_char = None
        
        for i, char in enumerate(query):
            if char in ('"', "'") and (i == 0 or query[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
            elif char == ';' and not in_string:
                # Check if there's more content after the semicolon
                remaining = query[i+1:].strip()
                if remaining and not remaining.startswith('--'):
                    return True
        
        return False

    def _has_suspicious_comments(self, query: str) -> bool:
        """Check for suspicious SQL comments"""
        # Check for inline comments that might hide injection
        if re.search(r'/\*.*?\*/', query, re.DOTALL):
            return True
        
        # Check for line comments in suspicious positions
        if re.search(r'--.*?(OR|AND|UNION)', query, re.IGNORECASE):
            return True
        
        return False

    def sanitize_table_name(self, table_name: str) -> Tuple[bool, str]:
        """
        Validate and sanitize table name
        Returns: (is_valid, sanitized_name or error_message)
        """
        # Table names should only contain alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
            return False, "Invalid table name format"
        
        # Check length
        if len(table_name) > 64:
            return False, "Table name too long"
        
        return True, table_name

    def sanitize_column_name(self, column_name: str) -> Tuple[bool, str]:
        """
        Validate and sanitize column name
        Returns: (is_valid, sanitized_name or error_message)
        """
        # Column names should only contain alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', column_name):
            return False, "Invalid column name format"
        
        # Check length
        if len(column_name) > 64:
            return False, "Column name too long"
        
        return True, column_name

    def validate_where_clause(self, where_clause: str) -> Tuple[bool, str]:
        """
        Validate WHERE clause for safety
        Returns: (is_valid, error_message)
        """
        if not where_clause:
            return True, ""
        
        # Check for OR with always-true conditions (common in SQLi)
        if re.search(r"OR\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?", where_clause, re.IGNORECASE):
            if re.search(r"OR\s+['\"]?1['\"]?\s*=\s*['\"]?1['\"]?", where_clause, re.IGNORECASE):
                return False, "Suspicious WHERE clause: always-true condition"
        
        # Check for UNION in WHERE clause
        if 'UNION' in where_clause.upper():
            return False, "UNION not allowed in WHERE clause"
        
        return True, ""

    def get_query_type(self, query: str) -> str:
        """
        Get the type of SQL query
        Returns: 'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DDL', or 'UNKNOWN'
        """
        query_upper = query.upper().strip()
        first_keyword = query_upper.split()[0] if query_upper.split() else ""
        
        if first_keyword in self.READ_ONLY_OPS:
            return 'SELECT'
        elif first_keyword in self.WRITE_OPS:
            return first_keyword
        elif first_keyword in self.DDL_OPS:
            return 'DDL'
        else:
            return 'UNKNOWN'

    def set_allow_ddl(self, allow: bool):
        """Enable or disable DDL operations"""
        self.allow_ddl = allow
