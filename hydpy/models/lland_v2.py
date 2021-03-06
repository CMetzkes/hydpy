# -*- coding: utf-8 -*-
"""
Version 2 of the L-Land model (lland_v2) is a slight modification of
:mod:`~hydpy.models.lland_v1`.  :mod:`~hydpy.models.lland_v1`
implements a specific equation for the calculation of reference evaporation
(:class:`~hydpy.models.lland.lland_fluxes.ET0`) for each hydrological
response unit (HRU).  In contrast, lland_v2 expects subbasin wide
potential evaporation values (:class:`~hydpy.models.lland.lland_inputs.PET`)
to be calculated externally and adjusts them to the different HRUs of
the subbasin.

:mod:`~hydpy.models.lland_v1` should be applied on daily step sized
only due to the restrictions of the Turc-Wendling equation for calculating
reference evaporation.  Instead, lland_v2 can be applied on arbitrary
simulation step sizes.

Integration tests:

    All integration tests are performed in January (to allow for realistic
    snow examples), spanning over a period of five days:

    >>> from hydpy import pub, Timegrid, Timegrids
    >>> pub.timegrids = Timegrids(Timegrid('01.01.2000',
    ...                                    '06.01.2000',
    ...                                    '1d'))

    Note that, for the first four days, all integration tests are virtually
    identical with the ones of :mod:`~hydpy.models.lland_v1`, to prove
    the almost identical behaviour of lland_v2.  This is accomplished by
    feeding in potential evaporation values in accordance with the
    Turc-Wendling equation and the given value of the correction factor
    :class:`~hydpy.models.lland.lland_control.KE`.  Only for the fifths day
    a deviating evaporation value is defined, leading to slighlty different
    calculations for some model components.

    Prepare the model instance and build the connections to element `land`
    and node `outlet`:

    >>> from hydpy.models.lland_v2 import *
    >>> parameterstep('1d')
    >>> from hydpy import Node, Element
    >>> outlet = Node('outlet')
    >>> land = Element('land', outlets=outlet)
    >>> land.connect(model)

    All tests shall be performed using a single hydrological response unit
    with a size of one square kilometre:

    >>> nhru(1)
    >>> ft(1.)
    >>> fhru(1.)

    Initialize a test function object, which prepares and runs the tests
    and prints their results for the given sequences:

    >>> from hydpy.core.testtools import IntegrationTest
    >>> test = IntegrationTest(land)

    Define a format for the dates to be printed:

    >>> test.dateformat = '%d.%m.'

    In the first example, coniferous forest is selected as the only
    land use class:

    >>> lnk(NADELW)

    All control parameters are set in manner, that lets their corresponding
    methods show an impact on the results:

    >>> kg(1.2)
    >>> kt(1.)
    >>> ke(2.)
    >>> fln(.5)
    >>> hinz(.2)
    >>> lai(4.)
    >>> treft(0.)
    >>> trefn(0.)
    >>> tgr(1.)
    >>> tsp(2.)
    >>> gtf(5.)
    >>> rschmelz(334.)
    >>> cpwasser(4.1868)
    >>> pwmax(1.4)
    >>> grasref_r(5.)
    >>> nfk(200.)
    >>> relwz(.5)
    >>> relwb(.05)
    >>> beta(.01)
    >>> fbeta(1.)
    >>> dmax(5.)
    >>> dmin(1.)
    >>> bsf(.4)
    >>> a1(1.)
    >>> a2(1.)
    >>> tind(1.)
    >>> eqb(100.)
    >>> eqi1(50.)
    >>> eqi2(10.)
    >>> eqd1(2.)
    >>> eqd2(1.)

    Initially, relative soil moisture is 75%, but all other storages are
    empty and there is base flow only:

    >>> test.inits = ((states.inzp, 0.),
    ...               (states.wats, 0.),
    ...               (states.waes, 0.),
    ...               (states.bowa, 150.),
    ...               (states.qdgz1, 0.),
    ...               (states.qdgz2, 0.),
    ...               (states.qigz1, 0.),
    ...               (states.qigz2, 0.),
    ...               (states.qbgz, 1.),
    ...               (states.qdga1, 0.),
    ...               (states.qdga2, 0.),
    ...               (states.qiga1, 0.),
    ...               (states.qiga2, 0.),
    ...               (states.qbga, 1.))

    For the input data, a strong increase in temperature from -5°C to +10°C
    is defined, to activate both the snow and the evapotranspiration routines:

    >>> inputs.nied.series = 0., 5., 5., 5., 0.
    >>> inputs.teml.series = -5., -5., 0., 5., 10.

    As explained above, the first four values of potential evaporation
    are taken from the integration example of :mod:`~hydpy.models.lland_v1`
    (divided by 2, which is the value defined for the correction factor
    :class:`~hydpy.models.lland.lland_control.KE`):

    >>> inputs.pet.series = (0.372368842264357,
    ...                      0.372368842264357,
    ...                      0.456618961145853,
    ...                      0.534338063059790,
    ...                      1.)

    For the first four days, the results of the first integration test of
    model :mod:`~hydpy.models.lland_v1` are reproduced.  The increased
    evaporation of the fifth day strenghtens the depletion of the soil
    moisture content.  However, there is no impact on the simulated runoff
    value due the operator splitting scheme implemented for LARSIM's soil
    routine:

    >>> test()
    |   date | nied | teml |      pet | nkor | tkor |      et0 |     evpo |     nbes |     sbes |      evi |      evb |      wgtf |     schm |     wada |      qdb |     qib1 |     qib2 |      qbb |     qdgz |        q |     inzp |    wats |     waes |       bowa |    qdgz1 |    qdgz2 |    qigz1 |    qigz2 |     qbgz |    qdga1 |    qdga2 |    qiga1 |    qiga2 |     qbga |   outlet |
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    | 01.01. |  0.0 | -5.0 | 0.372369 |  0.0 | -4.0 | 0.744738 | 0.372369 |      0.0 |      0.0 |      0.0 | 0.359997 |       0.0 |      0.0 |      0.0 |      0.0 |     0.75 | 1.414214 |      1.4 |      0.0 | 1.077855 |      0.0 |     0.0 |      0.0 |  146.07579 |      0.0 |      0.0 |     0.75 | 1.414214 |      1.4 |      0.0 |      0.0 |  0.00745 | 0.068411 | 1.001993 | 0.012475 |
    | 02.01. |  5.0 | -5.0 | 0.372369 |  6.0 | -4.0 | 0.744738 | 0.372369 |      5.2 |      5.2 | 0.372369 |      0.0 |       0.0 |      0.0 |      0.0 |      0.0 | 0.730379 | 1.251034 | 1.360758 |      0.0 | 1.216305 | 0.427631 |     5.2 |      5.2 | 142.733619 |      0.0 |      0.0 | 0.730379 | 1.251034 | 1.360758 |      0.0 |      0.0 | 0.021959 | 0.188588 | 1.005758 | 0.014078 |
    | 03.01. |  5.0 |  0.0 | 0.456619 |  6.0 |  1.0 | 0.913238 | 0.456619 | 5.627631 | 2.813816 | 0.456619 |      0.0 |  5.012535 | 5.012535 | 6.625839 |  2.04495 | 0.713668 | 1.117415 | 1.327336 |  2.04495 |  1.84654 | 0.343381 | 3.00128 | 4.201792 | 144.156088 | 1.510991 |  0.53396 | 0.713668 | 1.117415 | 1.327336 | 0.321934 | 0.196433 |  0.03582 | 0.283229 | 1.009124 | 0.021372 |
    | 04.01. |  5.0 |  5.0 | 0.534338 |  6.0 |  6.0 | 1.068676 | 0.534338 | 5.543381 |      0.0 | 0.534338 |      0.0 | 30.075212 |  3.00128 | 9.745173 | 3.096033 |  0.72078 |  1.17367 | 1.341561 | 3.096033 | 2.987559 | 0.265662 |     0.0 |      0.0 | 147.569218 | 1.677006 | 1.419027 |  0.72078 |  1.17367 | 1.341561 | 0.825163 | 0.735388 | 0.049313 | 0.365334 | 1.012361 | 0.034578 |
    | 05.01. |  0.0 | 10.0 |      1.0 |  0.0 | 11.0 |      2.0 |      1.0 |      0.0 |      0.0 | 0.265662 | 0.707835 | 55.137889 |      0.0 |      0.0 |      0.0 | 0.737846 | 1.312348 | 1.375692 |      0.0 | 2.976082 |      0.0 |     0.0 |      0.0 | 143.435497 |      0.0 |      0.0 | 0.737846 | 1.312348 | 1.375692 | 0.803032 | 0.645499 | 0.062779 | 0.448966 | 1.015807 | 0.034445 |

    The second example deals with a sealed surface:

    >>> lnk(VERS)

    For sealed surfaces, the soil routine is skippend an no base flow is
    calculated.  Thus the corresponding initial values are set to zero:

    >>> test.inits.bowa = 0.
    >>> test.inits.qbgz = 0.
    >>> test.inits.qbga = 0.

    The interception storage is totally drained during the fifth day both
    with the lower potential evaporation value of the second integration
    test of model :mod:`~hydpy.models.lland_v1` and the potential
    evaporation value defined in this example.  Hence only the values
    calculated for sequence :class:`~hydpy.models.lland.lland_fluxes.EvPo`
    differ between both integration tests:

    >>> test()
    |   date | nied | teml |      pet | nkor | tkor |      et0 |     evpo |     nbes |     sbes |      evi | evb |      wgtf |     schm |     wada |      qdb | qib1 | qib2 | qbb |     qdgz |        q |     inzp |    wats |     waes | bowa |    qdgz1 |    qdgz2 | qigz1 | qigz2 | qbgz |    qdga1 |    qdga2 | qiga1 | qiga2 | qbga |   outlet |
    -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    | 01.01. |  0.0 | -5.0 | 0.372369 |  0.0 | -4.0 | 0.744738 | 0.372369 |      0.0 |      0.0 |      0.0 | 0.0 |       0.0 |      0.0 |      0.0 |      0.0 |  0.0 |  0.0 | 0.0 |      0.0 |      0.0 |      0.0 |     0.0 |      0.0 |  0.0 |      0.0 |      0.0 |   0.0 |   0.0 |  0.0 |      0.0 |      0.0 |   0.0 |   0.0 |  0.0 |      0.0 |
    | 02.01. |  5.0 | -5.0 | 0.372369 |  6.0 | -4.0 | 0.744738 | 0.372369 |      5.2 |      5.2 | 0.372369 | 0.0 |       0.0 |      0.0 |      0.0 |      0.0 |  0.0 |  0.0 | 0.0 |      0.0 |      0.0 | 0.427631 |     5.2 |      5.2 |  0.0 |      0.0 |      0.0 |   0.0 |   0.0 |  0.0 |      0.0 |      0.0 |   0.0 |   0.0 |  0.0 |      0.0 |
    | 03.01. |  5.0 |  0.0 | 0.456619 |  6.0 |  1.0 | 0.913238 | 0.456619 | 5.627631 | 2.813816 | 0.456619 | 0.0 |  5.012535 | 5.012535 | 6.625839 | 6.625839 |  0.0 |  0.0 | 0.0 | 6.625839 | 2.151239 | 0.343381 | 3.00128 | 4.201792 |  0.0 | 1.849076 | 4.776763 |   0.0 |   0.0 |  0.0 | 0.393967 | 1.757273 |   0.0 |   0.0 |  0.0 | 0.024899 |
    | 04.01. |  5.0 |  5.0 | 0.534338 |  6.0 |  6.0 | 1.068676 | 0.534338 | 5.543381 |      0.0 | 0.534338 | 0.0 | 30.075212 |  3.00128 | 9.745173 | 9.745173 |  0.0 |  0.0 | 0.0 | 9.745173 | 5.772522 | 0.265662 |     0.0 |      0.0 |  0.0 | 1.897385 | 7.847788 |   0.0 |   0.0 |  0.0 |   0.9768 | 4.795722 |   0.0 |   0.0 |  0.0 | 0.066812 |
    | 05.01. |  0.0 | 10.0 |      1.0 |  0.0 | 11.0 |      2.0 |      1.0 |      0.0 |      0.0 | 0.265662 | 0.0 | 55.137889 |      0.0 |      0.0 |      0.0 |  0.0 |  0.0 | 0.0 |      0.0 | 4.772719 |      0.0 |     0.0 |      0.0 |  0.0 |      0.0 |      0.0 |   0.0 |   0.0 |  0.0 | 0.934763 | 3.837956 |   0.0 |   0.0 |  0.0 |  0.05524 |

    For water areas, evaporation is subtracted from the outflow of the
    subbasin.  Hence there is an actual difference between the simulated
    outflow value of the fifth day of this integration example and the
    outflow value of the third integration test of model
    :mod:`~hydpy.models.lland_v1`:

    >>> lnk(WASSER)
    >>> test()
    |   date | nied | teml |      pet | nkor | tkor |      et0 |     evpo | nbes | sbes |      evi | evb | wgtf | schm | wada | qdb | qib1 | qib2 | qbb | qdgz |        q | inzp | wats | waes | bowa |    qdgz1 |    qdgz2 | qigz1 | qigz2 | qbgz |    qdga1 |    qdga2 | qiga1 | qiga2 | qbga |   outlet |
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    | 01.01. |  0.0 | -5.0 | 0.372369 |  0.0 | -4.0 | 0.744738 | 0.372369 |  0.0 |  0.0 |      0.0 | 0.0 |  0.0 |  0.0 |  0.0 | 0.0 |  0.0 |  0.0 | 0.0 |  0.0 |      0.0 |  0.0 |  0.0 |  0.0 |  0.0 |      0.0 |      0.0 |   0.0 |   0.0 |  0.0 |      0.0 |      0.0 |   0.0 |   0.0 |  0.0 |      0.0 |
    | 02.01. |  5.0 | -5.0 | 0.372369 |  6.0 | -4.0 | 0.744738 | 0.372369 |  6.0 |  6.0 | 0.372369 | 0.0 |  0.0 |  0.0 |  6.0 | 6.0 |  0.0 |  0.0 | 0.0 |  6.0 | 1.551075 |  0.0 |  0.0 |  0.0 |  0.0 | 1.833333 | 4.166667 |   0.0 |   0.0 |  0.0 | 0.390612 | 1.532831 |   0.0 |   0.0 |  0.0 | 0.017952 |
    | 03.01. |  5.0 |  0.0 | 0.456619 |  6.0 |  1.0 | 0.913238 | 0.456619 |  6.0 |  3.0 | 0.456619 | 0.0 |  0.0 |  0.0 |  6.0 | 6.0 |  0.0 |  0.0 | 0.0 |  6.0 | 3.699393 |  0.0 |  0.0 |  0.0 |  0.0 | 1.833333 | 4.166667 |   0.0 |   0.0 |  0.0 | 0.958279 | 3.197733 |   0.0 |   0.0 |  0.0 | 0.042817 |
    | 04.01. |  5.0 |  5.0 | 0.534338 |  6.0 |  6.0 | 1.068676 | 0.534338 |  6.0 |  0.0 | 0.534338 | 0.0 |  0.0 |  0.0 |  6.0 | 6.0 |  0.0 |  0.0 | 0.0 |  6.0 | 4.578464 |  0.0 |  0.0 |  0.0 |  0.0 | 1.833333 | 4.166667 |   0.0 |   0.0 |  0.0 | 1.302586 | 3.810216 |   0.0 |   0.0 |  0.0 | 0.052991 |
    | 05.01. |  0.0 | 10.0 |      1.0 |  0.0 | 11.0 |      2.0 |      1.0 |  0.0 |  0.0 |      1.0 | 0.0 |  0.0 |  0.0 |  0.0 | 0.0 |  0.0 |  0.0 | 0.0 |  0.0 | 2.623511 |  0.0 |  0.0 |  0.0 |  0.0 |      0.0 |      0.0 |   0.0 |   0.0 |  0.0 | 1.120806 | 2.502705 |   0.0 |   0.0 |  0.0 | 0.030365 |
"""
# import...
# ...from standard library
from __future__ import division, print_function
# ...from HydPy
from hydpy.core.modelimports import *
from hydpy.core import modeltools
from hydpy.core import parametertools
from hydpy.core import sequencetools
# ...from lland
from hydpy.models.lland import lland_model
from hydpy.models.lland import lland_control
from hydpy.models.lland import lland_derived
from hydpy.models.lland import lland_inputs
from hydpy.models.lland import lland_fluxes
from hydpy.models.lland import lland_states
from hydpy.models.lland import lland_aides
from hydpy.models.lland import lland_outlets
from hydpy.models.lland.lland_parameters import Parameters
from hydpy.models.lland.lland_constants import *


