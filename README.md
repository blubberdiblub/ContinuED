# ContinuED

[*Elite Dangerous*](https://www.elitedangerous.com/) journal log processing tool
heavily inspired by [*Elite Dangerous Market Connector (EDMC)*](https://github.com/EDCD/EDMarketConnector)

The project name is a reference to the *Continued* event in the journal log.

# Project goals

* Allow plugins to act on journal events as neatly and as forward compatible as feasible.
* Digest events, clean up structural inconsistencies and messiness as much as possible and deliver them as high-level objects instead.
* Use modern techniques, such as Trio's async paradigm throughout the code and a Qt based GUI.
* Use modern Python features and coding style.
