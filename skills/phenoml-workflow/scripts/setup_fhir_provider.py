#!/usr/bin/env python3
"""
FHIR Provider Setup Script

Creates a FHIR provider using credentials from .env or CLI arguments.

Usage:
  python3 setup_fhir_provider.py
  python3 setup_fhir_provider.py --name "My FHIR Server" --provider medplum
  python3 setup_fhir_provider.py --help

Required .env variables:
  PHENOML_USERNAME, PHENOML_PASSWORD, PHENOML_BASE_URL
  FHIR_PROVIDER_BASE_URL, FHIR_PROVIDER_CLIENT_ID, FHIR_PROVIDER_CLIENT_SECRET

Example FHIR_PROVIDER_BASE_URL values:
  - Medplum: https://api.medplum.com/fhir/R4
  - Athena: https://api.preview.platform.athenahealth.com/fhir/r4
  - Epic: https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
  - Cerner: https://fhir-myrecord.cerner.com/r4/[tenant-id]

Optional .env variables:
  FHIR_PROVIDER_NAME (default: "FHIR Server")
  FHIR_PROVIDER_TYPE (default: "medplum")
  FHIR_AUTH_METHOD (default: "client_secret")
"""

import os
import sys
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

def main():
    parser = argparse.ArgumentParser(description='Create a FHIR provider for PhenoML workflows')
    parser.add_argument('--name', help='FHIR provider name')
    parser.add_argument('--provider', help='Provider type (medplum, epic, cerner, etc.)')
    parser.add_argument('--auth-method', help='Auth method (default: client_secret)')
    parser.add_argument('--base-url', help='FHIR base URL')
    parser.add_argument('--client-id', help='Client ID')
    parser.add_argument('--client-secret', help='Client secret')

    args = parser.parse_args()

    # Load environment
    load_dotenv()

    # Get configuration (CLI args override .env)
    name = args.name or os.getenv("FHIR_PROVIDER_NAME", "FHIR Server")
    provider_type = args.provider or os.getenv("FHIR_PROVIDER_TYPE", "medplum")
    auth_method = args.auth_method or os.getenv("FHIR_AUTH_METHOD", "client_secret")

    # Get FHIR provider credentials (CLI args override .env)
    base_url = args.base_url or os.getenv("FHIR_PROVIDER_BASE_URL")
    client_id = args.client_id or os.getenv("FHIR_PROVIDER_CLIENT_ID")
    client_secret = args.client_secret or os.getenv("FHIR_PROVIDER_CLIENT_SECRET")

    # Validate required fields
    if not base_url:
        print("❌ Error: FHIR base URL is required")
        print("   Set FHIR_PROVIDER_BASE_URL in .env, or use --base-url")
        print("\n   Example values:")
        print("   - Medplum: https://api.medplum.com/fhir/R4")
        print("   - Athena: https://api.preview.platform.athenahealth.com/fhir/r4")
        print("   - Epic: https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4")
        print("   - Cerner: https://fhir-myrecord.cerner.com/r4/[tenant-id]")
        sys.exit(1)

    if not client_id:
        print("❌ Error: Client ID is required")
        print("   Set FHIR_PROVIDER_CLIENT_ID in .env, or use --client-id")
        sys.exit(1)

    if not client_secret:
        print("❌ Error: Client secret is required")
        print("   Set FHIR_PROVIDER_CLIENT_SECRET in .env, or use --client-secret")
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

    # Create FHIR provider
    print(f"Creating FHIR provider:")
    print(f"  Name: {name}")
    print(f"  Provider: {provider_type}")
    print(f"  Base URL: {base_url}")
    print(f"  Auth method: {auth_method}\n")

    try:
        fhir_provider = client.fhir_provider.create(
            name=name,
            provider=provider_type,
            auth_method=auth_method,
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret
        )

        provider_id = fhir_provider.data.id
        print(f"✅ FHIR provider created successfully!")
        print(f"   Provider ID: {provider_id}\n")

        # Save to .env
        save_to_env("FHIR_PROVIDER_ID", provider_id)
        print(f"💾 Provider ID saved to .env")
        print(f"\n🎉 Setup complete! You can now create workflows using this provider.")

    except Exception as e:
        print(f"❌ Failed to create FHIR provider: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
