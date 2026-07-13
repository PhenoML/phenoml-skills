# PhenoML Skills

A shared skills repo for Codex and Claude Code. These skills help developers build, test, and analyze healthcare data workflows using PhenoML APIs.

## What's Included

- **phenoml-workflow** - Create and execute PhenoML workflows for:
  - Setting up FHIR provider connections
  - Creating workflows
  - Testing workflows with example data
  - Managing and executing healthcare data pipelines
- **rwe-analyze** - Conduct real-world evidence (RWE) analysis on FHIR data:
  - Defining patient cohorts from natural language
  - Generating population-level statistics
  - Comparing cohorts
  - Assessing clinical study feasibility

## Getting Started

### Prerequisites

- Codex or Claude Code
- Python 3.10+
- PhenoML account credentials
- FHIR provider credentials (Medplum, Athena, Epic, Cerner, etc.)
- Python packages: `python-dotenv` and `phenoml`
- For Claude Code, review `.claude/settings.json` and keep sensitive files such as `.env` blocked from reads.

This repo is designed for development use. Review your agent, workspace, and enterprise policies before using it with production systems or regulated data.

## Install for Codex

Codex discovers skills from `${CODEX_HOME:-$HOME/.codex}/skills`. Copy the shared skill folders there:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/phenoml-workflow "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/rwe-analyze "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Restart Codex or start a new session after copying the skills.

## Install for Claude Code CLI

1. Start Claude Code in your terminal:
```bash
claude
```

2. Add the marketplace:
```bash
/plugin marketplace add PhenoML/phenoml-skills
```

3. Install the plugin:
```bash
/plugin install phenoml-skills@phenoml-skills
```

If you previously installed the old `phenoml-workflow@phenoml-skills` plugin, remove it after installing the current plugin:

```bash
/plugin uninstall phenoml-workflow@phenoml-skills
```

## Install for Claude Code in VS Code

1. In the chat input, type `/` to open the command menu.
2. Select Manage Plugins
3. Click Marketplaces
4. Paste the repo URL: `https://github.com/PhenoML/phenoml-skills`
5. Install `phenoml-skills`
6. PhenoML Skills will now appear in your Plugins list!

## Environment

Create a `.env` file in the project where you are running workflows:

```env
PHENOML_USERNAME=
PHENOML_PASSWORD=
PHENOML_BASE_URL=https://experiment.app.pheno.ml

FHIR_PROVIDER_BASE_URL=
FHIR_PROVIDER_CLIENT_ID=
FHIR_PROVIDER_CLIENT_SECRET=
FHIR_PROVIDER_ID=
WORKFLOW_ID=
```

For the shared experiment at `https://experiment.app.pheno.ml`, the workflow and RWE scripts use the preconfigured `experiment-default` FHIR provider when `FHIR_PROVIDER_ID` is not set.
