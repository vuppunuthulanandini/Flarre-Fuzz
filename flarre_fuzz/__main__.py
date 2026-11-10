"""One-command launcher:  python -m flarre_fuzz   (opens http://127.0.0.1:8000)"""
import threading, webbrowser
import uvicorn

if __name__ == "__main__":
    threading.Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:8000")).start()
    uvicorn.run("flarre_fuzz.api:app", host="127.0.0.1", port=8000)
