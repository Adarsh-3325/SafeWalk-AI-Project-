from typing import List, Dict, Any
from backend.app.core.config import settings
from backend.app.services.providers import RoutingProvider, GoogleRoutingProvider, MockRoutingProvider

class RoutingService:
    def __init__(self):
        api_key = settings.clean_google_maps_api_key
        if api_key and not settings.USE_MOCK_DATA:
            self.provider: RoutingProvider = GoogleRoutingProvider(api_key)
        else:
            self.provider: RoutingProvider = MockRoutingProvider()

    def get_route_alternatives(self, origin: str, destination: str) -> List[Dict[str, Any]]:
        return self.provider.get_routes(origin, destination)
