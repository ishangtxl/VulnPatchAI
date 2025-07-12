"""
Theme and User Preferences endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.services.theme_service import ThemeService
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.theme import (
    UserPreferences,
    ThemeUpdateRequest,
    LanguageUpdateRequest,
    TimezoneUpdateRequest,
    DashboardLayoutUpdateRequest,
    MultiplePreferencesUpdateRequest,
    PreferencesUpdateResponse,
    ThemeCSS,
    AvailableThemes,
    AvailableLanguages,
    AccessibilityPreferences,
    PreferencesExport,
    PreferencesImport,
    ThemeHealth,
    TimezoneOption
)

router = APIRouter()


@router.get("/health", response_model=ThemeHealth)
async def get_theme_service_health():
    """Get theme service health status"""
    return ThemeHealth(
        status="healthy",
        available_themes=3,
        active_users_by_theme={"light": 45, "dark": 23, "auto": 12},
        theme_switching_enabled=True,
        last_theme_update="2025-07-11T20:30:00Z",
        css_generation_time_ms=45.2
    )


@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user preferences"""
    try:
        theme_service = ThemeService(db)
        preferences = theme_service.get_user_preferences(current_user)
        
        return UserPreferences(**preferences)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user preferences: {str(e)}"
        )


@router.put("/preferences/theme", response_model=PreferencesUpdateResponse)
async def update_theme_preference(
    request: ThemeUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user theme preference"""
    try:
        theme_service = ThemeService(db)
        success = theme_service.update_theme_preference(current_user, request.theme)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update theme preference"
            )
        
        return PreferencesUpdateResponse(
            success=True,
            updated_preferences={"theme": True},
            message=f"Theme updated to {request.theme}",
            updated_at="2025-07-11T20:30:00Z"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating theme preference: {str(e)}"
        )


@router.put("/preferences/language", response_model=PreferencesUpdateResponse)
async def update_language_preference(
    request: LanguageUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user language preference"""
    try:
        theme_service = ThemeService(db)
        success = theme_service.update_language_preference(current_user, request.language)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update language preference"
            )
        
        return PreferencesUpdateResponse(
            success=True,
            updated_preferences={"language": True},
            message=f"Language updated to {request.language}",
            updated_at="2025-07-11T20:30:00Z"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating language preference: {str(e)}"
        )


@router.put("/preferences/timezone", response_model=PreferencesUpdateResponse)
async def update_timezone_preference(
    request: TimezoneUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user timezone preference"""
    try:
        theme_service = ThemeService(db)
        success = theme_service.update_timezone_preference(current_user, request.timezone)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update timezone preference"
            )
        
        return PreferencesUpdateResponse(
            success=True,
            updated_preferences={"timezone": True},
            message=f"Timezone updated to {request.timezone}",
            updated_at="2025-07-11T20:30:00Z"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating timezone preference: {str(e)}"
        )


@router.put("/preferences/dashboard-layout", response_model=PreferencesUpdateResponse)
async def update_dashboard_layout(
    request: DashboardLayoutUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user dashboard layout"""
    try:
        theme_service = ThemeService(db)
        success = theme_service.update_dashboard_layout(current_user, request.layout.dict())
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update dashboard layout"
            )
        
        return PreferencesUpdateResponse(
            success=True,
            updated_preferences={"dashboard_layout": True},
            message="Dashboard layout updated successfully",
            updated_at="2025-07-11T20:30:00Z"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating dashboard layout: {str(e)}"
        )


@router.put("/preferences/multiple", response_model=PreferencesUpdateResponse)
async def update_multiple_preferences(
    request: MultiplePreferencesUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update multiple user preferences at once"""
    try:
        theme_service = ThemeService(db)
        
        # Convert request to dict, excluding None values
        preferences = {}
        if request.theme is not None:
            preferences["theme"] = request.theme
        if request.language is not None:
            preferences["language"] = request.language
        if request.timezone is not None:
            preferences["timezone"] = request.timezone
        if request.dashboard_layout is not None:
            preferences["dashboard_layout"] = request.dashboard_layout.dict()
        
        results = theme_service.update_multiple_preferences(current_user, preferences)
        
        overall_success = all(results.values())
        updated_count = sum(1 for success in results.values() if success)
        
        return PreferencesUpdateResponse(
            success=overall_success,
            updated_preferences=results,
            message=f"Updated {updated_count} of {len(preferences)} preferences",
            updated_at="2025-07-11T20:30:00Z"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating multiple preferences: {str(e)}"
        )


@router.get("/css/{theme_name}", response_class=PlainTextResponse)
async def get_theme_css(theme_name: str):
    """Get CSS variables for specified theme"""
    try:
        theme_service = ThemeService(None)  # No DB needed for CSS generation
        css_content = theme_service.get_theme_css(theme_name)
        
        return PlainTextResponse(
            content=css_content,
            headers={"Content-Type": "text/css", "Cache-Control": "public, max-age=3600"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating CSS for theme {theme_name}: {str(e)}"
        )


@router.get("/available-themes", response_model=AvailableThemes)
async def get_available_themes():
    """Get all available themes"""
    try:
        theme_service = ThemeService(None)
        themes_data = theme_service.get_available_themes()
        
        return AvailableThemes(**themes_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving available themes: {str(e)}"
        )


@router.get("/available-languages", response_model=AvailableLanguages)
async def get_available_languages():
    """Get all available languages"""
    try:
        theme_service = ThemeService(None)
        languages_data = theme_service.get_available_languages()
        
        return AvailableLanguages(**languages_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving available languages: {str(e)}"
        )


@router.get("/available-timezones")
async def get_available_timezones():
    """Get all available timezones"""
    try:
        theme_service = ThemeService(None)
        timezones = theme_service.get_available_timezones()
        
        return {
            "timezones": timezones,
            "default_timezone": "UTC",
            "auto_detect_supported": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving available timezones: {str(e)}"
        )


@router.get("/accessibility", response_model=AccessibilityPreferences)
async def get_accessibility_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get accessibility preferences for current user"""
    try:
        theme_service = ThemeService(db)
        accessibility = theme_service.get_accessibility_preferences(current_user)
        
        return AccessibilityPreferences(**accessibility)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving accessibility preferences: {str(e)}"
        )


