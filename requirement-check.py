#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   AWESOME-GRIZZLY-V1 - REQUIREMENT CHECKER                                   ║
║   Verifies all dependencies, system tools, and configurations                ║
║                                                                              ║
║   Author: Ian Carter Kulani                                                  ║
║   Version: 1.0.0                                                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import shutil
import platform
import subprocess
import importlib
from pathlib import Path
from datetime import datetime

# ============================================================
# COLOR HANDLING
# ============================================================
try:
    import colorama
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA = True
except ImportError:
    COLORAMA = False

class C:
    if COLORAMA:
        PRIMARY   = Fore.LIGHTRED_EX + Style.BRIGHT
        SECONDARY = Fore.LIGHTYELLOW_EX + Style.BRIGHT
        ACCENT    = Fore.LIGHTWHITE_EX + Style.BRIGHT
        SUCCESS   = Fore.LIGHTGREEN_EX + Style.BRIGHT
        WARNING   = Fore.LIGHTYELLOW_EX + Style.BRIGHT
        ERROR     = Fore.LIGHTRED_EX + Style.BRIGHT
        INFO      = Fore.LIGHTCYAN_EX + Style.BRIGHT
        RESET     = Style.RESET_ALL
        BOLD      = Style.BRIGHT
        DIM       = Style.DIM
    else:
        PRIMARY = SECONDARY = ACCENT = SUCCESS = WARNING = ERROR = INFO = ""
        RESET = BOLD = DIM = ""

# ============================================================
# VERSION
# ============================================================
VERSION = "1.0.0"
NAME = "AWESOME-GRIZZLY-V1"

# ============================================================
# DEPENDENCY DEFINITIONS
# ============================================================

PYTHON_MIN_VERSION = (3, 7)

PYTHON_PACKAGES = {
    # Core
    "colorama": {"version": "0.4.6", "required": True, "category": "Core"},
    "requests": {"version": "2.31.0", "required": True, "category": "Core"},
    "psutil": {"version": "5.9.0", "required": True, "category": "Core"},
    "dateutil": {"version": "2.8.2", "required": False, "category": "Core", "pip_name": "python-dateutil"},
    "yaml": {"version": "6.0", "required": False, "category": "Core", "pip_name": "pyyaml"},
    "dotenv": {"version": "1.0.0", "required": False, "category": "Core", "pip_name": "python-dotenv"},

    # Cryptography
    "cryptography": {"version": "41.0.0", "required": False, "category": "Cryptography"},
    "OpenSSL": {"version": "23.2.0", "required": False, "category": "Cryptography", "pip_name": "pyopenssl"},

    # SSH & Networking
    "paramiko": {"version": "3.3.0", "required": False, "category": "Networking"},
    "scapy": {"version": "2.5.0", "required": False, "category": "Networking"},
    "dns": {"version": "2.4.0", "required": False, "category": "Networking", "pip_name": "dnspython"},
    "netaddr": {"version": "0.9.0", "required": False, "category": "Networking"},
    "netifaces": {"version": "0.11.0", "required": False, "category": "Networking"},

    # Web
    "flask": {"version": "2.3.0", "required": False, "category": "Web", "pip_name": "Flask"},
    "flask_socketio": {"version": "5.3.0", "required": False, "category": "Web", "pip_name": "Flask-SocketIO"},
    "flask_cors": {"version": "4.0.0", "required": False, "category": "Web", "pip_name": "Flask-CORS"},
    "bs4": {"version": "4.12.0", "required": False, "category": "Web", "pip_name": "beautifulsoup4"},
    "lxml": {"version": "4.9.0", "required": False, "category": "Web"},

    # Bots
    "discord": {"version": "2.3.0", "required": False, "category": "Bots", "pip_name": "discord.py"},
    "telethon": {"version": "1.31.0", "required": False, "category": "Bots"},
    "slack_sdk": {"version": "3.23.0", "required": False, "category": "Bots", "pip_name": "slack-sdk"},
    "selenium": {"version": "4.13.0", "required": False, "category": "Bots"},
    "webdriver_manager": {"version": "4.0.0", "required": False, "category": "Bots", "pip_name": "webdriver-manager"},

    # Google
    "google.oauth2": {"version": "2.23.0", "required": False, "category": "Google", "pip_name": "google-auth"},
    "googleapiclient": {"version": "2.100.0", "required": False, "category": "Google", "pip_name": "google-api-python-client"},

    # Visualization
    "matplotlib": {"version": "3.7.0", "required": False, "category": "Visualization"},
    "numpy": {"version": "1.24.0", "required": False, "category": "Visualization"},

    # PDF & Docs
    "reportlab": {"version": "4.0.0", "required": False, "category": "Documents"},
    "docx": {"version": "0.8.11", "required": False, "category": "Documents", "pip_name": "python-docx"},
    "PyPDF2": {"version": "3.0.0", "required": False, "category": "Documents"},

    # Keylogger
    "pynput": {"version": "1.7.6", "required": False, "category": "Input"},
    "pyautogui": {"version": "0.9.54", "required": False, "category": "Input"},
    "pyperclip": {"version": "1.8.2", "required": False, "category": "Input"},
    "PIL": {"version": "10.0.0", "required": False, "category": "Input", "pip_name": "Pillow"},

    # Recon
    "whois": {"version": "0.8.0", "required": False, "category": "Recon", "pip_name": "python-whois"},
    "shodan": {"version": "1.28.0", "required": False, "category": "Recon"},
    "qrcode": {"version": "7.4.2", "required": False, "category": "Recon"},
    "pyshorteners": {"version": "1.0.1", "required": False, "category": "Recon"},

    # CLI
    "tqdm": {"version": "4.66.0", "required": False, "category": "CLI"},
    "tabulate": {"version": "0.9.0", "required": False, "category": "CLI"},
    "rich": {"version": "13.5.0", "required": False, "category": "CLI"},
    "click": {"version": "8.1.0", "required": False, "category": "CLI"},

    # Crypto extra
    "Crypto": {"version": "3.19.0", "required": False, "category": "Cryptography", "pip_name": "pycryptodome"},
    "rsa": {"version": "4.9", "required": False, "category": "Cryptography"},
    "jwt": {"version": "2.8.0", "required": False, "category": "Cryptography", "pip_name": "pyjwt"},
}

