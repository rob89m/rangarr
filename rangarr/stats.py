"""Thread-safe runtime statistics for the Homepage API widget."""

import datetime
import threading
from dataclasses import dataclass
from dataclasses import field


@dataclass
class RangarrStats:
    """Mutable runtime state updated by the main loop and read by the API server."""

    status: str = 'starting'
    instances: int = 0
    instance_names: list[str] = field(default_factory=list)
    searches_today: int = 0
    last_cycle_at: str = ''
    next_missing_in: str = ''
    next_upgrade_in: str = ''
    dry_run: bool = False
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def update(self, **kwargs: object) -> None:
        """Update one or more fields atomically."""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self, key) and not key.startswith('_'):
                    setattr(self, key, value)

    def increment_searches(self, count: int) -> None:
        """Increment the today search counter."""
        with self._lock:
            self.searches_today += count

    def reset_daily_searches(self) -> None:
        """Reset search counter (call at midnight or on startup)."""
        with self._lock:
            self.searches_today = 0
            self._reset_date = datetime.date.today()

    def snapshot(self) -> dict:
        """Return a copy of all public fields safe to serialise."""
        with self._lock:
            return {
                'status': self.status,
                'instances': self.instances,
                'instance_names': list(self.instance_names),
                'searches_today': self.searches_today,
                'last_cycle_at': self.last_cycle_at,
                'next_missing_in': self.next_missing_in,
                'next_upgrade_in': self.next_upgrade_in,
                'dry_run': self.dry_run,
            }


# Module-level singleton shared between the main loop and the API server.
stats = RangarrStats()
