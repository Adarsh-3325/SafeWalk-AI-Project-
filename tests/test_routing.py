import pytest
from backend.app.services.providers import MockRoutingProvider
from backend.app.services.routing_service import RoutingService

def test_mock_routing_provider():
    provider = MockRoutingProvider()
    routes = provider.get_routes("Connaught Place, New Delhi", "India Gate, New Delhi")
    assert len(routes) >= 1
    for r in routes:
        assert "route_id" in r
        assert r["distance_km"] > 0
        assert r["duration_minutes"] > 0
        assert len(r["geometry"]) >= 2
        assert "steps" in r

def test_routing_service():
    service = RoutingService()
    routes = service.get_route_alternatives("Hauz Khas Village, Delhi", "Saket Metro Station, Delhi")
    assert len(routes) >= 1
    assert routes[0]["origin_lat"] > 0
    assert routes[0]["dest_lng"] > 0
