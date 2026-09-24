from domain.model.user import User
from datasource.model.user_entity import UserEntity


class UserDatasourceMapper:
    def to_domain(self, entity: UserEntity) -> User:
        return User(uuid=entity.uuid, login=entity.login, password_hash=entity.password_hash)

    def to_entity(self, user: User) -> UserEntity:
        return UserEntity(uuid=user.uuid, login=user.login, password_hash=user.password_hash)
