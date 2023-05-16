# Auctions Alert
Project to send alerts and notifications of auctions that users have interest.

## What do you need to run this project?
- Python 3.9.7 (recomended), this was the default Python version that the project was created.
- Python virtual environment
- SMTP email allowed to send emails from apps
- Create a folder called `data` with the files `users.csv` and `filters.csv`


### Installing Python 3.9.7
Please follows this tutorial to install Python 3.9.7 if needed
- Windows and MacOS please download and install the from the [python.org](https://www.python.org/downloads/release/python-397/)
- Ubuntu/Linux please follows this [tutorial](https://gist.github.com/vitorpohlenz/4cf5bd9702ec12acf92862e8382feb92)


### Installing Python virtual environment
Please follows this tutorial to install virtual environment in Python
- [Install virtualenv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)


### SMTP email allowed to send emails from apps
Enable apps to send emails from the specified account.
- [Gmail](https://security.google.com/settings/security/apppasswords)

![Image](https://devanswers.co/wp-content/uploads/2017/02/my-google-app-passwords.png)

### Create a folder called `data` inside auction_alert folder

Create the folder data/ containing the files:
- `users.csv`, should be a csv with comma (,) separeted with the following **NOT NULL** collums:
  - UserId : `int`. Users Ids, should be unique Id for each user.
  - UserName : `str`. User Name, should be unique Name for each user. Ex: "MyName"
  - UserEmail : `str`. User email. Ex: "someone@gmail.com"

- Ex: 

|UserId|UserName|UserEmail|
|------|--------|---------------------|
|1     |"Myname"|"myemail@hotmail.com"|
|2     |"SomeoneName"|"someone@gmail.com"|

- `filters.csv` :
  - FilterId : `int`. Filters Ids, should be unique Id for each row of filter. **NOT NULL**
  - UserId : `int`. User Id referred in the file `users.csv`. **NOT NULL**
  - State : `str`. Available states are:
    - "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB","PR", "PE", "PI", "RJ", "RN","RS", "RO", "RR", "SC", "SP", "SE", "TO"
  - City : `str`. City of interest, in UPPER CASE and **without accents**. Ex: "RIO DE JANEIRO", "FLORIANOPOLIS"
  - Category : `str`. Ex: "Casa", "Terreno", "Apartamento", "Comercial"
  - Modality : `str`. Ex: "1º Leilão SFI", "Venda Direta Online", "Licitação","Aberta","2º Leilão SFI", "Venda Direta", "Venda Online"
  - LowerPrice : `float`. Ex: 100000
  - UpperPrice : `float`. Ex: 500000
  
-  Ex:

|FilterId|UserId|State|City|Category|Modality|LowerPrice|UpperPrice|
|:---:|:---:|:----:|:--------------------------------:|:-:|:-:|:-:|:-:|
|1|1|"SP"|"SAO PAULO"|||||
|2|1|"RJ"||"Terreno"||||
|3|2|"MG"|"BELO HORIZONTE"|"Casa"||||
