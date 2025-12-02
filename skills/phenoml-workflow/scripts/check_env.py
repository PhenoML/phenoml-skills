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

def is_shared_experiment():
    """Check if the user is on shared experiment (experiment.app.pheno.ml) based on PHENOML_BASE_URL"""
    base_url = os.getenv("PHENOML_BASE_URL", "")
    return "experiment" in base_url.lower()

def check_env_vars(env_file=None):
    """Check presence of required environment variables without exposing values"""
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    shared_experiment = is_shared_experiment()

    # Core credentials (always required)
    core_vars = {
        "PHENOML_USERNAME": bool(os.getenv("PHENOML_USERNAME")),
        "PHENOML_PASSWORD": bool(os.getenv("PHENOML_PASSWORD")),
        "PHENOML_BASE_URL": bool(os.getenv("PHENOML_BASE_URL"))
    }

    # FHIR provider credentials (required for dedicated instances, NOT for shared experiment)
    fhir_credentials = {
        "FHIR_PROVIDER_BASE_URL": bool(os.getenv("FHIR_PROVIDER_BASE_URL")),
        "FHIR_PROVIDER_CLIENT_ID": bool(os.getenv("FHIR_PROVIDER_CLIENT_ID")),
        "FHIR_PROVIDER_CLIENT_SECRET": bool(os.getenv("FHIR_PROVIDER_CLIENT_SECRET"))
    }

    # Generated IDs (created by scripts)
    # For shared experiment, FHIR_PROVIDER_ID defaults to "experiment-default"
    generated_ids = {
        "FHIR_PROVIDER_ID": bool(os.getenv("FHIR_PROVIDER_ID")) or shared_experiment,
        "WORKFLOW_ID": bool(os.getenv("WORKFLOW_ID"))
    }

    return {
        "core_credentials": core_vars,
        "fhir_credentials": fhir_credentials,
        "generated_ids": generated_ids,
        "shared_experiment": shared_experiment
    }

def print_status(status, verbose=False):
    """Print status in a user-friendly format"""

    def check_mark(present):
        return "✅" if present else "❌"

    shared_experiment = status.get("shared_experiment", False)

    print("\n" + "=" * 60)
    print("ENVIRONMENT VARIABLES STATUS")
    if shared_experiment:
        print("🧪 SHARED EXPERIMENT DETECTED (experiment.app.pheno.ml)")
    else:
        print("🏢 DEDICATED INSTANCE")
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
    if shared_experiment:
        print("\nFHIR Provider Credentials: (not required for shared experiment)")
        print("  ℹ️  Shared experiment uses pre-configured Medplum sandbox")
    else:
        print("\nFHIR Provider Credentials: (required for dedicated instance)")
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
    if shared_experiment:
        fhir_id_set = bool(os.getenv("FHIR_PROVIDER_ID"))
        if fhir_id_set:
            print(f"  {check_mark(True)} FHIR_PROVIDER_ID")
        else:
            print(f"  {check_mark(True)} FHIR_PROVIDER_ID (using shared experiment default)")
    else:
        print(f"  {check_mark(status['generated_ids']['FHIR_PROVIDER_ID'])} FHIR_PROVIDER_ID")
    print(f"  {check_mark(status['generated_ids']['WORKFLOW_ID'])} WORKFLOW_ID")

    if not shared_experiment and not status["generated_ids"]["FHIR_PROVIDER_ID"]:
        print("\n💡 Run setup_fhir_provider.py to create FHIR provider")
    if not status["generated_ids"]["WORKFLOW_ID"]:
        print("💡 Run create_workflow.py to create a workflow")

    # Overall status
    print("\n" + "=" * 60)
    if shared_experiment:
        if core_ready:
            print("✅ Shared experiment ready to create workflows!")
            print("   No FHIR provider setup needed - using Medplum sandbox")
        else:
            print("⚠️  Add missing core credentials to .env to proceed")
    else:
        fhir_ready = all(status["fhir_credentials"].values())
        if core_ready and fhir_ready:
            print("✅ Dedicated instance ready to create FHIR provider and workflows!")
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
    parser.add_argument(
        '--env-file',
        type=str,
        help='Path to .env file (defaults to .env in current directory)'
    )

    args = parser.parse_args()

    status = check_env_vars(env_file=args.env_file)

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print_status(status, verbose=args.verbose)

    # Exit with error code if core credentials are missing
    if not all(status["core_credentials"].values()):
        sys.exit(1)

if __name__ == "__main__":
    main()
