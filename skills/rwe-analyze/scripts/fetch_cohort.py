#!/usr/bin/env python3
"""
Fetch Cohort Script

Fetches patient data and generates IPS summaries for one or two cohorts.
Claude interprets the summaries to provide analysis, comparison, or feasibility assessment.

Usage:
    # Single cohort
    python fetch_cohort.py --cohort "patients with type 2 diabetes over 50"

    # Two cohorts for comparison
    python fetch_cohort.py --cohort "diabetics on metformin" --cohort-2 "diabetics on insulin"
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("Error: python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

try:
    from phenoml import Client
except ImportError:
    print("Error: phenoml not installed. Run: pip install phenoml")
    sys.exit(1)


def fetch_cohort_ips(client, description: str, provider: str, label: str) -> list[str]:
    """Fetch patients and generate IPS summaries for a cohort."""
    print(f"Fetching cohort: {description}", file=sys.stderr)

    try:
        cohort_response = client.tools.analyze_cohort(
            text=description,
            provider=provider
        )
        patients = cohort_response.patient_ids if hasattr(cohort_response, 'patient_ids') else []
        print(f"Found {len(patients)} patients", file=sys.stderr)
    except Exception as e:
        print(f"Error analyzing cohort: {e}", file=sys.stderr)
        return []

    if not patients:
        return []

    summaries = []
    for i, patient in enumerate(patients, 1):
        patient_id = patient.get("id") if isinstance(patient, dict) else patient
        print(f"Processing {label} patient {i}/{len(patients)}...", file=sys.stderr, end="\r")

        try:
            bundle = client.fhir.search(
                fhir_provider_id=os.environ.get("FHIR_PROVIDER_ID", provider),
                fhir_path=f"Patient/{patient_id}/$everything"
            )

            ips_response = client.summary.create(
                fhir_resources=bundle,
                mode="ips"
            )
            ips_text = ips_response.summary if hasattr(ips_response, 'summary') else str(ips_response)
            summaries.append(ips_text)

        except Exception as e:
            print(f"Error processing patient {patient_id}: {e}", file=sys.stderr)
            continue

    print(f"Processed {len(summaries)} {label} patients", file=sys.stderr)
    return summaries


def main():
    parser = argparse.ArgumentParser(
        description="Fetch patient cohorts and generate IPS summaries"
    )
    parser.add_argument(
        "--cohort",
        required=True,
        help="Natural language description of the patient cohort"
    )
    parser.add_argument(
        "--cohort-2",
        help="Optional second cohort for comparison"
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to .env file (default: .env)"
    )
    parser.add_argument(
        "--provider",
        help="FHIR provider ID (auto-detected if not specified)"
    )
    args = parser.parse_args()

    # Load environment
    env_path = Path(args.env_file)
    if env_path.exists():
        load_dotenv(env_path)

    if not os.environ.get("PHENOML_USERNAME") or not os.environ.get("PHENOML_PASSWORD"):
        print("Error: PHENOML_USERNAME and PHENOML_PASSWORD must be set", file=sys.stderr)
        sys.exit(1)

    try:
        client = Client(
            username=os.environ["PHENOML_USERNAME"],
            password=os.environ["PHENOML_PASSWORD"],
            base_url=os.environ.get("PHENOML_BASE_URL", "https://experiment.app.pheno.ml")
        )
    except Exception as e:
        print(f"Error initializing client: {e}", file=sys.stderr)
        sys.exit(1)

    # Auto-detect provider if not specified
    provider = args.provider
    if not provider:
        try:
            result = client.fhir_provider.list()
            if result.fhir_providers and len(result.fhir_providers) > 0:
                provider = result.fhir_providers[0].id
                print(f"Using FHIR provider: {result.fhir_providers[0].name} ({provider})", file=sys.stderr)
            else:
                print("Error: No FHIR providers available", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"Error fetching FHIR providers: {e}", file=sys.stderr)
            sys.exit(1)

    # Fetch first cohort
    summaries_1 = fetch_cohort_ips(client, args.cohort, provider, "cohort 1")

    # Output first cohort
    if args.cohort_2:
        print(f"\n### COHORT 1: {args.cohort}")
    else:
        print(f"\n### COHORT: {args.cohort}")
    print(f"Total patients: {len(summaries_1)}\n")

    for i, summary in enumerate(summaries_1, 1):
        print(f"--- Patient {i} ---")
        print(summary)
        print()

    # Fetch and output second cohort if provided
    if args.cohort_2:
        summaries_2 = fetch_cohort_ips(client, args.cohort_2, provider, "cohort 2")

        print(f"\n### COHORT 2: {args.cohort_2}")
        print(f"Total patients: {len(summaries_2)}\n")

        for i, summary in enumerate(summaries_2, 1):
            print(f"--- Patient {i} ---")
            print(summary)
            print()


if __name__ == "__main__":
    main()