SYSTEM_TOOLS = {
    "ping":        {"required": True,  "category": "Network",  "description": "ICMP ping utility"},
    "nmap":        {"required": True,  "category": "Network",  "description": "Network mapper / port scanner"},
    "curl":        {"required": True,  "category": "Network",  "description": "URL transfer tool"},
    "wget":        {"required": True,  "category": "Network",  "description": "File downloader"},
    "nc":          {"required": False, "category": "Network",  "description": "Netcat network utility"},
    "ncat":        {"required": False, "category": "Network",  "description": "Nmap netcat"},
    "dig":         {"required": False, "category": "DNS",      "description": "DNS lookup utility"},
    "nslookup":    {"required": False, "category": "DNS",      "description": "Name server lookup"},
    "traceroute":  {"required": False, "category": "Network",  "description": "Route tracing utility"},
    "tracert":     {"required": False, "category": "Network",  "description": "Windows route tracing"},
    "mtr":         {"required": False, "category": "Network",  "description": "My traceroute"},
    "tcptraceroute": {"required": False, "category": "Network", "description": "TCP traceroute"},
    "ssh":         {"required": False, "category": "SSH",      "description": "OpenSSH client"},
    "ssh-keygen":  {"required": False, "category": "SSH",      "description": "SSH key generator"},
    "ssh-keyscan": {"required": False, "category": "SSH",      "description": "SSH host key scanner"},
    "scp":         {"required": False, "category": "SSH",      "description": "Secure copy"},
    "whois":       {"required": False, "category": "Recon",    "description": "WHOIS lookup"},
    "docker":      {"required": False, "category": "Container","description": "Docker engine"},
    "iptables":    {"required": False, "category": "Firewall", "description": "Linux firewall"},
    "fping":       {"required": False, "category": "Network",  "description": "Fast ping utility"},
    "lft":         {"required": False, "category": "Network",  "description": "Layer four traceroute"},
    "tracepath":   {"required": False, "category": "Network",  "description": "Trace path utility"},
    "pathping":    {"required": False, "category": "Network",  "description": "Windows path ping"},
    "hashcat":     {"required": False, "category": "Cracking", "description": "Password cracker"},
    "john":        {"required": False, "category": "Cracking", "description": "John the Ripper"},
    "signal-cli":  {"required": False, "category": "Bots",     "description": "Signal CLI"},
}

