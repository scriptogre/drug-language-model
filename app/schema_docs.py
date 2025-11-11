"""
DrugCentral Database Schema Documentation

This module provides comprehensive schema information for the LLM to generate accurate SQL queries.
"""

SCHEMA_OVERVIEW = """
# DrugCentral Database Schema

DrugCentral is a comprehensive pharmaceutical database containing information about drugs, their structures,
products, targets, and clinical data.

## ⭐ RECOMMENDED: Simplified Views (USE THESE FIRST!)

These views make querying much simpler by pre-joining complex relationships. **Always try these views first!**

### drug_info (PRIMARY VIEW FOR DRUG SEARCHES)
Complete drug information in a single view. **Use this for most drug searches!**
- **Columns**:
  - drug_id: Unique drug identifier
  - drug_name: Drug name (search with ILIKE)
  - cas_reg_no: CAS Registry Number
  - chemical_formula: Chemical formula
  - molecular_weight: Molecular weight
  - smiles, inchikey: Chemical identifiers
  - primary_approval_authority: Main approval type ('FDA', 'EMA', etc.)
  - primary_approval_date: Date of primary approval
  - **is_fda_approved: Boolean - TRUE if FDA approved** (easiest way to filter FDA drugs!)
  - formulation_count, product_count, target_count: Counts of related data
- **Example**: `SELECT * FROM drug_info WHERE is_fda_approved = TRUE AND drug_name ILIKE '%remdesivir%'`

### fda_approved_drugs (EASIEST FOR FDA QUERIES)
Pre-filtered view of only FDA-approved drugs. **Use this instead of joining approval table!**
- **Columns**:
  - drug_id, drug_name, chemical_formula
  - fda_approval_date: Date approved by FDA
  - applicant_company: Company that got approval
  - is_orphan_drug: Boolean for orphan designation
  - formulation_count: Number of formulations
- **Example**: `SELECT * FROM fda_approved_drugs ORDER BY fda_approval_date DESC LIMIT 10`

### drug_products
All products containing each drug (pre-joined structures + active_ingredient + product).
- **Columns**:
  - drug_id, drug_name
  - ndc_product_code, product_name, generic_name
  - dosage_form: Form (e.g., 'TABLET', 'CAPSULE', 'INJECTION')
  - administration_route: Route (e.g., 'ORAL', 'INTRAVENOUS')
  - marketing_status, ingredient_quantity, ingredient_unit
- **Example**: `SELECT * FROM drug_products WHERE drug_name ILIKE '%aspirin%' AND dosage_form = 'TABLET'`

### drug_targets
What biological targets each drug acts on (pre-joined structures + act_table_full + target_dictionary).
- **Columns**:
  - drug_id, drug_name
  - target_id, target_name, target_class
  - target_organism: Species
  - action_type: Type of action ('INHIBITOR', 'AGONIST', 'ANTAGONIST')
  - activity_value, activity_unit, activity_type: Potency measurements
  - is_primary_mechanism: Boolean for primary MOA
- **Example**: `SELECT * FROM drug_targets WHERE drug_name ILIKE '%ibuprofen%' AND action_type = 'INHIBITOR'`

### drug_classes
Therapeutic classifications (ATC codes) for each drug.
- **Columns**:
  - drug_id, drug_name, atc_code
  - anatomical_group: Broadest level (e.g., 'NERVOUS SYSTEM')
  - therapeutic_group: Therapeutic category
  - pharmacological_group: Pharmacological category
  - chemical_group: Most specific (e.g., 'ANALGESICS', 'BETA BLOCKING AGENTS')
- **Example**: `SELECT * FROM drug_classes WHERE chemical_group ILIKE '%analgesic%'`

### drug_synonyms
All alternative names for each drug (including brand names).
- **Columns**:
  - drug_id, primary_name (primary drug name)
  - synonym: Alternative name
  - is_preferred: Boolean for preferred synonym
- **Example**: `SELECT * FROM drug_synonyms WHERE synonym ILIKE '%tylenol%'`

### drug_search_all (BEST FOR NAME SEARCHES)
Aggregated view with all names combined - easiest way to find a drug by any name.
- **Columns**:
  - drug_id, primary_name
  - all_synonyms: Pipe-separated list of all alternative names
  - chemical_formula, is_fda_approved, formulation_count
- **Example**: `SELECT * FROM drug_search_all WHERE primary_name ILIKE '%aspirin%' OR all_synonyms ILIKE '%aspirin%'`

## Original Complex Tables (Advanced Use Only)

### structures
The main drug/compound table containing chemical structures and properties.
- **Primary Key**: id (integer) - Unique structure identifier
- **Columns**:
  - id: Structure ID (primary key)
  - name: Drug name (e.g., "aspirin", "ibuprofen")
  - cas_reg_no: CAS Registry Number (chemical identifier)
  - cd_formula: Chemical formula (e.g., "C9H8O4")
  - cd_molweight: Molecular weight (numeric)
  - smiles: SMILES chemical notation string
  - inchi: InChI chemical identifier string
  - inchikey: InChI hash key (27 chars)
  - stem: Drug name stem/suffix (e.g., "-pril" for ACE inhibitors)
  - clogp: Calculated logP (lipophilicity)
  - tpsa: Topological polar surface area
  - no_formulations: Count of formulations containing this structure
  - status: Approval status string
- **Common Queries**: Search by drug name (use ILIKE), CAS number, or chemical formula

### product
Commercial drug products (medications you can buy/prescribe).
- **Primary Key**: id (integer)
- **Unique Key**: ndc_product_code (National Drug Code)
- **Columns**:
  - id: Product ID (primary key)
  - ndc_product_code: NDC code (format: XXXXX-XXX)
  - product_name: Brand/trade name (e.g., "TYLENOL")
  - generic_name: Generic drug name (e.g., "ACETAMINOPHEN")
  - form: Dosage form (e.g., "TABLET", "CAPSULE", "INJECTION", "AEROSOL")
  - route: Administration route (e.g., "ORAL", "INTRAVENOUS", "TOPICAL")
  - marketing_status: Marketing status (e.g., "ANDA", "NDA", "OTC")
  - active_ingredient_count: Number of active ingredients in this product
- **Common Queries**: Find products by name (search product_name OR generic_name), form, or route

### active_ingredient
Links products to their chemical structures (a product can have multiple active ingredients).
- **Foreign Keys**:
  - struct_id → structures.id
  - ndc_product_code → product.ndc_product_code
- **Columns**:
  - id: Primary key
  - struct_id: Structure ID (links to structures table)
  - ndc_product_code: Product NDC code (links to product table)
  - active_moiety_name: Name of the active chemical moiety
  - active_moiety_unii: UNII identifier for active moiety
  - substance_name: Name of the substance form
  - substance_unii: UNII identifier for substance
  - quantity: Amount of ingredient (numeric)
  - unit: Unit of measurement (e.g., "mg", "g", "mL")
  - quantity_denom_value: Denominator value for concentration
  - quantity_denom_unit: Denominator unit for concentration
- **Description**: Junction table showing which structures are in which products and their quantities

### target_dictionary
Biological targets (proteins, enzymes, receptors) that drugs act upon.
- **Primary Key**: id (integer)
- **Columns**:
  - id: Target ID (primary key)
  - name: Target name (protein/enzyme name)
  - organism: Species (e.g., "Homo sapiens", "Rattus norvegicus")
  - target_class: Class of target (e.g., "GPCR", "Kinase", "Enzyme", "Ion channel", "Cytokine")
  - protein_type: Type of protein (e.g., "SINGLE PROTEIN", "PROTEIN COMPLEX")
  - protein_components: Number of protein components (1 for single, >1 for complexes)
  - tdl: Target Development Level (druggability level)
- **Description**: Proteins, enzymes, receptors that drugs interact with

### act_table_full
Drug-target activity data (which drugs act on which targets and how strongly).
- **Foreign Keys**:
  - struct_id → structures.id
  - target_id → target_dictionary.id
- **Columns**:
  - act_id: Activity record ID (primary key)
  - struct_id: Structure ID (drug)
  - target_id: Target ID (protein)
  - target_name: Name of the target protein
  - target_class: Class of target (same as target_dictionary.target_class)
  - act_value: Activity value (e.g., IC50, Ki, EC50) - numeric potency
  - act_unit: Unit for activity value (e.g., "nM", "uM")
  - act_type: Type of activity measurement (e.g., "IC50", "Ki", "EC50", "Kd")
  - action_type: Type of action (e.g., "INHIBITOR", "AGONIST", "ANTAGONIST", "MODULATOR")
  - moa: Mechanism of action flag (1 = primary MOA, 0 = secondary)
  - relation: Relationship operator (e.g., "=", "<", ">")
  - organism: Species tested
  - act_source: Data source (e.g., "CHEMBL", "BINDING DB")
  - gene: Gene symbol(s)
  - accession: Protein accession numbers
- **Description**: Experimental data showing drug-target interactions and potency
- **Common Queries**: Find targets for a drug, find drugs for a target, filter by action_type or act_type

## Reference Tables

### approval
Regulatory approval information for structures.
- **Foreign Key**: struct_id → structures.id
- **Columns**:
  - id: Primary key
  - struct_id: Structure ID (links to structures table)
  - **approval: DATE of approval (e.g., '2020-05-08') - THIS IS A DATE, NOT A STRING**
  - **type: Approval authority** (e.g., "FDA", "EMA", "PMDA", "Health Canada", "KFDA", "YEAR INTRODUCED")
  - applicant: Company that applied for approval
  - orphan: Boolean flag for orphan drug designation
- **CRITICAL**: To find FDA-approved drugs, use `WHERE type = 'FDA'`, NOT `WHERE approval = 'FDA'` (approval is a DATE!)
- **Common Queries**: `WHERE type = 'FDA'` for FDA drugs, `WHERE approval > '2020-01-01'` for recent approvals

### atc
Anatomical Therapeutic Chemical (ATC) classification system (WHO standard).
- **Primary Key**: id
- **Columns**:
  - id: Primary key
  - code: 7-character ATC code (e.g., "N02BA01")
  - chemical_substance: Drug name
  - l1_code: Level 1 code (anatomical group, 1 char)
  - l1_name: Level 1 name (e.g., "ALIMENTARY TRACT AND METABOLISM")
  - l2_code: Level 2 code (therapeutic subgroup, 3 chars)
  - l2_name: Level 2 name (e.g., "DRUGS FOR ACID RELATED DISORDERS")
  - l3_code: Level 3 code (pharmacological subgroup, 4 chars)
  - l3_name: Level 3 name (e.g., "DRUGS FOR PEPTIC ULCER")
  - l4_code: Level 4 code (chemical subgroup, 5 chars)
  - l4_name: Level 4 name (e.g., "PROTON PUMP INHIBITORS")
  - chemical_substance_count: Count of substances in this class
- **Description**: Hierarchical drug classification system by therapeutic use
- **Common Queries**: Search by l4_name for drug classes (e.g., ILIKE '%analgesic%')

### struct2atc
Junction table linking structures to ATC codes.
- **Foreign Keys**:
  - struct_id → structures.id
  - atc_code → atc.code
- **Columns**:
  - struct_id: Structure ID
  - atc_code: ATC code (7 chars)
- **Description**: Links drugs to their ATC classifications (a drug can have multiple ATC codes)

### synonyms
Alternative names and brand names for structures.
- **Foreign Key**: struct_id → structures.id
- **Columns**:
  - syn_id: Synonym ID
  - id: Structure ID (links to structures table)
  - name: Alternative name (brand name, trade name, synonym)
  - preferred_name: Flag for preferred name (0 or 1)
  - parent_id: Parent structure ID if applicable
  - lname: Lowercase version of name (for case-insensitive search)
- **Description**: Brand names, trade names, and synonyms for compounds
- **Common Queries**: Search synonyms.name or synonyms.lname to find drugs by alternative names

### pharma_class
Pharmacological classification of drugs.
- **Description**: Drug classes and categories (e.g., "Beta Blocker", "Antibiotic", "NSAID")

## Adverse Events Tables

### faers, faers_female, faers_male, faers_ped, faers_ger
FDA Adverse Event Reporting System data segmented by demographics.
- **Description**: Reports of adverse drug reactions from real-world use

## Patent & Exclusivity Tables

### ob_patent
Orange Book patent information.
- **Description**: Patent data for approved drugs

### ob_exclusivity
Orange Book exclusivity information.
- **Description**: Market exclusivity periods for approved drugs

## ⭐ SIMPLE Query Patterns (USE THESE!)

These queries use the simplified views - much easier and less error-prone!

1. **Find all FDA-approved drugs** (SIMPLEST!):
   ```sql
   SELECT drug_name, fda_approval_date, applicant_company
   FROM fda_approved_drugs
   ORDER BY fda_approval_date DESC
   LIMIT 100
   ```

2. **Search for any drug by name**:
   ```sql
   SELECT drug_id, drug_name, is_fda_approved
   FROM drug_info
   WHERE drug_name ILIKE '%remdesivir%'
   ```

3. **Find all products containing a specific drug**:
   ```sql
   SELECT product_name, dosage_form, administration_route
   FROM drug_products
   WHERE drug_name ILIKE '%aspirin%'
   LIMIT 100
   ```

4. **Find what targets a drug acts on**:
   ```sql
   SELECT target_name, target_class, action_type, activity_value
   FROM drug_targets
   WHERE drug_name ILIKE '%ibuprofen%'
   LIMIT 100
   ```

5. **Find drugs by therapeutic class**:
   ```sql
   SELECT drug_name, chemical_group
   FROM drug_classes
   WHERE chemical_group ILIKE '%analgesic%'
   LIMIT 100
   ```

6. **Search for a drug by brand name**:
   ```sql
   SELECT primary_name, all_synonyms
   FROM drug_search_all
   WHERE primary_name ILIKE '%tylenol%' OR all_synonyms ILIKE '%tylenol%'
   ```

## Complex Query Patterns (Only if views don't work)

These use the original tables and require multiple JOINs - avoid if possible!

1. **Manual FDA query** (DON'T USE - use fda_approved_drugs view instead!):
   ```sql
   SELECT s.name, a.approval
   FROM structures s
   JOIN approval a ON s.id = a.struct_id
   WHERE a.type = 'FDA'
   ORDER BY a.approval DESC
   LIMIT 100
   ```

## Important Notes

- **⭐ ALWAYS USE THE SIMPLIFIED VIEWS FIRST!** They're much simpler and less error-prone
- **For FDA drugs**: Use `fda_approved_drugs` view OR `drug_info WHERE is_fda_approved = TRUE`
- **For drug searches**: Use `drug_info` or `drug_search_all` views
- **For products**: Use `drug_products` view
- **For targets**: Use `drug_targets` view
- **For drug classes**: Use `drug_classes` view
- Always use ILIKE for case-insensitive text searches
- Always include LIMIT clause (queries auto-limited to 1000 rows max)
- Boolean fields: `is_fda_approved`, `is_orphan_drug`, `is_primary_mechanism` use TRUE/FALSE
- Target classes include: GPCR, Kinase, Enzyme, Ion channel, Cytokine, Antibody
- Product forms include: TABLET, CAPSULE, INJECTION, AEROSOL, CREAM, etc.
- Administration routes include: ORAL, INTRAVENOUS, TOPICAL, SUBCUTANEOUS, etc.
"""
