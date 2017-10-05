# -*- coding: utf-8 -*-

# imports...
# ...standard library
from __future__ import division, print_function
# ...HydPy specific
from hydpy.core import modeltools


def calc_qpin_v1(self):
    """Calculate the input discharge portions of the different response
    functions.

    Required derived parameters:
      :class:`~hydpy.models.arma.arma_derived.Nmb`
      :class:`~hydpy.models.arma.arma_derived.MaxQ`
      :class:`~hydpy.models.arma.arma_derived.DiffQ`

    Required flux sequence:
      :class:`~hydpy.models.arma.arma_fluxes.QIn`

    Calculated flux sequences:
      :class:`~hydpy.models.arma.arma_fluxes.QPIn`

    Examples:

        Initialize an arma model with three different response functions:

        >>> from hydpy.models.arma import *
        >>> parameterstep()
        >>> derived.nmb = 3
        >>> derived.maxq.shape = 3
        >>> derived.diffq.shape = 2
        >>> fluxes.qpin.shape = 3

        Define the maximum discharge value of the respective response
        functions and their successive differences:

        >>> derived.maxq(0.0, 2.0, 6.0)
        >>> derived.diffq(2., 4.)

        The first six examples are performed for inflow values ranging from
        0 to 12 m³/s:

        >>> from hydpy.core.testtools import UnitTest
        >>> test = UnitTest(model, model.calc_qpin_v1, last_example=6)
        >>> test.nexts.qin = 0., 1., 2., 4., 6., 12.
        >>> test()
        | ex. | nmb |           maxq |      diffq |  qin |           qpin |
        -------------------------------------------------------------------
        |   1 |   3 | 0.0  2.0   6.0 | 2.0    4.0 |  0.0 | 0.0  0.0   0.0 |
        |   2 |   3 | 0.0  2.0   6.0 | 2.0    4.0 |  1.0 | 1.0  0.0   0.0 |
        |   3 |   3 | 0.0  2.0   6.0 | 2.0    4.0 |  2.0 | 2.0  0.0   0.0 |
        |   4 |   3 | 0.0  2.0   6.0 | 2.0    4.0 |  4.0 | 2.0  2.0   0.0 |
        |   5 |   3 | 0.0  2.0   6.0 | 2.0    4.0 |  6.0 | 2.0  4.0   0.0 |
        |   6 |   3 | 0.0  2.0   6.0 | 2.0    4.0 | 12.0 | 2.0  4.0   6.0 |


        The following two additional examples are just supposed to demonstrate
        method :func:`calc_qpin_v1` also functions properly if there is only
        one response function, wherefore total discharge does not need to be
        divided:

        >>> derived.nmb = 1
        >>> derived.maxq.shape = 1
        >>> derived.diffq.shape = 0
        >>> fluxes.qpin.shape = 1
        >>> derived.maxq(0.)

        >>> test = UnitTest(model, model.calc_qpin_v1,
        ...                 first_example=7, last_example=8)
        >>> test.nexts.qin = 0., 12.
        >>> test()
        | ex. | nmb | maxq | diffq |  qin | qpin |
        ------------------------------------------
        |   7 |   1 |  0.0 | empty |  0.0 |  0.0 |
        |   8 |   1 |  0.0 | empty | 12.0 | 12.0 |

    """
    der = self.parameters.derived.fastaccess
    flu = self.sequences.fluxes.fastaccess
    for idx in range(der.nmb-1):
        if flu.qin < der.maxq[idx]:
            flu.qpin[idx] = 0.
        elif flu.qin < der.maxq[idx+1]:
            flu.qpin[idx] = flu.qin-der.maxq[idx]
        else:
            flu.qpin[idx] = der.diffq[idx]
    flu.qpin[der.nmb-1] = max(flu.qin-der.maxq[der.nmb-1], 0.)


