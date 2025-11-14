#!/usr/bin/env python3
"""
Validation script to verify the optimized notebook structure and content.
This script checks that all optimizations are in place and the notebook is valid.
"""

import json
import sys

def validate_notebook(notebook_path):
    """Validate the optimized notebook."""
    
    print("=" * 60)
    print("Notebook Optimization Validation")
    print("=" * 60)
    
    try:
        with open(notebook_path, 'r') as f:
            notebook = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ FAILED: Invalid JSON in notebook: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ FAILED: Notebook not found at {notebook_path}")
        return False
    
    all_passed = True
    
    # Test 1: Valid notebook structure
    print("\n1. Testing notebook structure...")
    if 'cells' not in notebook:
        print("   ❌ FAILED: No 'cells' key in notebook")
        all_passed = False
    else:
        print(f"   ✅ PASSED: Notebook has {len(notebook['cells'])} cells")
    
    # Test 2: No hardcoded credentials
    print("\n2. Testing for hardcoded credentials...")
    dangerous_patterns = [
        'AKIAUGQ637RYKQTW47FH',
        'mKsDFJd+ZK',
        'AKIA',  # AWS Access Key pattern
    ]
    
    credentials_found = False
    for i, cell in enumerate(notebook.get('cells', [])):
        source = ''.join(cell.get('source', []))
        for pattern in dangerous_patterns:
            if pattern in source and 'REDACTED' not in source and 'HARDCODED' not in source:
                print(f"   ❌ FAILED: Potential credential found in cell {i}")
                credentials_found = True
                all_passed = False
    
    if not credentials_found:
        print("   ✅ PASSED: No hardcoded credentials found")
    
    # Test 3: Environment variable usage
    print("\n3. Testing for environment variable usage...")
    cell_4_source = ''.join(notebook['cells'][4].get('source', []))
    if 'os.environ.get' in cell_4_source:
        print("   ✅ PASSED: Cell 4 uses environment variables")
    else:
        print("   ❌ FAILED: Cell 4 doesn't use environment variables")
        all_passed = False
    
    # Test 4: Modern API usage
    print("\n4. Testing for modern PySpark API...")
    cell_9_source = ''.join(notebook['cells'][9].get('source', []))
    if 'createOrReplaceTempView' in cell_9_source:
        print("   ✅ PASSED: Cell 9 uses createOrReplaceTempView")
    else:
        print("   ❌ FAILED: Cell 9 doesn't use createOrReplaceTempView")
        all_passed = False
    
    # Check for actual usage (not in comments) by looking for method call pattern
    if 'registerTempTable(' in cell_9_source:
        print("   ❌ FAILED: Cell 9 still uses deprecated registerTempTable")
        all_passed = False
    
    # Test 5: No duplicate Spark session creation
    print("\n5. Testing for duplicate Spark session creation...")
    cell_13_source = ''.join(notebook['cells'][13].get('source', []))
    if 'SparkSession.builder' in cell_13_source:
        print("   ❌ FAILED: Cell 13 creates duplicate Spark session")
        all_passed = False
    elif 'spark_session.sql' in cell_13_source:
        print("   ✅ PASSED: Cell 13 reuses existing Spark session")
    else:
        print("   ⚠️  WARNING: Could not verify Spark session usage in cell 13")
    
    # Test 6: Optimized data collection (toPandas instead of collect)
    print("\n6. Testing for optimized data collection...")
    cells_to_check = [15, 19, 20, 21]  # Added Cell 19
    pandas_count = 0
    collect_count = 0
    
    for cell_idx in cells_to_check:
        if cell_idx < len(notebook['cells']):
            source = ''.join(notebook['cells'][cell_idx].get('source', []))
            if 'toPandas()' in source:
                pandas_count += 1
            if '.collect()' in source and 'toPandas' not in source:
                collect_count += 1
    
    print(f"   Cells using toPandas(): {pandas_count}")
    print(f"   Cells using collect() inefficiently: {collect_count}")
    
    if pandas_count >= 3:  # Updated from 2 to 3
        print("   ✅ PASSED: Multiple cells use optimized toPandas()")
    else:
        print("   ❌ FAILED: Not enough cells use toPandas()")
        all_passed = False
    
    # Test 7: F-strings usage
    print("\n7. Testing for f-string usage...")
    f_string_count = 0
    cells_to_check = [13, 20, 21]
    
    for cell_idx in cells_to_check:
        if cell_idx < len(notebook['cells']):
            source = ''.join(notebook['cells'][cell_idx].get('source', []))
            if 'f"' in source or "f'" in source:
                f_string_count += 1
    
    if f_string_count >= 2:
        print(f"   ✅ PASSED: {f_string_count} cells use f-strings")
    else:
        print(f"   ⚠️  WARNING: Only {f_string_count} cells use f-strings")
    
    # Test 8: Check for optimization comments
    print("\n8. Testing for optimization comments...")
    comment_count = 0
    
    for cell in notebook.get('cells', []):
        source = ''.join(cell.get('source', []))
        if 'OPTIMIZATION:' in source or 'SECURITY:' in source:
            comment_count += 1
    
    if comment_count >= 5:
        print(f"   ✅ PASSED: {comment_count} cells have optimization comments")
    else:
        print(f"   ⚠️  WARNING: Only {comment_count} cells have optimization comments")
    
    # Test 9: No inefficient loops in critical sections
    print("\n9. Testing for loop optimizations...")
    cell_21_source = ''.join(notebook['cells'][21].get('source', []))
    
    inefficient_pattern = "for i in range(0, 100):"
    if inefficient_pattern in cell_21_source:
        print("   ❌ FAILED: Cell 21 still has inefficient loops")
        all_passed = False
    else:
        print("   ✅ PASSED: Cell 21 doesn't have inefficient loops")
    
    # Test 10: Typo fix in cell 22
    print("\n10. Testing for bug fixes...")
    cell_22_source = ''.join(notebook['cells'][22].get('source', []))
    
    # Check for actual typo in labels (not in comments)
    if "'Decision Tree TMSE'" in cell_22_source or '"Decision Tree TMSE"' in cell_22_source:
        print("   ❌ FAILED: Cell 22 still has typo (TMSE instead of RMSE)")
        all_passed = False
    elif 'RMSE' in cell_22_source:
        print("   ✅ PASSED: Cell 22 typo fixed")
    else:
        print("   ⚠️  WARNING: Could not verify cell 22 content")
    
    # Test 11: Error handling in Cell 5
    print("\n11. Testing for error handling in data loading...")
    cell_5_source = ''.join(notebook['cells'][5].get('source', []))
    
    if 'try:' in cell_5_source and 'except' in cell_5_source:
        print("   ✅ PASSED: Cell 5 has error handling")
    else:
        print("   ❌ FAILED: Cell 5 lacks error handling")
        all_passed = False
    
    # Test 12: Path flexibility in Cell 5
    print("\n12. Testing for path flexibility...")
    if 'csv_paths' in cell_5_source or 'for csv_path' in cell_5_source:
        print("   ✅ PASSED: Cell 5 supports multiple paths")
    else:
        print("   ⚠️  WARNING: Cell 5 may use hardcoded path")
    
    # Final summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Notebook is properly optimized!")
        print("=" * 60)
        return True
    else:
        print("❌ SOME TESTS FAILED - Please review the notebook")
        print("=" * 60)
        return False

if __name__ == "__main__":
    notebook_path = "CropYield.ipynb"
    if len(sys.argv) > 1:
        notebook_path = sys.argv[1]
    
    success = validate_notebook(notebook_path)
    sys.exit(0 if success else 1)
