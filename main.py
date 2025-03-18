from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Annotated
from pydantic import BaseModel

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

#define database name
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

#create tables and database on startup
def lifespan(app: FastAPI):
    print("Starting up")
    SQLModel.metadata.create_all(engine)
    yield
    print("Shutting down")

app = FastAPI(lifespan=lifespan)

#allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserBase(BaseModel):
    title: str
    first_name: str
    last_name: str
    username: str = Field(nullable=True)

#user model in table
class User(UserBase, SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    password: str = Field(nullable=True)
    email: str

class UserPublic(UserBase):
    id: int = None

class UserCreate(UserBase):
    password: str
    email: str

class AddressBase(BaseModel):
    unit_number: str = Field(nullable=True)
    line_1: str
    line_2: str = Field(nullable=True)
    city: str
    postcode: str

#address model in table
class Address(AddressBase, SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

class AppointmentBase(BaseModel):
    time: str
    date: str
    appointment_type: str
    product: str
    user_id: int = Field(default=None, foreign_key="user.id")
    address_id: int = Field(default=None, foreign_key="address.id")
    consultation_id: int = Field(default=None, foreign_key="appointment.id", nullable=True)

#appointment model in table
class Appointment(AppointmentBase, SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

#get user by name, check if exists
@app.get("/getUserByName")
def get_name(username: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            return False
        else:
            return user

#create user
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

#get all users
@app.get("/GetUsers/", response_model=list[UserPublic])
def get_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
    return users

#get user by id
@app.get("/GetUser/{user_id}", response_model=UserPublic)
def get_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
    return user

#login with username and password
@app.get("/Login")
def login(username: str, password: str):
    user = get_name(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.password == password:
        return True
    else:
        return False

#delete user by id
@app.delete("/DeleteUser/{user_id}")
def delete_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        session.delete(user)
        session.commit()
    return {"message": "User deleted successfully"}

#create address
@app.post("/CreateAddress")
def create_address(address: AddressBase):
    address = Address.model_validate(address)
    with Session(engine) as session:
        session.add(address)
        session.commit()
        session.refresh(address)
    return address

#get address by id
@app.get("/GetAddress/{address_id}")
def get_address(address_id: int):
    with Session(engine) as session:
        address = session.get(Address, address_id)
    return address

#get all addresses
@app.get("/GetAddresses/", response_model=list[Address])
def get_addresses():
    with Session(engine) as session:
        addresses = session.exec(select(Address)).all()
    return addresses

@app.post("/CreateAppointment")
def create_appointment(appointment: AppointmentBase):
    appointment = Appointment.model_validate(appointment)
    with Session(engine) as session:
        session.add(appointment)
        session.commit()
        session.refresh(appointment)
    return appointment

@app.get("/GetAppointment/{appointment_id}")
def get_appointment(appointment_id: int):
    with Session(engine) as session:
        appointment = session.get(Appointment, appointment_id)
    return appointment

@app.get("/GetAppointments/", response_model=list[Appointment])
def get_appointments():
    with Session(engine) as session:
        appointments = session.exec(select(Appointment)).all()
    return appointments