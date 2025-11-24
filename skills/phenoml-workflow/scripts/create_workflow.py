#!/usr/bin/env python3
"""
Workflow Creation Script

Creates a PhenoML workflow using configuration from .env or CLI arguments.

Usage:
  python3 create_workflow.py
  python3 create_workflow.py --name "My Workflow" --instructions "..." --sample-data '{"key": "value"}'
  python3 create_workflow.py --help

Required .env variables:
  PHENOML_USERNAME, PHENOML_PASSWORD, PHENOML_BASE_URL
  FHIR_PROVIDER_ID (from setup_fhir_provider.py)

Workflow configuration (.env or CLI args):
  WORKFLOW_NAME or --name
  WORKFLOW_INSTRUCTIONS or --instructions
  WORKFLOW_SAMPLE_DATA (JSON string) or --sample-data

Optional:
  WORKFLOW_DYNAMIC_GENERATION (true/false) or --dynamic-generation
  WORKFLOW_VERBOSE (true/false) or --verbose
"""

import os
import sys
import json
import argparse
from phenoml import Client
from dotenv import load_dotenv

def save_to_env(key, value):
    """Save or update a key-value pair in .env file"""
    env_file = ".env"

    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write(f"{key}={value}\n")
        return

    with open(env_file, 'r') as f:
        lines = f.readlines()

    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            found = True
            break

    if not found:
        if lines and not lines[-1].endswith('\n'):
            lines.append('\n')
        lines.append(f"{key}={value}\n")

    with open(env_file, 'w') as f:
        f.writelines(lines)

def str_to_bool(s):
    """Convert string to boolean"""
    return s.lower() in ('true', '1', 'yes', 'y')

def main():
    parser = argparse.ArgumentParser(description='Create a PhenoML workflow')
    parser.add_argument('--name', help='Workflow name')
    parser.add_argument('--instructions', help='Workflow instructions')
    parser.add_argument('--sample-data', help='Sample data as JSON string')
    parser.add_argument('--dynamic-generation', type=str_to_bool, help='Enable dynamic generation (true/false)')
    parser.add_argument('--verbose', type=str_to_bool, help='Verbose mode (true/false)')
    parser.add_argument('--provider-id', help='FHIR provider ID (overrides .env)')

    args = parser.parse_args()

    # Load environment
    load_dotenv()

    # Get configuration (CLI args override .env)
    name = args.name or os.getenv("WORKFLOW_NAME")
    instructions = args.instructions or os.getenv("WORKFLOW_INSTRUCTIONS")
    sample_data_str = args.sample_data or os.getenv("WORKFLOW_SAMPLE_DATA")
    dynamic_generation = args.dynamic_generation if args.dynamic_generation is not None else str_to_bool(os.getenv("WORKFLOW_DYNAMIC_GENERATION", "true"))
    verbose = args.verbose if args.verbose is not None else str_to_bool(os.getenv("WORKFLOW_VERBOSE", "false"))
    provider_id = args.provider_id or os.getenv("FHIR_PROVIDER_ID")

    # Validate required fields
    if not name:
        print("❌ Error: Workflow name is required")
        print("   Set WORKFLOW_NAME in .env, or use --name")
        sys.exit(1)

    if not instructions:
        print("❌ Error: Workflow instructions are required")
        print("   Set WORKFLOW_INSTRUCTIONS in .env, or use --instructions")
        sys.exit(1)

    if not sample_data_str:
        print("❌ Error: Sample data is required")
        print("   Set WORKFLOW_SAMPLE_DATA in .env, or use --sample-data")
        sys.exit(1)

    if not provider_id:
        print("❌ Error: FHIR provider ID is required")
        print("   Run setup_fhir_provider.py first, or use --provider-id")
        sys.exit(1)

    # Parse sample data
    try:
        sample_data = json.loads(sample_data_str)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in sample data: {e}")
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

    # Create workflow
    print(f"Creating workflow:")
    print(f"  Name: {name}")
    print(f"  Provider ID: {provider_id}")
    print(f"  Dynamic generation: {dynamic_generation}")
    print(f"  Verbose: {verbose}")
    print(f"  Sample data: {json.dumps(sample_data, indent=2)}\n")

    try:
        workflow = client.workflows.create(
            name=name,
            workflow_instructions=instructions,
            sample_data=sample_data,
            fhir_provider_id=provider_id,
            verbose=verbose,
            dynamic_generation=dynamic_generation
        )

        workflow_id = workflow.workflow_id
        print(f"✅ Workflow created successfully!")
        print(f"   Workflow ID: {workflow_id}\n")

        # Save to .env
        save_to_env("WORKFLOW_ID", workflow_id)
        print(f"💾 Workflow ID saved to .env")
        print(f"\n🎉 Workflow creation complete! You can now test it with test_workflow.py")

    except Exception as e:
        print(f"❌ Failed to create workflow: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