def calc_login_v1(self):
    """Refresh the input log sequence for the different MA processes.

    Required derived parameters:
      :class:`~hydpy.models.arma.arma_derived.Nmb`
      :class:`~hydpy.models.arma.arma_derived.MA_Order`

    Required flux sequence:
      :class:`~hydpy.models.arma.arma_fluxes.QPIn`

    Updated log sequence:
      :class:`~hydpy.models.arma.arma_log.LogIn`

    Example:

        Assume there are three response functions, involving one, two and
        three MA coefficients respectively:

        >>> from hydpy.models.arma import *
        >>> parameterstep()
        >>> derived.nmb(3)
        >>> derived.ma_order.shape = 3
        >>> derived.ma_order = 1, 2, 3
        >>> fluxes.qpin.shape = 3
        >>> logs.login.shape = (3, 3)

        The "memory values" of the different MA processes are defined as
        follows (one row for each process):

        >>> logs.login = ((1.0, nan, nan),
        ...               (2.0, 3.0, nan),
        ...               (4.0, 5.0, 6.0))

        These are the new inflow discharge portions to be included into
        the memories of the different processes:

        >>> fluxes.qpin = 7.0, 8.0, 9.0

        Through applying method :func:`calc_login_v1` all values already
        existing are shifted to the right ("into the past").  Values, which
        are no longer required due to the limited order or the different
        MA processes, are discarded.  The new values are inserted in the
        first column:

        >>> model.calc_login_v1()
        >>> logs.login
        login(7.0, nan, nan,
              8.0, 2.0, nan,
              9.0, 4.0, 5.0)
    """
    der = self.parameters.derived.fastaccess
    flu = self.sequences.fluxes.fastaccess
    log = self.sequences.logs.fastaccess
    for idx in range(der.nmb):
        for jdx in range(der.ma_order[idx]-2, -1, -1):
            log.login[idx, jdx+1] = log.login[idx, jdx]
    for idx in range(der.nmb):
        log.login[idx, 0] = flu.qpin[idx]


def calc_qma_v1(self):
    """Calculate the discharge responses of the different MA processes.

    Required derived parameters:
      :class:`~hydpy.models.arma.arma_derived.Nmb`
      :class:`~hydpy.models.arma.arma_derived.MA_Order`
      :class:`~hydpy.models.arma.arma_derived.MA_Coeffs`

    Required log sequence:
      :class:`~hydpy.models.arma.arma_log.LogIn`

    Calculated flux sequence:
      :class:`~hydpy.models.arma.arma_fluxes.QMA`

    Examples:

        Assume there are three response functions, involving one, two and
        three MA coefficients respectively:

        >>> from hydpy.models.arma import *
        >>> parameterstep()
        >>> derived.nmb(3)
        >>> derived.ma_order.shape = 3
        >>> derived.ma_order = 1, 2, 3
        >>> derived.ma_coefs.shape = (3, 3)
        >>> logs.login.shape = (3, 3)
        >>> fluxes.qma.shape = 3

        The coefficients of the different MA processes are stored in
        seperate rows of the 2-dimensional parameter `ma_coefs`:

        >>> derived.ma_coefs = ((1.0, nan, nan),
        ...                     (0.8, 0.2, nan),
        ...                     (0.5, 0.3, 0.2))

        The "memory values" of the different MA processes are defined as
        follows (one row for each process).  The current values are stored
        in first column, the values of the last time step in the second
        column, and so on:

        >>> logs.login = ((1.0, nan, nan),
        ...               (2.0, 3.0, nan),
        ...               (4.0, 5.0, 6.0))

        Applying method :func:`calc_qma_v1` is equivalent to calculating
        the inner product of the different rows of both matrices:

        >>> model.calc_qma_v1()
        >>> fluxes.qma
        qma(1.0, 2.2, 4.7)

    """
    der = self.parameters.derived.fastaccess
    flu = self.sequences.fluxes.fastaccess
    log = self.sequences.logs.fastaccess
    for idx in range(der.nmb):
        flu.qma[idx] = 0.
        for jdx in range(der.ma_order[idx]):
            flu.qma[idx] += der.ma_coefs[idx, jdx] * log.login[idx, jdx]


