import math


def numeric(est, act):
    estimated = []
    actual = []
    for e, a in zip(est, act):
        try:
            x = float(e)
            y = float(a)
            estimated.append(x)
            actual.append(y)
        except:
            pass
    return (estimated, actual)
    
def mbe(est, act):
    est, act = numeric(est, act)
    error = []
    for e, a in zip(est, act):
        error.append(e - a)
    if len(error) > 0:
        return sum(error) / float(len(error))
    else:
        return None
    
def mape(est, act):
    est, act = numeric(est, act)
    error = []
    for e, a in zip(est, act):
        try:
            error.append(abs(e - a) / e)
        except:
            pass
    if len(error) > 0:
        return sum(error) / float(len(error))
    else:
        return None

def rmse(est, act):
    est, act = numeric(est, act)
    error = [(e - a)**2 for e, a in zip(est, act)]
    if len(error) > 0:
        return math.sqrt(sum(error) / float(len(error)))
    else:
        return None

def cvrmse(est, act):
    est, act = numeric(est, act)
    try:
        error = rmse(est, act)
        abar = sum(act) / float(len(act))
        return error / abar * 100.0
    except:
        return None
    
def nmbe(est, act):
    est, act = numeric(est, act)
    error = mbe(est, act)
    try:
        abar = sum(act) / float(len(act))
        return error / abar * 100.0
    except:
        return None

def pae(est, act, lo, hi):
    error = []
    for e, a, l, h in zip(est, act, lo, hi):
        try:
            error.append(abs(e - a) / float(h - l) * 100.0)
        except:
            pass
    return error


