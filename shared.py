from pathlib import Path

import pandas as pd

app_dir = Path(__file__).parent
tips = pd.read_csv(app_dir / "tips.csv")

# EXCEL IMPORTS
xlsx_df = "data/2025/MP_Data.xlsx";

# FUNCTION
def wrangle(path):
    df = pd.read_excel(path)
    df['Council'] = df['Council'].fillna(method='ffill')
    df['Constituency'] = df['Constituency'].fillna(method='ffill')
    df['MP'] = df['MP'].fillna(method='ffill')
    df['Party'] = df['Party'].fillna('Pending')
    df['Gender'] = df['Gender'].fillna('Pending')
    df['Council'] = df['Council'].replace('(Thekerani)', 'Thyolo')
    df['Council'] = df['Council'].replace('Chikhwawa', 'Chikwawa')
    df['Region'] = "";
    df['District'] = df['Council'].str.split(' ', n=1).str[0]
    df['District'] = df['District'].replace('Luchenza', 'Thyolo')
    df['District'] = df['District'].replace('M’mbelwa', 'Mzimba')
    df['District'] = df['District'].replace('Nkhata', 'Nkhatabay')
    df['District'] = df['District'].replace('Mzuzu', 'Mzimba')

    # Mapping Regions to districts
    districts_regions = {'Mwanza': 'Southern', 'Ntcheu': 'Central', 'Neno': 'Southern', 'Nkhatabay': 'Northern', 'Chikwawa': 'Southern', 
                         'Nsanje': 'Southern', 'Nkhotakota': 'Central', 'Salima': 'Central', 'Mangochi': 'Southern', 'Machinga': 'Southern', 
                         'Dedza': 'Central', 'Karonga': 'Northern', 'Chitipa': 'Northern', 'Balaka': 'Southern', 'Zomba': 'Southern', 
                         'Mchinji': 'Central', 'Blantyre': 'Southern', 'Mzimba': 'Northern', 'Likoma': 'Northern', 'Rumphi': 'Northern', 
                         'Kasungu': 'Central', 'Mulanje': 'Southern', 'Thyolo': 'Southern', 'Chiradzulu': 'Southern', 'Lilongwe': 'Central', 
                         'Ntchisi': 'Central', 'Phalombe': 'Southern', 'Dowa': 'Central'}
    df['Region'] = df['District'].map(districts_regions)

    return df

df_final = wrangle(xlsx_df)

# SUMMARY 1: Council Summary
council_summary = pd.pivot_table(df_final, index=['Region', 'Council'], columns='Gender', aggfunc='size', fill_value=0).reset_index()
council_summary['Total'] = council_summary.sum(axis=1, numeric_only=True)
council_summary['%'] = ((council_summary["Female"]) / (council_summary["Total"])) * 100
council_summary = council_summary.sort_values(by='%', ascending=False)

# SUMMARY 1: District Summary
district_summary = pd.pivot_table(df_final, index=['Region', 'District'], columns='Gender', aggfunc='size', fill_value=0).reset_index()
district_summary['Total'] = district_summary.sum(axis=1, numeric_only=True)
district_summary['Female_percentage'] = ((district_summary["Female"]) / (district_summary["Total"])) * 100
district_summary['Female_percentage'] = district_summary["Female_percentage"].round()
district_summary = district_summary.sort_values(by='Female_percentage', ascending=False)

# district_summary['Voter_Empathy'] = ((district_summary['Number Of Registred Voters'] - district_summary['Total Number Voted']) / district_summary['Number Of Registred Voters']) * 100
# district_summary['Voter_Cast'] = ((district_summary['Total Number Voted'])) * 100
# district_summary['Voter_Turnout'] = (((district_summary['Total Number Voted']) / district_summary['Number Of Registred Voters']) * 100)
district_summary = district_summary.reset_index()
# district_summary = district_summary.rename(columns={'District Name': 'District_Name', 'Number Of Registred Voters' : 'Number_Of_Registred_Voters', 'Total Number Voted': 'Total_Number_Voted'})
# district_summary["District_Name"] = district_summary["District_Name"].astype(str)
# district_summary["Voter_Empathy"] = pd.to_numeric(district_summary["Voter_Empathy"], errors="coerce").round()
# district_summary["Voter_Turnout"] = pd.to_numeric(district_summary["Voter_Turnout"], errors="coerce").round()
# district_summary["Voter_Cast"] = pd.to_numeric(district_summary["Voter_Cast"], errors="coerce").round()
# district_summary = district_summary.sort_values(by='Voter_Empathy', ascending=False)
district_summary['Longtude'] = "";
district_summary['Latitude'] = "";