def calc_qar_v1(self):
    """Calculate the discharge responses of the different AR processes.

    Required derived parameters:
      :class:`~hydpy.models.arma.arma_derived.Nmb`
      :class:`~hydpy.models.arma.arma_derived.AR_Order`
      :class:`~hydpy.models.arma.arma_derived.AR_Coeffs`

    Required log sequence:
      :class:`~hydpy.models.arma.arma_log.LogOut`

    Calculated flux sequence:
      :class:`~hydpy.models.arma.arma_fluxes.QAR`

    Examples:

        Assume there are four response functions, involving zero, one, two,
        and three AR coefficients respectively:

        >>> from hydpy.models.arma import *
        >>> parameterstep()
        >>> derived.nmb(4)
        >>> derived.ar_order.shape = 4
        >>> derived.ar_order = 0, 1, 2, 3
        >>> derived.ar_coefs.shape = (4, 3)
        >>> logs.logout.shape = (4, 3)
        >>> fluxes.qar.shape = 4

        The coefficients of the different AR processes are stored in
        seperate rows of the 2-dimensional parameter `ma_coefs`.
        Note the special case of the first AR process of zero order
        (first row), which involves no autoregressive memory at all:

        >>> derived.ar_coefs = ((nan, nan, nan),
        ...                     (1.0, nan, nan),
        ...                     (0.8, 0.2, nan),
        ...                     (0.5, 0.3, 0.2))

        The "memory values" of the different AR processes are defined as
        follows (one row for each process).  The values of the last time
        step are stored in first column, the values of the last time step
        in the second column, and so on:

        >>> logs.logout = ((nan, nan, nan),
        ...                (1.0, nan, nan),
        ...                (2.0, 3.0, nan),
        ...                (4.0, 5.0, 6.0))

        Applying method :func:`calc_qar_v1` is equivalent to calculating
        the inner product of the different rows of both matrices:

        >>> model.calc_qar_v1()
        >>> fluxes.qar
        qar(0.0, 1.0, 2.2, 4.7)

    """
    der = self.parameters.derived.fastaccess
    flu = self.sequences.fluxes.fastaccess
    log = self.sequences.logs.fastaccess
    for idx in range(der.nmb):
        flu.qar[idx] = 0.
        for jdx in range(der.ar_order[idx]):
            flu.qar[idx] += der.ar_coefs[idx, jdx] * log.logout[idx, jdx]


def calc_qpout_v1(self):
    """Calculate the ARMA results for the different response functions.

    Required derived parameter:
      :class:`~hydpy.models.arma.arma_derived.Nmb`

    Required flux sequences:
      :class:`~hydpy.models.arma.arma_fluxes.QMA`
      :class:`~hydpy.models.arma.arma_fluxes.QAR`

    Calculated flux sequence:
      :class:`~hydpy.models.arma.arma_fluxes.QPOut`

    Examples:

        Initialize an arma model with three different response functions:

        >>> from hydpy.models.arma import *
        >>> parameterstep()
        >>> derived.nmb(3)
        >>> fluxes.qma.shape = 3
        >>> fluxes.qar.shape = 3
        >>> fluxes.qpout.shape = 3

        Define the output values of the MA and of the AR processes
        associated with the three response functions and apply
        method :func:`calc_qpout_v1`:

        >>> fluxes.qar = 4.0, 5.0, 6.0
        >>> fluxes.qma = 1.0, 2.0, 3.0
        >>> model.calc_qpout_v1()
        >>> fluxes.qpout
        qpout(5.0, 7.0, 9.0)
    """
    der = self.parameters.derived.fastaccess
    flu = self.sequences.fluxes.fastaccess
    for idx in range(der.nmb):
        flu.qpout[idx] = flu.qma[idx]+flu.qar[idx]


