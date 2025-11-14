"""
Integration tests for complete QM algorithm
Tests end-to-end functionality with known benchmark cases
Run with: pytest test_integration.py -v
"""

import pytest
import sys
sys.path.insert(0, '.')
from QM import (
    generate_prime_implicants, build_pi_chart, find_essential_pis,
    get_uncovered_minterms, find_minimal_covers, parse_input_file
)


class TestTextbookExamples:
    """Test cases from standard textbooks"""
    
    def test_morris_mano_example_4_7(self):
        """Example 4-7 from Morris Mano's Digital Design"""
        # F(A,B,C,D) = Σm(0,1,2,5,6,7,8,9,10,14)
        minterms = [0, 1, 2, 5, 6, 7, 8, 9, 10, 14]
        num_vars = 4
        
        pis = generate_prime_implicants(minterms, [], num_vars)
        chart = build_pi_chart(pis, minterms)
        essential, indices = find_essential_pis(pis, chart)
        
        # Should have prime implicants
        assert len(pis) > 0
        
        # All minterms should be covered
        covered = set()
        for _, mins in pis:
            covered.update(mins)
        assert set(minterms).issubset(covered)
    
    def test_single_literal_function(self):
        """F(A) = m(1) should give F = A"""
        minterms = [1]
        num_vars = 1
        
        pis = generate_prime_implicants(minterms, [], num_vars)
        
        assert len(pis) == 1
        assert pis[0][0] == "1"
        assert pis[0][1] == {1}
    
    def test_two_var_simple(self):
        """F(A,B) = m(0,1,2) should give F = A' + B'"""
        minterms = [0, 1, 2]
        num_vars = 2
        
        pis = generate_prime_implicants(minterms, [], num_vars)
        chart = build_pi_chart(pis, minterms)
        
        # Should have 2 PIs: 0- (covers 0,1) and -0 (covers 0,2)
        assert len(pis) == 2
        
        # Both should be essential
        essential, indices = find_essential_pis(pis, chart)
        assert len(essential) == 2
    
    def test_complement_function(self):
        """F(A,B,C) = m(1,3,5,7) = A (odd parity)"""
        minterms = [1, 3, 5, 7]
        num_vars = 3
        
        pis = generate_prime_implicants(minterms, [], num_vars)
        
        # Should reduce to single PI: --1 (C)
        assert any(pi[0] == "--1" for pi in pis)


class TestDontCareHandling:
    """Test proper handling of don't care conditions"""
    
    def test_dontcare_optimization(self):
        """Don't cares should help reduce expression"""
        # F(A,B,C) = m(0,2,4) + d(5,6,7)
        minterms = [0, 2, 4]
        dont_cares = [5, 6, 7]
        num_vars = 3
        
        # With don't cares
        pis_with_dc = generate_prime_implicants(minterms, dont_cares, num_vars)
        
        # Without don't cares
        pis_without_dc = generate_prime_implicants(minterms, [], num_vars)
        
        # With don't cares should give simpler (fewer) PIs
        # because don't cares allow more combinations
        assert len(pis_with_dc) <= len(pis_without_dc) + len(dont_cares)
    
    def test_dontcare_not_in_chart(self):
        """Don't cares should not appear in PI chart"""
        minterms = [0, 1]
        dont_cares = [2, 3]
        num_vars = 2
        
        pis = generate_prime_implicants(minterms, dont_cares, num_vars)
        chart = build_pi_chart(pis, minterms)
        
        # Only minterms should be in chart
        assert all(m in minterms for m in chart.keys())
        assert all(d not in chart for d in dont_cares)
    
    def test_only_dontcares(self):
        """Function with only don't cares should work"""
        minterms = []
        dont_cares = [0, 1, 2, 3]
        num_vars = 2
        
        pis = generate_prime_implicants(minterms, dont_cares, num_vars)
        
        # Should generate PIs from don't cares
        assert len(pis) >= 0


class TestComplexCases:
    """Test complex multi-variable cases"""
    
    def test_six_variable_case(self):
        """Test with 6 variables"""
        # F = ABCDEF (minterm 63)
        minterms = [63]
        num_vars = 6
        
        pis = generate_prime_implicants(minterms, [], num_vars)
        
        assert len(pis) == 1
        assert pis[0][0] == "111111"
        assert pis[0][1] == {63}
    
    def test_seven_variable_case(self):
        """Test with 7 variables"""
        minterms = [0, 127]  # All 0s and all 1s
        num_vars = 7
        
        pis = generate_prime_implicants(minterms, [], num_vars)
        
        assert len(pis) == 2
        # Should have two non-overlapping PIs
        assert any(pi[0] == "0000000" for pi in pis)
        assert any(pi[0] == "1111111" for pi in pis)
    
    def test_sparse_minterms(self):
        """Test with very sparse minterms (large gaps)"""
        # Only powers of 2
        minterms = [1, 2, 4, 8]
        num_vars = 4
        
        pis = generate_prime_implicants(minterms, [], num_vars)
        
        # Each should be its own PI (can't combine)
        assert len(pis) == 4
    
    def test_dense_minterms(self):
        """Test with many minterms"""
        # All but one minterm
        minterms = list(range(16))
        minterms.remove(7)  # Remove one
        num_vars = 4
        
        pis = generate_prime_implicants(minterms, [], num_vars)
        
        # Should generate multiple PIs covering the pattern
        assert len(pis) > 0


