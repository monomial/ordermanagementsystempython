from pydantic import BaseModel, Field
from typing import List, Optional, TypeVar, Generic

# Define a TypeVar for the generic type
T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """
    A generic paginated response model that can be used with any type of item.
    """
    items: List[T]
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items across all pages")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    
    class Config:
        from_attributes = True 