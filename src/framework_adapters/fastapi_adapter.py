"""
FastAPI adapter for integrating database security system
"""

from fastapi import Request, HTTPException, Depends
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.firewall import DatabaseFirewall


class FastAPISecurityMiddleware:
    """
    FastAPI middleware for database security
    
    Usage:
        from fastapi import FastAPI
        from framework_adapters import FastAPISecurityMiddleware
        
        app = FastAPI()
        security = FastAPISecurityMiddleware()
        
        @app.get("/api/users")
        async def get_users(
            auth=Depends(security.protect(app_id="my_app", operation="SELECT"))
        ):
            results = await security.execute("SELECT * FROM users")
            return results
    """
    
    def __init__(self, firewall: Optional[DatabaseFirewall] = None):
        self.firewall = firewall or DatabaseFirewall()
    
    def protect(self, app_id: str, operation: str):
        """
        Dependency for protecting routes
        """
        def dependency(request: Request):
            request.state.security_app_id = app_id
            request.state.security_operation = operation
            request.state.security_ip = request.client.host
            return self
        return dependency
    
    def execute(self, request: Request, query: str):
        """Execute a query through the security system"""
        app_id = getattr(request.state, 'security_app_id', 'unknown')
        operation = getattr(request.state, 'security_operation', 'SELECT')
        ip_address = getattr(request.state, 'security_ip', request.client.host)
        
        is_auth, results, reason = self.firewall.execute_query(
            app_id=app_id,
            ip_address=ip_address,
            operation=operation,
            query=query
        )
        
        if not is_auth:
            raise HTTPException(status_code=403, detail=reason)
        
        return results
    
    def get_logs(self):
        """Get security logs"""
        return self.firewall.get_logs()
    
    def create_routes(self, app):
        """Create security monitoring routes"""
        from fastapi.responses import JSONResponse
        
        @app.get("/api/security/logs")
        async def get_security_logs():
            logs = self.get_logs()
            return JSONResponse(content={'logs': logs})
        
        @app.get("/api/security/stats")
        async def get_security_stats():
            logs = self.get_logs()
            stats = {
                'total_queries': len(logs),
                'blocked_queries': sum(1 for log in logs if log['action'] == 'REDIRECTED_TO_HONEYPOT'),
                'unique_ips': len(set(log['ip_address'] for log in logs))
            }
            return JSONResponse(content=stats)
        
        @app.post("/api/security/query")
        async def execute_protected_query(request: Request):
            data = await request.json()
            
            if 'query' not in data:
                raise HTTPException(status_code=400, detail="Missing query parameter")
            
            ip_address = request.client.host
            is_auth, results, reason = self.firewall.execute_query(
                app_id=data.get('app_id', 'unknown'),
                ip_address=ip_address,
                operation=data.get('operation', 'SELECT'),
                query=data['query']
            )
            
            return {
                'authorized': is_auth,
                'results': results,
                'reason': reason
            }


# Example FastAPI app integration
def create_protected_app():
    """Example of creating a FastAPI app with security protection"""
    from fastapi import FastAPI, Depends
    
    app = FastAPI(title="Protected Database API")
    security = FastAPISecurityMiddleware()
    
    security.create_routes(app)
    
    @app.get("/api/users")
    async def get_users(
        request: Request,
        auth=Depends(security.protect(app_id="webapp_frontend", operation="SELECT"))
    ):
        results = await security.execute(request, "SELECT * FROM users")
        return {'users': results}
    
    return app


if __name__ == "__main__":
    import uvicorn
    app = create_protected_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
