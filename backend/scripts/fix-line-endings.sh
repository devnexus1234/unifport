#!/usr/bin/env bash
# Fix line endings for all shell scripts
set -e

cd "$(dirname "$0")"
echo "Fixing line endings for shell scripts..."

for script in *.sh; do
    if [ -f "$script" ]; then
        # Remove all CR characters
        python3 -c "
import sys
with open('$script', 'rb') as f:
    data = f.read()
data = data.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
with open('$script', 'wb') as f:
    f.write(data)
"
        chmod +x "$script"
        echo "✓ Fixed $script"
    fi
done

echo "All scripts fixed!"
