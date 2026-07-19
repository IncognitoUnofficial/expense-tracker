from datetime import datetime, timezone

from flask_login import UserMixin

from app.extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=_utcnow, nullable=False)

    categories = db.relationship(
        "Category", back_populates="user", cascade="all, delete-orphan"
    )
    expenses = db.relationship(
        "Expense", back_populates="user", cascade="all, delete-orphan"
    )


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = (db.UniqueConstraint("user_id", "name", name="uq_user_category_name"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=_utcnow, nullable=False)

    user = db.relationship("User", back_populates="categories")
    expenses = db.relationship("Expense", back_populates="category")

    @property
    def expense_count(self):
        return len(self.expenses)


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255))
    expense_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=_utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    user = db.relationship("User", back_populates="expenses")
    category = db.relationship("Category", back_populates="expenses")
