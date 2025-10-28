# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright (c) 2025 Tecnalia Research & Innovation

import pandas as pd
import pvlib

from pathlib import Path
from pyproj import Transformer
from solar_energy_model import constants


# Function: PV Power Plants -> Model -> Step 01 : Build the specific configuration
def s01BuildSpecificConfiguration(payload: dict) -> tuple:
    """Model Step 01: Build the specific configuration.

    Args:
        payload (dict): The process payload::
        
            Example: see "input.json" file in the root directory.
    
    Returns:
        tuple

    """

    print('Model: Step 01/>  Building the specific configuration...')
    areaAvailableTH = payload['area_total_thermal'] if payload['area_total_thermal'] is not None else None
    powerTH = payload['power_thermal'] if payload['power_thermal'] is not None else None
    capexTH = payload['capex_thermal'] if payload['capex_thermal'] is not None else None
    areaAvailablePV = payload['area_total_pv'] if payload['area_total_pv'] is not None else None
    powerPV = payload['power_pv'] if payload['power_pv'] is not None else None
    capexPV = payload['capex_pv'] if payload['capex_pv'] is not None else None
    systemCostTH = payload['system_cost_thermal']   # in €
    systemCostPV = payload['system_cost_pv']   # in €
    loss = payload['loss']   # in %
    effTH = payload['efficiency_thermal'] / 100
    effOp = payload['efficiency_optical'] / 100
    aperture = payload['aperture'] / 100
    tilt = payload['tilt']
    azimuth = payload['azimuth']
    tracking = payload['tracking_percentage'] / 100
    opexTH = payload['opex_thermal']    # in €/W
    opexPV = payload['opex_pv']  # in €/W
    minGhiTH = payload['min_ghi_thermal']    # in W/m2
    minGhiPV = payload['min_ghi_pv']    # in W/m2
    landUseTH = payload['land_use_thermal']    # in W/m2
    landUsePV = payload['land_use_pv']    # in W/m2
    convertCoord = True if int(payload['convert_coord']) == 1 else False
    year = int(payload['pvgis_year'])
    listParametersTH = [areaAvailableTH, powerTH, capexTH]
    listParametersPV = [areaAvailablePV, powerPV, capexPV]

    # Finish
    print('Model: Step 01/>  [OK]')
    return listParametersTH, listParametersPV, systemCostTH, systemCostPV, \
        landUseTH, landUsePV, minGhiTH, minGhiPV, effTH, effOp, aperture, \
        convertCoord, year, tilt, azimuth, tracking, loss, opexTH, opexPV


# Function: PV Power Plants -> Model -> Step 02 -> Load the previous result
def s02LoadPreviousResult(nutsId: str) -> tuple:
    """Model Step 02: Load the previous result.

    Args:
        nutsId (str): Identifier of NUTS2 region for which the analysis will be carried out.
    
    Returns:
        tuple

    """

    # Load the result file of the Solar preprocess por the use case
    print('Model: Step 02/>  Loading the result file of the Solar preprocess...')
    csvPath = Path(__file__).parent.parent / \
        'usecases' / f'{nutsId.upper()}.csv'

    # Load the thermal data
    print('Model: Step 02/>  Loading the thermal data...')
    dfScadaTH, dfScadaPV = None, None
    dfScadaTH = pd.read_csv(csvPath,
                            header=0,
                            encoding="ISO-8859-1",
                            delimiter=",",
                            decimal=".").sort_values(by='Median_Radiation',
                                                     ascending=False)

    # Load the photovoltaic data
    print('Model: Step 02/>  Loading the photovoltaic data...')
    dfScadaPV = pd.read_csv(csvPath,
                            header=0,
                            encoding="ISO-8859-1",
                            delimiter=",",
                            decimal=".").sort_values(by='Median_Radiation',
                                                     ascending=False)

    # Finish
    print('Model: Step 02/>  [OK]')
    return dfScadaTH, dfScadaPV


