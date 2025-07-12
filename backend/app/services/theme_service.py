"""
Theme and User Preferences Service
"""
import json
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.user import User

logger = logging.getLogger(__name__)


class ThemeService:
    """Service for managing user themes and preferences"""
    
    # Available themes
    AVAILABLE_THEMES = {
        "light": {
            "name": "Light",
            "description": "Clean, bright interface for daytime use",
            "primary_color": "#1976d2",
            "secondary_color": "#dc004e",
            "background_color": "#ffffff",
            "surface_color": "#f5f5f5",
            "text_primary": "#212121",
            "text_secondary": "#757575",
            "accent_color": "#ff5722",
            "success_color": "#4caf50",
            "warning_color": "#ff9800",
            "error_color": "#f44336",
            "info_color": "#2196f3"
        },
        "dark": {
            "name": "Dark",
            "description": "Easy on the eyes for low-light environments",
            "primary_color": "#90caf9",
            "secondary_color": "#f48fb1",
            "background_color": "#121212",
            "surface_color": "#1e1e1e",
            "text_primary": "#ffffff",
            "text_secondary": "#b3b3b3",
            "accent_color": "#ff7043",
            "success_color": "#66bb6a",
            "warning_color": "#ffb74d",
            "error_color": "#ef5350",
            "info_color": "#42a5f5"
        },
        "auto": {
            "name": "Auto",
            "description": "Automatically switches based on system preference",
            "inherits_from": "system"
        }
    }
    
    # Available languages
    AVAILABLE_LANGUAGES = {
        "en": {"name": "English", "locale": "en-US", "rtl": False},
        "es": {"name": "Español", "locale": "es-ES", "rtl": False},
        "fr": {"name": "Français", "locale": "fr-FR", "rtl": False},
        "de": {"name": "Deutsch", "locale": "de-DE", "rtl": False},
        "ja": {"name": "日本語", "locale": "ja-JP", "rtl": False},
        "ar": {"name": "العربية", "locale": "ar-SA", "rtl": True},
        "zh": {"name": "中文", "locale": "zh-CN", "rtl": False}
    }
    
    # Common timezones
    COMMON_TIMEZONES = [
        {"value": "UTC", "label": "UTC (Coordinated Universal Time)", "offset": "+00:00"},
        {"value": "America/New_York", "label": "Eastern Time (US)", "offset": "-05:00"},
        {"value": "America/Chicago", "label": "Central Time (US)", "offset": "-06:00"},
        {"value": "America/Denver", "label": "Mountain Time (US)", "offset": "-07:00"},
        {"value": "America/Los_Angeles", "label": "Pacific Time (US)", "offset": "-08:00"},
        {"value": "Europe/London", "label": "Greenwich Mean Time", "offset": "+00:00"},
        {"value": "Europe/Paris", "label": "Central European Time", "offset": "+01:00"},
        {"value": "Europe/Berlin", "label": "Central European Time", "offset": "+01:00"},
        {"value": "Asia/Tokyo", "label": "Japan Standard Time", "offset": "+09:00"},
        {"value": "Asia/Shanghai", "label": "China Standard Time", "offset": "+08:00"},
        {"value": "Asia/Dubai", "label": "Gulf Standard Time", "offset": "+04:00"},
        {"value": "Australia/Sydney", "label": "Australian Eastern Time", "offset": "+10:00"}
    ]
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_preferences(self, user: User) -> Dict[str, Any]:
        """Get complete user preferences"""
        try:
            # Parse dashboard layout if it exists
            dashboard_layout = None
            if user.dashboard_layout:
                try:
                    dashboard_layout = json.loads(user.dashboard_layout)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid dashboard layout JSON for user {user.id}")
                    dashboard_layout = None
            
            # Get theme details
            theme_preference = user.theme_preference or "light"
            theme_details = self.AVAILABLE_THEMES.get(theme_preference, self.AVAILABLE_THEMES["light"])
            
            # Get language details
            language_preference = user.language_preference or "en"
            language_details = self.AVAILABLE_LANGUAGES.get(language_preference, self.AVAILABLE_LANGUAGES["en"])
            
            return {
                "user_id": user.id,
                "theme": {
                    "current": theme_preference,
                    "details": theme_details,
                    "available_themes": list(self.AVAILABLE_THEMES.keys())
                },
                "language": {
                    "current": language_preference,
                    "details": language_details,
                    "available_languages": self.AVAILABLE_LANGUAGES
                },
                "timezone": {
                    "current": user.timezone_preference or "UTC",
                    "available_timezones": self.COMMON_TIMEZONES
                },
                "dashboard_layout": dashboard_layout,
                "last_updated": user.updated_at.isoformat() if user.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting user preferences for user {user.id}: {e}")
            return self._get_default_preferences(user.id)
    
    def update_theme_preference(self, user: User, theme: str) -> bool:
        """Update user theme preference"""
        try:
            if theme not in self.AVAILABLE_THEMES:
                raise ValueError(f"Invalid theme: {theme}. Available themes: {list(self.AVAILABLE_THEMES.keys())}")
            
            user.theme_preference = theme
            self.db.commit()
            
            logger.info(f"Updated theme preference for user {user.id} to {theme}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating theme preference for user {user.id}: {e}")
            self.db.rollback()
            return False
    
    def update_language_preference(self, user: User, language: str) -> bool:
        """Update user language preference"""
        try:
            if language not in self.AVAILABLE_LANGUAGES:
                raise ValueError(f"Invalid language: {language}. Available languages: {list(self.AVAILABLE_LANGUAGES.keys())}")
            
            user.language_preference = language
            self.db.commit()
            
            logger.info(f"Updated language preference for user {user.id} to {language}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating language preference for user {user.id}: {e}")
            self.db.rollback()
            return False
    
    def update_timezone_preference(self, user: User, timezone: str) -> bool:
        """Update user timezone preference"""
        try:
            # Validate timezone
            valid_timezones = [tz["value"] for tz in self.COMMON_TIMEZONES]
            if timezone not in valid_timezones:
                raise ValueError(f"Invalid timezone: {timezone}")
            
            user.timezone_preference = timezone
            self.db.commit()
            
            logger.info(f"Updated timezone preference for user {user.id} to {timezone}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating timezone preference for user {user.id}: {e}")
            self.db.rollback()
            return False
    
    def update_dashboard_layout(self, user: User, layout: Dict[str, Any]) -> bool:
        """Update user dashboard layout"""
        try:
            # Validate layout structure
            if not self._validate_dashboard_layout(layout):
                raise ValueError("Invalid dashboard layout structure")
            
            user.dashboard_layout = json.dumps(layout)
            self.db.commit()
            
            logger.info(f"Updated dashboard layout for user {user.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating dashboard layout for user {user.id}: {e}")
            self.db.rollback()
            return False
    
    def update_multiple_preferences(self, user: User, preferences: Dict[str, Any]) -> Dict[str, bool]:
        """Update multiple user preferences at once"""
        results = {}
        
        try:
            # Update theme if provided
            if "theme" in preferences:
                results["theme"] = self.update_theme_preference(user, preferences["theme"])
            
            # Update language if provided
            if "language" in preferences:
                results["language"] = self.update_language_preference(user, preferences["language"])
            
            # Update timezone if provided
            if "timezone" in preferences:
                results["timezone"] = self.update_timezone_preference(user, preferences["timezone"])
            
            # Update dashboard layout if provided
            if "dashboard_layout" in preferences:
                results["dashboard_layout"] = self.update_dashboard_layout(user, preferences["dashboard_layout"])
            
            return results
            
        except Exception as e:
            logger.error(f"Error updating multiple preferences for user {user.id}: {e}")
            self.db.rollback()
            return {key: False for key in preferences.keys()}
    
    def get_theme_css(self, theme: str) -> str:
        """Generate CSS variables for theme"""
        try:
            theme_data = self.AVAILABLE_THEMES.get(theme, self.AVAILABLE_THEMES["light"])
            
            # Skip auto theme as it doesn't have direct CSS
            if theme == "auto":
                return self.get_theme_css("light")  # Default fallback
            
            css_vars = ":root {\n"
            for key, value in theme_data.items():
                if key not in ["name", "description", "inherits_from"]:
                    css_var_name = f"--{key.replace('_', '-')}"
                    css_vars += f"  {css_var_name}: {value};\n"
            css_vars += "}\n"
            
            return css_vars
            
        except Exception as e:
            logger.error(f"Error generating CSS for theme {theme}: {e}")
            return self.get_theme_css("light")  # Fallback to light theme
    
    def get_available_themes(self) -> Dict[str, Any]:
        """Get all available themes with their details"""
        return {
            "themes": self.AVAILABLE_THEMES,
            "default_theme": "light",
            "supports_auto": True
        }
    
    def get_available_languages(self) -> Dict[str, Any]:
        """Get all available languages"""
        return {
            "languages": self.AVAILABLE_LANGUAGES,
            "default_language": "en"
        }
    
    def get_available_timezones(self) -> List[Dict[str, str]]:
        """Get all available timezones"""
        return self.COMMON_TIMEZONES
    
    def reset_user_preferences(self, user: User) -> bool:
        """Reset user preferences to defaults"""
        try:
            user.theme_preference = "light"
            user.language_preference = "en"
            user.timezone_preference = "UTC"
            user.dashboard_layout = None
            self.db.commit()
            
            logger.info(f"Reset preferences for user {user.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting preferences for user {user.id}: {e}")
            self.db.rollback()
            return False
    
    def export_user_preferences(self, user: User) -> Dict[str, Any]:
        """Export user preferences for backup/transfer"""
        try:
            preferences = self.get_user_preferences(user)
            
            return {
                "export_version": "1.0",
                "exported_at": datetime.utcnow().isoformat(),
                "user_id": user.id,
                "preferences": {
                    "theme": preferences["theme"]["current"],
                    "language": preferences["language"]["current"],
                    "timezone": preferences["timezone"]["current"],
                    "dashboard_layout": preferences["dashboard_layout"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error exporting preferences for user {user.id}: {e}")
            return {}
    
    def import_user_preferences(self, user: User, preferences_data: Dict[str, Any]) -> bool:
        """Import user preferences from backup"""
        try:
            if preferences_data.get("export_version") != "1.0":
                raise ValueError("Unsupported preferences export version")
            
            prefs = preferences_data.get("preferences", {})
            return self.update_multiple_preferences(user, prefs)
            
        except Exception as e:
            logger.error(f"Error importing preferences for user {user.id}: {e}")
            return False
    
    def _get_default_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get default preferences when errors occur"""
        return {
            "user_id": user_id,
            "theme": {
                "current": "light",
                "details": self.AVAILABLE_THEMES["light"],
                "available_themes": list(self.AVAILABLE_THEMES.keys())
            },
            "language": {
                "current": "en",
                "details": self.AVAILABLE_LANGUAGES["en"],
                "available_languages": self.AVAILABLE_LANGUAGES
            },
            "timezone": {
                "current": "UTC",
                "available_timezones": self.COMMON_TIMEZONES
            },
            "dashboard_layout": None,
            "last_updated": None
        }
    
    def _validate_dashboard_layout(self, layout: Dict[str, Any]) -> bool:
        """Validate dashboard layout structure"""
        try:
            # Basic validation - layout should be a dict with reasonable structure
            if not isinstance(layout, dict):
                return False
            
            # Check for required fields
            required_fields = ["widgets", "grid_settings"]
            for field in required_fields:
                if field not in layout:
                    return False
            
            # Validate widgets array
            if not isinstance(layout["widgets"], list):
                return False
            
            # Validate each widget configuration
            for widget in layout["widgets"]:
                if not isinstance(widget, dict):
                    return False
                
                required_widget_fields = ["widget_type", "position", "size"]
                for field in required_widget_fields:
                    if field not in widget:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating dashboard layout: {e}")
            return False
    
    def get_accessibility_preferences(self, user: User) -> Dict[str, Any]:
        """Get accessibility-related preferences"""
        try:
            language_details = self.AVAILABLE_LANGUAGES.get(
                user.language_preference or "en", 
                self.AVAILABLE_LANGUAGES["en"]
            )
            
            theme_preference = user.theme_preference or "light"
            
            return {
                "high_contrast": theme_preference == "dark",
                "rtl_support": language_details.get("rtl", False),
                "locale": language_details.get("locale", "en-US"),
                "timezone": user.timezone_preference or "UTC",
                "reduced_motion": False,  # Could be added as a user preference
                "font_size_multiplier": 1.0,  # Could be added as a user preference
                "keyboard_navigation": True
            }
            
        except Exception as e:
            logger.error(f"Error getting accessibility preferences for user {user.id}: {e}")
            return {
                "high_contrast": False,
                "rtl_support": False,
                "locale": "en-US",
                "timezone": "UTC",
                "reduced_motion": False,
                "font_size_multiplier": 1.0,
                "keyboard_navigation": True
            }