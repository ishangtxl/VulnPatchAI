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
        self.cache = cve_cache
    
    async def lookup_cve(self, service_name: str, version: str, product: str = "") -> Optional[Dict]:
        """Lookup CVE information for a service with caching"""
        try:
            # Check cache first
            cached_data = self.cache.get_cve_data(service_name, version, product)
            if cached_data:
                # Don't return cached "no_cve_found" results - allow retry
                if not cached_data.get("no_cve_found"):
                    logger.debug(f"Cache hit for CVE lookup: {service_name} {version}")
                    return cached_data
                else:
                    logger.debug(f"Cached negative result found, retrying CVE lookup: {service_name} {version}")
            
            logger.info(f"Performing CVE lookup for: {service_name} {version} {product}")
            
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
                logger.debug(f"Searching CVEs with term: {term}")
                cve_data = await self._search_cves(term, version)
                if cve_data:
                    logger.info(f"Found CVE data for {service_name} using search term: {term}")
                    break
                else:
                    logger.debug(f"No CVE data found for term: {term}")
            
            # Cache the result only if we found something
            if cve_data:
                self.cache.set_cve_data(service_name, version, product, cve_data)
                logger.info(f"Successfully cached CVE data for: {service_name} {version}")
            else:
                logger.warning(f"No CVE data found for {service_name} {version} after trying all search terms")
            
            return cve_data
            
        except Exception as e:
            logger.error(f"CVE lookup failed for {service_name} {version}: {e}")
            return None
    
    async def _search_cves(self, keyword: str, version: str = "") -> Optional[Dict]:
        """Search CVEs by keyword"""
        session = None
        try:
            session = aiohttp.ClientSession()
            
            # Build search URL with improved search terms
            search_query = keyword
            if version:
                search_query += f" {version}"
            
            params = {
                "keywordSearch": search_query,
                "resultsPerPage": 10  # Increase results for better matching
            }
            
            logger.debug(f"NVD API request: {self.nvd_base_url} with params: {params}")
            
            async with session.get(self.nvd_base_url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                logger.debug(f"NVD API response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"NVD API response data keys: {list(data.keys())}")
                    
                    vulnerabilities = data.get("vulnerabilities", [])
                    logger.debug(f"Found {len(vulnerabilities)} vulnerabilities")
                    
                    if vulnerabilities:
                        # Return the most relevant (first) CVE
                        cve_item = vulnerabilities[0]
                        parsed_data = self._parse_cve_data(cve_item)
                        logger.debug(f"Parsed CVE data: {parsed_data}")
                        return parsed_data
                
                elif response.status == 429:  # Rate limited
                    logger.warning("NVD API rate limit exceeded, waiting...")
                    await asyncio.sleep(2)
                elif response.status == 403:
                    logger.error("NVD API access forbidden - check API key")
                else:
                    logger.warning(f"NVD API returned status: {response.status}")
                    response_text = await response.text()
                    logger.debug(f"Response content: {response_text[:500]}")
                
                return None
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout during CVE search for: {keyword}")
            return None
        except Exception as e:
            logger.error(f"CVE search failed for {keyword}: {e}")
            return None
        finally:
            if session:
                await session.close()
    
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
        session = None
        try:
            # Check cache first
            cached_details = self.cache.get_cve_details(cve_id)
            if cached_details:
                logger.debug(f"Cache hit for CVE details: {cve_id}")
                return cached_details
            
            logger.debug(f"Cache miss for CVE details: {cve_id}")
            
            session = aiohttp.ClientSession()
            
            url = f"{self.nvd_base_url}"
            params = {"cveId": cve_id}
            
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
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
        finally:
            if session:
                await session.close()
