"""
WebSocket service for real-time updates
"""
import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Store scan processing status
        self.scan_status: Dict[int, Dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected via WebSocket. Active connections: {len(self.active_connections.get(user_id, []))}")
        
        # Send current scan status if any
        if user_id in self.scan_status:
            await self.send_personal_message(user_id, {
                "type": "scan_status",
                "data": self.scan_status[user_id]
            })
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            # Clean up empty connection sets
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            
            logger.info(f"User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(self, user_id: int, message: dict):
        """Send message to specific user's connections"""
        if user_id not in self.active_connections:
            return
        
        message_str = json.dumps({
            **message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Send to all connections for this user
        disconnected_connections = set()
        
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                disconnected_connections.add(connection)
        
        # Remove failed connections
        for connection in disconnected_connections:
            self.active_connections[user_id].discard(connection)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected users"""
        message_str = json.dumps({
            **message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        for user_id, connections in self.active_connections.items():
            disconnected_connections = set()
            
            for connection in connections:
                try:
                    await connection.send_text(message_str)
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id}: {e}")
                    disconnected_connections.add(connection)
            
            # Remove failed connections
            for connection in disconnected_connections:
                connections.discard(connection)
    
    async def update_scan_progress(self, user_id: int, scan_id: int, progress: dict):
        """Update scan processing progress"""
        if user_id not in self.scan_status:
            self.scan_status[user_id] = {}
        
        self.scan_status[user_id][scan_id] = {
            "scan_id": scan_id,
            "progress": progress.get("progress", 0),
            "status": progress.get("status", "processing"),
            "message": progress.get("message", ""),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Send update to user
        await self.send_personal_message(user_id, {
            "type": "scan_progress",
            "data": self.scan_status[user_id][scan_id]
        })
    
    async def notify_scan_complete(self, user_id: int, scan_id: int, results: dict):
        """Notify when scan processing is complete"""
        # Update scan status
        if user_id in self.scan_status and scan_id in self.scan_status[user_id]:
            self.scan_status[user_id][scan_id].update({
                "status": "completed",
                "progress": 100,
                "message": "Scan processing completed",
                "results": results,
                "completed_at": datetime.utcnow().isoformat()
            })
        
        # Send completion notification
        await self.send_personal_message(user_id, {
            "type": "scan_complete",
            "data": {
                "scan_id": scan_id,
                "results": results,
                "message": "Your scan has been processed successfully!"
            }
        })
        
        # Also send updated dashboard metrics
        await self.send_dashboard_update(user_id)
    
    async def send_dashboard_update(self, user_id: int):
        """Send updated dashboard metrics to user"""
        # This would typically fetch fresh metrics from the database
        # For now, we'll send a refresh signal
        await self.send_personal_message(user_id, {
            "type": "dashboard_refresh",
            "data": {
                "message": "Dashboard data updated, please refresh metrics"
            }
        })
    
    async def notify_vulnerability_update(self, user_id: int, vulnerability_data: dict):
        """Notify about vulnerability status updates"""
        await self.send_personal_message(user_id, {
            "type": "vulnerability_update",
            "data": vulnerability_data
        })
    
    async def notify_critical_vulnerability(self, user_id: int, vulnerability: dict):
        """Send urgent notification for critical vulnerabilities"""
        await self.send_personal_message(user_id, {
            "type": "critical_alert",
            "data": {
                "severity": "critical",
                "title": "Critical Vulnerability Detected",
                "vulnerability": vulnerability,
                "action_required": True
            }
        })
    
    def get_connection_count(self) -> dict:
        """Get current connection statistics"""
        total_connections = sum(len(connections) for connections in self.active_connections.values())
        
        return {
            "total_users": len(self.active_connections),
            "total_connections": total_connections,
            "users_online": list(self.active_connections.keys())
        }


# Global connection manager instance
manager = ConnectionManager()


class WebSocketService:
    """Service for WebSocket operations"""
    
    def __init__(self):
        self.manager = manager
    
    async def handle_websocket_connection(self, websocket: WebSocket, user_id: int):
        """Handle individual WebSocket connection lifecycle"""
        await self.manager.connect(websocket, user_id)
        
        try:
            while True:
                # Listen for client messages (heartbeat, requests, etc.)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await self._handle_client_message(user_id, message)
                
        except WebSocketDisconnect:
            self.manager.disconnect(websocket, user_id)
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {e}")
            self.manager.disconnect(websocket, user_id)
    
    async def _handle_client_message(self, user_id: int, message: dict):
        """Handle messages from WebSocket clients"""
        message_type = message.get("type")
        
        if message_type == "ping":
            # Respond to heartbeat
            await self.manager.send_personal_message(user_id, {
                "type": "pong",
                "data": {"status": "alive"}
            })
        
        elif message_type == "request_dashboard_update":
            # Client requesting fresh dashboard data
            await self.manager.send_dashboard_update(user_id)
        
        elif message_type == "subscribe_scan":
            # Client wants to monitor specific scan
            scan_id = message.get("scan_id")
            if scan_id:
                # Send current status if available
                if user_id in self.manager.scan_status and scan_id in self.manager.scan_status[user_id]:
                    await self.manager.send_personal_message(user_id, {
                        "type": "scan_status",
                        "data": self.manager.scan_status[user_id][scan_id]
                    })


# Global WebSocket service instance
websocket_service = WebSocketService()