# Add to dashboard/main.py for tenant path handling

import os
from fastapi import FastAPI, Request
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles

# Tenant configuration
TENANT_NAME = os.environ.get('TENANT_NAME', 'mallon')
ROOT_PATH = f"/{TENANT_NAME}"

# Initialize FastAPI with root path for tenant
app = FastAPI(
    title="TM Legal Document Processing Platform",
    description="Enterprise Legal Document Processing for Mallon Consumer Law Group",
    version="1.9.0",
    root_path=ROOT_PATH  # This handles the /mallon/ prefix
)

class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to handle tenant-specific configurations"""
    
    async def dispatch(self, request: Request, call_next):
        # Add tenant context to request
        request.state.tenant = TENANT_NAME
        
        # Handle root redirect
        if request.url.path == "/":
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=f"{ROOT_PATH}/", status_code=301)
        
        response = await call_next(request)
        
        # Add tenant-specific headers
        response.headers["X-Tenant"] = TENANT_NAME
        response.headers["X-TM-Version"] = "1.9.0"
        
        return response

# Add middleware
app.add_middleware(TenantMiddleware)

# Update static file mounting for tenant path
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add tenant-aware settings
@app.get("/api/tenant/info")
async def get_tenant_info():
    """Get tenant-specific configuration"""
    return {
        "tenant": TENANT_NAME,
        "domain": "legal.satori-ai-tech.com",
        "ssl_enabled": True,
        "version": "1.9.0"
    }

# Update base URLs in templates
def get_base_url():
    """Get the base URL for the current tenant"""
    return f"https://legal.satori-ai-tech.com{ROOT_PATH}"

# Add to existing routes for proper URL generation
@app.get("/")
async def dashboard_root(request: Request):
    """Main dashboard with tenant context"""
    # Your existing dashboard code here
    # Make sure URLs in templates use get_base_url()
    pass