OPTIONAL_DIRS = [
    ".awesome_grizzly_v1",
    ".awesome_grizzly_v1/payloads",
    ".awesome_grizzly_v1/scans",
    ".awesome_grizzly_v1/phishing_pages",
    ".awesome_grizzly_v1/captured_credentials",
    ".awesome_grizzly_v1/ssh_keys",
    ".awesome_grizzly_v1/traffic_logs",
    ".awesome_grizzly_v1/keylogs",
    ".awesome_grizzly_v1/keylog_screenshots",
    ".awesome_grizzly_v1/malware",
    ".awesome_grizzly_v1/saas",
    ".awesome_grizzly_v1/shodan",
    ".awesome_grizzly_v1/c2_logs",
    "awesome_grizzly_reports",
    "awesome_grizzly_reports/pdf_reports",
    "awesome_grizzly_reports/graphics",
    "awesome_grizzly_reports/charts",
]

# ============================================================
# CHECK FUNCTIONS
# ============================================================

def banner():
    print(f"""{C.PRIMARY}
╔══════════════════════════════════════════════════════════════════════════════╗
║{C.SECONDARY}        🐻 AWESOME-GRIZZLY-V1 - REQUIREMENT CHECKER v{VERSION}              {C.PRIMARY}║
║{C.ACCENT}        Verifying dependencies, tools, and configurations                  {C.PRIMARY}║
╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}
""")


def check_python_version():
    """Check Python version."""
    print(f"\n{C.PRIMARY}{'='*70}{C.RESET}")
    print(f"{C.PRIMARY}🐍 Python Version Check{C.RESET}")
    print(f"{C.PRIMARY}{'='*70}{C.RESET}")

    current = sys.version_info[:3]
    required = PYTHON_MIN_VERSION
    ok = current >= required

    status = f"{C.SUCCESS}✅ PASS" if ok else f"{C.ERROR}❌ FAIL"
    print(f"  {status}{C.RESET}  Python {current[0]}.{current[1]}.{current[2]} "
          f"(required >= {required[0]}.{required[1]})")
    print(f"  Executable: {sys.executable}")
    print(f"  Platform:   {platform.platform()}")
    return ok


def check_packages():
    """Check Python packages."""
    print(f"\n{C.PRIMARY}{'='*70}{C.RESET}")
    print(f"{C.PRIMARY}📦 Python Package Check{C.RESET}")
    print(f"{C.PRIMARY}{'='*70}{C.RESET}")

    results = {"pass": 0, "fail": 0, "missing": [], "outdated": []}
    categories = {}

    for module_name, info in PYTHON_PACKAGES.items():
        category = info.get("category", "Other")
        categories.setdefault(category, [])

        try:
            mod = importlib.import_module(module_name)
            version = getattr(mod, "__version__", None)
            if version is None:
                # try pkg_resources
                try:
                    import pkg_resources
                    pkg_name = info.get("pip_name", module_name)
                    version = pkg_resources.get_distribution(pkg_name).version
                except Exception:
                    version = "unknown"
            results["pass"] += 1
            categories[category].append((module_name, version, True, info))
        except ImportError:
            results["fail"] += 1
            results["missing"].append(module_name)
            categories[category].append((module_name, None, False, info))

    # Print per category
    for cat, items in categories.items():
        print(f"\n  {C.SECONDARY}[{cat}]{C.RESET}")
        for module_name, version, ok, info in items:
            required = info.get("required", False)
            tag = f"{C.ERROR}REQUIRED{C.RESET}" if required else f"{C.DIM}optional{C.RESET}"
            if ok:
                print(f"    {C.SUCCESS}✅{C.RESET} {module_name:<22} {version:<15} {tag}")
            else:
                marker = f"{C.ERROR}❌{C.RESET}" if required else f"{C.WARNING}⚠️ {C.RESET}"
                print(f"    {marker} {module_name:<22} {'NOT INSTALLED':<15} {tag}")

    # Summary
    print(f"\n  {C.INFO}Summary:{C.RESET} "
          f"{C.SUCCESS}{results['pass']} installed{C.RESET}, "
          f"{C.WARNING}{results['fail']} missing{C.RESET}")

    if results["missing"]:
        print(f"\n  {C.WARNING}Missing packages (install with pip):{C.RESET}")
        print(f"    pip install " + " ".join(results["missing"]))

    return results


