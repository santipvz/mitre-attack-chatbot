"""
Basic tests for the indexer module.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock

# Note: These are basic structure tests. Full integration tests would require
# actual embedding models and may take longer to run.


class TestIndexer(unittest.TestCase):
    """Test cases for the indexer module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary JSON file with sample MITRE data
        self.test_data = [
            {
                "id": "T1059",
                "name": "Command and Scripting Interpreter",
                "description": "Adversaries may abuse command and script interpreters to execute commands, scripts, or binaries.",
                "tactics": ["execution"],
                "platforms": ["Linux", "macOS", "Windows"],
                "datasources": ["Process"],
                "permissions_required": ["User"],
                "url": "https://attack.mitre.org/techniques/T1059/",
                "mitigations": [
                    {
                        "name": "Code Signing",
                        "description": "Enforce binary and application integrity"
                    }
                ]
            }
        ]
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_data, self.temp_file)
        self.temp_file.close()
        
        # Create temporary directory for vector store
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_file.name)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_extract_metadata(self):
        """Test metadata extraction from MITRE records."""
        try:
            from src.indexer import extract_metadata
            
            record = self.test_data[0]
            metadata = {}
            result = extract_metadata(record, metadata)
            
            self.assertEqual(result['id'], 'T1059')
            self.assertEqual(result['name'], 'Command and Scripting Interpreter')
            self.assertEqual(result['tactics'], 'execution')
            self.assertIn('Linux', result['platforms'])
            
        except ImportError:
            self.skipTest("Indexer module not available for testing")
    
    def test_load_documents_file_not_found(self):
        """Test loading documents with non-existent file."""
        try:
            from src.indexer import load_documents
            
            with self.assertRaises(SystemExit):
                load_documents("non_existent_file.json")
                
        except ImportError:
            self.skipTest("Indexer module not available for testing")
    
    @patch('src.indexer.JSONLoader')
    def test_load_documents_success(self, mock_loader):
        """Test successful document loading."""
        try:
            from src.indexer import load_documents
            
            # Mock the loader
            mock_instance = MagicMock()
            mock_instance.load.return_value = ['doc1', 'doc2']
            mock_loader.return_value = mock_instance
            
            # Test loading
            docs = load_documents(self.temp_file.name)
            self.assertEqual(len(docs), 2)
            
        except ImportError:
            self.skipTest("Indexer module not available for testing")


if __name__ == '__main__':
    unittest.main()
