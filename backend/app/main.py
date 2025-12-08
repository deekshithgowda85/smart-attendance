from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import APP_NAME, ORIGINS
from .api.routes.auth import router as auth_router
from .api.routes.students import router as students_router
from .api.routes.attendance import router as attendance_router


def create_app() -> FastAPI:
    app = FastAPI(title=APP_NAME)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(auth_router)
    app.include_router(students_router)
    app.include_router(attendance_router)

    return app


app = create_app()

# Optional: run directly with `python -m app.main`
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
