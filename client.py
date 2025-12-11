from functools import cached_property

from msgraph.graph_service_client import GraphServiceClient

from onedrive_auth import OneDriveOAuthProvider


class Client:
    def __init__(self, client_id: str, client_secret: str):
        self.oauth_provider = OneDriveOAuthProvider(client_id, client_secret)

    @cached_property
    def client(self):
        credentials = self.oauth_provider.credentials
        scopes = self.oauth_provider.scopes
        return GraphServiceClient(
            credentials=credentials,
            scopes=scopes,
        )
