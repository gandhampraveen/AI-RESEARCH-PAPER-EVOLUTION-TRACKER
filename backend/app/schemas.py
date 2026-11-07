from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class PaperIn(BaseModel):
    title: str = Field(min_length=3, max_length=500)
    abstract: str = ""
    year: int | None = Field(default=None, ge=1800, le=2100)
    venue: str = ""
    doi: str | None = None
    citations: int = Field(default=0, ge=0)
    url: str = ""
    domain: str = "Other"
    authors: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)


class PaperOut(BaseModel):
    id: int
    title: str
    abstract: str
    year: int | None
    venue: str
    doi: str | None
    citations: int
    url: str
    domain: str
    model_config = ConfigDict(from_attributes=True)


class ChatIn(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
