from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.contrib.pydantic import PydanticInitPlugin
from app.routes.auth import auth_router
from app.routes.files import files_router
from app.database import engine, Base
from app.config import settings


# Create database tables
Base.metadata.create_all(bind=engine)

# Create Litestar app
app = Litestar(
    route_handlers=[auth_router, files_router],
    plugins=[PydanticInitPlugin(validate_strict=True)],
    cors_config=CORSConfig(
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    debug=settings.debug
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