# Function: PV Power Plants -> Model -> Step 03 -> Calculate the available thermal area
def s03CalculateAvailableThermalArea(listParametersTH: list,
                                     systemCostTH: float,
                                     landUseTH: float) -> tuple:
    """Model Step 03: Calculate the available thermal area.

    Args:
        listParametersTH (list): The list of thermal parameters. Example::

            [
                None,
                10,
                None
            ]
        systemCostTH (float): The thermal system cost in €.
        landUseTH (int): Land use ratio of CSP technology in W/m2 to compute
            required area for a given CSP power capacity.
    
    Returns:
        tuple
    """

    print('Model: Step 03/>  Calculating the available thermal area...')
    areaTH, powerTH, capexTH = x03GetAvailableArea(parameters=listParametersTH,
                                                cost=systemCostTH,
                                                landUse=landUseTH)

    print('Model: Step 03/>  Area -> ' + str(areaTH))
    print('Model: Step 03/>  Power -> ' + str(powerTH))
    print('Model: Step 03/>  Capex -> ' + str(capexTH))

    # Finish
    print('Model: Step 03/>  [OK]')
    return areaTH, powerTH, capexTH


# Function: PV Power Plants -> Model -> Step 04 -> Calculate the available PV area
def s04CalculateAvailablePVArea(listParametersPV: list,
                                systemCostPV: float,
                                landUsePV: float) -> tuple:
    """Model Step 04: Calculate the available PV area.

    Args:
        listParametersPV (list): The list of PV parameters. Example::

            [
                None,
                200,
                None
            ]
        systemCostPV (float): The PV system cost in €.
        landUsePV (int): Land use ratio of PV technology in W/m2 to compute
            required area for a given PV power capacity.
    
    Returns:
        tuple
    """

    print('Model: Step 04/>  Calculating the available PV area...')
    areaPV, powerPV, capexPV = x03GetAvailableArea(parameters=listParametersPV,
                                                cost=systemCostPV,
                                                landUse=landUsePV)
    print('Model: Step 04/>  Area -> ' + str(areaPV))
    print('Model: Step 04/>  Power -> ' + str(powerPV))
    print('Model: Step 04/>  Capex -> ' + str(capexPV))

    # Finish
    print('Model: Step 04/>  [OK]')
    return areaPV, powerPV, capexPV


# Function: PV Power Plants -> Model -> Step 05 -> Calculate the thermal production
def s05CalculateThermalProduction(scadaTH: pd.DataFrame,
                                  scadaPV: pd.DataFrame,
                                  areaTH: float,
                                  minGhiTH: float,
                                  landUseTH: float,
                                  effTH: float,
                                  effOp: float,
                                  aperture: float,
                                  convertCoord: int,
                                  year: int) -> tuple:
    """Model Step 05: Calculate the thermal production.

    Args:
        scadaTH (DataFrame): The Dataframe corresponding to thermal scada.
        scadaPV (DataFrame): The Dataframe corresponding to PV scada.
        areaTH (float): The thermal area.
        minGhiTH (float): Minimum annual Global Horizontal Irradiance in
            kWh/m2 in a land area to install CSP systems.
        landUseTH (float): Land use ratio of CSP technology in W/m2 to compute
            required area for a given CSP power capacity.
        effTH (float): Thermal efficiency in % of collectors of CSP systems. 
        effOp (float): Amount of incoming solar radiation in % captured in
            the collectors of CSP systems.
        aperture (float): Aperture area in % of solar field of CSP systems.
        convertCoord (int): Convert coordinates expressed into EPSG:3035 to EPSG:4326.
        year (int): Year for calculate time-series hourly production.
    
    Returns:
        tuple
    """

    # Get the regions
    print('Model: Step 05/>  Obtaining the regions...')
    rowsTH, nameNuts2 = x04GetRegions(scada=scadaTH,
                                   area=areaTH,
                                   minGHI=minGhiTH)

    # Get the thermal production and save it to a dataframe
    print('Model: Step 05/>  Obtaining the thermal production...')
    prodTH = x05GetThermalProduction(rows=rowsTH,
                                     landUse=landUseTH,
                                     effTH=effTH,
                                     effOp=effOp,
                                     aperture=areaTH * aperture,
                                     convertCoord=convertCoord,
                                     year=year)
    print('Model: Step 05/>  Saving the thermal production in a DataFrame...')
    dfTH = (pd.DataFrame(prodTH).sum(axis=0))

    # Get the distribution
    print('Model: Step 05/>  Obtaining the distribution...')
    if not dfTH.empty:
        nuts2TH, potDistTH, areasDistTH = x07GetDistribution(rows=rowsTH,
                                                             label='thermal_power')

        # Remove areas used with TH power
        print('Model: Step 05/>  Removing areas used with thermal power...')
        for region in rowsTH:
            df = scadaPV.loc[(scadaPV['Region'] == region['Region']) & (
                scadaPV['Threshold'] == region['Threshold'])]
            df.loc[:, 'Area_m2'] -= region['Area_m2']
            scadaPV.loc[(scadaPV['Region'] == region['Region']) & (
                scadaPV['Threshold'] == region['Threshold'])] = df

    # Finish
    print('Model: Step 05/>  [OK]')
    return nuts2TH, rowsTH, potDistTH, dfTH, scadaPV