def check_system_tools():
    """Check system tools."""
    print(f"\n{C.PRIMARY}{'='*70}{C.RESET}")
    print(f"{C.PRIMARY}🔧 System Tool Check{C.RESET}")
    print(f"{C.PRIMARY}{'='*70}{C.RESET}")

    results = {"pass": 0, "fail": 0, "missing_required": []}
    categories = {}

    for tool, info in SYSTEM_TOOLS.items():
        category = info.get("category", "Other")
        categories.setdefault(category, [])

        path = shutil.which(tool)
        ok = path is not None
        required = info.get("required", False)

        if ok:
            results["pass"] += 1
        else:
            results["fail"] += 1
            if required:
                results["missing_required"].append(tool)

        categories[category].append((tool, path, ok, info))

    for cat, items in categories.items():
        print(f"\n  {C.SECONDARY}[{cat}]{C.RESET}")
        for tool, path, ok, info in items:
            required = info.get("required", False)
            tag = f"{C.ERROR}REQUIRED{C.RESET}" if required else f"{C.DIM}optional{C.RESET}"
            desc = info.get("description", "")
            if ok:
                print(f"    {C.SUCCESS}✅{C.RESET} {tool:<16} {C.DIM}{path}{C.RESET} {tag}")
            else:
                marker = f"{C.ERROR}❌{C.RESET}" if required else f"{C.WARNING}⚠️ {C.RESET}"
                print(f"    {marker} {tool:<16} {C.DIM}{desc}{C.RESET} {tag}")

    print(f"\n  {C.INFO}Summary:{C.RESET} "
          f"{C.SUCCESS}{results['pass']} found{C.RESET}, "
          f"{C.WARNING}{results['fail']} missing{C.RESET}")

    if results["missing_required"]:
        print(f"\n  {C.ERROR}Missing REQUIRED tools: {', '.join(results['missing_required'])}{C.RESET}")
        print(f"  {C.WARNING}Install instructions:{C.RESET}")
        print(f"    Linux:  sudo apt install nmap curl wget netcat-openbsd")
        print(f"    macOS:  brew install nmap curl wget netcat")
        print(f"    Windows: choco install nmap curl wget netcat")

    return results


def check_directories():
    """Check and create required directories."""
    print(f"\n{C.PRIMARY}{'='*70}{C.RESET}")
    print(f"{C.PRIMARY}📁 Directory Check{C.RESET}")
    print(f"{C.PRIMARY}{'='*70}{C.RESET}")

    created = 0
    existing = 0

    for d in OPTIONAL_DIRS:
        p = Path(d)
        if p.exists():
            existing += 1
            print(f"  {C.SUCCESS}✅{C.RESET} {d}")
        else:
            try:
                p.mkdir(parents=True, exist_ok=True)
                created += 1
                print(f"  {C.INFO}📁{C.RESET} {d} {C.DIM}(created){C.RESET}")
            except Exception as e:
                print(f"  {C.ERROR}❌{C.RESET} {d} ({e})")

    print(f"\n  {C.INFO}Summary:{C.RESET} {existing} existing, {created} created")
    return True


