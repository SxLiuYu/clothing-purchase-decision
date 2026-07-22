import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.main import app

if __name__ == '__main__':
    import uvicorn

    host = os.environ.get('APP_HOST', '0.0.0.0')
    port = int(os.environ.get('APP_PORT', '8000'))
    env = os.environ.get('APP_ENV', 'development')
    reload = env == 'development'

    uvicorn.run(
        'app.main:app',
        host=host,
        port=port,
        reload=reload,
    )
