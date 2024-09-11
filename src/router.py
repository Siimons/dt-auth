from fastapi import APIRouter, HTTPException

from src.exceptions import (
    AppBaseException,
    UserAlreadyExistsException,
    UserNotFoundException,
    AuthenticationFailedException
)

from src.schemes import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserLogin
)

from src.service import (
    add_user,
    verify_password,
    get_user_info,
    update_user_info
)

router = APIRouter()

@router.post('/api/user/')
async def create_user(user: UserCreate):
    try:
        result = await add_user(user.username, user.email, user.password)
        return result
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=e.message)

@router.post('/api/login/')
async def get_user(user: UserLogin):
    try:
        result = await verify_password(user.email, user.password)
        return result
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except AuthenticationFailedException as e:
        raise HTTPException(status_code=401, detail=e.message)
    
@router.get('/api/user/info/')
async def find_user_info(user: UserResponse):
    try:
        result = await get_user_info(user.id, user.username, user.email)
        return result
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    
@router.put('/api/user/{id}')
async def update_user(user: UserUpdate):
    try:
        result = await update_user_info(user.id, user.username, user.email, user.password)
        return result 
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)