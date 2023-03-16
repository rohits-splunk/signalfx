# Splunk O11y Org token Rotation 
# Description

This is a python script which automatically rotates the org token in a Splunk observability realm by comparing the number of days remaining( From the current date) for a token to expire and number of days supplied as an argument(-d) . If number of days for token expiry are less than number of days supplied with "-d" the script will rotate the tokens with a grace period(days) which is also supplied at script run ( -g)  . Most importantly , Please use -n option to dry run the script to see the tokens which are going to get rotated, the dry run will not change anything in your environment. The scripts expects some required arguments . Please run with -h option to learn more. Before running this script in Production environment, try it out by creating some sample org tokens in a trial Splunk O11y org. Link to request : [Splunk O11y Trial](https://www.splunk.com/en_us/download/o11y-cloud-free-trial.html?utm_campaign=google_amer_en_search_brand&utm_source=google&utm_medium=cpc&utm_content=O11y_Cloud_Trial&utm_term=splunk%20observability&_bk=splunk%20observability&_bt=519215939673&_bm=p&_bn=g&_bg=111780047679&device=c&gclid=CjwKCAjw_MqgBhAGEiwAnYOAemEpo0Y04A9KtTe57d-Ln66LS6svOmPW48IpG3NQ_Afz6A6EhN5kTBoCRNAQAvD_BwE)

## Installation

```bash
pip3 install pandas
```

## Usage

```python
# Get help 
token_rotation.py -h

# Dry run . Replace with an actual API token. Remove -n to actually run the script to rotate the tokens.
token_rotation.py -a xxxxxxxxxxxx -r us1 -d 40 -g 50 -t -n

```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Caution:
1) Please run the script using a trial API token by creating some test org tokens in the Trial account.
2) If Running in the Production environment , please consider running with -n ( dry run ) to see the proposed changes. 
