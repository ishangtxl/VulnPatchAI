"""
Theme and User Preferences schemas
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class ThemeDetails(BaseModel):
    """Theme color details"""
    name: str = Field(..., description="Theme name")
    description: str = Field(..., description="Theme description")
    primary_color: Optional[str] = Field(None, description="Primary color")
    secondary_color: Optional[str] = Field(None, description="Secondary color")
    background_color: Optional[str] = Field(None, description="Background color")
    surface_color: Optional[str] = Field(None, description="Surface color")
    text_primary: Optional[str] = Field(None, description="Primary text color")
    text_secondary: Optional[str] = Field(None, description="Secondary text color")
    accent_color: Optional[str] = Field(None, description="Accent color")
    success_color: Optional[str] = Field(None, description="Success color")
    warning_color: Optional[str] = Field(None, description="Warning color")
    error_color: Optional[str] = Field(None, description="Error color")
    info_color: Optional[str] = Field(None, description="Info color")


class LanguageDetails(BaseModel):
    """Language details"""
    name: str = Field(..., description="Language name")
    locale: str = Field(..., description="Locale code")
    rtl: bool = Field(default=False, description="Right-to-left text direction")


class TimezoneOption(BaseModel):
    """Timezone option"""
    value: str = Field(..., description="Timezone value")
    label: str = Field(..., description="Timezone display label")
    offset: str = Field(..., description="UTC offset")


class DashboardWidget(BaseModel):
    """Dashboard widget configuration"""
    widget_type: str = Field(..., description="Type of widget")
    position: Dict[str, int] = Field(..., description="Widget position (x, y)")
    size: Dict[str, int] = Field(..., description="Widget size (width, height)")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Widget-specific settings")
    visible: bool = Field(default=True, description="Widget visibility")


class DashboardLayout(BaseModel):
    """Dashboard layout configuration"""
    widgets: List[DashboardWidget] = Field(..., description="List of dashboard widgets")
    grid_settings: Dict[str, Any] = Field(..., description="Grid configuration")
    theme_override: Optional[str] = Field(None, description="Dashboard-specific theme override")
    auto_refresh: bool = Field(default=True, description="Auto-refresh enabled")
    refresh_interval: int = Field(default=300, description="Refresh interval in seconds")


class UserPreferences(BaseModel):
    """Complete user preferences"""
    user_id: int = Field(..., description="User ID")
    theme: Dict[str, Any] = Field(..., description="Theme preferences")
    language: Dict[str, Any] = Field(..., description="Language preferences")
    timezone: Dict[str, Any] = Field(..., description="Timezone preferences")
    dashboard_layout: Optional[DashboardLayout] = Field(None, description="Dashboard layout")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")


class ThemeUpdateRequest(BaseModel):
    """Request to update theme preference"""
    theme: str = Field(..., description="Theme name (light, dark, auto)")


class LanguageUpdateRequest(BaseModel):
    """Request to update language preference"""
    language: str = Field(..., description="Language code (en, es, fr, etc.)")


class TimezoneUpdateRequest(BaseModel):
    """Request to update timezone preference"""
    timezone: str = Field(..., description="Timezone identifier")


class DashboardLayoutUpdateRequest(BaseModel):
    """Request to update dashboard layout"""
    layout: DashboardLayout = Field(..., description="Dashboard layout configuration")


class MultiplePreferencesUpdateRequest(BaseModel):
    """Request to update multiple preferences at once"""
    theme: Optional[str] = Field(None, description="Theme preference")
    language: Optional[str] = Field(None, description="Language preference")
    timezone: Optional[str] = Field(None, description="Timezone preference")
    dashboard_layout: Optional[DashboardLayout] = Field(None, description="Dashboard layout")


class PreferencesUpdateResponse(BaseModel):
    """Response for preferences update"""
    success: bool = Field(..., description="Overall success status")
    updated_preferences: Dict[str, bool] = Field(..., description="Status of each preference update")
    message: str = Field(..., description="Response message")
    updated_at: str = Field(..., description="Update timestamp")


class ThemeCSS(BaseModel):
    """CSS theme variables"""
    theme_name: str = Field(..., description="Theme name")
    css_variables: str = Field(..., description="CSS variables string")
    media_queries: Optional[str] = Field(None, description="Media queries for responsive design")


class AvailableThemes(BaseModel):
    """Available themes response"""
    themes: Dict[str, ThemeDetails] = Field(..., description="Available themes")
    default_theme: str = Field(..., description="Default theme")
    supports_auto: bool = Field(..., description="Auto theme support")


class AvailableLanguages(BaseModel):
    """Available languages response"""
    languages: Dict[str, LanguageDetails] = Field(..., description="Available languages")
    default_language: str = Field(..., description="Default language")


class AccessibilityPreferences(BaseModel):
    """Accessibility preferences"""
    high_contrast: bool = Field(default=False, description="High contrast mode")
    rtl_support: bool = Field(default=False, description="Right-to-left text support")
    locale: str = Field(default="en-US", description="Locale for formatting")
    timezone: str = Field(default="UTC", description="User timezone")
    reduced_motion: bool = Field(default=False, description="Reduced motion preference")
    font_size_multiplier: float = Field(default=1.0, description="Font size multiplier")
    keyboard_navigation: bool = Field(default=True, description="Keyboard navigation support")


class PreferencesExport(BaseModel):
    """Preferences export data"""
    export_version: str = Field(..., description="Export format version")
    exported_at: str = Field(..., description="Export timestamp")
    user_id: int = Field(..., description="User ID")
    preferences: Dict[str, Any] = Field(..., description="User preferences data")


class PreferencesImport(BaseModel):
    """Preferences import request"""
    preferences_data: PreferencesExport = Field(..., description="Preferences export data")


class ThemeValidation(BaseModel):
    """Theme validation response"""
    is_valid: bool = Field(..., description="Theme validity")
    theme_name: str = Field(..., description="Validated theme name")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")


class SystemThemeInfo(BaseModel):
    """System theme information"""
    current_theme: str = Field(..., description="Current active theme")
    system_preference: Optional[str] = Field(None, description="System theme preference")
    auto_switch_enabled: bool = Field(..., description="Auto theme switching enabled")
    sunrise_time: Optional[str] = Field(None, description="Sunrise time for auto switching")
    sunset_time: Optional[str] = Field(None, description="Sunset time for auto switching")


class ThemeStatistics(BaseModel):
    """Theme usage statistics"""
    theme_usage: Dict[str, int] = Field(..., description="Theme usage counts")
    most_popular_theme: str = Field(..., description="Most popular theme")
    user_theme_switches: int = Field(..., description="Number of theme switches by user")
    last_theme_change: Optional[str] = Field(None, description="Last theme change timestamp")


class CustomTheme(BaseModel):
    """Custom theme definition"""
    theme_id: str = Field(..., description="Unique theme identifier")
    name: str = Field(..., description="Custom theme name")
    description: str = Field(..., description="Theme description")
    based_on: str = Field(..., description="Base theme (light or dark)")
    custom_colors: Dict[str, str] = Field(..., description="Custom color overrides")
    created_by: int = Field(..., description="Creator user ID")
    is_public: bool = Field(default=False, description="Public theme availability")
    created_at: str = Field(..., description="Creation timestamp")


class ThemeConfiguration(BaseModel):
    """Complete theme configuration"""
    active_theme: str = Field(..., description="Currently active theme")
    theme_details: ThemeDetails = Field(..., description="Active theme details")
    custom_overrides: Optional[Dict[str, str]] = Field(None, description="Custom color overrides")
    accessibility_settings: AccessibilityPreferences = Field(..., description="Accessibility preferences")
    auto_switch_settings: Optional[Dict[str, Any]] = Field(None, description="Auto switch configuration")


class ResponsiveBreakpoints(BaseModel):
    """Responsive design breakpoints"""
    xs: int = Field(default=0, description="Extra small screens")
    sm: int = Field(default=600, description="Small screens")
    md: int = Field(default=960, description="Medium screens")
    lg: int = Field(default=1280, description="Large screens")
    xl: int = Field(default=1920, description="Extra large screens")


class ThemeAssets(BaseModel):
    """Theme-related assets"""
    logo_light: Optional[str] = Field(None, description="Logo for light theme")
    logo_dark: Optional[str] = Field(None, description="Logo for dark theme")
    favicon_light: Optional[str] = Field(None, description="Favicon for light theme")
    favicon_dark: Optional[str] = Field(None, description="Favicon for dark theme")
    background_pattern: Optional[str] = Field(None, description="Background pattern URL")


class ThemeHealth(BaseModel):
    """Theme service health status"""
    status: str = Field(..., description="Service health status")
    available_themes: int = Field(..., description="Number of available themes")
    active_users_by_theme: Dict[str, int] = Field(..., description="Active users per theme")
    theme_switching_enabled: bool = Field(..., description="Theme switching availability")
    last_theme_update: Optional[str] = Field(None, description="Last theme update timestamp")
    css_generation_time_ms: float = Field(..., description="CSS generation time in milliseconds")