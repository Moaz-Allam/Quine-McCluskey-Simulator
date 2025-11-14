"""
Fuzzing tests - Generate random test cases to find edge cases
Run with: python test_fuzzing.py
"""

import random
import sys
sys.path.insert(0, '.')
from QM import (
    generate_prime_implicants, build_pi_chart, find_essential_pis,
    get_uncovered_minterms, find_minimal_covers
)


def evaluate_term(binary_term, input_values):
    """Evaluate a single product term"""
    if len(binary_term) != len(input_values):
        return False
    
    for i in range(len(binary_term)):
        if binary_term[i] == '-':
            continue
        if binary_term[i] != input_values[i]:
            return False
    return True


def evaluate_solution(essential_pis, solution_indices, prime_implicants, input_values):
    """Evaluate complete solution"""
    for binary, _ in essential_pis:
        if evaluate_term(binary, input_values):
            return True
    
    for idx in solution_indices:
        binary, _ = prime_implicants[idx]
        if evaluate_term(binary, input_values):
            return True
    
    return False


def verify_correctness(num_vars, minterms, dont_cares, prime_implicants, 
                      essential_pis, solutions):
    """Verify that solution is functionally correct"""
    
    if not solutions:
        solutions = [[]]
    
    errors = []
    
    # Test all possible inputs
    for i in range(2 ** num_vars):
        binary_input = format(i, f'0{num_vars}b')
        
        # Expected output
        if i in dont_cares:
            continue  # Skip don't cares
        
        expected = i in minterms
        actual = evaluate_solution(essential_pis, solutions[0], prime_implicants, binary_input)
        
        if actual != expected:
            errors.append({
                'input': i,
                'binary': binary_input,
                'expected': expected,
                'actual': actual
            })
    
    return len(errors) == 0, errors


def fuzz_test_single(test_num, num_vars, density=0.3):
    """
    Run a single fuzz test
    
    Args:
        test_num: Test number for identification
        num_vars: Number of variables (2-8 recommended)
        density: Probability of including each minterm (0.0-1.0)
    
    Returns:
        (passed, error_info)
    """
    max_terms = 2 ** num_vars
    
    # Randomly select minterms
    num_minterms = random.randint(0, max_terms)
    all_indices = list(range(max_terms))
    random.shuffle(all_indices)
    
    minterms = sorted(all_indices[:num_minterms])
    
    # Randomly select don't cares from remaining
    remaining = [x for x in all_indices if x not in minterms]
    num_dontcares = random.randint(0, len(remaining))
    dont_cares = sorted(remaining[:num_dontcares])
    
    try:
        # Run QM algorithm
        pis = generate_prime_implicants(minterms, dont_cares, num_vars)
        chart = build_pi_chart(pis, minterms)
        essential, indices = find_essential_pis(pis, chart)
        uncovered = get_uncovered_minterms(essential, minterms)
        solutions = find_minimal_covers(pis, chart, uncovered, indices)
        
        # Verify correctness
        passed, errors = verify_correctness(num_vars, minterms, dont_cares, 
                                           pis, essential, solutions)
        
        if not passed:
            return False, {
                'test_num': test_num,
                'num_vars': num_vars,
                'minterms': minterms,
                'dont_cares': dont_cares,
                'errors': errors[:5]  # First 5 errors
            }
        
        return True, None
        
    except Exception as e:
        return False, {
            'test_num': test_num,
            'num_vars': num_vars,
            'minterms': minterms,
            'dont_cares': dont_cares,
            'exception': str(e)
        }


def run_fuzz_tests(num_tests=100, min_vars=2, max_vars=6):
    """
    Run multiple fuzz tests
    
    Args:
        num_tests: Number of random tests to run
        min_vars: Minimum number of variables
        max_vars: Maximum number of variables
    """
    print("="*70)
    print(f"FUZZING TEST SUITE")
    print(f"Running {num_tests} random tests")
    print(f"Variables: {min_vars}-{max_vars}")
    print("="*70)
    
    passed = 0
    failed = 0
    failures = []
    
    for i in range(num_tests):
        num_vars = random.randint(min_vars, max_vars)
        
        success, error_info = fuzz_test_single(i, num_vars)
        
        if success:
            passed += 1
            if (i + 1) % 10 == 0:
                print(f"✅ Tests 1-{i+1}: {passed} passed, {failed} failed")
        else:
            failed += 1
            failures.append(error_info)
            print(f"❌ Test {i+1} FAILED: {num_vars} vars, {len(error_info.get('minterms', []))} minterms")
            
            # Save failing case
            save_failing_case(error_info)
    
    # Final summary
    print("\n" + "="*70)
    print("FUZZING SUMMARY")
    print("="*70)
    print(f"Total tests: {num_tests}")
    print(f"Passed: {passed} ({100*passed/num_tests:.1f}%)")
    print(f"Failed: {failed} ({100*failed/num_tests:.1f}%)")
    
    if failures:
        print(f"\n{len(failures)} failing test cases saved to fuzz_failures/")
        print("\nFirst failure details:")
        print_failure_details(failures[0])
    else:
        print("\n✅ ALL FUZZ TESTS PASSED!")
    
    return failed == 0


