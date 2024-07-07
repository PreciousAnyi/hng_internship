from rest_framework_simplejwt.tokens import AccessToken

class CustomAccessToken(AccessToken):
    def get_token(self, user):
        token = super().get_token(user)
        token['userId'] = str(user.userId)  # Ensure userId is converted to string
        return token