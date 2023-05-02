from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm.session import sessionmaker

PG_DSN = 'postgresql+asyncpg://user:1234@127.0.0.1:5431/netology'
engine = create_async_engine(PG_DSN)

Session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


class SwapiPeople(Base):

    __tablename__ = 'swapi_people'
    id = Column(Integer, primary_key=True)
    birth_year = Column(String)
    eye_color = Column(String)
    films = Column(String)
    gender = Column(String)
    hair_color = Column(String)
    height = Column(String)
    homeworld = Column(String)
    mass = Column(String)
    name = Column(String)
    skin_color = Column(String)
    species = Column(String)
    starships = Column(String)
    vehicles = Column(String)
    url = Column(String)

    def __repr__(self):
        return (
            f'id: {self.id}\n'
            f'birth_year: {self.birth_year}\n'
            f'eye_color: {self.eye_color}\n'
            f'films: {self.films}\n'
            f'gender: {self.gender}\n'
            f'hair_color: {self.hair_color}\n'
            f'height: {self.height}\n'
            f'homeworld: {self.homeworld}\n'
            f'mass: {self.mass}\n'
            f'name: {self.name}\n'
            f'skin_color: {self.skin_color}\n'
            f'species: {self.species}\n'
            f'starships: {self.starships}\n'
            f'vehicles: {self.vehicles}\n'
            f'url: {self.url}\n'
        )
