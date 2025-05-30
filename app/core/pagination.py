from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Query
from sqlalchemy import func

T = TypeVar('T')

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int

    class Config:
        from_attributes = True

def paginate(query: Query, params: PaginationParams) -> PaginatedResponse:
    # Get total count
    total = query.count()
    if total:
        total = int(total)
    else:
        total = 0
    
    # Calculate pagination
    total_pages = (total + params.per_page - 1) // params.per_page
    offset = (params.page - 1) * params.per_page
    
    # Get paginated items
    items = query.offset(offset).limit(params.per_page).all()
    # print(items)
    print(params.page)
    print(params.per_page)
    print(total_pages)
    items=items,
    total=total,
    
    
    return PaginatedResponse(items=items, total=total, page=params.page, per_page=params.per_page, total_pages=total_pages)