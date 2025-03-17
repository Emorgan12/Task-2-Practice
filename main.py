from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Annotated
from pydantic import BaseModel


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def lifespan(app: FastAPI):
    print("Starting up")
    SQLModel.metadata.create_all(engine)
    yield
    print("Shutting down")

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserBase(BaseModel):
    username: str
    full_name: str = None
    age: int

class User(UserBase, SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    password: str
    bmi: float = Field(default=0)

class UserPublic(UserBase):
    id: int = None
    bmi: float = None

class UserCreate(UserBase):
    password: str
    email: str

class BMICalculate(BaseModel):
    user_id: int
    weight: float
    height: float

@app.get("/getUserByName")
def get_name(username: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            return False
        else:
            return user

@app.post("/CreateUser", response_model=UserPublic)
def create_user(user: UserCreate):
    user = User.model_validate(user)
    name_exists = get_name(user.username)
    if name_exists:
        raise HTTPException(status_code=400, detail="Username already exists")
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

@app.get("/GetUsers/", response_model=list[UserPublic])
def get_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
    return users

@app.get("/GetUser/{user_id}", response_model=UserPublic)
def get_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
    return user

@app.delete("/DeleteUser/{user_id}")
def delete_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        session.delete(user)
        session.commit()
    return {"message": "User deleted successfully"}

@app.post("/CalculateBMI", )
def calculate_bmi(bmi: BMICalculate):
    CalculatedBMI = bmi.weight / (bmi.height ** 2)
    with Session(engine) as session:
        user = session.get(User, bmi.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.bmi = CalculatedBMI
        session.add(user)
        session.commit()
        session.refresh(user)
    return CalculatedBMI

