#!/usr/bin/env bash
# ============================================================
# AWESOME-GRIZZLY-V1 - Installation Script (Linux/macOS)
# ============================================================
set -euo pipefail

# Colors
RED='\033[1;31m'
ORANGE='\033[1;33m'
GREEN='\033[1;32m'
CYAN='\033[1;36m'
WHITE='\033[1;37m'
DIM='\033[2m'
RESET='\033[0m'

# Metadata
VERSION="1.0.0"
NAME="AWESOME-GRIZZLY-V1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================================
# HELPERS
# ============================================================
banner() {
    clear || true
    echo -e "${RED}"
    cat <<'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║        🐻 AWESOME-GRIZZLY-V1 - INSTALLER                                    ║
║        Ultimate Cyber Command & Control Platform                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${RESET}"
}

log_info()    { echo -e "${CYAN}[INFO]${RESET} $*"; }
log_success() { echo -e "${GREEN}[ OK ]${RESET} $*"; }
log_warn()    { echo -e "${ORANGE}[WARN]${RESET} $*"; }
log_error()   { echo -e "${RED}[FAIL]${RESET} $*"; }

# ============================================================
# DETECT OS / PACKAGE MANAGER
# ============================================================
detect_os() {
    OS="unknown"
    DISTRO="unknown"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt-get >/dev/null 2>&1; then DISTRO="debian";
        elif command -v dnf >/dev/null 2>&1; then DISTRO="fedora";
        elif command -v yum >/dev/null 2>&1; then DISTRO="rhel";
        elif command -v pacman >/dev/null 2>&1; then DISTRO="arch";
        elif command -v apk >/dev/null 2>&1; then DISTRO="alpine";
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    fi
    log_info "Detected OS: $OS ($DISTRO)"
}

# ============================================================
# CHECK PYTHON
# ============================================================
check_python() {
    log_info "Checking Python installation..."
    if command -v python3 >/dev/null 2>&1; then
        PYTHON="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON="python"
    else
        log_error "Python not found. Please install Python 3.7+."
        exit 1
    fi

    PY_VERSION=$($PYTHON -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    log_success "Python $PY_VERSION detected ($PYTHON)"

    # Check version
    if ! $PYTHON -c 'import sys; sys.exit(0 if sys.version_info >= (3,7) else 1)'; then
        log_error "Python 3.7+ required. Found $PY_VERSION."
        exit 1
    fi
}

# ============================================================
# INSTALL SYSTEM PACKAGES
# ============================================================
install_system_packages() {
    log_info "Installing system packages..."
    case "$DISTRO" in
        debian)
            sudo apt-get update -y
            sudo apt-get install -y \
                python3-pip python3-dev python3-venv \
                build-essential libssl-dev libffi-dev \
                nmap curl wget netcat-openbsd dnsutils \
                traceroute whois git unzip libpcap-dev \
                libjpeg-dev zlib1g-dev libfreetype6-dev \
                tesseract-ocr tesseract-ocr-eng
            ;;
        fedora)
            sudo dnf install -y \
                python3-pip python3-devel \
                gcc gcc-c++ openssl-devel libffi-devel \
                nmap curl wget nmap-ncat bind-utils \
                traceroute whois git unzip libpcap-devel \
                libjpeg-turbo-devel zlib-devel freetype-devel
            ;;
        rhel)
            sudo yum install -y epel-release
            sudo yum install -y \
                python3-pip python3-devel \
                gcc gcc-c++ openssl-devel libffi-devel \
                nmap curl wget nmap-ncat bind-utils \
                traceroute whois git unzip libpcap-devel
            ;;
        arch)
            sudo pacman -Sy --noconfirm \
                python-pip python \
                base-devel openssl libffi \
                nmap curl wget gnu-netcat bind \
                traceroute whois git unzip libpcap
            ;;
        alpine)
            sudo apk add --no-cache \
                python3 python3-dev py3-pip \
                build-base openssl-dev libffi-dev \
                nmap curl wget netcat-openbsd bind-tools \
                traceroute whois git unzip libpcap-dev \
                jpeg-dev zlib-dev freetype-dev
            ;;
        *)
            log_warn "Unknown distro. Please install the following manually:"
            log_warn "  nmap curl wget netcat dig traceroute whois git"
            ;;
    esac
    log_success "System packages installed."
}

