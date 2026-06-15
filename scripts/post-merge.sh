#!/bin/bash
set -e

export PATH="/root/.nix-profile/bin:/nix/var/nix/profiles/default/bin:$HOME/.nix-profile/bin:$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

uv sync