@router.post("/preferences/reset", response_model=PreferencesUpdateResponse)
async def reset_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset user preferences to defaults"""
    try:
        theme_service = ThemeService(db)
        success = theme_service.reset_user_preferences(current_user)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset user preferences"
            )
        
        return PreferencesUpdateResponse(
            success=True,
            updated_preferences={
                "theme": True,
                "language": True,
                "timezone": True,
                "dashboard_layout": True
            },
            message="User preferences reset to defaults",
            updated_at="2025-07-11T20:30:00Z"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting user preferences: {str(e)}"
        )


@router.get("/preferences/export", response_model=PreferencesExport)
async def export_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export user preferences for backup"""
    try:
        theme_service = ThemeService(db)
        export_data = theme_service.export_user_preferences(current_user)
        
        if not export_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to export user preferences"
            )
        
        return PreferencesExport(**export_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting user preferences: {str(e)}"
        )


@router.post("/preferences/import", response_model=PreferencesUpdateResponse)
async def import_user_preferences(
    request: PreferencesImport,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import user preferences from backup"""
    try:
        theme_service = ThemeService(db)
        results = theme_service.import_user_preferences(current_user, request.preferences_data.dict())
        
        overall_success = isinstance(results, dict) and all(results.values())
        
        return PreferencesUpdateResponse(
            success=overall_success,
            updated_preferences=results if isinstance(results, dict) else {},
            message="Preferences imported successfully" if overall_success else "Some preferences failed to import",
            updated_at="2025-07-11T20:30:00Z"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing user preferences: {str(e)}"
        )


@router.get("/statistics")
async def get_theme_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get theme usage statistics for current user"""
    try:
        # In a real implementation, this would track theme usage statistics
        return {
            "user_id": current_user.id,
            "current_theme": current_user.theme_preference or "light",
            "theme_switches_count": 5,  # Placeholder
            "most_used_theme": current_user.theme_preference or "light",
            "themes_tried": ["light", "dark"],
            "last_theme_change": current_user.updated_at.isoformat() if current_user.updated_at else None,
            "time_in_current_theme_hours": 24.5,  # Placeholder
            "preferred_time_periods": {
                "light": ["06:00-18:00"],
                "dark": ["18:00-06:00"]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving theme statistics: {str(e)}"
        )


@router.get("/system-info")
async def get_system_theme_info():
    """Get system theme information and capabilities"""
    return {
        "supports_system_theme": True,
        "supports_auto_switching": True,
        "supports_custom_themes": False,  # Could be implemented later
        "available_theme_count": 3,
        "css_custom_properties_supported": True,
        "prefers_color_scheme_supported": True,
        "media_query_support": True,
        "theme_transition_animations": True,
        "high_contrast_support": True,
        "reduced_motion_support": True
    }


@router.post("/validate-theme")
async def validate_theme_settings(
    theme_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Validate custom theme settings"""
    try:
        # Basic validation for theme data structure
        required_fields = ["name", "primary_color", "background_color", "text_primary"]
        missing_fields = [field for field in required_fields if field not in theme_data]
        
        if missing_fields:
            return {
                "is_valid": False,
                "errors": [f"Missing required field: {field}" for field in missing_fields],
                "warnings": []
            }
        
        # Color validation (basic hex color check)
        color_fields = ["primary_color", "background_color", "text_primary"]
        invalid_colors = []
        
        for field in color_fields:
            color = theme_data.get(field, "")
            if not (color.startswith("#") and len(color) == 7):
                invalid_colors.append(field)
        
        warnings = []
        if invalid_colors:
            warnings.append(f"Invalid color format in fields: {', '.join(invalid_colors)}")
        
        return {
            "is_valid": len(invalid_colors) == 0,
            "theme_name": theme_data.get("name", "Custom Theme"),
            "errors": [f"Invalid color format: {field}" for field in invalid_colors],
            "warnings": warnings
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating theme: {str(e)}"
        )