#!/usr/bin/env sh
set -e

json_escape() {
    printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

checked_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
os_name=$(uname -s 2>/dev/null || echo "unknown")
platform=$(uname -s 2>/dev/null || echo "unknown")
release=$(uname -r 2>/dev/null || echo "unknown")
version=$(uname -v 2>/dev/null || echo "unknown")
machine=$(uname -m 2>/dev/null || echo "unknown")
processor=$(uname -p 2>/dev/null || echo "unknown")

python_path=$(command -v python 2>/dev/null || true)
python3_path=$(command -v python3 2>/dev/null || true)
git_path=$(command -v git 2>/dev/null || true)
rg_path=$(command -v rg 2>/dev/null || true)
pytest_path=$(command -v pytest 2>/dev/null || true)

python_available=false
python_executable=null
if [ -n "$python_path" ]; then
    python_available=true
    python_executable="\"$(json_escape "$python_path")\""
elif [ -n "$python3_path" ]; then
    python_available=true
    python_executable="\"$(json_escape "$python3_path")\""
fi

git_available=false
git_executable=null
if [ -n "$git_path" ]; then
    git_available=true
    git_executable="\"$(json_escape "$git_path")\""
fi

rg_available=false
rg_executable=null
if [ -n "$rg_path" ]; then
    rg_available=true
    rg_executable="\"$(json_escape "$rg_path")\""
fi

pytest_available=false
pytest_executable=null
if [ -n "$pytest_path" ]; then
    pytest_available=true
    pytest_executable="\"$(json_escape "$pytest_path")\""
fi

printf '{'
printf '"schema_version":1,'
printf '"checked_at":"%s",' "$(json_escape "$checked_at")"
printf '"os":{"name":"%s","platform":"%s","release":"%s","version":"%s","machine":"%s","processor":"%s","is_windows":false,"is_linux":true,"is_macos":false},' \
    "$(json_escape "$os_name")" "$(json_escape "$platform")" "$(json_escape "$release")" "$(json_escape "$version")" "$(json_escape "$machine")" "$(json_escape "$processor")"
printf '"python":{"available":%s,"executable":%s,"version":null,"version_info":[],"implementation":null},' "$python_available" "$python_executable"
printf '"tools":{"git":{"available":%s,"path":%s},"rg":{"available":%s,"path":%s},"pytest":{"available":%s,"path":%s}}' \
    "$git_available" "$git_executable" "$rg_available" "$rg_executable" "$pytest_available" "$pytest_executable"
printf '}\n'

if [ "$python_available" != "true" ]; then
    exit 2
fi
