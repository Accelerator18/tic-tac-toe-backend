from domain.model.board import Board
from domain.model.game import Game, GameMode, GameStatus
from datasource.model.game_entity import GameEntity


class GameDatasourceMapper:
    def to_domain(self, entity: GameEntity) -> Game:
        return Game(
            uuid=entity.uuid,
            board=Board(entity.board),
            mode=GameMode(entity.mode),
            status=GameStatus(entity.status),
            player_x_uuid=entity.player_x_uuid,
            player_o_uuid=entity.player_o_uuid,
            current_turn_uuid=entity.current_turn_uuid,
            winner_uuid=entity.winner_uuid,
        )

    def to_entity(self, game: Game) -> GameEntity:
        return GameEntity(
            uuid=game.uuid,
            board=game.board.cells,
            mode=game.mode.value,
            status=game.status.value,
            player_x_uuid=game.player_x_uuid,
            player_o_uuid=game.player_o_uuid,
            current_turn_uuid=game.current_turn_uuid,
            winner_uuid=game.winner_uuid,
        )

    def update_entity(self, entity: GameEntity, game: Game) -> GameEntity:
        entity.board = game.board.cells
        entity.mode = game.mode.value
        entity.status = game.status.value
        entity.player_x_uuid = game.player_x_uuid
        entity.player_o_uuid = game.player_o_uuid
        entity.current_turn_uuid = game.current_turn_uuid
        entity.winner_uuid = game.winner_uuid
        return entity
