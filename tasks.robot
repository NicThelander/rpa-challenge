*** Settings ***
Library           OperatingSystem
Library           Process

*** Tasks ***
Run Main Script
    Change Directory    ${CURDIR}/src
    ${result} =    Run Process    python    ${CURDIR}/main.py    shell=${True}
    Log    ${result.stdout}
    Log    ${result.stderr}