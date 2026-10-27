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

I chose random forest regression because it had the lowest validation MAE and beat the baseline, with a validation MAE of 223.86 fans. Its test MAE was 351.20 fans, meaning its predictions were off by about 351 fans per test game, so on average 127.34 fans more than on the validation games. This suggests the model did not generalize as well to the 2025 season. Differences in opponents, scheduling, or attendance patterns may have contributed. Looking at the dataset, one difference that may have contributed to the higher test MAE is that the team tended to have a higher prior win percentage in the test season than in earlier seasons. The small training dataset may also have limited the model’s ability to learn patterns that hold across seasons.

### Top Features
| Feature | Importance | Business meaning |
| :--- | ---: | :--- |
| Prior win percentage | 52.99% | The team’s performance before each game may reflect fan interest and demand for tickets. |
| Days since last home game | 26.83% | The time between home games may affect demand, including differences between short breaks and the offseason. |
| Week | 16.22% | The point in the football season may capture changes in attendance related to scheduling or playoff interest. |
| Season | 3.97% | The year may capture differences in attendance patterns across seasons. |


### limits
The model uses a small dataset, and attendance varies relatively little across home games. This limits the patterns it can learn and helps explain why predicting the training average was difficult to beat. Its higher test MAE also shows that validation performance does not guarantee the same accuracy in a later season.

The model does not account for ticket prices, or opponent popularity. Adding more seasons and these factors could help explain attendance differences. 