def check_network():
    """Check network connectivity."""
    print(f"\n{C.PRIMARY}{'='*70}{C.RESET}")
    print(f"{C.PRIMARY}🌐 Network Check{C.RESET}")
    print(f"{C.PRIMARY}{'='*70}{C.RESET}")

    import socket

    # Local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"  {C.SUCCESS}✅{C.RESET} Local IP: {local_ip}")
    except Exception as e:
        print(f"  {C.WARNING}⚠️ {C.RESET} Local IP: could not determine ({e})")
        local_ip = "127.0.0.1"

    # Hostname
    print(f"  {C.SUCCESS}✅{C.RESET} Hostname: {socket.gethostname()}")

    # DNS resolution
    try:
        ip = socket.gethostbyname("google.com")
        print(f"  {C.SUCCESS}✅{C.RESET} DNS resolution: google.com -> {ip}")
    except Exception as e:
        print(f"  {C.ERROR}❌{C.RESET} DNS resolution failed: {e}")

    # Internet connectivity
    try:
        import urllib.request
        urllib.request.urlopen("https://www.google.com", timeout=5)
        print(f"  {C.SUCCESS}✅{C.RESET} Internet connectivity: OK")
    except Exception as e:
        print(f"  {C.WARNING}⚠️ {C.RESET} Internet connectivity: limited ({e})")

    return True


def check_permissions():
    """Check permissions (root/admin)."""
    print(f"\n{C.PRIMARY}{'='*70}{C.RESET}")
    print(f"{C.PRIMARY}🔐 Permission Check{C.RESET}")
    print(f"{C.PRIMARY}{'='*70}{C.RESET}")

    system = platform.system().lower()
    is_admin = False

    try:
        if system == "windows":
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            is_admin = os.geteuid() == 0
    except Exception:
        pass

    if is_admin:
        print(f"  {C.SUCCESS}✅{C.RESET} Running with elevated privileges (root/admin)")
    else:
        print(f"  {C.WARNING}⚠️ {C.RESET} Running WITHOUT elevated privileges")
        print(f"  {C.DIM}    Some features (raw sockets, iptables) may not work.{C.RESET}")
        print(f"  {C.DIM}    Run with sudo/admin for full functionality.{C.RESET}")

    return is_admin


def check_optional_features():
    """Check optional feature availability."""
    print(f"\n{C.PRIMARY}{'='*70}{C.RESET}")
    print(f"{C.PRIMARY}🎯 Optional Feature Availability{C.RESET}")
    print(f"{C.PRIMARY}{'='*70}{C.RESET}")

    features = {}

    def check(feature_name, condition, hint=""):
        features[feature_name] = condition
        if condition:
            print(f"  {C.SUCCESS}✅{C.RESET} {feature_name}")
        else:
            print(f"  {C.WARNING}⚠️ {C.RESET} {feature_name} {C.DIM}{hint}{C.RESET}")

    # SSH
    try:
        import paramiko  # noqa
        check("SSH Remote Access", True)
    except ImportError:
        check("SSH Remote Access", False, "(pip install paramiko)")

    # Scapy
    try:
        import scapy.all  # noqa
        check("Advanced Packet Crafting (Scapy)", True)
    except ImportError:
        check("Advanced Packet Crafting (Scapy)", False, "(pip install scapy)")

    # Discord
    try:
        import discord  # noqa
        check("Discord Bot Integration", True)
    except ImportError:
        check("Discord Bot Integration", False, "(pip install discord.py)")

    # Telegram
    try:
        import telethon  # noqa
        check("Telegram Bot Integration", True)
    except ImportError:
        check("Telegram Bot Integration", False, "(pip install telethon)")

    # Slack
    try:
        import slack_sdk  # noqa
        check("Slack Bot Integration", True)
    except ImportError:
        check("Slack Bot Integration", False, "(pip install slack-sdk)")

    # Web dashboard
    try:
        import flask  # noqa
        check("Web Dashboard", True)
    except ImportError:
        check("Web Dashboard", False, "(pip install flask)")

    # Keylogger
    try:
        import pynput  # noqa
        check("Keylogger Module", True)
    except ImportError:
        check("Keylogger Module", False, "(pip install pynput)")

    # Charts
    try:
        import matplotlib  # noqa
        check("Chart Generation", True)
    except ImportError:
        check("Chart Generation", False, "(pip install matplotlib)")

    # PDF
    try:
        import reportlab  # noqa
        check("PDF Report Generation", True)
    except ImportError:
        check("PDF Report Generation", False, "(pip install reportlab)")

    # Shodan
    try:
        import shodan  # noqa
        check("Shodan Integration", True)
    except ImportError:
        check("Shodan Integration", False, "(pip install shodan)")

    # WhatsApp
    try:
        import selenium  # noqa
        check("WhatsApp Bot Integration", True)
    except ImportError:
        check("WhatsApp Bot Integration", False, "(pip install selenium)")

    # Signal
    check("Signal Bot Integration", shutil.which("signal-cli") is not None,
          "(install signal-cli)")

    # iMessage (macOS only)
    check("iMessage Integration", platform.system().lower() == "darwin",
          "(macOS only)")

    return features


