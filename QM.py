import sys
from itertools import combinations

def decimal_to_binary(num, num_vars):
    """Convert decimal number to binary string of specified length."""
    return format(num, f'0{num_vars}b')

def count_ones(binary_str):
    """Count number of '1's in binary string."""
    return binary_str.count('1')

def can_combine(term1, term2):
    """Check if two terms differ by exactly one bit."""
    if len(term1) != len(term2):
        return False
    
    diff_count = 0
    for i in range(len(term1)):
        if term1[i] != term2[i]:
            if term1[i] == '-' or term2[i] == '-':
                return False
            diff_count += 1
    
    return diff_count == 1

def combine_terms(term1, term2, minterms1, minterms2):
    """Combine two terms that differ by one bit."""
    new_binary = ""
    for i in range(len(term1)):
        if term1[i] == term2[i]:
            new_binary += term1[i]
        else:
            new_binary += '-'
    
    new_minterms = minterms1.union(minterms2)
    return new_binary, new_minterms

def generate_prime_implicants(minterms, dont_cares, num_vars):
    """Generate all prime implicants using Quine-McCluskey algorithm."""
    # Combine minterms and don't cares
    all_terms = minterms + dont_cares
    
    # Create initial terms: (binary_string, set_of_minterms)
    current_terms = []
    for term in all_terms:
        binary = decimal_to_binary(term, num_vars)
        current_terms.append((binary, {term}))
    
    prime_implicants = []
    
    # Iteratively combine terms
    while current_terms:
        # Group by number of ones
        groups = {}
        for binary, mins in current_terms:
            ones = count_ones(binary)
            if ones not in groups:
                groups[ones] = []
            groups[ones].append((binary, mins))
        
        next_terms = []
        seen_binaries = set()
        used_terms = set()  # Track which binary strings were combined
        
        # Combine terms between adjacent groups
        sorted_ones = sorted(groups.keys())
        for ones in sorted_ones:
            if ones + 1 in groups:
                for bin1, mins1 in groups[ones]:
                    for bin2, mins2 in groups[ones + 1]:
                        if can_combine(bin1, bin2):
                            # Mark both terms as used
                            used_terms.add(bin1)
                            used_terms.add(bin2)
                            
                            # Combine
                            new_bin, new_mins = combine_terms(bin1, bin2, mins1, mins2)
                            
                            if new_bin not in seen_binaries:
                                next_terms.append((new_bin, new_mins))
                                seen_binaries.add(new_bin)
        
        # Add unused terms to prime implicants
        for binary, mins in current_terms:
            if binary not in used_terms:
                # Check if already in prime implicants
                already_exists = False
                for pi_binary, pi_mins in prime_implicants:
                    if pi_binary == binary:
                        already_exists = True
                        break
                
                if not already_exists:
                    prime_implicants.append((binary, mins))
        
        current_terms = next_terms
    
    # Sort by first minterm for consistent output
    prime_implicants.sort(key=lambda x: min(x[1]))
    
    return prime_implicants

def build_pi_chart(prime_implicants, minterms):
    """Build prime implicant chart mapping minterms to PI indices."""
    pi_chart = {m: [] for m in minterms}
    
    for idx, (binary, mins) in enumerate(prime_implicants):
        for m in mins:
            if m in minterms:
                pi_chart[m].append(idx)
    
    return pi_chart

def find_essential_pis(prime_implicants, pi_chart):
    """Find essential prime implicants."""
    essential_indices = set()
    
    for minterm, pi_indices in pi_chart.items():
        if len(pi_indices) == 1:
            essential_indices.add(pi_indices[0])
    
    essential_pis = [prime_implicants[idx] for idx in sorted(essential_indices)]
    return essential_pis, essential_indices

def get_uncovered_minterms(essential_pis, minterms):
    """Find minterms not covered by essential PIs."""
    covered = set()
    for binary, mins in essential_pis:
        for m in mins:
            if m in minterms:
                covered.add(m)
    
    uncovered = set(minterms) - covered
    return uncovered

def term_to_expression(binary, num_vars):
    """Convert binary term to Boolean expression."""
    var_names = [chr(ord('A') + i) for i in range(num_vars)]
    expr = ""
    
    for i in range(len(binary)):
        if binary[i] == '1':
            expr += var_names[i]
        elif binary[i] == '0':
            expr += var_names[i] + "'"
    
    return expr if expr else "1"

def term_to_verilog(binary, num_vars):
    """Convert binary term to Verilog expression."""
    var_names = [chr(ord('a') + i) for i in range(num_vars)]
    parts = []
    
    for i in range(len(binary)):
        if binary[i] == '1':
            parts.append(var_names[i])
        elif binary[i] == '0':
            parts.append(f"~{var_names[i]}")
    
    if not parts:
        return "1'b1"
    return " & ".join(parts)

