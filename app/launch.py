import os, sys, subprocess
port = os.environ.get("DATABRICKS_APP_PORT", "8080")
sys.exit(subprocess.call([
    "streamlit", "run", "app.py",
    "--server.port", port,
    "--server.address", "0.0.0.0",
    "--server.headless", "true",
    "--server.enableCORS", "false",
    "--server.enableXsrfProtection", "false",
]))
