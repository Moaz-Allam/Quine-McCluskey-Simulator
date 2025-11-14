QUINE-McCLUSKEY LOGIC MINIMIZATION PROGRAM

## PROJECT DESCRIPTION

This program implements the Quine–McCluskey algorithm for minimizing Boolean
functions. It supports:

* Boolean functions with up to 20 variables
* Minterm and maxterm notation
* Don't-care conditions
* Generation of prime implicants and essential prime implicants
* Finding minimal Boolean expressions
* Verilog HDL generation

## TEAM MEMBERS

* Moaz Allam         —  900231984
* Karim El Henawy    —  900231975
* Zyad Maher         —  900232155

## FILE STRUCTURE (relevant parts)

```
project/
├── qm.py
├── README.md        <-- this file
├── test_cases/
│   └── test1.txt ... test10.txt
├── complex_test_cases/
│   └── test1.txt ... test10.txt
└── testing/
    ├── test_qm_unit.py
    ├── test_integration.py
    ├── test_truth_table.py
    └── test_fuzzing.py
```

---

## USAGE (Run the program)

1. Open a terminal/command prompt in the project directory.
2. Run the main program:

```bash
python qm.py
```

3. When prompted, enter testcase numbers (e.g. `1-10` or `1 2 3`).

---

# TESTING

The testing package is included under `./testing/`:

* `test_qm_unit.py` — unit tests for individual functions (conversion, grouping, combination, PI generation, essential PI detection, formatting).
* `test_integration.py` — integration tests that run full workflows end-to-end using representative test cases.
* `test_truth_table.py` — exhaustive truth-table verification: for given input specifications it verifies the minimized solution is functionally equivalent over all `2^n` input combinations (the gold standard).
* `test_fuzzing.py` — randomized input generation and verification to find edge cases and ensure robustness.

### How to run the testing package

```powershell
python .\testing\test_qm_uni.py
python .\testing\test_integration.py.py
python .\testing\test_truth_table.py
python .\testing\test_fuzzing.py
```

> These commands executes the four test suites above (`test_qm_unit.py`, `test_integration.py`, `test_truth_table.py`, `test_fuzzing.py`) and prints a consolidated result summary to the console.

### What each test checks 

* **Unit tests (`test_qm_unit.py`)**

  * Binary conversions and formatting
  * Grouping by bit-count
  * Term combination correctness
  * Prime implicant generation correctness
  * Utility function edge cases

* **Integration tests (`test_integration.py`)**

  * Full QM workflow on textbook and complex examples
  * Correct handling of don't-cares and maxterms
  * Output formatting and Verilog generation sanity checks

* **Truth table verification (`test_truth_table.py`)**

  * For every candidate solution, evaluate the minimized expression against the original function for all 2^n input combinations
  * Ensures functional equivalence (no false positives/negatives)

* **Fuzzing (`test_fuzzing.py`)**

  * Generates randomized cases (variable count, minterms, don't-cares)
  * Verifies results with truth-table check / reference evaluator
  * Detects crashes, inconsistent outputs, and edge-case

LIMITATIONS
================================================================================
- Very large functions (15+ variables with many minterms) may take 
  significant processing time
- Maximum search depth limited to prevent infinite loops in complex cases
- Console output only (no GUI)