def check_existing_installation():
    """Check existing AWESOME-GRIZZLY-V1 installation."""
    print(f"\n{C.PRIMARY}{'='*70}{C.RESET}")
    print(f"{C.PRIMARY}🐻 Existing Installation Check{C.RESET}")
    print(f"{C.PRIMARY}{'='*70}{C.RESET}")

    config_dir = Path(".awesome_grizzly_v1")
    if config_dir.exists():
        print(f"  {C.SUCCESS}✅{C.RESET} Config directory exists: {config_dir.absolute()}")

        db_file = config_dir / "awesome_grizzly_v1.db"
        if db_file.exists():
            size = db_file.stat().st_size
            print(f"  {C.SUCCESS}✅{C.RESET} Database found: {size} bytes")

        config_file = config_dir / "config.json"
        if config_file.exists():
            print(f"  {C.SUCCESS}✅{C.RESET} Config file found")
    else:
        print(f"  {C.INFO}ℹ️ {C.RESET} No existing installation found (will be created on first run)")

    return True


def generate_report(results):
    """Generate a JSON report of all checks."""
    report = {
        "tool": NAME,
        "version": VERSION,
        "timestamp": datetime.now().isoformat(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": ".".join(map(str, sys.version_info[:3])),
        },
        "results": results,
    }

    report_path = Path(".awesome_grizzly_v1/requirements_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n{C.INFO}📄 Report saved to: {report_path}{C.RESET}")
    return report


def print_final_summary(py_results, tool_results, features):
    """Print final summary."""
    print(f"\n{C.PRIMARY}{'='*70}{C.RESET}")
    print(f"{C.PRIMARY}📊 FINAL SUMMARY{C.RESET}")
    print(f"{C.PRIMARY}{'='*70}{C.RESET}")

    required_missing = [
        mod for mod, info in PYTHON_PACKAGES.items()
        if info.get("required") and mod in py_results.get("missing", [])
    ]

    required_tools_missing = tool_results.get("missing_required", [])

    all_ok = not required_missing and not required_tools_missing

    if all_ok:
        print(f"\n  {C.SUCCESS}🎉 ALL REQUIRED DEPENDENCIES ARE SATISFIED!{C.RESET}")
        print(f"  {C.SUCCESS}✅ The application should run without issues.{C.RESET}")
    else:
        print(f"\n  {C.WARNING}⚠️  MISSING REQUIRED DEPENDENCIES:{C.RESET}")
        if required_missing:
            print(f"    Python packages: {', '.join(required_missing)}")
            print(f"    {C.DIM}Run: pip install -r requirements.txt{C.RESET}")
        if required_tools_missing:
            print(f"    System tools:    {', '.join(required_tools_missing)}")

    enabled = sum(1 for v in features.values() if v)
    total = len(features)
    print(f"\n  {C.INFO}Optional features: {enabled}/{total} available{C.RESET}")

    print(f"\n  {C.DIM}For full functionality, install optional deps:{C.RESET}")
    print(f"  {C.DIM}pip install -r requirements.txt{C.RESET}")

    return all_ok


def main():
    banner()

    py_ok = check_python_version()
    py_results = check_packages()
    tool_results = check_system_tools()
    check_directories()
    check_network()
    check_permissions()
    features = check_optional_features()
    check_existing_installation()

    report = generate_report({
        "python": py_results,
        "tools": tool_results,
        "features": features,
    })

    all_ok = print_final_summary(py_results, tool_results, features)

    print(f"\n{C.PRIMARY}{'='*70}{C.RESET}\n")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
