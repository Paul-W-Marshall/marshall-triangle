#!/usr/bin/env bash
# Launch wrapper: ensures the correct libexpat is loaded before Python starts.
#
# Python 3.11.14's pyexpat.so was compiled against expat-2.7.3 (RUNPATH embedded),
# but at runtime a different (older) libexpat.so.1 is resolved first, causing:
#   ImportError: undefined symbol: XML_SetReparseDeferralEnabled
#
# Fix: LD_PRELOAD the exact expat-2.7.3 that pyexpat.so expects so the dynamic
# linker uses it in preference to any other libexpat on the library path.

EXPAT_LIB="/nix/store/sr4cnxyzx24ylxygfk7d81hy4791l8gm-expat-2.7.3/lib/libexpat.so.1"

if [ -f "$EXPAT_LIB" ]; then
    export LD_PRELOAD="${EXPAT_LIB}${LD_PRELOAD:+:$LD_PRELOAD}"
fi

exec uv run python stealth_server.py "$@"
