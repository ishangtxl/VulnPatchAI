"""
Command templates for common vulnerability remediation
"""
from typing import Dict, List, Any

class CommandTemplates:
    """Predefined command templates for common vulnerabilities"""
    
    @staticmethod
    def get_ssh_commands(version: str = "") -> List[Dict[str, Any]]:
        """Get SSH update and hardening commands"""
        return [
            {
                "title": "Update OpenSSH (Ubuntu/Debian)",
                "command": "sudo apt update && sudo apt install openssh-server",
                "os": "ubuntu",
                "description": "Update OpenSSH to the latest available version",
                "requires_sudo": True,
                "is_destructive": False
            },
            {
                "title": "Update OpenSSH (CentOS/RHEL)",
                "command": "sudo yum update openssh-server",
                "os": "centos",
                "description": "Update OpenSSH to the latest available version",
                "requires_sudo": True,
                "is_destructive": False
            },
            {
                "title": "Restart SSH Service (Ubuntu/Debian)",
                "command": "sudo systemctl restart ssh",
                "os": "ubuntu",
                "description": "Restart SSH service to apply updates",
                "requires_sudo": True,
                "is_destructive": False
            },
            {
                "title": "Restart SSH Service (CentOS/RHEL)",
                "command": "sudo systemctl restart sshd",
                "os": "centos",
                "description": "Restart SSH service to apply updates",
                "requires_sudo": True,
                "is_destructive": False
            },
            {
                "title": "Disable Root Login",
                "command": "sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config && sudo systemctl restart ssh",
                "os": "ubuntu",
                "description": "Disable direct root login via SSH for security",
                "requires_sudo": True,
                "is_destructive": True
            },
            {
                "title": "Verify SSH Version",
                "command": "ssh -V",
                "os": "ubuntu",
                "description": "Check the installed SSH version",
                "requires_sudo": False,
                "is_destructive": False
            }
        ]
    
    @staticmethod
    def get_mysql_commands(version: str = "") -> List[Dict[str, Any]]:
        """Get MySQL update and security commands"""
        return [
            {
                "title": "Update MySQL (Ubuntu/Debian)",
                "command": "sudo apt update && sudo apt install mysql-server",
                "os": "ubuntu",
                "description": "Update MySQL to the latest available version",
                "requires_sudo": True,
                "is_destructive": False
            },
            {
                "title": "Update MySQL (CentOS/RHEL)",
                "command": "sudo yum update mysql-server",
                "os": "centos",
                "description": "Update MySQL to the latest available version",
                "requires_sudo": True,
                "is_destructive": False
            },
            {
                "title": "Restart MySQL Service",
                "command": "sudo systemctl restart mysql",
                "os": "ubuntu",
                "description": "Restart MySQL service to apply updates",
                "requires_sudo": True,
                "is_destructive": True
            },
            {
                "title": "Run MySQL Security Script",
                "command": "sudo mysql_secure_installation",
                "os": "ubuntu",
                "description": "Run the MySQL security configuration script",
                "requires_sudo": True,
                "is_destructive": True
            },
            {
                "title": "Check MySQL Version",
                "command": "mysql --version",
                "os": "ubuntu",
                "description": "Verify the installed MySQL version",
                "requires_sudo": False,
                "is_destructive": False
            }
        ]
    
    @staticmethod
    def get_ftp_commands(service: str = "vsftpd") -> List[Dict[str, Any]]:
        """Get FTP service update commands"""
        commands = []
        
        if service.lower() == "vsftpd":
            commands.extend([
                {
                    "title": "Update vsftpd (Ubuntu/Debian)",
                    "command": "sudo apt update && sudo apt install vsftpd",
                    "os": "ubuntu",
                    "description": "Update vsftpd to the latest available version",
                    "requires_sudo": True,
                    "is_destructive": False
                },
                {
                    "title": "Update vsftpd (CentOS/RHEL)",
                    "command": "sudo yum update vsftpd",
                    "os": "centos",
                    "description": "Update vsftpd to the latest available version",
                    "requires_sudo": True,
                    "is_destructive": False
                },
                {
                    "title": "Restart vsftpd Service",
                    "command": "sudo systemctl restart vsftpd",
                    "os": "ubuntu",
                    "description": "Restart vsftpd service to apply updates",
                    "requires_sudo": True,
                    "is_destructive": False
                },
                {
                    "title": "Disable Anonymous FTP",
                    "command": "sudo sed -i 's/anonymous_enable=YES/anonymous_enable=NO/' /etc/vsftpd.conf && sudo systemctl restart vsftpd",
                    "os": "ubuntu",
                    "description": "Disable anonymous FTP access for security",
                    "requires_sudo": True,
                    "is_destructive": True
                }
            ])
        
        return commands
    
    @staticmethod
    def get_web_server_commands(service: str = "apache") -> List[Dict[str, Any]]:
        """Get web server update commands"""
        commands = []
        
        if service.lower() in ["apache", "apache2"]:
            commands.extend([
                {
                    "title": "Update Apache (Ubuntu/Debian)",
                    "command": "sudo apt update && sudo apt install apache2",
                    "os": "ubuntu",
                    "description": "Update Apache to the latest available version",
                    "requires_sudo": True,
                    "is_destructive": False
                },
                {
                    "title": "Update Apache (CentOS/RHEL)",
                    "command": "sudo yum update httpd",
                    "os": "centos",
                    "description": "Update Apache to the latest available version",
                    "requires_sudo": True,
                    "is_destructive": False
                },
                {
                    "title": "Restart Apache Service (Ubuntu)",
                    "command": "sudo systemctl restart apache2",
                    "os": "ubuntu",
                    "description": "Restart Apache service to apply updates",
                    "requires_sudo": True,
                    "is_destructive": True
                },
                {
                    "title": "Restart Apache Service (CentOS)",
                    "command": "sudo systemctl restart httpd",
                    "os": "centos",
                    "description": "Restart Apache service to apply updates",
                    "requires_sudo": True,
                    "is_destructive": True
                }
            ])
        elif service.lower() == "nginx":
            commands.extend([
                {
                    "title": "Update Nginx (Ubuntu/Debian)",
                    "command": "sudo apt update && sudo apt install nginx",
                    "os": "ubuntu",
                    "description": "Update Nginx to the latest available version",
                    "requires_sudo": True,
                    "is_destructive": False
                },
                {
                    "title": "Update Nginx (CentOS/RHEL)",
                    "command": "sudo yum update nginx",
                    "os": "centos",
                    "description": "Update Nginx to the latest available version",
                    "requires_sudo": True,
                    "is_destructive": False
                },
                {
                    "title": "Restart Nginx Service",
                    "command": "sudo systemctl restart nginx",
                    "os": "ubuntu",
                    "description": "Restart Nginx service to apply updates",
                    "requires_sudo": True,
                    "is_destructive": True
                }
            ])
        
        return commands
    
    @staticmethod
    def get_commands_for_service(service_name: str, version: str = "") -> List[Dict[str, Any]]:
        """Get appropriate commands based on service name"""
        service_lower = service_name.lower()
        
        if service_lower in ["ssh", "openssh"]:
            return CommandTemplates.get_ssh_commands(version)
        elif service_lower in ["mysql", "mariadb"]:
            return CommandTemplates.get_mysql_commands(version)
        elif service_lower in ["ftp", "vsftpd", "proftpd"]:
            # Default to vsftpd for generic "ftp"
            ftp_service = "vsftpd" if service_lower == "ftp" else service_lower
            return CommandTemplates.get_ftp_commands(ftp_service)
        elif service_lower in ["http", "https", "apache", "apache2", "nginx"]:
            return CommandTemplates.get_web_server_commands(service_lower)
        else:
            # Return generic update commands
            return [
                {
                    "title": f"Update {service_name} (Ubuntu/Debian)",
                    "command": f"sudo apt update && sudo apt install {service_name}",
                    "os": "ubuntu",
                    "description": f"Update {service_name} to the latest available version",
                    "requires_sudo": True,
                    "is_destructive": False
                },
                {
                    "title": f"Update {service_name} (CentOS/RHEL)",
                    "command": f"sudo yum update {service_name}",
                    "os": "centos",
                    "description": f"Update {service_name} to the latest available version",
                    "requires_sudo": True,
                    "is_destructive": False
                },
                {
                    "title": f"Restart {service_name} Service",
                    "command": f"sudo systemctl restart {service_name}",
                    "os": "ubuntu",
                    "description": f"Restart {service_name} service to apply updates",
                    "requires_sudo": True,
                    "is_destructive": True
                }
            ]