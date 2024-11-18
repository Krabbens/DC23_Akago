from typing import AsyncGenerator

from fastapi.templating import Jinja2Templates

from akago.config import TEMPLATES_DIR


async def get_templates() -> AsyncGenerator[Jinja2Templates, None]:
    templates = Jinja2Templates(directory=TEMPLATES_DIR)

    yield templates
