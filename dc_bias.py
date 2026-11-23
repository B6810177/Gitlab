"""DC bias calculation entry point.

Lab 04's example layout uses ``dc_bias.py`` for the engineering module.
The implementation lives in the ``bjt_bias`` package so the three bias
modes can share helpers; this module re-exports the public functions so
both import paths work.

The Flask route (``app.py``) and the tests import from here.
"""

from bjt_bias.bias import calculate_bias, calculate_emitter, calculate_fixed

__all__ = ["calculate_bias", "calculate_fixed", "calculate_emitter"]
