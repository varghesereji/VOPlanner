# VOPlanner
A tool to plan astronomical observation with Astroplan.

# Install

Run the following command in terminal

```bash
pip install git+https://github.com/varghesereji/VOPlanner.git

# Usage

Download the config file from
[Here](https://github.com/varghesereji/VOPlanner/blob/main/src/voplanner/config/plan_config.config)

Create the target list in the format of [this]() file and save as csv file. Add the filename in the config file with

```bash
TARGETS =

Save the config file. Then run the following command in terminal

```bash

voplanner plan_config.config