# ============================================================
# CREATE VIRTUAL ENV & INSTALL PIP PACKAGES
# ============================================================
install_python_packages() {
    log_info "Creating virtual environment..."
    if [ ! -d "venv" ]; then
        $PYTHON -m venv venv
        log_success "Virtual environment created."
    else
        log_info "Virtual environment already exists."
    fi

    # shellcheck disable=SC1091
    source venv/bin/activate

    log_info "Upgrading pip, setuptools, wheel..."
    pip install --upgrade pip setuptools wheel

    if [ -f "requirements.txt" ]; then
        log_info "Installing requirements from requirements.txt..."
        pip install -r requirements.txt
        log_success "Python requirements installed."
    else
        log_warn "requirements.txt not found — installing core packages manually."
        pip install colorama requests psutil paramiko scapy dnspython \
                    Flask Flask-SocketIO Flask-CORS \
                    discord.py telethon slack-sdk selenium \
                    matplotlib numpy reportlab python-docx \
                    pynput pyautogui pyperclip Pillow \
                    python-whois shodan qrcode pyshorteners \
                    cryptography tqdm tabulate rich click
    fi
}

# ============================================================
# SETUP DIRECTORIES
# ============================================================
setup_directories() {
    log_info "Creating configuration directories..."
    mkdir -p .awesome_grizzly_v1/{payloads,scans,phishing_pages,captured_credentials,\
ssh_keys,traffic_logs,keylogs,keylog_screenshots,malware,saas,shodan,c2_logs,\
sessions,temp,web_templates,email_templates,dos_logs,agents,modules,\
network_monitor,keylog_exfil,deployments,domain_hosting,\
reverse_engineering,cracking,docker_scans,tenants,billing,api_keys,\
malware_images,email_composer,threat_monitor,mac_logs,arp_logs,nat_logs,\
platform_logs,custom_phishing,wordlists,bots,remote_exec}
    mkdir -p awesome_grizzly_reports/{pdf_reports,graphics,charts}
    log_success "Directories created."
}

# ============================================================
# VERIFY INSTALLATION
# ============================================================
verify_installation() {
    log_info "Verifying installation..."

    if [ -f "requirement-check.py" ]; then
        # shellcheck disable=SC1091
        source venv/bin/activate
        python requirement-check.py || true
    fi

    log_success "Installation complete!"
}

# ============================================================
# PRINT USAGE
# ============================================================
print_usage() {
    echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${GREEN}║            🎉 INSTALLATION SUCCESSFUL! 🎉                     ║${RESET}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${RESET}"
    echo -e ""
    echo -e "${CYAN}To start AWESOME-GRIZZLY-V1:${RESET}"
    echo -e "  ${WHITE}source venv/bin/activate${RESET}"
    echo -e "  ${WHITE}python3 awesome_grizzly.py${RESET}"
    echo -e ""
    echo -e "${CYAN}To run tests:${RESET}"
    echo -e "  ${WHITE}python3 test-commands.py${RESET}"
    echo -e ""
    echo -e "${CYAN}To re-check requirements:${RESET}"
    echo -e "  ${WHITE}python3 requirement-check.py${RESET}"
    echo -e ""
    echo -e "${ORANGE}⚠️  For full functionality, run with sudo:${RESET}"
    echo -e "  ${WHITE}sudo -E venv/bin/python awesome_grizzly.py${RESET}"
    echo -e ""
}

# ============================================================
# MAIN
# ============================================================
main() {
    banner
    cd "$SCRIPT_DIR"

    detect_os
    check_python

    if [[ "${SKIP_SYSTEM:-0}" != "1" ]]; then
        install_system_packages
    fi

    install_python_packages
    setup_directories
    verify_installation
    print_usage
}

main "$@"
