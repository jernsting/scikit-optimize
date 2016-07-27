from collections import Iterable
import numbers
import numpy as np

from scipy.optimize import OptimizeResult
from sklearn.utils import check_random_state

from .space import Space


def dummy_minimize(func, dimensions, n_calls=100,
                   x0=None, y0=None, random_state=None):
    """Random search by uniform sampling within the given bounds.

    Parameters
    ----------
    * `func` [callable]:
        Function to minimize. Should take a array of parameters and
        return the function values.

    * `dimensions` [list, shape=(n_dims,)]:
        List of search space dimensions.
        Each search dimension can be defined either as

        - a `(upper_bound, lower_bound)` tuple (for `Real` or `Integer`
          dimensions),
        - a `(upper_bound, lower_bound, "prior")` tuple (for `Real`
          dimensions),
        - as a list of categories (for `Categorical` dimensions), or
        - an instance of a `Dimension` object (`Real`, `Integer` or
          `Categorical`).

    * `n_calls` [int, default=100]:
        Number of calls to `func` to find the minimum.

    * `x0` [list or list of lists or None]:
        Initial input points.
        - If it is a list of lists, use it as a list of input points.
        - If it is a list, use it as a single initial input point.
        - If it is `None`, no initial input points are used.

    * `y0` [list or scalar or None]
        Evaluation of initial input points.
        - If it is a list, then it corresponds to evaluations of the function
          at each element of `x0` : the i-th element of `y0` corresponds
          to the function evaluated at the i-th element of `x0`.
        - If it is a scalar, then it corresponds to the evaluation of the
          function at `x0`.
        - If it is None and `x0` is provided, then the function is evaluated
          at each element of `x0`.

    * `random_state` [int, RandomState instance, or None (default)]:
        Set random state to something other than None for reproducible
        results.

    Returns
    -------
    * `res` [`OptimizeResult`, scipy object]:
        The optimization result returned as a OptimizeResult object.
        Important attributes are:

        - `x` [list]: location of the minimum.
        - `fun` [float]: function value at the minimum.
        - `x_iters` [list of lists]: location of function evaluation for each
           iteration.
        - `func_vals` [array]: function value for each iteration.
        - `space` [Space]: the optimisation space.

        For more details related to the OptimizeResult object, refer
        http://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.OptimizeResult.html
    """
    rng = check_random_state(random_state)
    space = Space(dimensions)
    if x0 is None:
        x0 = []
    elif not isinstance(x0[0], list):
        x0 = [x0]

    if not isinstance(x0, list):
        raise ValueError("Expected x0 to be a list, but got %s" % type(x0))

    if y0 is None and x0:
        init_y = func(x0[0])
        if not np.isscalar(init_y):
            raise ValueError(
                "The function to be optimized should return a scalar")
        y0 = [init_y] + [func(x) for x in x0[1:]]
        n_calls -= len(y0)
    elif x0:
        if isinstance(y0, Iterable):
            y0 = list(y0)
        elif isinstance(y0, numbers.Number):
            y0 = [y0]
        else:
            raise ValueError(
                "Expected y0 to be an iterable or a scalar, got %s" % type(y0))
        if len(x0) != len(y0):
            raise ValueError("x0 and y0 should have the same length")
        if not all(map(np.isscalar, y0)):
            raise ValueError(
                "y0 elements should be scalars")
    else:
        y0 = []

    X_left = space.rvs(n_samples=n_calls, random_state=rng)
    if y0:
        y_left = [func(X_left[i]) for i in range(0, n_calls)]
    else:
        init_y = func(X_left[0])
        if not np.isscalar(init_y):
            raise ValueError(
                "The function to be optimized should return a scalar")
        y_left = ([init_y] +
                  [func(X_left[i]) for i in range(1, n_calls)])

    X = x0 + X_left
    y = y0 + y_left
    y = np.array(y)
    res = OptimizeResult()
    best = np.argmin(y)
    res.x = X[best]
    res.fun = y[best]
    res.func_vals = y
    res.x_iters = X
    res.space = space
    # create attribute even though it is empty
    res.models = []

    return res
