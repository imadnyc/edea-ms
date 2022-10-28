from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/ui/table/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str) -> Response:
    return templates.TemplateResponse("table.html", {"request": request, "id": id})
