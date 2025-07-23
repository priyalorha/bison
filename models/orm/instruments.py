from datetime import datetime

from sqlalchemy import String, Integer, Enum, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

import constants
from models.base import Base


class Instruments(Base):
    __tablename__ = 'instruments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    symbol: Mapped[str] = mapped_column(String, nullable=False)
    exchange: Mapped[constants.Exchange] = mapped_column(Enum(constants.Exchange), nullable=False)
    segment: Mapped[constants.Segment] = mapped_column(Enum(constants.Segment), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                 onupdate=datetime.utcnow)

    _table_args__ = (
        UniqueConstraint('symbol', 'exchange', name='uq_symbol_exchange'),
    )



# # engine = create_engine('sqlite:///mydatabase.db')  # or your database URL
# #
# # root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# # db_path = os.path.join(root_dir, 'mydb.db')
# # print(root_dir)
# # print(db_path)
# #
# # # Create engine with absolute path
# # engine = create_engine(f'sqlite:///{db_path}')
# # # 4. Create all tables
# # Base.metadata.create_all(engine)


# import os
#
# from sqlalchemy import create_engine, String, Integer, Enum
# from sqlalchemy.orm import Mapped, mapped_column
#
# import constants
# from models.base import Base
#
#
# class Instruments(Base):
#     __tablename__ = 'instruments'
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String, nullable=False)
#     symbol: Mapped[str] = mapped_column(String, nullable=False)
#     exchange: Mapped[constants.Exchange] = mapped_column(Enum(constants.Exchange), nullable=False)
#     segment: Mapped[constants.Segment] = mapped_column(Enum(constants.Segment), nullable=False)
#
#
# def initialize_database():
#     # Set up database path
#     root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#     db_path = os.path.join(root_dir, 'mydb.db')
#
#     print(f"Database will be created at: {db_path}")
#
#     # Create engine
#     engine = create_engine(f'sqlite:///{db_path}')
#
#     # Create all tables
#     Base.metadata.create_all(engine)
#     print("Tables created successfully!")
#
#     return engine
#
#
# def drop_all_tables(engine):
#     # Drop all tables
#     Base.metadata.drop_all(engine)
#     print("All tables dropped successfully")
#
#
# if __name__ == "__main__":
#     # Initialize database and create tables
#     engine = initialize_database()
#
#     # If you need to drop tables later (be careful!)
#     # drop_all_tables(engine)