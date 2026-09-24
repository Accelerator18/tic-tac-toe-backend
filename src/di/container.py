from datasource.mapper.game_datasource_mapper import GameDatasourceMapper
from datasource.mapper.user_datasource_mapper import UserDatasourceMapper
from datasource.repository.game_repository import GameRepository
from datasource.repository.user_repository import UserRepository
from domain.service.auth_service import AuthService
from domain.service.game_logic_service import GameLogicService
from domain.service.game_service import GameService
from domain.service.user_service import UserService
from web.auth.user_authenticator import UserAuthenticator
from web.mapper.board_web_mapper import BoardWebMapper
from web.mapper.game_web_mapper import GameWebMapper
from web.mapper.user_web_mapper import UserWebMapper


class Container:

    def __init__(self):
        self.user_datasource_mapper = UserDatasourceMapper()
        self.game_datasource_mapper = GameDatasourceMapper()

        self.user_repository = UserRepository(self.user_datasource_mapper)
        self.game_repository = GameRepository(self.game_datasource_mapper)

        self.game_logic_service = GameLogicService()
        self.user_service = UserService(self.user_repository)
        self.auth_service = AuthService(self.user_service)
        self.game_service = GameService(self.game_repository, self.game_logic_service)

        self.authenticator = UserAuthenticator(self.auth_service)

        self.board_web_mapper = BoardWebMapper()
        self.game_web_mapper = GameWebMapper(self.board_web_mapper)
        self.user_web_mapper = UserWebMapper()
