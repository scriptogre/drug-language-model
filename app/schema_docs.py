"""
DrugCentral Database Schema Documentation

This module provides comprehensive schema information for the LLM to generate accurate SQL queries.
"""

SCHEMA_OVERVIEW = """
# DrugCentral Database - Query Guide

## Rule #1: Finding Drugs by Name

**Use `drug_search_all` for ALL drug name searches.**

This view has:
- `drug_id` - Unique identifier
- `primary_name` - Chemical name (e.g., "acetylsalicylic acid")
- `all_synonyms` - All other names (e.g., contains "aspirin")
- `chemical_formula` - Chemical formula
- `is_fda_approved` - TRUE if FDA approved
- `formulation_count` - Number of formulations

**Search pattern:**
```sql
SELECT drug_id, primary_name, chemical_formula
FROM drug_search_all
WHERE primary_name ILIKE '%DRUGNAME%' OR all_synonyms ILIKE '%DRUGNAME%'
```

**Examples:**
```sql
-- Find aspirin
SELECT * FROM drug_search_all
WHERE primary_name ILIKE '%aspirin%' OR all_synonyms ILIKE '%aspirin%'

-- Find Tylenol
SELECT * FROM drug_search_all
WHERE primary_name ILIKE '%tylenol%' OR all_synonyms ILIKE '%tylenol%'
```

## Rule #2: Getting Drug Details

**Use `drug_info` for complete drug information.**

This view has:
- `drug_id` - Unique identifier
- `drug_name` - Chemical name only (NOT brand names)
- `chemical_formula` - Chemical formula
- `molecular_weight` - Molecular weight
- `cas_reg_no` - CAS number
- `smiles`, `inchikey` - Chemical identifiers
- `is_fda_approved` - TRUE if FDA approved
- `formulation_count`, `product_count`, `target_count` - Counts

**Simple search (if you know the chemical name):**
```sql
SELECT drug_name, molecular_weight, chemical_formula
FROM drug_info
WHERE drug_name ILIKE '%ibuprofen%'
```

**Search by any name (brand or chemical):**
```sql
SELECT di.drug_name, di.molecular_weight, di.chemical_formula
FROM drug_info di
JOIN drug_search_all dsa ON di.drug_id = dsa.drug_id
WHERE dsa.primary_name ILIKE '%aspirin%' OR dsa.all_synonyms ILIKE '%aspirin%'
```

## Rule #3: Finding FDA Approved Drugs

**Use `fda_approved_drugs` for FDA-specific queries.**

This view has:
- `drug_id` - Unique identifier
- `drug_name` - Chemical name
- `chemical_formula` - Chemical formula
- `fda_approval_date` - FDA approval date
- `applicant_company` - Company name
- `is_orphan_drug` - TRUE if orphan drug
- `formulation_count` - Number of formulations

**Examples:**
```sql
-- 10 most recent FDA approvals
SELECT drug_name, fda_approval_date, applicant_company
FROM fda_approved_drugs
ORDER BY fda_approval_date DESC
LIMIT 10

-- FDA approvals in 2020
SELECT drug_name, fda_approval_date
FROM fda_approved_drugs
WHERE fda_approval_date BETWEEN '2020-01-01' AND '2020-12-31'

-- Orphan drugs
SELECT drug_name, fda_approval_date
FROM fda_approved_drugs
WHERE is_orphan_drug = TRUE
ORDER BY fda_approval_date DESC
LIMIT 10
```

## Rule #4: Finding Drug Products

**Use `drug_products` for product formulations.**

This view has:
- `drug_id` - Unique identifier
- `drug_name` - Chemical name only (NOT brand names)
- `ndc_product_code` - Product code
- `product_name` - Product brand name
- `generic_name` - Generic name
- `dosage_form` - Form (TABLET, CAPSULE, INJECTION, etc.)
- `administration_route` - Route (ORAL, INTRAVENOUS, TOPICAL, etc.)
- `marketing_status` - Marketing status
- `ingredient_quantity`, `ingredient_unit` - Dosage

**Search by chemical name:**
```sql
SELECT product_name, dosage_form, administration_route
FROM drug_products
WHERE drug_name ILIKE '%ibuprofen%' AND dosage_form = 'TABLET'
```

**Search by any name (brand or chemical):**
```sql
SELECT dp.product_name, dp.dosage_form, dp.administration_route
FROM drug_products dp
JOIN drug_search_all dsa ON dp.drug_id = dsa.drug_id
WHERE (dsa.primary_name ILIKE '%aspirin%' OR dsa.all_synonyms ILIKE '%aspirin%')
AND dp.dosage_form = 'TABLET'
```

## Rule #5: Finding Drug Targets

**Use `drug_targets` for mechanism of action.**

This view has:
- `drug_id` - Unique identifier
- `drug_name` - Chemical name only (NOT brand names)
- `target_id` - Target identifier
- `target_name` - Protein/enzyme name
- `target_class` - Class (GPCR, Kinase, Enzyme, Ion channel, etc.)
- `target_organism` - Species (Homo sapiens, etc.)
- `action_type` - Action (INHIBITOR, AGONIST, ANTAGONIST, etc.)
- `activity_value`, `activity_unit` - Potency (IC50, Ki, etc.)
- `is_primary_mechanism` - TRUE if primary MOA

**Search by chemical name:**
```sql
SELECT target_name, target_class, action_type, activity_value
FROM drug_targets
WHERE drug_name ILIKE '%atorvastatin%'
```

**Search by any name:**
```sql
SELECT dt.target_name, dt.target_class, dt.action_type
FROM drug_targets dt
JOIN drug_search_all dsa ON dt.drug_id = dsa.drug_id
WHERE dsa.primary_name ILIKE '%lipitor%' OR dsa.all_synonyms ILIKE '%lipitor%'
```

**Filter by target type:**
```sql
SELECT drug_name, target_name, action_type
FROM drug_targets
WHERE target_class = 'GPCR' AND action_type = 'AGONIST'
```

## Rule #6: Finding Drug Classes

**Use `drug_classes` for therapeutic classification.**

This view has:
- `drug_id` - Unique identifier
- `drug_name` - Chemical name
- `atc_code` - ATC code
- `anatomical_group` - Broadest (e.g., "NERVOUS SYSTEM")
- `therapeutic_group` - Therapeutic (e.g., "ANALGESICS")
- `pharmacological_group` - Pharmacological
- `chemical_group` - Most specific (e.g., "OPIOID ANALGESICS")

**Examples:**
```sql
-- All analgesics
SELECT drug_name, chemical_group
FROM drug_classes
WHERE chemical_group ILIKE '%analgesic%'

-- All cardiovascular drugs
SELECT drug_name, therapeutic_group, chemical_group
FROM drug_classes
WHERE anatomical_group ILIKE '%cardiovascular%'
```

## Important Notes

- Always use ILIKE for case-insensitive searches
- Always include LIMIT (queries auto-limited to 1000 rows)
- Boolean fields use TRUE/FALSE (not 1/0)
- When user mentions a drug name, ALWAYS search using drug_search_all first
- Column names are exact: use `drug_name` in drug_info, `primary_name` in drug_search_all
"""
