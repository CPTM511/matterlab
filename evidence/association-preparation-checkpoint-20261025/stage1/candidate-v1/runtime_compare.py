"""Type-sensitive saved-runtime comparisons; no model imports or inference."""
from copy import deepcopy
import json

CAPABILITY_PREFIX = '  - CPU capability usage: '

def typed_equal(left, right):
    return json.dumps(left, sort_keys=True, allow_nan=False, separators=(',', ':')) == json.dumps(right, sort_keys=True, allow_nan=False, separators=(',', ':'))

def capability_line(runtime):
    if not isinstance(runtime, dict) or not isinstance(runtime.get('torch_build'), str):
        raise ValueError('Malformed runtime/build description')
    lines = runtime['torch_build'].splitlines()
    matches = [x for x in lines if 'CPU capability usage:' in x]
    if len(matches) != 1 or not matches[0].startswith(CAPABILITY_PREFIX) or matches[0][len(CAPABILITY_PREFIX):] != runtime.get('cpu_capability'):
        raise ValueError('Missing, duplicate or inconsistent capability line')
    return matches[0]

def compare_runtime(left, right, *, dispatch_contrast=False):
    try:
        if not isinstance(left, dict) or not isinstance(right, dict) or set(left) != set(right):
            raise ValueError('Runtime field set differs')
        a, b = deepcopy(left), deepcopy(right)
        lines = [capability_line(a), capability_line(b)]
        for x in (a, b):
            if not isinstance(x['condition'], str):
                raise ValueError('Condition label must be a string')
            x.pop('condition')
        if dispatch_contrast:
            for x, line in zip((a, b), lines, strict=True):
                pair = (x['environment_controls']['ATEN_CPU_CAPABILITY'], x['cpu_capability'])
                if pair not in {(None, 'AVX512'), ('default', 'NO AVX')}:
                    raise ValueError('Unrecognized dispatch intervention')
                x.pop('cpu_capability')
                x['environment_controls'].pop('ATEN_CPU_CAPABILITY')
                x['torch_build'] = x['torch_build'].replace(line + '\n', '', 1)
        return {'passed': typed_equal(a, b), 'rule': 'diagnostic_dispatch' if dispatch_contrast else 'strict_same_condition'}
    except (KeyError, TypeError, ValueError) as error:
        return {'passed': False, 'reason': str(error)}
