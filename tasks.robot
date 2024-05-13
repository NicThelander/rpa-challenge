*** Settings ***
Library           main

*** Tasks ***
Minimal Task
    ${search_query}=    Set Variable    your_search_query
    ${months}=    Set Variable    your_months_value
    minimal_task    ${search_query}    ${months}