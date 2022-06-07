#!/usr/bin/env python
# coding: utf-8

# ## The Americas COVID Dashboard
# 
# By: Rosmerry Izaguire, Shirsho Dasgupta and Albert Franquiz (2021)

# ### Notes:
# 
# Lacking a reliable, cohesive and unified database for demographic profiles and economic indicators of all the countries in the Americas, the team from the Miami Herald, el Nuevo Herald and McClatchy Washington Bureau used estimates and projections from a variety of sources to build their own database. 
# 
# Data for population, percentage of people living below the poverty line and percentage of people with healthcare coverage were sourced from the UN Economic Commission for Latin America and the Caribbean (ECLAC). In cases where the numbers for people living below the poverty line were not recorded by ECLAC, the team used data from the World Bank. 
# 
# The team used estimates from the International Monetary Fund’s World Economic Outlook Database for per capita Gross Domestic Product (GDP) and the ratio of public debt to GDP. Where figures were not available from the UN, the IMF or the World Bank, the team relied on latest statistics published by the Central Intelligence Agency’s World Factbook. 
# The team used ECLAC data to estimate Cuba’s per capita GDP, which is not recorded by the IMF. 
# 
# The U.S. Census Bureau was the source for data on the U.S. population, the percentage of people living in poverty and Puerto Rico’s population. For Puerto Rico’s GDP per capita, the team used World Bank data. The team relied on Statistics Canada to determine Canada’s population and percentage of Canadians living below the poverty line. The average per capita GDP in Latin America and the Caribbean ⁠— $8,870 ⁠— was determined by the World Bank and the average percentage of population living in poverty, 30.5 percent, was provided by ECLAC. 
# 
# The number for COVID cases and COVID-related deaths were taken from the World Health Organization/Pan American Health Organization. For data on vaccinations, the team used statistics compiled by Oxford University.
# 
# The automated dashboard is based on data from the 37 countries and dependencies in the Americas that are uniformly reporting numbers for vaccinations, COVID cases and deaths periodically, if not daily.

# Read the story: https://www.miamiherald.com/news/nation-world/world/americas/article251071689.html 
# View the dashboard: https://datawrapper.dwcdn.net/KtTbP/21/

# #### Sources:
# 
# ##### Demographic and economic data
# 
# UN ECLAC: https://www.cepal.org/en/publications/46688-social-panorama-latin-america-2020
# 
# World Bank: https://data.worldbank.org/indicator/SI.POV.NAHC?locations=ZJ
# 
# IMF World Economic Outlook: https://www.imf.org/en/Publications/WEO/weo-database/2020/October/weo-report?c=311,213,314,313,316,339,218,223,228,233,238,321,243,248,253,328,258,336,263,268,343,273,278,283,288,293,361,362,364,366,369,298,299,&s=NGDPDPC,GGXWDN_NGDP,GGXWDG_NGDP,&sy=2018&ey=2021&ssm=0&scsm=1&scc=0&ssd=1&ssc=0&sic=0&sort=country&ds=.&br=1
# 
# CIA World Factbook: https://www.cia.gov/the-world-factbook/
# 
# US Census Bureau: https://data.census.gov/cedsci/
# 
# Statistics Canada: https://www.statcan.gc.ca/eng/start
# 
# 
# ##### COVID cases, deaths and vaccinations
# 
# UN WHO/PAHO: https://ais.paho.org/phip/viz/COVID19Table.asp
# 
# Our World in Data/University of Oxford: https://ourworldindata.org/covid-vaccinations

# ### Importing libraries

# In[ ]:


import pandas as pd
import datetime as dt
import gspread


# In[ ]:


### Google API and credentials for daily scraping go here ###


# In[ ]:


tnow = dt.datetime.now()
print("Starting at ", tnow)


# In[ ]:


### ignore copy warning
pd.options.mode.chained_assignment = None  
# default = "warn"


# ### Creating master demographic table 

# In[ ]:


# reading master demographic spreadsheet; replace with path to spreadsheet if needed
master = pd.read_csv("countries_master.csv")

# cleaning up names of countries
master["NATION"][master["NATION"] == "Venezuela (Bolivarian Republic of)"] = "Venezuela" 
master["NATION"][master["NATION"] == "Bolivia (Plurinational State of)"] = "Bolivia"
master["NATION"][master["NATION"] == "United States of America"] = "United States"
master["NATION"][master["NATION"] == "Curaçao"] = "Curacao"
master["NATION"][master["NATION"] == "Saint Barthélemy"] = "Saint Barthelemy"

# changing for viz compatibility on datawrapper
master["NATION"][master["NATION"] == "Saint Martin (French part)"] = "Saint Martin"
master["NATION"][master["NATION"] == "Sint Maarten (Dutch part)"] = "Sint Maarten"
master["NATION"][master["NATION"] == "Bahamas"] = "The Bahamas"


# ### Creating vaccination table

# In[ ]:


# importing data for country vaccination numbers
vax_count = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv")

# dropping the daily and per population numbers
vax_count =  vax_count.drop(["daily_vaccinations_raw", "daily_vaccinations", "total_vaccinations_per_hundred", "people_vaccinated_per_hundred", "people_fully_vaccinated_per_hundred", "daily_vaccinations_per_million"], axis = 1)

