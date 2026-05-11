#!/usr/bin/env python3
"""
AET Core State & Logic Implementation
Foundational class for AET expression handling and validation.
"""

import re

class AET:
    """Core AET Engine for expression identification and basic logic"""
    
    PRIMITIVES = ['State', 'WaveState', 'Attention', 'EntropyGate']
    OPERATORS = ['@', '>>', '⊗', '⊕']

    @staticmethod
    def is_aet_expression(expr: str) -> bool:
        """Determines if a string is a valid AET expression"""
        if not expr: return False
        
        # Check for presence of primitives or operators
        has_primitive = any(p in expr for p in AET.PRIMITIVES)
        has_operator = any(o in expr for o in AET.OPERATORS)
        
        # AET expressions usually define a state space or a transform chain
        is_assignment = "→" in expr or "=" in expr
        
        return has_primitive or has_operator or is_assignment

    @staticmethod
    def validate_syntax(expr: str) -> bool:
        """Basic AET syntax validation"""
        # Ensure balanced parentheses for State/WaveState
        if expr.count('(') != expr.count(')'):
            return False
        return True

if __name__ == "__main__":
    test_expr = "State(2048) → s1"
    print(f"Is AET: {AET.is_aet_expression(test_expr)}")
