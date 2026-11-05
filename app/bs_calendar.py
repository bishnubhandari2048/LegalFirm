"""Bikram Sambat (BS) <-> Gregorian (AD) Date Conversion Utility for Nepal Legal Practice."""

from datetime import date, datetime, timedelta

# Days in each BS month (Baisakh to Chaitra) for years 2070 BS to 2090 BS
BS_CALENDAR_DATA: dict[int, list[int]] = {
    2070: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    2071: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2072: [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2073: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2074: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2075: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2076: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2077: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2078: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2079: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2080: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2081: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2082: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2083: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2084: [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
    2085: [31, 32, 31, 32, 30, 31, 30, 30, 29, 30, 30, 30],
    2086: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2087: [31, 31, 32, 31, 31, 31, 30, 30, 29, 30, 30, 30],
    2088: [30, 31, 32, 32, 30, 31, 30, 30, 29, 30, 30, 30],
    2089: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2090: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
}

# Reference anchor: 2070-01-01 BS == 2013-04-14 AD
ANCHOR_AD = date(2013, 4, 14)
ANCHOR_BS_YEAR = 2070

BS_MONTH_NAMES_NP = [
    "बैशाख", "जेठ", "असार", "साउन", "भदौ", "असोज",
    "कार्तिक", "मंसिर", "पुष", "माघ", "फागुन", "चैत"
]

BS_MONTH_NAMES_EN = [
    "Baisakh", "Jestha", "Ashadh", "Shrawan", "Bhadra", "Ashwin",
    "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra"
]


def ad_to_bs(ad_date_val: date | str | None) -> str:
    """Convert an AD date (YYYY-MM-DD or date object) to BS string YYYY-MM-DD."""
    if not ad_date_val:
        return ""
    if isinstance(ad_date_val, str):
        try:
            ad_date_val = datetime.strptime(ad_date_val[:10], "%Y-%m-%d").date()
        except ValueError:
            return ""

    delta_days = (ad_date_val - ANCHOR_AD).days
    if delta_days < 0:
        # Approximate for dates before 2070 BS (add ~56 years 8 months 17 days)
        approx_year = ad_date_val.year + 56
        approx_month = ad_date_val.month + 8
        approx_day = ad_date_val.day + 16
        if approx_day > 30:
            approx_day -= 30
            approx_month += 1
        if approx_month > 12:
            approx_month -= 12
            approx_year += 1
        return f"{approx_year:04d}-{approx_month:02d}-{approx_day:02d}"

    bs_year = ANCHOR_BS_YEAR
    bs_month = 1
    bs_day = 1

    remaining = delta_days
    while remaining > 0:
        year_months = BS_CALENDAR_DATA.get(bs_year, [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30])
        days_in_month = year_months[bs_month - 1]
        days_left_in_month = days_in_month - bs_day
        if remaining <= days_left_in_month:
            bs_day += remaining
            remaining = 0
        else:
            remaining -= (days_left_in_month + 1)
            bs_day = 1
            bs_month += 1
            if bs_month > 12:
                bs_month = 1
                bs_year += 1

    return f"{bs_year:04d}-{bs_month:02d}-{bs_day:02d}"


def bs_to_ad(bs_date_str: str | None) -> date | None:
    """Convert a BS date string (YYYY-MM-DD) to an AD date object."""
    if not bs_date_str:
        return None
    try:
        parts = bs_date_str.strip().replace("/", "-").split("-")
        if len(parts) != 3:
            return None
        target_year, target_month, target_day = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return None

    if target_year < ANCHOR_BS_YEAR or target_year > 2090:
        # Approximate fallback
        try:
            approx_ad = date(target_year - 57, target_month, min(target_day, 28)) + timedelta(days=105)
            return approx_ad
        except Exception:
            return None

    total_days = 0
    for y in range(ANCHOR_BS_YEAR, target_year):
        total_days += sum(BS_CALENDAR_DATA.get(y, [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]))

    year_months = BS_CALENDAR_DATA.get(target_year, [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30])
    for m in range(1, target_month):
        if 1 <= m <= 12:
            total_days += year_months[m - 1]

    total_days += (target_day - 1)
    return ANCHOR_AD + timedelta(days=total_days)


def format_bs_human(bs_date_str: str | None) -> str:
    """Format YYYY-MM-DD BS date into Nepali readable format e.g. २०८३ कार्तिक १८."""
    if not bs_date_str:
        return "-"
    try:
        parts = bs_date_str.strip().split("-")
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        month_name = BS_MONTH_NAMES_NP[m - 1] if 1 <= m <= 12 else str(m)
        return f"{y} {month_name} {d}"
    except Exception:
        return bs_date_str


def today_bs() -> str:
    return ad_to_bs(date.today())
