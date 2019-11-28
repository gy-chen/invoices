class UserModel:
    def register_user(self, user_sub, email):
        """Register user

        Args:
            user_sub (str)
            email (str)

        Returns:
            registered user
        """
        return NotImplemented

    def load_user(self, user_sub):
        """Load user data

        Args:
            user_sub (str)

        Returns:
            User or None
        """
        return NotImplemented
