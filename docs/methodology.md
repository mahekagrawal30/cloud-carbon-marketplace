# Methodology and limitations

## Calculation method

For every usage record, the prototype calculates estimated emissions as:

`estimated emissions (kg CO2e) = energy use (kWh) × regional carbon intensity (kg CO2e/kWh)`

The dashboard totals these estimates by cloud provider, service, region, and month. Tonnes of CO2e equal kilograms divided by 1,000.

## Recommendation method

The prototype uses transparent rules: high-carbon regions produce migration suggestions; always-on compute services produce right-sizing suggestions; and low-use storage produces lifecycle/archival suggestions. Estimated savings are illustrative percentages, not guaranteed outcomes.

## Limitations

- Usage data, electricity estimates, regional factors, carbon projects, and transactions are simulated.
- Static regional factors cannot replace provider-specific or time-based emissions information.
- The application does not connect to cloud accounts or payment systems.
- Carbon projects and certificates are demonstration records only; they do not convey ownership, retirement, or verification of a real credit.
