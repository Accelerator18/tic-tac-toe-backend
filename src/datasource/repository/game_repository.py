from domain.model.game import Game, GameStatus
from datasource.database import db
from datasource.mapper.game_datasource_mapper import GameDatasourceMapper
from datasource.model.game_entity import GameEntity


class GameRepository:
    def __init__(self, mapper: GameDatasourceMapper):
        self._mapper = mapper

    def save(self, game: Game) -> Game:
        entity = db.session.get(GameEntity, game.uuid)
        if entity is None:
            entity = self._mapper.to_entity(game)
            db.session.add(entity)
        else:
            self._mapper.update_entity(entity, game)
        db.session.commit()
        return game

    def get_by_uuid(self, game_uuid: str) -> Game | None:
        entity = db.session.get(GameEntity, game_uuid)
        if entity is None:
            return None
        return self._mapper.to_domain(entity)

    def get_available_games(self, current_user_uuid: str) -> list[Game]:
        entities = (
            GameEntity.query
            .filter(GameEntity.status == GameStatus.WAITING_PLAYERS.value)
            .filter(GameEntity.player_x_uuid != current_user_uuid)
            .order_by(GameEntity.created_at.desc())
            .all()
        )
        return [self._mapper.to_domain(entity) for entity in entities]

    def get_games_for_user(self, user_uuid: str) -> list[Game]:
        entities = (
            GameEntity.query
            .filter((GameEntity.player_x_uuid == user_uuid) | (GameEntity.player_o_uuid == user_uuid))
            .order_by(GameEntity.updated_at.desc())
            .all()
        )
        return [self._mapper.to_domain(entity) for entity in entities]
