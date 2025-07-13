"""
Text processing utilities for the MITRE ATT&CK chatbot.
"""

import re
from typing import List, Dict, Any, Optional


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text (str): Input text to clean.
    
    Returns:
        str: Cleaned text.
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might interfere with processing
    text = re.sub(r'[^\w\s\-\.\,\:\;\!\?\(\)]', '', text)
    
    return text.strip()


def extract_technique_id(text: str) -> Optional[str]:
    """
    Extract MITRE ATT&CK technique ID from text.
    
    Args:
        text (str): Text that might contain a technique ID.
    
    Returns:
        str or None: Extracted technique ID if found.
    """
    # Pattern for MITRE ATT&CK technique IDs (e.g., T1059, T1059.001)
    pattern = r'T\d{4}(?:\.\d{3})?'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0).upper() if match else None


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract relevant keywords from text for better search.
    
    Args:
        text (str): Input text to extract keywords from.
        max_keywords (int): Maximum number of keywords to return.
    
    Returns:
        list: List of extracted keywords.
    """
    if not text:
        return []
    
    # Convert to lowercase and remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Split into words
    words = text.split()
    
    # Filter out common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
        'they', 'me', 'him', 'her', 'us', 'them'
    }
    
    # Filter and get unique keywords
    keywords = [word for word in words if len(word) > 2 and word not in stop_words]
    
    # Remove duplicates while preserving order
    unique_keywords = []
    seen = set()
    for keyword in keywords:
        if keyword not in seen:
            unique_keywords.append(keyword)
            seen.add(keyword)
    
    return unique_keywords[:max_keywords]


def format_mitre_response(technique_data: Dict[str, Any]) -> str:
    """
    Format MITRE ATT&CK technique data into a readable response.
    
    Args:
        technique_data (dict): Dictionary containing technique information.
    
    Returns:
        str: Formatted response string.
    """
    response_parts = []
    
    # Technique name and ID
    name = technique_data.get('name', 'Unknown Technique')
    technique_id = technique_data.get('id', 'N/A')
    response_parts.append(f"**Technique**: {name} ({technique_id})")
    
    # Tactics
    tactics = technique_data.get('tactics', [])
    if tactics:
        if isinstance(tactics, str):
            tactics = [tactics]
        response_parts.append(f"**Tactics**: {', '.join(tactics)}")
    
    # Description
    description = technique_data.get('description', '')
    if description:
        response_parts.append(f"**Description**: {clean_text(description)}")
    
    # Platforms
    platforms = technique_data.get('platforms', [])
    if platforms:
        if isinstance(platforms, str):
            platforms = [platforms]
        response_parts.append(f"**Platforms**: {', '.join(platforms)}")
    
    # Data sources
    datasources = technique_data.get('datasources', [])
    if datasources:
        if isinstance(datasources, str):
            datasources = [datasources]
        response_parts.append(f"**Data Sources**: {', '.join(datasources)}")
    
    # Detection
    detection = technique_data.get('detection', '')
    if detection:
        response_parts.append(f"**Detection**: {clean_text(detection)}")
    
    # Mitigations
    mitigations = technique_data.get('mitigations', [])
    if mitigations:
        mitigation_text = []
        for mitigation in mitigations:
            if isinstance(mitigation, dict):
                name = mitigation.get('name', 'Unknown')
                desc = mitigation.get('description', '')
                mitigation_text.append(f"- {name}: {clean_text(desc)}")
            else:
                mitigation_text.append(f"- {str(mitigation)}")
        
        if mitigation_text:
            response_parts.append(f"**Mitigations**:\n{chr(10).join(mitigation_text)}")
    
    # URL
    url = technique_data.get('url', '')
    if url:
        response_parts.append(f"**Reference**: {url}")
    
    return "\n\n".join(response_parts)


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length while preserving word boundaries.
    
    Args:
        text (str): Text to truncate.
        max_length (int): Maximum length of the truncated text.
        suffix (str): Suffix to add when text is truncated.
    
    Returns:
        str: Truncated text.
    """
    if len(text) <= max_length:
        return text
    
    # Find the last space before the max_length to avoid cutting words
    truncate_at = text.rfind(' ', 0, max_length - len(suffix))
    
    if truncate_at == -1:  # No space found, just cut at max_length
        truncate_at = max_length - len(suffix)
    
    return text[:truncate_at] + suffix


def validate_query(query: str, min_length: int = 3, max_length: int = 500) -> tuple[bool, str]:
    """
    Validate user query for basic requirements.
    
    Args:
        query (str): User query to validate.
        min_length (int): Minimum query length.
        max_length (int): Maximum query length.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty."
    
    query = query.strip()
    
    if len(query) < min_length:
        return False, f"Query too short. Minimum {min_length} characters required."
    
    if len(query) > max_length:
        return False, f"Query too long. Maximum {max_length} characters allowed."
    
    # Check for potential injection attempts (basic validation)
    suspicious_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'data:text/html',
        r'eval\s*\(',
        r'exec\s*\('
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return False, "Query contains potentially unsafe content."
    
    return True, ""
