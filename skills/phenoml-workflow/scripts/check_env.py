#!/usr/bin/env python3
"""
Environment Variables Checker

Safely checks which environment variables are set without exposing their values.
This prevents accidental credential leakage in LLM conversations.

Usage:
  python3 check_env.py
  python3 check_env.py --help

Security: This script only reports presence (true/false), never actual values.
"""

import os
import sys
import json
import argparse
from dotenv import load_dotenv

def check_env_vars():
    """Check presence of required environment variables without exposing values"""
    load_dotenv()

    # Core credentials (always required)
    core_vars = {
        "PHENOML_USERNAME": bool(os.getenv("PHENOML_USERNAME")),
        "PHENOML_PASSWORD": bool(os.getenv("PHENOML_PASSWORD")),
        "PHENOML_BASE_URL": bool(os.getenv("PHENOML_BASE_URL"))
    }

    # FHIR provider credentials (required for setup)
    fhir_credentials = {
        "FHIR_PROVIDER_BASE_URL": bool(os.getenv("FHIR_PROVIDER_BASE_URL")),
        "FHIR_PROVIDER_CLIENT_ID": bool(os.getenv("FHIR_PROVIDER_CLIENT_ID")),
        "FHIR_PROVIDER_CLIENT_SECRET": bool(os.getenv("FHIR_PROVIDER_CLIENT_SECRET"))
    }

    # Generated IDs (created by scripts)
    generated_ids = {
        "FHIR_PROVIDER_ID": bool(os.getenv("FHIR_PROVIDER_ID")),
        "WORKFLOW_ID": bool(os.getenv("WORKFLOW_ID"))
    }

    return {
        "core_credentials": core_vars,
        "fhir_credentials": fhir_credentials,
        "generated_ids": generated_ids
    }

def print_status(status, verbose=False):
    """Print status in a user-friendly format"""

    def check_mark(present):
        return "✅" if present else "❌"

    print("\n" + "=" * 60)
    print("ENVIRONMENT VARIABLES STATUS")
    print("=" * 60 + "\n")

    # Core credentials
    print("Core PhenoML Credentials:")
    for key, present in status["core_credentials"].items():
        print(f"  {check_mark(present)} {key}")

    core_ready = all(status["core_credentials"].values())
    if not core_ready:
        print("\n⚠️  Missing core credentials. Add them to .env file:")
        print("   PHENOML_USERNAME=your_username")
        print("   PHENOML_PASSWORD=your_password")
        print("   PHENOML_BASE_URL=your_base_url")

    # FHIR credentials
    print("\nFHIR Provider Credentials:")
    for key, present in status["fhir_credentials"].items():
        print(f"  {check_mark(present)} {key}")

    fhir_ready = all(status["fhir_credentials"].values())
    if not fhir_ready:
        print("\n⚠️  Missing FHIR credentials. Add them to .env file:")
        print("   FHIR_PROVIDER_BASE_URL=https://api.medplum.com/fhir/R4")
        print("   FHIR_PROVIDER_CLIENT_ID=your_client_id")
        print("   FHIR_PROVIDER_CLIENT_SECRET=your_client_secret")

    # Generated IDs
    print("\nGenerated IDs:")
    for key, present in status["generated_ids"].items():
        print(f"  {check_mark(present)} {key}")

    if not status["generated_ids"]["FHIR_PROVIDER_ID"]:
        print("\n💡 Run setup_fhir_provider.py to create FHIR provider")
    if not status["generated_ids"]["WORKFLOW_ID"]:
        print("💡 Run create_workflow.py to create a workflow")

    # Overall status
    print("\n" + "=" * 60)
    if core_ready and fhir_ready:
        print("✅ Ready to create FHIR provider and workflows!")
    elif core_ready:
        print("✅ Core credentials ready")
        print("⚠️  Add FHIR credentials to proceed with provider setup")
    else:
        print("⚠️  Add missing credentials to .env to proceed")
    print("=" * 60 + "\n")

    if verbose:
        print("\nJSON Output:")
        print(json.dumps(status, indent=2))

def main():
    parser = argparse.ArgumentParser(
        description='Check environment variable status without exposing values'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format only'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Include JSON output with formatted output'
    )

    args = parser.parse_args()

    status = check_env_vars()

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print_status(status, verbose=args.verbose)

    # Exit with error code if core credentials are missing
    if not all(status["core_credentials"].values()):
        sys.exit(1)

if __name__ == "__main__":
    main()
