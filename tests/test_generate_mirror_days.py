from datetime import date, timedelta

from scripts.generate_mirror_days import daylight, mirror_days, render


def test_calendar_contains_every_day() -> None:
    peak, matches = mirror_days(2026)

    assert peak.month == 6
    assert len(matches) == 365
    assert matches[peak] == peak


def test_mirror_is_opposite_and_close() -> None:
    peak, matches = mirror_days(2026)
    requested = date(2026, 8, 12)
    mirror = matches[requested]

    assert mirror < peak < requested
    assert abs(daylight(mirror)[2] - daylight(requested)[2]) < timedelta(minutes=2)


def test_render_highlights_today() -> None:
    page = render(2026, date(2026, 8, 12))

    assert "# Mirror Days" in page
    assert "2026-08-12 **Today**" in page
    assert page.count("\n| 2026-") == 365
