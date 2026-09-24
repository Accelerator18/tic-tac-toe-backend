from domain.model.user import User


class UserWebMapper:
    def to_json(self, user: User) -> dict:
        return {
            "uuid": user.uuid,
            "login": user.login,
        }
