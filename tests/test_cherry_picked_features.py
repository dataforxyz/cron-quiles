"""
Tests para las funcionalidades cherry-picked del PR #1 de dataforxyz:
- Modo --fast (skip_enrich, fast_mode)
- geocode_location retorna tupla (éxito, usó_api)
- Enrutamiento de agregadores (_select_aggregator_key)
- Extracción thread-safe (sesión por hilo)
- Rate limiter y backoff exponencial
"""

import sys
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from dateutil import tz
from icalendar import Event

# Agregar src al path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from cronquiles.ics_aggregator import ICSAggregator
from cronquiles.models import EventNormalized
from cronquiles.aggregators.luma import LumaAggregator
from cronquiles.aggregators.meetup import MeetupAggregator
from cronquiles.rate_limiter import RateLimiter, enrich_with_backoff


class TestFastMode(unittest.TestCase):
    """Tests para el modo --fast del pipeline."""

    def test_ics_aggregator_fast_mode_default_off(self):
        """fast_mode está desactivado por defecto."""
        agg = ICSAggregator()
        self.assertFalse(agg.fast_mode)

    def test_ics_aggregator_fast_mode_on(self):
        """fast_mode se propaga a los sub-agregadores."""
        agg = ICSAggregator(fast_mode=True)
        self.assertTrue(agg.fast_mode)
        self.assertTrue(agg.aggregators["luma"].skip_enrich)
        self.assertTrue(agg.aggregators["meetup"].skip_enrich)

    def test_ics_aggregator_fast_mode_off_no_skip(self):
        """Sin fast_mode, los sub-agregadores no saltan enriquecimiento."""
        agg = ICSAggregator(fast_mode=False)
        self.assertFalse(agg.aggregators["luma"].skip_enrich)
        self.assertFalse(agg.aggregators["meetup"].skip_enrich)

    def test_luma_skip_enrich_param(self):
        """LumaAggregator acepta skip_enrich."""
        agg = LumaAggregator(skip_enrich=True)
        self.assertTrue(agg.skip_enrich)

        agg2 = LumaAggregator(skip_enrich=False)
        self.assertFalse(agg2.skip_enrich)

    def test_meetup_skip_enrich_param(self):
        """MeetupAggregator acepta skip_enrich."""
        agg = MeetupAggregator(skip_enrich=True)
        self.assertTrue(agg.skip_enrich)

        agg2 = MeetupAggregator()
        self.assertFalse(agg2.skip_enrich)


class TestGeocodeLocationTuple(unittest.TestCase):
    """Tests para el retorno de tupla de geocode_location."""

    def _make_event(self, location="", is_online=False):
        ev = Event()
        ev.add("summary", "Test Event")
        ev.add("dtstart", datetime(2024, 3, 15, 18, 0, 0, tzinfo=tz.UTC))
        if location:
            ev.add("location", location)
        norm = EventNormalized(ev, "https://example.com/feed.ics")
        norm.location = location
        if is_online:
            norm.location = "Online"
        return norm

    def test_returns_tuple(self):
        """geocode_location retorna una tupla de 2 elementos."""
        event = self._make_event("Ciudad de México, México")
        result = event.geocode_location(cache={})
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_short_location_returns_false_false(self):
        """Ubicación demasiado corta retorna (False, False)."""
        event = self._make_event("AB")
        result = event.geocode_location()
        self.assertEqual(result, (False, False))

    def test_empty_location_returns_false_false(self):
        """Ubicación vacía retorna (False, False)."""
        event = self._make_event("")
        result = event.geocode_location()
        self.assertEqual(result, (False, False))

    def test_online_event_returns_false_false(self):
        """Evento online retorna (False, False) sin intentar geocodear."""
        event = self._make_event(is_online=True)
        result = event.geocode_location()
        self.assertEqual(result, (False, False))

    def test_cache_hit_does_not_use_api(self):
        """Un cache hit retorna used_api=False."""
        event = self._make_event("Guadalajara, Jalisco, México")
        cache = {
            "Guadalajara, Jalisco, México": {
                "address_components": [
                    {"long_name": "Guadalajara", "short_name": "Guadalajara",
                     "types": ["locality", "political"]},
                    {"long_name": "Jalisco", "short_name": "Jal.",
                     "types": ["administrative_area_level_1", "political"]},
                    {"long_name": "México", "short_name": "MX",
                     "types": ["country", "political"]},
                ],
                "formatted_address": "Guadalajara, Jal., México",
                "geometry": {"location": {"lat": 20.67, "lng": -103.35}},
            }
        }
        success, used_api = event.geocode_location(cache=cache)
        self.assertTrue(success)
        self.assertFalse(used_api)

    def test_cache_empty_entry_returns_false(self):
        """Un cache con entrada vacía retorna (False, False) sin usar API."""
        event = self._make_event("Lugar inexistente, México")
        cache = {"Lugar inexistente, México": {}}
        success, used_api = event.geocode_location(cache=cache)
        # Vacío en cache = no se encontró ubicación, pero no usó API
        self.assertFalse(used_api)


