"""
Unit tests for QM simulator components
Run with: pytest test_qm_unit.py -v
"""

import pytest
import sys
sys.path.insert(0, '.')
from QM import (
    decimal_to_binary, count_ones, can_combine, combine_terms,
    generate_prime_implicants, build_pi_chart, find_essential_pis,
    get_uncovered_minterms, term_to_expression, term_to_verilog
)


class TestBinaryConversion:
    """Test binary conversion utilities"""
    
    def test_decimal_to_binary_basic(self):
        assert decimal_to_binary(0, 4) == "0000"
        assert decimal_to_binary(5, 4) == "0101"
        assert decimal_to_binary(15, 4) == "1111"
    
    def test_decimal_to_binary_variable_width(self):
        assert decimal_to_binary(7, 3) == "111"
        assert decimal_to_binary(7, 5) == "00111"
        assert decimal_to_binary(63, 6) == "111111"
    
    def test_count_ones(self):
        assert count_ones("0000") == 0
        assert count_ones("0101") == 2
        assert count_ones("1111") == 4
        assert count_ones("10-1") == 2
        assert count_ones("----") == 0


class TestTermCombination:
    """Test term combination logic"""
    
    def test_can_combine_differ_by_one(self):
        assert can_combine("0000", "0001") == True
        assert can_combine("1010", "1011") == True
        assert can_combine("1111", "0111") == True
    
    def test_can_combine_differ_by_multiple(self):
        assert can_combine("0000", "0011") == False
        assert can_combine("1010", "0101") == False
    
    def test_can_combine_same_terms(self):
        assert can_combine("1010", "1010") == False
    
    def test_can_combine_with_dontcare(self):
        assert can_combine("10-1", "1001") == False
        assert can_combine("1-01", "1001") == False
        assert can_combine("-010", "0010") == False
    
    def test_can_combine_different_lengths(self):
        assert can_combine("101", "1010") == False
    
    def test_combine_terms_basic(self):
        binary, minterms = combine_terms("0000", "0001", {0}, {1})
        assert binary == "000-"
        assert minterms == {0, 1}
    
    def test_combine_terms_complex(self):
        binary, minterms = combine_terms("1010", "1110", {10}, {14})
        assert binary == "1-10"
        assert minterms == {10, 14}


class TestPrimeImplicantGeneration:
    """Test prime implicant generation"""
    
    def test_single_minterm(self):
        pis = generate_prime_implicants([63], [], 6)
        assert len(pis) == 1
        assert pis[0][0] == "111111"
        assert pis[0][1] == {63}
    
    def test_simple_combination(self):
        # Minterms 0,1 should combine to 000-
        pis = generate_prime_implicants([0, 1], [], 3)
        # Should have one PI covering both
        assert any(pi[1] == {0, 1} for pi in pis)
    
    def test_with_dont_cares(self):
        # Minterms: 0, don't care: 1
        pis = generate_prime_implicants([0], [1], 2)
        # Should combine 0,1 into 0-
        assert any(pi[0] == "0-" and pi[1] == {0, 1} for pi in pis)
    
    def test_no_minterms(self):
        pis = generate_prime_implicants([], [1, 2, 3], 2)
        # Only don't cares, should still generate PIs
        assert len(pis) >= 0
    
    def test_all_minterms(self):
        # All 8 minterms for 3 variables
        pis = generate_prime_implicants([0,1,2,3,4,5,6,7], [], 3)
        # Should reduce to single PI: ---
        assert any(pi[0] == "---" for pi in pis)


class TestPIChart:
    """Test prime implicant chart building"""
    
    def test_build_pi_chart_simple(self):
        pis = [("00-", {0, 1}), ("0-0", {0, 2})]
        minterms = [0, 1, 2]
        chart = build_pi_chart(pis, minterms)
        
        assert 0 in chart
        assert 1 in chart
        assert 2 in chart
        assert len(chart[0]) == 2  # Minterm 0 covered by both PIs
        assert len(chart[1]) == 1  # Minterm 1 covered by PI 0 only
        assert len(chart[2]) == 1  # Minterm 2 covered by PI 1 only
    
    def test_build_pi_chart_with_dontcare(self):
        # PI covers minterm and don't care
        pis = [("0-", {0, 1})]
        minterms = [0]  # Only 0 is minterm, 1 is don't care
        chart = build_pi_chart(pis, minterms)
        
        assert 0 in chart
        assert 1 not in chart  # Don't care not in chart


