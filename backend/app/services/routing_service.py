from typing import List, Dict, Any
from backend.app.core.config import settings
from backend.app.services.providers import RoutingProvider, GoogleRoutingProvider, MockRoutingProvider

class RoutingService:
    def __init__(self):
        if settings.GOOGLE_MAPS_API_KEY and not settings.USE_MOCK_DATA:
            self.provider: RoutingProvider = GoogleRoutingProvider(settings.GOOGLE_MAPS_API_KEY)
        else:
            self.provider: RoutingProvider = MockRoutingProvider()

    def get_route_alternatives(self, origin: str, destination: str) -> List[Dict[str, Any]]:
        return self.provider.get_routes(origin, destination)
