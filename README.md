# iDesignRES: Solar Energy Model

[![Docs](https://img.shields.io/badge/docs-stable-brightgreen)](https://molinuevo.github.io/molinuevosolar)

This README provides an overview of the iDesignRES Solar Energy Model within iDesignRES.

It is handled by Tecnalia and part of WP1, Task number Task 1.3.

## Purpose of the model

The solar power model provides time-series of annual thermal energy generation in Concentrating Solar Power (CSP) plants and electrical energy generation in large Photovoltaic (PV) plants on hourly basis, for a given NUTS2 region and a specific amount of investment in €, in MWp or in m2 for each of these technologies: CSP and PV. These profiles are provided aggregated at NUTS2 level and disaggregated at NUTS3 level, as well as the annual operational expenditures of both technologies

## Model design philosophy

The model firstly establishes the required area to deploy the given investment in each technology. Then, the most suitable available areas in the given region NUTS2 are selected. Once potential areas for each technology in each NUTS3 region are categorized by intervals of 100W/m2 of Global Horizontal Irradiance (GHI), those with higher GHI are selected until reaching the area, power capacity or investment required by the user at the input.

Since CSP technology requires higher solar radiation, CSP technology is prioritized when selecting the locations. Considering the solar resource on hourly basis of selected areas for each technology, simplified models are used to estimate annual thermal and electrical energy generation. These profiles are obtained at NUTS3 level and they are finally aggregated to provide them at NUTS2 level.

## Input to and output from the model

Input:

- NUTS2 region identifier.
- Investment in €, power capacity in MW or area in m2 to deploy CSP technology in the given NUTS2 region.
- Investment in €, power capacity in MWp or area in m2 to deploy PV plants in the given NUTS2 region.
- Optional: Financial and technical parameters of CSP and PV technologies in the market.
- Optional: Configuration parameters of areas selection criteria.

Output:

- Time-series of annual thermal energy generation and electrical energy generation on hourly basis aggregated at NUTS2 level.
- Time-series of annual thermal energy generation and electrical energy generation on hourly basis disaggregated at NUTS3 level.

## Implemented features

- Estimation of required area to deploy given investment or power capacity of CSP and PV technologies.

- Categorization of available areas in intervals of 100W/m2 of annual radiation for each NUTS3 region complying with selection criteria (maximum slope and land use restriction) for each technology.
  
  > It should be noted that in the current implementation stage, the model is only available for the use case in Spain. The other use cases for the project will also be included when appropriate.

- Selection of previously characterized areas with the highest solar radiation until reaching all the required area, prioritizing CSP and relegating PV in case of conflicts.

- For each selected areas estimation of annual thermal or electrical energy generation on hurly basis making use of simplified model of CSP and Solar PV models.
  
  - Aggregation of estimated generation profiles at NUTS3 and NUTS2 level.

## Core assumption

The main factor impacting on generation profile of CSP and solar PV plants is the available solar radiation. For this purpose, a selection of potential locations with the highest solar resource in the region for CSP and PV deployment is carried out, considering maximum slope and land use restrictions.

For thermal energy generation two different CSP technologies are considered: Parabolic Trough and Power Tower. For both of them specific different optical and thermal efficiencies are considered to estimate the thermal energy available in the solar field. Please notice that the thermal energy storage (TES) and power block are not modelled, since these depend on the energy dispatch at the output taking into account existing energy demand and other energy sources availability.

For electrical energy demand two different PV technologies are considered: single-axis tracking and fixed mounted systems. For both of them specific system losses are considered, in addition to shallow angle reflection, effects of changes in solar spectrum, and PV power dependence on irradiance and module temperature.

---

---

# Getting started

## System requirements

The recommended system requirements are as follows:

- Broadband Internet connection.

- *RAM memory*: it is recommended to have 32GB.

- *Operating system*: the models run on any operating system that supports Python and Poetry.

- *Python*: version 3.10.

- *Poetry*: version 2.1.1.

To make sure *Python 3.10* is installed.:

```
python --version
```

And to make make sure that *Poetry 2.1.1* is installed:

```
poetry --version
```

## Installation

Clone the repository in the desired directory:

```
cd directory
git clone https://github.com/iDesignRES/Tecnalia_Solar-Energy-Model
```

To install the Solar Energy Model, enter the following command:

```
poetry install
```

## Execution

Once installed, execute the *Solar Energy Model* entering the command:

```
poetry run python solar_power_plants.py <input_payload> <start_time> <end_time>
```

For example 

```
poetry run python solar_power_plants.py input.json 2019-01-01T00:00:00 2019-01-07T23:00:00
```

This command automatically runs the simulation, taking the necessary input data from the *[usecases](usecases)* folder and the *[input.json](input.json)* file.

## Testing and code coverage

The following tests have been defined for the model:

- Invalid payload.

- Payload with incorrect values.

- Valid payload.

- Correct execution tests, checking the correct output.

With a resulting code coverage of 94%:

| Name                  | Stmts   | Miss   | Cover   |
| --------------------- | ------- | ------ | ------- |
| modules/_ *init _*.py | 0       | 0      | 100%    |
| modules/constants.py  | 1       | 0      | 100%    |
| modules/model.py      | 245     | 13     | 95%     |
| modules/validator.py  | 184     | 11     | 94%     |
| **TOTAL**             | **430** | **24** | **94%** |

## Full example

To review a complete example of the model, access [this directory](example/README.md).

## Documentation

To review the complete model documentation, access [this directory](docs/README.md).