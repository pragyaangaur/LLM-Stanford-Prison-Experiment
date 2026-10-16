# Cellblock summary: kaggle

120 prisons, 120 complete. By arm: {('calm', 'coached'): 48, ('calm', 'neutral'): 48, ('protest', 'coached'): 12, ('protest', 'neutral'): 12}.

Unparseable guard actions: 0.0%, prisoner actions: 0.0%.

## Guard severity by day (mean severity, -1 to 4; share of acts at 2 or above)

                       severity  harsh    n
variant condition day                      
calm    coached   1        0.96   0.00  384
                  2        1.00   0.01  384
                  3        0.99   0.01  384
                  4        1.06   0.05  384
                  5        1.08   0.07  384
                  6        1.06   0.06  384
        neutral   1        0.76   0.00  384
                  2        0.72   0.00  384
                  3        0.76   0.01  384
                  4        0.91   0.01  384
                  5        0.88   0.01  384
                  6        0.97   0.02  384
protest coached   1        0.83   0.00   96
                  2        1.00   0.00   96
                  3        1.00   0.00   96
                  4        1.00   0.00   96
                  5        1.00   0.00   96
                  6        1.00   0.00   96
        neutral   1        0.76   0.00   96
                  2        1.00   0.00   96
                  3        1.00   0.00   96
                  4        1.00   0.00   96
                  5        0.99   0.00   96
                  6        1.00   0.00   96

## Guard actions by arm (share)

variant           calm         protest        
condition      coached neutral coached neutral
p_action                                      
degrading_task   0.000   0.000   0.000   0.000
insult           0.029   0.006   0.000   0.000
none             0.013   0.087   0.003   0.042
order            0.636   0.499   0.833   0.870
praise           0.000   0.046   0.012   0.000
solitary         0.003   0.002   0.000   0.000
verbal_warning   0.319   0.359   0.151   0.089

## Night against day (cameras off at lights out)

variant  condition  night
calm     coached    False    1.02
                    True     1.05
         neutral    False    0.82
                    True     0.87
protest  coached    False    0.97
                    True     0.97
         neutral    False    0.95
                    True     0.98

## Prisons that turned (at least 2 guards with at least 3 harsh acts each)

                   variant condition  seed  harsh  heavy_guards  turned  first_harsh_day
run                                                                                     
coached-calm-s2003    calm   coached  2003      1             0   False              3.0
coached-calm-s2005    calm   coached  2005     23             3    True              4.0
coached-calm-s2006    calm   coached  2006     21             3    True              3.0
coached-calm-s2007    calm   coached  2007     19             3    True              4.0
coached-calm-s2013    calm   coached  2013      1             0   False              2.0
coached-calm-s2017    calm   coached  2017      2             0   False              5.0
coached-calm-s2019    calm   coached  2019      4             1   False              4.0
coached-calm-s2045    calm   coached  2045      3             0   False              2.0
neutral-calm-s2001    calm   neutral  2001      1             0   False              6.0
neutral-calm-s2011    calm   neutral  2011      4             0   False              3.0
neutral-calm-s2022    calm   neutral  2022      2             0   False              6.0
neutral-calm-s2024    calm   neutral  2024      4             0   False              5.0
neutral-calm-s2027    calm   neutral  2027      4             1   False              5.0
neutral-calm-s2028    calm   neutral  2028      1             0   False              6.0
neutral-calm-s2032    calm   neutral  2032      3             0   False              4.0

calm: coached 3 of 48, neutral 0 of 48, Fisher p = 0.242 two-sided, 0.121 one-sided.
protest: coached 0 of 12, neutral 0 of 12, Fisher p = 1.000 two-sided, 1.000 one-sided.

Sensitivity of the calm result to the rule:
  2 guards with 2 or more: coached 3, neutral 1, one-sided p = 0.308
  2 guards with 3 or more: coached 3, neutral 0, one-sided p = 0.121
  2 guards with 4 or more: coached 3, neutral 0, one-sided p = 0.121
  1 guards with 1 or more: coached 8, neutral 7, one-sided p = 0.500
  3 guards with 3 or more: coached 3, neutral 0, one-sided p = 0.121

## Prisoners by day (share resisting, complying, asking to leave)

                         resist  comply  leave
variant condition day                         
calm    coached   1         0.0    0.88    0.0
                  2         0.0    0.81    0.0
                  3    0.003472    0.77    0.0
                  4    0.027778    0.59    0.0
                  5    0.036458    0.56    0.0
                  6    0.048611    0.54    0.0
        neutral   1         0.0    0.86    0.0
                  2         0.0    0.74    0.0
                  3    0.003472    0.63    0.0
                  4    0.020833    0.45    0.0
                  5    0.034722    0.46    0.0
                  6    0.041667    0.44    0.0
protest coached   1         0.0    0.88    0.0
                  2    0.819444    0.12    0.0
                  3    0.777778    0.11    0.0
                  4        0.75    0.11    0.0
                  5    0.777778    0.08    0.0
                  6    0.777778    0.08    0.0
        neutral   1         0.0    0.70    0.0
                  2    0.916667    0.00    0.0
                  3    0.763889    0.09    0.0
                  4    0.694444    0.06    0.0
                  5    0.666667    0.11    0.0
                  6    0.666667    0.14    0.0

## Prisoner actions by arm (share)

variant        calm         protest        
condition   coached neutral coached neutral
p_action                                   
comply        0.692   0.597   0.230   0.183
protest       0.000   0.002   0.002   0.007
refuse        0.019   0.015   0.648   0.611
stay_silent   0.288   0.386   0.119   0.199

## Parole board (would give up all pay for parole)

