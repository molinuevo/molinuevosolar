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

from pathlib import Path
from solar_energy_model import validator


TEST_INPUT_PATH = str(Path(__file__).parent / 'input_test.json')


# Test -> Invalid payload
def test_invalidPayload():
    '''
    Test -> Invalid payload.
    Input parameters:
        None.
    '''

    exceptionsRaised = 0

    # Load the payload file
    with open(TEST_INPUT_PATH, 'r') as payloadFile:
        processPayload = json.load(payloadFile)
        for key in processPayload:
            payloadCopy = processPayload.copy()
            del payloadCopy[key]
            try:
                validator.validateProcessPayload(payloadCopy)
            except Exception as e:
                exceptionsRaised += 1

    assert exceptionsRaised > 0


# Test -> Wrong values in the payload
def test_wrongValuesPayload():
    '''
    Test -> Wrong values in the payload.
    Input parameters:
        None.
    '''

    exceptionsRaised = 0

    # Load the payload file
    with open(TEST_INPUT_PATH, 'r') as payloadFile:
        processPayload = json.load(payloadFile)

        for key in processPayload:
            payloadCopy = processPayload.copy()
            payloadCopy[key] = 'ES70' if key == 'nutsid' else -10
            try:
                validator.validateProcessPayload(payloadCopy)
            except Exception as e:
                exceptionsRaised += 1

    assert exceptionsRaised > 0


# Test -> Valid payload
def test_validPayload():
    '''
    Test -> Valid payload.
    Input parameters:
        None.
    '''

    exceptionsRaised = 0

    # Load the payload file
    with open(TEST_INPUT_PATH, 'r') as payloadFile:
        processPayload = json.load(payloadFile)
        try:
            validator.validateProcessPayload(processPayload)
        except Exception as e:
            exceptionsRaised += 1

    assert exceptionsRaised == 0
