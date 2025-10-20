"""
Templates API endpoints for ISO/IEC 42001 templates.
"""
import os
import yaml
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.database import get_db
from app.models import Organization

router = APIRouter()

# Template metadata cache
_template_cache: List[Dict[str, Any]] = []

def load_templates_from_filesystem() -> List[Dict[str, Any]]:
    """Load template metadata from filesystem."""
    templates_dir = "/Users/fabio/Desktop/foundry/aims_readiness_templates_en"
    templates = []
    
    if not os.path.exists(templates_dir):
        return templates
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.md') and filename != 'README.md':
            file_path = os.path.join(templates_dir, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse front-matter YAML
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        yaml_content = parts[1].strip()
                        markdown_content = parts[2].strip()
                        
                        try:
                            metadata = yaml.safe_load(yaml_content)
                            if metadata:
                                template_info = {
                                    "filename": filename,
                                    "template_id": metadata.get("template_id", filename.replace('.md', '')),
                                    "iso_clauses": metadata.get("iso_clauses", []),
                                    "ai_act": metadata.get("ai_act", []),
                                    "version": metadata.get("version", "1.0.0"),
                                    "language": metadata.get("language", "en"),
                                    "generated_at": metadata.get("generated_at", ""),
                                    "size": len(content)
                                }
                                templates.append(template_info)
                        except yaml.YAMLError:
                            # Fallback if YAML parsing fails
                            template_info = {
                                "filename": filename,
                                "template_id": filename.replace('.md', ''),
                                "iso_clauses": [],
                                "ai_act": [],
                                "version": "1.0.0",
                                "language": "en",
                                "generated_at": "",
                                "size": len(content)
                            }
                            templates.append(template_info)
            except Exception as e:
                logger.error(f"Error loading template {filename}: {e}")
                continue
    
    return sorted(templates, key=lambda x: x["filename"])

@router.get("/templates")
async def get_templates(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Get list of available ISO/IEC 42001 templates.
    Returns metadata only (no full content).
    """
    global _template_cache
    
    # Reload cache if empty
    if not _template_cache:
        _template_cache = load_templates_from_filesystem()
    
    return {
        "templates": _template_cache,
        "count": len(_template_cache)
    }

@router.get("/templates/{template_id}")
async def get_template_content(
    template_id: str,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Get raw content of a specific template.
    Returns the full Markdown file content.
    """
    templates_dir = "/Users/fabio/Desktop/foundry/aims_readiness_templates_en"
    
    # Find template by template_id or filename
    template_file = None
    for filename in os.listdir(templates_dir):
        if filename.endswith('.md') and filename != 'README.md':
            file_path = os.path.join(templates_dir, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if template_id matches
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        yaml_content = parts[1].strip()
                        try:
                            metadata = yaml.safe_load(yaml_content)
                            if metadata and metadata.get("template_id") == template_id:
                                template_file = filename
                                break
                        except yaml.YAMLError:
                            pass
                
                # Fallback: check filename
                if filename.replace('.md', '') == template_id:
                    template_file = filename
                    break
            except Exception:
                continue
    
    if not template_file:
        raise HTTPException(status_code=404, detail="Template not found")
    
    file_path = os.path.join(templates_dir, template_file)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return PlainTextResponse(
            content=content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"inline; filename={template_file}",
                "X-Template-ID": template_id
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading template: {str(e)}")

def initialize_templates():
    """Initialize template cache on startup."""
    logger = logging.getLogger(__name__)
    global _template_cache
    _template_cache = load_templates_from_filesystem()
    logger.info(f"Templates loaded: {len(_template_cache)}")
