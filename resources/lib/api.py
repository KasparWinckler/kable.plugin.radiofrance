# SPDX-FileCopyrightText: 2026 Kaspar Winckler
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os.path


MUSIC_ID_MARKERS = {"100", "CHANSON", "FIP", "MOUV", "MUSIQUE_"}

GROUP_RADIO_FRANCE = "Radio France"
GROUP_LES_MUSIQUES = "Les musiques de Radio France"


def _get_brands():
    brands = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "brands.json",
    )
    try:
        with open(brands) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _get_favicon(brand_id=None):
    brand_id = (brand_id or "radiofrance").lower()
    return f"https://www.radiofrance.fr/external/favicons/{brand_id}/favicon.png"


def _get_groups(brand_title, radio):
    groups = [GROUP_RADIO_FRANCE, brand_title]

    radio_id = radio.get("id") or ""
    if any(marker in radio_id for marker in MUSIC_ID_MARKERS):
        groups.append(GROUP_LES_MUSIQUES)

    return groups


def _get_title(brand_title, radio):
    radio_title = radio.get("title") or ""

    if not radio_title.lower().startswith(brand_title.lower()):
        return f"{brand_title} {radio_title}"
    return radio_title


def _build_catalogs():
    brands = {}
    radios = []

    for brand in _get_brands():
        brand_id = brand.get("id") or ""
        favicon = _get_favicon(brand_id)

        brand_title = brand.get("title") or ""
        brands[brand_title] = favicon

        for radio in (
            [brand] + (brand.get("localRadios") or []) + (brand.get("webRadios") or [])
        ):
            if not radio.get("liveStream"):
                continue

            radios.append(
                {
                    "id": radio.get("id", ""),
                    "favicon": favicon,
                    "groups": _get_groups(brand_title, radio),
                    "stream": radio["liveStream"],
                    "title": _get_title(brand_title, radio),
                }
            )

    return brands, sorted(radios, key=lambda x: x["title"].lower())


BRANDS, RADIOS = _build_catalogs()


def get_favicon_by_group(group):
    return BRANDS.get(group) or _get_favicon(None)


def get_groups():
    groups = {group: None for radio in RADIOS for group in radio["groups"]}
    return sorted(list(groups.keys()), key=lambda s: s.lower())


def get_radio_by_id(radio_id):
    for radio in RADIOS:
        if radio_id == radio["id"]:
            return radio
    return None


def get_radios_by_group(group):
    return [radio for radio in RADIOS if group in radio["groups"]]


def get_stream(radio):
    path = radio["stream"].split("/")[-1]
    slug, _ = path.split("-")

    return f"https://stream.radiofrance.fr/{slug}/{slug}.m3u8?id=radiofrance"


def search_radios_by_title(search_term):
    target = search_term.lower().strip()
    return [radio for radio in RADIOS if target in radio.get["title"].lower()]
