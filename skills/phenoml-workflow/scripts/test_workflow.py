#!/usr/bin/env python3
"""
Workflow Testing Script

Tests a PhenoML workflow using test data from .env, CLI arguments, or a JSON file.

Usage:
  python3 test_workflow.py
  python3 test_workflow.py --workflow-id abc123 --input-data '{"patient": "Smith"}'
  python3 test_workflow.py --input-file test_data.json
  python3 test_workflow.py --help

Required .env variables:
  PHENOML_USERNAME, PHENOML_PASSWORD, PHENOML_BASE_URL

Test configuration (.env or CLI args):
  WORKFLOW_ID or --workflow-id
  WORKFLOW_TEST_DATA (JSON string) or --input-data or --input-file
"""

import os
import sys
import json
import argparse
from phenoml import Client
from dotenv import load_dotenv

def main():
    parser = argparse.ArgumentParser(description='Test a PhenoML workflow')
    parser.add_argument('--workflow-id', help='Workflow ID to test')
    parser.add_argument('--input-data', help='Input data as JSON string')
    parser.add_argument('--input-file', help='Path to JSON file with input data')
    parser.add_argument('--output-file', help='Save results to JSON file')

    args = parser.parse_args()

    # Load environment
    load_dotenv()

    # Get configuration (CLI args override .env)
    workflow_id = args.workflow_id or os.getenv("WORKFLOW_ID")

    # Validate workflow ID
    if not workflow_id:
        print("❌ Error: Workflow ID is required")
        print("   Set WORKFLOW_ID in .env, or use --workflow-id")
        sys.exit(1)

    # Get input data from various sources
    input_data = None

    if args.input_file:
        # Load from file
        try:
            with open(args.input_file, 'r') as f:
                input_data = json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: File not found: {args.input_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in file {args.input_file}: {e}")
            sys.exit(1)
    elif args.input_data:
        # Parse from CLI arg
        try:
            input_data = json.loads(args.input_data)
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in input data: {e}")
            sys.exit(1)
    else:
        # Try to load from .env
        test_data_str = os.getenv("WORKFLOW_TEST_DATA")
        if test_data_str:
            try:
                input_data = json.loads(test_data_str)
            except json.JSONDecodeError as e:
                print(f"❌ Error: Invalid JSON in WORKFLOW_TEST_DATA: {e}")
                sys.exit(1)

    if not input_data:
        print("❌ Error: Input data is required")
        print("   Set WORKFLOW_TEST_DATA in .env, use --input-data, or use --input-file")
        sys.exit(1)

    # Initialize PhenoML client
    print("Initializing PhenoML client...")
    try:
        client = Client(
            username=os.getenv("PHENOML_USERNAME"),
            password=os.getenv("PHENOML_PASSWORD"),
            base_url=os.getenv("PHENOML_BASE_URL")
        )
        print("✅ PhenoML client initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize PhenoML client: {e}")
        print("   Make sure PHENOML_USERNAME, PHENOML_PASSWORD, and PHENOML_BASE_URL are set in .env")
        sys.exit(1)

    # Execute workflow
    print(f"Testing workflow:")
    print(f"  Workflow ID: {workflow_id}")
    print(f"  Input data:")
    print(json.dumps(input_data, indent=4))
    print("\n⏳ Executing workflow (this may take a moment)...\n")

    try:
        result = client.workflows.execute(
            id=workflow_id,
            input_data=input_data
        )

        print("✅ Workflow executed successfully!\n")
        print("=" * 60)
        print("EXECUTION RESULTS")
        print("=" * 60)

        result_dict = result.model_dump()
        print(json.dumps(result_dict, indent=2))

        # Save to file if requested
        if args.output_file:
            with open(args.output_file, 'w') as f:
                json.dump(result_dict, f, indent=2)
            print(f"\n💾 Results saved to {args.output_file}")

        print("\n🎉 Test complete!")

    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
