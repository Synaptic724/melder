import ctypes
import os
from ctypes import wintypes
from typing import Any, Dict, List, Optional, Tuple


_WIN_CPU_SET_TYPE = 0
_ERROR_INSUFFICIENT_BUFFER = 122
_DWORD_PTR = ctypes.c_size_t
_AFFINITY_STATUS_CACHE = None


def _env_bool(name: str, default: bool) -> bool:
    """
    Purpose:
        Parse a boolean environment flag.
    Contract:
        - Accepts truthy values `1,true,yes,on` (case-insensitive).
        - Accepts falsy values `0,false,no,off` (case-insensitive).
        - Falls back to `default` for unset or unrecognized values.
    Args:
        name:
            Environment variable name.
        default:
            Fallback value when parsing fails.
    Returns:
        Parsed boolean value.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _load_winapi() -> Optional[Dict[str, Any]]:
    """
    Purpose:
        Load Windows APIs required for CPU-set discovery and affinity pinning.
    Contract:
        - Returns `None` on non-Windows platforms.
        - Returns callable handles for CPU-set and process-affinity APIs on Windows.
    Returns:
        Optional dictionary containing WinAPI callables.
    """
    if os.name != "nt":
        return None

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    get_system_cpu_set_info = kernel32.GetSystemCpuSetInformation
    get_system_cpu_set_info.argtypes = [
        ctypes.c_void_p,
        wintypes.ULONG,
        ctypes.POINTER(wintypes.ULONG),
        wintypes.HANDLE,
        wintypes.ULONG,
    ]
    get_system_cpu_set_info.restype = wintypes.BOOL

    get_current_process = kernel32.GetCurrentProcess
    get_current_process.argtypes = []
    get_current_process.restype = wintypes.HANDLE

    get_process_affinity_mask = kernel32.GetProcessAffinityMask
    get_process_affinity_mask.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(_DWORD_PTR),
        ctypes.POINTER(_DWORD_PTR),
    ]
    get_process_affinity_mask.restype = wintypes.BOOL

    set_process_affinity_mask = kernel32.SetProcessAffinityMask
    set_process_affinity_mask.argtypes = [wintypes.HANDLE, _DWORD_PTR]
    set_process_affinity_mask.restype = wintypes.BOOL

    return {
        "get_system_cpu_set_info": get_system_cpu_set_info,
        "get_current_process": get_current_process,
        "get_process_affinity_mask": get_process_affinity_mask,
        "set_process_affinity_mask": set_process_affinity_mask,
    }


def _mask_to_cpu_list(mask: int) -> List[int]:
    """
    Purpose:
        Convert a process affinity bitmask into logical CPU indexes.
    Contract:
        - Produces indexes for all set bits within platform pointer width.
        - Returns empty list when no bits are set.
    Args:
        mask:
            Affinity bitmask value.
    Returns:
        Sorted logical CPU indexes represented by the mask.
    """
    bit_count = ctypes.sizeof(_DWORD_PTR) * 8
    cpus: List[int] = []
    for index in range(bit_count):
        if (mask >> index) & 1:
            cpus.append(index)
    return cpus


def _cpu_list_to_mask(cpus: List[int]) -> int:
    """
    Purpose:
        Convert logical CPU indexes into an affinity bitmask.
    Contract:
        - Ignores indexes outside pointer-width bit range.
        - Returns zero when CPU list is empty.
    Args:
        cpus:
            Logical CPU indexes.
    Returns:
        Integer bitmask suitable for `SetProcessAffinityMask`.
    """
    bit_count = ctypes.sizeof(_DWORD_PTR) * 8
    mask = 0
    for cpu in cpus:
        if 0 <= int(cpu) < bit_count:
            mask |= 1 << int(cpu)
    return mask


def _get_process_and_system_affinity(winapi: Dict[str, Any]) -> Optional[Tuple[List[int], List[int]]]:
    """
    Purpose:
        Resolve current process and system affinity CPU lists.
    Contract:
        - Uses `GetProcessAffinityMask` for current process handle.
        - Returns `None` when API call fails.
    Args:
        winapi:
            WinAPI callable dictionary.
    Returns:
        Optional tuple `(process_cpus, system_cpus)`.
    """
    process_mask = _DWORD_PTR(0)
    system_mask = _DWORD_PTR(0)
    ok = winapi["get_process_affinity_mask"](
        winapi["get_current_process"](),
        ctypes.byref(process_mask),
        ctypes.byref(system_mask),
    )
    if not ok:
        return None
    return _mask_to_cpu_list(int(process_mask.value)), _mask_to_cpu_list(int(system_mask.value))


def _read_cpu_set_records(winapi: Dict[str, Any]) -> List[Dict[str, int]]:
    """
    Purpose:
        Read `SYSTEM_CPU_SET_INFORMATION` records from Windows.
    Contract:
        - Returns a list of parsed CPU-set records when available.
        - Returns an empty list when CPU-set information cannot be resolved.
        - Skips unknown record types and malformed records.
    Args:
        winapi:
            WinAPI callable dictionary.
    Returns:
        List of parsed CPU-set dictionaries.
    """
    get_system_cpu_set_info = winapi["get_system_cpu_set_info"]
    get_current_process = winapi["get_current_process"]

    required = wintypes.ULONG(0)
    ok = get_system_cpu_set_info(
        None,
        0,
        ctypes.byref(required),
        get_current_process(),
        0,
    )
    if (not ok) and ctypes.get_last_error() not in {0, _ERROR_INSUFFICIENT_BUFFER}:
        return []
    if required.value <= 0:
        return []

    buffer = (ctypes.c_ubyte * required.value)()
    returned = wintypes.ULONG(0)
    ok = get_system_cpu_set_info(
        ctypes.byref(buffer),
        required,
        ctypes.byref(returned),
        get_current_process(),
        0,
    )
    if not ok or returned.value <= 0:
        return []

    raw = bytes(buffer[: returned.value])
    records: List[Dict[str, int]] = []
    offset = 0
    minimum_cpu_set_record_size = 32

    while offset + 8 <= len(raw):
        record_size = int.from_bytes(raw[offset: offset + 4], "little", signed=False)
        record_type = int.from_bytes(raw[offset + 4: offset + 8], "little", signed=False)

        if record_size <= 0:
            break
        if offset + record_size > len(raw):
            break

        if record_type == _WIN_CPU_SET_TYPE and record_size >= minimum_cpu_set_record_size:
            base = offset + 8
            record = {
                "id": int.from_bytes(raw[base: base + 4], "little", signed=False),
                "group": int.from_bytes(raw[base + 4: base + 6], "little", signed=False),
                "logical_processor_index": int(raw[base + 6]),
                "core_index": int(raw[base + 7]),
                "last_level_cache_index": int(raw[base + 8]),
                "numa_node_index": int(raw[base + 9]),
                "efficiency_class": int(raw[base + 10]),
                "flags": int(raw[base + 11]),
                "scheduling_class": int(raw[base + 12]),
                "allocation_tag": int.from_bytes(raw[base + 16: base + 24], "little", signed=False),
            }
            records.append(record)

        offset += record_size

    return records


def detect_p_core_logical_cpus() -> Tuple[List[int], List[int], Dict[str, Any]]:
    """
    Purpose:
        Detect likely P-core logical CPU indexes using Windows EfficiencyClass.
    Contract:
        - Uses highest observed `efficiency_class` as the P-core class.
        - Restricts discovered indexes to processor group 0 for affinity-mask compatibility.
        - Falls back to all logical CPUs when CPU-set records are unavailable.
    Returns:
        Tuple `(p_core_indexes, other_indexes, debug_info)`.
    """
    winapi = _load_winapi()
    if winapi is None:
        logical_count = os.cpu_count() or 1
        all_indexes = list(range(int(logical_count)))
        return all_indexes, [], {"status": "fallback_all", "reason": "non_windows_platform"}

    records = _read_cpu_set_records(winapi)
    if not records:
        logical_count = os.cpu_count() or 1
        all_indexes = list(range(int(logical_count)))
        return all_indexes, [], {"status": "fallback_all", "reason": "no_cpu_set_records"}

    max_efficiency = max(record["efficiency_class"] for record in records)
    classes = sorted({record["efficiency_class"] for record in records})
    groups = sorted({record["group"] for record in records})

    p_cores = sorted(
        {
            record["logical_processor_index"]
            for record in records
            if record["efficiency_class"] == max_efficiency and record["group"] == 0
        }
    )
    others = sorted(
        {
            record["logical_processor_index"]
            for record in records
            if record["efficiency_class"] != max_efficiency and record["group"] == 0
        }
    )

    debug_info: Dict[str, Any] = {
        "status": "detected",
        "record_count": len(records),
        "max_efficiency_class": max_efficiency,
        "efficiency_classes_present": classes,
        "groups_present": groups,
    }
    if not p_cores:
        logical_count = os.cpu_count() or 1
        p_cores = list(range(int(logical_count)))
        debug_info["status"] = "fallback_all"
        debug_info["reason"] = "no_group0_p_cores_detected"
    return p_cores, others, debug_info


def pin_current_process_to_p_cores(*, strict: bool) -> Dict[str, Any]:
    """
    Purpose:
        Pin current process affinity to detected P-core logical CPUs.
    Contract:
        - Performs no change when platform/tools are unavailable.
        - Intersects detected P-core indexes with current process/system affinity.
        - Returns structured status payload describing request outcome.
    Args:
        strict:
            When `True`, include low-level API failure details in debug payload.
    Returns:
        Structured status dictionary.
    """
    status: Dict[str, Any] = {
        "requested": True,
        "applied": False,
        "strict": strict,
        "platform": os.name,
        "reason": "unknown",
        "p_core_logical_cpus": [],
        "other_logical_cpus": [],
        "selected_affinity": [],
        "process_affinity_before": [],
        "process_affinity_after": [],
        "debug": {},
    }

    winapi = _load_winapi()
    if winapi is None:
        status["reason"] = "non_windows_platform"
        return status

    p_cores, others, debug_info = detect_p_core_logical_cpus()
    status["p_core_logical_cpus"] = p_cores
    status["other_logical_cpus"] = others
    status["debug"] = debug_info
    if not p_cores:
        status["reason"] = "no_detected_p_cores"
        return status

    affinity_lists = _get_process_and_system_affinity(winapi)
    if affinity_lists is None:
        status["reason"] = "get_process_affinity_mask_failed"
        if strict:
            status["debug"] = dict(status["debug"], last_error=ctypes.get_last_error())
        return status

    process_cpus, system_cpus = affinity_lists
    candidate = sorted(set(process_cpus).intersection(set(p_cores)))
    if not candidate:
        candidate = sorted(set(p_cores).intersection(set(system_cpus)))
    if not candidate:
        status["reason"] = "no_candidate_cpus_after_intersection"
        status["process_affinity_before"] = process_cpus
        return status

    status["process_affinity_before"] = process_cpus
    status["selected_affinity"] = candidate

    target_mask = _cpu_list_to_mask(candidate)
    ok = winapi["set_process_affinity_mask"](
        winapi["get_current_process"](),
        _DWORD_PTR(target_mask),
    )
    if not ok:
        status["reason"] = "set_process_affinity_mask_failed"
        if strict:
            status["debug"] = dict(status["debug"], last_error=ctypes.get_last_error())
        return status

    after_lists = _get_process_and_system_affinity(winapi)
    if after_lists is None:
        status["reason"] = "read_back_affinity_failed"
        return status

    process_after, _ = after_lists
    status["process_affinity_after"] = process_after
    status["applied"] = set(process_after) == set(candidate)
    status["reason"] = "pinned" if status["applied"] else "pin_mismatch"
    return status


def maybe_pin_current_process_to_p_cores_from_env() -> Dict[str, Any]:
    """
    Purpose:
        Conditionally pin benchmark process affinity based on env toggles.
    Contract:
        - Reads `DI_PIN_P_CORES` (`0/1`, bool-like values) to enable/disable pinning.
        - Reads `DI_PIN_P_CORES_STRICT` to control strict failure reporting.
        - Returns status payload without raising for expected environment failures.
    Returns:
        Structured affinity status dictionary.
    """
    enabled = _env_bool("DI_PIN_P_CORES", False)
    strict = _env_bool("DI_PIN_P_CORES_STRICT", False)
    if not enabled:
        return {
            "requested": False,
            "applied": False,
            "strict": strict,
            "platform": os.name,
            "reason": "disabled_by_env",
            "p_core_logical_cpus": [],
            "other_logical_cpus": [],
            "selected_affinity": [],
            "process_affinity_before": [],
            "process_affinity_after": [],
            "debug": {},
        }
    return pin_current_process_to_p_cores(strict=strict)


def get_or_apply_p_core_affinity_from_env() -> Dict[str, Any]:
    """
    Purpose:
        Apply env-driven affinity once and reuse status for subsequent calls.
    Contract:
        - First call executes env-driven affinity flow.
        - Later calls return a copy of cached status.
    Returns:
        Structured affinity status dictionary.
    """
    global _AFFINITY_STATUS_CACHE
    if _AFFINITY_STATUS_CACHE is None:
        _AFFINITY_STATUS_CACHE = maybe_pin_current_process_to_p_cores_from_env()
    return dict(_AFFINITY_STATUS_CACHE)
