"""Registry for applications and profiles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from config.models import AppDefinition, Config, Profile


@dataclass
class AppRegistry:
    apps: Dict[str, AppDefinition]
    profiles: Dict[str, Profile]

    @classmethod
    def from_config(cls, config: Config) -> "AppRegistry":
        return cls(apps=config.apps, profiles=config.profiles)

    def get_app(self, app_id: str) -> AppDefinition | None:
        return self.apps.get(app_id)

    def get_profile(self, profile_id: str) -> Profile | None:
        return self.profiles.get(profile_id)

    def list_apps_for_profile(self, profile_id: str) -> List[AppDefinition]:
        profile = self.get_profile(profile_id)
        if not profile:
            return []
        return [self.apps[app_id] for app_id in profile.apps if app_id in self.apps]
