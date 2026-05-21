# SPDX-FileCopyrightText: 2026 Kaspar Winckler
# SPDX-License-Identifier: GPL-3.0-or-later

import kplugin

from . import api


class Groups(kplugin.Folder):
    def open(self):
        self.set_cache_to_disc(True)
        for group in api.get_groups():
            yield Group(group=group)


class Group(kplugin.Folder, qargs=["group"]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.group = self.query.get("group")

    def get_list_item(self):
        group = self.query.get("group")
        return {
            "label": group,
            "art": {
                "thumb": api.get_favicon_by_group(group),
            },
        }

    def open(self):
        self.set_cache_to_disc(True)
        group = self.query.get("group")
        for radio in api.get_radios_by_group(group):
            yield Radio(id=radio["id"], radio=radio)


class Radio(kplugin.Playable, qargs=["id"]):
    def __init__(self, radio=None, **kwargs):
        super().__init__(**kwargs)
        self.radio = radio or api.get_radio_by_id(self.query.get("id"))

    def get_list_item(self):
        return {
            "label": self.radio["title"],
            "art": {
                "thumb": self.radio["favicon"],
            },
        }

    def open(self):
        return self.get_list_item() | {
            "mimetype": "application/vnd.apple.mpegurl;codec=aac",
            "path": api.get_stream(self.radio),
        }


def run():
    kplugin.kodi_run(Groups)