def save_failing_case(error_info):
    """Save a failing test case for reproduction"""
    import os
    
    os.makedirs('fuzz_failures', exist_ok=True)
    
    test_num = error_info['test_num']
    filename = f"fuzz_failures/fail_{test_num}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"{error_info['num_vars']}\n")
        
        minterms = error_info['minterms']
        if minterms:
            f.write(','.join(f"m{m}" for m in minterms) + "\n")
        else:
            f.write("\n")
        
        dont_cares = error_info.get('dont_cares', [])
        if dont_cares:
            f.write(','.join(f"d{d}" for d in dont_cares) + "\n")


def print_failure_details(error_info):
    """Print detailed information about a failure"""
    print(f"  Test number: {error_info['test_num']}")
    print(f"  Variables: {error_info['num_vars']}")
    print(f"  Minterms: {error_info['minterms']}")
    print(f"  Don't cares: {error_info.get('dont_cares', [])}")
    
    if 'exception' in error_info:
        print(f"  Exception: {error_info['exception']}")
    
    if 'errors' in error_info:
        print(f"  Logic errors: {len(error_info['errors'])} found")
        for err in error_info['errors'][:3]:
            print(f"    Input {err['input']} ({err['binary']}): "
                  f"Expected {err['expected']}, Got {err['actual']}")


def stress_test_large_cases():
    """Test with larger variable counts"""
    print("\n" + "="*70)
    print("STRESS TESTING - Large Variable Counts")
    print("="*70)
    
    test_cases = [
        (7, 10, "7 vars, 10 minterms"),
        (7, 50, "7 vars, 50 minterms"),
        (8, 20, "8 vars, 20 minterms"),
        (9, 10, "9 vars, 10 minterms (sparse)"),
    ]
    
    for num_vars, num_minterms, description in test_cases:
        print(f"\nTesting: {description}")
        
        try:
            max_terms = 2 ** num_vars
            minterms = sorted(random.sample(range(max_terms), 
                            min(num_minterms, max_terms)))
            
            import time
            start = time.time()
            
            pis = generate_prime_implicants(minterms, [], num_vars)
            chart = build_pi_chart(pis, minterms)
            essential, indices = find_essential_pis(pis, chart)
            uncovered = get_uncovered_minterms(essential, minterms)
            solutions = find_minimal_covers(pis, chart, uncovered, indices)
            
            elapsed = time.time() - start
            
            # Verify
            passed, errors = verify_correctness(num_vars, minterms, [], 
                                               pis, essential, solutions)
            
            if passed:
                print(f"  ✅ PASSED in {elapsed:.3f}s")
                print(f"     PIs: {len(pis)}, Essential: {len(essential)}, "
                      f"Solutions: {len(solutions)}")
            else:
                print(f"  ❌ FAILED - {len(errors)} logic errors")
                
        except Exception as e:
            print(f"  ❌ EXCEPTION: {e}")


def test_edge_cases():
    """Test specific edge cases"""
    print("\n" + "="*70)
    print("EDGE CASE TESTING")
    print("="*70)
    
    test_cases = [
        ("Empty function", 4, [], []),
        ("All minterms", 3, list(range(8)), []),
        ("Single minterm", 5, [17], []),
        ("All but one", 3, [0,1,2,3,4,5,6], []),
        ("Only don't cares", 3, [], [0,1,2,3]),
        ("Powers of 2", 4, [1,2,4,8], []),
        ("Consecutive", 4, [5,6,7,8,9], []),
    ]
    
    passed = 0
    failed = 0
    
    for description, num_vars, minterms, dont_cares in test_cases:
        print(f"\nTesting: {description}")
        
        try:
            pis = generate_prime_implicants(minterms, dont_cares, num_vars)
            chart = build_pi_chart(pis, minterms)
            essential, indices = find_essential_pis(pis, chart)
            uncovered = get_uncovered_minterms(essential, minterms)
            solutions = find_minimal_covers(pis, chart, uncovered, indices)
            
            # Verify
            if minterms:  # Only verify if there are minterms
                success, errors = verify_correctness(num_vars, minterms, dont_cares,
                                                    pis, essential, solutions)
                if success:
                    print(f"  ✅ PASSED")
                    passed += 1
                else:
                    print(f"  ❌ FAILED - {len(errors)} logic errors")
                    failed += 1
            else:
                print(f"  ✅ PASSED (no minterms to verify)")
                passed += 1
                
        except Exception as e:
            print(f"  ❌ EXCEPTION: {e}")
            failed += 1
    
    print(f"\nEdge case results: {passed} passed, {failed} failed")


if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    
    # Run main fuzzing tests
    all_passed = run_fuzz_tests(num_tests=100, min_vars=2, max_vars=6)
    
    # Test edge cases
    test_edge_cases()
    
    # Stress test
    stress_test_large_cases()
    
    sys.exit(0 if all_passed else 1)