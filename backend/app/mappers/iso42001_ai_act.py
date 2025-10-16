"""ISO 42001 to AI Act mapping."""

ISO_TO_AI_ACT = {
    "ISO42001:5.1 Governance": ["AIAct:Accountability", "AIAct:Transparency"],
    "ISO42001:6.1 Risk Management": ["AIAct:RiskMgmt", "AIAct:PostMarketMonitoring"],
    "ISO42001:7.2 Competence": ["AIAct:AI_Literacy"],
    "ISO42001:8.3 Design & Dev": ["AIAct:DataGovernance", "AIAct:TechnicalDocumentation"],
    "ISO42001:9.1 Monitoring": ["AIAct:Logging", "AIAct:RecordKeeping"],
}

