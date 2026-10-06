# Cellblock summary: overnight

8 prisons, 0 complete. By arm: {('calm', 'coached'): 4, ('calm', 'neutral'): 4}.

Unparseable guard actions: 0.0%, prisoner actions: 0.0%.

## Guard severity by day (mean severity, -1 to 4; share of acts at 2 or above)

                       severity  harsh   n
variant condition day                     
calm    coached   1        1.00    0.0  32
                  2        1.00    0.0  32
                  3        1.00    0.0  32
                  4        1.00    0.0  32
                  5        1.00    0.0  32
        neutral   1        0.34    0.0  32
                  2        0.41    0.0  32
                  3        0.69    0.0  32
                  4        1.00    0.0  32
                  5        0.56    0.0  32

## Guard actions by arm (share)

variant           calm        
condition      coached neutral
p_action                      
none             0.000   0.100
order            0.462   0.344
praise           0.000   0.150
verbal_warning   0.538   0.406

## Night against day (cameras off at lights out)

variant  condition  night
calm     coached    False    1.00
                    True     1.00
         neutral    False    0.59
                    True     0.62

## Prisons that turned (at least 2 guards with at least 3 harsh acts each)

Empty DataFrame
Columns: [variant, condition, seed, harsh, heavy_guards, turned, first_harsh_day]
Index: []

calm: coached 0 of 4, neutral 0 of 4, Fisher p = 1.000 two-sided, 1.000 one-sided.

Sensitivity of the calm result to the rule:
  2 guards with 2 or more: coached 0, neutral 0, one-sided p = 1.000
  2 guards with 3 or more: coached 0, neutral 0, one-sided p = 1.000
  2 guards with 4 or more: coached 0, neutral 0, one-sided p = 1.000
  1 guards with 1 or more: coached 0, neutral 0, one-sided p = 1.000
  3 guards with 3 or more: coached 0, neutral 0, one-sided p = 1.000

## Prisoners by day (share resisting, complying, asking to leave)

                      resist  comply  leave
variant condition day                      
calm    coached   1      0.0    0.98    0.0
                  2      0.0    1.00    0.0
                  3      0.0    0.98    0.0
                  4      0.0    0.98    0.0
                  5      0.0    0.88    0.0
        neutral   1      0.0    0.71    0.0
                  2      0.0    0.67    0.0
                  3      0.0    0.67    0.0
                  4      0.0    0.67    0.0
                  5      0.0    0.67    0.0

## Prisoner actions by arm (share)

variant        calm        
condition   coached neutral
p_action                   
comply        0.962   0.675
stay_silent   0.038   0.325

## Parole board (would give up all pay for parole)

variant  condition
calm     coached      0 yes of 12
         neutral      0 yes of 12

## Diary scales by role, arm and day (1 to 7)

                                p_enjoy_power  p_prisoners_are_people  p_stress  p_distress  p_feel_like_my_number  p_helpless  p_want_to_leave
role     variant condition day                                                                                                                 
guard    calm    coached   1             4.92                    2.92      3.42         NaN                    NaN         NaN             1.92
                           2             5.08                    2.67      3.75         NaN                    NaN         NaN             2.50
                           3             5.18                    3.27      5.27         NaN                    NaN         NaN             2.64
                           4             5.17                    4.00      5.25         NaN                    NaN         NaN             2.67
                 neutral   1             3.50                    4.50      2.75         NaN                    NaN         NaN             1.42
                           2             3.33                    4.50      3.42         NaN                    NaN         NaN             1.67
                           3             4.50                    4.08      4.25         NaN                    NaN         NaN             2.50
                           4             4.08                    4.25      5.75         NaN                    NaN         NaN             2.83
prisoner calm    coached   1              NaN                     NaN       NaN        3.40                   5.70        3.50             2.90
                           2              NaN                     NaN       NaN        3.70                   6.00        3.90             3.50
                           3              NaN                     NaN       NaN        4.75                   6.67        4.83             4.00
                           4              NaN                     NaN       NaN        4.92                   6.58        5.00             3.67
                 neutral   1              NaN                     NaN       NaN        3.36                   6.18        3.64             2.45
                           2              NaN                     NaN       NaN        3.55                   6.36        3.91             2.55
                           3              NaN                     NaN       NaN        4.18                   6.45        4.09             3.09
                           4              NaN                     NaN       NaN        4.20                   6.50        4.40             3.60

Guard diaries over all days: coached enjoy_power 5.09 prisoners_are_people 3.21, neutral enjoy_power 3.85 prisoners_are_people 4.33

## Paired test, coached minus neutral, same seed (calm)

Mean guard severity: coached 1.00, neutral 0.60, difference +0.40 over 4 seed pairs, sign-flip p = 0.2482.
Escalation slope per day, coached: mean +0.000, 0 of 4 prisons rising, sign-flip p against zero = 1.0000.
Escalation slope per day, neutral: mean +0.103, 2 of 4 prisons rising, sign-flip p against zero = 0.7448.

