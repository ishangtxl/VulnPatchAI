"""
WebSocket endpoints for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.services.websocket_service import websocket_service, manager
from app.utils.auth import get_current_user_websocket, get_current_user
from app.models.user import User

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)


@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time updates
    Usage: ws://localhost:8000/api/v1/ws/connect?token=<jwt_token>
    """
    try:
        # Authenticate user via token parameter
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
            return
        
        # Verify JWT token and get user
        user = await get_current_user_websocket(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication token")
            return
        
        # Handle the WebSocket connection
        await websocket_service.handle_websocket_connection(websocket, user.id)
        
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Internal server error")
        except:
            pass


@router.get("/status")
async def websocket_status(current_user: User = Depends(get_current_user)):
    """Get WebSocket connection status and statistics"""
    try:
        connection_stats = manager.get_connection_count()
        
        # Check if current user is connected
        user_connected = current_user.id in manager.active_connections
        user_connections = len(manager.active_connections.get(current_user.id, set()))
        
        return {
            "status": "active",
            "global_stats": connection_stats,
            "user_status": {
                "connected": user_connected,
                "connection_count": user_connections,
                "user_id": current_user.id
            },
            "features": [
                "Real-time scan progress",
                "Dashboard updates",
                "Critical vulnerability alerts",
                "Scan completion notifications"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving WebSocket status: {str(e)}"
        )


@router.post("/broadcast")
async def broadcast_message(
    message: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Broadcast message to all connected users (admin only)
    """
    # Check if user has admin privileges
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can broadcast messages"
        )
    
    try:
        await manager.broadcast_to_all({
            "type": "admin_broadcast",
            "data": {
                "message": message.get("message", ""),
                "priority": message.get("priority", "info"),
                "from": "System Administrator"
            }
        })
        
        return {
            "status": "success",
            "message": "Broadcast sent successfully",
            "recipients": manager.get_connection_count()["total_users"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error broadcasting message: {str(e)}"
        )


@router.post("/notify/{user_id}")
async def send_user_notification(
    user_id: int,
    notification: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Send notification to specific user
    """
    # Users can only send notifications to themselves, admins can send to anyone
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only send notifications to yourself"
        )
    
    try:
        await manager.send_personal_message(user_id, {
            "type": "notification",
            "data": {
                "title": notification.get("title", "Notification"),
                "message": notification.get("message", ""),
                "severity": notification.get("severity", "info"),
                "action_url": notification.get("action_url"),
                "from_user": current_user.email
            }
        })
        
        return {
            "status": "success",
            "message": f"Notification sent to user {user_id}",
            "notification": notification
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending notification: {str(e)}"
        )


@router.delete("/disconnect/{user_id}")
async def force_disconnect_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Force disconnect user (admin only)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can force disconnect users"
        )
    
    try:
        if user_id in manager.active_connections:
            # Send disconnect message to user
            await manager.send_personal_message(user_id, {
                "type": "force_disconnect",
                "data": {
                    "reason": "Disconnected by administrator",
                    "message": "Your session has been terminated by an administrator"
                }
            })
            
            # Close all connections for this user
            connections_to_close = list(manager.active_connections[user_id])
            for connection in connections_to_close:
                try:
                    await connection.close(code=status.WS_1008_POLICY_VIOLATION, reason="Disconnected by admin")
                except:
                    pass
                manager.disconnect(connection, user_id)
            
            return {
                "status": "success",
                "message": f"User {user_id} disconnected successfully",
                "connections_closed": len(connections_to_close)
            }
        else:
            return {
                "status": "info",
                "message": f"User {user_id} is not currently connected"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error disconnecting user: {str(e)}"
        )


@router.get("/health")
async def websocket_health():
    """WebSocket service health check"""
    try:
        stats = manager.get_connection_count()
        
        return {
            "status": "healthy",
            "service": "WebSocket Service",
            "version": "1.0.0",
            "statistics": stats,
            "uptime": "Available",
            "features": {
                "real_time_updates": True,
                "scan_progress": True,
                "dashboard_refresh": True,
                "notifications": True,
                "admin_broadcast": True
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"WebSocket service unhealthy: {str(e)}"
        )