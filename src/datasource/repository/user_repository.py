from domain.model.user import User
from datasource.database import db
from datasource.mapper.user_datasource_mapper import UserDatasourceMapper
from datasource.model.user_entity import UserEntity


class UserRepository:
    def __init__(self, mapper: UserDatasourceMapper):
        self._mapper = mapper

    def save(self, user: User) -> User:
        entity = self._mapper.to_entity(user)
        db.session.add(entity)
        db.session.commit()
        return user

    def get_by_uuid(self, user_uuid: str) -> User | None:
        entity = db.session.get(UserEntity, user_uuid)
        if entity is None:
            return None
        return self._mapper.to_domain(entity)

    def get_by_login(self, login: str) -> User | None:
        entity = UserEntity.query.filter_by(login=login).first()
        if entity is None:
            return None
        return self._mapper.to_domain(entity)
