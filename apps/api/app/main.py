from fastapi import FastAPI

app = FastAPI(title="Shopping Copilot API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
