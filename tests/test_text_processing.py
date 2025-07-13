"""
Tests for the text processing utilities.
"""

import unittest
from src.utils.text_processing import (
    clean_text,
    extract_technique_id,
    extract_keywords,
    truncate_text,
    validate_query
)


class TestTextProcessing(unittest.TestCase):
    """Test cases for text processing utilities."""
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        # Test basic cleaning
        self.assertEqual(clean_text("  Hello   World  "), "Hello World")
        
        # Test with special characters
        self.assertEqual(clean_text("Hello@#$%World"), "HelloWorld")
        
        # Test empty string
        self.assertEqual(clean_text(""), "")
        
        # Test None input
        self.assertEqual(clean_text(None), "")
    
    def test_extract_technique_id(self):
        """Test MITRE technique ID extraction."""
        # Test basic technique ID
        self.assertEqual(extract_technique_id("T1059"), "T1059")
        
        # Test sub-technique ID
        self.assertEqual(extract_technique_id("T1059.001"), "T1059.001")
        
        # Test case insensitive
        self.assertEqual(extract_technique_id("t1059"), "T1059")
        
        # Test in context
        self.assertEqual(extract_technique_id("The technique T1059 is about command execution"), "T1059")
        
        # Test no technique ID
        self.assertIsNone(extract_technique_id("No technique here"))
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "PowerShell command execution and scripting"
        keywords = extract_keywords(text)
        
        self.assertIn("powershell", keywords)
        self.assertIn("command", keywords)
        self.assertIn("execution", keywords)
        self.assertIn("scripting", keywords)
        
        # Test max keywords limit
        keywords_limited = extract_keywords(text, max_keywords=2)
        self.assertEqual(len(keywords_limited), 2)
        
        # Test empty text
        self.assertEqual(extract_keywords(""), [])
    
    def test_truncate_text(self):
        """Test text truncation."""
        text = "This is a long text that needs to be truncated properly"
        
        # Test normal truncation
        truncated = truncate_text(text, max_length=20)
        self.assertTrue(len(truncated) <= 20)
        self.assertTrue(truncated.endswith("..."))
        
        # Test no truncation needed
        short_text = "Short"
        self.assertEqual(truncate_text(short_text, max_length=20), short_text)
    
    def test_validate_query(self):
        """Test query validation."""
        # Test valid query
        is_valid, error = validate_query("What is T1059?")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
        
        # Test empty query
        is_valid, error = validate_query("")
        self.assertFalse(is_valid)
        self.assertIn("empty", error.lower())
        
        # Test too short query
        is_valid, error = validate_query("Hi")
        self.assertFalse(is_valid)
        self.assertIn("short", error.lower())
        
        # Test too long query
        long_query = "A" * 600
        is_valid, error = validate_query(long_query)
        self.assertFalse(is_valid)
        self.assertIn("long", error.lower())


if __name__ == '__main__':
    unittest.main()
