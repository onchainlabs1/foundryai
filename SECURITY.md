# Security Documentation

This document outlines the security measures, configurations, and best practices for the AIMS Readiness platform.

## Security Architecture

### 1. Application Security

#### Authentication & Authorization
- **API Key Authentication**: All API endpoints require valid API keys
- **Organization Isolation**: Data is isolated by organization
- **Role-Based Access**: Different access levels for different operations
- **Session Management**: Secure session handling with proper expiration

#### Data Protection
- **Encryption at Rest**: Database and file storage encryption
- **Encryption in Transit**: HTTPS/TLS for all communications
- **Data Anonymization**: PII handling and anonymization procedures
- **Access Logging**: Comprehensive audit trails

### 2. Infrastructure Security

#### Network Security
- **Firewall Configuration**: Only necessary ports exposed
- **VPN Access**: Secure remote access to infrastructure
- **Network Segmentation**: Isolated network segments
- **DDoS Protection**: Cloudflare DDoS protection

#### Server Security
- **OS Hardening**: Minimal attack surface
- **Regular Updates**: Automated security updates
- **Intrusion Detection**: Monitoring and alerting
- **Backup Security**: Encrypted backups

## MinIO Security Configuration

### 1. Firewall Rules

```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw deny 9000/tcp   # MinIO API (internal only)
ufw deny 9001/tcp   # MinIO Console (internal only)

# Enable firewall
ufw enable
```

### 2. MinIO Access Configuration

```yaml
# docker-compose.production.yml
minio:
  environment:
    - MINIO_ROOT_USER=${MINIO_ACCESS_KEY}
    - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY}
    - MINIO_BROWSER_REDIRECT_URL=https://minio.aims.yourdomain.com
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.minio.rule=Host(`minio.aims.yourdomain.com`)"
    - "traefik.http.routers.minio.tls.certresolver=letsencrypt"
    - "traefik.http.routers.minio.tls=true"
    - "traefik.http.routers.minio.middlewares=auth"
    - "traefik.http.middlewares.auth.basicauth.users=admin:$$2y$$10$$..."
```

### 3. Bucket Policies

#### Evidence Bucket (Private)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::aims-evidence/*",
      "Condition": {
        "StringNotEquals": {
          "aws:Referer": "https://aims.yourdomain.com"
        }
      }
    }
  ]
}
```

#### Public Documents Bucket
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::aims-public/*"
    }
  ]
}
```

### 4. Presigned URLs

```python
# Generate presigned URLs for secure access
def generate_presigned_url(bucket, key, expiration=3600):
    return minio_client.presigned_get_object(
        bucket, 
        key, 
        expires=timedelta(seconds=expiration)
    )
```

## Rate Limiting Configuration

### 1. Traefik Rate Limiting

```yaml
# docker-compose.production.yml
labels:
  - "traefik.http.middlewares.ratelimit.ratelimit.burst=100"
  - "traefik.http.middlewares.ratelimit.ratelimit.average=50"
  - "traefik.http.routers.aims-api.middlewares=ratelimit"
```

### 2. Application Rate Limiting

```python
# FastAPI rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/evidence/{system_id}")
@limiter.limit("10/minute")
async def upload_evidence(request: Request, ...):
    pass
```

### 3. API Key Throttling

```python
# Per-API-key rate limiting
@limiter.limit("1000/hour", key_func=lambda request: request.headers.get("X-API-Key"))
async def api_endpoint(request: Request, ...):
    pass
```

## Content Security Policy (CSP)

### 1. CSP Headers

```python
# FastAPI CSP middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://aims.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add CSP headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://api.aims.yourdomain.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

### 2. Next.js CSP Configuration

```javascript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.aims.yourdomain.com;"
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin'
  }
]

module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ]
  },
}
```

## File Upload Security

### 1. MIME Type Validation

```python
# Allowed MIME types
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'text/plain',
    'text/csv',
    'application/json',
    'text/markdown'
}

# File validation
def validate_file_type(file: UploadFile) -> bool:
    return file.content_type in ALLOWED_MIME_TYPES
```

### 2. File Size Limits

```python
# File size limits
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_TOTAL_SIZE = 500 * 1024 * 1024  # 500MB per system

