import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const systemId = searchParams.get('system_id') || '1';
    
    // Execute the Python script
    const { stdout, stderr } = await execAsync(
      `cd /Users/fabio/Desktop/foundry/backend && python ../generate_audit_ready_zip.py`,
      { 
        env: { 
          ...process.env,
          PYTHONPATH: '/Users/fabio/Desktop/foundry/backend'
        }
      }
    );
    
    if (stderr) {
      console.error('Python script error:', stderr);
    }
    
    // Read the generated ZIP file
    const fs = require('fs');
    const path = `/Users/fabio/Desktop/foundry/AUDIT-READY-${systemId}.zip`;
    
    if (!fs.existsSync(path)) {
      throw new Error('ZIP file not generated');
    }
    
    const zipBuffer = fs.readFileSync(path);
    
    return new NextResponse(zipBuffer, {
      headers: {
        'Content-Type': 'application/zip',
        'Content-Disposition': `attachment; filename="audit-ready-${systemId}.zip"`,
        'Content-Length': zipBuffer.length.toString(),
      },
    });
    
  } catch (error) {
    console.error('Error generating audit ZIP:', error);
    return NextResponse.json(
      { error: 'Failed to generate audit ZIP' },
      { status: 500 }
    );
  }
}
