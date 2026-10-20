# Masked against prison frame, calm, seeds 2012-2047

Exploratory. Prisons per frame and condition: {('masked', 'coached'): 36, ('masked', 'neutral'): 36, ('prison', 'coached'): 36, ('prison', 'neutral'): 36}.

## Per prison

                  severity  harsh  turned  prisons
frame  condition                                  
masked coached       0.980  0.028       0       36
       neutral       0.822  0.028       0       36
prison coached       1.000  0.278       0       36
       neutral       0.832  0.389       0       36

## Coached minus neutral within each frame (paired by seed)

masked: mean difference 0.157, coached higher in 27 of 36, sign-flip p = 0.0001

masked: turned coached 0 of 36, neutral 0 of 36, one-sided Fisher p = 1.000

prison: mean difference 0.168, coached higher in 27 of 36, sign-flip p = 0.0000

prison: turned coached 0 of 36, neutral 0 of 36, one-sided Fisher p = 1.000

## Masked minus prison, same seed and condition

coached: mean severity difference -0.020, masked higher in 9 of 36, sign-flip p = 0.0462

neutral: mean severity difference -0.010, masked higher in 17 of 36, sign-flip p = 0.8851

## Distributions

coached, per-prison severity: KS D = 0.139 (p = 0.8849), Mann-Whitney p = 0.9846

coached, per-prison harsh: KS D = 0.083 (p = 0.9998), Mann-Whitney p = 0.1598

neutral, per-prison severity: KS D = 0.083 (p = 0.9998), Mann-Whitney p = 0.8964

neutral, per-prison harsh: KS D = 0.111 (p = 0.9822), Mann-Whitney p = 0.0842

Guard action mix, share of turns:

frame           masked          prison        
condition      coached neutral coached neutral
p_action                                      
degrading_task   0.001   0.000   0.000   0.001
insult           0.000   0.001   0.002   0.005
none             0.012   0.041   0.013   0.086
order            0.891   0.670   0.604   0.487
praise           0.005   0.069   0.000   0.047
solitary         0.000   0.000   0.003   0.002
verbal_warning   0.092   0.220   0.378   0.371

coached: action mix differs by frame, chi-square 414.8, df 6, p = 1.8e-86

neutral: action mix differs by frame, chi-square 163.4, df 6, p = 1.152e-32

Guard severity, share of turns at each level:

frame       masked          prison        
condition  coached neutral coached neutral
p_severity                                
-1.0         0.005   0.069   0.000   0.047
 0.0         0.012   0.041   0.013   0.086
 1.0         0.983   0.890   0.981   0.858
 2.0         0.000   0.001   0.002   0.005
 3.0         0.001   0.000   0.000   0.001
 4.0         0.000   0.000   0.003   0.002

## Prisoners and residents

frame   condition
masked  coached      0.005
        neutral      0.015
prison  coached      0.021
        neutral      0.017

## Debrief

                  sum  size
frame  condition           
masked coached     59   216
       neutral     26   216
prison coached    202   216
       neutral    190   216

A masked agent that names the Stanford Prison Experiment recognised the structure without the words.

