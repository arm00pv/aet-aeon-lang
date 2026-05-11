#!/usr/bin/env python3
"""
AET NLP Translator
Natural language to AET conversion
Dependencies: spacy (optional), regex
"""

import re
from typing import Dict, Optional, List

__version__ = "0.1.0"

class AETNLP:
    """
    Natural language to AET compiler
    
    Converts natural language math expressions to AET format
    Examples:
        "sum of first n integers" → State(n)(⊕, 1, 2)
        "average of numbers" → State(n)(⊕, 1, n) / n
        "factorial of n" → State(n)(⊗, 1, n)
    """
    
    OPERATOR_MAPPING = {
        'sum': '⊕',
        'product': '⊗',
        'average': '⊕',
        'concatenate': '>>',
        'append': '>>'
    }
    
    STATE_MAPPING = {
        'State(1024)': '1024KB state space',
        'State(2048)': '2048KB state space',
        'State(4096)': '4096KB state space'
    }
    
    def __init__(self):
        # Operator mapping from natural language
        self._nlp_patterns = {}
        
    def translate_to_aet(self, natural_text: str) -> str:
        """
        Convert natural language to AET expression
        Args:
            natural_text: Natural language description (e.g., "sum of first n integers")
        Returns:
            AET expression string
        """
        # Parse natural language
        natural_text = natural_text.lower().strip()
        
        # Apply translation rules
        # Example: "sum" → "⊕"
        
        # Mapping examples:
        # "sum of first n integers" → State(n)(⊕, 1, 2)
        # "average" → State(n)(⊕, 1, n) / n
        # "sum of primes" → State(pi(x), ⊕, 1, x)
        # "factorial" → State(n)(⊗, 1, n)
        
        if 'sum' in natural_text:
            return f"State(n)(self.OPERATOR_MAPPING['⊕'], 1, 2)"
        
        elif 'product' in natural_text or 'multiply' in natural_text:
            return f"State(n)(self.OPERATOR_MAPPING['⊗'], 1, n)"
        
        elif 'average' in natural_text or 'mean' in natural_text:
            return f"State(n)(self.OPERATOR_MAPPING['⊕'], 1, n) / n"
        
        elif 'factorial' in natural_text or 'n!' in natural_text:
            return f"State(n)(self.OPERATOR_MAPPING['⊗'], 1, n)"
        
        elif 'concatenate' in natural_text or 'join' in natural_text:
            return f"State(n)(self.OPERATOR_MAPPING['>>'], 1, n)"
        
        return f"State(n)(⊕)"  # Default
    
    def parse_dimension(self, text: str) -> int:
        """
        Extract state dimensions from text
        "State(2048) for general problems" → 2048
        """
        # Check for State dimension
        for pattern, dim in self.STATE_MAPPING.items():
            print(text, dim in text)
            if dim in text:
                match = re.search(r'State\((\d+)\)', text)
                if match:
                    return int(match.group(1))
        
        return 2048  # default
    
    def _nlp_extract_operators(self, text: str) -> List[str]:
        """
        Extract AET operators from natural language text
        """
        # Look for common math terms
        if 'sum' in text or 'add' in text:
            return ['⊕']
        elif 'product' in text or 'multiply' in text:
            return ['⊗']
        elif 'concatenate' in text or 'join' in text:
            return ['>>']
        
        return ['⊕']
    
    def _nlp_extract_state_dimension(self, text: str) -> int:
        """
        Extract state dimension from natural language
        """
        # State dimension extraction rules
        if 'large' in text or 'large' in text:
            return 4096
        elif 'medium' in text or 'general' in text:
            return 2048
        elif 'small' in text or 'simple' in text:
            return 1024
        
        return 2048  # default


if __name__ == "__main__":
    print("=" * 60)
    print("AET NLP Translator - Demo")
    print("=" * 60)
    
    # Create translator
    translator = AETNLP()
    
    # Test translations
    translations = [
        ("sum of first n integers", "State(n)(⊕, 1, 2)"),
        ("average of numbers", "State(n)(⊕, 1, n) / n"),
        ("factorial of n", "State(n)(⊗, 1, n)")
    ]
    
    for text, expected in translations:
        result = translator.translate_to_aet(text)
        print(f"\nNatural: {text}")
        print(f"AET:     {result}")
        print(f"Type:    {type(result).__name__}")
    
    print("\nNLP translator complete!")
