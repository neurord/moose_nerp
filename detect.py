import functools
import numpy as np

print('detect values > 0.0')

def arrayize(type):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return np.fromiter(func(*args, **kwargs), type)
        return functools.update_wrapper(wrapper, func)
    return decorator

@arrayize(int)
def detect_peaks(y, min_high_ratio=0.5, P_low=0.5, P_high=0.5, both=False):
    low_i, low = 0, y[0]
    high_i, high = 0, y[0]

    i = (y > 0).argmax() if np.any(y > 0) else len(y) # find True
    while True:
        for i in range(i, len(y)):
            if y[i] < low:
                low_i, low = i, y[i]
            if y[i] > high:
                high_i, high = i, y[i]

            if y[i] - low < (high - low) * P_high:
                break
        else:
            break

        yield high_i
        low_i, low = i, y[i]

        for i in range(i, len(y)):
            if y[i] < low:
                low_i, low = i, y[i]
            if y[i] > high:
                high_i, high = i, y[i]

            if y[i] - low > (high - low) * P_low:
                break
        else:
            break

        if both:
            yield low_i
        high_i, high = i, y[i]