# Function: PV Power Plants -> Model -> Step 06 -> Calculate the PV production
def s06CalculatePVProduction(scadaPV: pd.DataFrame,
                             areaPV: pd.DataFrame,
                             minGhiPV: float,
                             landUsePV: float,
                             tilt: float,
                             azimuth: float,
                             tracking: float,
                             loss: float,
                             convertCoord: int,
                             year: int) -> tuple:
    """Model Step 06: Calculate the PV production.

    Args:
        scadaPV (DataFrame): The Dataframe corresponding to PV scada.
        areaPV (float): The PV area.
        minGhiPV (float): Minimum annual Global Horizontal Irradiance in kWh/m2
            in a land area to install PV systems.
        landUsePV (float): Land use ratio of PV technology in W/m2 to compute
            required area for a given PV power capacity.
        tilt (float): Tilt angle in º from horizontal plane.
        azimuth (float): Orientation (azimuth angle) of the (fixed) plane
            of array. Clockwise from north.
        tracking (float): Percentage in % of single-axis tracking systems from the
            total PV capacity. The rest is considered fixed mounted systems.
        loss (float): Percentage in % of power losses of PV systems. Please read the
            documentation to understand which other losses are already included in the model.
        convertCoord (int): Convert coordinates expressed into EPSG:3035 to EPSG:4326.
        year (int): Year for calculate time-series hourly production.
    
    Returns:
        tuple
    """

    # Get the regions
    print('Model: Step 06/>  Obtaining the regions...')
    rowsPV, nameNuts2 = x04GetRegions(scada=scadaPV, area=areaPV, minGHI=minGhiPV)

    # Get the PV production
    print('Model: Step 06/>  Obtaining the PV production...')
    prodPVTracking = x06GetPVProduction(rows=rowsPV,
                                        landUse=landUsePV,
                                        tilt=tilt,
                                        azimuth=azimuth,
                                        tracking=1,
                                        loss=loss,
                                        convertCoord=convertCoord,
                                        year=year)
    prodPVFixed = x06GetPVProduction(rows=rowsPV,
                                     landUse=landUsePV,
                                     tilt=tilt,
                                     azimuth=azimuth,
                                     tracking=0,
                                     loss=loss,
                                     convertCoord=convertCoord,
                                     year=year)
    prodPV = list(map(sum, zip(map(lambda x: x * tracking, prodPVTracking),
                  map(lambda x: x * (1 - tracking), prodPVFixed))))
    print('Model: Step 06/>  Saving the PV production in a DataFrame...')
    dfPV = (pd.DataFrame(prodPV).sum(axis=0))

    # Get the distribution
    print('Model: Step 06/>  Obtaining the distribution...')
    nuts2PV, potDistPV, areasDistPV = x07GetDistribution(rows=rowsPV,
                                                         label='pv_power')

    # Finish
    print('Model: Step 06/>  [OK]')
    return nameNuts2, nuts2PV, potDistPV, dfPV