def calc_logout_v1(self):
    """Refresh the log sequence for the different AR processes.

    Required derived parameters:
      :class:`~hydpy.models.arma.arma_derived.Nmb`
      :class:`~hydpy.models.arma.arma_derived.AR_Order`

    Required flux sequence:
      :class:`~hydpy.models.arma.arma_fluxes.QPOut`

    Updated log sequence:
      :class:`~hydpy.models.arma.arma_log.LogOut`

    Example:

        Assume there are four response functions, involving zero, one, two
        and three AR coefficients respectively:

        >>> from hydpy.models.arma import *
        >>> parameterstep()
        >>> derived.nmb(4)
        >>> derived.ar_order.shape = 4
        >>> derived.ar_order = 0, 1, 2, 3
        >>> fluxes.qpout.shape = 4
        >>> logs.logout.shape = (4, 3)

        The "memory values" of the different AR processes are defined as
        follows (one row for each process).  Note the special case of the
        first AR process of zero order (first row), which is why there are
        no autoregressive memory values required:

        >>> logs.logout = ((nan, nan, nan),
        ...                (0.0, nan, nan),
        ...                (1.0, 2.0, nan),
        ...                (3.0, 4.0, 5.0))

        These are the new outflow discharge portions to be included into
        the memories of the different processes:

        >>> fluxes.qpout = 6.0, 7.0, 8.0, 9.0

        Through applying method :func:`calc_logout_v1` all values already
        existing are shifted to the right ("into the past").  Values, which
        are no longer required due to the limited order or the different
        AR processes, are discarded.  The new values are inserted in the
        first column:

        >>> model.calc_logout_v1()
        >>> logs.logout
        logout(nan, nan, nan,
               7.0, nan, nan,
               8.0, 1.0, nan,
               9.0, 3.0, 4.0)

    """
    der = self.parameters.derived.fastaccess
    flu = self.sequences.fluxes.fastaccess
    log = self.sequences.logs.fastaccess
    for idx in range(der.nmb):
        for jdx in range(der.ar_order[idx]-2, -1, -1):
            log.logout[idx, jdx+1] = log.logout[idx, jdx]
    for idx in range(der.nmb):
        if der.ar_order[idx] > 0:
            log.logout[idx, 0] = flu.qpout[idx]


def calc_qout_v1(self):
    """Sum up the results of the different response functions.

    Required derived parameter:
      :class:`~hydpy.models.arma.arma_derived.Nmb`

    Required flux sequences:
      :class:`~hydpy.models.arma.arma_fluxes.QPOut`

    Calculated flux sequence:
      :class:`~hydpy.models.arma.arma_fluxes.QOut`

    Examples:

        Initialize an arma model with three different response functions:

        >>> from hydpy.models.arma import *
        >>> parameterstep()
        >>> derived.nmb(3)
        >>> fluxes.qpout.shape = 3

        Define the output values of the three response functions and
        apply method :func:`calc_qout_v1`:

        >>> fluxes.qpout = 1.0, 2.0, 3.0
        >>> model.calc_qout_v1()
        >>> fluxes.qout
        qout(6.0)
    """
    der = self.parameters.derived.fastaccess
    flu = self.sequences.fluxes.fastaccess
    flu.qout = 0.
    for idx in range(der.nmb):
        flu.qout += flu.qpout[idx]


def pick_q_v1(self):
    """Update inflow."""
    flu = self.sequences.fluxes.fastaccess
    inl = self.sequences.inlets.fastaccess
    flu.qin = 0.
    for idx in range(inl.len_q):
        flu.qin += inl.q[idx][0]


def pass_q_v1(self):
    """Update outflow."""
    flu = self.sequences.fluxes.fastaccess
    out = self.sequences.outlets.fastaccess
    out.q[0] += flu.qout


class Model(modeltools.Model):
    """Base model ARMA."""

    _INPUT_METHODS = (pick_q_v1,)
    _RUN_METHODS = (calc_qpin_v1,
                    calc_login_v1,
                    calc_qma_v1,
                    calc_qar_v1,
                    calc_qpout_v1,
                    calc_logout_v1,
                    calc_qout_v1)
    _OUTPUT_METHODS = (pass_q_v1,)
