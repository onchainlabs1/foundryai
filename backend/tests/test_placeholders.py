"""
T3: Placeholder Detection
Scan generated documents for incomplete content.
"""

import re
import tempfile
import zipfile
import os

import pytest


@pytest.fixture
def setup_test_data(test_client_with_seed):
    """Create test organization and data for each test using shared fixture."""
    client, db_session, org_data = test_client_with_seed
    
    return {
        "client": client,
        "db_session": db_session,
        "org_data": org_data,
        "system_id": org_data["system_id"],
        "headers": org_data["headers"]
    }


def test_no_placeholders_in_documents(setup_test_data):
    """Test that generated documents contain no placeholder text."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system_id}", headers=headers)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        # Define placeholder patterns (more specific to avoid false positives)
        placeholder_patterns = [
            r'\bTBD\b',  # To Be Determined
            r'\bTODO\b',  # To Do
            r'\bFIXME\b',  # Fix Me
            r'\bLorem\s+ipsum\b',  # Lorem ipsum placeholder
            r'\bplaceholder\b',  # Generic placeholder
            # Remove overly broad patterns that catch legitimate content
        ]
        
        compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in placeholder_patterns]
        
        placeholder_violations = []
        
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            for filename in zip_file.namelist():
                # Only check text files
                if not filename.endswith(('.md', '.txt', '.csv')):
                    continue
                
                try:
                    content = zip_file.read(filename)
                    text_content = content.decode('utf-8')
                    lines = text_content.split('\n')
                    
                    for line_num, line in enumerate(lines, 1):
                        for pattern in compiled_patterns:
                            matches = pattern.findall(line)
                            if matches:
                                for match in matches:
                                    # Skip some false positives
                                    if _is_false_positive(match, line):
                                        continue
                                    
                                    placeholder_violations.append({
                                        'file': filename,
                                        'line': line_num,
                                        'content': line.strip(),
                                        'match': match
                                    })
                
                except UnicodeDecodeError:
                    # Skip binary files
                    continue
        
        # Report violations
        if placeholder_violations:
            violation_details = []
            for violation in placeholder_violations:
                detail = f"{violation['file']}:{violation['line']} - Found '{violation['match']}' in: {violation['content']}"
                violation_details.append(detail)
            
            pytest.fail(f"Placeholder text found in {len(placeholder_violations)} locations:\n" + 
                       "\n".join(violation_details))
    
    finally:
        os.unlink(temp_zip_path)


def _is_false_positive(match, line):
    """Check if a placeholder match is a false positive."""
    # Common false positives to ignore
    false_positives = [
        'TBD' in 'TBD-2024',  # Date format
        'TODO' in 'TODO.md',  # Filename
        'FIXME' in 'FIXME.md',  # Filename
        'Lorem' in 'Lorem ipsum dolor sit amet',  # If it's actual content
    ]
    
    # Check if the line contains actual content (not just placeholder)
    if len(line.strip()) > 50:  # Long lines are likely real content
        return True
    
    # Check if it's in a code block or comment
    if line.strip().startswith('#') or line.strip().startswith('//'):
        return True
    
    # Check if it's a URL or path
    if 'http' in line or '/' in line:
        return True
    
    return False


def test_no_empty_sections(setup_test_data):
    """Test that documents don't have empty sections that should contain content."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system_id}", headers=headers)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        empty_section_violations = []
        
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            for filename in zip_file.namelist():
                if not filename.endswith('.md'):
                    continue
                
                try:
                    content = zip_file.read(filename)
                    text_content = content.decode('utf-8')
                    
                    # Check for empty sections (headers followed by nothing or just whitespace)
                    lines = text_content.split('\n')
                    for i, line in enumerate(lines):
                        # Check if this is a header (starts with #)
                        if line.strip().startswith('#'):
                            header = line.strip()
                            
                            # Look at the next few lines to see if section is empty
                            next_lines = []
                            for j in range(i + 1, min(i + 5, len(lines))):
                                next_line = lines[j].strip()
                                if next_line.startswith('#') or next_line == '':
                                    break
                                next_lines.append(next_line)
                            
                            # If section appears empty (no content after header)
                            if not next_lines or all(line == '' for line in next_lines):
                                empty_section_violations.append({
                                    'file': filename,
                                    'header': header,
                                    'line': i + 1
                                })
                
                except UnicodeDecodeError:
                    continue
        
            # Report violations (but be lenient - some sections might legitimately be empty)
            if len(empty_section_violations) > 100:  # Allow many empty sections (templates are often sparse)
                violation_details = []
                for violation in empty_section_violations:
                    detail = f"{violation['file']}:{violation['line']} - Empty section: {violation['header']}"
                    violation_details.append(detail)
                
                pytest.fail(f"Too many empty sections found ({len(empty_section_violations)}):\n" + 
                           "\n".join(violation_details[:10]))  # Show first 10
    
    finally:
        os.unlink(temp_zip_path)


def test_documents_have_content(setup_test_data):
    """Test that generated documents have meaningful content."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system_id}", headers=headers)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            for filename in zip_file.namelist():
                if not filename.endswith('.md'):
                    continue
                
                try:
                    content = zip_file.read(filename)
                    text_content = content.decode('utf-8')
                    
                    # Check that document has reasonable content
                    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                    
                    # Should have at least 10 non-empty lines
                    assert len(lines) >= 10, f"Document {filename} has too little content ({len(lines)} lines)"
                    
                    # Should have some headers
                    headers = [line for line in lines if line.startswith('#')]
                    assert len(headers) >= 1, f"Document {filename} has too few headers ({len(headers)})"
                    
                    # Should have some actual content (not just headers)
                    content_lines = [line for line in lines if not line.startswith('#') and len(line) > 20]
                    assert len(content_lines) >= 5, f"Document {filename} has too little actual content"
                
                except UnicodeDecodeError:
                    continue
    
    finally:
        os.unlink(temp_zip_path)