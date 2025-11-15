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

## PROJECT GITHUB REPO LINK
https://github.com/Moaz-Allam/Quine-McCluskey-Simulator.git

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

We have two main directories `./simple_test_cases/` and `./Complex_test_cases/`. Each directory has 10 testcases. The expected output for both simple and complex testcases are in a .txt files to verfy the program output. Created the expected output for complex testcases using the Claude AI tool. 

LIMITATIONS
================================================================================
- Very large functions (15+ variables with many minterms) may take 
  significant processing time
- Maximum search depth limited to prevent infinite loops in complex cases
- Console output only (no GUI)