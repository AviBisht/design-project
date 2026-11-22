import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("STARTING CLINICAL INTELLIGENCE BENCHMARK CONSOLE")
    print("Dual-Pipeline Comparative Study (VMSB UTU Capstone 2026-27)")
    print("URL: http://127.0.0.1:8000")
    print("=" * 70)
    uvicorn.run("web.app:app", host="127.0.0.1", port=8000, reload=True)

