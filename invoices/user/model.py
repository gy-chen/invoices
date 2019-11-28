import collections

User = collections.namedtuple("User", "sub email")


class UserModel:
    def register_user(self, user):
        return NotImplemented

    def get_user(self, sub):
        return NotImplemented
