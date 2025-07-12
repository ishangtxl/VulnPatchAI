"""
Enhanced CVE/CVSS lookup service with Redis caching
"""
import aiohttp
import asyncio
from typing import Dict, Optional, List
import logging
import json
import hashlib

from app.core.config import settings
from app.services.cache_service import cve_cache

logger = logging.getLogger(__name__)


class CVEService:
    def __init__(self):
        self.nvd_base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.session = None
        self.cache = cve_cache
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            headers = {}
            if settings.NVD_API_KEY:
                headers["apiKey"] = settings.NVD_API_KEY
            
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def lookup_cve(self, service_name: str, version: str, product: str = "") -> Optional[Dict]:
        """Lookup CVE information for a service with caching"""
        try:
            # Check cache first
            cached_data = self.cache.get_cve_data(service_name, version, product)
            if cached_data:
                logger.debug(f"Cache hit for CVE lookup: {service_name} {version}")
                return cached_data
            
            logger.debug(f"Cache miss for CVE lookup: {service_name} {version}")
            
            # Map common service names to their CVE-searchable equivalents
            service_mapping = {
                "ssh": ["OpenSSH", "SSH"],
                "mysql": ["MySQL", "MariaDB"],
                "ftp": ["vsftpd", "ProFTPD", "Pure-FTPd", "FTP"],
                "http": ["Apache", "nginx", "IIS"],
                "https": ["Apache", "nginx", "IIS"],
                "smtp": ["Postfix", "Exim", "Sendmail"],
                "pop3": ["Dovecot", "Courier"],
                "imap": ["Dovecot", "Courier"],
                "telnet": ["Telnet"],
                "snmp": ["SNMP"],
                "dns": ["BIND", "dnsmasq"],
                "ntp": ["NTP", "chrony"]
            }
            
            # Search for CVEs related to the service
            search_terms = []
            
            # Add mapped terms for common services
            service_lower = service_name.lower()
            if service_lower in service_mapping:
                search_terms.extend(service_mapping[service_lower])
            
            # Add original service name and product
            search_terms.append(service_name)
            if product:
                search_terms.append(product)
            
            # Try different search strategies
            cve_data = None
            for term in search_terms:
                cve_data = await self._search_cves(term, version)
                if cve_data:
                    logger.info(f"Found CVE data for {service_name} using search term: {term}")
                    break
            
            # Cache the result (even if None to avoid repeated API calls)
            if cve_data:
                self.cache.set_cve_data(service_name, version, product, cve_data)
                logger.debug(f"Cached CVE data for: {service_name} {version}")
            else:
                # Cache empty result for a shorter time to avoid repeated failed lookups
                empty_result = {"no_cve_found": True, "searched_at": asyncio.get_event_loop().time()}
                self.cache.set_cve_data(service_name, version, product, empty_result)
            
            return cve_data
            
        except Exception as e:
            logger.error(f"CVE lookup failed for {service_name} {version}: {e}")
            return None
    
    async def _search_cves(self, keyword: str, version: str = "") -> Optional[Dict]:
        """Search CVEs by keyword"""
        try:
            session = await self._get_session()
            
            # Build search URL
            params = {
                "keywordSearch": keyword,
                "resultsPerPage": 5  # Limit results
            }
            
            if version:
                params["keywordSearch"] += f" {version}"
            
            async with session.get(self.nvd_base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    vulnerabilities = data.get("vulnerabilities", [])
                    if vulnerabilities:
                        # Return the most relevant (first) CVE
                        cve_item = vulnerabilities[0]
                        return self._parse_cve_data(cve_item)
                
                elif response.status == 429:  # Rate limited
                    logger.warning("NVD API rate limit exceeded")
                    await asyncio.sleep(1)
                
                return None
                
        except Exception as e:
            logger.error(f"CVE search failed: {e}")
            return None
    
    def _parse_cve_data(self, cve_item: Dict) -> Dict:
        """Parse CVE data from NVD response"""
        try:
            cve = cve_item.get("cve", {})
            cve_id = cve.get("id", "")
            
            # Extract CVSS score
            cvss_score = None
            severity = "Unknown"
            
            metrics = cve.get("metrics", {})
            
            # Try CVSS v3.1 first, then v3.0, then v2.0
            for version in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
                if version in metrics and metrics[version]:
                    metric = metrics[version][0]  # Take first metric
                    cvss_data = metric.get("cvssData", {})
                    cvss_score = cvss_data.get("baseScore")
                    
                    # Determine severity based on score
                    if cvss_score:
                        if cvss_score >= 9.0:
                            severity = "Critical"
                        elif cvss_score >= 7.0:
                            severity = "High"
                        elif cvss_score >= 4.0:
                            severity = "Medium"
                        else:
                            severity = "Low"
                    break
            
            # Extract description
            descriptions = cve.get("descriptions", [])
            description = ""
            for desc in descriptions:
                if desc.get("lang") == "en":
                    description = desc.get("value", "")
                    break
            
            return {
                "cve_id": cve_id,
                "cvss_score": cvss_score,
                "severity": severity,
                "description": description,
                "published_date": cve.get("published", ""),
                "last_modified": cve.get("lastModified", ""),
                "nvd_url": f"https://nvd.nist.gov/vuln/detail/{cve_id}"
            }
            
        except Exception as e:
            logger.error(f"Error parsing CVE data: {e}")
            return {}
    
    async def get_cve_details(self, cve_id: str) -> Optional[Dict]:
        """Get detailed information for a specific CVE with caching"""
        try:
            # Check cache first
            cached_details = self.cache.get_cve_details(cve_id)
            if cached_details:
                logger.debug(f"Cache hit for CVE details: {cve_id}")
                return cached_details
            
            logger.debug(f"Cache miss for CVE details: {cve_id}")
            
            session = await self._get_session()
            
            url = f"{self.nvd_base_url}"
            params = {"cveId": cve_id}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    vulnerabilities = data.get("vulnerabilities", [])
                    
                    if vulnerabilities:
                        cve_details = self._parse_cve_data(vulnerabilities[0])
                        
                        # Cache the details
                        if cve_details:
                            self.cache.set_cve_details(cve_id, cve_details)
                            logger.debug(f"Cached CVE details for: {cve_id}")
                        
                        return cve_details
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get CVE details for {cve_id}: {e}")
            return None
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None