# Time-To-Value Manual Checklist

**Objective:** Complete system onboarding → ZIP export in ≤40 minutes

## Prerequisites (not counted in time)
- [ ] Access to frontend (localhost:3000 or production URL)
- [ ] API key obtained
- [ ] Browser ready
- [ ] Test data prepared (sample PDFs, etc.)

## Timed Steps (Start timer)

### Step 1: System Onboarding (Target: 8 min)
- [ ] Navigate to /onboarding
- [ ] Fill: Name, Purpose, Domain, AI Act Class
- [ ] Submit → Note system_id
- **Checkpoint:** System created
- **Time taken:** _____ minutes

### Step 2: Evidence Upload (Target: 10 min)
- [ ] Navigate to Inventory → Evidence
- [ ] Upload 5 evidence files (sample PDFs)
- [ ] Add descriptions for each
- **Checkpoint:** 5 evidences uploaded
- **Time taken:** _____ minutes

### Step 3: FRIA Submission (Target: 5 min)
- [ ] Navigate to Reports → FRIA
- [ ] Answer assessment questions
- [ ] Submit FRIA
- **Checkpoint:** FRIA completed
- **Time taken:** _____ minutes

### Step 4: Controls Management (Target: 10 min)
- [ ] Navigate to Templates → Controls
- [ ] Bulk import or create 10 controls
- [ ] Assign owners and due dates
- **Checkpoint:** 10 controls created
- **Time taken:** _____ minutes

### Step 5: Incident Logging (Target: 2 min)
- [ ] Navigate to Incidents
- [ ] Log 1 incident with corrective action
- **Checkpoint:** Incident logged
- **Time taken:** _____ minutes

### Step 6: ZIP Export (Target: 5 min)
- [ ] Navigate to Reports
- [ ] Click "Export Annex IV"
- [ ] Download ZIP
- [ ] Extract and verify contents
- **Checkpoint:** ZIP downloaded (Stop timer)
- **Time taken:** _____ minutes

## Results
- **Total Time:** _____ minutes
- **Target Met:** [ ] Yes (≤40 min) [ ] No
- **Completion Rate:** ___/6 steps = ____%
- **Notes:** _______________

## Detailed Timing Breakdown

| Step | Target Time | Actual Time | Variance | Notes |
|------|-------------|-------------|----------|-------|
| 1. System Onboarding | 8 min | _____ min | _____ min | |
| 2. Evidence Upload | 10 min | _____ min | _____ min | |
| 3. FRIA Submission | 5 min | _____ min | _____ min | |
| 4. Controls Management | 10 min | _____ min | _____ min | |
| 5. Incident Logging | 2 min | _____ min | _____ min | |
| 6. ZIP Export | 5 min | _____ min | _____ min | |
| **Total** | **40 min** | **_____ min** | **_____ min** | |

## Quality Checklist

### System Creation
- [ ] System name is descriptive
- [ ] Purpose is clearly defined
- [ ] Domain is appropriate
- [ ] AI Act class is correct
- [ ] Role is specified

### Evidence Upload
- [ ] All 5 files uploaded successfully
- [ ] File descriptions are meaningful
- [ ] Files are properly categorized
- [ ] No upload errors

### FRIA Assessment
- [ ] All questions answered
- [ ] Answers are consistent
- [ ] FRIA is marked as applicable/not applicable
- [ ] Assessment is submitted

### Controls Management
- [ ] 10 controls created
- [ ] Controls have proper ISO clauses
- [ ] Owners are assigned
- [ ] Due dates are set
- [ ] Priorities are assigned

### Incident Logging
- [ ] Incident is properly described
- [ ] Severity is appropriate
- [ ] Corrective action is documented
- [ ] Status is set

### ZIP Export
- [ ] ZIP file downloads successfully
- [ ] ZIP contains expected files
- [ ] Files are not corrupted
- [ ] Manifest is present and valid

## Common Issues and Solutions

### System Creation Issues
- **Issue:** Form validation errors
- **Solution:** Check required fields, ensure proper format
- **Time Impact:** +2-3 minutes

### Evidence Upload Issues
- **Issue:** File upload failures
- **Solution:** Check file size limits, MIME types
- **Time Impact:** +5-10 minutes

### FRIA Issues
- **Issue:** Assessment questions unclear
- **Solution:** Refer to documentation, ask for clarification
- **Time Impact:** +3-5 minutes

### Controls Issues
- **Issue:** Bulk import fails
- **Solution:** Check CSV format, try individual creation
- **Time Impact:** +5-15 minutes

### Export Issues
- **Issue:** ZIP generation fails
- **Solution:** Check system completeness, retry
- **Time Impact:** +2-5 minutes

## Performance Optimization Tips

### For Faster System Creation
- [ ] Prepare system details in advance
- [ ] Use templates for common configurations
- [ ] Have domain and AI Act class pre-determined

### For Faster Evidence Upload
- [ ] Prepare all files in advance
- [ ] Use consistent naming conventions
- [ ] Have descriptions ready
- [ ] Use bulk upload if available

