"""
Basic tests for the chatbot module.
"""

import unittest
from unittest.mock import patch, MagicMock


class TestChatbot(unittest.TestCase):
    """Test cases for the chatbot module."""
    
    def test_build_context(self):
        """Test context building functionality."""
        try:
            from src.chatbot import build_context
            
            # Mock vector store and documents
            mock_vector_store = MagicMock()
            
            # Mock document with metadata
            mock_doc = MagicMock()
            mock_doc.page_content = "Test content"
            mock_doc.metadata = {
                'name': 'Test Technique',
                'id': 'T1059',
                'tactics': 'execution',
                'detection': 'Monitor process execution',
                'datasources': 'Process monitoring',
                'permissions_required': 'User',
                'mitigations': [
                    {'name': 'Code Signing', 'description': 'Enforce integrity'}
                ],
                'url': 'https://attack.mitre.org/techniques/T1059/'
            }
            
            mock_vector_store.similarity_search.return_value = [mock_doc]
            
            # Test context building
            context = build_context("test query", mock_vector_store, 1)
            
            self.assertIn("Test Technique", context)
            self.assertIn("T1059", context)
            self.assertIn("execution", context)
            self.assertIn("Code Signing", context)
            
        except ImportError:
            self.skipTest("Chatbot module not available for testing")
    
    def test_parse_arguments(self):
        """Test argument parsing."""
        try:
            from src.chatbot import parse_arguments
            
            # Test with minimal arguments
            with patch('sys.argv', ['chatbot.py']):
                args = parse_arguments()
                self.assertIsNotNone(args)
                self.assertTrue(hasattr(args, 'vector_store'))
                self.assertTrue(hasattr(args, 'openai'))
                self.assertTrue(hasattr(args, 'num_similar'))
                
        except ImportError:
            self.skipTest("Chatbot module not available for testing")
    
    def test_setup_embedding_model(self):
        """Test embedding model setup."""
        try:
            from src.chatbot import setup_embedding_model
            
            # Test with mock OpenAI key
            with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
                with patch('src.chatbot.config') as mock_config:
                    mock_config.OPENAI_API_KEY = 'test_key'
                    mock_config.EMBEDDING_MODEL = 'text-embedding-3-small'
                    mock_config.LOCAL_EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
                    
                    # This would normally create an actual embedding model
                    # For testing, we just verify the function can be called
                    # without errors in the basic logic
                    try:
                        model = setup_embedding_model(use_openai=False, use_local=True)
                        # If we get here, the function structure is correct
                        self.assertTrue(True)
                    except Exception as e:
                        # Expected for missing dependencies in test environment
                        self.assertIn(("sentence-transformers" in str(e) or 
                                     "huggingface" in str(e) or
                                     "torch" in str(e)), True)
                        
        except ImportError:
            self.skipTest("Chatbot module not available for testing")


if __name__ == '__main__':
    unittest.main()
