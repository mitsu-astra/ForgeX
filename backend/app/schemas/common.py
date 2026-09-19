from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List


class ApiResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