# Function: PV Power Plants -> Model -> Step 07 -> Calculate the aggregated production
def s07CalculateAggregatedProduction(dfTH: pd.DataFrame,
                                     dfPV: pd.DataFrame,
                                     nameNuts2: str) -> pd.DataFrame:
    """Model Step 07: Calculate the aggregated production.

    Args:
        dfTH (DataFrame): The DataFrame corresponding to the thermal data.
        dfPV (DataFrame): The Dataframe corresponding to the PV data.
        nameNuts2 (str): The name of the NUTS2 region.
    
    Returns:
        pd.DataFrame
    """

    print('Model: Step 07/>  Calculating the aggregated production...')
    if not dfTH.empty:
        prodAgreggated = pd.concat([dfTH.reset_index(),
                                    dfPV.reset_index()],
                                   ignore_index=False,
                                   axis=1)
        prodAgreggated = prodAgreggated.drop(columns=['time'])
        prodAgreggated = prodAgreggated.set_index('time(UTC)')
        prodAgreggated.columns = ['Pthermal_' + str(nameNuts2),
                                  'Ppv_' + str(nameNuts2)]
        prodAgreggated.index = pd.to_datetime(prodAgreggated.index,
                                              format='%Y-%m-%d %H:%M:%S').round('h').strftime('%Y-%m-%d %H:%M:%S')
    else:
        prodAgreggated = pd.DataFrame(dfPV,
                                      columns=['Ppv_' + str(nameNuts2)])
        prodAgreggated.index = pd.to_datetime(
            prodAgreggated.index).round('h').strftime('%Y-%m-%d %H:%M:%S')

    # Finish
    print('Model: Step 07/>  [OK]')
    return prodAgreggated


# Function: PV Power Plants -> Model -> Step 08 -> Calculate the distributed production
def s08CalculateDistributedProduction(dfTH: pd.DataFrame,
                                      nuts2TH: pd.DataFrame,
                                      nuts2PV: pd.DataFrame) -> pd.DataFrame:
    """Model Step 08: Calculate the distributed production.

    Args:
        dfTH (DataFrame): The DataFrame corresponding to the thermal data.
        nuts2TH (DataFrame): The Dataframe corresponding to the NUTS2 thermal data.
        nuts2PV (DataFrame): The Dataframe corresponding to the NUTS2 PV data.
    
    Returns:
        pd.DataFrame
    """

    print('Model: Step 08/>  Calculating the distributed production...')
    if not dfTH.empty:
        nuts2TH = nuts2TH.add_suffix('_Pthermal')
        nuts2PV = nuts2PV.add_suffix('_Ppv')
        nuts2Dist = pd.concat([nuts2TH.reset_index(),
                               nuts2PV.reset_index()],
                              ignore_index=False,
                              axis=1)
        nuts2Dist = nuts2Dist.drop(columns=['time'])
        nuts2Dist = nuts2Dist.set_index('time(UTC)')
    else:
        nuts2PV = nuts2PV.add_suffix('_Ppv')
        nuts2Dist = nuts2PV
        nuts2Dist = nuts2Dist.rename_axis('time(UTC)')

    # Finish
    print('Model: Step 08/>  [OK]')
    return nuts2Dist


