import os
from typing import Type, List

import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from tools.database.model.database_models import Base, User, Vacancy, City, Admin

dotenv.load_dotenv()


class LocalDatabase:

    def __init__(self):
        self.__engine__ = create_engine(os.getenv('DATABASE_URL'))
        self.__Session__ = sessionmaker(self.__engine__)
        self.__session__ = self.__Session__()

        Base.metadata.create_all(self.__engine__)

    async def get_user_by_id(self, id: int) -> Type[User]:
        return self.__session__.query(User).filter_by(telegram_id=id).first()

    async def add_new_user(self, user: User):
        self.__session__.add(user)
        self.__session__.commit()

    async def update_name_user(self, user_id: int, name: str):
        user = await self.get_user_by_id(user_id)
        if user:
            user.name = name
            self.__session__.commit()

    async def add_vacancy_to_user_at_userid(self, user_id: int, vacancy: Vacancy):
        user = await self.get_user_by_id(user_id)
        if user:
            user.vacancies.append(vacancy)
            self.__session__.add(user)
            self.__session__.commit()

    async def add_vacancy(self, vacancy: Vacancy):
        self.__session__.add(vacancy)
        self.__session__.commit()

    async def get_all_vacancies(self) -> list[Type[Vacancy]]:
        return self.__session__.query(Vacancy).all()

    async def add_city_to_vacancy(self, vacancy_id: int, city_name: str):
        try:
            vacancy = self.__session__.query(Vacancy).filter_by(id=vacancy_id).first()
            if not vacancy:
                return None

            city = self.__session__.query(City).filter_by(name=city_name).first()
            if not city:
                city = City(name=city_name)
                self.__session__.add(city)
                self.__session__.commit()

            if city not in vacancy.cities:
                vacancy.cities.append(city)
                self.__session__.add(vacancy)
                self.__session__.commit()
        except Exception as e:
            self.__session__.rollback()  # Rollback in case of error
            print(f"Error: {e}")
        finally:
            self.__session__.close()  # Close the session properly

    async def get_vacancy_by_city(self, city_name: str) -> list[Type[Vacancy]]:
        city = self.__session__.query(City).filter_by(name=city_name).first()
        if city:
            return city.vacancies
        return []

    async def add_city(self, city_name: str):
        city = City(name=city_name)
        self.__session__.add(city)
        self.__session__.commit()

    async def edit_city_by_id(self, city_id: int, new_name: str):
        city = self.__session__.query(City).filter_by(id=city_id).first()
        if city:
            city.name = new_name
            self.__session__.commit()

    async def get_all_cities(self) -> list[Type[City]]:
        return self.__session__.query(City).all()

    async def get_city_by_id(self, city_id: int) -> Type[City]:
        return self.__session__.query(City).filter_by(id=city_id).first()

    async def delete_city_by_id(self, city_id: int):
        city = self.__session__.query(City).filter_by(id=city_id).first()
        if city:
            self.__session__.delete(city)
            self.__session__.commit()

    async def delete_vacancy_by_id(self, vacancy_id: int):
        vacancy = self.__session__.query(Vacancy).filter_by(id=vacancy_id).first()
        if vacancy:
            self.__session__.delete(vacancy)
            self.__session__.commit()

    async def get_vacancy_by_id(self, vacancy_id: int):
        vacancy = self.__session__.query(Vacancy).filter_by(id=vacancy_id).first()
        if vacancy:
            return vacancy


    async def get_admins_list(self) -> list[Type[Admin]]:
        return self.__session__.query(Admin).all()

    async def add_new_admin(self, admin: Admin):
        self.__session__.add(admin)
        self.__session__.commit()

    async def delete_admin_by_id(self, admin_id):
        admin = self.__session__.query(Admin).filter_by(id=admin_id).first()
        if admin:
            self.__session__.delete(admin)
            self.__session__.commit()
