
from fastapi import APIRouter
from models.user_model import User

admin_router = APIRouter(
    prefix="/admin",
)

@admin_router.post("/login")
def login( req: User):
    return {"user": req.username, "status": "logged in"}