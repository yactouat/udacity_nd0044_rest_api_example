from sqlalchemy import Column, String, Integer, ForeignKey
from flask_sqlalchemy import SQLAlchemy

database_path = "postgresql://usr:pwd@pgsql:5432/rest"

db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""


def setup_db(app, database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


"""
Item

"""


class Item(db.Model):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    item = Column(String, nullable=False, unique=True)
    category = Column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False
    )
    categ = db.relationship("Category", back_populates="items")

    def checkItemUniqueness(self):
        check = Item.query.filter(
            Item.item == self.item
        ).one_or_none()
        return check is None

    def format(self):
        return {
            'id': self.id,
            'item': self.item,
            'category': self.categ.type,
        }


"""
Category

"""


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False, unique=True)
    items = db.relationship(
        "Item",
        back_populates="categ",
        lazy=True,
        collection_class=list,
        cascade="all, delete-orphan"
    )

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }
