import uvicorn
from fastapi import FastAPI
from src.api.v1.routers.batches import router as batches_router
from src.api.v1.routers.products import router as products_router

app = FastAPI()

app.include_router(batches_router)
app.include_router(products_router)


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="127.0.0.1", reload=True)