# AppStoreLocalizationUploader
A tool for fast update version localizations for your application in the app store

You need to generate Team Auth Key *.p8 
In the root make .env file with next parameters: 

KEY_ID=XXXXXXXXXXX

ISSUER_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

PATH_TO_KEY=AuthKey_XXXXXXXXXX.p8

Also, you need to download from Google Sheets 
file TestLocalization.xlsx.

Which contains 'locale', 'promotionalText' and 'whatsNew' data.
with same locale in JSON files contained in data folder.