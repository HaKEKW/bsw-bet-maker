from adapters.connection_engines.sql_alchemy.models.user import UserModel
from domain.entities.user import User


class SQLAlchemyUserRepositoryMapper:
    @staticmethod
    def to_entity(user_orm: UserModel) -> User:
        return User(
            id=user_orm.id,
            name=user_orm.name,
            email=user_orm.email,
            role=user_orm.role,
        )

    @staticmethod
    def to_model(user_orm: UserModel, *, name: str, email: str, password_hash: str, role) -> None:
        user_orm.name = name
        user_orm.email = email
        user_orm.password_hash = password_hash
        user_orm.role = role