# Function: PV Power Plants -> Model -> Step 09 -> Save the results
def s09SaveResults(prodAgreggated: pd.DataFrame,
                   nuts2Dist: pd.DataFrame,
                   dfTH: pd.DataFrame,
                   potDistTH: pd.DataFrame,
                   potDistPV: pd.DataFrame,
                   opexTH: pd.DataFrame,
                   opexPV: pd.DataFrame) -> list:
    """Model Step 09: Save the results.

    Args:
        prodAgreggated (DataFrame): The DataFrame corresponding to aggregated production.
        nuts2Dist (DataFrame): The Dataframe corresponding to the NUTS2 distribution data.
        dfTH (DataFrame): The DataFrame corresponding to the thermal data.
        potDistTH (DataFrame): The DataFrame corresponding to the thermal distributed power.
        potDistPV (DataFrame): The DataFrame corresponding to the PV distributed power.
        opexTH (DataFrame): The DataFrame corresponding to the thermal Opex.
        opexPV (DataFrame): The DataFrame corresponding to the PV Opex.
    
    Returns:
        list
    """

    print('Model: Step 09/>  Saving the results...')
    prodAgreggated = prodAgreggated.reset_index()
    dfColumns = prodAgreggated.columns.tolist()
    dfColumns[1] = 'Pthermal'
    dfColumns[2] = 'Ppv'
    prodAgreggated.columns = dfColumns
    output = [prodAgreggated]

    namesNuts3 = list(
        dict.fromkeys([nuts2Dist.columns[col].rsplit('_')[0] for col in range(len(nuts2Dist.columns))]))
    for i in range(len(namesNuts3)):
        dfNuts3 = pd.DataFrame()
        nuts3Cols = [x for x in nuts2Dist if (x.startswith(namesNuts3[i]))]
        newNuts3Cols = [item.rsplit('_')[1] for item in nuts3Cols]
        dfNuts3[newNuts3Cols] = nuts2Dist[nuts3Cols]
        output.append(dfNuts3.reset_index())

    print('Model: Step 09/>  Combining the dictionaries...')
    potPV = {f'{k}_pv': v for k, v in potDistPV.items()}
    potTH = {f'{k}_thermal': v for k,
             v in potDistTH.items()} if not dfTH.empty else 0
    combinedDict = {**potTH, **potPV} if not dfTH.empty else {**potPV}

    print('Model: Step 09/>  Calculating the OPEX and saving...')
    opexTotTH, opexTotPV = x08CalculateOpex(dictData=combinedDict,
                                            opexTH=opexTH,
                                            opexPV=opexPV)
    combinedDict['opex_thermal'] = opexTotTH  # In €
    combinedDict['opex_pv'] = opexTotPV  # In €
    output.append(combinedDict)

    # Finish
    print('Model: Step 09/>  [OK]')
    return output


#####################################################################
######################## Auxiliary functions ########################
#####################################################################


# Auxiliary function 01: Get coordinates
def x01GetCoord(df: pd.DataFrame) -> tuple:
    """Auxiliary function 01: Get the coordinates.

    Args:
        df (DataFrame): The source DataFrame.
    
    Returns:
        tuple
    """

    sampleX = df['Median_Radiation_X']
    sampleY = df['Median_Radiation_Y']

    transformer = Transformer.from_crs("EPSG:3035",
                                       "EPSG:4326",
                                       always_xy=True)
    xy = transformer.transform(sampleX,
                               sampleY)
    return xy[0], xy[1]


# Auxiliary function 02: Get the thermal model
def x02ThermalModel(radiation: pd.DataFrame,
                    effTH: float,
                    effOp: float,
                    aperture: float) -> list:
    """Auxiliary function 02: Get the thermal model.

    Args:
        radiation (DataFrame): The radiation DataFrame.
        effTH (float): Thermal efficiency in % of collectors of CSP systems.
        effOp (float): Amount of incoming solar radiation in % captured in
            the collectors of CSP systems.
        aperture (float): Aperture area in % of solar field of CSP systems.
    
    Returns:
        list
    """

    return radiation * aperture * effTH * effOp / 1.0e+06  # in  MWh


