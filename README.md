## PyNmon2Highcharts

   Generate Highcharts graphics from NMON output log.

      AIX:   http://www.ibm.com/developerworks/aix/library/au-analyze_aix/
      Linux: http://nmon.sourceforge.net/pmwiki.php

## Overview

   This tool was made to replicate the reports generated by Nmon Analyzer. (http://www.ibm.com/developerworks/aix/library/au-nmon_analyser/). While using the same input file, PyNmon2Highcharts with the use of fidyeates/PyHighcharts wrapper (https://github.com/fidyeates/PyHighcharts forked for my own needs) use Highchart charts (http://www.highcharts.com/) for the same kind of graphics.

   This project was mainly inspired by https://github.com/madmaze/pyNmonAnalyzer.
   
## Requirements

   * Python 3.x + Internet Browser (Firefox, Chrome, etc.)
   * Nmon output log (AIX or Linux)

## Usage

   ```
   python PyNmon2Highcharts.py [-h] -i INPUT
   ```

## Install

   1) Install Python 3.3.* (http://www.python.org/download/)

   2) Get https://github.com/DarkAngelStrike/PyHighcharts and into Python installation folder in "Lib\site-packages".

   3) Get https://github.com/DarkAngelStrike/PyNmon2Highcharts
   
## Example

   ```
   python PyNmon2Highcharts.py -i test.nmon
   ```

   This will generate, in the same directory, and open in the default browser a web page with the same name as the input file with the html extension. (test.nmon.html)

## Samples

   For these samples the nmon output from this project was used:

      https://github.com/madmaze/pyNmonAnalyzer/blob/master/test.nmon

   Here is screenshots from excel file generated with Nmon Analyzer. (test.nmon.xlsx)

![test.nmon.xlsx.001.png](https://raw.github.com/DarkAngelStrike/PyNmon2Highcharts/master/Samples/test.nmon.xlsx.001.png)
![test.nmon.xlsx.002.png](https://raw.github.com/DarkAngelStrike/PyNmon2Highcharts/master/Samples/test.nmon.xlsx.002.png)
![test.nmon.xlsx.003.png](https://raw.github.com/DarkAngelStrike/PyNmon2Highcharts/master/Samples/test.nmon.xlsx.003.png)

   Here is screenshots from the html file generated with PyNmon2Highcharts.py (test.nmon.html)
   
![test.nmon.html.001.png](https://raw.github.com/DarkAngelStrike/PyNmon2Highcharts/master/Samples/test.nmon.html.001.png)
![test.nmon.html.002.png](https://raw.github.com/DarkAngelStrike/PyNmon2Highcharts/master/Samples/test.nmon.html.002.png)
![test.nmon.html.003.png](https://raw.github.com/DarkAngelStrike/PyNmon2Highcharts/master/Samples/test.nmon.html.003.png)
![test.nmon.html.004.png](https://raw.github.com/DarkAngelStrike/PyNmon2Highcharts/master/Samples/test.nmon.html.004.png)
![test.nmon.html.005.png](https://raw.github.com/DarkAngelStrike/PyNmon2Highcharts/master/Samples/test.nmon.html.005.png)

## Warning 

   Be aware that Highcharts disallows commercial use of there products. (http://www.highcharts.com/license). But you can use Highcharts for a personal or non-profit project for free under the Creative Commons Attribution-NonCommercial 3.0 License.

   ```
   PyNmon2Highcharts
   -----------------
   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
   ```