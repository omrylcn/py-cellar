from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from crud_api.db import db_session
from crud_api.crud import CompanyCRUD
from crud_api.schemas import CompanyUpdate, CompanyCreate


company_router = APIRouter()

@company_router.post("/")
async def create_company(company: CompanyCreate, db: AsyncSession = Depends(db_session)):
    try:
        crud = CompanyCRUD(session=db)
        company = await crud.create(data=company)
        return JSONResponse(content={"message": "Company created successfully!"},status_code=201)
    except Exception as e:
        return JSONResponse(content={"message": f"Error! : {e}"},status_code=500)
    
@company_router.get("/")
async def get_company(id: int, db: AsyncSession = Depends(db_session)):
    try:
        crud = CompanyCRUD(session=db)
        company = await crud.get(id=id)
        if company is None:
            return {"message": "No company found!"}
        else:
            return company
    except Exception as e:
        return {"message": f"Error! : {e}"}
    
@company_router.patch("/")
async def update_company(id: int, company_update: CompanyUpdate, db: AsyncSession = Depends(db_session)):
    try:
        crud = CompanyCRUD(session=db)
        company = await crud.patch(id=id, data=company_update)
        if company is None:
            return {"message": "No company found!"}
        else:
            return company
    except Exception as e:
        return {"message": f"Error! : {e}"}

@company_router.delete("/")
async def delete_company(id: int, db: AsyncSession = Depends(db_session)):
    try:
        crud = CompanyCRUD(session=db)
        success = await crud.delete(id=id)
        if success is False:
            return {"message": "No company found!"}
        else:
            return {"message": "Company deleted successfully!"}
    except Exception as e:
        return {"message": f"Error! : {e}"}