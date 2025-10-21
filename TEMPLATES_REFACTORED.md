# Templates Refactoring Status

## ✅ REFATORADOS (8/14):

1. ✅ `01_RISK_ASSESSMENT.md` - Uses `{% for risk in risks %}`
2. ✅ `02_IMPACT_ASSESSMENT.md` - Uses risks + FRIA data
3. ✅ `06_PM_MONITORING_REPORT.md` - Uses PMM real data
4. ✅ `07_HUMAN_OVERSIGHT_SOP.md` - Uses Oversight real data  
5. ✅ `09_SOA_TEMPLATE.md` - Uses controls + evidence
6. ✅ `12_ANNEX_IV.md` - Complete with all sections
7. ✅ `13_INSTRUCTIONS_FOR_USE.md` - New audit-grade template
8. ✅ `14_TRANSPARENCY_NOTICE_GPAI.md` - New conditional template

## ⚠️ AINDA COM PLACEHOLDERS (6/14):

3. `03_MODEL_CARD.md` - ML-specific, can use system data
4. `04_DATA_SHEET.md` - Data-specific, can use system data  
5. `05_LOGGING_PLAN.md` - Can use PMM logging_scope
6. `08_APPEALS_FLOW.md` - Can use oversight appeals data
7. `10_POLICY_REGISTER.md` - Generic policies
8. `11_AUDIT_LOG.md` - Generic audit trail

## DECISÃO:

Templates 3-5 e 8 são **úteis** - vou refatorar.  
Templates 10-11 são **genéricos** - podem ficar como estão (não impedem audit-grade).

**Ação:** Refatorar 03, 04, 05, 08 (4 templates).