### For Faster FRIA Assessment
- [ ] Review questions beforehand
- [ ] Have answers prepared
- [ ] Use consistent assessment criteria

### For Faster Controls Management
- [ ] Use bulk import templates
- [ ] Prepare control data in advance
- [ ] Use standard ISO clauses
- [ ] Assign owners in bulk

### For Faster Incident Logging
- [ ] Prepare incident details
- [ ] Use standard incident templates
- [ ] Have corrective actions ready

### For Faster ZIP Export
- [ ] Ensure all prerequisites are met
- [ ] Check system completeness
- [ ] Use high-speed internet connection

## Success Criteria

### Time Targets
- [ ] Total time ≤ 40 minutes
- [ ] Each step within target time
- [ ] No major delays or blockers

### Quality Targets
- [ ] All 6 steps completed
- [ ] No errors or failures
- [ ] All data properly entered
- [ ] ZIP export successful

### User Experience
- [ ] Interface is intuitive
- [ ] No confusing steps
- [ ] Clear progress indicators
- [ ] Helpful error messages

## Reporting

### For Each Test
- [ ] Record start and end times
- [ ] Note any issues encountered
- [ ] Document solutions applied
- [ ] Rate user experience (1-5)

### For Multiple Tests
- [ ] Calculate average time
- [ ] Identify common bottlenecks
- [ ] Note improvement areas
- [ ] Track progress over time

## Test Environment

### Local Testing
- [ ] Frontend: http://localhost:3000
- [ ] Backend: http://localhost:8000
- [ ] Database: SQLite local
- [ ] Storage: Local filesystem

### Production Testing
- [ ] Frontend: https://aims.yourdomain.com
- [ ] Backend: https://api.aims.yourdomain.com
- [ ] Database: PostgreSQL
- [ ] Storage: MinIO

## Test Data Requirements

### Sample Files (5 required)
- [ ] model_card.pdf (2-5 MB)
- [ ] training_data_spec.pdf (1-3 MB)
- [ ] validation_report.pdf (3-7 MB)
- [ ] bias_analysis.pdf (2-4 MB)
- [ ] security_audit.pdf (5-10 MB)

### System Information
- [ ] System name: "TTV Test System"
- [ ] Purpose: "Automated decision making for TTV testing"
- [ ] Domain: "finance"
- [ ] AI Act class: "high"
- [ ] Role: "provider"

### FRIA Answers
- [ ] Biometric data: No
- [ ] Fundamental rights: Yes
- [ ] Critical infrastructure: No
- [ ] Vulnerable groups: Yes
- [ ] High-risk area: Yes

### Controls (10 required)
- [ ] ISO42001:6.1 - Risk Management Process (High, Implemented)
- [ ] ISO42001:6.2 - Risk Assessment (High, Implemented)
- [ ] ISO42001:7.1 - Resource Management (Medium, In Progress)
- [ ] ISO42001:7.2 - Competence (Medium, Implemented)
- [ ] ISO42001:7.3 - Awareness (Low, Planned)
- [ ] ISO42001:8.1 - Operational Planning (High, Implemented)
- [ ] ISO42001:8.2 - AI System Development (High, Implemented)
- [ ] ISO42001:8.3 - AI System Deployment (High, Implemented)
- [ ] ISO42001:8.4 - AI System Operation (Medium, In Progress)
- [ ] ISO42001:8.5 - AI System Monitoring (Medium, Implemented)

### Incident
- [ ] Severity: Medium
- [ ] Description: "Model drift detected in production"
- [ ] Corrective action: "Retrained model with recent data"
- [ ] Status: Resolved

## Validation

### ZIP Contents
- [ ] manifest.json
- [ ] annex_iv.md
- [ ] fria.md
- [ ] soa.csv
- [ ] monitoring_report.md
- [ ] controls.csv
- [ ] risk_register.md
- [ ] evidence_manifest.csv
- [ ] All evidence files

### File Integrity
- [ ] All files are readable
- [ ] No corrupted files
- [ ] Proper file sizes
- [ ] Correct MIME types

### Content Quality
- [ ] No placeholder text
- [ ] All fields populated
- [ ] Consistent formatting
- [ ] Proper citations

## Troubleshooting

### Common Problems
1. **Slow page loads**: Check internet connection, clear browser cache
2. **Upload failures**: Check file size limits, try different files
3. **Form errors**: Check required fields, ensure proper format
4. **Export failures**: Check system completeness, retry
5. **Timeout errors**: Check server status, retry

### Emergency Procedures
1. **System crash**: Restart browser, clear cache, retry
2. **Data loss**: Check if data is saved, restore from backup
3. **Export failure**: Check system status, contact support
4. **Performance issues**: Check server load, try again later

## Notes

### Test Date: ___________
### Tester: ___________
### Environment: ___________
### Browser: ___________
### Internet Speed: ___________

### Additional Notes:
_________________________________
_________________________________
_________________________________

### Recommendations:
_________________________________
_________________________________
_________________________________
