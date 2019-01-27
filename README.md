# fund_stats
Python program retrieving fund-statistics, store to local database and generate graphical report


----------------------
Installing
----------------------
```
# sudo apt-get py-reportlab
# sudo apt-get py-httplib2
# git clone https://github.com/engdan77/fund_stats.git

```

----------------------
Update parameters in fund_stats.py
----------------------
```
varMainLimit = "-20"
# Format (["Name of Fund", "Current Andelar", "Anskaffningsvarde for Andelar", "Url at pensionsmyndigheten"])
fundList = (['AlfredBerg Fastighetsfond', '146.05', '15678', 'https://secure.pensionsmyndigheten.se/FondfaktasidaPopup.html?id=320176'],
            ['EastCapital Ryssland', '0.56', '612', 'https://secure.pensionsmyndigheten.se/FondfaktasidaPopup.html?id=834788'],
            ['HandelsBanken Sverige OMXSB', '252.63', '27167', 'https://secure.pensionsmyndigheten.se/FondfaktasidaPopup.html?id=465914'])

# Mail address to send to
mail_address = "xxxxxx@xxxxxxx"

# Mail configuaration
mailServer = "xxx"
fromAddress = "xxx"
```

-------------------------
Usage
-------------------------
```
$ python fund_stats.py 
Creating DB
Adding data - 2015-02-17, AlfredBerg Fastighetsfond, 235,99, 34466.34, 54.51
Adding data - 2015-02-17, EastCapital Ryssland, 808,68, 452.86, -26.00
Adding data - 2015-02-17, HandelsBanken Sverige OMXSB, 197,03, 49775.69, 45.42
Adding data - 2015-02-17, 84694.89, 73.93
```

-------------------------
Pictures
-------------------------
![Pic0](https://github.com/engdan77/fund_stats/blob/master/pics/pic0.png)
![Pic3](https://github.com/engdan77/fund_stats/blob/master/pics/pic3.png)
![Pic4](https://github.com/engdan77/fund_stats/blob/master/pics/pic4.png)
