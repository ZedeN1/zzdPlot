"""
/***************************************************************************
Generate a ZZD Convergence Dashboard using Dash
                             -------------------
        begin                : 2026-01-09
        copyright            : (C) 2026
 ***************************************************************************/
"""

import base64
import io
import re
import mmap
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html

import pandas as pd
import numpy as np

# Warning code descriptions
WARNING_DESCRIPTIONS = {
    "W2000": "Poor model convergence",
    "W2001": "Conduits with variable x-section are not permitted",
    "W2002": "Conduits with variable bottom friction are not permitted",
    "W2003": "Conduits with variable top friction are not permitted",
    "W2004": "Conduits with variable friction forms are not permitted",
    "W2005": "Conduits with variable side friction are not permitted",
    "W2008": "Water level below invert",
    "W2010": "Poor interpolation u/s",
    "W2012": "Flow over side spills not calculated",
    "W2013": "Very small change in flow resulting from correction",
    "W2014": "Unit running dry",
    "W2016": "Steady file could not be opened",
    "W2017": "Extra sections need to be added by the user",
    "W2018": "Indeterminate reaches have been found",
    "W2019": "Water level rose beyond the max level of section data",
    "W2020": "Water level >3m above max level of section data",
    "W2021": "Solution found with reduced accuracy",
    "W2023": "Zero areas in Bernoulli Loss unit",
    "W2024": "Extra sections gave insufficient accuracy",
    "W2025": "Data error found in RNDSC gate",
    "W2026": "CONDUIT and RIVER units should not be directly connected",
    "W2027": "No rules currently valid for RULES unit",
    "W2031": "Reservoir units in network",
    "W2032": "Water level outside channel boundary",
    "W2033": "Zero area calculated at node",
    "W2034": "Overbank spill units in network",
    "W2035": "HT boundary at upstream end of reach not permitted",
    "W2036": "QH boundary at upstream end of reach not permitted",
    "W2037": "qt boundary at downstream end of reach not permitted",
    "W2039": "Split/join parameter mismatch",
    "W2040": "Split estimates are wrong at junction",
    "W2042": "Illegal tidal constituent",
    "W2043": "Decreasing cross section distance",
    "W2044": "Different values for Mannings n within one panel",
    "W2045": "Water level at or below reservoir invert",
    "W2046": "Lateral inflows set to zero",
    "W2047": "Non-rectangular control section with notional weir",
    "W2048": "Very small change in heads results in large change in flow",
    "W2050": "Ratio between upstream and downstream areas exceeds 2.0",
    "W2051": "Estimated theta value is very large",
    "W2052": "MSL is outside FSR range",
    "W2053": "Soil is outside FSR range",
    "W2054": "Urban fraction should not be > 0.808",
    "W2055": "RSMD is outside FSR range",
    "W2056": "CWI is outside expected range",
    "W2057": "Rainfall Profile duration issue",
    "W2058": "Model convergence criteria were not met",
    "W2059": "Catchment area is outside FSR range",
    "W2060": "Conveyance decreases",
    "W2061": "S1085 is outside FSR range",
    "W2100": "Invalid value given for modular limit",
    "W2201": "Friction law not specified correctly in bridge",
    "W2202": "Bridge calibration factor set to zero",
    "W2203": "Insignificant flow through arches at USBPR bridge",
    "W2204": "Bridge is surcharged",
    "W2205": "Extrapolating base curves",
    "W2206": "Extrapolating pier curves",
    "W2207": "Extrapolating pier sigma curves",
    "W2208": "Extrapolating skew curves",
    "W2209": "Failed to load convey.dll",
    "W2211": "Failed to free memory in CES dll",
    "W2212": "CES dll magic number error",
    "W2213": "CES dll version error",
    "W2214": "Failed to set 'Flood Modeller' in CES",
    "W2215": "Bad gauge data",
    "W2216": "Gauge limit incompatibility",
    "W2217": "No method file specified for gauge unit",
    "W2229": "Trash screen height is set to 0",
    "W2235": "Variable Percentage Runoff Flag error",
    "W2236": "Optimum number of internal calculation points exceeded",
    "W2237": "MUSK-RSEC data error",
    "W2238": "Panel has very small width",
    "W2260": "Culvert bend losses coefficient issue",
    "W2261": "Backflow encountered at culvert bend or loss unit",
    "W2262": "Backflow encountered CULVERT OUTLET unit",
    "W2263": "Backflow encountered at CULVERT INLET unit",
    "W2264": "Level below culvert invert",
    "W2266": "Level below culvert invert",
    "W2267": "No sub/supercritical depth could be found",
    "W2268": "Direct supercritical method cannot handle this configuration",
    "W2271": "Failed to find minimum of energy function",
    "W2272": "Energy equation failed to converge",
    "W2273": "Defaulting to critical depth",
    "W2274": "Bernoulli loss unit level/area issue",
    "W2275": "Two levels have zero upstream area",
    "W2276": "Water level set to adjacent lowest bed level",
    "W2277": "Last appearance of conduits message",
    "W2278": "Zero calibration coefficient",
    "W2279": "Reference velocity exceeds 3 m/s",
    "W2280": "Estimated theta value is negative",
    "W2281": "No flow possible with zero coefficient",
    "W2282": "Minimum/initial timestep has been changed",
    "W2283": "Conduit section has been reversed",
    "W2286": "Reservoir/Pond area is smaller than previous",
    "W2287": "Two levels have zero area",
    "W2288": "Initial water levels upstream not all equal",
    "W2289": "Discharge coefficient set to zero",
    "W2290": "Opening is zero - no flow possible",
    "W2291": "Initial water level higher than crest of SPILL",
    "W2292": "Failed to converge to normal depth",
    "W2293": "Linear interpolation with rainfall data not allowed",
    "W2294": "Crump, Flat-V weir not connected correctly",
    "W2295": "Seasonal PMPs extrapolated",
    "W2296": "Rule interpretation warning",
    "W2297": "Date/time from Tidal Boundary unit used",
    "W2298": "Data interval less than one minute",
    "W2299": "Storm duration not integer multiple of dt",
    "W2300": "ARF equation for short durations called",
    "W2301": "Adaptive timestepping parameter issue",
    "W2302": "Time to peak not integer multiple of data interval",
    "W2313": "Zero modular limit",
    "W2314": "Modular limit set to unity or greater",
    "W2315": "Negative loss coefficient entered",
    "W2317": "Downstream flow area constrained",
    "W2318": "Initial adaptive timestep not read from file",
    "W2319": "Downstream constraining factor not set",
    "W2320": "Reservoir updating unit not connected to reservoir",
    "W2321": "Conduit slot dimensions incorrect",
    "W2322": "Failed to read event data",
    "W2323": "Unrealistic density input",
    "W2531": "Cannot find upstream condition for supercritical integration",
    "W2532": "Model start time is NOT t=0",
    "W2533": "Volumes not calculated for Muskingum sections",
    "W2534": "Errors occurred opening/writing to file",
    "W2535": "c0 scaling factor input error",
    "N3002": "Very small change in heads results in large change in flow",
    "N3003": "Percentage runoff calculated as negative",
    "N3006": "End of backflow at CULVERT INLET unit",
    "N3007": "End of backflow at CULVERT OUTLET unit",
    "N3010": "Simplified method used",
    "N3012": "Zero flow beyond point",
    "N3013": "Transcritical point(s) occurred",
    "N3014": "EVENT DATA FILE READ FAILED",
    "N3015": "Simulation event date/time overrides Tidal Boundary",
    "N3016": "Tidal Boundary unit with no event date/time",
    "N3017": "Tidal boundary used with direct method",
    "N3018": "2D Input Data check completed",
    "N3019": "User-input PMF time to peak adjustment note",
    "N3025": "Minimum flow applied at boundary",
    "N3026": "Initial adaptive timestep read from input file",
    "N3027": "2d timestep read from tcf file",
    "N3028": "Data points omitted from deactivated section areas",
    "N3029": "Duplicated units found",
    "E1003": "Bernoulli loss - no. of data sets must not be > 30 or < 1",
    "E1004": "Data read error",
    "E1005": "Unit unacceptable as first data unit",
    "E1006": "No. of stage/gate opening datasets < 2",
    "E1007": "Maximum no of gates exceeded",
    "E1008": "Maximum number of nodes is exceeded",
    "E1009": "Maximum number of units is exceeded",
    "E1011": "Unidentified unit",
    "E1013": "The EGGFORM option is not yet available, try using a CIRCULAR conduit with a suitable diameter",
    "E1014": "Supercritical flow between 'label1' and 'label2'. You should use the option for dealing with Froude numbers greater than 1",
    "E1017": "Negative flow - the direct method cannot handle backflow",
    "E1018": "Maximum no. of iterations exceeded",
    "E1019": "No solution found in Direct Method",
    "E1020": "Water level exceeded maximum section data level dflood",
    "E1022": "Not a recognised type number / Error writing OTTA file",
    "E1023": "Generic ERROR - see zzd file / complementary error code",
    "E1027": "Value of rsmd should not be less than 10",
    "E1028": "Maximum number of unit hydrograph ordinates exceeded",
    "E1029": "Error - data interval too small for unit hydrograph calculation or Time to Peak",
    "E1033": "Incorrect percentage runoff code of 'x' in subroutine prcal",
    "E1036": "Storm return period of 'x' too small to estimate rainfall depth.",
    "E1038": "Areal reduction factor equation very inaccurate for durations less than 0.5 hr",
    "E1039": "Water level below invert.",
    "E1042": "HTBDY - No of data pairs must be > 1",
    "E1044": "Previous unit was not a RIVER or CONDUIT",
    "E1045": "It is not allowed to have interpolated sections here",
    "E1046": "You must have a RIVER or CONDUIT downstream of INTERPOLATED sections",
    "E1051": "Format error in numerical data. JUNCTION data error",
    "E1056": "The direct method cannot be used with automatic controllers",
    "E1057": "Inconsistencies found in node labels",
    "E1065": "Variable outside linearization range",
    "E1066": "Variable outside interpolation range",
    "E1072": "rn must be greater than 1",
    "E1073": "cd outside allowed range",
    "E1074": "cv outside allowed range",
    "E1075": "Weir breadth must be positive.",
    "E1079": "Maximum no. of network iterations exceeded",
    "E1080": "Number of data points is less than 2.",
    "E1081": "Number of data points is greater than maximum allowed.",
    "E1091": "FULL ARCH CONDUIT. The height of the crown specified is too high.",
    "E1094": "Reverse flows not valid in syphon spillways",
    "E1095": "Decreasing cross section distance found",
    "E1096": "Panel contains zero and non-zero Manning's n",
    "E1097": "Cross-section contains all zero Manning's n",
    "E1098": "Number of height points exceeds maximum",
    "E1100": "Model is diverging. No solution has been found with the current time step",
    "E1105": "Time-dependent data in unit doesn't cover the start time of the model duration",
    "E1106": "Time-dependent data in unit doesn't cover the start time of the model duration",
    "E1108": "Tolerance for the direct method cannot be negative",
    "E1109": "Tolerance for the direct method cannot be greater than 0.1",
    "E1111": "None of the labels in the initial conditions have been tagged.",
    "E1112": "Number of labels in initial conditions does not match number in data file",
    "E1113": "Generic data read error",
    "E1114": "Data error in zzs file",
    "E1115": "Generic data read error",
    "E1117": "Data error. Lower Froude Number greater or equal to higher value",
    "E1118": "Error in reader",
    "E1119": "Previous unit was not a RIVER or CONDUIT",
    "E1120": "REPLICATE/INTERPOLATE must be preceded by a RIVER or REPLICATE with dx>0",
    "E1121": "There is a spill label assigned to the last river unit in a reach.",
    "E1123": "Unit type may not be connected to reservoir at specified label",
    "E1128": "You must have at least two consecutive RIVERs or CONDUITs to form a unit.",
    "E1129": "It is not possible to find a solution with the current time step",
    "E1131": "Water level outside channel boundary",
    "E1133": "Extra added sections gave insufficient accuracy",
    "E1139": "no. of stage/gate opening datasets > 4.",
    "E1159": "Length of crest in direction of flow must be > 0.1 - rnweir data error",
    "E1168": "Unit not yet available with the direct method - run terminated",
    "E1169": "Pump is in stopped mode; This mode is incompatible with the direct method.",
    "E1179": "Remote upstream control not yet available. For use with the direct method.",
    "E1184": "Third label required for WATER3 option for remote control mode",
    "E1185": "Values given must be greater than zero",
    "E1188": "No gate opening given for MANUAL operation",
    "E1189": "No initial gate opening given for AUTO operation",
    "E1195": "Matrix structurally singular. iflag = -1",
    "E1196": "Matrix numerically singular. iflag = -2",
    "E1197": "Row or column index out of range. iflag = -12",
    "E1198": "Dir = 'x' reverse flow direction hn1 = 'y' hn2 = 'z' node = 'n'",
    "E1199": "Error in spill at line 'l'. bank chainage must increase for each data pair",
    "E1200": "Maximum gate opening MUST be less than radius plus height of pivot",
    "E1201": "Gate opening MUST be less than radius plus height of pivot",
    "E1202": "Gate radius MUST be greater than height of pivot",
    "E1203": "Number of data points in SPILL unit must be must be greater than 1",
    "E1210": "Negative flow specified at a Q:T boundary - this is not permitted",
    "E1211": "Perturbation matrix is singular",
    "E1219": "cv outside allowed range",
    "E1221": "rlimit outside allowed range",
    "E1230": "Suter pump - numerical data outside allowable range",
    "E1234": "Generic error - see zzd file for further information",
    "E1237": "SAAR must be positive for event rainfall calculation",
    "E1238": "Event Rainfall flag is expected to be OBSER, FEHER, FSRER, or PMFER",
    "E1239": "Positive non-zero value is expected for the OBSERVED event rainfall",
    "E1241": "Catchment Wetness Index flag is expected to be OBSCW, FSRCW or PMFCW",
    "E1243": "Percentage Runoff Flag is expected to be BSPR, FEHPR, FSRPR or F16PR",
    "E1244": "Error in OBSERVED percentage runoff, it must not be > 100.0",
    "E1245": "Error in OBSERVED percentage runoff, it must not be <0.0",
    "E1246": "Time to Peak Flag is expected to be OBSTP, FEHTP, F16TP, FSRTP or R124TP",
    "E1247": "Positive non-zero value is expected for the OBSERVED Time to Peak, TP",
    "E1248": "Positive non-zero value is expected for the Calibration factor of TP",
    "E1249": "Base Flow Flag is expected to be OBSBF or F16BF",
    "E1250": "Positive non-zero value is expected for the catchment area, carea",
    "E1253": "Unit Hydrograph Flag is expected to be OBSUH, FSRUH, UBRUH or SCSUH",
    "E1255": "Rainfall Profile Flag is expected to be OBSRP, WINPMP or SUMPMP",
    "E1256": "Number of rainfall values outside range",
    "E1258": "ERROR in calculated percentage runoff at subroutine prcal, it is > 100.0",
    "E1262": "Error in routine interp in fsrqt - value out of range",
    "E1266": "Calculated no of unit hydro. Ordinates is greater than max allowed",
    "E1267": "For SUMRP unequal return periods are unacceptable. This can, however, be forced by using the parameter FORCE.",
    "E1268": "Invalid Velocity Flag specified",
    "E1269": "Power law constants cannot be negative",
    "E1285": "Reservoir/Pond level is lower than or the same as the previous level",
    "E1301": "No flow boundaries have been defined therefore direct steady method is not applicable",
    "E1302": "No head boundaries have been defined therefore direct steady method is not applicable",
    "E1324": "Number of q:h data pairs exceeds the maximum permitted",
    "E1330": "Efficiency values must be greater than zero and less than or equal to one",
    "E1331": "Optimal head and flow values must both be positive",
    "E1332": "Number of switch data sets must be > 1",
    "E1333": "Invalid switch type keyword",
    "E1334": "Unrecognised pump mode keyword",
    "E1336": "Missing control label for controller switch type",
    "E1338": "Time multiples must be positive",
    "E1339": "Unrecognised pump mode",
    "E1340": "Number of Suter points must be between 1 and 133",
    "E1341": "No corresponding pump mode given for MANUAL operation at model time",
    "E1343": "Number of head, flow, efficiency data sets must be between 1 and 50.",
    "E1344": "Error reading data in datafile.",
    "E1345": "Head, flow and efficiency cannot all be simultaneously greater than zero.",
    "E1346": "Invalid number of switch data sets",
    "E1347": "Unknown switch type: type code",
    "E1348": "Unable to find control unit for controller mode",
    "E1349": "Unknown instruction code for logical switching",
    "E1401": "Skew angle of bridge > 45 ; Must be in range 0 < =angle < =45.",
    "E1402": "Width of bridge< =0.0. Data error in bridge unit",
    "E1403": "Invalid bridge abutment code. Should be 1, 2 or 3. Data error in bridge attached to 'label1', 'label2'",
    "E1404": "Pier coefficient out of range. Must be >=0.0 and < =8.0. Data error in bridge",
    "E1405": "Invalid bridge pier description. 'x'(Number of piers), 'y' (type of shape of bridge soffit), 'z' (type of bridge pier cross sectional type). Data error in bridge attached to 'label1', 'label2'.",
    "E1406": "Number of bridge piers >0 , with Width of bridge piers < =0.",
    "E1410": "Too many culverts in bridge attached to 'label1','label2'.",
    "E1411": "Culvert drowning coefficient must be <1. Data error in bridge attached to 'label1','label2'",
    "E1412": "Culvert invert level is greater than soffit level. Data error in bridge attached to 'label1','label2'.",
    "E1421": "Number of arches < 0",
    "E1422": "Number of arches exceeds the maximum",
    "E1423": "USBPR Bridge error on arch data 'x' (number of arch) x coord of left side of arch must coincide with cross chainage point",
    "E1431": "Too many markers in bridge channel section",
    "E1432": "Left or Right markers wrong in bridge section.",
    "E1510": "Unrecognised direction keyword keyword should be UPSTREAM or DOWNSTREAM",
    "E1511": "Invalid loss coefficient: Loss coefficient must be value between 0 and 10.",
    "E1512": "Upstream section for a BEND/LOSS unit in upstream control must be a RIVER or CONDUIT unit.",
    "E1513": "Invalid loss coefficient: Loss coefficient should be value between 0 and 1.",
    "E1514": "Unit upstream of a CULVERT OUTLET unit must be RIVER or CONDUIT unit.",
    "E1515": "Unrecognised conduit type code. Should be A or B",
    "E1516": "Value of unsubmerged inlet control loss coefficient should be between 0 and 1; current value is x",
    "E1517": "Value of exponent for inlet control should be between 0 and 3; current value is:x",
    "E1518": "Value of submerged inlet control loss coefficient should be between 0 and 0.1; current value is x.",
    "E1519": "Value of submerged inlet control adjustment factor should be between 0 and 1; current value is x",
    "E1520": "Value of outlet control loss coefficient should be between 0 and 1; current value is x",
    "E1521": "Value of trash screen width should be greater than 0; current value is x",
    "E1522": "Value of trash screen bar proportion should be between 0 and 1; current value is x.",
    "E1523": "Value of trash screen blockage ratio should be between 0 and 1; current value is x.",
    "E1524": "Value of trash screen head loss coefficient should be greater than 0; current value is x",
    "E1525": "Unit downstream of a CULVERT INLET unit must be a RIVER or CONDUIT unit.",
    "E1526": "Maximum number of trans-critical points exceeded",
    "E1528": "Junction at l1 appears to be neither a join nor a split",
    "E1529": "Unable to find unit number in list of river reaches",
    "E1530": "Internal error - invalid trans-critical point",
    "E1532": "Upstream/downstream nodes of unit are not rivers/conduits.",
    "E1533": "Cannot find label",
    "E1534": "Save interval (or timestep) must be positive",
    "E1536": "Upstream/downstream/remote/constriction section label does not exist.",
    "E1537": "Upstream and/or downstream river units at bridge not found",
    "E1538": "Culvert flow failed to converge",
    "E1539": "Perturbation failed",
    "E1540": "No nodes found",
    "E1541": "Country must be ENGLAND, IRELAND, SCOTLAND or WALES",
    "E1542": "Value of s1085 must be positive for time to peak calculation",
    "E1543": "Value of MSL/DPSBAR/DPLBAR must be positive for time to peak calculation, or PROPWET must be between 0 and 1.",
    "E1544": "SOIL must be between 0 and 1.0",
    "E1545": "Time step must be positive",
    "E1546": "Urban fraction/extent cannot be <0 or> 1",
    "E1547": "Storm duration of x is less than or equal to zero",
    "E1548": "[Time] interpolation error",
    "E1549": "INTERPOLATE unit must have a positive chainage",
    "E1550": "A reach has more than 100 interpolated sections (split the reach using a RIVER)",
    "E1551": "Numb=0 in INTERPOLATE",
    "E1552": "Total chainage must be positive",
    "E1555": "Unit type may not be connected to junction",
    "E1562": "dx must be positive",
    "E1564": "X number of data points is less than 2",
    "E1565": "X number of data points greater than maximum",
    "E1566": "Lateral inflows cannot be used with MUSKINGUM units",
    "E1567": "Zero wave speed or chainage Ensure that the reach is not dry",
    "E1568": "Slope must be positive",
    "E1569": "Channel section data error. At least 2 section points and a positive slope are required for velocity calculation",
    "E1570": "Attempt to read results from before start of run. Start your run with structure in MANUAL mode",
    "E1571": "Error attempting to read earlier result",
    "E1572": "Unrecognised operation type",
    "E1573": "Weir discharge coefficient must be greater than 0",
    "E1574": "Surcharged discharge coefficient must be greater than 0",
    "E1575": "Pump bore area must be greater than 0",
    "E1576": "Soffit must be higher than invert",
    "E1577": "Bridge soffit is more than 10m above cross section. Please extend your section data or modify the arch dimensions",
    "E1578": "icount is zero - arch error",
    "E1579": "Conduit section should start with x=0 at invert centre line",
    "E1580": "Unrecognised time factor keyword",
    "E1581": "Flood Modeller has detected a different label length in the initial conditions file from the value in operation in the datafile. This is not allowed",
    "E1582": "Maximum number of pond data lines exceeded (max=50)",
    "E1583": "INTERPOLATE must be preceded by a RIVER or REPLICATE with a positive chainage",
    "E1584": "Non-channel unit found in the middle of a reach. Reach must end with dx = 0",
    "E1585": "Length of weir in direction of flow is more than 100 x width of crest. This is not acceptable",
    "E1586": "Crest length must be positive",
    "E1587": "Unknown controller operation mode",
    "E1588": "Unknown sluice gate operation mode",
    "E1589": "No time data available in switch data set for current model time",
    "E1590": "Unable to find controller label for controller mode",
    "E1591": "Unknown controller operation mode",
    "E1592": "Error in floodplain section at line n. Chainage must be positive for friction flow",
    "E1593": "First matrix element is zero",
    "E1594": "Xset points are not all distinct",
    "E1595": "Gate orientation must be FORWARD or REVERSE",
    "E1596": "ctc must be greater than 0",
    "E1597": "cgt must be greater than 0",
    "E1598": "crev must be greater than 0",
    "E1599": "dr must be greater than 0",
    "E1600": "Only one gate is allowed in gated weir",
    "E1601": "Gate height must be greater than zero",
    "E1602": "Gate crest higher than max. gate height",
    "E1603": "Crest is lower than sill",
    "E1605": "Unit version number n is not supported in this version of Flood Modeller",
    "E1606": "Negative breach width xm is invalid",
    "E1607": "Negative breach side slope x is invalid.",
    "E1608": "Error in breach: unable to fit breach, check the breach and associated spill section",
    "E1610": "Invalid blockage proportion x. Proportion p must have 0.0 < = P <=1.0",
    "E1611": "Upstream/Downstream/Constriction unit of a blockage (connected or remote) must be RIVER, CONDUIT or BRIDGE unit.",
    "E1612": "Invalid loss coefficient: Loss coefficient must be at least 0.",
    "E1613": "OPEN pump operation is specified but parameters for OPEN operation are not set",
    "E1614": "Selected node l1 for OLD rules has been removed from the output list",
    "E1620": "Unit not supported in this version of Flood Modeller",
    "E1621": "Invalid lateral inflow weight factor (= x) entered for connecting unit",
    "E1622": "User defined weight factors do not sum to 1.0",
    "E1623": "Unrecognised connecting boundary node entered",
    "E1624": "Link to lateral inflow not recognised",
    "E1625": "Reservoir connected to reach - weighted lateral inflow",
    "E1627": "Connected Muskingum has zero reach length",
    "E1628": "Weight factor type not recognised",
    "E1629": "Muskingum section connected to area distributed lateral",
    "E1630": "This Muskingum type will not receive lateral inflows",
    "E1631": "Zero reach length river section connected to lateral inflow",
    "E1640": "Number of data pairs must be greater than zero",
    "E1641": "No input data types recognised",
    "E1642": "No data in l1 at line n before/after x hrs",
    "E1643": "2 data points with same time",
    "E1644": "Time values are not increasing",
    "E1669": "Zero or Negative slope encountered in Normal depth boundary This is not permitted",
    "E1672": "Remote label not found or not connected to a channel section",
    "E1673": "No valid path found from upstream to downstream slope extents",
    "E1674": "No section data specified or available for normal/critical depth boundary",
    "E1675": "Zero area or width in Critical depth boundary",
    "E1676": "No sign change detected in normal depth equation. Normal depth could not be calculated",
    "E1678": "Data error at line n. Dry lower depth greater or equal to dry higher depth",
    "E1680": "Maximum number 50 of lateral connections for quality run exceeded",
    "E1681": "Data error at line n. no RAD FILE tag found",
    "E1682": "Data error at line n. no GENERAL tag found",
    "E1683": "Failed CES dll function call to SetRoughnessFile",
    "E1684": "Failed CES dll function call to GetRoughnessLoadingErrors",
    "E1685": "Failed CES dll function call to AddSection",
    "E1686": "Failed CES dll function call to Populate Section for section id",
    "E1687": "Failed CES dll function call to Add Section Roughness for section id",
    "E1688": "CES dlls have not been initialised",
    "E1689": "Failed CES dll function call to Calculate Conveyance for section id",
    "E1690": "Failed CES dll function call to Get Depth Intervals",
    "E1691": "Failed CES dll function call to Get Eddy Viscosity",
    "E1692": "Failed CES dll function call to Get Min Depth",
    "E1693": "Failed CES dll function call to Get No Panels",
    "E1694": "Failed CES dll function call to GetRelaxation",
    "E1695": "Failed CES dll function call to Get Temperature",
    "E1696": "Failed CES dll function call to Get Max Iterations",
    "E1697": "Failed CES dll function call to Set Relaxation",
    "E1698": "Failed CES dll function call to Set Depth Intervals",
    "E1699": "Failed CES dll function call to SetEddyViscosity",
    "E1700": "Failed CES dll function call to Set Min Depth",
    "E1701": "Failed CES dll function call to Set No Panels",
    "E1702": "Failed CES dll function call to Set Max Iterations",
    "E1703": "Failed CES dll function call to SetTemperature",
    "E1704": "Failed CES dll function call to GetHytMultiplier",
    "E1705": "Failed CES dll function call to SetHytMultiplier",
    "E1706": "Failed function call to fn_requestoutputs_at_timestage for section",
    "E1707": "Failed function call to fn_get_isis_tables for section",
    "E1708": "Failed CES dll function call to FnGetMinMax_Output_Elevations for section id",
    "E1709": "Failed CES dll function call to fngetmaxarea for section",
    "E1720": "Too many substrings in rule",
    "E1721": "Parse error in rule",
    "E1722": "Logical storage capacity exceded in rule l1",
    "E1723": "Error in rule l1",
    "E1724": "Failed CES dll function call to SetConvTolerance",
    "E1725": "Failed CES dll function call to GetConvTolerance",
    "E1726": "Failed CES dll function call to SetConveyanceType",
    "E1727": "Rule l1 has already been defined. Note that only the first 10 characters of the name are significant.",
    "E1728": "Rule ALL is not valid. It could be confused with the keyword ALL in the TIME RULE DATA SET.",
    "E1729": "Fatal error in 2D solver",
    "E1730": "Indeterminate flow direction in qxbdy",
    "E1800": "Unknown bank type for section id",
    "E1801": "Sinuosity can only provided on a left bank in section id",
    "E1802": "Even number of bank markers required for section id",
    "E1803": "Put roughness chainage in ascending order for section id",
    "E1804": "Put section chainage in ascending order for section id",
    "E1805": "RO bank marker must follow LI for section id",
    "E1806": "RI bank marker must follow LO for section id",
    "E1807": "LI bank marker must follow RO for section id",
    "E1808": "LO bank marker must follow RI for section id",
    "E1809": "RS bank marker must follow LS for section id",
    "E1810": "LS bank marker must follow RS for section id",
    "E1811": "Date out of range in section",
    "E1813": "No section data to calculate conveyance for section id",
    "E1814": "No roughness data to calculate conveyance for section id",
    "E1815": "Roughness zone not found in roughness file for section id",
    "E1818": "[No message]",
    "E1819": "Data error at line X. failed to load roughness file.",
    "E1820": "Non unique section name found for section id/replicate",
    "E1821": "Start date is out of the range specified in the roughness file for section id",
    "E1822": "Finish date is out of the range specified in the roughness file for section id",
    "E1824": "Section not found",
    "E1825": "At least two bank markers required for section id",
    "E1827": "Failed CES dll function call to FnAddInterpolate for interpolated section, cannot find upstream section for section id",
    "E1828": "Failed CES dll function call to FnAddInterpolate for interpolated section, cannot find downstream section for section id",
    "E1830": "Cannot find urban unit.",
    "E1831": "This urban throughflow unit is not associated with an urban unit.",
    "E1832": "The data store cannot accurately store the urban unit's number.",
    "E1900": "Cannot allocate memory, status = n",
    "E1926": "One of many E1926 errors",
    "E1999": "One of many E1999 errors"
}

