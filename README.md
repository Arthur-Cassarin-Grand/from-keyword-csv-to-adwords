# Create an Adwords Campaign from a keywords list CSV file

From a keywords list extract from a SEO software like Yooda or SEM Rush, **generate campaigns, ads groups and add keywords to them**. It's really helpful to create a lot of campaigns like products families for e-commerce websites.

This CSV file sample contains the required columns, but you can keep other columns like "Search Volume", "CPC", or so into your CSV file.

| Request        | Group               | Targeting | Campaign                 |
|----------------|---------------------|-----------|--------------------------|
| First keyword  | My first ads group  | Broad     | [EN] My Adwords Campaign |
| Second Keyword | My second ads group | Phrase    | [EN] My Adwords Campaign |
| Third Keyword  | My third ads group  | Exact     | [EN] My Adwords Campaign |

**You can execute the script more than one time if you update your CSV file.**
It will add the campaigns, ads groups and keywords that doesn't exists yet.

You can edit headings mapping by with the `headings_map` from the main.py to match your CSV headings (according to your language).
You can do the same for targeting settings with the `targeting_map` variable.
Don't use spaces in headings or you'll have a `KeyError exception` (will be fix ASAP).

**This script does not create ads**, just campaigns, ads group and keywords in them.

## Librairies used

This script uses the googleads API library from Google that you can find here : https://github.com/googleads/googleads-python-lib

Reading the library's doc will be very helpful.

You can install it by typing (assuming you're using Python 3.X) : `pip3 install googleads` or `pip install googleads` if Python 3 is your default version.

## Configure OAuth 2 authentification for Google Adwords API

You must use the 0Auth 2 acces granted by Google.
You can follow the documentation here : https://github.com/googleads/googleads-python-lib/wiki/API-access-using-own-credentials-(installed-application-flow)

I assume you already have a project into the Google Cloud Plateform (it's free).

Next :

- Create a `googleads.yaml` file into your root directory project using this model : https://raw.githubusercontent.com/googleads/googleads-python-lib/master/googleads.yaml

- Download the generate_refresh_token.py file (for Python 3.X) here : https://github.com/googleads/googleads-python-lib/releases (it is provided into this repo)

- Create an 0Auth 2.0 here : https://console.developers.google.com/apis/credentials

- Specify "Other" as application type (Google does not accept Web app applications)

- Copy your CLIENT_ID and your CLIENT_SECRET keys.

- Type : `python3 generate_refresh_token.py --client_id CLIENT_ID --client_secret CLIENT_SECRET`

- Go on the returned URL with a browser.

- Edit your `googleads.yaml` file with this values : client_id, client_secret and refresh_token.

- Add your developer_token into the `googleads.yaml`. You can ask it to Google API team into your Adwords's CM account, into *API Center* > *Developper token*. The average waiting time for an answer is 48 hours. Fill the form right because Google ask many questions, the way you answer them will grant you the right access you need. A *Standard access* is enough for this script.

## How to start the script

`python3 main.py -c data.csv -a 123-456-7891 -d ';'`

```
usage: main.py [-h] -csv CSV -idadwords IDADWORDS -delimiter DELIMITER

optional arguments:
  -csv CSV, --csv CSV, -c CSV
                        The CSV file that contains keywords, ads groups and campaigns.
  -idadwords IDADWORDS, --idadwords IDADWORDS, -a IDADWORDS
                        The account Adwords that will receive new keywords, ads groups and campaigns. 
                        I.e. 123-456-7891 or 1234567891
  -delimiter DELIMITER, --delimiter DELIMITER, -d DELIMITER
                        CSV delimiter, for exemple , or ;
```

## What this Google Adwords API Python's script can teach you

I had a hard time to setup Google API account, so I hope my script will help beginners to start developping with Google Adwords API for Python. Look at the main.py file.

Here's the questions I asked myself and what you can learn by reading my code :

- How to use a Manager Customer Account into Google Adwords API ?
- How to set a customer ID as a parameter into a Google Adwords API function ?
- How to handle errors into Google Adwords API ?