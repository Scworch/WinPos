"""Configuration models for WinPos."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class WindowMatch:
    title_contains: Optional[str] = None
    title_equals: Optional[str] = None
    class_name: Optional[str] = None
    process_name: Optional[str] = None

    @staticmethod
    def from_dict(data: Dict[str, Any] | None) -> "WindowMatch | None":
        if not data:
            return None
        return WindowMatch(
            title_contains=data.get("title_contains"),
            title_equals=data.get("title_equals"),
            class_name=data.get("class_name"),
            process_name=data.get("process_name"),
        )


@dataclass
class LaunchSpec:
    cmd: str
    args: List[str] = field(default_factory=list)
    cwd: Optional[str] = None

    @staticmethod
    def from_dict(data: Dict[str, Any] | None) -> "LaunchSpec | None":
        if not data:
            return None
        return LaunchSpec(
            cmd=data.get("cmd", ""),
            args=list(data.get("args", []) or []),
            cwd=data.get("cwd"),
        )


@dataclass
class ActionSpec:
    type: str
    params: Dict[str, Any] = field(default_factory=dict)
    when: Optional[Dict[str, Any]] = None
    retry: Optional[Dict[str, Any]] = None
    on_failure: List["ActionSpec"] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ActionSpec":
        return ActionSpec(
            type=data.get("type", ""),
            params=dict(data.get("params", {}) or {}),
            when=data.get("when"),
            retry=data.get("retry"),
            on_failure=[ActionSpec.from_dict(item) for item in data.get("on_failure", [])],
        )


@dataclass
class AppDefinition:
    app_id: str
    display_name: str
    launch: Optional[LaunchSpec] = None
    window_match: Optional[WindowMatch] = None
    actions: List[ActionSpec] = field(default_factory=list)

    @staticmethod
    def from_dict(app_id: str, data: Dict[str, Any]) -> "AppDefinition":
        return AppDefinition(
            app_id=app_id,
            display_name=data.get("display_name", app_id),
            launch=LaunchSpec.from_dict(data.get("launch")),
            window_match=WindowMatch.from_dict(data.get("window_match")),
            actions=[ActionSpec.from_dict(item) for item in data.get("actions", [])],
        )


@dataclass
class Profile:
    profile_id: str
    apps: List[str]
    allow_parallel: bool = False

    @staticmethod
    def from_dict(profile_id: str, data: Dict[str, Any]) -> "Profile":
        return Profile(
            profile_id=profile_id,
            apps=list(data.get("apps", []) or []),
            allow_parallel=bool(data.get("allow_parallel", False)),
        )


@dataclass
class Settings:
    allow_profile_reentry: bool = False
    default_timeout_s: float = 15.0
    default_profile: str = "default"

    @staticmethod
    def from_dict(data: Dict[str, Any] | None) -> "Settings":
        if not data:
            return Settings()
        return Settings(
            allow_profile_reentry=bool(data.get("allow_profile_reentry", False)),
            default_timeout_s=float(data.get("default_timeout_s", 15.0)),
            default_profile=str(data.get("default_profile", "default")),
        )


@dataclass
class Config:
    version: int
    monitor_roles: Dict[str, Dict[str, Any]]
    action_chains: Dict[str, List[ActionSpec]]
    apps: Dict[str, AppDefinition]
    profiles: Dict[str, Profile]
    settings: Settings

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Config":
        monitor_roles = dict(data.get("monitor_roles", {}) or {})
        action_chains = {
            name: [ActionSpec.from_dict(item) for item in chain]
            for name, chain in (data.get("action_chains", {}) or {}).items()
        }
        apps = {
            app_id: AppDefinition.from_dict(app_id, app_data)
            for app_id, app_data in (data.get("apps", {}) or {}).items()
        }
        profiles = {
            profile_id: Profile.from_dict(profile_id, profile_data)
            for profile_id, profile_data in (data.get("profiles", {}) or {}).items()
        }
        settings = Settings.from_dict(data.get("settings"))
        return Config(
            version=int(data.get("version", 1)),
            monitor_roles=monitor_roles,
            action_chains=action_chains,
            apps=apps,
            profiles=profiles,
            settings=settings,
        )