# renaming columns for uniform format
vax_count.rename(columns = {"total_vaccinations":"TOTAL VACCINATIONS", "people_vaccinated":"PEOPLE VACCINATED", "people_fully_vaccinated":"PEOPLE FULLY VACCINATED","date":"LAST VACCINE UPDATE"}, inplace = True)

# changing for viz compatibility on datawrapper
vax_count["location"][vax_count["location"] == "Saint Martin (French part)"] = "Saint Martin"
vax_count["location"][vax_count["location"] == "Sint Maarten (Dutch part)"] = "Sint Maarten"
vax_count["location"][vax_count["location"] == "Bahamas"] = "The Bahamas"

# saving to a new table
vax_count = vax_count.sort_values("LAST VACCINE UPDATE").groupby("location").tail(1)

# converting dates to datetime type
vax_count["LAST VACCINE UPDATE"] = vax_count["LAST VACCINE UPDATE"].astype("datetime64[ns]")

# removing time stamp
vax_count["LAST VACCINE UPDATE"] = [time.date() for time in vax_count["LAST VACCINE UPDATE"]]


# ### Joining master demographic table to vaccination table 

# In[ ]:


vax_pop = master.join(vax_count.set_index("location"), on = "NATION", how = "left")

# calculating the share of those vaccinated
vax_pop["PEOPLE VACCINATED PERCENT"] = round(vax_pop["PEOPLE VACCINATED"] / vax_pop["POPULATION"] * 100, 2)
vax_pop["PEOPLE FULLY_VACCINATED PERCENT"] = round(vax_pop["PEOPLE FULLY VACCINATED"] / vax_pop["POPULATION"] * 100, 2)


# ### Creating vaccine manufacturers table

# In[ ]:


# importing the data for vaccination manufacturers
vax_type = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/locations.csv")

# dropping the vaccine numbers
vax_type =  vax_type.drop(["iso_code", "last_observation_date", "source_name", "source_website"], axis = 1)

# changing for viz compatibility on datawrapper
vax_type["location"][vax_type["location"] == "Bahamas"] = "The Bahamas"
vax_type["location"][vax_type["location"] == "Saint Martin (French part)"] = "Saint Martin"
vax_type["location"][vax_type["location"] == "Sint Maarten (Dutch part)"] = "Sint Maarten"

# renaming columns for uniform format
vax_type.rename(columns = {"vaccines":"TYPE OF VACCINE"}, inplace = True)


# ### Joining manufacturers and vaccinations-demographics table

# In[ ]:


vaccinations = vax_pop.join(vax_type.set_index("location"), on = "NATION", how = "left")


# ### Creating COVID cases and deaths table

# In[ ]:


# importing case data
cases = pd.read_csv("https://covid19.who.int/WHO-COVID-19-global-table-data.csv", skiprows = [1])

# cleaning up names of countries
cases["Name"][cases["Name"] == "Venezuela (Bolivarian Republic of)"] = "Venezuela" 
cases["Name"][cases["Name"] == "Bolivia (Plurinational State of)"] = "Bolivia"
cases["Name"][cases["Name"] == "United States of America"] = "United States"
cases["Name"][cases["Name"] == "Curaçao"] = "Curacao"
cases["Name"][cases["Name"] == "Saint Barthélemy"] = "Saint Barthelemy"

# changing for viz compatibility on datawrapper
cases["Name"][cases["Name"] == "Bahamas"] = "The Bahamas"
cases["Name"][cases["Name"] == "Saint Martin (French part)"] = "Saint Martin"
cases["Name"][cases["Name"] == "Sint Maarten (Dutch part)"] = "Sint Maarten"

# dropping extra columns
cases =  cases.drop(["WHO Region", "Cases - cumulative total per 100000 population", "Cases - newly reported in last 7 days", "Cases - newly reported in last 7 days per 100000 population", "Cases - newly reported in last 24 hours", "Deaths - cumulative total per 100000 population", "Deaths - newly reported in last 7 days", "Deaths - newly reported in last 7 days per 100000 population", "Deaths - newly reported in last 24 hours"], axis = 1)

# renaming columns for uniform format
cases.rename(columns = {"Cases - cumulative total" : "TOTAL CASES", "Deaths - cumulative total" : "TOTAL DEATHS"}, inplace = True)


# ### Joining vaccinations-demographics-manufacturers table and COVID cases-deaths table

# In[ ]:


final_vax = vaccinations.join(cases.set_index("Name"), on = "NATION", how = "left")

# dropping extra columns
final_vax =  final_vax.drop(["iso_code"], axis = 1)

# calculating the per capita rates
final_vax["TOTAL CASES PER THOUSAND"] = round(final_vax["TOTAL CASES"] / final_vax["POPULATION"] * 1000, 2)
final_vax["TOTAL DEATHS PER THOUSAND"] = round(final_vax["TOTAL DEATHS"] / final_vax["POPULATION"] * 1000, 2)

# replacing NaN values with zero; this is for Datawrapper to read
final_vax.fillna(0, inplace = True)

# converting back to string for export  
final_vax["LAST VACCINE UPDATE"] = final_vax["LAST VACCINE UPDATE"].astype(str)


# ### Exporting master spreadsheet to CSV

# In[ ]:


# exporting to csv; replace with path if necessary
final_vax.to_csv("latam_vax.csv", index = False)

sheet.update([final_vax.columns.values.tolist()] + final_vax.values.tolist(), value_input_option = "USER_ENTERED")

tnow = dt.datetime.now()
print ("Lat Am  file updated at ", tnow)

