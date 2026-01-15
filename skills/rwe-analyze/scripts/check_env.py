#!/usr/bin/env python3
"""
Environment Variables Checker for RWE Analysis Skill

Checks whether required PhenoML credentials are configured without
revealing their actual values. This prevents accidental credential
leakage in LLM conversations.

Usage:
    python check_env.py [--json] [--verbose] [--env-file .env]
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("Error: python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)


def get_instance_type(base_url: str | None) -> str:
    """Determine if using shared experiment or dedicated instance."""
    if not base_url:
        return "unknown"
    if "experiment" in base_url.lower():
        return "shared"
    return "dedicated"


def check_env_var(name: str) -> dict:
    """Check if an environment variable is set without revealing its value."""
    value = os.environ.get(name)
    return {
        "name": name,
        "set": value is not None and len(value) > 0,
        "length": len(value) if value else 0
    }


def print_status(results: dict, verbose: bool = False) -> None:
    """Display environment check results with visual indicators."""
    print("\n=== PhenoML RWE Analysis Environment Check ===\n")

    instance_type = results.get("instance_type", "unknown")
    print(f"Instance Type: {instance_type.upper()}")
    if instance_type == "shared":
        print("  (Using pre-configured Medplum sandbox)\n")
    else:
        print("  (Using dedicated FHIR instance)\n")

    print("Core Credentials:")
    for var in results["core"]:
        status = "\u2705" if var["set"] else "\u274c"
        print(f"  {status} {var['name']}")

    if not all(var["set"] for var in results["core"]):
        print("\n\u26a0\ufe0f  Missing core credentials!")
        print("  Set these in your .env file:")
        print("    PHENOML_USERNAME=your_username")
        print("    PHENOML_PASSWORD=your_password")
        print("    PHENOML_BASE_URL=https://experiment.app.pheno.ml")

    print("\nFHIR Provider (for dedicated instances):")
    for var in results["fhir"]:
        status = "\u2705" if var["set"] else "\u2b1c"
        print(f"  {status} {var['name']}")

    if instance_type == "shared":
        print("\n\u2139\ufe0f  FHIR provider credentials not required for shared experiments.")
    elif not all(var["set"] for var in results["fhir"]):
        print("\n\u26a0\ufe0f  FHIR provider not configured.")
        print("  For dedicated instances, configure your FHIR provider.")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Check PhenoML environment configuration"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show both human-readable and JSON output"
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to .env file (default: .env)"
    )
    args = parser.parse_args()

    # Load environment variables from file
    env_path = Path(args.env_file)
    if env_path.exists():
        load_dotenv(env_path)

    # Check core credentials
    core_vars = [
        check_env_var("PHENOML_USERNAME"),
        check_env_var("PHENOML_PASSWORD"),
        check_env_var("PHENOML_BASE_URL")
    ]

    # Check FHIR provider credentials (for dedicated instances)
    fhir_vars = [
        check_env_var("FHIR_BASE_URL"),
        check_env_var("FHIR_CLIENT_ID"),
        check_env_var("FHIR_CLIENT_SECRET"),
        check_env_var("FHIR_PROVIDER_ID")
    ]

    # Determine instance type
    base_url = os.environ.get("PHENOML_BASE_URL")
    instance_type = get_instance_type(base_url)

    results = {
        "instance_type": instance_type,
        "core": core_vars,
        "fhir": fhir_vars,
        "ready": all(var["set"] for var in core_vars)
    }

    # Output results
    if args.json and not args.verbose:
        print(json.dumps(results, indent=2))
    elif args.verbose:
        print_status(results, verbose=True)
        print("JSON Output:")
        print(json.dumps(results, indent=2))
    else:
        print_status(results)

    # Exit with error if core credentials missing
    if not results["ready"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