# --- Pre-compiled Regex Patterns ---
RE_START = re.compile(rb'start time.*?(\d+\.?\d*)', re.IGNORECASE)
RE_END   = re.compile(rb'end time.*?(\d+\.?\d*)', re.IGNORECASE)
RE_CONV = re.compile(
    rb'Poor model convergence.*?time\s+(\d+\.?\d*).*?\n.*?\n.*?MAX DQ=\s*(\S+)\s+at\s+(\S+).*?MAX DH=\s*(\S+)\s+at\s+(\S+)',
    re.DOTALL | re.IGNORECASE
)
RE_WARN = re.compile(
    rb'Model time\s+(\d+\.?\d*).*?\n.*?\*\*\*\s+(warning|note|error)\s+(\w+)\s+\*\*\*\s+at label:\s+(\S+)',
    re.DOTALL | re.IGNORECASE
)

app = dash.Dash(__name__)
server = app.server
app.title = 'ZZD Dashboard'

# --- Layout ---
app.layout = html.Div([
    # Refined Header with Responsive Wrapping
    html.Div([
        # Column 1: Title and File Info
        html.Div([
            html.H4('ZZD Convergence Dashboard', style={'margin': '0', 'color': '#2c3e50'}),
            html.Div(id='file-info', style={'fontSize': '0.85em', 'color': '#666', 'marginTop': '5px'})
        ], style={'flex': '1 1 200px'}), 

        # Column 2: STACKED Tolerance Inputs
        html.Div([
            html.Div([
                html.Label('QTOL:', style={'display': 'inline-block', 'width': '50px', 'fontWeight': 'bold'}),
                dcc.Input(id='qtol-input', type='number', value=0.01, step=0.001,
                          style={'width': '80px', 'height': '28px', 'borderRadius': '4px', 'border': '1px solid #ccc'}),
            ], style={'marginBottom': '4px'}),

            html.Div([
                html.Label('HTOL:', style={'display': 'inline-block', 'width': '50px', 'fontWeight': 'bold'}),
                dcc.Input(id='htol-input', type='number', value=0.01, step=0.001,
                          style={'width': '80px', 'height': '28px', 'borderRadius': '4px', 'border': '1px solid #ccc'}),
            ]),
        ], style={
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'center',
            'padding': '0 15px',
            'borderLeft': '1px solid #ddd',
            'minWidth': '140px'
        }),

        # Column 3: Upload Area
        html.Div([
            dcc.Upload(
                id='upload-zzd',
                children=html.Div([
                    html.Div([
                        html.Div([
                            html.Span("📂", style={'fontSize': '20px', 'marginRight': '10px'}),
                            "Drag/Drop .zzd"
                        ], style={'borderRight': '1px solid #ccc', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
                        html.Div([
                            html.A('Select File', style={'textDecoration': 'underline', 'fontWeight': 'bold'})
                        ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
                    ], style={'display': 'grid', 'gridTemplateColumns': '1.5fr 1fr', 'height': '100%'})
                ]),
                style={
                    'width': '100%', 'height': '55px', 'lineHeight': '55px',
                    'borderWidth': '2px', 'borderStyle': 'dashed', 'borderRadius': '8px',
                    'textAlign': 'center', 'backgroundColor': '#fff', 'cursor': 'pointer'
                }
            )
        ], style={'flex': '2 1 300px'}), 

        # Column 4: Summary Status
        html.Div(id='processing-output', style={
            'flex': '1 1 150px',
            'textAlign': 'right',
            'fontSize': '0.9em',
            'color': '#2980b9',
        })

    ], style={
        'flex': '0 0 auto',          # CHANGE 1: Header takes only needed space (no growth/shrink)
        'display': 'flex',
        'flexWrap': 'wrap',
        'gap': '15px',
        'alignItems': 'center',
        'padding': '15px 25px',
        'background': '#f8f9fa',
        'borderBottom': '2px solid #dee2e6',
        'fontFamily': 'sans-serif'
    }),

    dcc.Tabs([
        dcc.Tab(label='Convergence (DQ & DH)', children=[
            # CHANGE 2: Graph takes 100% of parent Tab content
            dcc.Graph(id='convergence-graph', style={'height': '100%', 'width': '100%'})
        ]),
        dcc.Tab(label='Warning Analysis', children=[
            # CHANGE 2: Graph takes 100% of parent Tab content
            dcc.Graph(id='warning-graph', style={'height': '100%', 'width': '100%'})
        ]),
    ], 
    # CHANGE 3: Tabs expand to fill remaining vertical space
    parent_style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'},
    content_style={'flex': '1', 'position': 'relative'}
    )

], style={
    # CHANGE 4: Main container fills viewport and uses flex column
    'height': 'calc(100vh - 15px)', 
    'display': 'flex', 
    'flexDirection': 'column',
    'overflow': 'hidden'
})

# --- Data Extraction ---
def extract_zzd_data(zzd_bytes):
    """
    Parses ZZD raw bytes efficiently using regex iterators.
    Input: zzd_bytes (bytes) - Raw result from base64 decode
    """

    # --- A. Fast Metadata Extraction ---
    # Search first 5KB for Start Time
    start_match = RE_START.search(zzd_bytes[:5000])
    start_time = float(start_match.group(1)) if start_match else 0.0

    # Search last 5KB for End Time
    end_match = RE_END.search(zzd_bytes[-5000:])
    end_time = float(end_match.group(1)) if end_match else 0.0

    # --- B. Fast Data Extraction ---
    dq_data = []
    dh_data = []
    warn_data = []

    last_err_t = None
    last_err_c = None

    # 1. Extract Convergence Data (DQ & DH)
    for m in RE_CONV.finditer(zzd_bytes):
        t = float(m.group(1))

        # DQ Entry
        dq_data.append({
            'time': t,
            'value': float(m.group(2)),
            'node': m.group(3).decode('utf-8', errors='ignore')
        })

        # DH Entry
        dh_data.append({
            'time': t,
            'value': float(m.group(4)),
            'node': m.group(5).decode('utf-8', errors='ignore')
        })

    # 2. Extract Warnings
    for m in RE_WARN.finditer(zzd_bytes):
        t = float(m.group(1))
        etype = m.group(2).decode('utf-8', errors='ignore').upper()
        ecode = m.group(3).decode('utf-8', errors='ignore')
        label = m.group(4).decode('utf-8', errors='ignore')

        warn_data.append({
            'time': t,
            'type': etype,
            'code': ecode,
            'label': label
        })

        if etype == 'ERROR':
            last_err_t = t
            last_err_c = ecode

    # --- C. Fatal Crash Check ---
    is_fatal = b"stopped in error" in zzd_bytes[-2000:]

    # --- D. ROBUST TIME INFERENCE (THE FIX) ---
    # If regex failed to find explicit start/end times (common in crashed files),
    # we infer them from the data we actually found.
    if start_time == 0.0 or end_time == 0.0:
        all_timestamps = []

        # Collect timestamps from all sources
        if dq_data:
            all_timestamps.append(dq_data[0]['time'])
            all_timestamps.append(dq_data[-1]['time'])
        if warn_data:
            all_timestamps.append(warn_data[0]['time'])
            all_timestamps.append(warn_data[-1]['time'])

        if all_timestamps:
            if start_time == 0.0: start_time = min(all_timestamps)
            if end_time == 0.0:   end_time = max(all_timestamps)

    # Force a valid time duration if start == end
    # (e.g., if there is only 1 warning message at t=693.25 and nothing else)
    if start_time >= end_time:
        if start_time == 0.0:
            end_time = 1.0  # Default 1 hr if file is totally empty
        else:
            end_time = start_time + 1.0  # Add 1 hr buffer so plot is visible

    # --- E. DataFrame Creation & Memory Optimization ---
    df_dq = pd.DataFrame(dq_data)
    df_dh = pd.DataFrame(dh_data)
    df_w  = pd.DataFrame(warn_data)

    # Convert repetitive strings to Categoricals (Huge RAM saver)
    if not df_dq.empty:
        df_dq['node'] = df_dq['node'].astype('category')

    if not df_dh.empty:
        df_dh['node'] = df_dh['node'].astype('category')

    if not df_w.empty:
        # Map descriptions BEFORE converting to category
        df_w['note'] = df_w['code'].map(WARNING_DESCRIPTIONS).fillna("Unknown Warning")

        # Convert to category
        df_w['code'] = df_w['code'].astype('category')
        df_w['note'] = df_w['note'].astype('category')
        df_w['type'] = df_w['type'].astype('category')

    return {
        'dq': df_dq,
        'dh': df_dh,
        'warnings': df_w,
        'start': start_time,
        'end': end_time,
        'fail_t': last_err_t if is_fatal else None,
        'fail_c': last_err_c if is_fatal else None
    }

# --- Plotting ---
@app.callback(
    [Output('convergence-graph', 'figure'),
     Output('warning-graph', 'figure'),
     Output('file-info', 'children'),
     Output('processing-output', 'children')],
    [Input('upload-zzd', 'contents'), Input('qtol-input', 'value'), Input('htol-input', 'value')],
    [State('upload-zzd', 'filename')]
)
def update_dashboard(contents, qtol, htol, filename):
    if not contents:
        return go.Figure(), go.Figure(), "No file selected", ""

    # 1. Get RAW BYTES
    _, content_str = contents.split(',')
    decoded_bytes = base64.b64decode(content_str)

    # 2. Pass BYTES to the optimized function (Do NOT .decode('utf-8'))
    data = extract_zzd_data(decoded_bytes)

    # 1. Convergence Plot
    c_fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.10,
                         subplot_titles=('DQ Convergence (Violations Only)', 'DH Convergence (Violations Only)'))

    # --- NEW: Pre-calculate total violations per node for sorting ---
    # We combine DQ and DH violations to find the "worst" nodes across both categories
    dq_counts = data['dq'][data['dq']['value'].abs() >= qtol]['node'].value_counts()
    dh_counts = data['dh'][data['dh']['value'].abs() >= htol]['node'].value_counts()

    # Combine counts (fill NaN with 0 for nodes that only violate one criteria)
    total_counts = dq_counts.add(dh_counts, fill_value=0).sort_values(ascending=False)
    sorted_nodes = total_counts.index.tolist()

    # --- Corrected Legend Logic ---
    seen_nodes = set() # Track nodes to ensure they appear in legend exactly once

    for df_key, row, val in [('dq', 1, qtol), ('dh', 2, htol)]:
        df = data[df_key]
        if not df.empty:
            df_filtered = df[df['value'].abs() >= val]

            for i, node in enumerate(sorted_nodes):
                nd = df_filtered[df_filtered['node'] == node]
                if nd.empty:
                    continue

                # Determine if this is the first time we are plotting this node
                # If it is, we show it in the legend.
                show_in_legend = False
                if node not in seen_nodes:
                    show_in_legend = True
                    seen_nodes.add(node)

                this_dq = int(dq_counts.get(node, 0))
                this_dh = int(dh_counts.get(node, 0))
                custom_label = f"{node} | DQ: {this_dq}, DH: {this_dh}"

                symbols = ['circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 'star', 'hexagram']
                colors = px.colors.qualitative.Dark24 + px.colors.qualitative.Alphabet

                c_fig.add_trace(go.Scattergl(
                    x=nd['time'],
                    y=nd['value'],
                    mode='markers',
                    name=custom_label,
                    legendgroup=node,
                    showlegend=show_in_legend, # Corrected: Shows for the first occurrence found
                    marker=dict(
                        symbol=symbols[i % len(symbols)],
                        color=colors[i % len(colors)],
                        size=8,
                        line=dict(width=1, color='DarkSlateGrey')
                    )
                ), row=row, col=1)

        # Static X-range based on parsed file bounds
        c_fig.update_xaxes(range=[data['start'], data['end']], row=row, col=1)

    # Row 1: DQ Tolerance
    c_fig.add_hline(y=qtol, line_dash="dot", line_color="black", line_width=1,
                    annotation_text=f"QTOL (+{qtol})", annotation_position="top right", row=1, col=1)

    # Row 2: DH Tolerance
    c_fig.add_hline(y=htol, line_dash="dot", line_color="black", line_width=1,
                    annotation_text=f"HTOL (+{htol})", annotation_position="top right", row=2, col=1)

    # 2. Warning Plot
    w_fig = make_subplots(rows=2, cols=1, row_heights=[0.7, 0.3], vertical_spacing=0.10,
                          subplot_titles=('Temporal Warning Distribution', 'Total Warning Counts'))

    if not data['warnings'].empty:
        df_w = data['warnings']

        # 1. Prepare unique codes and notes
        unique_codes = sorted(df_w['code'].unique())
        code_to_idx = {code: i for i, code in enumerate(unique_codes)}
        heatmap_notes = [WARNING_DESCRIPTIONS.get(c, "N/A") for c in unique_codes]

        # 2. Pre-calculate 2D Histogram counts manually
        # Create 100 bins for time (X) and 1 bin per code (Y)
        t_bins = np.linspace(data['start'], data['end'], 101)
        c_bins = np.arange(len(unique_codes) + 1)

        counts, x_edges, y_edges = np.histogram2d(
            df_w['time'],
            df_w['code'].map(code_to_idx),
            bins=[t_bins, c_bins]
        )

        # 3. Log-transform the Z data (counts)
        # We use log10(n + 1) to ensure 0 stays 0 and 1 is distinguishable
        # Transpose counts to match Plotly Heatmap [row, col] -> [y, x]
        z_log = np.log10(counts.T + 1)
        z_log[z_log == 0] = np.nan  # Transparent for zero values

        # 4. Create Note grid for customdata (mapping notes to the Y-axis)
        # Shape must match z_log [len(unique_codes) x 100]
        note_grid = np.array([[note] * 100 for note in heatmap_notes])

        # 1. Define Logarithmic Tick Marks for the Color Bar
        # This creates labels like 1, 10, 100, 1000 at the correct log positions
        max_val = counts.max()
        # Find the highest power of 10 needed
        max_log = int(np.ceil(np.log10(max_val))) if max_val > 0 else 1
        tick_vals = [np.log10(10**i + 1) for i in range(max_log + 1)]
        tick_text = [str(10**i) for i in range(max_log + 1)]

        # 2. Heatmap Trace with Custom Color Bar
        w_fig.add_trace(go.Heatmap(
            x=t_bins,
            y=unique_codes,
            z=z_log,
            colorscale='Viridis',
            hoverongaps=False,
            customdata=np.stack((counts.T, note_grid), axis=-1),
            colorbar=dict(
                title="Count",
                tickvals=tick_vals,
                ticktext=tick_text,
                thickness=15,
            ),
            hovertemplate=(
                "<b>Code: %{y}</b><br>" +
                "Time: ~%{x:.2f} hrs<br>" +
                "<b>Count: %{customdata[0]}</b><br>" +
                "Note: %{customdata[1]}<br>" +
                "<extra></extra>"
            )
        ), row=1, col=1)

        # 3. Bar Chart (Bottom)
        df_w['note'] = df_w['code'].map(lambda x: WARNING_DESCRIPTIONS.get(x, "N/A"))
        counts = df_w.groupby(['code', 'type', 'note'], observed=True).size().reset_index(name='count')
        counts = counts.sort_values('count', ascending=False)

        bar_colors = ['#e74c3c' if t == 'ERROR' else '#3498db' for t in counts['type']]

        w_fig.add_trace(go.Bar(
            x=counts['count'],
            y=counts['code'],
            orientation='h',
            marker_color=bar_colors,
            customdata=counts['note'],
            hovertemplate=(
                "<b>Code: %{y}</b><br>" +
                "Total Count: %{x}<br>" +
                "Note: %{customdata}<br>" +
                "<extra></extra>"
            ),
            text=counts['count'],
            textposition='auto'
        ), row=2, col=1)

    # --- Corrected Global Axis & Fatal Error Logic ---
    # Calculate duration and a 2% buffer
    duration = data['end'] - data['start']
    # Avoid buffer if duration is 0 to prevent errors
    buffer = duration * 0.02 if duration > 0 else 1.0

    # 1. Convergence Plot: Both rows are Time, so we can update all x-axes
    c_fig.update_xaxes(
        range=[data['start'] - buffer, data['end'] + buffer],
    )

    # Update DQ axis labels
    c_fig.update_yaxes(
        title_text="DQ (m³/s)",
        row=1, col=1
    )

    # Update DH axis labels
    c_fig.update_yaxes(
        title_text="DH (m)",
        row=2, col=1
    )

    c_fig.update_xaxes(
        title_text="Model Time (hr)",
        row=2, col=1
    )

    # Warning Plot Heatmap
    w_fig.update_xaxes(
        range=[data['start'] - buffer, data['end'] + buffer],
        row=1, col=1,
        title_text="Model Time (hr)",
    )

    w_fig.update_xaxes(
        row=2, col=1,
        title_text="Message Count",
    )

    # Apply Log Scale to Warning Count
    w_fig.update_xaxes(
        type="log",
        row=2, col=1,
        title_text="Message Count",
    )

    # 3. Fatal Error Line: Only add to subplots that use a Time x-axis
    if data['fail_t']:
        # Add to both rows of Convergence plot
        c_fig.add_vline(x=data['fail_t'], line_width=3, line_dash="dash", line_color="red",
                       annotation_text=f"FAIL: {data['fail_c']}")

        # Add ONLY to the top row of the Warning plot
        w_fig.add_vline(x=data['fail_t'], line_width=3, line_dash="dash", line_color="red",
                       annotation_text=f"FAIL: {data['fail_c']}", row=1, col=1)

    fig_title = f"ZZD Analysis: {filename}"
    c_fig.update_layout(margin=dict(l=60, r=40, t=40, b=40), showlegend=True)
    w_fig.update_layout(margin=dict(l=60, r=40, t=40, b=40), showlegend=False)

    status = f"Sim: {data['start']} to {data['end']} hrs"
    if data['fail_t']: status += f" | ⚠ FAILED AT {data['fail_t']}h"

    return c_fig, w_fig, filename, status

if __name__ == '__main__':
    app.run(debug=False)