def generate_verilog(prime_implicants, essential_pis, solutions, num_vars, testcase_num):
    """Generate Verilog module for the minimized expression."""
    var_names = [chr(ord('a') + i) for i in range(num_vars)]
    
    # Use first solution
    if not solutions:
        solution = []
    else:
        solution = solutions[0]
    
    verilog_code = f"module boolean_function_{testcase_num} (\n"
    verilog_code += f"    input {', '.join(var_names)},\n"
    verilog_code += f"    output x\n"
    verilog_code += f");\n\n"
    
    # Collect all terms
    terms = []
    
    # Add essential PIs
    for binary, mins in essential_pis:
        terms.append(term_to_verilog(binary, num_vars))
    
    # Add selected PIs
    for pi_idx in solution:
        binary, mins = prime_implicants[pi_idx]
        terms.append(term_to_verilog(binary, num_vars))
    
    if not terms:
        verilog_code += f"    assign x = 1'b0;\n"
    else:
        verilog_code += f"    assign x = "
        verilog_code += " |\n                   ".join(f"({term})" for term in terms)
        verilog_code += ";\n"
    
    verilog_code += f"\nendmodule\n"
    
    return verilog_code

def find_minimal_covers(prime_implicants, pi_chart, uncovered_minterms, 
                        essential_indices, max_depth=15):
    """Find all minimal covers for uncovered minterms using backtracking."""
    if not uncovered_minterms:
        return [[]]
    
    # Get non-essential PIs that cover uncovered minterms
    covering_pis = {}
    for m in uncovered_minterms:
        covering_pis[m] = [idx for idx in pi_chart[m] if idx not in essential_indices]
    
    solutions = []
    
    def backtrack(current_solution, current_covered, depth):
        nonlocal solutions
        
        # All covered - found a solution
        if len(current_covered) == len(uncovered_minterms):
            if not solutions or len(current_solution) <= len(solutions[0]):
                if solutions and len(current_solution) < len(solutions[0]):
                    solutions.clear()
                solutions.append(current_solution[:])
            return
        
        # Pruning
        if solutions and len(current_solution) >= len(solutions[0]):
            return
        
        if depth > max_depth:
            return
        
        # Find an uncovered minterm
        uncovered = None
        for m in uncovered_minterms:
            if m not in current_covered:
                uncovered = m
                break
        
        if uncovered is None:
            return
        
        # Try each PI that covers this minterm
        for pi_idx in covering_pis[uncovered]:
            if pi_idx in current_solution:
                continue
            
            # Add this PI
            current_solution.append(pi_idx)
            new_covered = current_covered.copy()
            
            for m in prime_implicants[pi_idx][1]:
                if m in uncovered_minterms:
                    new_covered.add(m)
            
            backtrack(current_solution, new_covered, depth + 1)
            current_solution.pop()
    
    backtrack([], set(), 0)
    return solutions

def print_results(prime_implicants, essential_pis, essential_indices, 
                 uncovered_minterms, solutions, num_vars):
    """Print all results."""
    print("\n=== PRIME IMPLICANTS ===")
    for idx, (binary, mins) in enumerate(prime_implicants):
        minterms_str = ", ".join(map(str, sorted(mins)))
        expr = term_to_expression(binary, num_vars)
        print(f"PI{idx + 1}: {binary} | Covers minterms: {minterms_str} | Expression: {expr}")
    
    print("\n=== ESSENTIAL PRIME IMPLICANTS ===")
    if not essential_pis:
        print("None")
    else:
        for binary, mins in essential_pis:
            print(term_to_expression(binary, num_vars))
    
    print("\n=== UNCOVERED MINTERMS ===")
    if not uncovered_minterms:
        print("None (all minterms covered by essential PIs)")
    else:
        print(", ".join(map(str, sorted(uncovered_minterms))))
    
    print("\n=== MINIMIZED BOOLEAN EXPRESSION(S) ===")
    for sol_idx, solution in enumerate(solutions):
        print(f"Solution {sol_idx + 1}: F = ", end="")
        
        terms = []
        
        # Add essential PIs
        for binary, mins in essential_pis:
            terms.append(term_to_expression(binary, num_vars))
        
        # Add selected PIs
        for pi_idx in solution:
            binary, mins = prime_implicants[pi_idx]
            terms.append(term_to_expression(binary, num_vars))
        
        if not terms:
            print("0")
        else:
            print(" + ".join(terms))

