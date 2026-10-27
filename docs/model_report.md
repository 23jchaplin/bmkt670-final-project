# Model Report

### Figures

![histogram of attendance](figures/attendance_distribution.png)
Attendance was fairly consistent across training games, with most games drawing around 78,000–78,400 and there being 10 games with attendance around 78,250.

![sctterplot of attendance vs days since last game](figures/attendance_vs_home_game_gap.png)
There doesn't appear to be a clear relationship between attendance and days since the last home game, with attendance after long offseason breaks falling within the range seen after shorter gaps.

![scatter plot of attendance vs win percentage](figures/attendance_vs_win_pct.png)
There appears to be a slight postive relationship between games with higher prior win percentages and higher attendance.

### Error Measure
I used mean absolute error (MAE), which measures how many fans my attendance predictions were off by on average, regardless of whether they were too high or too low. For example, an MAE of 480 means the predictions differed from actual attendance by an average of 480 fans. A lower MAE indicates more accurate predictions.

### Comparison Table
![comparison table: baseline and each model, scored on validate rows](comparison_table.png)

### Model Chosen

I chose KNN regression because it was the only model that beat the baseline, with a validation MAE of 227.89 fans. 

### Top Features
| Feature | Importance | Business meaning |
| :--- | ---: | :--- |


### limits
The model uses a small dataset, and attendance varies relatively little across home games. This limits the patterns it can learn and helps explain why predicting the training average was difficult to beat. Its higher test MAE also shows that validation performance does not guarantee the same accuracy in a later season.

The model does not account for ticket prices, opponent popularity. Adding more seasons and these factors could help explain attendance differences. Because the London game was excluded, the model’s results should not be assumed to apply to games at other venues.

Season is also a limited predictor for a random forest because it cannot reliably project a continuing year-to-year trend into future seasons.