class Model(modeltools.Model):
    """External ET0 version of HydPy-L-Land (lland_v2)."""
    _RUNMETHODS = (lland_model.calc_nkor_v1,
                   lland_model.calc_tkor_v1,
                   lland_model.calc_et0_v2,
                   lland_model.calc_evpo_v1,
                   lland_model.calc_nbes_inzp_v1,
                   lland_model.calc_evi_inzp_v1,
                   lland_model.calc_sbes_v1,
                   lland_model.calc_wgtf_v1,
                   lland_model.calc_schm_wats_v1,
                   lland_model.calc_wada_waes_v1,
                   lland_model.calc_evb_v1,
                   lland_model.calc_qbb_v1,
                   lland_model.calc_qib1_v1,
                   lland_model.calc_qib2_v1,
                   lland_model.calc_qdb_v1,
                   lland_model.calc_bowa_v1,
                   lland_model.calc_qbgz_v1,
                   lland_model.calc_qigz1_v1,
                   lland_model.calc_qigz2_v1,
                   lland_model.calc_qdgz_v1,
                   lland_model.calc_qdgz1_qdgz2_v1,
                   lland_model.calc_qbga_v1,
                   lland_model.calc_qiga1_v1,
                   lland_model.calc_qiga2_v1,
                   lland_model.calc_qdga1_v1,
                   lland_model.calc_qdga2_v1,
                   lland_model.calc_q_v1,
                   lland_model.update_outlets_v1)