class TestAggregatorKeyRouting(unittest.TestCase):
    """Tests para _select_aggregator_key."""

    def setUp(self):
        self.agg = ICSAggregator()

    def test_eventbrite_organizer_url(self):
        url = "https://www.eventbrite.com.mx/o/epam-27283356907"
        self.assertEqual(self.agg._select_aggregator_key(url), "eventbrite")

    def test_eventbrite_event_url(self):
        url = "https://www.eventbrite.com/e/mujeres-en-tech-tickets-123"
        self.assertEqual(self.agg._select_aggregator_key(url), "eventbrite")

    def test_luma_vanity_url(self):
        url = "https://luma.com/ai-cdmx"
        self.assertEqual(self.agg._select_aggregator_key(url), "luma")

    def test_luma_short_url(self):
        url = "https://lu.ma/some-event"
        self.assertEqual(self.agg._select_aggregator_key(url), "luma")

    def test_meetup_url(self):
        url = "https://www.meetup.com/python-mexico/events/ical"
        self.assertEqual(self.agg._select_aggregator_key(url), "meetup")

    def test_hievents_url(self):
        url = "https://reuniones.pythonistas-gdl.org/events/1/pythonistas-gdl"
        self.assertEqual(self.agg._select_aggregator_key(url), "hievents")

    def test_hievents_hi_events_domain(self):
        url = "https://hi.events/some-event"
        self.assertEqual(self.agg._select_aggregator_key(url), "hievents")

    def test_generic_ics_url(self):
        url = "https://calendar.google.com/calendar/ical/test/basic.ics"
        self.assertEqual(self.agg._select_aggregator_key(url), "ics")

    def test_luma_api_url(self):
        url = "https://api2.luma.com/ics/get?entity=calendar&id=cal-xxx"
        self.assertEqual(self.agg._select_aggregator_key(url), "luma")


class TestRateLimiter(unittest.TestCase):
    """Tests para el rate limiter con backoff exponencial."""

    def test_rate_limiter_enforces_interval(self):
        """RateLimiter espera el intervalo mínimo entre llamadas."""
        limiter = RateLimiter(min_interval=0.1)
        start = time.monotonic()
        limiter.acquire()
        limiter.acquire()
        elapsed = time.monotonic() - start
        # Segunda llamada debe haber esperado al menos 0.1s
        self.assertGreaterEqual(elapsed, 0.09)

    def test_enrich_with_backoff_success(self):
        """enrich_with_backoff ejecuta la función con éxito."""
        limiter = RateLimiter(min_interval=0.01)
        event = MagicMock()
        enrich_fn = MagicMock()

        enrich_with_backoff(event, enrich_fn, limiter)
        enrich_fn.assert_called_once_with(event)

    def test_enrich_with_backoff_retries(self):
        """enrich_with_backoff reintenta en caso de error."""
        limiter = RateLimiter(min_interval=0.01)
        event = MagicMock()
        # Falla 2 veces, éxito al 3er intento
        enrich_fn = MagicMock(side_effect=[Exception("error"), Exception("error"), None])

        enrich_with_backoff(event, enrich_fn, limiter, max_retries=3)
        self.assertEqual(enrich_fn.call_count, 3)

    def test_enrich_with_backoff_exhausted(self):
        """enrich_with_backoff no lanza excepción después de agotar reintentos."""
        limiter = RateLimiter(min_interval=0.01)
        event = MagicMock()
        enrich_fn = MagicMock(side_effect=Exception("error"))

        # No debe lanzar excepción, solo loguear warning
        enrich_with_backoff(event, enrich_fn, limiter, max_retries=2)
        self.assertEqual(enrich_fn.call_count, 2)


class TestThreadSafeExtraction(unittest.TestCase):
    """Tests para la extracción thread-safe de feeds."""

    def test_extract_single_feed_creates_own_session(self):
        """_extract_single_feed crea su propia sesión HTTP (no reutiliza self.session)."""
        agg = ICSAggregator()
        feed = {"url": "https://www.meetup.com/test/events/ical", "name": "Test"}

        with patch("cronquiles.ics_aggregator.requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session
            # MeetupAggregator.extract llamará a super().extract que hará fetch
            # Pero el punto es verificar que se crea una nueva sesión
            with patch.object(MeetupAggregator, "extract", return_value=[]):
                agg._extract_single_feed(feed)
            mock_session_cls.assert_called_once()

    def test_extract_single_feed_empty_url(self):
        """_extract_single_feed retorna lista vacía para URL vacía."""
        agg = ICSAggregator()
        result = agg._extract_single_feed({"url": "", "name": "Empty"})
        self.assertEqual(result, [])

    def test_extract_single_feed_string_feed(self):
        """_extract_single_feed acepta un string como feed."""
        agg = ICSAggregator()
        with patch("cronquiles.ics_aggregator.requests.Session"):
            with patch.object(GenericICSAggregator, "extract", return_value=[]):
                result = agg._extract_single_feed(
                    "https://calendar.example.com/feed.ics"
                )
        self.assertEqual(result, [])


# Importar aquí para no romper si falta el módulo
from cronquiles.aggregators.ics import GenericICSAggregator  # noqa: E402


if __name__ == "__main__":
    unittest.main()
