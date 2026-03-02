import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict
from .ics import GenericICSAggregator
from ..models import EventNormalized
from ..rate_limiter import RateLimiter, enrich_with_backoff

logger = logging.getLogger(__name__)

_meetup_limiter = RateLimiter(min_interval=0.3)


class MeetupAggregator(GenericICSAggregator):
    """Aggregator for Meetup ICS feeds with location enrichment."""

    def __init__(self, session=None, timeout: int = 30, max_retries: int = 2,
                 skip_enrich: bool = False):
        super().__init__(session, timeout, max_retries)
        self.skip_enrich = skip_enrich

    def extract(
        self, source: str | Dict, feed_name: Optional[str] = None
    ) -> List[EventNormalized]:
        events = super().extract(source, feed_name)

        # Enrich events needing location
        to_enrich = [
            e
            for e in events
            if e.url and "meetup.com" in e.url and len(e.location) < 15
        ]

        if to_enrich and not self.skip_enrich:
            logger.info(f"Found {len(to_enrich)} Meetup events to potentially enrich")
            session = self.session

            def _enrich(event):
                enrich_with_backoff(
                    event,
                    lambda e: e.enrich_location_from_meetup(session),
                    _meetup_limiter,
                )

            with ThreadPoolExecutor(max_workers=5) as pool:
                futures = {pool.submit(_enrich, e): e for e in to_enrich}
                for future in as_completed(futures):
                    exc = future.exception()
                    if exc:
                        event = futures[future]
                        logger.warning(f"Error enriching Meetup event {event.url}: {exc}")

        return events
