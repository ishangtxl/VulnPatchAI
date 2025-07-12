"""
Nmap XML Parser Service
"""
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NmapXMLParser:
    """Parser for Nmap XML scan results"""
    
    def __init__(self):
        self.parsed_data = {}
    
    def parse_xml_file(self, xml_content: str) -> Dict:
        """Parse Nmap XML content and extract vulnerability data"""
        try:
            root = ET.fromstring(xml_content)
            
            # Extract scan info
            scan_info = self._extract_scan_info(root)
            
            # Extract hosts and services
            hosts = self._extract_hosts(root)
            
            # Extract services and potential vulnerabilities
            services = self._extract_services(hosts)
            
            return {
                "scan_info": scan_info,
                "hosts": hosts,
                "services": services,
                "total_hosts": len(hosts),
                "total_services": len(services),
                "parsed_at": datetime.utcnow().isoformat()
            }
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            raise ValueError(f"Invalid XML format: {e}")
        except Exception as e:
            logger.error(f"Unexpected error parsing XML: {e}")
            raise ValueError(f"Error parsing XML: {e}")
    
    def _extract_scan_info(self, root: ET.Element) -> Dict:
        """Extract scan metadata"""
        scan_info = {
            "scanner": root.get("scanner", "nmap"),
            "version": root.get("version", ""),
            "start_time": root.get("start", ""),
            "args": root.get("args", "")
        }
        
        # Extract run stats
        runstats = root.find("runstats")
        if runstats is not None:
            finished = runstats.find("finished")
            if finished is not None:
                scan_info["end_time"] = finished.get("time", "")
                scan_info["elapsed"] = finished.get("elapsed", "")
        
        return scan_info
    
    def _extract_hosts(self, root: ET.Element) -> List[Dict]:
        """Extract host information"""
        hosts = []
        
        for host in root.findall("host"):
            host_data = {
                "state": host.find("status").get("state") if host.find("status") is not None else "unknown",
                "addresses": [],
                "hostnames": [],
                "ports": []
            }
            
            # Extract addresses
            for address in host.findall("address"):
                host_data["addresses"].append({
                    "addr": address.get("addr"),
                    "addrtype": address.get("addrtype")
                })
            
            # Extract hostnames
            hostnames = host.find("hostnames")
            if hostnames is not None:
                for hostname in hostnames.findall("hostname"):
                    host_data["hostnames"].append({
                        "name": hostname.get("name"),
                        "type": hostname.get("type")
                    })
            
            # Extract ports
            ports = host.find("ports")
            if ports is not None:
                for port in ports.findall("port"):
                    port_data = self._extract_port_info(port)
                    if port_data:
                        host_data["ports"].append(port_data)
            
            hosts.append(host_data)
        
        return hosts
    
    def _extract_port_info(self, port: ET.Element) -> Optional[Dict]:
        """Extract port and service information"""
        port_data = {
            "port": int(port.get("portid", 0)),
            "protocol": port.get("protocol", "tcp"),
            "state": "",
            "service": {}
        }
        
        # Extract state
        state = port.find("state")
        if state is not None:
            port_data["state"] = state.get("state", "")
        
        # Extract service info
        service = port.find("service")
        if service is not None:
            port_data["service"] = {
                "name": service.get("name", ""),
                "product": service.get("product", ""),
                "version": service.get("version", ""),
                "extrainfo": service.get("extrainfo", ""),
                "method": service.get("method", ""),
                "conf": service.get("conf", "")
            }
        
        # Extract script results (for vulnerability detection)
        scripts = port.findall("script")
        if scripts:
            port_data["scripts"] = []
            for script in scripts:
                script_data = {
                    "id": script.get("id", ""),
                    "output": script.get("output", "")
                }
                port_data["scripts"].append(script_data)
        
        return port_data if port_data["state"] == "open" else None
    
    def _extract_services(self, hosts: List[Dict]) -> List[Dict]:
        """Extract and consolidate service information"""
        services = []
        
        for host in hosts:
            host_ip = host["addresses"][0]["addr"] if host["addresses"] else "unknown"
            
            for port in host["ports"]:
                service_data = {
                    "host": host_ip,
                    "port": port["port"],
                    "protocol": port["protocol"],
                    "service_name": port["service"].get("name", "unknown"),
                    "product": port["service"].get("product", ""),
                    "version": port["service"].get("version", ""),
                    "extrainfo": port["service"].get("extrainfo", ""),
                    "state": port["state"],
                    "scripts": port.get("scripts", [])
                }
                
                # Identify potential vulnerabilities based on service info
                service_data["potential_vulnerabilities"] = self._identify_vulnerabilities(service_data)
                
                services.append(service_data)
        
        return services
    
    def _identify_vulnerabilities(self, service: Dict) -> List[Dict]:
        """Identify potential vulnerabilities based on service information"""
        vulnerabilities = []
        
        # Check for outdated versions (simplified logic)
        service_name = service.get("service_name", "").lower()
        version = service.get("version", "")
        product = service.get("product", "")
        
        # Common vulnerable services patterns
        vulnerable_patterns = {
            "ssh": {"versions": ["OpenSSH 7.4", "OpenSSH 6.6"], "severity": "Medium"},
            "http": {"versions": ["Apache 2.2", "nginx 1.10"], "severity": "High"},
            "ftp": {"versions": ["vsftpd 2.3.4"], "severity": "Critical"},
            "telnet": {"versions": ["*"], "severity": "High"},  # Telnet is inherently insecure
            "smtp": {"versions": ["Postfix 2.8"], "severity": "Medium"},
            "mysql": {"versions": ["MySQL 5.5"], "severity": "High"},
            "postgresql": {"versions": ["PostgreSQL 9.3"], "severity": "Medium"}
        }
        
        # Check against known vulnerable patterns
        if service_name in vulnerable_patterns:
            pattern = vulnerable_patterns[service_name]
            
            # Check if version matches vulnerable versions
            is_vulnerable = False
            if "*" in pattern["versions"]:  # All versions vulnerable
                is_vulnerable = True
            elif version:
                for vuln_version in pattern["versions"]:
                    if vuln_version.lower() in f"{product} {version}".lower():
                        is_vulnerable = True
                        break
            
            if is_vulnerable:
                vulnerabilities.append({
                    "type": "outdated_version",
                    "severity": pattern["severity"],
                    "description": f"Potentially vulnerable {service_name} service detected",
                    "recommendation": f"Update {service_name} to the latest version",
                    "cve_candidates": []  # Will be populated by CVE lookup
                })
        
        # Check script results for vulnerability indicators
        for script in service.get("scripts", []):
            script_id = script.get("id", "")
            if "vuln" in script_id or "cve" in script_id:
                vulnerabilities.append({
                    "type": "script_detection",
                    "severity": "Unknown",
                    "description": f"Vulnerability detected by script: {script_id}",
                    "recommendation": "Review script output and apply appropriate patches",
                    "script_output": script.get("output", ""),
                    "cve_candidates": []
                })
        
        return vulnerabilities