class ControlParameters(parametertools.SubParameters):
    """Control parameters of lland_v2, directly defined by the user."""
    _PARCLASSES = (lland_control.FT,
                   lland_control.NHRU,
                   lland_control.Lnk,
                   lland_control.FHRU,
                   lland_control.KG,
                   lland_control.KT,
                   lland_control.KE,
                   lland_control.FLn,
                   lland_control.HInz,
                   lland_control.LAI,
                   lland_control.TRefT,
                   lland_control.TRefN,
                   lland_control.TGr,
                   lland_control.TSp,
                   lland_control.GTF,
                   lland_control.RSchmelz,
                   lland_control.CPWasser,
                   lland_control.PWMax,
                   lland_control.GrasRef_R,
                   lland_control.NFk,
                   lland_control.RelWZ,
                   lland_control.RelWB,
                   lland_control.Beta,
                   lland_control.FBeta,
                   lland_control.DMax,
                   lland_control.DMin,
                   lland_control.BSf,
                   lland_control.A1,
                   lland_control.A2,
                   lland_control.TInd,
                   lland_control.EQB,
                   lland_control.EQI1,
                   lland_control.EQI2,
                   lland_control.EQD1,
                   lland_control.EQD2)


class DerivedParameters(parametertools.SubParameters):
    """Derived parameters of lland_v2, indirectly defined by the user."""
    _PARCLASSES = (lland_derived.MOY,
                   lland_derived.KInz,
                   lland_derived.WB,
                   lland_derived.WZ,
                   lland_derived.KB,
                   lland_derived.KI1,
                   lland_derived.KI2,
                   lland_derived.KD1,
                   lland_derived.KD2,
                   lland_derived.QFactor)


