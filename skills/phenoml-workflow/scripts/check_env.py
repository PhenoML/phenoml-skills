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

def get_instance_type():
    """
    Determine instance type based on PHENOML_BASE_URL.
    Returns: "shared_experiment", "dedicated", or "unknown"
    """
    base_url = os.getenv("PHENOML_BASE_URL", "")
    if not base_url:
        return "unknown"
    if "experiment" in base_url.lower():
        return "shared_experiment"
    return "dedicated"

def check_env_vars(env_file=None):
    """Check presence of required environment variables without exposing values"""
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    instance_type = get_instance_type()
    is_shared = instance_type == "shared_experiment"

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
        "FHIR_PROVIDER_ID": bool(os.getenv("FHIR_PROVIDER_ID")) or is_shared,
        "WORKFLOW_ID": bool(os.getenv("WORKFLOW_ID"))
    }

    return {
        "core_credentials": core_vars,
        "fhir_credentials": fhir_credentials,
        "generated_ids": generated_ids,
        "instance_type": instance_type
    }

def print_status(status, verbose=False):
    """Print status in a user-friendly format"""

    def check_mark(present):
        return "✅" if present else "❌"

    instance_type = status.get("instance_type", "unknown")
    is_shared = instance_type == "shared_experiment"
    is_dedicated = instance_type == "dedicated"
    is_unknown = instance_type == "unknown"

    print("\n" + "=" * 60)
    print("ENVIRONMENT VARIABLES STATUS")
    if is_shared:
        print("🧪 SHARED EXPERIMENT DETECTED (experiment.app.pheno.ml)")
    elif is_dedicated:
        print("🏢 DEDICATED INSTANCE")
    else:
        print("❓ INSTANCE TYPE UNKNOWN (PHENOML_BASE_URL not set)")
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
        print("\n   Example PHENOML_BASE_URL values:")
        print("   - Shared experiment: https://experiment.app.pheno.ml")
        print("   - Dedicated instance: https://yourcompany.app.pheno.ml")

    # FHIR credentials
    if is_shared:
        print("\nFHIR Provider Credentials: (not required for shared experiment)")
        print("  ℹ️  Shared experiment uses pre-configured Medplum sandbox")
    elif is_unknown:
        print("\nFHIR Provider Credentials: (status depends on instance type)")
        for key, present in status["fhir_credentials"].items():
            print(f"  {check_mark(present)} {key}")
        print("\n  ℹ️  Set PHENOML_BASE_URL first to determine if FHIR credentials are needed")
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
    if is_shared:
        fhir_id_set = bool(os.getenv("FHIR_PROVIDER_ID"))
        if fhir_id_set:
            print(f"  {check_mark(True)} FHIR_PROVIDER_ID")
        else:
            print(f"  {check_mark(True)} FHIR_PROVIDER_ID (using shared experiment default)")
    else:
        print(f"  {check_mark(status['generated_ids']['FHIR_PROVIDER_ID'])} FHIR_PROVIDER_ID")
    print(f"  {check_mark(status['generated_ids']['WORKFLOW_ID'])} WORKFLOW_ID")

    if is_dedicated and not status["generated_ids"]["FHIR_PROVIDER_ID"]:
        print("\n💡 Run setup_fhir_provider.py to create FHIR provider")
    if not status["generated_ids"]["WORKFLOW_ID"]:
        print("💡 Run create_workflow.py to create a workflow")

    # Overall status
    print("\n" + "=" * 60)
    if is_unknown:
        print("⚠️  Set PHENOML_BASE_URL to determine instance type and requirements")
    elif is_shared:
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