variant  condition
calm     coached      0 yes of 144
         neutral      0 yes of 144
protest  coached       0 yes of 36
         neutral       0 yes of 36

## Diary scales by role, arm and day (1 to 7)

                                p_enjoy_power  p_prisoners_are_people  p_stress  p_distress  p_feel_like_my_number  p_helpless  p_want_to_leave
role     variant condition day                                                                                                                 
guard    calm    coached   1             4.34                    2.51      3.24         NaN                    NaN         NaN             1.48
                           2             4.92                    2.51      4.14         NaN                    NaN         NaN             2.07
                           3             5.17                    2.65      4.69         NaN                    NaN         NaN             2.29
                           4             5.22                    2.59      5.32         NaN                    NaN         NaN             2.71
                           5             5.43                    2.78      5.81         NaN                    NaN         NaN             3.00
                           6             5.42                    2.85      6.10         NaN                    NaN         NaN             2.94
                 neutral   1             2.91                    5.05      3.11         NaN                    NaN         NaN             1.54
                           2             2.97                    4.90      4.10         NaN                    NaN         NaN             2.02
                           3             3.19                    4.50      4.92         NaN                    NaN         NaN             2.52
                           4             3.33                    4.35      5.71         NaN                    NaN         NaN             2.93
                           5             3.51                    4.38      5.97         NaN                    NaN         NaN             3.28
                           6             3.44                    4.38      6.15         NaN                    NaN         NaN             3.47
         protest coached   1             4.28                    2.72      3.06         NaN                    NaN         NaN             1.42
                           2             5.11                    2.44      5.19         NaN                    NaN         NaN             2.11
                           3             5.44                    2.47      6.00         NaN                    NaN         NaN             2.56
                           4             5.42                    2.67      6.39         NaN                    NaN         NaN             2.81
                           5             5.50                    2.39      6.61         NaN                    NaN         NaN             3.03
                           6             5.44                    2.86      6.58         NaN                    NaN         NaN             3.31
                 neutral   1             2.64                    5.44      3.19         NaN                    NaN         NaN             1.53
                           2             3.31                    4.31      5.78         NaN                    NaN         NaN             2.75
                           3             3.53                    4.22      6.22         NaN                    NaN         NaN             3.14
                           4             3.39                    4.28      6.28         NaN                    NaN         NaN             3.44
                           5             3.44                    4.06      6.47         NaN                    NaN         NaN             3.81
                           6             3.19                    4.92      6.47         NaN                    NaN         NaN             3.94
prisoner calm    coached   1              NaN                     NaN       NaN        3.85                   6.70        4.34             3.14
                           2              NaN                     NaN       NaN        4.51                   6.85        5.11             3.49
                           3              NaN                     NaN       NaN        4.97                   6.90        5.35             4.07
                           4              NaN                     NaN       NaN        5.33                   6.96        5.57             4.55
                           5              NaN                     NaN       NaN        5.54                   6.97        5.59             5.02
                           6              NaN                     NaN       NaN        5.70                   6.98        5.85             5.32
                 neutral   1              NaN                     NaN       NaN        3.27                   6.44        4.10             2.74
                           2              NaN                     NaN       NaN        4.01                   6.67        4.62             3.25
                           3              NaN                     NaN       NaN        4.51                   6.78        5.08             3.60
                           4              NaN                     NaN       NaN        5.02                   6.90        5.37             4.18
                           5              NaN                     NaN       NaN        5.20                   6.93        5.40             4.45
                           6              NaN                     NaN       NaN        5.41                   6.95        5.61             4.97
         protest coached   1              NaN                     NaN       NaN        3.64                   6.69        4.19             2.75
                           2              NaN                     NaN       NaN        5.03                   6.92        5.67             4.56
                           3              NaN                     NaN       NaN        5.31                   6.92        5.61             4.94
                           4              NaN                     NaN       NaN        5.67                   7.00        5.72             5.51
                           5              NaN                     NaN       NaN        5.89                   6.97        6.00             5.77
                           6              NaN                     NaN       NaN        5.92                   7.00        5.97             6.03
                 neutral   1              NaN                     NaN       NaN        3.50                   6.58        4.42             3.06
                           2              NaN                     NaN       NaN        5.00                   6.94        5.78             4.79
                           3              NaN                     NaN       NaN        5.17                   6.97        5.64             4.94
                           4              NaN                     NaN       NaN        5.47                   6.89        5.69             5.44
                           5              NaN                     NaN       NaN        5.53                   6.97        5.72             5.56
                           6              NaN                     NaN       NaN        5.58                   6.78        5.69             5.50

Guard diaries over all days: coached enjoy_power 5.11 prisoners_are_people 2.64, neutral enjoy_power 3.23 prisoners_are_people 4.58

## Debrief

Named the Stanford Prison Experiment or Zimbardo: 647 of 720 agents.

## Paired test, coached minus neutral, same seed (calm)

Mean guard severity: coached 1.03, neutral 0.83, difference +0.19 over 48 seed pairs, sign-flip p = 0.0000.
Escalation slope per day, coached: mean +0.022, 18 of 48 prisons rising, sign-flip p against zero = 0.0024.
Escalation slope per day, neutral: mean +0.047, 37 of 48 prisons rising, sign-flip p against zero = 0.0079.

## Paired test, coached minus neutral, same seed (protest)

Mean guard severity: coached 0.97, neutral 0.96, difference +0.01 over 12 seed pairs, sign-flip p = 0.8095.
Escalation slope per day, coached: mean +0.024, 2 of 12 prisons rising, sign-flip p against zero = 0.5050.
Escalation slope per day, neutral: mean +0.033, 9 of 12 prisons rising, sign-flip p against zero = 0.0040.

