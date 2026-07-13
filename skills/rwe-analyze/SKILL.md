---
name: rwe-analyze
description: Analyze real-world evidence cohorts using PhenoML APIs and FHIR data. Use when defining patient cohorts from natural language, generating population statistics, comparing cohorts, or assessing clinical study feasibility.
---

# RWE Cohort Analysis Skill

This skill provides real-world evidence (RWE) analysis using PhenoML APIs. It enables biopharma analysts to define patient cohorts, generate population statistics, compare cohorts, and assess study feasibility.

## How It Works

A single script (`fetch_cohort.py`) fetches patient data and generates IPS (International Patient Summary) natural language summaries. The active AI agent then interprets these summaries to provide whatever analysis the user needs.

## When to Use This Skill

Use this skill when users need to:
- Define and analyze a patient cohort from natural language criteria
- Generate population-level statistics (demographics, conditions, medications)
- Compare two patient cohorts (e.g., treatment vs control groups)
- Assess feasibility of a clinical study against a patient population

## Prerequisites

Before using this skill, ensure:
1. Python 3.10+ is installed
2. Required packages are available: `python-dotenv`, `phenoml`
3. PhenoML credentials are configured (PHENOML_USERNAME, PHENOML_PASSWORD)

## Workflow

### Step 0: Verify Environment

Always start by checking the environment configuration:

```bash
python /path/to/skill/scripts/check_env.py --env-file .env
```

Resolve `/path/to/skill` as the directory containing this `SKILL.md`. In Claude Code, `${CLAUDE_SKILL_DIR}` can be used when available.

If credentials are missing, guide the user to set up their `.env` file with:
- PHENOML_USERNAME
- PHENOML_PASSWORD
- PHENOML_BASE_URL (defaults to https://experiment.app.pheno.ml)

### Step 1: Fetch Patient Data

Use the single fetch script for all use cases:

**Single cohort:**
```bash
python /path/to/skill/scripts/fetch_cohort.py \
  --cohort "<natural language criteria>" \
  --env-file .env
```

**Two cohorts for comparison:**
```bash
python /path/to/skill/scripts/fetch_cohort.py \
  --cohort "<first cohort>" \
  --cohort-2 "<second cohort>" \
  --env-file .env
```

### Step 2: Analyze the IPS Summaries

The script outputs IPS natural language summaries. Analyze them based on what the user asked for:

**Population Analysis:**
- Total patient count
- Age distribution (mean, range, brackets)
- Gender breakdown
- Most common conditions with prevalence
- Most common medications with prevalence

**Cohort Comparison:**
- Patient counts for each cohort
- Demographics differences
- Condition prevalence differences
- Medication differences

**Study Feasibility:**
1. Parse the user's study criteria (age, required conditions, exclusions, medications)
2. Check each patient's IPS against criteria
3. Generate feasibility report:
   - Total patients in cohort
   - Number and percentage eligible
   - Breakdown by criterion
   - Overall assessment (High ≥70%, Moderate 40-69%, Low <40%)

## Important Guidelines

1. **Always use --env-file**: Pass the `.env` file path explicitly.

2. **Natural language cohort descriptions**: The PhenoML API accepts natural language:
   - "patients with type 2 diabetes"
   - "females over 65 with hypertension"
   - "patients diagnosed with breast cancer in the last 2 years"

3. **IPS format**: The IPS summaries include sections for:
   - Patient demographics (name, DOB, age, gender)
   - Allergies and Intolerances
   - Medication List
   - Problem List (conditions)

## Example Interactions

### Example 1: Basic Cohort Analysis
**User**: "I need to understand our diabetic patient population"

**Response**: Run fetch_cohort.py with `--cohort "patients with diabetes"`, then analyze the IPS summaries to report demographics, common comorbidities, and medication patterns.

### Example 2: Comparing Treatment Groups
**User**: "Compare patients on metformin versus those on insulin"

**Response**: Run fetch_cohort.py with `--cohort "diabetic patients on metformin" --cohort-2 "diabetic patients on insulin"`, then compare the IPS summaries.

### Example 3: Study Feasibility
**User**: "How many diabetics aged 40-70 without kidney problems would qualify for our trial?"

**Response**: Run fetch_cohort.py with `--cohort "patients with diabetes"`, then evaluate each patient's IPS against the criteria (age 40-70, no kidney disease) and report eligibility.

## API Methods Used

| Script | PhenoML APIs |
|--------|--------------|
| fetch_cohort.py | `tools.analyze_cohort()`, `fhir.search()`, `summary.create(mode="ips")` |