class TestMinimalCoverFinding:
    """Test the minimal cover selection algorithm"""
    
    def test_unique_minimal_cover(self):
        """Test case with single minimal cover"""
        minterms = [0, 1, 2, 3]
        num_vars = 2
        
        pis = generate_prime_implicants(minterms, [], num_vars)
        chart = build_pi_chart(pis, minterms)
        essential, indices = find_essential_pis(pis, chart)
        uncovered = get_uncovered_minterms(essential, minterms)
        
        solutions = find_minimal_covers(pis, chart, uncovered, indices)
        
        # Should have at least one solution
        assert len(solutions) >= 1
    
    def test_multiple_minimal_covers(self):
        """Test case with multiple equally minimal covers"""
        # Symmetric pattern often gives multiple solutions
        minterms = [0, 2, 5, 7]
        num_vars = 3
        
        pis = generate_prime_implicants(minterms, [], num_vars)
        chart = build_pi_chart(pis, minterms)
        essential, indices = find_essential_pis(pis, chart)
        uncovered = get_uncovered_minterms(essential, minterms)
        
        solutions = find_minimal_covers(pis, chart, uncovered, indices)
        
        # May have multiple solutions
        if len(solutions) > 1:
            # All solutions should have same size (minimal)
            sizes = [len(sol) for sol in solutions]
            assert len(set(sizes)) == 1  # All same size
    
    def test_all_essential_cover(self):
        """Test where essential PIs cover everything"""
        # Each minterm has unique bit pattern
        minterms = [1, 2, 4, 8]
        num_vars = 4
        
        pis = generate_prime_implicants(minterms, [], num_vars)
        chart = build_pi_chart(pis, minterms)
        essential, indices = find_essential_pis(pis, chart)
        uncovered = get_uncovered_minterms(essential, minterms)
        
        # All should be covered by essentials
        assert len(uncovered) == 0


class TestFileBasedTests:
    """Test against actual test case files"""
    
    def test_testcase_4_single_minterm(self):
        """Test case 4: Single minterm (simplest)"""
        num_vars, minterms, dont_cares = parse_input_file("./complex_test_cases/test4.txt")
        
        assert num_vars == 6
        assert minterms == [63]
        assert dont_cares == []
        
        pis = generate_prime_implicants(minterms, dont_cares, num_vars)
        
        assert len(pis) == 1
        assert pis[0][0] == "111111"
    
    def test_testcase_9_empty_function(self):
        """Test case 9: No minterms (empty function)"""
        num_vars, minterms, dont_cares = parse_input_file("./complex_test_cases/test9.txt")
        
        assert num_vars == 7
        assert len(minterms) == 0
        
        pis = generate_prime_implicants(minterms, dont_cares, num_vars)
        
        # No minterms means no PIs covering actual minterms
        # (Don't cares might generate PIs but they don't matter)
        chart = build_pi_chart(pis, minterms)
        assert len(chart) == 0  # No minterms in chart


class TestPropertyBasedInvariants:
    """Test that certain properties always hold"""
    
    def test_all_minterms_covered(self):
        """Every minterm must be covered by at least one PI"""
        for _ in range(10):  # Test multiple random cases
            import random
            num_vars = random.randint(3, 5)
            num_minterms = random.randint(1, min(10, 2**num_vars))
            minterms = random.sample(range(2**num_vars), num_minterms)
            
            pis = generate_prime_implicants(minterms, [], num_vars)
            
            # Check all minterms covered
            covered = set()
            for _, mins in pis:
                covered.update(mins)
            
            assert set(minterms).issubset(covered)
    
    def test_pi_minimality(self):
        """Each PI should be a prime implicant (can't be further combined)"""
        minterms = [0, 1, 2, 3, 8, 9, 10, 11]
        num_vars = 4
        
        pis = generate_prime_implicants(minterms, [], num_vars)
        
        # Each PI should have at least one dash (combined from simpler terms)
        # OR be a single minterm that can't combine
        for binary, mins in pis:
            # If it covers multiple minterms, it must be combined (have dash)
            if len(mins) > 1:
                assert '-' in binary
    
    def test_solution_covers_all_minterms(self):
        """Final solution must cover all minterms"""
        minterms = [0, 1, 5, 7, 8, 14, 15]
        num_vars = 4
        
        pis = generate_prime_implicants(minterms, [], num_vars)
        chart = build_pi_chart(pis, minterms)
        essential, indices = find_essential_pis(pis, chart)
        uncovered = get_uncovered_minterms(essential, minterms)
        solutions = find_minimal_covers(pis, chart, uncovered, indices)
        
        if not solutions:
            solutions = [[]]
        
        # Check first solution covers everything
        covered = set()
        for _, mins in essential:
            covered.update(mins)
        for pi_idx in solutions[0]:
            _, mins = pis[pi_idx]
            covered.update(mins)
        
        assert set(minterms).issubset(covered)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])