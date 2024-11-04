import os
from idlelib.pyparse import trans

import dotenv
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()
dotenv.load_dotenv()

# Промежуточная таблица для связи многие ко многим между пользователями и вакансиями
user_vacancy_association = Table(
    'user_vacancy', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('vacancy_id', Integer, ForeignKey('vacancies.id'), primary_key=True)
)

# Промежуточная таблица для связи многие ко многим между вакансиями и городами
vacancy_city_association = Table(
    'vacancy_city_association', Base.metadata,
    Column('vacancy_id', Integer, ForeignKey('vacancies.id'), primary_key=True),
    Column('city_id', Integer, ForeignKey('cities.id'), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    name = Column(String, nullable=True)

    # Связь многие ко многим с вакансиями
    vacancies = relationship('Vacancy', secondary=user_vacancy_association, back_populates='users')


class Vacancy(Base):
    __tablename__ = 'vacancies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    # Связь многие ко многим с пользователями
    users = relationship('User', secondary=user_vacancy_association, back_populates='vacancies')

    # Связь многие ко многим с городами через промежуточную таблицу
    cities = relationship('City', secondary=vacancy_city_association, back_populates='vacancies')


class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    # Связь многие ко многим с вакансиями
    vacancies = relationship('Vacancy', secondary=vacancy_city_association, back_populates='cities')


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, nullable=False)

# Настройка базы данных
engine = create_engine(os.getenv('DATABASE_URL'))
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
