import time
from typing import Any, Optional

from azure.identity import AuthorizationCodeCredential, TokenCachePersistenceOptions
from msal import ConfidentialClientApplication


class Credentials:
    def __init__(self, token_dict: dict[str, Any]):
        if "error" in token_dict:
            raise Exception(
                f"Failed to obtain credentials, cause: {token_dict['error_description']}"
            )
        self.access_token = token_dict["access_token"]
        self.refresh_token = token_dict["refresh_token"]
        self.expires_at = token_dict["expires_in"] + int(time.time())
        self.scope: list[str] = (
            str(token_dict.get("scope")).split() if token_dict.get("scope") else []
        )
        self.name: Optional[str] = token_dict.get("name")
        self.preferred_username: Optional[str] = token_dict.get("preferred_username")
        self.oid: Optional[str] = token_dict.get("oid")
        self.tid: Optional[str] = token_dict.get("tid")


class OneDriveOAuthProvider:

    _authority = "https://login.microsoftonline.com/common"
    credentials: Optional[AuthorizationCodeCredential] = None

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def oauth_get_authorization_url(self, redirect_uri: str, scopes: list[str]) -> str:
        app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self._authority,
        )

        url = app.get_authorization_request_url(
            redirect_uri=redirect_uri,
            scopes=scopes,
            response_type="code",
            prompt="consent",
        )

        self.scopes = scopes

        return url

    def oauth_get_credentials(
        self,
        redirect_uri: str,
        code: str,
    ) -> AuthorizationCodeCredential:
        # app = ConfidentialClientApplication(
        #     client_id=self.client_id,
        #     client_credential=self.client_secret,
        #     authority=self._authority,
        # )
        # token_dict = app.acquire_token_by_authorization_code(
        #     code, self.scopes, redirect_uri
        # )

        self.credentials = AuthorizationCodeCredential(
            tenant_id="common",
            client_id=self.client_id,
            authorization_code=code,
            redirect_uri=redirect_uri,
            client_secret=self.client_secret,
            cache_persistence_options=TokenCachePersistenceOptions(),
        )

        return self.credentials

    # async def oauth_refresh_credentials(
    #     self,
    # ) -> ClientSecretCredential:
    #     if not self._credentials:
    #         raise Exception("No credentials to refresh.")

    #     app = ConfidentialClientApplication(
    #         client_id=self.client_id,
    #         client_credential=self.client_secret,
    #         authority=self._authority,
    #     )
    #     self._credentials.get_token(*self._scopes)
    #     token_dict = app.acquire_token_by_refresh_token(
    #         self._credentials.refresh_token, self._scopes
    #     )

    #     self._credentials = Credentials(token_dict)

    #     return self._credentials
