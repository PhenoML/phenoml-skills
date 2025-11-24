# PhenoML Skills

A collection of Claude Code plugins and skills that enable developers to rapidly build and test healthcare data workflows using PhenoML. These interactive skills provide guided, conversational experiences for using PhenoML APIs.

## What's Included

### Plugins

- **phenoml-workflow** - Create and execute PhenoML workflows for healthcare data processing

### Skills

- **phenoml-workflow** - Interactive skill for:
  - Setting up FHIR provider connections
  - Creating workflows
  - Testing workflows with example data
  - Managing and executing healthcare data pipelines

## Getting Started

### Prerequisites

- Claude Code CLI installed
- Python 3.x
- PhenoML account credentials
- FHIR provider credentials (Medplum, Athena, Epic, Cerner, etc.)

### Installation

1. Start Claude Code in your terminal
```bash
claude
```

2. Add the marketplace
```bash
/plugin marketplace add PhenoML/phenoml-skills
```

3. Install the plugin
```bash
/plugin install phenoml-workflow@phenoml-skills
```
