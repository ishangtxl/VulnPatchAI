#!/usr/bin/env python3
"""
Test script to verify command generation for vulnerabilities
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.command_templates import CommandTemplates
import json

def test_command_templates():
    """Test command template generation"""
    print("Testing command templates...")
    
    # Test SSH commands
    ssh_commands = CommandTemplates.get_ssh_commands()
    print(f"\nSSH Commands ({len(ssh_commands)} commands):")
    for cmd in ssh_commands:
        print(f"  - {cmd['title']} ({cmd['os']})")
        print(f"    Command: {cmd['command']}")
        print(f"    Sudo: {cmd['requires_sudo']}, Destructive: {cmd['is_destructive']}")
    
    # Test MySQL commands
    mysql_commands = CommandTemplates.get_mysql_commands()
    print(f"\nMySQL Commands ({len(mysql_commands)} commands):")
    for cmd in mysql_commands:
        print(f"  - {cmd['title']} ({cmd['os']})")
    
    # Test service-based lookup
    print("\nTesting service-based lookup:")
    test_services = ["ssh", "mysql", "ftp", "apache", "nginx", "unknown_service"]
    
    for service in test_services:
        commands = CommandTemplates.get_commands_for_service(service)
        print(f"  {service}: {len(commands)} commands")
    
    print("\nCommand template test completed successfully!")

if __name__ == "__main__":
    test_command_templates()