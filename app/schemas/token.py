from pydantic import BaseModel

class Token(BaseModel):
    """
    Token schema for representing access tokens in responses.

    Attributes:
        access_token (str): The token that grants the bearer access to the protected resources.
        token_type (str): The type of token issued. Typically, this is a Bearer token.

    This schema is used to generate the response model for endpoints that authenticate users
    and issue tokens. It adheres to the OAuth 2.0 specification for token responses.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    TokenData schema for capturing essential information about the token.

    Attributes:
        id (int | None): The user ID associated with the token. Defaults to None.
        username (str | None): The username associated with the token. Defaults to None.
        is_guest (bool | None): A flag indicating whether the token belongs to a guest user. Defaults to None.

    This schema can be used to validate token payloads or to carry information related to the
    authentication context of a request. It is especially useful for endpoints that need to
    process or validate tokens without accessing the user's sensitive information directly.
    """
    id: int | None = None
    username: str | None = None
    is_guest: bool | None = None
