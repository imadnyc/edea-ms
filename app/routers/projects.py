from typing import List

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.models import Project

router = APIRouter()


@router.get("/projects", response_model=List[Project], tags=["projects"])
async def get_projects() -> List[Project]:
    items = await Project.objects.all()
    return items


@router.post("/projects", response_model=Project, tags=["projects"])
async def create_projects(project: Project) -> Project:
    await project.save()
    return project


@router.put("/projects/{id}", tags=["projects"])
async def get_project(id: int, project: Project) -> Project:
    tx = await Project.objects.get(pk=id)
    return await tx.update(**project.dict())


@router.delete("/projects/{id}", tags=["projects"])
async def delete_project(id: int, project: Project = None) -> JSONResponse:
    if project:
        return JSONResponse(content={"deleted_rows": await project.delete()})
    tx = await Project.objects.get(pk=id)
    return JSONResponse(content={"deleted_rows": await tx.delete()})