# Auxiliary function 03: Get the available area
def x03GetAvailableArea(parameters: list,
                        cost: float,
                        landUse: float) -> tuple:
    """Auxiliary function 03: Get the available area.

    Args:
        parameters (list): The list of parameters.
        cost (float): The system cost.
        landUse (float): The land use ratio.
    
    Returns:
        tuple
    """

    index = next((i for i, value in enumerate(
        parameters) if value is not None), -1)
    if index == 2:
        capex = parameters[index]
        power = parameters[index] / (cost * 1.0e+06)  # in MW
        area = power * 1.0e+06 / landUse  # in m2
    elif index == 1:
        area = parameters[index] * 1.0e+06 / landUse  # in m2
        power = parameters[index]
        capex = power * cost * 1.0e+06
    else:
        area = parameters[0]  # en m2
        power = (area * landUse) / 1.0e+06  # in MW
        capex = power * cost * 1.0e+06

    return area, power, capex


# Auxiliary function 04: Get the regions
def x04GetRegions(scada: pd.DataFrame,
                  area: float,
                  minGHI: float) -> tuple:
    """Auxiliary function 04: Get the regions.

    Args:
        scada (DataFrame): The source DataFrame.
        area (float): The source area.
        minGHI (float): Minimum annual Global Horizontal Irradiance in kWh/m2.
    
    Returns:
        tuple
    """

    currentSum = 0
    nameNuts2 = None
    rows = []
    for index, row in scada.iterrows():
        if nameNuts2 is None:
            nameNuts2 = row['Region'][:-1]
        if row['Area_m2'] > 0 and row['Region'] != nameNuts2 and row['Threshold'] >= minGHI:
            if currentSum + row['Area_m2'] > area:
                row['Area_m2'] = area - currentSum
                currentSum += row['Area_m2']
                rows.append(row)
                break
            currentSum += row['Area_m2']
            rows.append(row)

    return rows, nameNuts2


# Auxiliary function 05: Get the thermal production
def x05GetThermalProduction(rows: list,
                            landUse: float,
                            effTH: float,
                            effOp: float,
                            aperture: float,
                            convertCoord: bool,
                            year: int) -> list:
    """Auxiliary function 05: Get the regions.

    Args:
        rows (list): The source list of rows.
        landUse (float): The land use ratio.
        effTH (float): Thermal efficiency in % of collectors of CSP systems.
        effOp (float): Amount of incoming solar radiation in % captured in
            the collectors of CSP systems.
        aperture (float): Aperture area in % of solar field of CSP systems.
        convertCoord (bool): Convert coordinates expressed into EPSG:3035 to EPSG:4326.
        year (int): Year for calculate time-series hourly production.
    
    Returns:
        list
    """

    production = []
    for region in rows:
        lon, lat = region['Median_Radiation_X'], region['Median_Radiation_Y']
        if convertCoord or lat > 180:
            lon, lat = x01GetCoord(region)

        factor = 1
        try:
            data, moths, inputs, metadata = pvlib.iotools.get_pvgis_tmy(latitude=lat,
                                                                        longitude=lon,
                                                                        outputformat='json',
                                                                        usehorizon=True,
                                                                        userhorizon=None,
                                                                        startyear=None,
                                                                        endyear=None,
                                                                        map_variables=True,
                                                                        timeout=30)
        except Exception as e:
            raise Exception(
                'Main/>  Could not get thermal production because the external server is not responding!')

        data.index = data.index.map(lambda x: x.replace(year=year))
        region['radiation'] = data['dni']
        region['temperature'] = data['temp_air']
        region['power_installed(kW)'] = (region['Area_m2'] * landUse) / 1.0e+06

        region['thermal_power'] = x02ThermalModel(radiation=data['dni'],
                                                  effTH=effTH,
                                                  effOp=effOp,
                                                  aperture=aperture) * factor
        production.append(region['thermal_power'])  # in MWh
    return production


