#!/usr/bin/env sh
set -e

json_escape() {
    printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

json_string() {
    if [ -n "$1" ]; then
        printf '"%s"' "$(json_escape "$1")"
    else
        printf 'null'
    fi
}

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" >/dev/null 2>&1 && pwd)
repo_root_arg=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        --repo-root|-r)
            shift
            repo_root_arg=${1:-}
            ;;
        *)
            repo_root_arg=$1
            ;;
    esac
    shift || break
done

repo_root=${repo_root_arg:-"$script_dir/../../../.."}
repo_root_exists=false
if [ -n "$repo_root" ] && [ -d "$repo_root" ]; then
    repo_root_exists=true
    repo_root=$(CDPATH= cd -- "$repo_root" >/dev/null 2>&1 && pwd)
fi

context_compass_root="$repo_root/context_compass"
context_compass_exists=false
if [ "$repo_root_exists" = "true" ] && [ -d "$context_compass_root" ]; then
    context_compass_exists=true
fi

active_env_root="$context_compass_root/system/installation/environments/active_environments/linux"
active_env_exists=false
active_env_path=""
if [ "$context_compass_exists" = "true" ] && [ -d "$active_env_root" ]; then
    active_env_exists=true
    for candidate in "$active_env_root"/context_compass_py*; do
        if [ -d "$candidate" ]; then
            active_env_path=$candidate
            break
        fi
    done
fi

active_env_python_exists=false
active_env_python_path=""
if [ -n "$active_env_path" ]; then
    candidate="$active_env_path/bin/python"
    if [ -x "$candidate" ]; then
        active_env_python_exists=true
        active_env_python_path="$candidate"
    fi
fi

system_db_path="$context_compass_root/system/storage/sqlite/system.db"
user_db_path="$context_compass_root/system/storage/sqlite/user.db"
system_db_exists=false
user_db_exists=false
if [ "$context_compass_exists" = "true" ] && [ -f "$system_db_path" ]; then
    system_db_exists=true
fi
if [ "$context_compass_exists" = "true" ] && [ -f "$user_db_path" ]; then
    user_db_exists=true
fi

system_ready=false
if [ "$context_compass_exists" = "true" ] && [ "$system_db_exists" = "true" ] && [ "$user_db_exists" = "true" ]; then
    system_ready=true
fi

checked_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
os_name=$(uname -s 2>/dev/null || echo "unknown")
platform=$(uname -s 2>/dev/null || echo "unknown")
release=$(uname -r 2>/dev/null || echo "unknown")
version=$(uname -v 2>/dev/null || echo "unknown")
machine=$(uname -m 2>/dev/null || echo "unknown")
processor=$(uname -p 2>/dev/null || echo "unknown")

is_linux=false
is_macos=false
case "$os_name" in
    Linux) is_linux=true ;;
    Darwin) is_macos=true ;;
esac

python_path=$(command -v python 2>/dev/null || true)
python3_path=$(command -v python3 2>/dev/null || true)
git_path=$(command -v git 2>/dev/null || true)
rg_path=$(command -v rg 2>/dev/null || true)
pytest_path=$(command -v pytest 2>/dev/null || true)

python_available=false
python_executable=null
if [ -n "$python_path" ]; then
    python_available=true
    python_executable=$(json_string "$python_path")
elif [ -n "$python3_path" ]; then
    python_available=true
    python_executable=$(json_string "$python3_path")
fi

git_available=false
git_executable=null
if [ -n "$git_path" ]; then
    git_available=true
    git_executable=$(json_string "$git_path")
fi

rg_available=false
rg_executable=null
if [ -n "$rg_path" ]; then
    rg_available=true
    rg_executable=$(json_string "$rg_path")
fi

pytest_available=false
pytest_executable=null
if [ -n "$pytest_path" ]; then
    pytest_available=true
    pytest_executable=$(json_string "$pytest_path")
fi

printf '{'
printf '"schema_version":1,'
printf '"checked_at":"%s",' "$(json_escape "$checked_at")"
printf '"os":{"name":"%s","platform":"%s","release":"%s","version":"%s","machine":"%s","processor":"%s","is_windows":false,"is_linux":%s,"is_macos":%s},' \
    "$(json_escape "$os_name")" "$(json_escape "$platform")" "$(json_escape "$release")" "$(json_escape "$version")" "$(json_escape "$machine")" "$(json_escape "$processor")" "$is_linux" "$is_macos"
printf '"python":{"available":%s,"executable":%s,"version":null,"version_info":[],"implementation":null},' "$python_available" "$python_executable"
printf '"tools":{"git":{"available":%s,"path":%s},"rg":{"available":%s,"path":%s},"pytest":{"available":%s,"path":%s}},' \
    "$git_available" "$git_executable" "$rg_available" "$rg_executable" "$pytest_available" "$pytest_executable"
printf '"repo":{"root":%s,"exists":%s,"context_compass":{"path":%s,"exists":%s},' \
    "$(json_string "$repo_root")" "$repo_root_exists" "$(json_string "$context_compass_root")" "$context_compass_exists"
printf '"databases":{"system_db":{"path":%s,"exists":%s},"user_db":{"path":%s,"exists":%s}},"ready":%s},' \
    "$(json_string "$system_db_path")" "$system_db_exists" "$(json_string "$user_db_path")" "$user_db_exists" "$system_ready"
printf '"environment":{"active_env_root":%s,"active_env_exists":%s,"active_env_path":%s,"active_env_python":%s,"active_env_python_exists":%s},' \
    "$(json_string "$active_env_root")" "$active_env_exists" "$(json_string "$active_env_path")" "$(json_string "$active_env_python_path")" "$active_env_python_exists"
printf '"system_ready":%s' "$system_ready"
printf '}\n'

if [ "$python_available" != "true" ]; then
    exit 2
fi
