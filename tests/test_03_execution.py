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
import numpy as np
import pandas as pd

from pathlib import Path
from solar_power_plants import executeSolarEnergyModelProcess


TEST_INPUT_PATH = str(Path(__file__).parent / 'input_test.json')
TEST_OUTPUT_PATH = str(Path(__file__).parent / 'output_test.csv')


# Test -> First execution test for process
def test_firstExecutionForProcess():
    '''
    Test -> First execution test for process. The area, power and capex are null.
    Input parameters:
        None.
    '''

    exceptionsRaised = 0

    # Load the payload file
    with open(TEST_INPUT_PATH, 'r') as payloadFile:
        # Execute the process
        try:
            payload = json.load(payloadFile)
            payload['area_total_thermal'] = None
            payload['power_thermal'] = None
            payload['capex_thermal'] = None
            payload['area_total_pv'] = None
            payload['power_pv'] = None
            payload['capex_pv'] = None
            executeSolarEnergyModelProcess(payload,
                                           '2019-03-01T13:00:00',
                                           '2019-03-02T13:00:00')
        except:
            exceptionsRaised += 1

    assert exceptionsRaised == 0


# Test -> Second execution test for process
def test_secondExecutionForProcess():
    '''
    Test -> Second execution test for process. At least one of the area, power and
            capex values ​​is not null.
    Input parameters:
        None.
    '''

    exceptionsRaised = 0

    # Load the payload file
    with open(TEST_INPUT_PATH, 'r') as payloadFile:
        # Execute the process
        try:
            result = executeSolarEnergyModelProcess(json.load(payloadFile),
                                                    '2019-03-01T13:00:00',
                                                    '2019-03-02T13:00:00')
            assert result is not None
        except:
            exceptionsRaised += 1

    assert exceptionsRaised == 0


# Test -> Third execution test for process
def test_thirdExecutionForProcess():
    '''
    Test -> Third execution test for process to validate the output.
    Input parameters:
        None.
    '''

    exceptionsRaised = 0

    # Load the payload file
    with open(TEST_INPUT_PATH, 'r') as payloadFile:
        # Execute the process
        areEqual = True
        try:
            result = executeSolarEnergyModelProcess(json.load(payloadFile),
                                                    '2019-03-01T13:00:00',
                                                    '2019-03-02T13:00:00')
            dfResult = pd.DataFrame(result)
            with open(TEST_OUTPUT_PATH, 'r') as outputFile:
                dfTest = pd.read_csv(outputFile,
                                     header=0,
                                     encoding='ISO-8859-1',
                                     sep=',',
                                     decimal='.')
                dfTest['time(UTC)'] = pd.to_datetime(dfTest['time(UTC)'])

            # Compare both DataFrames
            thComparison = np.isclose(dfResult["Pthermal"],
                                      dfTest["Pthermal"])
            pvComparison = np.isclose(dfResult["Ppv"],
                                      dfTest["Ppv"])
            total = thComparison & pvComparison
            if False in total:
                raise Exception()
        except:
            exceptionsRaised += 1

    assert exceptionsRaised == 0
