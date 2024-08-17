import abc
from app.adapter.uow import model, generics


class User(model.RepositoryData):
    name: str
    last_name: str
    username: str
    password: str

    @staticmethod
    def create(name: str, last_name: str, username: str, password: str) -> "User":
        return User(
            name=name,
            last_name=last_name,
            username=username,
            password=password, # TO SHA
        )



class UserCreatorRepository(generics.AlterGeneric):
    ...


class UserFinderRepository(generics.Getter):
    @abc.abstractmethod
    def by_username(self, username: str) -> User | None:
        raise NotImplementedError()