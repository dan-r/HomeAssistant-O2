# O2 for Home Assistant

An unofficial integration for fetching O2 allowance data.

This is currently a work-in-progress.

## Installation

### HACS
This is the recommended installation method.
1. Add this repository to HACS as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories)
2. Search for and install the O2 (UK) addon from HACS
3. Restart Home Assistant

### Manual
1. Download the [latest release](https://github.com/dan-r/HomeAssistant-O2/releases)
2. Copy the contents of `custom_components` into the `<config directory>/custom_components` directory of your Home Assistant installation
3. Restart Home Assistant


## Setup
From the Home Assistant Integrations page, search for and add the O2 (UK) integration.

## Update Time
Currently all data is updated every 30 minutes.
