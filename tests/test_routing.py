import pytest
from backend.app.services.providers import MockRoutingProvider
from backend.app.services.routing_service import RoutingService

def test_mock_routing_provider():
    provider = MockRoutingProvider()
    routes = provider.get_routes("37.7749, -122.4194", "37.7925, -122.4012")
    assert len(routes) == 3
    for r in routes:
        assert "route_id" in r
        assert r["distance_km"] > 0
        assert r["duration_minutes"] > 0
        assert len(r["geometry"]) >= 2

def test_routing_service():
    service = RoutingService()
    routes = service.get_route_alternatives("Financial District, SF", "Mission District, SF")
    assert len(routes) >= 1
