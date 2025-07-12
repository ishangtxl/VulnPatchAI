"""
Redis Caching Service for performance optimization
"""
import json
import hashlib
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import redis
import pickle
import asyncio
from functools import wraps

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service for performance optimization"""
    
    def __init__(self):
        self.redis_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Redis client with error handling"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=False,  # We'll handle encoding ourselves
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Check if Redis cache is available"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a consistent cache key"""
        # Create a string representation of all arguments
        key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            kwargs_str = ':'.join(f"{k}={v}" for k, v in sorted_kwargs)
            key_data += f":{kwargs_str}"
        
        # Hash if key is too long
        if len(key_data) > 200:
            key_hash = hashlib.md5(key_data.encode()).hexdigest()
            return f"{prefix}:hash:{key_hash}"
        
        return key_data
    
    def set(
        self, 
        key: str, 
        value: Any, 
        expire_seconds: Optional[int] = None
    ) -> bool:
        """Set a value in cache with optional expiration"""
        if not self.is_available():
            return False
        
        try:
            # Serialize the value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = pickle.dumps(value)
            
            # Set with expiration
            if expire_seconds:
                return self.redis_client.setex(key, expire_seconds, serialized_value)
            else:
                return self.redis_client.set(key, serialized_value)
                
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def get(self, key: str) -> Any:
        """Get a value from cache"""
        if not self.is_available():
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # Try JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(value)
                
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        if not self.is_available():
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern"""
        if not self.is_available():
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error deleting cache pattern {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache"""
        if not self.is_available():
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Error checking cache key existence {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """Get time to live for a key"""
        if not self.is_available():
            return -1
        
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Error getting TTL for key {key}: {e}")
            return -1
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a numeric value"""
        if not self.is_available():
            return None
        
        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing key {key}: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.is_available():
            return {"status": "unavailable"}
        
        try:
            info = self.redis_client.info()
            return {
                "status": "available",
                "memory_used": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"status": "error", "error": str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)


class CVECache:
    """Specialized cache for CVE lookups"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.default_ttl = 86400  # 24 hours
    
    def get_cve_key(self, service_name: str, version: str = "", product: str = "") -> str:
        """Generate cache key for CVE lookup"""
        return self.cache._generate_key("cve", service_name, version, product)
    
    def get_cve_details_key(self, cve_id: str) -> str:
        """Generate cache key for CVE details"""
        return self.cache._generate_key("cve_details", cve_id)
    
    def set_cve_data(
        self, 
        service_name: str, 
        version: str, 
        product: str, 
        cve_data: Dict
    ) -> bool:
        """Cache CVE lookup data"""
        key = self.get_cve_key(service_name, version, product)
        # Add cache metadata
        cached_data = {
            "data": cve_data,
            "cached_at": datetime.utcnow().isoformat(),
            "service_name": service_name,
            "version": version,
            "product": product
        }
        return self.cache.set(key, cached_data, self.default_ttl)
    
    def get_cve_data(
        self, 
        service_name: str, 
        version: str = "", 
        product: str = ""
    ) -> Optional[Dict]:
        """Get cached CVE lookup data"""
        key = self.get_cve_key(service_name, version, product)
        cached_data = self.cache.get(key)
        
        if cached_data and isinstance(cached_data, dict):
            return cached_data.get("data")
        
        return None
    
    def set_cve_details(self, cve_id: str, details: Dict) -> bool:
        """Cache CVE details"""
        key = self.get_cve_details_key(cve_id)
        cached_data = {
            "data": details,
            "cached_at": datetime.utcnow().isoformat(),
            "cve_id": cve_id
        }
        return self.cache.set(key, cached_data, self.default_ttl)
    
    def get_cve_details(self, cve_id: str) -> Optional[Dict]:
        """Get cached CVE details"""
        key = self.get_cve_details_key(cve_id)
        cached_data = self.cache.get(key)
        
        if cached_data and isinstance(cached_data, dict):
            return cached_data.get("data")
        
        return None


class AIResponseCache:
    """Specialized cache for AI responses"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        # Different TTLs for different types of AI responses
        self.ttl_config = {
            "vulnerability_analysis": 3600,    # 1 hour
            "query_response": 1800,            # 30 minutes
            "report_generation": 7200,         # 2 hours
            "business_impact": 3600,           # 1 hour
            "patch_recommendation": 1800       # 30 minutes
        }
    
    def _get_query_hash(self, query: str, context: Dict) -> str:
        """Generate hash for query + context"""
        query_data = f"{query}:{json.dumps(context, sort_keys=True)}"
        return hashlib.md5(query_data.encode()).hexdigest()
    
    def get_vulnerability_analysis_key(
        self, 
        service_name: str, 
        version: str, 
        description: str
    ) -> str:
        """Generate cache key for vulnerability analysis"""
        analysis_hash = hashlib.md5(f"{service_name}:{version}:{description}".encode()).hexdigest()
        return self.cache._generate_key("ai_vuln_analysis", analysis_hash)
    
    def get_query_response_key(self, query: str, context: Dict, user_id: int) -> str:
        """Generate cache key for query responses"""
        query_hash = self._get_query_hash(query, context)
        return self.cache._generate_key("ai_query", user_id, query_hash)
    
    def get_report_key(self, vulnerabilities_hash: str, report_type: str) -> str:
        """Generate cache key for report generation"""
        return self.cache._generate_key("ai_report", report_type, vulnerabilities_hash)
    
    def set_vulnerability_analysis(
        self,
        service_name: str,
        version: str,
        description: str,
        analysis: Dict
    ) -> bool:
        """Cache vulnerability analysis"""
        key = self.get_vulnerability_analysis_key(service_name, version, description)
        cached_data = {
            "analysis": analysis,
            "cached_at": datetime.utcnow().isoformat(),
            "service_name": service_name,
            "version": version
        }
        ttl = self.ttl_config.get("vulnerability_analysis", 3600)
        return self.cache.set(key, cached_data, ttl)
    
    def get_vulnerability_analysis(
        self,
        service_name: str,
        version: str,
        description: str
    ) -> Optional[Dict]:
        """Get cached vulnerability analysis"""
        key = self.get_vulnerability_analysis_key(service_name, version, description)
        cached_data = self.cache.get(key)
        
        if cached_data and isinstance(cached_data, dict):
            return cached_data.get("analysis")
        
        return None
    
    def set_query_response(
        self,
        query: str,
        context: Dict,
        user_id: int,
        response: str
    ) -> bool:
        """Cache query response"""
        key = self.get_query_response_key(query, context, user_id)
        cached_data = {
            "response": response,
            "cached_at": datetime.utcnow().isoformat(),
            "query": query[:100],  # Truncated for debugging
            "user_id": user_id
        }
        ttl = self.ttl_config.get("query_response", 1800)
        return self.cache.set(key, cached_data, ttl)
    
    def get_query_response(
        self,
        query: str,
        context: Dict,
        user_id: int
    ) -> Optional[str]:
        """Get cached query response"""
        key = self.get_query_response_key(query, context, user_id)
        cached_data = self.cache.get(key)
        
        if cached_data and isinstance(cached_data, dict):
            return cached_data.get("response")
        
        return None
    
    def set_report(
        self,
        vulnerabilities_hash: str,
        report_type: str,
        report_content: str
    ) -> bool:
        """Cache report generation"""
        key = self.get_report_key(vulnerabilities_hash, report_type)
        cached_data = {
            "content": report_content,
            "cached_at": datetime.utcnow().isoformat(),
            "report_type": report_type,
            "vulnerabilities_hash": vulnerabilities_hash
        }
        ttl = self.ttl_config.get("report_generation", 7200)
        return self.cache.set(key, cached_data, ttl)
    
    def get_report(
        self,
        vulnerabilities_hash: str,
        report_type: str
    ) -> Optional[str]:
        """Get cached report"""
        key = self.get_report_key(vulnerabilities_hash, report_type)
        cached_data = self.cache.get(key)
        
        if cached_data and isinstance(cached_data, dict):
            return cached_data.get("content")
        
        return None
    
    def invalidate_user_cache(self, user_id: int) -> int:
        """Invalidate all cached data for a user"""
        pattern = f"*:ai_query:{user_id}:*"
        return self.cache.delete_pattern(pattern)


# Cache decorators for easy use
def cache_result(cache_key_func, ttl: int = 3600, cache_service: Optional[CacheService] = None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if cache_service is None or not cache_service.is_available():
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = cache_key_func(*args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                cache_service.set(cache_key, result, ttl)
                logger.debug(f"Cached result for key: {cache_key}")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if cache_service is None or not cache_service.is_available():
                return func(*args, **kwargs)
            
            # Generate cache key
            cache_key = cache_key_func(*args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache_service.set(cache_key, result, ttl)
                logger.debug(f"Cached result for key: {cache_key}")
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global cache instances
cache_service = CacheService()
cve_cache = CVECache(cache_service)
ai_cache = AIResponseCache(cache_service)