class InputSequences(sequencetools.InputSequences):
    """Input sequences of lland_v2."""
    _SEQCLASSES = (lland_inputs.Nied,
                   lland_inputs.TemL,
                   lland_inputs.PET)


class FluxSequences(sequencetools.FluxSequences):
    """Flux sequences of lland_v2."""
    _SEQCLASSES = (lland_fluxes.NKor,
                   lland_fluxes.TKor,
                   lland_fluxes.ET0,
                   lland_fluxes.EvPo,
                   lland_fluxes.NBes,
                   lland_fluxes.SBes,
                   lland_fluxes.EvI,
                   lland_fluxes.EvB,
                   lland_fluxes.WGTF,
                   lland_fluxes.Schm,
                   lland_fluxes.WaDa,
                   lland_fluxes.QDB,
                   lland_fluxes.QIB1,
                   lland_fluxes.QIB2,
                   lland_fluxes.QBB,
                   lland_fluxes.QDGZ,
                   lland_fluxes.Q)


class StateSequences(sequencetools.StateSequences):
    """State sequences of lland_v2."""
    _SEQCLASSES = (lland_states.Inzp,
                   lland_states.WATS,
                   lland_states.WAeS,
                   lland_states.BoWa,
                   lland_states.QDGZ1,
                   lland_states.QDGZ2,
                   lland_states.QIGZ1,
                   lland_states.QIGZ2,
                   lland_states.QBGZ,
                   lland_states.QDGA1,
                   lland_states.QDGA2,
                   lland_states.QIGA1,
                   lland_states.QIGA2,
                   lland_states.QBGA)


class AideSequences(sequencetools.AideSequences):
    """Aide sequences of lland_v2."""
    _SEQCLASSES = (lland_aides.Temp,
                   lland_aides.SfA,
                   lland_aides.Exz,
                   lland_aides.BVl,
                   lland_aides.MVl,
                   lland_aides.RVl,
                   lland_aides.EPW)


class OutletSequences(sequencetools.LinkSequences):
    """Downstream link sequences of lland_v2."""
    _SEQCLASSES = (lland_outlets.Q,)


tester = Tester()
cythonizer = Cythonizer()
cythonizer.complete()
