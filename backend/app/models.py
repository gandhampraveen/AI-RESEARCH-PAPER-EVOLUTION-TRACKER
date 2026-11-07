from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="USER")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Paper(Base):
    __tablename__ = "papers"
    __table_args__ = (UniqueConstraint("doi", name="uq_paper_doi"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    abstract: Mapped[str] = mapped_column(Text, default="")
    year: Mapped[int | None] = mapped_column(Integer, index=True)
    venue: Mapped[str] = mapped_column(String(255), default="")
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    citations: Mapped[int] = mapped_column(Integer, default=0)
    url: Mapped[str] = mapped_column(String(1000), default="")
    domain: Mapped[str] = mapped_column(String(120), default="Other", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    authors: Mapped[list["PaperAuthor"]] = relationship(back_populates="paper", cascade="all, delete-orphan")
    topics: Mapped[list["PaperTopic"]] = relationship(back_populates="paper", cascade="all, delete-orphan")


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    affiliation: Mapped[str] = mapped_column(String(255), default="")


class PaperAuthor(Base):
    __tablename__ = "paper_authors"
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    paper: Mapped[Paper] = relationship(back_populates="authors")
    author: Mapped[Author] = relationship()


class Topic(Base):
    __tablename__ = "research_topics"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    papers: Mapped[list["PaperTopic"]] = relationship(back_populates="topic", cascade="all, delete-orphan")


class PaperTopic(Base):
    __tablename__ = "paper_topics"
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("research_topics.id", ondelete="CASCADE"), primary_key=True)
    paper: Mapped[Paper] = relationship(back_populates="topics")
    topic: Mapped[Topic] = relationship(back_populates="papers")


class ChatMessage(Base):
    __tablename__ = "chat_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Keyword(Base):
    __tablename__ = "keywords"
    id: Mapped[int] = mapped_column(primary_key=True)
    term: Mapped[str] = mapped_column(String(120), unique=True, index=True)


class PaperKeyword(Base):
    __tablename__ = "paper_keywords"
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True)


class Citation(Base):
    __tablename__ = "citations"
    citing_paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True)
    cited_paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True)


class ResearchTrend(Base):
    __tablename__ = "research_trends"
    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("research_topics.id", ondelete="CASCADE"), index=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    paper_count: Mapped[int] = mapped_column(Integer, default=0)
    growth_rate: Mapped[float] = mapped_column(Float, default=0)


class JobPosting(Base):
    __tablename__ = "job_postings"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    company: Mapped[str] = mapped_column(String(255), default="Sample employer")
    location: Mapped[str] = mapped_column(String(180), default="Not specified")
    experience: Mapped[str] = mapped_column(String(100), default="Not specified")
    salary: Mapped[str] = mapped_column(String(120), default="")
    skills: Mapped[str] = mapped_column(Text, default="")
    employment_type: Mapped[str] = mapped_column(String(80), default="Full-time")
    posting_date: Mapped[str] = mapped_column(String(20), default="")
    is_sample: Mapped[bool] = mapped_column(Boolean, default=True)


class Skill(Base):
    __tablename__ = "job_skills"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)


class JobPostingSkill(Base):
    __tablename__ = "job_posting_skills"
    job_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("job_skills.id", ondelete="CASCADE"), primary_key=True)