# Size validation
def validate_file_size(file: UploadFile) -> bool:
    return file.size <= MAX_FILE_SIZE
```

### 3. Malware Scanning

```python
# Basic file content validation
def scan_file_content(content: bytes) -> bool:
    # Check for suspicious patterns
    suspicious_patterns = [
        b'<script',
        b'javascript:',
        b'vbscript:',
        b'data:text/html',
        b'<iframe',
        b'<object',
        b'<embed'
    ]
    
    for pattern in suspicious_patterns:
        if pattern in content.lower():
            return False
    
    return True
```

### 4. Secure File Storage

```python
# Secure file naming
import uuid
import hashlib

def generate_secure_filename(original_filename: str) -> str:
    # Generate secure filename
    file_id = str(uuid.uuid4())
    extension = os.path.splitext(original_filename)[1]
    return f"{file_id}{extension}"

# File path validation
def validate_file_path(file_path: str) -> bool:
    # Prevent directory traversal
    return not ('..' in file_path or file_path.startswith('/'))
```

## API Key Management

### 1. API Key Generation

```python
# Secure API key generation
import secrets
import string

def generate_api_key(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# API key format: aims-{random-string}
def generate_organization_api_key() -> str:
    random_part = generate_api_key(24)
    return f"aims-{random_part}"
```

### 2. API Key Rotation

```python
# API key rotation procedure
def rotate_api_key(org_id: int) -> str:
    # Generate new key
    new_key = generate_organization_api_key()
    
    # Update in database
    db.query(Organization).filter(Organization.id == org_id).update({
        "api_key": new_key
    })
    db.commit()
    
    # Log rotation
    log_api_key_rotation(org_id, new_key)
    
    return new_key
```

### 3. API Key Validation

```python
# API key validation
def validate_api_key(api_key: str) -> Optional[Organization]:
    if not api_key or len(api_key) < 20:
        return None
    
    # Check format
    if not api_key.startswith('aims-'):
        return None
    
    # Check database
    return db.query(Organization).filter(
        Organization.api_key == api_key
    ).first()
```

## Database Security

### 1. Connection Security

```python
# Secure database connection
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=require"

# Connection pool configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### 2. Query Security

```python
# Parameterized queries only
def get_system_by_id(system_id: int, org_id: int):
    return db.query(AISystem).filter(
        AISystem.id == system_id,
        AISystem.org_id == org_id
    ).first()

# No raw SQL with user input
def unsafe_query(user_input: str):
    # NEVER DO THIS
    query = f"SELECT * FROM systems WHERE name = '{user_input}'"
    return db.execute(query)
```

### 3. Data Encryption

```python
# Encrypt sensitive data
from cryptography.fernet import Fernet

def encrypt_sensitive_data(data: str) -> str:
    key = os.getenv('ENCRYPTION_KEY')
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data: str) -> str:
    key = os.getenv('ENCRYPTION_KEY')
    f = Fernet(key)
    return f.decrypt(encrypted_data.encode()).decode()
```

## Incident Response

### 1. Security Incident Classification

```python
# Incident severity levels
INCIDENT_SEVERITY = {
    'low': 'Minor security issue, no data exposure',
    'medium': 'Potential data exposure, limited impact',
    'high': 'Data exposure confirmed, significant impact',
    'critical': 'System compromise, immediate action required'
}
```

### 2. Incident Response Procedures

```python
# Automated incident response
def handle_security_incident(incident_type: str, severity: str):
    # Log incident
    log_security_incident(incident_type, severity)
    
    # Notify security team
    if severity in ['high', 'critical']:
        notify_security_team(incident_type, severity)
    
    # Take automated actions
    if severity == 'critical':
        # Disable affected API keys
        disable_affected_api_keys()
        
        # Block suspicious IPs
        block_suspicious_ips()
        
        # Alert administrators
        alert_administrators()
```

### 3. Security Monitoring

```python
# Security event monitoring
def monitor_security_events():
    # Monitor failed login attempts
    failed_logins = get_failed_login_attempts()
    if len(failed_logins) > 10:
        handle_security_incident('brute_force', 'medium')
    
    # Monitor unusual API usage
    unusual_usage = detect_unusual_api_usage()
    if unusual_usage:
        handle_security_incident('unusual_usage', 'low')
    
    # Monitor file uploads
    suspicious_uploads = detect_suspicious_uploads()
    if suspicious_uploads:
        handle_security_incident('suspicious_upload', 'medium')
```

## Compliance and Auditing

### 1. Audit Logging

```python
# Comprehensive audit logging
def log_audit_event(user_id: int, action: str, resource: str, details: dict):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        details=details,
        timestamp=datetime.utcnow(),
        ip_address=get_client_ip(),
        user_agent=get_user_agent()
    )
    db.add(audit_log)
    db.commit()
```

### 2. Data Retention

```python
# Data retention policies
DATA_RETENTION_POLICIES = {
    'audit_logs': 7 * 365,  # 7 years
    'user_sessions': 30,     # 30 days
    'temp_files': 1,         # 1 day
    'backup_files': 90       # 90 days
}

def cleanup_expired_data():
    for data_type, retention_days in DATA_RETENTION_POLICIES.items():
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        delete_expired_data(data_type, cutoff_date)
```

### 3. Compliance Reporting

```python
# Generate compliance reports
def generate_compliance_report(org_id: int, report_type: str):
    if report_type == 'gdpr':
        return generate_gdpr_report(org_id)
    elif report_type == 'ai_act':
        return generate_ai_act_report(org_id)
    elif report_type == 'iso42001':
        return generate_iso42001_report(org_id)
    else:
        raise ValueError(f"Unknown report type: {report_type}")
```

## Security Testing

### 1. Automated Security Tests

```python
# Security test suite
def test_api_key_authentication():
    # Test without API key
    response = client.get("/systems")
    assert response.status_code == 401
    
    # Test with invalid API key
    response = client.get("/systems", headers={"X-API-Key": "invalid"})
    assert response.status_code == 401
    
    # Test with valid API key
    response = client.get("/systems", headers={"X-API-Key": "valid-key"})
    assert response.status_code == 200

def test_file_upload_security():
    # Test malicious file upload
    malicious_content = b"<script>alert('xss')</script>"
    response = client.post(
        "/evidence/1",
        files={"file": ("malicious.html", malicious_content, "text/html")},
        headers=HEADERS
    )
    assert response.status_code == 400  # Should be rejected
```

### 2. Penetration Testing

```bash
# OWASP ZAP security testing
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://api.aims.yourdomain.com \
  -r zap-report.html

# Nmap port scanning
nmap -sS -O -sV -p 1-65535 api.aims.yourdomain.com
```

## Security Checklist

### Pre-Deployment Security Checklist

- [ ] All environment variables are secure
- [ ] API keys are properly generated and stored
- [ ] Database passwords are strong and unique
- [ ] SSL certificates are properly configured
- [ ] Firewall rules are properly set
- [ ] File upload restrictions are in place
- [ ] Rate limiting is configured
- [ ] CSP headers are set
- [ ] Audit logging is enabled
- [ ] Backup procedures are tested
- [ ] Incident response procedures are documented
- [ ] Security monitoring is active

### Post-Deployment Security Checklist

- [ ] All services are running securely
- [ ] SSL certificates are valid and auto-renewing
- [ ] Security headers are present
- [ ] API endpoints are properly protected
- [ ] File uploads are working within limits
- [ ] Rate limiting is functioning
- [ ] Audit logs are being generated
- [ ] Monitoring alerts are configured
- [ ] Backup procedures are working
- [ ] Incident response procedures are tested

## Security Contacts

### Internal Security Team
- **Security Lead**: security@yourdomain.com
- **Incident Response**: incident@yourdomain.com
- **Compliance**: compliance@yourdomain.com

### External Security Contacts
- **Security Researcher**: security-research@yourdomain.com
- **Bug Bounty**: bug-bounty@yourdomain.com
- **Legal**: legal@yourdomain.com

## Security Updates

This security documentation is regularly updated to reflect:
- New security threats and mitigations
- Updated compliance requirements
- Improved security practices
- New security tools and technologies

**Last Updated**: 2024-01-01
**Next Review**: 2024-04-01
**Version**: 1.0
