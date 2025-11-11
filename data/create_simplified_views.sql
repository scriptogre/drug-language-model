-- =====================================================
-- Simplified Views for DrugCentral Database
-- These views make it much easier for LLMs to query
-- the database by pre-joining complex relationships
-- =====================================================

-- View 1: drug_info - Complete drug information in one place
-- This is the main view for general drug searches
DROP VIEW IF EXISTS drug_info CASCADE;
CREATE VIEW drug_info AS
SELECT DISTINCT
    s.id as drug_id,
    s.name as drug_name,
    s.cas_reg_no,
    s.cd_formula as chemical_formula,
    s.cd_molweight as molecular_weight,
    s.smiles,
    s.inchikey,
    -- Approval info (using DISTINCT ON to get one approval per drug, preferring FDA)
    (SELECT a.type
     FROM approval a
     WHERE a.struct_id = s.id
     ORDER BY CASE WHEN a.type = 'FDA' THEN 0 ELSE 1 END, a.approval DESC
     LIMIT 1) as primary_approval_authority,
    (SELECT a.approval
     FROM approval a
     WHERE a.struct_id = s.id
     ORDER BY CASE WHEN a.type = 'FDA' THEN 0 ELSE 1 END, a.approval DESC
     LIMIT 1) as primary_approval_date,
    -- Check if FDA approved
    EXISTS(SELECT 1 FROM approval a WHERE a.struct_id = s.id AND a.type = 'FDA') as is_fda_approved,
    -- Counts
    s.no_formulations as formulation_count,
    (SELECT COUNT(*) FROM active_ingredient ai WHERE ai.struct_id = s.id) as product_count,
    (SELECT COUNT(DISTINCT target_id) FROM act_table_full atf WHERE atf.struct_id = s.id) as target_count
FROM structures s;

COMMENT ON VIEW drug_info IS 'Simplified view with complete drug information. Search by drug_name using ILIKE. Check is_fda_approved for FDA status.';


-- View 2: drug_products - What products contain each drug
DROP VIEW IF EXISTS drug_products CASCADE;
CREATE VIEW drug_products AS
SELECT
    s.id as drug_id,
    s.name as drug_name,
    p.ndc_product_code,
    p.product_name,
    p.generic_name,
    p.form as dosage_form,
    p.route as administration_route,
    p.marketing_status,
    ai.quantity as ingredient_quantity,
    ai.unit as ingredient_unit
FROM structures s
JOIN active_ingredient ai ON s.id = ai.struct_id
JOIN product p ON ai.ndc_product_code = p.ndc_product_code;

COMMENT ON VIEW drug_products IS 'Shows all products containing each drug. Search by drug_name, dosage_form (TABLET, CAPSULE, etc.), or administration_route (ORAL, IV, etc.)';


-- View 3: drug_targets - What biological targets each drug acts on
DROP VIEW IF EXISTS drug_targets CASCADE;
CREATE VIEW drug_targets AS
SELECT
    s.id as drug_id,
    s.name as drug_name,
    td.id as target_id,
    td.name as target_name,
    td.target_class,
    atf.organism as target_organism,
    atf.action_type,
    atf.act_value as activity_value,
    atf.act_unit as activity_unit,
    atf.act_type as activity_type,
    CASE WHEN atf.moa = 1 THEN true ELSE false END as is_primary_mechanism
FROM structures s
JOIN act_table_full atf ON s.id = atf.struct_id
JOIN target_dictionary td ON atf.target_id = td.id;

COMMENT ON VIEW drug_targets IS 'Shows what biological targets (proteins/enzymes) each drug acts on. Filter by action_type (INHIBITOR, AGONIST, etc.) or target_class (GPCR, Kinase, etc.)';


-- View 4: drug_classes - Therapeutic classification of drugs
DROP VIEW IF EXISTS drug_classes CASCADE;
CREATE VIEW drug_classes AS
SELECT
    s.id as drug_id,
    s.name as drug_name,
    atc.code as atc_code,
    atc.l1_name as anatomical_group,
    atc.l2_name as therapeutic_group,
    atc.l3_name as pharmacological_group,
    atc.l4_name as chemical_group
FROM structures s
JOIN struct2atc s2a ON s.id = s2a.struct_id
JOIN atc ON s2a.atc_code = atc.code;

COMMENT ON VIEW drug_classes IS 'Shows therapeutic classifications (ATC codes) for each drug. Search by chemical_group (most specific, e.g., "ANALGESICS") or therapeutic_group (broader, e.g., "NERVOUS SYSTEM")';


-- View 5: drug_synonyms - All names for each drug (including brand names)
DROP VIEW IF EXISTS drug_synonyms CASCADE;
CREATE VIEW drug_synonyms AS
SELECT
    s.id as drug_id,
    s.name as primary_name,
    syn.name as synonym,
    CASE WHEN syn.preferred_name = 1 THEN true ELSE false END as is_preferred
FROM structures s
JOIN synonyms syn ON s.id = syn.id
WHERE syn.name IS NOT NULL AND syn.name != '';

COMMENT ON VIEW drug_synonyms IS 'Shows all alternative names for each drug including brand names and trade names. Use this to find drugs by common/brand names.';


-- View 6: fda_approved_drugs - Quick view of all FDA approved drugs
DROP VIEW IF EXISTS fda_approved_drugs CASCADE;
CREATE VIEW fda_approved_drugs AS
SELECT
    s.id as drug_id,
    s.name as drug_name,
    s.cd_formula as chemical_formula,
    a.approval as fda_approval_date,
    a.applicant as applicant_company,
    a.orphan as is_orphan_drug,
    s.no_formulations as formulation_count
FROM structures s
JOIN approval a ON s.id = a.struct_id
WHERE a.type = 'FDA'
ORDER BY a.approval DESC;

COMMENT ON VIEW fda_approved_drugs IS 'Quick view of all FDA-approved drugs with approval dates. Already filtered to FDA only.';


-- View 7: drug_search_all - Combined search across all names
DROP VIEW IF EXISTS drug_search_all CASCADE;
CREATE VIEW drug_search_all AS
SELECT DISTINCT
    s.id as drug_id,
    s.name as primary_name,
    COALESCE(
        STRING_AGG(DISTINCT syn.name, ' | ') FILTER (WHERE syn.name IS NOT NULL),
        ''
    ) as all_synonyms,
    s.cd_formula as chemical_formula,
    EXISTS(SELECT 1 FROM approval a WHERE a.struct_id = s.id AND a.type = 'FDA') as is_fda_approved,
    s.no_formulations as formulation_count
FROM structures s
LEFT JOIN synonyms syn ON s.id = syn.id
GROUP BY s.id, s.name, s.cd_formula, s.no_formulations;

COMMENT ON VIEW drug_search_all IS 'Easiest view for searching drugs. Search primary_name OR all_synonyms columns with ILIKE to find any drug.';

-- Grant permissions (adjust as needed)
GRANT SELECT ON drug_info TO PUBLIC;
GRANT SELECT ON drug_products TO PUBLIC;
GRANT SELECT ON drug_targets TO PUBLIC;
GRANT SELECT ON drug_classes TO PUBLIC;
GRANT SELECT ON drug_synonyms TO PUBLIC;
GRANT SELECT ON fda_approved_drugs TO PUBLIC;
GRANT SELECT ON drug_search_all TO PUBLIC;
