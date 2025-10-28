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

import json
import pandas as pd
import sys

from datetime import datetime
from solar_energy_model import constants
from solar_energy_model import model
from solar_energy_model import validator


# Function: Execute the Model
def executeModel(modelPayload: dict) -> list:
    """Function to execute the Solar Energy Model.

    Args:
        modelPayload (dict): The dictionary with the Model input payload::

            Example: see "input.json" file in the root directory.
    
    Returns:
        list

    """

    print('Main/>  Executing the Solar Energy Model (please wait)...')
    print('')
    listParametersTH, listParametersPV, systemCostTH, systemCostPV, \
        landUseTH, landUsePV, minGhiTH, minGhiPV, effTH, effOp, aperture, \
        convertCoord, year, tilt, azimuth, tracking, loss, opexTH, opexPV = model.s01BuildSpecificConfiguration(
            modelPayload)
    print('')
    scadaTH, scadaPV = model.s02LoadPreviousResult(modelPayload['nutsid'])
    print('')
    areaTH, powerTH, capexTH = model.s03CalculateAvailableThermalArea(listParametersTH,
                                                                      systemCostTH,
                                                                      landUseTH)
    print('')
    areaPV, powerPV, capexPV = model.s04CalculateAvailablePVArea(
        listParametersPV, systemCostPV, landUsePV)
    print('')
    nuts2TH, rowsTH, potDistTH, dfTH, scadaPV = model.s05CalculateThermalProduction(scadaTH,
                                                                                    scadaPV,
                                                                                    areaTH,
                                                                                    minGhiTH,
                                                                                    landUseTH,
                                                                                    effTH,
                                                                                    effOp,
                                                                                    aperture,
                                                                                    convertCoord,
                                                                                    year)
    print('')
    nameNuts2, nuts2PV, potDistPV, dfPV = model.s06CalculatePVProduction(scadaPV,
                                                                         areaPV,
                                                                         minGhiPV,
                                                                         landUsePV,
                                                                         tilt,
                                                                         azimuth,
                                                                         tracking,
                                                                         loss,
                                                                         convertCoord,
                                                                         year)
    print('')
    prodAggregated = model.s07CalculateAggregatedProduction(dfTH,
                                                            dfPV,
                                                            nameNuts2)
    print('')
    nuts2Distrib = model.s08CalculateDistributedProduction(dfTH,
                                                           nuts2TH,
                                                           nuts2PV)
    print('')
    output = model.s09SaveResults(prodAggregated,
                                  nuts2Distrib,
                                  dfTH,
                                  potDistTH,
                                  potDistPV,
                                  opexTH,
                                  opexPV)
    print('')
    return output


# Function: Execute the Solar Energy Model process
def executeSolarEnergyModelProcess(processPayload: dict,
                                   startTime: str,
                                   endTime: str) -> dict:
    """Function to execute the Solar Energy Model process.

    Args:
        processPayload (dict): The dictionary with the process input payload::

            Example: see "input.json" file in the root directory.

        startTime (str): The start datetime, e.g., "2019-03-01T13:00:00".
        endTime (str): The end datetime, e.g., "2019-03-02T13:00:00".
    
    Returns:
        dict

    """

    try:
        # Execute the Model
        print(
            'Main/>  *** Solar Energy Model process [version ' + constants.VERSION + '] ***')
        output = executeModel(processPayload)

        # Return the result (filtered)
        result = output[0]
        result['time(UTC)'] = pd.to_datetime(result['time(UTC)'])
        start = pd.to_datetime(datetime.strptime(
            startTime, '%Y-%m-%dT%H:%M:%S'))
        end = pd.to_datetime(datetime.strptime(endTime, '%Y-%m-%dT%H:%M:%S'))
        resultFiltered = result[(result['time(UTC)'] >= start) & (
            result['time(UTC)'] <= end)].copy()
        resultFiltered['Ppv'] = resultFiltered['Ppv'].apply(
            lambda x: float(str(x).replace(',', '.')))
        resultFiltered['Pthermal'] = resultFiltered['Pthermal'].apply(
            lambda x: float(str(x).replace(',', '.')))
        negativeValues = validator.validateProcessOutput(resultFiltered)
        print('Main/>  Validating the output...')
        if negativeValues:
            raise Exception('Main/>  The output contains negative values!')
        print('Main/>  The output has no negative values.')
        print('Main/>  [OK]')
        return resultFiltered.to_dict(orient='list')
    except Exception as error:
        print('Main/>  An error occurred executing the Solar Energy Model process!')
        print(error)


# Function: Main
def main():
    """Main function.

    Args:
        sys.argv[0] (str): The current file name, e.g., "solar_power_plants.py".
        sys.argv[1] (str): The process input data file path, e.g., "input.json".
        sys.argv[2] (str): The start datetime, e.g., "2019-03-01T13:00:00".
        sys.argv[3] (str): The end datetime, e.g., "2019-03-02T13:00:00".
    
    Returns:
        None

    """

    try:
        # Validate the command line parameters
        validator.validateCommandLineParameters(sys.argv)

        # Load the process payload
        print('Main/>  Loading the process payload...')
        with open(sys.argv[1].strip(), 'r') as payloadFile:
            processPayload = json.load(payloadFile)

        # Validate the process payload
        processPayload = validator.validateProcessPayload(processPayload)
        print('Main/>  Input data validation OK!...')

        # Execute the process
        print('Main/>  Loading the Model...')
        executeSolarEnergyModelProcess(processPayload,
                                       sys.argv[2],
                                       sys.argv[3])
    except Exception as exception:
        print(f'{exception}')


if __name__ == "__main__":
    main()
