from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import predict


@asynccontextmanager
async def lifespan(app: FastAPI):
    # https://fastapi.tiangolo.com/advanced/events/#lifespan
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_api_route("/predict", predict, methods=["GET"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="app.__main__:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
