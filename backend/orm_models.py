"""
SQLAlchemy ORM models — database tables for RouteRanker.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.db import Base


class Route(Base):
    __tablename__ = "routes"

    route_id = Column(String, primary_key=True, index=True)
    route_short_name = Column(String, nullable=True)
    route_long_name = Column(String, nullable=True)
    trip_count = Column(Integer, nullable=True)
    unique_stops = Column(Integer, nullable=True)
    avg_duration_sec = Column(Float, nullable=True)
    peak_ratio = Column(Float, nullable=True)
    route_length_km = Column(Float, nullable=True)

    predictions = relationship("Prediction", back_populates="route")
    recommendations = relationship("Recommendation", back_populates="route")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(String, ForeignKey("routes.route_id"), index=True)
    performance = Column(String, index=True)
    cluster = Column(Integer)
    model_version = Column(String, default="xgb_v1")
    predicted_at = Column(DateTime, default=datetime.utcnow)

    route = relationship("Route", back_populates="predictions")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(String, ForeignKey("routes.route_id"), index=True)
    suggestion = Column(Text)
    priority = Column(Integer, default=1)

    route = relationship("Route", back_populates="recommendations")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="planner")
    created_at = Column(DateTime, default=datetime.utcnow)