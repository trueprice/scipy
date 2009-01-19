"""
Real spectrum tranforms (DCT, DST, MDCT)
"""

__all__ = ['dct']

import numpy as np
from scipy.fftpack import _fftpack

import atexit
atexit.register(_fftpack.destroy_ddct1_cache)
atexit.register(_fftpack.destroy_ddct2_cache)

def dct(x, type=2, n=None, axis=-1, norm=None):
    """
    Return the Discrete Cosine Transform of arbitrary type sequence x.

    Parameters
    ----------
    x : array-like
        input array.
    type : {1, 2, 3}
        type of the DCT (see Notes).
    n : int, optional
        Length of the transform.
    axis : int, optional
        axis over which to compute the transform.
    norm : {None, 'ortho'}
        normalization mode (see Notes).

    Returns
    -------
    y : real ndarray

    Notes
    -----
    For a single dimension array x, dct(x, norm='ortho') is equal to matlab
    dct(x).

    There are theoretically 8 types of the DCT, only the first 3 types are
    implemented in scipy. 'The' DCT generally refers to DCT type 2, and 'the'
    Inverse DCT generally refers to DCT type 3.

    type I
    ~~~~~~
    There are several definitions of the DCT-I; we use the following (for
    norm=None):

    for 0 <= k < N,

                                           N-1
        y[k] = x[0] + (-1)**k x[N-1] + 2 * sum x[n]*cos(pi*k*n/(N-1))
                                           n=0

    type II
    ~~~~~~~
    There are several definitions of the DCT-II; we use the following (for
    norm=None):

                  N-1
        y[k] = 2* sum x[n]*cos(pi*k*(2n+1)/(2*N)), 0 <= k < N.
                  n=0

    If norm='ortho', y[k] is multiplied by a scaling factor f:

        f = sqrt(1/(4*N)) if k = 0
        f = sqrt(1/(2*N)) otherwise

    Which makes the corresponding matrix of coefficients orthonormal (OO' = Id).

    type III
    ~~~~~~~~
    There are several definitions, we use the following (norm=None):

                          N-1
        y[k] = x[0] + 2 * sum x[n]*cos(pi*(k+0.5)*n/N), 0 <= k < N.
                          n=0

    Or (norm='ortho'), for 0 <= k < N:

                                            N-1
        y[k] = x[0] / sqrt(N) + sqrt(1/N) * sum x[n]*cos(pi*(k+0.5)*n/N)
                                            n=0

    The (unnormalized) DCT-III is the inverse of the (unnormalized) DCT-II, up
    to a factor 2*N. The orthonormalized DCT-III is exactly the inverse of the
    orthonormalized DCT-II.

    References
    ----------

    http://en.wikipedia.org/wiki/Discrete_cosine_transform

    'A Fast Cosine Transform in One and Two Dimensions', by J. Makhoul, in IEEE
    Transactions on acoustics, speech and signal processing.
    """
    if type == 1 and norm is not None:
        raise NotImplementedError(
              "Orthonormalization not yet supported for DCT-I")
    return _dct(x, type, n, axis, normalize=norm)

def idct(x, type=2, n=None, axis=-1, norm=None):
    """
    Return the Inverse Discrete Cosine Transform of arbitrary type sequence x.

    Parameters
    ----------
    x : array-like
        input array.
    type : {1, 2, 3}
        type of the IDCT (see Notes).
    n : int, optional
        Length of the transform.
    axis : int, optional
        axis over which to compute the transform.
    norm : {None, 'ortho'}
        normalization mode (see Notes).

    Returns
    -------
    y : real ndarray

    Notes
    -----
    For a single dimension array x, idct(x, norm='ortho') is equal to matlab
    idct(x)

    'The' IDCT is the IDCT of type 2, which is the same as DCT of type 3.

    IDCT of type 1 is the DCT of type 1, IDCT of type 2 is the DCT of type 3,
    and IDCT of type 3 is the DCT of type 2.

    See Also
    --------
    dct
    """
    if type == 1 and norm is not None:
        raise NotImplementedError(
              "Orthonormalization not yet supported for IDCT-I")
    # Inverse/forward type table
    _TP = {1:1, 2:3, 3:2}
    return _dct(x, _TP[type], n, axis, normalize=norm)

def _dct(x, type, n=None, axis=-1, overwrite_x=0, normalize=None):
    """
    Return Discrete Cosine Transform of arbitrary type sequence x.

    Parameters
    ----------
    x : array-like
        input array.
    n : int, optional
        Length of the transform.
    axis : int, optional
        Axis along which the dct is computed. (default=-1)
    overwrite_x : bool, optional
        If True the contents of x can be destroyed. (default=False)

    Returns
    -------
    z : real ndarray

    """
    tmp = np.asarray(x)
    if not np.isrealobj(tmp):
        raise TypeError,"1st argument must be real sequence"

    if n is None:
        n = tmp.shape[axis]
    else:
        raise NotImplemented("Padding/truncating not yet implemented")

    if tmp.dtype == np.double:
        if type == 1:
            f = _fftpack.ddct1
        elif type == 2:
            f = _fftpack.ddct2
        elif type == 3:
            f = _fftpack.ddct3
        else:
            raise ValueError("Type %d not understood" % type)
    elif tmp.dtype == np.float32:
        if type == 1:
            f = _fftpack.dct1
        elif type == 2:
            f = _fftpack.dct2
        elif type == 3:
            f = _fftpack.dct3
        else:
            raise ValueError("Type %d not understood" % type)
    else:
        raise ValueError("dtype %s not supported" % tmp.dtype)

    if normalize:
        if normalize == "ortho":
            nm = 1
        else:
            raise ValueError("Unknown normalize mode %s" % normalize)
    else:
        nm = 0

    if axis == -1 or axis == len(tmp.shape) - 1:
        return f(tmp, n, nm, overwrite_x)
    #else:
    #    raise NotImplementedError("Axis arg not yet implemented")

    tmp = np.swapaxes(tmp, axis, -1)
    tmp = f(tmp, n, nm, overwrite_x)
    return np.swapaxes(tmp, axis, -1)