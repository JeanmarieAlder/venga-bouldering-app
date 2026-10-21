from flask_login import UserMixin
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)


class User(UserMixin):
    def __init__(
        self,
        id,
        username,
        display_name,
        role,
        password_hash,
    ):
        self.id = id
        self.username = username
        self.display_name = display_name
        self.role = role
        self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    @property
    def is_admin(self):
        return self.role == "admin"
    
    @property
    def is_setter(self):
        return self.role == "setter"

    @property
    def can_set_boulders(self):
        return self.role in ("setter", "admin")

    @property
    def is_climber(self):
        return self.role in ("climber", "setter", "admin")

    def to_dict(self):
        # Never expose the password hash to API clients.
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "role": self.role,
        }