def parse_input_file(filename):
    """Parse input file and return num_vars, minterms, and don't cares."""
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
        
        if len(lines) < 2:
            print("Error: File must have at least 2 lines")
            return None, None, None
        
        # Read number of variables
        num_vars = int(lines[0])
        if num_vars < 1 or num_vars > 20:
            print("Error: Number of variables must be between 1 and 20")
            return None, None, None
        
        # Read minterms or maxterms
        is_maxterm = False
        minterms = []
        
        tokens = lines[1].split(',')
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            
            if token[0] == 'M':
                is_maxterm = True
            
            if token[0] in ['m', 'M']:
                val = int(token[1:])
                if val < 0 or val >= (2 ** num_vars):
                    print(f"Error: Term {val} out of range")
                    return None, None, None
                minterms.append(val)
        
        # Convert maxterms to minterms
        if is_maxterm:
            maxterm_set = set(minterms)
            minterms = [i for i in range(2 ** num_vars) if i not in maxterm_set]
        
        # Read don't cares
        dont_cares = []
        if len(lines) > 2 and lines[2]:
            tokens = lines[2].split(',')
            for token in tokens:
                token = token.strip()
                if not token:
                    continue
                
                if token[0] in ['d', 'D']:
                    val = int(token[1:])
                    if val < 0 or val >= (2 ** num_vars):
                        print(f"Error: Don't care {val} out of range")
                        return None, None, None
                    dont_cares.append(val)
        
        return num_vars, minterms, dont_cares
    
    except FileNotFoundError:
        print(f"Error: Cannot open file {filename}")
        return None, None, None
    except ValueError as e:
        print(f"Error: Invalid input format - {e}")
        return None, None, None

def parse_testcase_input(input_str):
    """Parse test case input string and return list of test case numbers.
    
    Supports:
    - Individual numbers: "1 3 5 4" -> [1, 3, 5, 4]
    - Ranges: "1-5" -> [1, 2, 3, 4, 5]
    - Mixed: "1 3-5 7" -> [1, 3, 4, 5, 7]
    """
    testcases = []
    parts = input_str.replace(',', ' ').split()
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        if '-' in part:
            # Handle range
            try:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                if start > end:
                    start, end = end, start
                testcases.extend(range(start, end + 1))
            except ValueError:
                print(f"Warning: Invalid range '{part}', skipping")
        else:
            # Handle individual number
            try:
                testcases.append(int(part))
            except ValueError:
                print(f"Warning: Invalid number '{part}', skipping")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_testcases = []
    for tc in testcases:
        if tc not in seen:
            seen.add(tc)
            unique_testcases.append(tc)
    
    return unique_testcases

def process_testcase(testcase_num):
    """Process a single test case."""
    filename = f"./complex_test_cases/test{testcase_num}.txt"
    # filename = f"./test_cases/test{testcase_num}.txt"
    
    # Parse input
    num_vars, minterms, dont_cares = parse_input_file(filename)
    
    if num_vars is None:
        return False
    
    # Print input
    print(f"Number of variables: {num_vars}")
    print(f"Minterms: {', '.join(map(str, minterms))}")
    print(f"Don't cares: {', '.join(map(str, dont_cares)) if dont_cares else 'None'}")
    
    # Generate prime implicants
    prime_implicants = generate_prime_implicants(minterms, dont_cares, num_vars)
    
    # Build PI chart
    pi_chart = build_pi_chart(prime_implicants, minterms)
    
    # Find essential PIs
    essential_pis, essential_indices = find_essential_pis(prime_implicants, pi_chart)
    
    # Find uncovered minterms
    uncovered_minterms = get_uncovered_minterms(essential_pis, minterms)
    
    # Find minimal covers
    solutions = find_minimal_covers(prime_implicants, pi_chart, uncovered_minterms, 
                                   essential_indices)
    
    if not solutions and not uncovered_minterms:
        solutions = [[]]
    
    # Print results
    print_results(prime_implicants, essential_pis, essential_indices, 
                 uncovered_minterms, solutions, num_vars)
    
    # Generate Verilog
    verilog_code = generate_verilog(prime_implicants, essential_pis, solutions, 
                                    num_vars, testcase_num)
    
    print("\n=== VERILOG CODE ===")
    print(verilog_code)
    
    # Save Verilog to file
    verilog_filename = f"boolean_function_{testcase_num}.v"
    try:
        with open(verilog_filename, 'w') as f:
            f.write(verilog_code)
        print(f"\nVerilog code saved to: {verilog_filename}")
    except IOError as e:
        print(f"\nWarning: Could not save Verilog file: {e}")
    
    return True

def main():
    """Main function."""
    # Get testcase numbers
    testcase_input = input("Enter testcase number(s): ").strip()
    
    testcases = parse_testcase_input(testcase_input)
    
    if not testcases:
        print("Error: No valid test cases specified")
        return 1
    
    print(f"\nProcessing {len(testcases)} test case(s): {testcases}\n")
    
    success_count = 0
    failed_cases = []
    
    for idx, testcase_num in enumerate(testcases):
        if len(testcases) > 1:
            print("=" * 80)
            print(f"TESTCASE {testcase_num} ({idx + 1}/{len(testcases)})")
            print("=" * 80)
        
        success = process_testcase(testcase_num)
        
        if success:
            success_count += 1
        else:
            failed_cases.append(testcase_num)
        
        if idx < len(testcases) - 1:
            print("\n")
    
    # Summary
    if len(testcases) > 1:
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total test cases: {len(testcases)}")
        print(f"Successful: {success_count}")
        print(f"Failed: {len(failed_cases)}")
        if failed_cases:
            print(f"Failed cases: {failed_cases}")
    
    return 0 if not failed_cases else 1

if __name__ == "__main__":
    exit(main())