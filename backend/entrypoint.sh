#!/bin/sh
# Set up Oracle environment
ORACLE_DIR=$(ls -d /usr/lib/oracle/*/client64 2>/dev/null | head -1)
if [ -n "$ORACLE_DIR" ]; then
  export ORACLE_HOME="$ORACLE_DIR"
  # Include standard library paths for system libraries like libaio
  # These paths are where Debian/Ubuntu store system libraries
  # Prepend to existing LD_LIBRARY_PATH if set, otherwise create new
  if [ -n "$LD_LIBRARY_PATH" ]; then
    export LD_LIBRARY_PATH="$ORACLE_DIR/lib:/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
  else
    export LD_LIBRARY_PATH="$ORACLE_DIR/lib:/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu"
  fi
  export PATH="$ORACLE_DIR/bin:$PATH"
fi
# Ensure standard library paths are always in LD_LIBRARY_PATH even if ORACLE_DIR not found
if [ -z "$LD_LIBRARY_PATH" ] || [ -z "$(echo $LD_LIBRARY_PATH | grep -o '/lib/x86_64-linux-gnu')" ]; then
  if [ -n "$LD_LIBRARY_PATH" ]; then
    export LD_LIBRARY_PATH="/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
  else
    export LD_LIBRARY_PATH="/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu"
  fi
fi
if [ $# -eq 0 ]; then
  exec /bin/sh
else
  exec "$@"
fi
