"""
Truth table verification for QM outputs
This is the GOLD STANDARD test - verifies minimized function matches original
Run with: python test_truth_table.py
"""

import sys
sys.path.insert(0, '.')
from QM import (
    generate_prime_implicants, build_pi_chart, find_essential_pis,
    get_uncovered_minterms, find_minimal_covers, parse_input_file
)


def evaluate_term(binary_term, input_values):
    """
    Evaluate a single product term against input values
    
    Args:
        binary_term: e.g., "10-1" means A=1, B=0, C=don't care, D=1
        input_values: binary string of actual input, e.g., "1001"
    
    Returns:
        True if term matches, False otherwise
    """
    if len(binary_term) != len(input_values):
        return False
    
    for i in range(len(binary_term)):
        if binary_term[i] == '-':
            continue  # Don't care
        if binary_term[i] != input_values[i]:
            return False
    
    return True


def evaluate_solution(essential_pis, solution_pi_indices, prime_implicants, input_values):
    """
    Evaluate complete minimized function for given input
    
    Args:
        essential_pis: List of (binary, minterms) tuples
        solution_pi_indices: List of non-essential PI indices to include
        prime_implicants: All prime implicants
        input_values: Binary string input
    
    Returns:
        True if function outputs 1, False if 0
    """
    # Check essential PIs
    for binary, _ in essential_pis:
        if evaluate_term(binary, input_values):
            return True
    
    # Check solution PIs
    for idx in solution_pi_indices:
        binary, _ = prime_implicants[idx]
        if evaluate_term(binary, input_values):
            return True
    
    return False


def verify_testcase(testcase_num, verbose=True):
    """
    Verify a test case by comparing truth tables
    
    Returns:
        (passed, total_tests, errors)
    """
    filename = f"./complex_test_cases/test{testcase_num}.txt"
    
    # Parse input
    num_vars, minterms, dont_cares = parse_input_file(filename)
    
    if num_vars is None:
        return False, 0, ["Failed to parse input file"]
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"VERIFYING TESTCASE {testcase_num}")
        print(f"{'='*70}")
        print(f"Variables: {num_vars}")
        print(f"Minterms: {len(minterms)} terms")
        print(f"Don't cares: {len(dont_cares)} terms")
    
    # Generate solution
    prime_implicants = generate_prime_implicants(minterms, dont_cares, num_vars)
    pi_chart = build_pi_chart(prime_implicants, minterms)
    essential_pis, essential_indices = find_essential_pis(prime_implicants, pi_chart)
    uncovered_minterms = get_uncovered_minterms(essential_pis, minterms)
    solutions = find_minimal_covers(prime_implicants, pi_chart, uncovered_minterms, 
                                   essential_indices)
    
    if not solutions and uncovered_minterms:
        return False, 0, ["No solution found but uncovered minterms exist"]
    
    if not solutions:
        solutions = [[]]  # Empty solution if all covered by essentials
    
    # Test all possible inputs
    errors = []
    total_tests = 2 ** num_vars
    passed_tests = 0
    
    for i in range(total_tests):
        binary_input = format(i, f'0{num_vars}b')
        
        # Expected output
        if i in minterms:
            expected = True
        elif i in dont_cares:
            # Don't care - can be either, so we skip checking
            passed_tests += 1
            continue
        else:
            expected = False
        
        # Actual output from minimized function (test first solution)
        actual = evaluate_solution(essential_pis, solutions[0], prime_implicants, binary_input)
        
        if actual != expected:
            errors.append(f"Input {i:3d} ({binary_input}): Expected {expected}, Got {actual}")
        else:
            passed_tests += 1
    
    if verbose:
        if not errors:
            print(f"✅ PASSED: All {passed_tests}/{total_tests} test vectors correct")
        else:
            print(f"❌ FAILED: {passed_tests}/{total_tests} passed, {len(errors)} errors")
            for error in errors[:10]:  # Show first 10 errors
                print(f"   {error}")
            if len(errors) > 10:
                print(f"   ... and {len(errors) - 10} more errors")
    
    return len(errors) == 0, total_tests, errors


def verify_all_testcases(testcase_numbers):
    """Verify multiple test cases"""
    print("\n" + "="*70)
    print("TRUTH TABLE VERIFICATION SUITE")
    print("="*70)
    
    results = {}
    total_passed = 0
    total_failed = 0
    
    for tc in testcase_numbers:
        try:
            passed, total, errors = verify_testcase(tc, verbose=True)
            results[tc] = (passed, total, errors)
            
            if passed:
                total_passed += 1
            else:
                total_failed += 1
        except Exception as e:
            print(f"❌ TESTCASE {tc}: Exception - {e}")
            results[tc] = (False, 0, [str(e)])
            total_failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total testcases: {len(testcase_numbers)}")
    print(f"Passed: {total_passed} ✅")
    print(f"Failed: {total_failed} ❌")
    
    if total_failed > 0:
        print("\nFailed testcases:")
        for tc, (passed, _, errors) in results.items():
            if not passed:
                print(f"  - Testcase {tc}: {len(errors)} errors")
    
    return total_failed == 0


def test_specific_case():
    """Test a specific known case by hand"""
    print("\n" + "="*70)
    print("MANUAL TEST: F(A,B,C) = m(0,1,2,5,6,7)")
    print("="*70)
    
    minterms = [0, 1, 2, 5, 6, 7]
    dont_cares = []
    num_vars = 3
    
    pis = generate_prime_implicants(minterms, dont_cares, num_vars)
    pi_chart = build_pi_chart(pis, minterms)
    essential_pis, essential_indices = find_essential_pis(pis, pi_chart)
    uncovered = get_uncovered_minterms(essential_pis, minterms)
    solutions = find_minimal_covers(pis, pi_chart, uncovered, essential_indices)
    
    if not solutions:
        solutions = [[]]
    
    print(f"Prime Implicants: {len(pis)}")
    for idx, (binary, mins) in enumerate(pis):
        print(f"  PI{idx}: {binary} covers {sorted(mins)}")
    
    print(f"\nEssential PIs: {len(essential_pis)}")
    for binary, mins in essential_pis:
        print(f"  {binary} covers {sorted(mins)}")
    
    print(f"\nUncovered minterms: {sorted(uncovered) if uncovered else 'None'}")
    print(f"Solutions found: {len(solutions)}")
    
    # Verify truth table
    print("\nTruth Table Verification:")
    print("A B C | Expected | Actual | Status")
    print("-" * 40)
    
    all_correct = True
    for i in range(8):
        binary_input = format(i, '03b')
        expected = i in minterms
        actual = evaluate_solution(essential_pis, solutions[0], pis, binary_input)
        status = "✅" if expected == actual else "❌"
        
        if expected != actual:
            all_correct = False
        
        print(f"{binary_input[0]} {binary_input[1]} {binary_input[2]} |    {int(expected)}     |   {int(actual)}    | {status}")
    
    print("\n" + ("✅ ALL CORRECT" if all_correct else "❌ ERRORS FOUND"))
    return all_correct


if __name__ == "__main__":
    # Test specific manual case first
    test_specific_case()
    
    # Verify all test cases
    testcases = list(range(1, 11))
    all_passed = verify_all_testcases(testcases)
    
    sys.exit(0 if all_passed else 1)