# Auxiliary function 06: Get the PV production
def x06GetPVProduction(rows: list,
                       landUse: float,
                       tilt: float,
                       azimuth: float,
                       tracking: int,
                       loss: float,
                       convertCoord: bool,
                       year: int) -> list:
    """Auxiliary function 06: Get the PV production.

    Args:
        rows (list): The source list of rows.
        landUse (float): The land use ratio.
        tilt (float): Tilt angle in º from horizontal plane.
        azimuth (float): Orientation (azimuth angle) of the (fixed)
            plane of array. Clockwise from north.
        tracking (float): Percentage in % of single-axis tracking systems from the total
            PV capacity. The rest is considered fixed mounted systems.
        loss (float): Percentage in % of power losses of PV systems.
        convertCoord (bool): Convert coordinates expressed into EPSG:3035 to EPSG:4326.
        year (int): Year for calculate time-series hourly production.
    
    Returns:
        list
    """

    production = []
    for region in rows:
        lon, lat = region['Median_Radiation_X'], region['Median_Radiation_Y']
        if convertCoord:
            lon, lat = x01GetCoord(region)

        potMW = (region['Area_m2'] * landUse) / 1.0e+06
        region['power_installed(kW)'] = potMW

        # pvgis is limited in peakpower to 1.0e+08
        potMW = potMW / 1.0e+03 if potMW * 1.0e+03 > 1.0e+08 else potMW
        factor = 1.0e+03 if potMW * 1.0e+03 > 1.0e+08 else 1

        prod = []
        df, params, meta = pvlib.iotools.get_pvgis_hourly(latitude=lat,
                                                          longitude=lon,
                                                          start=year,
                                                          end=year,
                                                          raddatabase='PVGIS-SARAH3',
                                                          surface_tilt=tilt,
                                                          surface_azimuth=azimuth,
                                                          pvcalculation=True,
                                                          peakpower=potMW * 1.0e+03,
                                                          trackingtype=tracking,
                                                          loss=loss,
                                                          components=False)
        prod.append(df['P'])  # in Wh
        region['pv_power'] = (pd.DataFrame(prod).sum(
            axis=0)) * factor / 1.0e+06  # to MW
        production.append((pd.DataFrame(prod).sum(
            axis=0) * factor / 1.0e+06))  # to MkW
    return production


# Auxiliary function 07: Get the distribution
def x07GetDistribution(rows: list,
                       label: str) -> tuple:
    """Auxiliary function 07: Get the distribution.

    Args:
        rows (list): The source list of rows.
        label (str): The label.
    
    Returns:
        tuple
    """

    res = []
    for i in rows:
        if i['Region'] not in res:
            res.append(i['Region'])

    df = pd.DataFrame(rows)
    sumNuts = []
    sumAreas = []
    sumPots = []
    for i in res:
        nuts = df.loc[i == df['Region']][label]
        dfNuts = pd.DataFrame(nuts.tolist())
        sumNuts.append(dfNuts.sum())
        areasNuts3 = df.loc[i == df['Region']]['Area_m2']
        potNuts3 = df.loc[i == df['Region']]['power_installed(kW)']
        sumAreas.append(pd.DataFrame(areasNuts3.tolist()).sum())
        sumPots.append(pd.DataFrame(potNuts3.tolist()).sum())

    areas = dict(zip(res, [x[0] for x in sumAreas]))
    pots = dict(zip(res, [x[0] for x in sumPots]))

    nuts2 = pd.DataFrame(sumNuts,
                         index=res).transpose()
    nuts2 = nuts2.dropna(axis=1)
    nuts2.index = nuts2.index.strftime('%Y-%m-%d %H:%M:%S')
    return nuts2, pots, areas


# Auxiliary function 08: Calculate the OPEX
def x08CalculateOpex(dictData: dict,
                     opexTH: float,
                     opexPV: float) -> tuple:
    """Auxiliary function 08: Calculate the OPEX.

    Args:
        dictData (dict): The source dictionary.
        opexTH (float): The thermal Opex.
        opexPV (float): The PV Opex.
    
    Returns:
        tuple
    """

    totalTH = 0
    totalPV = 0
    for dKey, dValue in dictData.items():
        if 'thermal' in dKey:
            totalTH += dValue
        elif 'pv' in dKey:
            totalPV += dValue
    return totalTH * opexTH, totalPV * opexPV
