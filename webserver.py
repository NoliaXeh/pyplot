from plotserver import app

from uvicorn import run

run(app, host='127.0.0.1', port=8000)