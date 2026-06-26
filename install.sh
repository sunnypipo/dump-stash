#!/usr/bin/env bash
set -euo pipefail

# ── colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# ── checks ────────────────────────────────────────────────────────────────────
check_environment() {
    if [[ ! -f /etc/debian_version ]]; then
        error "This script is for proot-ubuntu only."
    fi

    if [[ "$(whoami)" == "root" ]]; then
        warn "Running as root (expected inside proot)."
    fi
}

# ── system deps ───────────────────────────────────────────────────────────────
install_system_deps() {
    info "Updating apt..."
    apt update

    info "Upgrading existing packages..."
    apt upgrade -y

    info "Installing system dependencies..."
    apt install -y \
        curl \
        git \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-fil \
        pandoc \
        ghostscript \
        python3 \
        python3-venv
    # Note: python3-pip is intentionally skipped.
    # pip is bootstrapped inside the venv via ensurepip (more reliable on
    # minimal Ubuntu images where python3-pip may be missing or broken).
}

# ── python venv ───────────────────────────────────────────────────────────────
setup_venv() {
    info "Creating virtual environment..."
    python3 -m venv .venv

    info "Bootstrapping pip inside venv..."
    .venv/bin/python -m ensurepip --upgrade

    info "Upgrading pip..."
    .venv/bin/pip install --upgrade pip

    info "Installing Python dependencies..."
    .venv/bin/pip install -r requirements.txt
}

# ── folders ───────────────────────────────────────────────────────────────────
setup_folders() {
    info "Creating folders..."
    mkdir -p dump output
}

# ── main ──────────────────────────────────────────────────────────────────────
main() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  dump-stash installer"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo

    check_environment
    install_system_deps
    setup_venv
    setup_folders

    echo
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  Done! Run with:${NC}"
    echo -e "${GREEN}  source .venv/bin/activate${NC}"
    echo -e "${GREEN}  python stash.py${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

main "$@"
