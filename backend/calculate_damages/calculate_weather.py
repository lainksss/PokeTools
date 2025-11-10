from typing import Dict, Optional, Tuple


def compute_weather_mult(field: Dict, mv_type: Optional[str], move: Dict) -> Tuple[float, Dict]:
    """Return (multiplier, effects) for weather.

    effects may include flags like 'prevent_freeze', 'sandstorm_spdef_boost', 'hail_end_of_turn_damage',
    and 'snow_def_boost'.
    """
    weather = field.get("weather")
    if field.get("cloud_nine") or field.get("air_lock") or any(p.get("ability") in ("cloud-nine", "air-lock") for p in field.get("pokemon", [])):
        weather = None
    effects = {}
    weather_mult = 1.0
    if not weather:
        return weather_mult, effects

    w = str(weather).lower()
    # Harsh sunlight (strong sun)
    if w in ("harsh-sunlight", "harsh_sunlight", "harsh sun", "strong-sun", "strong_sun", "sunny-day-strong", "sunny-day"):
        # boosts Fire, weakens Water, prevents freeze
        if mv_type == "fire":
            weather_mult = 1.5
        if mv_type == "water":
            weather_mult = 0.5
        effects["prevent_freeze"] = True
        effects["name"] = "harsh-sunlight"
        return weather_mult, effects

    if w in ("sun", "sunny", "sunny-day", "sunny day"):
        if mv_type == "fire" or move.get("name") == "hydro-steam":
            weather_mult = 1.5
        if mv_type == "water" and move.get("name") != "hydro-steam":
            weather_mult = 0.5
        effects["name"] = "sun"
        return weather_mult, effects

    if w in ("rain", "rainy"):
        if mv_type == "water":
            weather_mult = 1.5
        if mv_type == "fire":
            weather_mult = 0.5
        effects["name"] = "rain"
        return weather_mult, effects

    if w in ("sandstorm", "sand-storm"):
        # sandstorm does not change move power except special defense buff for Rock types
        effects["name"] = "sandstorm"
        effects["sandstorm_spdef_boost"] = True
        return weather_mult, effects

    if w in ("hail",):
        # hail damages non-ice at end of turn; in Gen9 replaced by snow
        effects["name"] = "hail"
        effects["hail_end_of_turn_damage"] = True
        return weather_mult, effects

    if w in ("snow",):
        # snow increases Defense of Ice types by 50%
        effects["name"] = "snow"
        effects["snow_def_boost"] = True
        return weather_mult, effects

    return weather_mult, effects
