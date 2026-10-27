import uvicorn
import os
import sys

# Ensure backend root is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"🚀 Starting OmniTrace Core Engine on http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
