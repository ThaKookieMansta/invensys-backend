from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, APIRouter, Depends

from core.config import Settings
from core.hashing import Hasher
from core.security import create_access_token
from db.repository.login import repo_get_user
from db.sessions import get_db
from schemas.token import Token

router = APIRouter()


async def authenticate_user(username: str, password: str, db: AsyncSession):
    user = await repo_get_user(username, db)
    if not user:
        return False
    if not Hasher.verify_password(password, user.password_hash):
        return False

    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Username or Password"
        )
    access_token = create_access_token(
        data={
            "sub": user.username
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Your token has expired. You need to renew it"
    )

    try:
        payload = jwt.decode(token, Settings.SECRET_KEY,
                             algorithms=[Settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await repo_get_user(username=username, db=db)
    if user is None:
        raise credentials_exception
    return user