# Mapping latitude to districts
districts_longtudes = {'Blantyre': '35.0058', 'Lilongwe': '33.7833', 'Mzuzu': '34.0151', 'Zomba': '35.3192', 'Karonga': '33.9333', 
                           'Kasungu': '33.4833', 'Mangochi': '35.2667', 'Salima': '34.4333', 'Likoma': '34.7333', 'Dedza': '34.3333', 
                           'Nkhotakota': '34.3', 'Mchinji': '32.9', 'Nsanje': '35.2667', 'Mzimba': '33.6', 'Rumphi': '33.8667', 
                           'Ntcheu': '34.6667', 'Mulanje': '35.5081', 'Mwanza': '34.5178', 'Chitipa': '33.27', 'Nkhatabay': '34.3', 
                           'Ntchisi': '34', 'Dowa': '33.9167', 'Thyolo': '35.1333', 'Phalombe': '35.6533', 'Chiradzulu': '35.1833', 
                           'Machinga': '35.5167', 'Balaka': '34.9591', 'Neno': '34.6534', 'Chikwawa': '34.801'}
district_summary['Longtude'] = district_summary['District'].map(districts_longtudes)

# Mapping longtude to districts
districts_latitudes = {
        'Blantyre': '-15.7861', 'Lilongwe': '-13.9833', 'Mzuzu': '-11.4581', 'Zomba': '-15.3869', 'Karonga': '-9.9333', 'Kasungu': '-13.0333', 
        'Mangochi': '-14.4667', 'Salima': '-13.7833', 'Likoma': '-12.0667', 'Dedza': '-14.3667', 'Nkhotakota': '-12.9167', 
        'Mchinji': '-13.8167', 'Nsanje': '-16.9167', 'Mzimba': '-11.9', 'Rumphi': '-11.0167', 'Ntcheu': '-14.8333', 'Mulanje': '-16.0258', 
        'Mwanza': '-15.5986', 'Chitipa': '-9.7019', 'Nkhatabay': '-11.6', 'Ntchisi': '-13.3667', 'Dowa': '-13.6667', 'Thyolo': '-16.0667', 
        'Phalombe': '-15.8033', 'Chiradzulu': '-15.7', 'Machinga': '-14.9667', 'Balaka': '-14.9889', 'Neno': '-15.3981', 'Chikwawa': '-16.035'}
district_summary['Latitude'] = district_summary['District'].map(districts_latitudes)

# SUMMARY 2: Party Summary
party_gender_summary = pd.pivot_table(df_final, index=['Party'], columns='Gender', aggfunc='size', fill_value=0).reset_index()
party_gender_summary['Total'] = party_gender_summary.sum(axis=1, numeric_only=True)
party_gender_summary['%'] = (((party_gender_summary["Female"]) / (party_gender_summary["Total"])) * 100).round()
party_gender_summary = party_gender_summary.sort_values(by='%', ascending=False)

# SUMMARY 3: Region Summary
region_summary = pd.pivot_table(df_final, index=['Region'], columns='Gender', aggfunc='size', fill_value=0).reset_index()
region_summary['Total'] = region_summary.sum(axis=1, numeric_only=True)
region_summary['Female %'] = (((region_summary["Female"]) / (region_summary["Total"])) * 100).round()
region_summary['Male %'] = (((region_summary["Male"]) / (region_summary["Total"])) * 100).round()
region_summary['Pending %'] = (((region_summary["Pending"]) / (region_summary["Total"])) * 100).round()
region_summary = region_summary.sort_values(by='Female %', ascending=False)

# SUMMARY 4: Region by Party Summary
region_party_summary = pd.pivot_table(df_final, index=['Region'], columns='Party', aggfunc='size', fill_value=0).reset_index()
region_party_summary['Total'] = region_party_summary.sum(axis=1, numeric_only=True)
region_party_summary = region_party_summary.sort_values(by='Total', ascending=False)

# region_summary['Voter_Empathy'] = ((region_summary['Number Of Registred Voters'] - region_summary['Total Number Voted']) / region_summary['Number Of Registred Voters']) * 100
region_summary = region_summary.reset_index()
# region_summary = region_summary.rename(columns={'Number Of Registred Voters' : 'Number_Of_Registred_Voters', 'Total Number Voted': 'Total_Number_Voted'})
# region_summary = region_summary.sort_values(by='Voter_Empathy', ascending=False)

region_summary.to_excel("data/2025/mp_region_summary.xlsx", index=False)
region_party_summary.to_excel("data/2025/MP/party_region_summary.xlsx", index=False)
party_gender_summary.to_excel("data/2025/MP/party_gender_summary.xlsx", index=False)
council_summary.to_excel("data/2025/mp_council_summary.xlsx", index=False)
district_summary.to_excel("data/2025/mp_district_summary.xlsx", index=False)