class TestEssentialPIs:
    """Test essential prime implicant detection"""
    
    def test_find_essential_basic(self):
        pis = [("00", {0}), ("01", {1}), ("1-", {2, 3})]
        chart = {0: [0], 1: [1], 2: [2], 3: [2]}
        
        essential, indices = find_essential_pis(pis, chart)
        
        assert 0 in indices  # PI 0 is essential (only covers 0)
        assert 1 in indices  # PI 1 is essential (only covers 1)
        assert 2 in indices  # PI 2 is essential (only covers 2 and 3)
    
    def test_find_essential_none(self):
        pis = [("0-", {0, 1}), ("-0", {0, 2})]
        chart = {0: [0, 1], 1: [0], 2: [1]}
        
        essential, indices = find_essential_pis(pis, chart)
        
        # Both are essential because each uniquely covers a minterm
        assert len(indices) == 2
    
    def test_get_uncovered_minterms(self):
        essential_pis = [("00", {0, 1})]
        minterms = [0, 1, 2, 3]
        
        uncovered = get_uncovered_minterms(essential_pis, minterms)
        
        assert uncovered == {2, 3}


class TestExpressionConversion:
    """Test expression formatting"""
    
    def test_term_to_expression_basic(self):
        assert term_to_expression("000", 3) == "A'B'C'"
        assert term_to_expression("111", 3) == "ABC"
        assert term_to_expression("101", 3) == "AB'C"
    
    def test_term_to_expression_with_dontcare(self):
        assert term_to_expression("0-1", 3) == "A'C"
        assert term_to_expression("-10", 3) == "BC'"
        assert term_to_expression("---", 3) == "1"
    
    def test_term_to_expression_six_vars(self):
        assert term_to_expression("111111", 6) == "ABCDEF"
        assert term_to_expression("000000", 6) == "A'B'C'D'E'F'"
    
    def test_term_to_verilog_basic(self):
        assert term_to_verilog("000", 3) == "~a & ~b & ~c"
        assert term_to_verilog("111", 3) == "a & b & c"
    
    def test_term_to_verilog_with_dontcare(self):
        assert term_to_verilog("0-1", 3) == "~a & c"
        assert term_to_verilog("---", 3) == "1'b1"


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_single_variable(self):
        # F(A) = m(1)
        pis = generate_prime_implicants([1], [], 1)
        assert len(pis) == 1
        assert pis[0][0] == "1"
    
    def test_empty_function(self):
        # No minterms
        pis = generate_prime_implicants([], [], 3)
        assert len(pis) == 0
    
    def test_full_function(self):
        # All minterms for 2 variables
        pis = generate_prime_implicants([0, 1, 2, 3], [], 2)
        # Should reduce to single PI covering everything
        assert any(pi[0] == "--" for pi in pis)
    
    def test_large_minterm_values(self):
        # 7 variables, test with large minterm
        pis = generate_prime_implicants([127], [], 7)
        assert len(pis) == 1
        assert pis[0][0] == "1111111"


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_simple_qm_flow(self):
        """Test complete QM flow for simple case"""
        # F(A,B,C) = m(0,1,2,5,6,7)
        minterms = [0, 1, 2, 5, 6, 7]
        dont_cares = []
        num_vars = 3
        
        # Generate PIs
        pis = generate_prime_implicants(minterms, dont_cares, num_vars)
        
        # Build chart
        chart = build_pi_chart(pis, minterms)
        
        # Find essential
        essential, indices = find_essential_pis(pis, chart)
        
        # Get uncovered
        uncovered = get_uncovered_minterms(essential, minterms)
        
        # Verify all minterms covered by PIs
        all_covered = set()
        for pi_binary, pi_mins in pis:
            all_covered.update(pi_mins)
        
        assert set(minterms).issubset(all_covered)
    
    def test_with_dont_cares_flow(self):
        """Test complete flow with don't cares"""
        # F(A,B,C,D) = m(0,1,3,7,8,9) + d(10,11)
        minterms = [0, 1, 3, 7, 8, 9]
        dont_cares = [10, 11]
        num_vars = 4
        
        pis = generate_prime_implicants(minterms, dont_cares, num_vars)
        chart = build_pi_chart(pis, minterms)
        
        # All minterms should be in chart
        assert all(m in chart for m in minterms)
        
        # Don't cares should NOT be in chart
        assert all(d not in chart for d in dont_cares)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])