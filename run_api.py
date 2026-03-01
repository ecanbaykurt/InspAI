#!/usr/bin/env python3
"""Run the Structure Analysis API server."""
import uvicorn

if __name__ == "__main__":
    # Mock mode by default so server starts without GPU; set STRUCTURE_API_MOCK=0 and GPU for real model
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
