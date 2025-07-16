from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
import os
import sqlite3
from typing import Optional

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

SECRET_KEY = os.environ.get("SECRET_KEY", "changemeinenv")
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
DATABASE_URL = os.environ.get("DATABASE_URL", "./users.db")

class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None

def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def get_user(db, username: str):
    cursor = db.cursor()
    cursor.execute('SELECT username, full_name, email FROM users WHERE username=?', (username,))
    row = cursor.fetchone()
    if row:
        return User(username=row[0], full_name=row[1], email=row[2])
    return None

def verify_token(token: str, db):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    user = get_user(db, username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    return user

@app.get("/users/me", response_model=User)
def read_users_me(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    return verify_token(token, db)

@app.post("/token")
def login(username: str, db=Depends(get_db)):
    # For simplicity in this mock, assume the user provides only a username
    user = get_user(db, username)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid user")
    encoded_jwt = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": encoded_jwt, "token_type": "bearer"}

@app.on_event("startup")
def startup_db():
    # Create a sample database & user for demonstration
dbfile = DATABASE_URL
    if not os.path.exists(dbfile):
        conn = sqlite3.connect(dbfile)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE users (username TEXT PRIMARY KEY, full_name TEXT, email TEXT)')
        cursor.execute('INSERT INTO users (username, full_name, email) VALUES (?,?,?)',
                       ("alice", "Alice Smith", "alice@example.com"))
        conn.commit()
        conn.close()
