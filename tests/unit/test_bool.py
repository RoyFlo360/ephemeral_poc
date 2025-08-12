from unittest import TestCase


class TestBooleanOperations(TestCase):
    def test_boolean_operations(self):
        """Test basic boolean operations: AND, OR, NOT"""
        assert (True and True) is True
        assert (True and False) is False
        assert (False and True) is False
        assert (False and False) is False
        
        assert (True or True) is True
        assert (True or False) is True
        assert (False or True) is True
        assert (False or False) is False
        
        assert not True is False
        assert not False is True


class TestBooleanTruthiness(TestCase):
    def test_boolean_truthiness(self):
        """Test truthiness of various values in boolean context"""
        # Falsy values
        assert bool(0) == False
        assert bool("") == False
        assert bool([]) == False
        assert bool(None) == False
        assert bool(False) == False
        
        # Truthy values
        assert bool(1) == True
        assert bool("hello") == True
        assert bool([1, 2, 3]) == True
        assert bool(True) == True


class TestBooleanComparisons(TestCase):
    def test_boolean_comparisons(self):
        """Test boolean comparison operations"""
        # Equality
        assert True == True
        assert False == False
        assert True != False
        assert False != True
        
        # Comparison with other types
        assert True == 0
        assert False == 0
        assert True > False
        assert False < True
        
        # Identity
        assert True is True
        assert False is False
        assert True is not False
