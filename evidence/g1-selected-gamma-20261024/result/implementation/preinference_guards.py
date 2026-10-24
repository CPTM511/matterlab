"""Additional assertion-only guards before the first forward. No model evaluation."""
import json
from pathlib import Path
from runtime_compare import typed_equal, compare_runtime

REFERENCE = Path('evidence/dispatch-contrast-20261023/C1-default')

def check_hash_record(root, output, name):
    actual = json.loads((output / name).read_text())
    expected = json.loads((root / REFERENCE / name).read_text())
    if not typed_equal(actual, expected):
        raise ValueError('Pre-inference capture/parameter mismatch: ' + name)

def check_runtime(root, output, runtime):
    expected = json.loads((root / REFERENCE / 'runtime.json').read_text())
    result = compare_runtime(runtime, expected)
    (output / 'pre-inference-runtime-check.json').write_text(json.dumps(result, indent=2) + '\n')
    if not result['passed']:
        raise ValueError('Pre-inference full same-condition runtime mismatch')

def check_model_finite(values):
    import numpy as np
    if not values or any(not x.size or not np.isfinite(x).all() for x in values.values()):
        raise ValueError('Empty or nonfinite captured model output')
