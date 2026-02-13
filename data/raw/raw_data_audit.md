# Raw Data Audit Report
**Generated:** 2026-02-13
**Purpose:** Comprehensive examination of all raw Excel files across 2022, 2023, and 2024.

---

## Executive Summary

### 2022 Data Overview

| File | Rows | Columns |
|------|------|--------|
| 1. Applicants.xlsx | 437 | 63 |
| 10. Secondary Application.xlsx | 437 | 51 |
| 11. Military.xlsx | 0 | 0 |
| 12. GPA Trend.xlsx | 437 | 3 |
| 2. Language.xlsx | 1,004 | 5 |
| 3. Parents.xlsx | 863 | 7 |
| 4. Siblings.xlsx | 776 | 4 |
| 5. Academic Records.xlsx | 25,084 | 13 |
| 6. Experiences.xlsx | 5,904 | 13 |
| 8. Schools.xlsx | 1,069 | 14 |
| 9. Personal Statement.xlsx | 437 | 3 |

### 2023 Data Overview

| File | Rows | Columns |
|------|------|--------|
| 1. Applicants.xlsx | 401 | 60 |
| 10. Secondary Application.xlsx | 401 | 51 |
| 11. Military.xlsx | 8 | 7 |
| 12. GPA Trend.xlsx | 401 | 3 |
| 2. Language.xlsx | 916 | 5 |
| 3. Parents.xlsx | 795 | 7 |
| 4. Siblings.xlsx | 757 | 5 |
| 5. Academic Records.xlsx | 22,490 | 13 |
| 6. Experiences.xlsx | 5,454 | 13 |
| 8. Schools.xlsx | 921 | 14 |
| 9. Personal Statement.xlsx | 401 | 3 |

### 2024 Data Overview

| File | Rows | Columns |
|------|------|--------|
| 1. Applicants.xlsx | 613 | 60 |
| 10. Secondary Application.xlsx | 613 | 51 |
| 11. Military.xlsx | 5 | 7 |
| 12. GPA Trend.xlsx | 613 | 3 |
| 2. Language.xlsx | 1,472 | 5 |
| 3. Parents.xlsx | 1,198 | 7 |
| 4. Siblings.xlsx | 1,077 | 4 |
| 5. Academic Records.xlsx | 35,803 | 13 |
| 6. Experiences.xlsx | 8,501 | 13 |
| 8. School.xlsx | 1,455 | 14 |
| 9. Personal Statement.xlsx | 613 | 3 |

---

## Detailed File Analysis

================================================================================
## FILE: 1. Applicants.xlsx
================================================================================

### Year-over-Year Overview

| Year | Rows | Columns | Status |
|------|------|---------|--------|
| 2022 | 437 | 63 | ✓ OK |
| 2023 | 401 | 60 | ✓ OK |
| 2024 | 613 | 60 | ✓ OK |

### 2022 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| Appl_Year | int64 | 1 | 0.0% |
| Amcas_ID | int64 | 437 | 0.0% |
| Prev_Applied_Rush | object | 10 | 83.3% |
| Age | int64 | 18 | 0.0% |
| Gender | object | 2 | 0.0% |
| Citizenship | object | 15 | 0.0% |
| SES_Value | object | 2 | 0.0% |
| Eo_Level | object | 2 | 72.3% |
| First_Generation_Ind | object | 2 | 0.0% |
| Disadvantanged_Ind | object | 2 | 0.0% |
| Hrdshp_Comments | object | 115 | 73.7% |
| RU_Ind | object | 2 | 0.0% |
| Num_Dependents | int64 | 3 | 0.0% |
| Inst_Action_Ind | object | 2 | 0.0% |
| Inst_Action_Desc | object | 29 | 93.4% |
| Prev_Matric_Ind | object | 1 | 0.0% |
| Prev_Matric_Sschool | float64 | 0 | 100.0% |
| Prev_Matric_Year | float64 | 1 | 99.8% |
| Prev_Matric_Desc | float64 | 0 | 100.0% |
| Investigation_Ind | object | 1 | 0.0% |
| Felony_Ind | object | 1 | 0.0% |
| Felony_Desc | float64 | 0 | 100.0% |
| Misdemeanor_Ind | object | 2 | 0.0% |
| Misdemeanor_Desc | object | 7 | 98.4% |
| Military_Discharge_Ind | object | 1 | 0.0% |
| Military_HON_Discharge_Ind | int64 | 1 | 0.0% |
| Military_Discharge_Desc | float64 | 0 | 100.0% |
| Exp_Hour_Total | int64 | 432 | 0.0% |
| Exp_Hour_Research | float64 | 248 | 9.2% |
| Exp_Hour_Volunteer_Med | float64 | 260 | 9.4% |
| Exp_Hour_Volunteer_Non_Med | float64 | 237 | 15.1% |
| Exp_Hour_Employ_Med | float64 | 221 | 27.2% |
| Exp_Hour_Shadowing | float64 | 163 | 13.3% |
| Comm_Service_Ind | object | 2 | 0.0% |
| Comm_Service_Total_Hours | int64 | 347 | 0.0% |
| HealthCare_Ind | object | 1 | 0.0% |
| HealthCare_Total_Hours | int64 | 393 | 0.0% |
| Highest_Test_Date_2015 | object | 85 | 0.0% |
| Under_School | object | 181 | 0.2% |
| Major_Long_Desc | object | 175 | 0.2% |
| Military_Service | object | 1 | 0.0% |
| Military_Service_Status | float64 | 0 | 100.0% |
| Pell_Grant | object | 4 | 0.0% |
| Fee_Assistance_Program | object | 3 | 0.0% |
| Childhood_Med_Underserved_Self_Reported | object | 4 | 0.0% |
| Family_Income_Level | object | 19 | 0.0% |
| Number_in_Household | int64 | 11 | 0.0% |
| Family_Assistance_Program | object | 2 | 0.0% |
| Paid_Employment_BF_18 | object | 2 | 0.0% |
| Contribution_to_Family | object | 2 | 0.0% |
| Academic_Scholarship_Percentage | float64 | 56 | 9.8% |
| Finacial_Need_Based_Percentage | float64 | 60 | 9.8% |
| Student_Loan_Percentage | float64 | 51 | 9.8% |
| Other_Loan_Percentage | float64 | 22 | 9.8% |
| Family_Contribution_Percentage | float64 | 65 | 9.8% |
| Applicant_Contribution_Percentage | float64 | 29 | 9.8% |
| Other_Percentage | float64 | 14 | 9.8% |
| Application Review Score | int64 | 13 | 0.0% |
| Service Rating (Categorical) | object | 4 | 0.0% |
| Service Rating (Numerical) | int64 | 4 | 0.0% |
| AMCAS ID | int64 | 437 | 0.0% |
| Total_GPA_Trend | float64 | 2 | 45.1% |
| BCPM_GPA_Trend | float64 | 2 | 47.8% |

#### Sample Data (First 3 Rows)

```
Row 1:
  Appl_Year: 2022
  Amcas_ID: 12950085
  Prev_Applied_Rush: 2014; 2021
  Age: 36
  Gender: Male
  Citizenship: USA
  SES_Value: Yes
  Eo_Level: EO1
  First_Generation_Ind: No
  Disadvantanged_Ind: No
Row 2:
  Appl_Year: 2022
  Amcas_ID: 13099483
  Prev_Applied_Rush: nan
  Age: 40
  Gender: Male
  Citizenship: TZA
  SES_Value: No
  Eo_Level: nan
  First_Generation_Ind: Yes
  Disadvantanged_Ind: Yes
Row 3:
  Appl_Year: 2022
  Amcas_ID: 13489485
  Prev_Applied_Rush: nan
  Age: 32
  Gender: Male
  Citizenship: USA
  SES_Value: No
  Eo_Level: nan
  First_Generation_Ind: No
  Disadvantanged_Ind: No
```

#### Categorical Column Distributions

**Appl_Year** (Top 10 values):
- `2022`: 437 (100.0%)

**Prev_Applied_Rush** (Top 10 values):
- `2021`: 47 (10.8%)
- `2020`: 15 (3.4%)
- `2020; 2021`: 3 (0.7%)
- `2019; 2020; 2021`: 2 (0.5%)
- `2014; 2021`: 1 (0.2%)
- `2019`: 1 (0.2%)
- `2018; 2021`: 1 (0.2%)
- `2016; 2018`: 1 (0.2%)
- `2018; 2019; 2021`: 1 (0.2%)
- `2018; 2020`: 1 (0.2%)

**Age** (Top 10 values):
- `25`: 109 (24.9%)
- `26`: 91 (20.8%)
- `27`: 69 (15.8%)
- `24`: 66 (15.1%)
- `28`: 33 (7.6%)
- `29`: 19 (4.3%)
- `30`: 16 (3.7%)
- `23`: 13 (3.0%)
- `31`: 5 (1.1%)
- `32`: 4 (0.9%)

**Gender** (Top 10 values):
- `Female`: 251 (57.4%)
- `Male`: 186 (42.6%)

**Citizenship** (Top 10 values):
- `USA`: 419 (95.9%)
- `UGA`: 2 (0.5%)
- `IRN`: 2 (0.5%)
- `IND`: 2 (0.5%)
- `MEX`: 2 (0.5%)
- `TZA`: 1 (0.2%)
- `CHN`: 1 (0.2%)
- `CMR`: 1 (0.2%)
- `KEN`: 1 (0.2%)
- `KOR`: 1 (0.2%)

**SES_Value** (Top 10 values):
- `No`: 316 (72.3%)
- `Yes`: 121 (27.7%)

**Eo_Level** (Top 10 values):
- `EO1`: 83 (19.0%)
- `EO2`: 38 (8.7%)

**First_Generation_Ind** (Top 10 values):
- `No`: 365 (83.5%)
- `Yes`: 72 (16.5%)

**Disadvantanged_Ind** (Top 10 values):
- `No`: 322 (73.7%)
- `Yes`: 115 (26.3%)

**RU_Ind** (Top 10 values):
- `U`: 430 (98.4%)
- `R`: 7 (1.6%)

**Num_Dependents** (Top 10 values):
- `0`: 427 (97.7%)
- `1`: 7 (1.6%)
- `2`: 3 (0.7%)

**Inst_Action_Ind** (Top 10 values):
- `No`: 408 (93.4%)
- `Yes`: 29 (6.6%)

**Inst_Action_Desc** (Top 10 values):
- `I was placed on academic probation I after my first semester at Tufts (12/2010), and academic probation II after my second semester (05/2011). The sudden freedom of college, after a strict upbringing by recently immigrated parents, side-tracked my progress and nearly squandered my academic potential. Uninformed and inexperienced when it came to navigating educational and social opportunities, I needed several failures to awaken to the reality that I had to change.

Every day after that dismal freshman performance, I tasked myself with getting closer to the medical career through which I can contribute to my community -- and my commitment to study fell right into place. I made steps to prioritize and organize, moving between the library and the gym, and making stops at office hours and the Academic Resource Center. Major adjustments yielded academic improvements that restored my confidence. I am grateful for the lessons in commitment and resilience that reestablished my academic performance.`: 1 (0.2%)
- `During the beginning of my freshman year, I was distracted by my newfound independence. On two occasions, Fall and Spring semester, I took responsibility for inappropriate items found in my dorm by campus safety. Both times (October 2016 and May 2017), this consisted of a bottle of alcohol and a marijuana grinder. I completed the necessary sanctions after meetings with college administrators and the following summer, I obtained my EMT certification and volunteered in an emergency room. This gave me an opportunity to surround myself with like-minded peers. In addition, I became a tutor the following semester and further realized the type of person I wanted to be. Not who I was freshman year. Since then, I have been an active member of my college community and worked to right my wrongs by setting positive examples for younger students.
During the fall semester of my senior year, a small dent in my apartment wall was discovered. Since this was an accident and I promptly repaired the wall, my appeal was accepted by the Office of Residential Life. Additionally, my Dean of Students has offered to write me a letter of support for all instances mentioned.`: 1 (0.2%)
- `I was placed under academic probation after failing to meet a 2.0 requirement by the university. This occurred during the Fall 2016 semester. Honestly, I had prioritized the wrong things and had forgotten where I was coming from, but I won't make that mistake again.`: 1 (0.2%)
- `On September 1, 2018, I made the regrettable decision to drink alcohol underage. I chose to drink with a classmate, who became so intoxicated that campus officers discussed transporting her. I offered to take her home myself, knowing that my involvement could result in disciplinary action. I was able to ensure she got home safely but was subsequently placed on Disciplinary Probation for 6 months for underage alcohol use. 
Being on probation meant my study abroad offer was rescinded. I explained my lapse in judgement to the program head, who opted to re-accept me. I went on to work closely with this professor and form a professional relationship built on mutual trust and respect. Her faith in my ability to grow inspired me to use this incident as a wakeup call. I was struggling with my transition into college and took advantage of my independence by disrespecting the law, my institution, and myself. I learned that each choice I make defines who I am, and have since strictly upheld the Georgia Tech Code of Conduct and continued my coursework without further altercation. While I think it is important to explain the event’s context, I take full responsibility for my actions and the consequences that followed. I am grateful I could reshape my priorities and become a person whose actions are worthy of respect.`: 1 (0.2%)
- `In the spring of my Freshman year, 2017, I was placed on Academic Warning due to an F in Calculus 2 and a D in Physics. I have Crohn's disease, and the severity of the illness worsened my freshman year. I did not know how to manage it yet, and my grades suffered as a result. However, I changed my medications and started being more consistent with my diet after my freshman year ended. Auburn university removed me from Academic warning in the fall of my sophomore year due to improved grades.`: 1 (0.2%)
- `This was not an institutional action. I wanted to use this box to explain dropping my class during Summer 2020. I decided to drop my class on Day 1 to purchase materials for the MCAT instead with the money I used as my tuition for the summer (refunded). The course did not show up on my transcript, but instead says "Summer Session 1 Withdrawn from University", even though I technically dropped the class before it started.`: 1 (0.2%)
- `Each incident has been expunged from my record:

09/17/16: I was reprimanded for alcohol possession in a dorm room and met with my RA to discuss the incident. I understand policies regarding alcohol possession are in place to protect the health of students as well as myself. I recognize this act was irresponsible of me. I should have known better than to put my health at risk for something so careless.

10/29/17: I utilized a prior semester’s edition of our textbook to complete an open-book homework assignment for General Biology Lab, unaware that using prior editions was prohibited in the current semester. I was flagged for including information on my assignment from this prior textbook and charged with a violation of the Academic Integrity Policy. I had misplaced my copy and mistakenly assumed that a prior semester’s textbook could be utilized instead. My professor acknowledged that this incident was due to my misunderstanding of class policy. I received no credit for the assignment, but I successfully completed the course with a B+. I learned to be more cognizant of class policies. 

Since these early incidents, I have worked hard to maintain a strong academic and extracurricular record. I have no interest in jeopardizing my future with further acts of negligence and ignorance.`: 1 (0.2%)
- `On 4/29/19, I received a violation for academic dishonesty. A classmate was copying me during an exam, and I failed to report him. Other classmates reported this student, and my professor then sent out an email asking for others with more information on the incident to come forward. I emailed the professor, stating I had a feeling he had been copying me but didn’t think much of it. I received a zero 0 on the exam and lost bonus points for the course. I was also required to take an online training course on academic dishonesty and its effects on society. 

I should’ve approached the student in private after the test and asked if he had cheated off of me. If he did, then I should have given him a chance to turn himself to the professor. If he denied it, then I should have reported the incident to the professor right away. But the fact that I did not act on the situation right away makes me guilty and an accomplice. I was enabling this behavior to continue. That is dangerous because dishonest students become dishonest professionals; I could’ve potentially caused harm to other people by not reporting this individual. 

This experience has helped me grow and analyze situations more critically. If I see something ethically wrong, I need to address it immediately because it can have detrimental consequences.`: 1 (0.2%)
- `Plagiarism, HIST 1301, 05/2017.  For an extra credit book report, I paraphrased online information without citing. I was deducted half a letter grade from my final grade. I recognize the severity of my mistake and grateful for this opportunity to learn from it. I learned to always follow assignment instructions while citing accordingly, and have not repeated that mistake since.`: 1 (0.2%)
- `In 2014 I began my undergraduate degree at the University of Vermont. During the fall semester of freshman year, I engaged in behavior uncharacteristic of me as a person. I was involved in a fistfight with another student while intoxicated in the dorms. Subsequently, I was suspended from the university for the following semester. After reflection on my behavior and considering my option to finish the semester while disciplinary action was under review, I opted to withdraw for the semester in order to return home to begin making amends. The next year, I decided to attend the University of New Hampshire to give myself a clean slate. Throughout my time at UNH I had no further transgressions of any type and worked to redeem myself through extensive community service and in positions of responsibility, including as a chemistry tutor and a volunteer EMT. I believe that my resume and letters of recommendation will reflect that I have matured and my actions as an 18-year-old do not accurately reflect the person I am today. While my actions at UVM were wrong, I have worked hard to redeem myself. I take full responsibility for my actions and hope that the admissions committees will agree that I have matured greatly and that my actions following this incident are a true representation of my personal integrity.`: 1 (0.2%)

**Prev_Matric_Ind** (Top 10 values):
- `No`: 437 (100.0%)

**Prev_Matric_Year** (Top 10 values):
- `0.0`: 1 (0.2%)

**Investigation_Ind** (Top 10 values):
- `No`: 437 (100.0%)

**Felony_Ind** (Top 10 values):
- `No`: 437 (100.0%)

**Misdemeanor_Ind** (Top 10 values):
- `No`: 430 (98.4%)
- `Yes`: 7 (1.6%)

**Misdemeanor_Desc** (Top 10 values):
- `On the evening of February of 2015 (2/13/15), I received an Open Container in Public Violation and was fined a fee. I was at Signal Hill Park in Long Beach, CA with friends and was told to go home by the police officer. On the court date, I pleaded no contest and the misdemeanor was reduced into an infraction. A public defender represented me at the Long Beach courthouse. Also, the judge gave me the option to do community hours in lieu of paying the fine.  I volunteered at a local thrift store to fulfill my community hours. I have learned since this incident to be more responsible for my actions. I deeply regret this irresponsible behavior and have learned a valuable lesson. From this incident, I have learned to truly consider all my actions and be a responsible and mature adult.`: 1 (0.2%)
- `I bought a taser off of Amazon April 19th 2015 for $20. At the time I was 17. The purpose behind the purchase was to protect myself from the rising effects of gang activity in my neighborhood that put me in harm's way multiple times. Shortly after I bought it, I thought I had lost it. Years later on my way home I was searched by the NYC Police Transit Bureau. Upon searching my bag they found the taser I had believed to be lost for years. They attempted to use it and we realized it was broken. The taser was nonfunctional but they charged me with felony charges of possession of a weapon and I pleaded guilty to one count of Criminal Possession Weapon-4th: Firearm/Weapon and one count Criminal Possession Weapon-4th: Intent to use. The counts are misdemeanors and the sentence included 2 weeks of community service and a fine of about $100 dollars. While I realize that I should have checked whether tasers were legal in New York City before ordering one from Amazon, and take full responsibility for my mistake, it should be mentioned that it was reported by the New York Post that a federal judge ruled in March 2019 that banning tasers in New York was unconstitutional as these devices are alternatives to lethal weapons. Since then they have been legalized. It should also be mentioned that I never used the taser.`: 1 (0.2%)
- `On the night of July 9, 2014, I was charged with the “consumption of alcohol by a minor” in Barrington, Illinois. During an administrative adjudication hearing, I pleaded guilty to this charge. I received a local ordinance violation order (Case Number: AA1-005708) to pay $250.00 and complete 24 hours of community service.

I paid the $250.00 immediately and completed the community service shortly thereafter. Thus, this offense was expunged from my permanent record.

I learned that my actions have consequences that can not only damage my own well-being, but can also harm my greater community. I took responsibility for my lapse in judgment, and actively pursued volunteer opportunities that would allow me to become a contributing member of society to avoid making this type of mistake again in the future. At the University of Illinois at Urbana-Champaign, I volunteered with the Alpha Phi Omega Service Fraternity and Global Medical Brigades to give back to my community and reduce healthcare disparities abroad, which taught me that service can be a powerful way to improve society at-large.`: 1 (0.2%)
- `In September of 2016, I jumped the fairgate at a metro station in Fairfax, Virginia. I didn't have enough money on my Metro card, so I made the brash decision to attempt to jump the gate without paying. I was soon caught by a metro police officer. I was found guilty in 2017 and fined $150 for it. 

I sincerely regret this poor choice. The judge was lenient on me, as I had no prior infractions. I have not had any infractions since that day and have maintained a clean record since then. This was a major lesson for me; actions, no matter how small, can have long-term consequences.`: 1 (0.2%)
- `At the age of 16, I made a decision that to this day, I still regret. At 16 I chose to drink underaged and was charged with a Class C misdemeanor for minor in consumption of alcohol in Richardson, Texas. After I was charged with this I completed the volunteer hours required, enrolled in an alcohol and drug awareness course, and paid the fee of the ticket. At this time, I had no sense of the weight that each of my decisions made in my life. This moment established a realization in my life that was lacking. I learned that no matter how big or small the decision, each of my decisions would either add or subtract to my character. With this newfound awareness, I began my journey of character development. I stayed away from drinking, went back to church to renew my faith, and used my experience to turn my focus to family, education, and the future.`: 1 (0.2%)
- `I was cited for a minor in consumption May of 2017 in Breckenridge, MN. This is my only conviction and I was fined 225$ to which settled my debt to the state of Minnesota. There was no rehabilitation or community service required and there was no sentence imposed. While I realize that this was mistake I learned my lesson and as a result I came out more  mature and responsible.`: 1 (0.2%)
- `I received three speeding tickets in 2020 (all in Florida): One in January and the other two in August. Speeding is considered a misdemeanor in the state of Florida. I hired a ticket clinic law service to handle my case for each ticket. The legal representatives entered a plea of nolo contendere for each ticket. I paid each fine. After the third ticket, I was mandated to attend a basic drivers education course, which emphasized the dangers of speeding and safe driving practices. I am now very vigilant of my speed when I am driving and have not since received a ticket.`: 1 (0.2%)

**Military_Discharge_Ind** (Top 10 values):
- `No`: 437 (100.0%)

**Military_HON_Discharge_Ind** (Top 10 values):
- `0`: 437 (100.0%)

**Comm_Service_Ind** (Top 10 values):
- `Yes`: 435 (99.5%)
- `No`: 2 (0.5%)

**HealthCare_Ind** (Top 10 values):
- `Yes`: 437 (100.0%)

**Military_Service** (Top 10 values):
- `No`: 437 (100.0%)

**Pell_Grant** (Top 10 values):
- `No`: 303 (69.3%)
- `Yes`: 130 (29.7%)
- `Don't Know`: 3 (0.7%)
- `Decline to Answer`: 1 (0.2%)

**Fee_Assistance_Program** (Top 10 values):
- `No`: 340 (77.8%)
- `Yes`: 92 (21.1%)
- `Y - Invalid for Application Submission information`: 5 (1.1%)

**Childhood_Med_Underserved_Self_Reported** (Top 10 values):
- `No`: 281 (64.3%)
- `Yes`: 121 (27.7%)
- `Don't Know`: 33 (7.6%)
- `Decline to Answer`: 2 (0.5%)

**Family_Income_Level** (Top 10 values):
- `$50,000 - 74,999`: 65 (14.9%)
- `$75,000 - 99,999`: 62 (14.2%)
- `$25,000 - 49,999`: 48 (11.0%)
- `$100,000 - 124,999`: 48 (11.0%)
- `Less than $25,000`: 32 (7.3%)
- `Do not know`: 31 (7.1%)
- `$400,000 or more`: 25 (5.7%)
- `$125,000 - 149,999`: 23 (5.3%)
- `$150,000 - 174,999`: 17 (3.9%)
- `$200,000 - 224,999`: 16 (3.7%)

**Number_in_Household** (Top 10 values):
- `4`: 183 (41.9%)
- `5`: 110 (25.2%)
- `6`: 53 (12.1%)
- `3`: 51 (11.7%)
- `7`: 17 (3.9%)
- `2`: 8 (1.8%)
- `8`: 8 (1.8%)
- `9`: 4 (0.9%)
- `11`: 1 (0.2%)
- `16`: 1 (0.2%)

**Family_Assistance_Program** (Top 10 values):
- `No`: 276 (63.2%)
- `Yes`: 161 (36.8%)

**Paid_Employment_BF_18** (Top 10 values):
- `Yes`: 270 (61.8%)
- `No`: 167 (38.2%)

**Contribution_to_Family** (Top 10 values):
- `No`: 375 (85.8%)
- `Yes`: 62 (14.2%)

**Other_Loan_Percentage** (Top 10 values):
- `0.0`: 369 (84.4%)
- `15.0`: 3 (0.7%)
- `30.0`: 2 (0.5%)
- `25.0`: 2 (0.5%)
- `35.0`: 1 (0.2%)
- `12.5`: 1 (0.2%)
- `33.0`: 1 (0.2%)
- `27.9`: 1 (0.2%)
- `9.0`: 1 (0.2%)
- `50.0`: 1 (0.2%)

**Applicant_Contribution_Percentage** (Top 10 values):
- `0.0`: 253 (57.9%)
- `10.0`: 26 (5.9%)
- `5.0`: 21 (4.8%)
- `15.0`: 11 (2.5%)
- `25.0`: 10 (2.3%)
- `20.0`: 10 (2.3%)
- `2.0`: 9 (2.1%)
- `1.0`: 7 (1.6%)
- `4.0`: 6 (1.4%)
- `45.0`: 4 (0.9%)

**Other_Percentage** (Top 10 values):
- `0.0`: 373 (85.4%)
- `5.0`: 4 (0.9%)
- `80.0`: 4 (0.9%)
- `15.0`: 2 (0.5%)
- `100.0`: 2 (0.5%)
- `1.0`: 1 (0.2%)
- `25.0`: 1 (0.2%)
- `30.0`: 1 (0.2%)
- `50.0`: 1 (0.2%)
- `70.0`: 1 (0.2%)

**Application Review Score** (Top 10 values):
- `15`: 100 (22.9%)
- `19`: 81 (18.5%)
- `0`: 54 (12.4%)
- `25`: 52 (11.9%)
- `23`: 42 (9.6%)
- `21`: 37 (8.5%)
- `17`: 28 (6.4%)
- `11`: 27 (6.2%)
- `13`: 8 (1.8%)
- `7`: 3 (0.7%)

**Service Rating (Categorical)** (Top 10 values):
- `Significant`: 219 (50.1%)
- `Exceptional`: 148 (33.9%)
- `Lacking/Does Not Meet`: 49 (11.2%)
- `Adequate`: 21 (4.8%)

**Service Rating (Numerical)** (Top 10 values):
- `3`: 219 (50.1%)
- `4`: 148 (33.9%)
- `1`: 49 (11.2%)
- `2`: 21 (4.8%)

**Total_GPA_Trend** (Top 10 values):
- `1.0`: 196 (44.9%)
- `0.0`: 44 (10.1%)

**BCPM_GPA_Trend** (Top 10 values):
- `1.0`: 186 (42.6%)
- `0.0`: 42 (9.6%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| Appl_Year | 437 | 2022.00 | 0.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 |
| Amcas_ID | 437 | 15011632.22 | 363254.26 | 12950085.00 | 14880945.00 | 15057778.00 | 15243303.00 | 15499135.00 |
| Age | 437 | 26.34 | 2.86 | 22.00 | 25.00 | 26.00 | 27.00 | 62.00 |
| Num_Dependents | 437 | 0.03 | 0.21 | 0.00 | 0.00 | 0.00 | 0.00 | 2.00 |
| Prev_Matric_Sschool | 0 | nan | nan | nan | nan | nan | nan | nan |
| Prev_Matric_Year | 1 | 0.00 | nan | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Prev_Matric_Desc | 0 | nan | nan | nan | nan | nan | nan | nan |
| Felony_Desc | 0 | nan | nan | nan | nan | nan | nan | nan |
| Military_HON_Discharge_Ind | 437 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Military_Discharge_Desc | 0 | nan | nan | nan | nan | nan | nan | nan |
| Exp_Hour_Total | 437 | 10075.37 | 13163.75 | 704.00 | 4801.00 | 7524.00 | 11400.00 | 115474.00 |
| Exp_Hour_Research | 397 | 1395.81 | 2167.38 | 5.00 | 370.00 | 760.00 | 1555.00 | 24220.00 |
| Exp_Hour_Volunteer_Med | 396 | 643.58 | 873.54 | 16.00 | 200.00 | 438.00 | 700.50 | 9650.00 |
| Exp_Hour_Volunteer_Non_Med | 371 | 730.36 | 1172.24 | 10.00 | 191.00 | 390.00 | 773.50 | 12000.00 |
| Exp_Hour_Employ_Med | 318 | 2637.29 | 2399.54 | 30.00 | 967.50 | 2007.50 | 3515.00 | 16000.00 |
| Exp_Hour_Shadowing | 379 | 184.44 | 384.56 | 4.00 | 57.00 | 105.00 | 213.50 | 6760.00 |
| Comm_Service_Total_Hours | 437 | 1203.24 | 1413.07 | 0.00 | 475.00 | 773.00 | 1341.00 | 12000.00 |
| HealthCare_Total_Hours | 437 | 2662.28 | 2574.83 | 52.00 | 900.00 | 1886.00 | 3424.00 | 17860.00 |
| Military_Service_Status | 0 | nan | nan | nan | nan | nan | nan | nan |
| Number_in_Household | 437 | 4.61 | 1.38 | 0.00 | 4.00 | 4.00 | 5.00 | 16.00 |
| Academic_Scholarship_Percentage | 394 | 19.70 | 27.86 | 0.00 | 0.00 | 5.00 | 30.00 | 100.00 |
| Finacial_Need_Based_Percentage | 394 | 21.50 | 30.69 | 0.00 | 0.00 | 0.00 | 40.00 | 100.00 |
| Student_Loan_Percentage | 394 | 9.80 | 17.56 | 0.00 | 0.00 | 0.00 | 14.52 | 95.00 |
| Other_Loan_Percentage | 394 | 1.73 | 8.12 | 0.00 | 0.00 | 0.00 | 0.00 | 72.00 |
| Family_Contribution_Percentage | 394 | 40.03 | 38.92 | 0.00 | 1.00 | 25.00 | 80.00 | 100.00 |
| Applicant_Contribution_Percentage | 394 | 5.08 | 10.49 | 0.00 | 0.00 | 0.00 | 5.00 | 80.00 |
| Other_Percentage | 394 | 2.17 | 12.29 | 0.00 | 0.00 | 0.00 | 0.00 | 100.00 |
| Application Review Score | 437 | 16.07 | 7.30 | 0.00 | 15.00 | 17.00 | 21.00 | 25.00 |
| Service Rating (Numerical) | 437 | 3.07 | 0.91 | 1.00 | 3.00 | 3.00 | 4.00 | 4.00 |
| AMCAS ID | 437 | 15011632.22 | 363254.26 | 12950085.00 | 14880945.00 | 15057778.00 | 15243303.00 | 15499135.00 |
| Total_GPA_Trend | 240 | 0.82 | 0.39 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| BCPM_GPA_Trend | 228 | 0.82 | 0.39 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### 2023 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| Appl_Year | int64 | 1 | 0.0% |
| Amcas_ID | int64 | 401 | 0.0% |
| Prev_Applied_Rush | object | 7 | 88.3% |
| Age | int64 | 19 | 0.0% |
| Gender | object | 3 | 0.0% |
| Citizenship | object | 7 | 0.0% |
| SES_Value | object | 2 | 0.0% |
| Eo_Level | object | 2 | 74.8% |
| First_Generation_Ind | object | 2 | 0.0% |
| Disadvantanged_Ind | object | 2 | 0.0% |
| Hrdshp_Comments | object | 95 | 76.3% |
| RU_Ind | object | 2 | 0.0% |
| Num_Dependents | int64 | 4 | 0.0% |
| Inst_Action_Ind | object | 2 | 0.0% |
| Inst_Action_Desc | object | 20 | 95.0% |
| Prev_Matric_Ind | object | 1 | 0.0% |
| Prev_Matric_Sschool | float64 | 0 | 100.0% |
| Prev_Matric_Year | float64 | 1 | 99.5% |
| Prev_Matric_Desc | float64 | 0 | 100.0% |
| Investigation_Ind | object | 2 | 0.0% |
| Felony_Ind | object | 1 | 0.0% |
| Felony_Desc | float64 | 0 | 100.0% |
| Misdemeanor_Ind | object | 2 | 0.0% |
| Misdemeanor_Desc | object | 1 | 99.8% |
| Military_Discharge_Ind | object | 1 | 0.0% |
| Military_HON_Discharge_Ind | int64 | 2 | 0.0% |
| Military_Discharge_Desc | float64 | 0 | 100.0% |
| Exp_Hour_Total | int64 | 391 | 0.0% |
| Exp_Hour_Research | float64 | 239 | 7.7% |
| Exp_Hour_Volunteer_Med | float64 | 222 | 12.0% |
| Exp_Hour_Volunteer_Non_Med | float64 | 218 | 13.7% |
| Exp_Hour_Employ_Med | float64 | 262 | 13.7% |
| Exp_Hour_Shadowing | float64 | 141 | 16.0% |
| Comm_Service_Ind | object | 2 | 0.0% |
| Comm_Service_Total_Hours | int64 | 319 | 0.0% |
| HealthCare_Ind | object | 1 | 0.0% |
| HealthCare_Total_Hours | int64 | 376 | 0.0% |
| Highest_Test_Date_2015 | object | 86 | 0.0% |
| Under_School | object | 178 | 0.0% |
| Major_Long_Desc | object | 167 | 0.0% |
| Military_Service | object | 2 | 0.0% |
| Military_Service_Status | object | 3 | 98.0% |
| Pell_Grant | object | 4 | 0.0% |
| Fee_Assistance_Program | object | 3 | 0.0% |
| Childhood_Med_Underserved_Self_Reported | object | 4 | 0.0% |
| Family_Income_Level | object | 18 | 0.0% |
| Number_in_Household | int64 | 12 | 0.0% |
| Family_Assistance_Program | object | 2 | 0.0% |
| Paid_Employment_BF_18 | object | 2 | 0.0% |
| Contribution_to_Family | object | 2 | 0.0% |
| Academic_Scholarship_Percentage | float64 | 64 | 8.0% |
| Finacial_Need_Based_Percentage | float64 | 52 | 8.0% |
| Student_Loan_Percentage | float64 | 50 | 8.0% |
| Other_Loan_Percentage | float64 | 13 | 8.0% |
| Family_Contribution_Percentage | float64 | 61 | 8.0% |
| Applicant_Contribution_Percentage | float64 | 34 | 8.0% |
| Other_Percentage | float64 | 23 | 8.0% |
| Application Review Score | int64 | 14 | 0.0% |
| Service Rating (Categorical) | object | 4 | 0.0% |
| Service Rating (Numerical) | int64 | 4 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  Appl_Year: 2023
  Amcas_ID: 13278986
  Prev_Applied_Rush: 2019; 2021
  Age: 34
  Gender: Woman
  Citizenship: USA
  SES_Value: No
  Eo_Level: nan
  First_Generation_Ind: No
  Disadvantanged_Ind: No
Row 2:
  Appl_Year: 2023
  Amcas_ID: 13767033
  Prev_Applied_Rush: nan
  Age: 29
  Gender: Another Gender Identity
  Citizenship: USA
  SES_Value: Yes
  Eo_Level: EO2
  First_Generation_Ind: No
  Disadvantanged_Ind: Yes
Row 3:
  Appl_Year: 2023
  Amcas_ID: 13769330
  Prev_Applied_Rush: 2021
  Age: 29
  Gender: Woman
  Citizenship: USA
  SES_Value: Yes
  Eo_Level: EO1
  First_Generation_Ind: Yes
  Disadvantanged_Ind: Yes
```

#### Categorical Column Distributions

**Appl_Year** (Top 10 values):
- `2023`: 401 (100.0%)

**Prev_Applied_Rush** (Top 10 values):
- `2022`: 19 (4.7%)
- `2021`: 16 (4.0%)
- `2020; 2021`: 4 (1.0%)
- `2021; 2022`: 4 (1.0%)
- `2020`: 2 (0.5%)
- `2019; 2021`: 1 (0.2%)
- `2019; 2020`: 1 (0.2%)

**Age** (Top 10 values):
- `24`: 93 (23.2%)
- `25`: 92 (22.9%)
- `23`: 59 (14.7%)
- `26`: 47 (11.7%)
- `27`: 28 (7.0%)
- `22`: 18 (4.5%)
- `29`: 18 (4.5%)
- `28`: 17 (4.2%)
- `32`: 6 (1.5%)
- `30`: 5 (1.2%)

**Gender** (Top 10 values):
- `Woman`: 231 (57.6%)
- `Man`: 167 (41.6%)
- `Another Gender Identity`: 3 (0.7%)

**Citizenship** (Top 10 values):
- `USA`: 388 (96.8%)
- `MEX`: 7 (1.7%)
- `IND`: 2 (0.5%)
- `GUY`: 1 (0.2%)
- `CAN`: 1 (0.2%)
- `ETH`: 1 (0.2%)
- `IRQ`: 1 (0.2%)

**SES_Value** (Top 10 values):
- `No`: 300 (74.8%)
- `Yes`: 101 (25.2%)

**Eo_Level** (Top 10 values):
- `EO1`: 74 (18.5%)
- `EO2`: 27 (6.7%)

**First_Generation_Ind** (Top 10 values):
- `No`: 333 (83.0%)
- `Yes`: 68 (17.0%)

**Disadvantanged_Ind** (Top 10 values):
- `No`: 306 (76.3%)
- `Yes`: 95 (23.7%)

**RU_Ind** (Top 10 values):
- `U`: 393 (98.0%)
- `R`: 8 (2.0%)

**Num_Dependents** (Top 10 values):
- `0`: 391 (97.5%)
- `1`: 6 (1.5%)
- `2`: 3 (0.7%)
- `3`: 1 (0.2%)

**Inst_Action_Ind** (Top 10 values):
- `No`: 381 (95.0%)
- `Yes`: 20 (5.0%)

**Inst_Action_Desc** (Top 10 values):
- `In my freshman year, Spring 2006, I was placed on academic probation due to poor grades. I lacked the maturity to make the adjustments necessary to succeed in college. Though I was able to be removed from academic probation after Fall 2006, I found myself on academic probation again in Spring 2007. During Summer 2007, I took classes at San Diego CC; during that time, my grandpa became sick, and I spent time back home without completing my courses, putting me on academic probation. Days before the start of Fall 2007, my grandpa passed away after battling cancer. Attempting to cope with his loss and maintain satisfactory academic performance was too much for me, and I was academically dismissed from San Diego State after the Fall 2007 semester. I attempted to continue my education at the local community college in Spring 2008 but made no changes to my academic habits or attempts to heal from my grief. I was academically dismissed from San Diego CC. In reflection, I should have taken a leave of absence from academics to cope with my loss, but a leave would have likely just delayed the inevitable as I had failed to change my study habits. When I returned to school, I had improved time management and study habits.`: 1 (0.2%)
- `In the spring of 2014, I was placed on departmental academic probation. I was taking 2-5 science classes like biochemistry, microbiology, organic chemistry, and labs. I wanted to take the same classes as my peers, ignoring my lack of a solid academic foundation and socioeconomic hardships. 
 
I was hungry and couch surfing, while also taking time to go to my mother’s appointments 3 hours away by bus. I would often become emotionally overwhelmed with family, financial, and immigration worries and was unable to focus on class. We were severely in debt as my mother went through her cancer treatments and once I gained the right to legal employment in 2013, I became the head of household.  I feared DACA immigration policy would end, and I would be unable to continue to support my family. 
 
From 2014 until my graduation in 2017, I was not placed on departmental academic probation again. I found mentors, worked less so I could attend office hours, and joined study groups; I learned I enjoy teaching others. These experiences taught me to have good communication with family members to support my mother, good time management to balance school, work, and studying, as well as the humility to ask for help when necessary to move ahead. I can appreciate the hardships I experienced because of the resilience developed.`: 1 (0.2%)
- `In my first week of college during my first freshman semester, I received a dorm conduct violation for writing on my friend's door decorations in the residence hall. I took full responsibility for my actions and reported myself to the resident assistant. I subsequently wrote apology letters and redid all door decorations for the residents. After the incident, I reflected on my character and did not want these actions to represent who I am. I worked diligently to earn a leadership position in the campus dorms. I learned the importance of integrity and that our immature decisions have consequences. I greatly regret my mistake but am fortunate to have been able to redeem my character, learn from my mistakes, and I did not receive any other disciplinary actions throughout college.`: 1 (0.2%)
- `In preparation for the Cell Biology midterm my sophomore year, I created an extensive study guide that covered all class materials in great detail. During group study sessions leading up to the exam, my classmates and I discussed important concepts using my study guide as an outline. When taking the open-book, online exam, I utilized my study guide the best I could. However, this study guide was shared to the classmates I worked with, and I was naive to use the same study material on an exam that did not permit group-work. On two questions that asked about a specific concept that we had covered during the study sessions, my classmates and I had written an answer that was nearly identical to what was on my study guide. 

Ultimately, I was responsible for sharing my study guide with my classmates. Studying as a group is a valuable learning method, but it is a different story when that led to a gateway of cheating in an exam that strictly prohibited collaboration. I should have been aware that as an open-book exam, sharing a study guide was a risk factor for both myself and my fellow classmates. I pushed my boundaries to an extent I now realize I should not have, and it was an experience that fundamentally changed my mindset regarding the need to be more cognizant of my own behavior and those around me.`: 1 (0.2%)
- `1/16/2020 - My roommate and I were fined $5.00 for a residence hall violation for stacking boxes near our window area when they were not supposed to be there. During the weekly inspection of all dorm rooms, our resident hall director determined that the floor of our room was not clear of personal belongings. Specifically, on the fine, he noted that he "noticed a large pile of boxes and belongings in the back of the room by the window."

2/24/2021 - My roommate and I were fined $5.00 for a residence hall violation. We had left our room for class and failed to clear our textbooks off of the floor. During the weekly inspection of all dorm rooms, our resident hall director determined that the floor of our room was not clean. Specifically, on the fine, he noted that our room "did not meet the outlined expectations for room checks."

My roommate and I failed to work together to ensure that our room met residence hall standards on two separate occasions. I learned that when things are not up to standard, it is the responsibility of all team members, not just an individual, to directly correct or mitigate issues. My roommate and I should have functioned as a team, and we were met with consequences when we did not do so. I have realized that this lesson is highly applicable to healthcare as well as everyday life.`: 1 (0.2%)
- `On Sunday, September 4th, 2016, during my first three-day weekend as a first-year undergraduate student, I attended a small gathering in another dorm room. Shortly after I arrived, at around 10:00 pm, the Resident Assistant knocked on the door and explained that the noise level in the room was too loud. He took the student ID information from everyone in the room. I was assigned an excessive noise violation for being in attendance at the gathering. As the first person in my family to attend college out of state, I was excited to mingle and meet new people. However, I realized after this incident that I was also contributing to a disturbance for neighboring students. As the eldest sibling in my family, I understand the importance of leading by example for my younger sister and acknowledging areas of improvement. After receiving the noise violation, I completed community service hours at the LGBTQ+ Resource Center. Through community service, I was able to meet some amazing people at the center as well as at the Women’s Center next door. This experience gave me the opportunity early on in my college career to reflect on how I wanted to move forward in my next four years. As I progressed through my undergraduate years, I met so many people through clubs and classes who remain my close friends to this day.`: 1 (0.2%)
- `In October of my freshman fall semester, I was asked to meet with Student Conduct about an alcohol infraction. My roommate had recently called an RA to my aid one Saturday night because I went out and drank more than I should've. As a first-year new to campus, there was much stress in my world. I was acclimating to intense academic rigor and a heavy athletic training schedule. After receiving my first ever C on a college exam, I went into the weekend with a lot of emotions. I later took responsibility for my actions. Stress is no excuse to drink recklessly. My conduct counselor advised me to explain the situation to my family and behave smarter in the future. Nothing of the sort ever happened again. 

In the spring semester of my senior year, I was asked to meet with Student Conduct about a community standard violation. A few weeks prior, I attended a boxing class with friends. In minding the community standard, we all wore masks and put together a group of 10, which was the maximum number that Duke allowed to gather. However, after the class, the group took a picture to capture the moment. Because the boxing instructor and the receptionist hopped into the photo, our group jumped to 12. The violation was excused, but I held myself accountable and recognize the importance of health guidelines.`: 1 (0.2%)
- `In May of 2020, we had just started the lockdown, and our coursework had become fully online. During the Physics 1 final, I attempted to access information while taking the exam, which was not permitted. I was caught doing so and reported to the Dean of Students. A few months later, during the fall semester, I had a meeting with the Dean and the instructor of the course, where we discussed my transgressions and what the consequences would be. I was placed on Academic Probation, had a mark of Academic Dishonesty placed on my record, and wrote a two page essay detailing what I had done wrong, the lessons I had learned, and what I would do if I was to be placed in that situation again. This was the biggest mistake I have made in my academic career, and I deeply regret having made it. After going through that process, I have done everything I could to compensate for the mistake, and have grown both academically and personally. I hope to continue to grow as a student and person and to avoid making bad decisions such as academic dishonesty again.`: 1 (0.2%)
- `During Winter break of the 2019-2020 school year, the RA staff searched rooms and I received a write-up for one empty spiked seltzer can in my trash can. This can was in fact not mine, but I understand that because it was my trash can it is my responsibility. I only received a warning and did not meet with the Dean.`: 1 (0.2%)
- `Twenty-two years ago, in the spring of 2000, I plagiarized a paragraph of text on an essay. I was running out of time to submit the essay for a class that I had deprioritized in favor of writing my undergraduate thesis. The violation was obvious and in a meeting with the professor and the dean, I received the punishment of a failing grade in the class and a one-year hold on my diploma. This disrupted my post-graduate plans considerably and led to much soul-searching about how I could reach such a low point in my previously unblemished academic life. More than two decades later I can call up these feelings of shame and regret easily.

I believe I emerged from this episode a better student and a more compassionate person. First, I learned to overcome my natural timidity and reach out to my instructors for help when I was struggling in a class. Second, I took responsibility for my terrible decision and lived with the consequences of getting an F in a class and not graduating on time. Third, I learned to forgive myself and move forward, eventually earning three other degrees with zero academic integrity issues. As I look back on this experience with the benefit of time, I believe that finding empathy for myself directly led to my desire to help others.`: 1 (0.2%)

**Prev_Matric_Ind** (Top 10 values):
- `No`: 401 (100.0%)

**Prev_Matric_Year** (Top 10 values):
- `0.0`: 2 (0.5%)

**Investigation_Ind** (Top 10 values):
- `No`: 400 (99.8%)
- `Yes`: 1 (0.2%)

**Felony_Ind** (Top 10 values):
- `No`: 401 (100.0%)

**Misdemeanor_Ind** (Top 10 values):
- `No`: 400 (99.8%)
- `Yes`: 1 (0.2%)

**Misdemeanor_Desc** (Top 10 values):
- `During my freshman year of college, I was driving home to see my family for Easter when I was pulled over for speeding. This occurred is Mexico, Missouri on 04/20/2019 in which I exceeded the speed limit by 11-15 miles per hour which is classified as a misdemeanor class C in Missouri. For this offence, the sentence imposed was a fine of $70.50. For my own improvement, I enrolled in a driving safety course and learned about the dangers of speeding and the potential consequences. As I have gotten older, I have realized the impact that one person driving at a higher speed can have on others around them. I now always drive diligently and have not incurred any other violations.`: 1 (0.2%)

**Military_Discharge_Ind** (Top 10 values):
- `No`: 401 (100.0%)

**Military_HON_Discharge_Ind** (Top 10 values):
- `0`: 398 (99.3%)
- `1`: 3 (0.7%)

**Comm_Service_Ind** (Top 10 values):
- `Yes`: 394 (98.3%)
- `No`: 7 (1.7%)

**HealthCare_Ind** (Top 10 values):
- `Yes`: 401 (100.0%)

**Military_Service** (Top 10 values):
- `No`: 393 (98.0%)
- `Yes`: 8 (2.0%)

**Military_Service_Status** (Top 10 values):
- `Veteran`: 4 (1.0%)
- `US Reserves or National Guard`: 3 (0.7%)
- `Active Duty`: 1 (0.2%)

**Pell_Grant** (Top 10 values):
- `No`: 279 (69.6%)
- `Yes`: 116 (28.9%)
- `Don't Know`: 5 (1.2%)
- `Decline to Answer`: 1 (0.2%)

**Fee_Assistance_Program** (Top 10 values):
- `No`: 324 (80.8%)
- `Yes`: 74 (18.5%)
- `Y - Invalid for Application Submission information`: 3 (0.7%)

**Childhood_Med_Underserved_Self_Reported** (Top 10 values):
- `No`: 243 (60.6%)
- `Yes`: 116 (28.9%)
- `Don't Know`: 38 (9.5%)
- `Decline to Answer`: 4 (1.0%)

**Family_Income_Level** (Top 10 values):
- `$50,000 - 74,999`: 54 (13.5%)
- `$100,000 - 124,999`: 50 (12.5%)
- `$75,000 - 99,999`: 49 (12.2%)
- `$25,000 - 49,999`: 48 (12.0%)
- `$400,000 or more`: 34 (8.5%)
- `Less than $25,000`: 27 (6.7%)
- `Do not know`: 26 (6.5%)
- `$150,000 - 174,999`: 23 (5.7%)
- `$200,000 - 224,999`: 20 (5.0%)
- `$125,000 - 149,999`: 17 (4.2%)

**Number_in_Household** (Top 10 values):
- `4`: 151 (37.7%)
- `5`: 103 (25.7%)
- `6`: 63 (15.7%)
- `3`: 42 (10.5%)
- `7`: 21 (5.2%)
- `8`: 8 (2.0%)
- `2`: 5 (1.2%)
- `10`: 4 (1.0%)
- `14`: 1 (0.2%)
- `9`: 1 (0.2%)

**Family_Assistance_Program** (Top 10 values):
- `No`: 249 (62.1%)
- `Yes`: 152 (37.9%)

**Paid_Employment_BF_18** (Top 10 values):
- `Yes`: 268 (66.8%)
- `No`: 133 (33.2%)

**Contribution_to_Family** (Top 10 values):
- `No`: 341 (85.0%)
- `Yes`: 60 (15.0%)

**Student_Loan_Percentage** (Top 10 values):
- `0.0`: 232 (57.9%)
- `10.0`: 13 (3.2%)
- `50.0`: 13 (3.2%)
- `25.0`: 11 (2.7%)
- `20.0`: 10 (2.5%)
- `40.0`: 8 (2.0%)
- `5.0`: 8 (2.0%)
- `30.0`: 8 (2.0%)
- `100.0`: 6 (1.5%)
- `15.0`: 5 (1.2%)

**Other_Loan_Percentage** (Top 10 values):
- `0.0`: 350 (87.3%)
- `10.0`: 4 (1.0%)
- `20.0`: 3 (0.7%)
- `5.0`: 2 (0.5%)
- `15.0`: 2 (0.5%)
- `85.0`: 1 (0.2%)
- `17.0`: 1 (0.2%)
- `4.0`: 1 (0.2%)
- `25.0`: 1 (0.2%)
- `50.0`: 1 (0.2%)

**Applicant_Contribution_Percentage** (Top 10 values):
- `0.0`: 215 (53.6%)
- `10.0`: 41 (10.2%)
- `5.0`: 38 (9.5%)
- `20.0`: 9 (2.2%)
- `2.0`: 7 (1.7%)
- `15.0`: 6 (1.5%)
- `1.0`: 4 (1.0%)
- `3.0`: 4 (1.0%)
- `8.0`: 4 (1.0%)
- `50.0`: 4 (1.0%)

**Other_Percentage** (Top 10 values):
- `0.0`: 337 (84.0%)
- `35.0`: 3 (0.7%)
- `50.0`: 3 (0.7%)
- `20.0`: 2 (0.5%)
- `4.0`: 2 (0.5%)
- `80.0`: 2 (0.5%)
- `10.0`: 2 (0.5%)
- `30.0`: 2 (0.5%)
- `100.0`: 2 (0.5%)
- `2.0`: 1 (0.2%)

**Application Review Score** (Top 10 values):
- `19`: 71 (17.7%)
- `15`: 68 (17.0%)
- `11`: 49 (12.2%)
- `17`: 43 (10.7%)
- `21`: 37 (9.2%)
- `13`: 30 (7.5%)
- `25`: 26 (6.5%)
- `23`: 24 (6.0%)
- `9`: 23 (5.7%)
- `7`: 17 (4.2%)

**Service Rating (Categorical)** (Top 10 values):
- `Significant`: 182 (45.4%)
- `Adequate`: 118 (29.4%)
- `Exceptional`: 93 (23.2%)
- `Lacking/Does Not Meet`: 8 (2.0%)

**Service Rating (Numerical)** (Top 10 values):
- `3`: 182 (45.4%)
- `2`: 118 (29.4%)
- `4`: 93 (23.2%)
- `1`: 8 (2.0%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| Appl_Year | 401 | 2023.00 | 0.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 |
| Amcas_ID | 401 | 15219108.26 | 377750.72 | 13278986.00 | 15039509.00 | 15273506.00 | 15477871.00 | 15758293.00 |
| Age | 401 | 25.45 | 2.86 | 21.00 | 24.00 | 25.00 | 26.00 | 45.00 |
| Num_Dependents | 401 | 0.04 | 0.26 | 0.00 | 0.00 | 0.00 | 0.00 | 3.00 |
| Prev_Matric_Sschool | 0 | nan | nan | nan | nan | nan | nan | nan |
| Prev_Matric_Year | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Prev_Matric_Desc | 0 | nan | nan | nan | nan | nan | nan | nan |
| Felony_Desc | 0 | nan | nan | nan | nan | nan | nan | nan |
| Military_HON_Discharge_Ind | 401 | 0.01 | 0.09 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| Military_Discharge_Desc | 0 | nan | nan | nan | nan | nan | nan | nan |
| Exp_Hour_Total | 401 | 9543.35 | 22710.29 | 1208.00 | 4221.00 | 6389.00 | 10140.00 | 412667.00 |
| Exp_Hour_Research | 370 | 1061.40 | 1345.59 | 0.00 | 294.00 | 651.00 | 1272.00 | 10550.00 |
| Exp_Hour_Volunteer_Med | 353 | 509.38 | 771.78 | 0.00 | 105.00 | 290.00 | 576.00 | 8000.00 |
| Exp_Hour_Volunteer_Non_Med | 346 | 774.39 | 5767.43 | 7.00 | 131.25 | 300.00 | 587.50 | 107299.00 |
| Exp_Hour_Employ_Med | 346 | 2509.21 | 2940.50 | 0.00 | 712.50 | 1500.00 | 3490.00 | 23000.00 |
| Exp_Hour_Shadowing | 337 | 123.07 | 177.62 | 0.00 | 48.00 | 80.00 | 133.00 | 2439.00 |
| Comm_Service_Total_Hours | 401 | 1116.58 | 5402.02 | 0.00 | 320.00 | 570.00 | 1080.00 | 107487.00 |
| HealthCare_Total_Hours | 401 | 2716.89 | 3013.88 | 100.00 | 916.00 | 1800.00 | 3450.00 | 23000.00 |
| Number_in_Household | 401 | 4.79 | 1.45 | 1.00 | 4.00 | 5.00 | 5.00 | 14.00 |
| Academic_Scholarship_Percentage | 369 | 20.98 | 26.87 | 0.00 | 0.00 | 7.00 | 37.50 | 100.00 |
| Finacial_Need_Based_Percentage | 369 | 17.82 | 27.77 | 0.00 | 0.00 | 0.00 | 30.00 | 100.00 |
| Student_Loan_Percentage | 369 | 11.69 | 22.12 | 0.00 | 0.00 | 0.00 | 14.00 | 100.00 |
| Other_Loan_Percentage | 369 | 1.33 | 7.76 | 0.00 | 0.00 | 0.00 | 0.00 | 85.00 |
| Family_Contribution_Percentage | 369 | 39.12 | 39.55 | 0.00 | 0.00 | 25.00 | 80.00 | 100.00 |
| Applicant_Contribution_Percentage | 369 | 6.19 | 13.35 | 0.00 | 0.00 | 0.00 | 7.00 | 100.00 |
| Other_Percentage | 369 | 2.87 | 12.32 | 0.00 | 0.00 | 0.00 | 0.00 | 100.00 |
| Application Review Score | 401 | 15.94 | 5.18 | 2.00 | 11.00 | 17.00 | 19.00 | 25.00 |
| Service Rating (Numerical) | 401 | 2.90 | 0.77 | 1.00 | 2.00 | 3.00 | 3.00 | 4.00 |

### 2024 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| Appl_Year | int64 | 1 | 0.0% |
| Amcas_ID | int64 | 613 | 0.0% |
| Prev_Applied_Rush | object | 11 | 85.3% |
| Age | int64 | 19 | 0.0% |
| Gender | object | 4 | 0.0% |
| Citizenship | object | 16 | 0.0% |
| SES_Value | object | 2 | 0.0% |
| Eo_Level | object | 2 | 78.8% |
| First_Generation_Ind | object | 2 | 0.0% |
| Disadvantanged_Ind | object | 1 | 0.0% |
| Hrdshp_Comments | float64 | 0 | 100.0% |
| RU_Ind | object | 2 | 0.0% |
| Num_Dependents | int64 | 3 | 0.0% |
| Inst_Action_Ind | object | 2 | 0.0% |
| Inst_Action_Desc | object | 38 | 93.8% |
| Prev_Matric_Ind | object | 2 | 0.0% |
| Prev_Matric_Sschool | object | 1 | 99.8% |
| Prev_Matric_Year | float64 | 2 | 99.3% |
| Prev_Matric_Desc | object | 1 | 99.8% |
| Investigation_Ind | object | 1 | 0.0% |
| Felony_Ind | object | 1 | 0.0% |
| Felony_Desc | float64 | 0 | 100.0% |
| Misdemeanor_Ind | object | 2 | 0.0% |
| Misdemeanor_Desc | object | 3 | 99.5% |
| Military_Discharge_Ind | object | 1 | 0.0% |
| Military_HON_Discharge_Ind | int64 | 2 | 0.0% |
| Military_Discharge_Desc | float64 | 0 | 100.0% |
| Exp_Hour_Total | int64 | 594 | 0.0% |
| Exp_Hour_Research | float64 | 296 | 8.2% |
| Exp_Hour_Volunteer_Med | float64 | 328 | 10.9% |
| Exp_Hour_Volunteer_Non_Med | float64 | 319 | 10.3% |
| Exp_Hour_Employ_Med | float64 | 343 | 16.0% |
| Exp_Hour_Shadowing | float64 | 202 | 13.7% |
| Comm_Service_Ind | object | 2 | 0.0% |
| Comm_Service_Total_Hours | int64 | 441 | 0.0% |
| HealthCare_Ind | object | 1 | 0.0% |
| HealthCare_Total_Hours | int64 | 544 | 0.0% |
| Highest_Test_Date_2015 | object | 91 | 0.0% |
| Under_School | object | 198 | 0.2% |
| Major_Long_Desc | object | 236 | 0.2% |
| Military_Service | object | 2 | 0.0% |
| Military_Service_Status | object | 3 | 99.2% |
| Pell_Grant | object | 4 | 0.0% |
| Fee_Assistance_Program | object | 3 | 0.0% |
| Childhood_Med_Underserved_Self_Reported | object | 4 | 0.0% |
| Family_Income_Level | object | 19 | 0.0% |
| Number_in_Household | int64 | 14 | 0.0% |
| Family_Assistance_Program | object | 2 | 0.0% |
| Paid_Employment_BF_18 | object | 2 | 0.0% |
| Contribution_to_Family | object | 2 | 0.0% |
| Academic_Scholarship_Percentage | float64 | 60 | 11.1% |
| Finacial_Need_Based_Percentage | float64 | 59 | 11.1% |
| Student_Loan_Percentage | float64 | 55 | 11.1% |
| Other_Loan_Percentage | float64 | 14 | 11.1% |
| Family_Contribution_Percentage | float64 | 81 | 11.1% |
| Applicant_Contribution_Percentage | float64 | 38 | 11.1% |
| Other_Percentage | float64 | 15 | 11.1% |
| Application_Review_Score | int64 | 22 | 0.0% |
| Service_Rating_Categorical | object | 4 | 0.0% |
| Service_Rating_Numerical | int64 | 4 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  Appl_Year: 2024
  Amcas_ID: 13149516
  Prev_Applied_Rush: nan
  Age: 38
  Gender: Man
  Citizenship: USA
  SES_Value: Yes
  Eo_Level: EO1
  First_Generation_Ind: Yes
  Disadvantanged_Ind: No
Row 2:
  Appl_Year: 2024
  Amcas_ID: 13573284
  Prev_Applied_Rush: nan
  Age: 31
  Gender: Woman
  Citizenship: USA
  SES_Value: No
  Eo_Level: nan
  First_Generation_Ind: No
  Disadvantanged_Ind: No
Row 3:
  Appl_Year: 2024
  Amcas_ID: 13596519
  Prev_Applied_Rush: 2022
  Age: 32
  Gender: Woman
  Citizenship: USA
  SES_Value: No
  Eo_Level: nan
  First_Generation_Ind: No
  Disadvantanged_Ind: No
```

#### Categorical Column Distributions

**Appl_Year** (Top 10 values):
- `2024`: 613 (100.0%)

**Prev_Applied_Rush** (Top 10 values):
- `2023`: 56 (9.1%)
- `2022`: 19 (3.1%)
- `2022; 2023`: 4 (0.7%)
- `2021`: 2 (0.3%)
- `2020; 2021`: 2 (0.3%)
- `2020`: 2 (0.3%)
- `2018; 2021; 2022`: 1 (0.2%)
- `2019; 2023`: 1 (0.2%)
- `2019`: 1 (0.2%)
- `2019; 2020; 2021`: 1 (0.2%)

**Age** (Top 10 values):
- `23`: 158 (25.8%)
- `24`: 145 (23.7%)
- `22`: 84 (13.7%)
- `25`: 70 (11.4%)
- `26`: 41 (6.7%)
- `27`: 32 (5.2%)
- `21`: 26 (4.2%)
- `28`: 20 (3.3%)
- `29`: 12 (2.0%)
- `31`: 7 (1.1%)

**Gender** (Top 10 values):
- `Woman`: 380 (62.0%)
- `Man`: 229 (37.4%)
- `Another Gender Identity`: 3 (0.5%)
- `Decline to Answer`: 1 (0.2%)

**Citizenship** (Top 10 values):
- `USA`: 578 (94.3%)
- `KOR`: 6 (1.0%)
- `IND`: 5 (0.8%)
- `MEX`: 4 (0.7%)
- `CAN`: 4 (0.7%)
- `NGA`: 4 (0.7%)
- `TUR`: 2 (0.3%)
- `CHN`: 2 (0.3%)
- `BRA`: 1 (0.2%)
- `VNM`: 1 (0.2%)

**SES_Value** (Top 10 values):
- `No`: 483 (78.8%)
- `Yes`: 130 (21.2%)

**Eo_Level** (Top 10 values):
- `EO1`: 91 (14.8%)
- `EO2`: 39 (6.4%)

**First_Generation_Ind** (Top 10 values):
- `No`: 516 (84.2%)
- `Yes`: 97 (15.8%)

**Disadvantanged_Ind** (Top 10 values):
- `No`: 613 (100.0%)

**RU_Ind** (Top 10 values):
- `U`: 603 (98.4%)
- `R`: 10 (1.6%)

**Num_Dependents** (Top 10 values):
- `0`: 596 (97.2%)
- `1`: 13 (2.1%)
- `2`: 4 (0.7%)

**Inst_Action_Ind** (Top 10 values):
- `No`: 575 (93.8%)
- `Yes`: 38 (6.2%)

**Inst_Action_Desc** (Top 10 values):
- `In 02/2012, prior to turning 21 in undergrad, I received a warning letter for a low-level (per school's classification) violation for alcohol at a student gathering. At that time, I had just applied to be a resident assistant and, as a consequence to my actions, my application was denied. There were no other penalties or sanctions. I appreciated that I was held accountable for my actions as it taught me the importance of following all rules. I was and remain remorseful for my actions and have not had any violations since.`: 1 (0.2%)
- `In Winter quarter of 2021 (February), my lab partner and I collaborated on an online Organic Chemistry lab assignment. Since my classmate was short on time, I allowed her to plagiarize some of my answers. We accepted our consequences and received zero credit on the assignment. For the remainder of the year, I was placed on academic probation. I then took an Academic Integrity class in Spring Quarter of 2021 and was reminded of the importance of moral values and integrity. The class also reminded me how allowing others to plagiarize my work is still a violation of academic integrity and that in order to set a good example to others, I need to first be able to uphold my values of honesty, integrity, and responsibility. Since then, I have personally grown and reflected on my actions and am committed to upholding these values. I have worked my hardest to change and will never forget the mistake I made. I have been committed to completing all of my assignments with the utmost integrity ever since and have vowed to continue doing so for all my future assignments. I will never again share my work for others to claim or ever claim another person's work as my own.`: 1 (0.2%)
- `As a freshman on April 13, 2020, I was cited for using my peer’s work in part of my submission for Introduction to Theatre (THEA 101). As a result of this action, I received a 0 on this assignment. This incident served as a pivotal moment as I reflected on my actions. I realized that such an action not only undermines the integrity of my education system but also hinders my individual growth and development. I had let myself down and sought to employ my best judgment in my work and daily life moving forward.

Becoming a teacher for ENG 100, an introductory course required to be taken by all freshmen in engineering, allowed me to channel this lesson into a tangible impact. By emphasizing the importance of maintaining integrity and sharing my experience, I aimed to instill ethical habits early on in the college careers of freshmen. Through my academic integrity violation, I have also developed a greater sense of responsibility and self-awareness. True success is not measured solely by my external achievements, but by the character and integrity I cultivate on the path. For the last 3 years, I have submitted work that I am proud of, knowing that it is the result of my own efforts and merit. I will continue this same commitment to integrity and personal growth in medical school.`: 1 (0.2%)
- `On 10/12/2020, I violated a housing policy. The policy states that on-campus guests are not permitted if assigned to different buildings, apartments, or complexes and who do not have the same level of access to an on-campus, residential area. This policy was put in place due to COVID-19. During this time, there was great confusion surrounding the guest policy since it was changing frequently. At the time of the incident, my resident assistant (RA) misinformed us that we were allowed to have guests as long as we lived in the same "area", which usually consisted of 4-5 dorm buildings. As a result, I believed it was allowed for me to visit a friend who lived in a dorm building in my area. We were in the common area of her floor and were wearing masks and social distancing. However, her RA said that I was not allowed to be there and she reported the incident. Despite the misunderstanding, I was found responsible for the violation by the conduct office because the rule was clearly stated in the housing manual. After this experience, I take full accountability for my mistake given that I was responsible for reading the housing manual in full before living on campus. After this incident, I read all of the conduct rules and never committed a violation again. I always remained in good standing at the university.`: 1 (0.2%)
- `I was the recipient of an institutional action from St. Louis University for a conduct violation. In the end of 2019, I found a laptop under my seat on the train home from SLU. With the intention to return it to its owner, I put the laptop in my backpack. Once I came home and opened the device, the cops came to my home. After detailing the story of how I found it, they took the device with them. 

Later that week, I was mailed a letter stating that I had to meet with SLU’s committee because the laptop belonged to a SLU student. They had doubts that I stole the laptop. After committee hearings and the preponderance of evidence standard, the committee gave me a sanction. This was an isolated situation, one where I did not feel like I was properly able to make my case. 

I believe in my heart that I did the right thing that day. I tried to report a lost item and use my knowledge to track its owner. Over the next couple of years, I have tried with every ounce of effort to do the right thing no matter how hard it seems. I pushed forward so as to not disrupt my education. I am not glad that this situation occurred by any means, however, I persevered through many challenges because I knew my end goal was to become a physician. At Loyola, I have never received any sanctions nor have I been accused.`: 1 (0.2%)
- `On April 13th, 2019 I was charged with a noise violation when I had friends over in my dorm room and received a disciplinary probation period of four months.

On October 4th, 2019 I was charged with underage presence of alcohol when I attended a friend's birthday party in someone's dorm. I accepted responsibility for being in the presence of alcohol and was given a written warning.`: 1 (0.2%)
- `In the Spring of my first-year (2018) at Northwestern University, I foolishly pulled the fire alarm when there was no fire. I was challenged by a peer to see how far I could pull the lever without the alarm going off. I pushed the alarm just a millimeter further than it should have gone.  I immediately reported myself to the security guard at the front desk to let him know that there was no real fire. I believe that turning myself in speaks volumes to my integrity and accountability.

This was one of my biggest lessons learned in college. There are consequences to actions and I take full responsibility for my wrongdoing. I believe that I have grown tremendously since this moment; I am thoughtful in my actions and I have processed the importance of public safety. I was placed on housing probation for the rest of that year, and have not had any institutional actions since.`: 1 (0.2%)
- `In my third week of college as a freshman at Gonzaga University, I violated Gonzaga University’s Alcohol Policy. Following the incident, I met with our Residence Director and I admitted that I was drinking in the dorm with my peers. I was required to pay a fine. I apologized to the Residence Director and my RA for having to enforce the rules. This was the only institutional action I have received.

I am thankful for the growth that I experienced following this incident and in the seven years since its occurrence. Accepting this mistake helped me mature while teaching me that my actions illustrate my integrity. The integrity that I continued to build during my time in college and continue to build to this day.`: 1 (0.2%)
- `I had a meeting with my college Provost as a result of having similar answers with some of my classmates on three lab assignments. During my second year at UCSC, I was enrolled in an online Stats Lab course (AMS 7L) that lacked in-person sections or lectures. The course was structured in such a way that collaboration with fellow students was allowed as long as we completed the work ourselves. As a result, I would sometimes meet up with two friends from the class and we would go through the lab together to make sure we understood how to do that week’s lab assignment. After going through the lab, we would then split-up and complete the assignments individually. Unfortunately, due to our use of a shared “base” number during these collaborative sessions (as subsequent answers depended on the previous answer), we produced similar answers on three of the labs. At the time, I was not aware we were ending up with similar answers and I had no intention to do so. Consequently of doing so unknowingly, I was given a warning from the Provost and was told to not work together on the assignments again. While I don’t regret my efforts working with my peers to help each other understand the lab content, I am ashamed of the outcome. This experience has taught me to be more cautious and mindful when working with others.`: 1 (0.2%)
- `I was on academic probation as a undergraduate student at the University of California, Berkeley.`: 1 (0.2%)

**Prev_Matric_Ind** (Top 10 values):
- `No`: 610 (99.5%)
- `Yes`: 3 (0.5%)

**Prev_Matric_Sschool** (Top 10 values):
- `The University of Texas Health Science Center at San Antonio Joe R. and Teresa Lozano Long School of Medicine`: 1 (0.2%)

**Prev_Matric_Year** (Top 10 values):
- `0.0`: 3 (0.5%)
- `2019.0`: 1 (0.2%)

**Prev_Matric_Desc** (Top 10 values):
- `The University of Texas Health Science Center at San Antonio Joe R. and Teresa Lozano Long School of Medicine`: 1 (0.2%)

**Investigation_Ind** (Top 10 values):
- `No`: 613 (100.0%)

**Felony_Ind** (Top 10 values):
- `No`: 613 (100.0%)

**Misdemeanor_Ind** (Top 10 values):
- `No`: 610 (99.5%)
- `Yes`: 3 (0.5%)

**Misdemeanor_Desc** (Top 10 values):
- `As a student, I was convicted of a DUI misdemeanor first offense on January 31, 2020, in Williamsburg, VA. After, I completed an alcohol safety program. This period in my life was the most pivotal and tumultuous. Sink or swim, I continuously told myself. This decision endangered me and those around me. I felt lost and ashamed. My passion for medicine became my lifeline. I used this as a springboard rather than an anchor. I pushed forward: focusing on my school work and finding ways to get involved with populations that felt misunderstood and lost, as I once had. The National Crisis Textline and Prevention Point helped me channel these feelings into tangible impact. At the Prevention point, I understood each patient’s plight: helplessness towards certain choices made in life. It was cathartic to take responsibility for my past decision and support patients who may feel similarly. At the Crisis Textline, I could relay my strategies and create bonds with several brave people who called in with unique stories. Four years removed from this phase of my life, I am ready to embark on this journey. I understand that every day I must prove that I am a sum of more than my past mistakes. I am excited about the challenge of continually proving myself and improving my society through healthcare.`: 1 (0.2%)
- `On June 13, 2022, I received a speeding ticket in Gwinnett County, Georgia on my way home from class. I plead guilty, paid the required fine, and attended mandated driver education courses. I am currently an active driver in the state of Georgia and the United States, and I implement the material I learned during the courses into my day-to-day driving.`: 1 (0.2%)
- `I have had one speeding ticket the 31st of December of 2021. I was required to pay a fine.`: 1 (0.2%)

**Military_Discharge_Ind** (Top 10 values):
- `No`: 613 (100.0%)

**Military_HON_Discharge_Ind** (Top 10 values):
- `0`: 611 (99.7%)
- `1`: 2 (0.3%)

**Comm_Service_Ind** (Top 10 values):
- `Yes`: 608 (99.2%)
- `No`: 5 (0.8%)

**HealthCare_Ind** (Top 10 values):
- `Yes`: 613 (100.0%)

**Military_Service** (Top 10 values):
- `No`: 608 (99.2%)
- `Yes`: 5 (0.8%)

**Military_Service_Status** (Top 10 values):
- `Active Duty`: 2 (0.3%)
- `Veteran`: 2 (0.3%)
- `US Reserves or National Guard`: 1 (0.2%)

**Pell_Grant** (Top 10 values):
- `No`: 430 (70.1%)
- `Yes`: 168 (27.4%)
- `Don't Know`: 8 (1.3%)
- `Decline to Answer`: 7 (1.1%)

**Fee_Assistance_Program** (Top 10 values):
- `No`: 468 (76.3%)
- `Yes`: 136 (22.2%)
- `Y - Invalid for Application Submission information`: 9 (1.5%)

**Childhood_Med_Underserved_Self_Reported** (Top 10 values):
- `No`: 405 (66.1%)
- `Yes`: 154 (25.1%)
- `Don't Know`: 49 (8.0%)
- `Decline to Answer`: 5 (0.8%)

**Family_Income_Level** (Top 10 values):
- `$100,000 - 124,999`: 75 (12.2%)
- `$50,000 - 74,999`: 73 (11.9%)
- `$75,000 - 99,999`: 73 (11.9%)
- `$25,000 - 49,999`: 71 (11.6%)
- `Less than $25,000`: 47 (7.7%)
- `Do not know`: 45 (7.3%)
- `$150,000 - 174,999`: 38 (6.2%)
- `$400,000 or more`: 37 (6.0%)
- `$125,000 - 149,999`: 37 (6.0%)
- `$200,000 - 224,999`: 23 (3.8%)

**Number_in_Household** (Top 10 values):
- `4`: 250 (40.8%)
- `5`: 158 (25.8%)
- `6`: 65 (10.6%)
- `3`: 64 (10.4%)
- `7`: 29 (4.7%)
- `2`: 19 (3.1%)
- `10`: 8 (1.3%)
- `8`: 8 (1.3%)
- `9`: 6 (1.0%)
- `11`: 2 (0.3%)

**Family_Assistance_Program** (Top 10 values):
- `No`: 398 (64.9%)
- `Yes`: 215 (35.1%)

**Paid_Employment_BF_18** (Top 10 values):
- `Yes`: 384 (62.6%)
- `No`: 229 (37.4%)

**Contribution_to_Family** (Top 10 values):
- `No`: 533 (86.9%)
- `Yes`: 80 (13.1%)

**Other_Loan_Percentage** (Top 10 values):
- `0.0`: 528 (86.1%)
- `25.0`: 2 (0.3%)
- `5.0`: 2 (0.3%)
- `35.0`: 2 (0.3%)
- `50.0`: 2 (0.3%)
- `39.0`: 1 (0.2%)
- `42.0`: 1 (0.2%)
- `10.0`: 1 (0.2%)
- `36.0`: 1 (0.2%)
- `5.7`: 1 (0.2%)

**Applicant_Contribution_Percentage** (Top 10 values):
- `0.0`: 331 (54.0%)
- `10.0`: 45 (7.3%)
- `5.0`: 40 (6.5%)
- `20.0`: 16 (2.6%)
- `15.0`: 13 (2.1%)
- `30.0`: 13 (2.1%)
- `25.0`: 10 (1.6%)
- `2.0`: 8 (1.3%)
- `1.0`: 8 (1.3%)
- `4.0`: 8 (1.3%)

**Other_Percentage** (Top 10 values):
- `0.0`: 519 (84.7%)
- `5.0`: 4 (0.7%)
- `20.0`: 4 (0.7%)
- `10.0`: 3 (0.5%)
- `50.0`: 3 (0.5%)
- `7.0`: 2 (0.3%)
- `25.0`: 2 (0.3%)
- `100.0`: 1 (0.2%)
- `8.0`: 1 (0.2%)
- `27.0`: 1 (0.2%)

**Application_Review_Score** (Top 10 values):
- `0`: 94 (15.3%)
- `21`: 90 (14.7%)
- `19`: 70 (11.4%)
- `22`: 47 (7.7%)
- `15`: 39 (6.4%)
- `24`: 38 (6.2%)
- `20`: 31 (5.1%)
- `18`: 27 (4.4%)
- `12`: 27 (4.4%)
- `13`: 23 (3.8%)

**Service_Rating_Categorical** (Top 10 values):
- `Significant`: 282 (46.0%)
- `Adequate`: 125 (20.4%)
- `Lacking/Does Not Meet`: 107 (17.5%)
- `Exceptional`: 99 (16.2%)

**Service_Rating_Numerical** (Top 10 values):
- `3`: 282 (46.0%)
- `2`: 125 (20.4%)
- `1`: 107 (17.5%)
- `4`: 99 (16.2%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| Appl_Year | 613 | 2024.00 | 0.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 |
| Amcas_ID | 613 | 15463699.57 | 409149.24 | 13149516.00 | 15280062.00 | 15519360.00 | 15750866.00 | 16091417.00 |
| Age | 613 | 24.30 | 2.53 | 20.00 | 23.00 | 24.00 | 25.00 | 41.00 |
| Hrdshp_Comments | 0 | nan | nan | nan | nan | nan | nan | nan |
| Num_Dependents | 613 | 0.03 | 0.21 | 0.00 | 0.00 | 0.00 | 0.00 | 2.00 |
| Prev_Matric_Year | 4 | 504.75 | 1009.50 | 0.00 | 0.00 | 0.00 | 504.75 | 2019.00 |
| Felony_Desc | 0 | nan | nan | nan | nan | nan | nan | nan |
| Military_HON_Discharge_Ind | 613 | 0.00 | 0.06 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| Military_Discharge_Desc | 0 | nan | nan | nan | nan | nan | nan | nan |
| Exp_Hour_Total | 613 | 9206.54 | 13587.12 | 748.00 | 4300.00 | 6545.00 | 9770.00 | 208872.00 |
| Exp_Hour_Research | 563 | 1106.30 | 1541.29 | 0.00 | 350.00 | 670.00 | 1222.50 | 18400.00 |
| Exp_Hour_Volunteer_Med | 546 | 597.93 | 894.73 | 0.00 | 182.50 | 400.00 | 650.00 | 11370.00 |
| Exp_Hour_Volunteer_Non_Med | 550 | 938.83 | 4475.30 | 0.00 | 200.00 | 403.50 | 742.50 | 100419.00 |
| Exp_Hour_Employ_Med | 515 | 2058.61 | 2357.90 | 0.00 | 594.00 | 1376.00 | 2679.00 | 16810.00 |
| Exp_Hour_Shadowing | 529 | 149.59 | 177.73 | 0.00 | 52.00 | 100.00 | 166.00 | 1570.00 |
| Comm_Service_Total_Hours | 613 | 1374.93 | 4351.50 | 0.00 | 512.00 | 738.00 | 1283.00 | 101895.00 |
| HealthCare_Total_Hours | 613 | 2391.17 | 2521.21 | 45.00 | 905.00 | 1635.00 | 2942.00 | 17560.00 |
| Number_in_Household | 613 | 4.71 | 1.62 | 2.00 | 4.00 | 4.00 | 5.00 | 17.00 |
| Academic_Scholarship_Percentage | 545 | 24.57 | 31.39 | 0.00 | 0.00 | 7.00 | 50.00 | 100.00 |
| Finacial_Need_Based_Percentage | 545 | 18.65 | 28.31 | 0.00 | 0.00 | 0.00 | 30.00 | 100.00 |
| Student_Loan_Percentage | 545 | 9.84 | 18.81 | 0.00 | 0.00 | 0.00 | 12.50 | 99.50 |
| Other_Loan_Percentage | 545 | 1.04 | 7.17 | 0.00 | 0.00 | 0.00 | 0.00 | 100.00 |
| Family_Contribution_Percentage | 545 | 38.65 | 38.38 | 0.00 | 0.00 | 25.00 | 75.00 | 100.00 |
| Applicant_Contribution_Percentage | 545 | 6.13 | 12.46 | 0.00 | 0.00 | 0.00 | 7.00 | 90.00 |
| Other_Percentage | 545 | 1.12 | 7.12 | 0.00 | 0.00 | 0.00 | 0.00 | 100.00 |
| Application_Review_Score | 613 | 15.30 | 7.82 | 0.00 | 12.00 | 19.00 | 21.00 | 25.00 |
| Service_Rating_Numerical | 613 | 2.61 | 0.95 | 1.00 | 2.00 | 3.00 | 3.00 | 4.00 |

### Schema Consistency Across Years

| Column | 2022 | 2023 | 2024 | Notes |
|--------|------|------|------|-------|
| AMCAS ID | ✓ | ✗ | ✗ |  |
| Academic_Scholarship_Percentage | ✓ | ✓ | ✓ |  |
| Age | ✓ | ✓ | ✓ |  |
| Amcas_ID | ✓ | ✓ | ✓ |  |
| Appl_Year | ✓ | ✓ | ✓ |  |
| Applicant_Contribution_Percentage | ✓ | ✓ | ✓ |  |
| Application Review Score | ✓ | ✓ | ✗ | Removed in 2024 |
| Application_Review_Score | ✗ | ✗ | ✓ |  |
| BCPM_GPA_Trend | ✓ | ✗ | ✗ |  |
| Childhood_Med_Underserved_Self_Reported | ✓ | ✓ | ✓ |  |
| Citizenship | ✓ | ✓ | ✓ |  |
| Comm_Service_Ind | ✓ | ✓ | ✓ |  |
| Comm_Service_Total_Hours | ✓ | ✓ | ✓ |  |
| Contribution_to_Family | ✓ | ✓ | ✓ |  |
| Disadvantanged_Ind | ✓ | ✓ | ✓ |  |
| Eo_Level | ✓ | ✓ | ✓ |  |
| Exp_Hour_Employ_Med | ✓ | ✓ | ✓ |  |
| Exp_Hour_Research | ✓ | ✓ | ✓ |  |
| Exp_Hour_Shadowing | ✓ | ✓ | ✓ |  |
| Exp_Hour_Total | ✓ | ✓ | ✓ |  |
| Exp_Hour_Volunteer_Med | ✓ | ✓ | ✓ |  |
| Exp_Hour_Volunteer_Non_Med | ✓ | ✓ | ✓ |  |
| Family_Assistance_Program | ✓ | ✓ | ✓ |  |
| Family_Contribution_Percentage | ✓ | ✓ | ✓ |  |
| Family_Income_Level | ✓ | ✓ | ✓ |  |
| Fee_Assistance_Program | ✓ | ✓ | ✓ |  |
| Felony_Desc | ✓ | ✓ | ✓ |  |
| Felony_Ind | ✓ | ✓ | ✓ |  |
| Finacial_Need_Based_Percentage | ✓ | ✓ | ✓ |  |
| First_Generation_Ind | ✓ | ✓ | ✓ |  |
| Gender | ✓ | ✓ | ✓ |  |
| HealthCare_Ind | ✓ | ✓ | ✓ |  |
| HealthCare_Total_Hours | ✓ | ✓ | ✓ |  |
| Highest_Test_Date_2015 | ✓ | ✓ | ✓ |  |
| Hrdshp_Comments | ✓ | ✓ | ✓ |  |
| Inst_Action_Desc | ✓ | ✓ | ✓ |  |
| Inst_Action_Ind | ✓ | ✓ | ✓ |  |
| Investigation_Ind | ✓ | ✓ | ✓ |  |
| Major_Long_Desc | ✓ | ✓ | ✓ |  |
| Military_Discharge_Desc | ✓ | ✓ | ✓ |  |
| Military_Discharge_Ind | ✓ | ✓ | ✓ |  |
| Military_HON_Discharge_Ind | ✓ | ✓ | ✓ |  |
| Military_Service | ✓ | ✓ | ✓ |  |
| Military_Service_Status | ✓ | ✓ | ✓ |  |
| Misdemeanor_Desc | ✓ | ✓ | ✓ |  |
| Misdemeanor_Ind | ✓ | ✓ | ✓ |  |
| Num_Dependents | ✓ | ✓ | ✓ |  |
| Number_in_Household | ✓ | ✓ | ✓ |  |
| Other_Loan_Percentage | ✓ | ✓ | ✓ |  |
| Other_Percentage | ✓ | ✓ | ✓ |  |
| Paid_Employment_BF_18 | ✓ | ✓ | ✓ |  |
| Pell_Grant | ✓ | ✓ | ✓ |  |
| Prev_Applied_Rush | ✓ | ✓ | ✓ |  |
| Prev_Matric_Desc | ✓ | ✓ | ✓ |  |
| Prev_Matric_Ind | ✓ | ✓ | ✓ |  |
| Prev_Matric_Sschool | ✓ | ✓ | ✓ |  |
| Prev_Matric_Year | ✓ | ✓ | ✓ |  |
| RU_Ind | ✓ | ✓ | ✓ |  |
| SES_Value | ✓ | ✓ | ✓ |  |
| Service Rating (Categorical) | ✓ | ✓ | ✗ | Removed in 2024 |
| Service Rating (Numerical) | ✓ | ✓ | ✗ | Removed in 2024 |
| Service_Rating_Categorical | ✗ | ✗ | ✓ |  |
| Service_Rating_Numerical | ✗ | ✗ | ✓ |  |
| Student_Loan_Percentage | ✓ | ✓ | ✓ |  |
| Total_GPA_Trend | ✓ | ✗ | ✗ |  |
| Under_School | ✓ | ✓ | ✓ |  |

================================================================================
## FILE: 10. Secondary Application.xlsx
================================================================================

### Year-over-Year Overview

| Year | Rows | Columns | Status |
|------|------|---------|--------|
| 2022 | 437 | 51 | ✓ OK |
| 2023 | 401 | 51 | ✓ OK |
| 2024 | 613 | 51 | ✓ OK |

### 2022 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| application_id | int64 | 437 | 0.0% |
| App Year | int64 | 1 | 0.0% |
| AMCAS ID | int64 | 437 | 0.0% |
| Last Name | object | 394 | 0.0% |
| First Name | object | 357 | 0.0% |
| Middle Name | object | 227 | 37.1% |
| 1 - Personal Attributes / Life Experiences | object | 437 | 0.0% |
| 2 - Challenging Situation | object | 437 | 0.0% |
| 3 - Reflect Experience | object | 437 | 0.0% |
| 4 - Hope to Gain | object | 437 | 0.0% |
| 5 - Employed Undergrad | object | 2 | 0.0% |
| 5 - Employment Hours | object | 3 | 18.3% |
| 5 - Employment Duration | object | 4 | 18.3% |
| 6 - Direct Care Experience | object | 1 | 0.0% |
| 6 - Experiences | object | 436 | 0.2% |
| 6 - Addtl Info | float64 | 0 | 100.0% |
| 7 - COVID Impact | object | 412 | 5.7% |
| 8 - Institutional Action / Crime | object | 2 | 0.0% |
| 8 - Details | object | 15 | 96.6% |
| 3 - Research | object | 1 | 0.0% |
| 3 - # Summers | float64 | 0 | 100.0% |
| 3 - # Semesters | float64 | 0 | 100.0% |
| 3 - # Years | float64 | 0 | 100.0% |
| 3 - Abstract(s) | float64 | 0 | 100.0% |
| 3 - Conference Presentation(s) | float64 | 0 | 100.0% |
| 3 - Poster Presentation(s) | float64 | 0 | 100.0% |
| 3 - Publication(s) | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Employer 1 | float64 | 0 | 100.0% |
| 4 - Employer 1 Direct Patient | float64 | 0 | 100.0% |
| 4 - Employer 1 Duration | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Employer 2 | float64 | 0 | 100.0% |
| 4 - Employer 2 Direct Patient | float64 | 0 | 100.0% |
| 4 - Employer 2 Duration | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Employer 3 | float64 | 0 | 100.0% |
| 4 - Employer 3 Direct Patient | float64 | 0 | 100.0% |
| 4 - Employer 3 Duration | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Volunteer 1 | float64 | 0 | 100.0% |
| 4 - Volunteer 1 Direct Patient | float64 | 0 | 100.0% |
| 4 - Volunteer 1 Duration | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Volunteer 2 | float64 | 0 | 100.0% |
| 4 - Volunteer 2 Direct Patient | float64 | 0 | 100.0% |
| 4 - Volunteer 2 Duration | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Volunteer 3 | float64 | 0 | 100.0% |
| 4 - Volunteer 3 Direct Patient | float64 | 0 | 100.0% |
| 4 - Volunteer 3 Duration | float64 | 0 | 100.0% |
| LOR - Offer Committee Letter | object | 2 | 0.0% |
| LOR - Letter Types Submitting | object | 3 | 0.0% |
| LOR - Not Submitting Committee Letter Reason | object | 21 | 95.2% |
| LOR - Which Three Letters | object | 196 | 55.1% |
| Citizenship - Signature | object | 437 | 0.0% |
| Citizenship - Signature Date | int64 | 102 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  application_id: 84183
  App Year: 2022
  AMCAS ID: 14570549
  Last Name: Shindler
  First Name: Isabella
  Middle Name: Perlis
  1 - Personal Attributes / Life Experiences: I began tutoring adults at Literacy Chicago when I was in 7th grade. I‚Äôm now entering my 12th year as a volunteer. I‚Äôve developed life long relationships with adults I may have never gotten the opportunity to meet had it not been for literacy. Regardless of age or where they are from, besides helping them become better readers, all anyone ever wants is for me to be present while we‚Äôre together. I‚Äôve traveled around the country speaking to other kids at churches and schools about volunteering. When they ask me what is the most important thing to being a good tutor, the answer is always the same. For that one hour, make that person feel like they matter. Whether it‚Äôs tutoring someone to read, teaching an exercise class to females at Cook County Jail, working as a medical scribe or someday being a physician myself, as a result of this capability, I believe I will always be able to understand my patients from any culture or background.
  2 - Challenging Situation: While I was working as a medical scribe, a 14 year old female came in for a checkup. It turns out she had an STD. Since she was over the age of 12, she had the right to ask her mom to leave the room. When the provider started to question her about her sexual activity, she broke down crying. I‚Äôve never seen such a look of shame on someone‚Äôs face. After several minutes, she finally told the provider that she was dating a girl. She was embarrassed and scared and barely audible. She needed a voice. She needed her mom. I knew I would have had I been in a similar situation. Although I disagreed with it, I realized the rule was in place for a reason and respected the doctor‚Äôs decision to ask the mom to wait outside. Emotions and compassion are important‚Äî however nothing overrides a patient‚Äôs rights. Over these past few years, I‚Äôve developed talents, traits and skill sets which I now know will make me capable of resolving challenging situations I personally will face as a practicing physician.
  3 - Reflect Experience: Being rejected from Rush Medical School is undoubtedly an experience I gained more from than was expected. Initially, what appeared to be a life altering negative detour turned into a life altering positive event. I was given the gift that many never get. Time. Time to breathe, time to stop all the rushing, time for self discovery, time to become better. I‚Äôm proud of what I have accomplished and who I have become over these last few years. Someday, I‚Äôll be able to tell my daughter or my son how they are never, ever allowed to give up on a dream. And they won‚Äôt just be encouraging words from their loving mom. They‚Äôll be the truths of her story.
  4 - Hope to Gain: One of the things most impressive about Rush is their dedication to pro bono service. As a future student of the school, I‚Äôm planning to create a panel consisting of both volunteer medical students and volunteer law students where people can come together at a meeting site and get free consultations concerning both their medical and legal questions. I hope to someway incorporate my connection with Literacy Chicago and Rush Medical School to thread the two together. Because of Rush‚Äôs belief in serving its community in more ways than just medical care, I believe my experiences there will allow me to leave with more than just my medical degree and serve in more ways than just a physician.
Row 2:
  application_id: 84185
  App Year: 2022
  AMCAS ID: 15281761
  Last Name: Adil
  First Name: Anam
  Middle Name: B
  1 - Personal Attributes / Life Experiences: While growing up involved in service activities at the mosque, my Islamic teachers emphasized that the strength of my spirituality is expressed by my relations with others. Respect is a birthright and must be given regardless of one's community. As a woman wearing a headscarf, a visual representation of being culturally different, this respect was not always reciprocated. While it was disheartening, it strengthened my desire to understand and appreciate others' values. I built upon this in instances such as conducting wellness checks for the elderly at IMAN and even working at a jewelry store. Outside of routine conversations, we digressed on childhood, history, and religion. By displaying full attentiveness, I found we all have traditions and principles we cherish. I understood our shared connection of giving importance to preserving them, but also the necessity to adapt for our growth. I will carry this concentration and awareness with me as a physician to build patient trust.
  2 - Challenging Situation: At the start of the pandemic, I read how college students made face shields for local hospitals. Since my university had the tools and design institute to work on a similar project, I contacted the director to help me. Despite our best efforts, we faced resistance because the school did not want to open facilities to anyone off-campus since students were still residing in dorms. I understood their concern but disagreed with their alternative proposal where volunteers picked up cloth for masks that must be sanitized, sown, and shipped back. I believed this protocol seemed less efficient. I navigated this response by receiving advice from faculty and peers, who helped me fulfill my plan in a safe and ordered manner. I sourced local vendors who gave us materials at cost price, organized community volunteers, and socially distant spaces to produce 1000 shields. I learned that one could find alternate avenues to achieve their goals through guidance and communication.
  3 - Reflect Experience: As a peer-aid for a group that assists special-needs-based individuals, I helped a five-year-old with Down syndrome do school work and play games. I assumed this would mimic my previous responsibilities as a tutor, but it was quite different. From this experience, I realized that how we respond and interact varies based on one's needs. I learned to react to changes in mood and social behaviors with careful sensitiveness. It also developed my intuition as I understood his wants without him telling me explicitly. I needed to recognize all factors to explain what may be affecting his learning. When we transferred to a virtual platform, it was not easy keeping him engaged. This inspired me to co-create "StoryTown," a channel that features children's read-alouds and physical activities. It reinforced the impact I can have in one's life by using the resources and opportunities available. This experience fostered my growth as it worked upon the qualities of an understanding individual.
  4 - Hope to Gain: In my research and education on Chicago neighborhoods, I was dismayed when I learned that a twenty-minute difference between two neighborhoods in Chicago would have a near twenty-year life expectancy gap. Structural violence and inequity themselves are a cause of high rates of common diseases and death. Because Rush was the first medical college in Chicago, it understands how one's location correlates with health and the advantages of better-resourced hospitals for patients. This is why I hope to gain a comprehensive education at Rush that, along with excellent academia and research opportunity, also teaches how to deliver great care to underserved settings in a manner that is consistent and not constrained by a lack of resources. Rush‚Äôs balance between education and commitment to serve the surrounding communities to mitigate these disparities is how I hope to learn the ways in which I can contribute to working towards health equity as a future physician.
Row 3:
  application_id: 84186
  App Year: 2022
  AMCAS ID: 14869074
  Last Name: Thompson
  First Name: Michael
  Middle Name: Robert
  1 - Personal Attributes / Life Experiences: ‚ÄúI don‚Äôt trust doctors.‚Äù I heard this countless times in my volunteer and clinical work with the homeless, in particular._x000D_
_x000D_
One day while handing out burritos to the homeless with Share a Meal, a very hostile man ran up yelling angrily. Being marginalized by society, I understood why he felt slighted, that we had purposely skipped him. Before explaining that it was an accident, I listened. When I offered him two burritos to make amends, he apologized. It was impactful for me: I learned how listening not only diffuses situations, it builds trust. _x000D_
_x000D_
Through volunteering in Los Angeles, Mexico, and Salt Lake City, I learned the value of listening. Engaging with diverse communities opened new opportunities to learn. I developed more empathy and an understanding that their experiences differed dramatically from mine. It wasn‚Äôt an easy process, as I grew up in a homogenous Mormon community. It added depth and meaning to what I‚Äôll contribute to society as an individual and as a physician.
  2 - Challenging Situation: One of my favorite parts of the All of Us Research program at the Keck Hospital of USC was working with nurses and physicians. Initially, I recruited for the study in Internal Medicine. After nurses took patient vitals, I entered patient rooms to pitch the study as quickly and effectively as possible. I left the room before the physician entered. The system worked._x000D_
_x000D_
Then the program hired a new coordinator. I showed her my routine and taught her how to be an effective recruiter. Within a week, with little experience, she wanted to change the system entirely, that is, wait in the waiting room for an online notification. This meant a delay in interactions. We‚Äôd have less time with the patient and more chance of interrupting the physician. But she was adamant and the other research coordinator didn‚Äôt want to speak up. While frustrated, I had to accept the new system. At the end of the day, no one was hurt by the new recruiting strategy, and I still recruited to the best of my ability._x000D_

  3 - Reflect Experience: When I thought life couldn‚Äôt get worse, it did. The person I cared most about, my girlfriend, left me weeks before my MCAT. She was part of my identity, inspiring me to be more self-confident. It felt like all that work was wiped clean in one horrible conversation. When she lost faith in me, I stopped believing, too. I tried opening up to my mom, but she has stage 4 cancer, was worried about her father‚Äôs cancer, and was drained by cancer meds. My friends told me to ‚Äúget over it.‚Äù I felt like a burden._x000D_
_x000D_
So, I focused on what I could control: healthy exercise habits and getting A‚Äôs at Cal State Fullerton. I met a girl also struggling emotionally and I felt happy to help her. I had lost the satisfaction I get when I help others and it was restored. I started driving to LA every weekend to volunteer and carpooled with physicians to our clinic in Mexico._x000D_
_x000D_
I had been devastated emotionally and I turned it around to gain a stronger sense of self and a revitalized focus on my medical goals.
  4 - Hope to Gain: The Rush Medical College on the West side of Chicago gives me an opportunity to learn about and serve diverse and underprivileged populations. I worked with the homeless in Los Angeles and through those experiences, I learned the importance of community outreach. I‚Äôd like to apply that knowledge and continue my education in another large urban setting like Chicago._x000D_
_x000D_
I expect to build strong clinical skills at RMC through early clinical experience, especially with the proximity of Rush University Medical Center, and the John H. Stroger, Jr. Hospital of Cook County. I‚Äôm also interested in the RMC Department of Pediatrics, based on my work with children at the Primary Children‚Äôs hospital in Salt Lake City. I love helping kids, and would like to be part of RMC‚Äôs Heal the Children program. _x000D_
_x000D_
With RMC‚Äôs close ties to the community, many research opportunities, and early opportunities for clinical experience ‚Äì I think there‚Äôs a lot I can contribute and learn._x000D_

```

#### Categorical Column Distributions

**App Year** (Top 10 values):
- `2022`: 437 (100.0%)

**5 - Employed Undergrad** (Top 10 values):
- `Yes`: 357 (81.7%)
- `No`: 80 (18.3%)

**5 - Employment Hours** (Top 10 values):
- `Part-time (less than 20 hours)`: 187 (42.8%)
- `Part-time (20 hours or more)`: 153 (35.0%)
- `Full-time`: 17 (3.9%)

**5 - Employment Duration** (Top 10 values):
- `More than 3 Academic Years`: 183 (41.9%)
- `2 Academic Years`: 84 (19.2%)
- `1 Academic Year`: 56 (12.8%)
- `Less Than 1 Academic Year`: 34 (7.8%)

**6 - Direct Care Experience** (Top 10 values):
- `Yes`: 437 (100.0%)

**8 - Institutional Action / Crime** (Top 10 values):
- `No`: 422 (96.6%)
- `Yes`: 15 (3.4%)

**8 - Details** (Top 10 values):
- `On July 9, 2014, after our first year of college, a small group of my high school friends gathered at one of their homes in Barrington, IL to celebrate and catch up. Unfortunately, we made the poor decision to consume alcohol at this celebration. When my friend‚Äôs next door neighbor realized this, they notified the police. When officers arrived, several of my friends ran from the scene, but I knew that this was unacceptable. Those of us who had stayed when the officers arrived cooperated fully and I was charged with the consumption of alcohol by a minor._x000D_
_x000D_
During the administrative adjudication hearing, I pleaded guilty to this charge and received a local ordinance violation, instructing me to pay a $250 fine and complete 24 hours of community service. I paid the fine immediately and finished my community service requirements shortly thereafter. This offense has been officially expunged from my permanent record, but, in the spirit of transparency, I wanted to be completely forthcoming.`: 1 (0.2%)
- `During my freshmen year of college, I paraphrased online information without citing for an extra credit assignment. Instead of reading the book to complete the short answer assignment, I answered the questions using information found online. This was an act of plagiarism born out of a desire to take shortcuts. I was deducted half a letter grade from my final grade in the class. I recognize the severity of my action and grateful for this opportunity to learn from it. I learned that plagiarism robs from the original writer and is a terrible offense. I also learned that it is better to take the long road rather than shortcuts because it is beneficial to my own learning experience. I am proud to say that I have not since repeated this mistake.`: 1 (0.2%)
- `In October of 2017, I had used a textbook from a previous semester (instead of my current semester) from a roommate to complete an open-note assignment for General Biology Laboratory. I had lost my copy and wrongly assumed prior copies could be utilized. I later learned that prior copies are prohibited material. I was charged with a violation of Academic Integrity and received no credit for the work, but was able to complete the course with a B+. I understand and agree that such rules need to be in place to protect the integrity of institutions and their students. I should have been more careful and thorough in understanding my class‚Äôs policies. _x000D_
_x000D_
I knew moving forward from this incident that I needed to be more intentional with my actions. I have since worked hard to maintain a strong academic and extracurricular record. I am presently extremely cautious of the decisions I make, the actions I take, and the consequences they may have on myself and those around me.`: 1 (0.2%)
- `_x000D_
I was put on disciplinary probation for one year in August of 2018. The night before my 21st birthday, I was surprised by a birthday party. At midnight, my friends took me outside of my townhouse so they could sing happy birthday to me and give me a present. However, even though it was a Saturday night, people in our complex had work and responsibilities the following morning. Because of that, the police gave me a noise complaint. I was called by the University for violating the students‚Äô Code of Conduct for hosting a "loud party" at my off-campus residency. None of that reflects on my transcript nor did it interrupt my academics. After the incident, I apologized to my neighbors, and ever since then, I have had better communication with people from my neighborhood. This experience made me understand that you have to be more conscious about people around you and be aware that they have responsibilities that do not deserve to be disturbed by external factors`: 1 (0.2%)
- `When I was 21 years old, I pleaded no contest to a fare evasion charge. I was in Fairfax, Virginia, and I was short on cash. I made a brash decision to try to pass through the gate. I was caught by an officer. I was given a court date. I pleaded no contest and was automatically found guilty. I had to pay a fine and was given a misdemeanor._x000D_
I regret making this decision. I should have exhausted potential resources and considered any long term consequences to these actions. Although I cannot undo what is done, I have not had any arrests, charges, or convictions since then. I strive to be an honest and hardworking citizen, and have advised my younger cousins who look up to me about the potential risks and consequences of similar actions. I realize now the value in humility and asking for help before making such choices. _x000D_
`: 1 (0.2%)
- `I was sentenced under the First Offender Act in 2015 for Possession of Marijuana (Under 1oz). I successfully completed my probation and all records of the arrest and charges have been removed from my official criminal history maintained by the GCIC. The First Offender is Georgia‚Äôs ‚Äúsecond chance‚Äù law. People who have never been convicted of a felony can be sentenced under the First Offender Act. If the person successfully completes the sentence, they will not have the burden of a conviction as they move on with their life. I was sentenced as a first offender and successfully completed my probation. The record of the arrest and sentence are sealed from my official criminal history record. _x000D_
I do deeply regret the choice I made as an 18-year-old and did not realize the impact of my decisions on my future at that time. Regardless, I have worked hard on moving forward with my life in a positive manner and continue to learn from past experience.`: 1 (0.2%)
- `Nearly seven years ago, I made a decision that put my entire reputation on the line. It was my second semester as a Freshman at Emory University, and I decided to look at another student's test during a chemistry exam. After being confronted by the professor, I admitted to having done so and was given an F in the course._x000D_
_x000D_
This is a mistake that I carry with me to this day. It is a constant reminder of the importance of integrity and how one uncharacteristic decision can truly change your life. Had I been able to see past the sheer panic I felt in that moment as I faced potential failure, I might have realized the widespread damage that my actions could have caused. The consequences for me were, justifiably, severe, and that does not even account for the transgressions against my fellow students and professors that my decision entailed. This situation also reiterated my need to confront my family situation that was contributing to my academic and personal struggles. `: 1 (0.2%)
- `My Freshman year in General Chemistry was the first time I had ever stepped foot in a chemical laboratory, which came with as many feelings of excitement as did the numerous challenges that arise for an inexperienced chemist like myself. In this novel academic environment, I felt the need to work closely with another student by performing our data calculations and interpretations on a shared file. This decision resulted in receiving an email from the Student Affairs Office for violating Code 11.14.B - Unauthorized collaboration on a project, homework or other assignment. Having submitted work that was identical, I was flagged for plagiarism and received grade deductions on six lab reports. As a first-generation Latino college student, I needed additional academic support and should have sought help from my professors. Unfortunately, my naivete got the best of me, and over the past seven years I‚Äôve worked on honing my intellectual independence to address my educational shortcomings.`: 1 (0.2%)
- `On 4/29/19, I received a violation for academic dishonesty in my PSYC 323 class. A classmate was copying me during an exam, and I failed to report him. I had a suspicion he was copying from me but decided to ignore the situation because I was unsure. Another person reported this student after class. My professor then sent out an email about a day or two later asking for others with more information on the incident to come forward. I emailed the professor, stating I had a feeling he had been copying me but didn't think much of it. My professor then scheduled a meeting with me and said she respected my honesty for coming forward. She said she did not want this to affect my future career but that I needed to face my consequences. My professor decided that I receive a zero 0 on the exam and lose my bonus points for the course. I was also required to take an online training course on academic dishonesty. Although I am not happy about the situation, I am glad I came out a better person._x000D_
`: 1 (0.2%)
- `I was cited for a minor in consumption May of 2017 in Breckenridge, MN. This is my only conviction and I was fined 225$ to which settled my debt to the state of Minnesota. There was no rehabilitation or community service required and there was no sentence imposed. While I realize that this was a mistake I learned my lesson and as a result I came out more mature and responsible.`: 1 (0.2%)

**3 - Research** (Top 10 values):
- `No Research`: 437 (100.0%)

**LOR - Offer Committee Letter** (Top 10 values):
- `No`: 260 (59.5%)
- `Yes`: 177 (40.5%)

**LOR - Letter Types Submitting** (Top 10 values):
- `Three Individual Letters`: 251 (57.4%)
- `Committee Letter`: 156 (35.7%)
- `Letter Packet`: 30 (6.9%)

**LOR - Not Submitting Committee Letter Reason** (Top 10 values):
- `Being a 2017 USC spring admit, I took courses at Valencia College (my local college) during the fall of 2016. Once I started at USC, the Biology I class I completed at Valencia College transferred in as Biology II, and since Biology I was only offered in the fall, I was unable to take any Biology at USC that semester. My USC advisor then encouraged me to take General Chemistry I during the summer of 2017 so I would not fall behind. Once I transferred to Georgetown in the fall of 2017, I was then told that the Biology I course I completed at Valencia would transfer in as such, rather than as Biology II as it had at USC. Given that Georgetown only offered Biology II & General Chemistry II in the spring, I was advised to begin my physics sequence during the fall of 2017. I later withdrew from physics. Seeing as I was a double major and was required to study abroad for the Spanish major, I was then encouraged to complete my prerequisite courses during the summers of 2018 & 2019 at Valencia College to finish my degree by my expected graduation date._x000D_
_x000D_
Since I transferred and completed science coursework at different universities, I did not have the required amount of science credit hours at Georgetown University for a committee letter. _x000D_
_x000D_
Valencia College does not provide committee letters. `: 1 (0.2%)
- `I decided that, given my academic performance, I would like to have the freedom and flexibility to choose the professors I most respect and trust to write recommendation letters for me. I prefer this freedom and flexibility to depending on an advisor or committee. `: 1 (0.2%)
- `My undergraduate institution does provide a committee letter, but I took most of my science classes at Charles R. Drew University (CDU) during my post-baccalaureate, so I did not get a letter from the institution. As for CDU, since I got my certificate in 2019, I was no longer eligible for the committee letter. `: 1 (0.2%)
- `I believe that given the amount of time that has passed since my undergraduate studies, it makes more sense for me to submit individual letters of recommendation. The people who were gracious enough to write letters for me have a detailed understanding of who I am as a person, student and young professional based on my experiences with them.`: 1 (0.2%)
- `I decided not to request a letter from my pre-professional advisor committee because I felt my other letters were strong and would be more representative of who I am as a person and as a student. Rutgers University is a huge university and I understood how difficult it would be for this office to write a strong, personalized letter on my behalf. Although I fulfilled all the requirements to receive one, I believe my application is as strong and complete without one. _x000D_
`: 1 (0.2%)
- `I chose not to utilize my school‚Äôs committee program for a number of reasons. The most pertinent reason being delays due to COVID-19 would put my letter at risk for late submission, therefore possibly delaying my secondary applications. Also, my school had strict restrictions on the number of letters and the route of their submission, which was another reason for me choosing to submit letters individually. As a non-traditional applicant, my situation was best handled by relying on individual submissions from my recommenders.`: 1 (0.2%)
- `I unfortunately missed the deadline to apply for a Committee letter. I had recently moved to a new city and started a new job and let the deadline slip my mind. It was a mistake on my part that I have learned from. `: 1 (0.2%)
- `I am not able to submit a Committee Letter. I was not able to get one, because of a miscommunication on my part regarding the deadline. I explained the situation to my advisor, who has drafted a letter of recommendation for me in lieu of a committee letter. `: 1 (0.2%)
- `My Undergraduate Pre-Professional Advisory Committee would not write letter packets for students who were not applying to medical school in their senior year of college. I knew I wanted to take some time between undergrad and medical school to pursue more work and life experience that would better prepare me for the medical path. For this reason, I was not qualified to pursue a committee letter packet.`: 1 (0.2%)
- `I graduated from my undergraduate institution more than ten years ago (May 2009). Therefore, I am submitting a Packet Letter from my graduate school institution, which does not offer a Committee Letter.`: 1 (0.2%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| application_id | 437 | 89257.97 | 2887.35 | 84183.00 | 86947.00 | 89182.00 | 91428.00 | 94820.00 |
| App Year | 437 | 2022.00 | 0.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 |
| AMCAS ID | 437 | 15011632.22 | 363254.26 | 12950085.00 | 14880945.00 | 15057778.00 | 15243303.00 | 15499135.00 |
| 6 - Addtl Info | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - # Summers | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - # Semesters | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - # Years | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - Abstract(s) | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - Conference Presentation(s) | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - Poster Presentation(s) | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - Publication(s) | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Employer 1 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 1 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 1 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Employer 2 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 2 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 2 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Employer 3 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 3 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 3 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Volunteer 1 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 1 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 1 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Volunteer 2 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 2 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 2 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Volunteer 3 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 3 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 3 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| Citizenship - Signature Date | 437 | 44399.95 | 424.87 | 35562.00 | 44397.00 | 44410.00 | 44436.00 | 44515.00 |

### 2023 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| application_id | int64 | 401 | 0.0% |
| App Year | int64 | 1 | 0.0% |
| AMCAS ID | int64 | 401 | 0.0% |
| Last Name | object | 374 | 0.0% |
| First Name | object | 316 | 0.0% |
| Middle Name | object | 243 | 29.9% |
| 1 - Personal Attributes / Life Experiences | object | 401 | 0.0% |
| 2 - Challenging Situation | object | 401 | 0.0% |
| 3 - Reflect Experience | float64 | 0 | 100.0% |
| 4 - Hope to Gain | float64 | 0 | 100.0% |
| 5 - Employed Undergrad | object | 2 | 0.0% |
| 5 - Employment Hours | object | 3 | 15.2% |
| 5 - Employment Duration | object | 4 | 15.2% |
| 6 - Direct Care Experience | object | 1 | 0.0% |
| 6 - Experiences | object | 399 | 0.5% |
| 6 - Addtl Info | float64 | 0 | 100.0% |
| 7 - COVID Impact | object | 367 | 8.5% |
| 8 - Institutional Action / Crime | object | 2 | 0.0% |
| 8 - Details | object | 7 | 98.2% |
| 3 - Research | object | 1 | 0.0% |
| 3 - # Summers | float64 | 0 | 100.0% |
| 3 - # Semesters | float64 | 0 | 100.0% |
| 3 - # Years | float64 | 0 | 100.0% |
| 3 - Abstract(s) | float64 | 0 | 100.0% |
| 3 - Conference Presentation(s) | float64 | 0 | 100.0% |
| 3 - Poster Presentation(s) | float64 | 0 | 100.0% |
| 3 - Publication(s) | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Employer 1 | float64 | 0 | 100.0% |
| 4 - Employer 1 Direct Patient | float64 | 0 | 100.0% |
| 4 - Employer 1 Duration | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Employer 2 | float64 | 0 | 100.0% |
| 4 - Employer 2 Direct Patient | float64 | 0 | 100.0% |
| 4 - Employer 2 Duration | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Employer 3 | float64 | 0 | 100.0% |
| 4 - Employer 3 Direct Patient | float64 | 0 | 100.0% |
| 4 - Employer 3 Duration | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Volunteer 1 | float64 | 0 | 100.0% |
| 4 - Volunteer 1 Direct Patient | float64 | 0 | 100.0% |
| 4 - Volunteer 1 Duration | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Volunteer 2 | float64 | 0 | 100.0% |
| 4 - Volunteer 2 Direct Patient | float64 | 0 | 100.0% |
| 4 - Volunteer 2 Duration | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Volunteer 3 | float64 | 0 | 100.0% |
| 4 - Volunteer 3 Direct Patient | float64 | 0 | 100.0% |
| 4 - Volunteer 3 Duration | float64 | 0 | 100.0% |
| LOR - Offer Committee Letter | object | 2 | 0.0% |
| LOR - Letter Types Submitting | object | 3 | 0.0% |
| LOR - Not Submitting Committee Letter Reason | object | 23 | 94.3% |
| LOR - Which Three Letters | object | 167 | 55.9% |
| Citizenship - Signature | object | 401 | 0.0% |
| Citizenship - Signature Date | int64 | 98 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  application_id: 97034
  App Year: 2023
  AMCAS ID: 14463063
  Last Name: Moats
  First Name: Michelle
  Middle Name: Anne
  1 - Personal Attributes / Life Experiences: While volunteering at Lotus House, a local women‚Äôs shelter in my community, I served people of diverse backgrounds different from my own, which allowed me to enhance my ability to understand those unlike myself. I taught and engaged with children and mothers from a wide variety of backgrounds, most notably African American and Hispanic. I connected and worked with all the children, and engaged with them in a loving, compassionate manner as I taught them the arts and crafts activity of the day. I also displayed patient and understanding if a tantrum, or the like, occurred. The children respected me and they worked well together despite their differences. I enjoyed seeing the children grow and mature week after week and became more comfortable teaching them the arts and crafts activity of the day. As time passed, I became more confident with working and engaging with the children of all backgrounds, and I plan to do the same in the future as a pediatric physician. 
  2 - Challenging Situation: While volunteering at West Kendall Baptist Hospital in Miami, FL, I noticed that there was a patient who did not have any visitors. On the weekend, I got flowers and went to visit with the older gentleman for a few minutes. He was very moved, and I was glad to have made a positive difference in someone‚Äôs life. On a larger scale, I had the opportunity to impact the community at Lotus House, a women‚Äôs shelter in my community of Miami, FL. Once a week, I taught the children the arts and crafts activity of the day. In the time that I had with the children I was satisfied that I was able to assist in giving them a nurturing, safe environment to learn and explore. Seeing the children run to me to greet me or smile and welcome me week after week was very rewarding. This experience helped to solidify my aspirations of pursuing pediatric medicine. I plan to implement the same compassionate manner at the bedside with my future patients.
  3 - Reflect Experience: nan
  4 - Hope to Gain: nan
Row 2:
  application_id: 97036
  App Year: 2023
  AMCAS ID: 14887989
  Last Name: Amador
  First Name: Ethan
  Middle Name: Alexander
  1 - Personal Attributes / Life Experiences: Most days, I take a virtual passport and practice Spanish with people from around the world through language exchange apps. Through this, I have made a friend named Sadaf. She is a student from Iran with aspirations to study abroad. She also happens to be proficient in Farsi, English, and Spanish. _x000D_
I had built this preconceived notion that Iran, and moreover, the Middle East, was the antithesis of western culture. News outlets and politicians would have you believe that our lifestyles are incompatible. But the reality is far from stereotypes or headlines. By getting to know Sadaf and her culture, I discovered that there is far more that unites us than divides us. I began to understand that people's differences stemmed from the environment they were brought up in. I learned that by focusing on our shared humanity, you can open a window into an entirely new culture. In a nation where we are taught to be fearful of strangers, I aspire to approach diversity with an open mind and arms.
  2 - Challenging Situation: Every week I volunteered at various elementary schools around the Fresno School District to help students with their math and reading. While my house was a brief 20 minutes away, the drive to South Fresno underscored a tale of two cities. From the windowless classrooms to the playground devoid of a playset, it was clear that these students faced an uphill battle. The pandemic left many students on an academic hiatus. This had drastic downstream effects on the students‚Äô academic and emotional development. I sought to address this issue by engaging with students in a way that left them excited to learn. Whether it was illustrating a passage or turning a few paragraphs into a time trial, I knew that developing their interest in learning would be vital. The payoff was at the end of the year when I was able to see the marked improvement in their standardized testing. But beyond improving their scores, I believe I was able to guide these students to be their own advocates for success.
  3 - Reflect Experience: nan
  4 - Hope to Gain: nan
Row 3:
  application_id: 97045
  App Year: 2023
  AMCAS ID: 14540408
  Last Name: Kumar
  First Name: Iksha
  Middle Name: nan
  1 - Personal Attributes / Life Experiences: I am a first-generation Indian-American-Canadian, who was born in San Francisco, spent her middle school years in Delhi, immigrated to Vancouver, BC at age 12, and now lives in Portland. Adapting to new cultures at a young age taught me the value of building connections with people of all backgrounds. As a new fourth-grade student in Delhi, I recall making friends by sharing my traditions like trick-or-treating on Halloween. In return, my classmates taught me Hindi at lunchtime as we scarfed down PBJs and paranthas. _x000D_
_x000D_
These early experiences cultivated a lifelong commitment to diversity and inclusion. In college, I hosted celebrations such as Pride and Eid, where students connected through shared experiences. Recently, my advocacy for the needs of BIPOC patients led to a collaboration with Dr. Tiffany Mayo to create resources on psoriasis symptoms in black patients. I hope to share my experiences with peers at RMC to promote inclusivity in our student body and patient population.
  2 - Challenging Situation: While working as a Clinical Trials Research Assistant, I met with "Alma," a Spanish-only speaking patient with severe vitiligo who was an excellent candidate for an active study. Unfortunately, since she required a translator to review the informed consent form, she could not enroll in the trial. When I approached my colleagues to request a translator, I was initially met with resistance as they shared that trial sponsors rarely agreed to pay for this service. Disappointed by this information, I urged Alma to return with an English-speaking caregiver. Fortunately, she did; and enrolled in the trial a few days later. However, most minority patients are not as lucky. _x000D_
 _x000D_
To prevent future discrimination against Spanish-speaking patients, I took on the responsibility of working with trial sponsors to ensure our clinic received Spanish translations of all informed consent forms. I also pioneered a relationship with a non-profit organization that offers free, on-demand, translation services.
  3 - Reflect Experience: nan
  4 - Hope to Gain: nan
```

#### Categorical Column Distributions

**App Year** (Top 10 values):
- `2023`: 401 (100.0%)

**5 - Employed Undergrad** (Top 10 values):
- `Yes`: 340 (84.8%)
- `No`: 61 (15.2%)

**5 - Employment Hours** (Top 10 values):
- `Part-time (less than 20 hours)`: 190 (47.4%)
- `Part-time (20 hours or more)`: 132 (32.9%)
- `Full-time`: 18 (4.5%)

**5 - Employment Duration** (Top 10 values):
- `More than 3 Academic Years`: 171 (42.6%)
- `2 Academic Years`: 92 (22.9%)
- `1 Academic Year`: 51 (12.7%)
- `Less Than 1 Academic Year`: 26 (6.5%)

**6 - Direct Care Experience** (Top 10 values):
- `Yes`: 401 (100.0%)

**8 - Institutional Action / Crime** (Top 10 values):
- `No`: 394 (98.3%)
- `Yes`: 7 (1.7%)

**8 - Details** (Top 10 values):
- `I look back and profoundly regret my stupid decisions surrounding alcohol during my early years at USD. Although there were three of them in a short while, I did not have a problem with alcohol, nor do I have one currently. I think that I didn't know the proper way to celebrate or hang out with friends. I have learned from my mistakes and now practice safe drinking habits. I am excited to continue my healthy relationship with alcohol using the lessons I learned from these institutional actions.`: 1 (0.2%)
- `In May of 2020, we had just started the lockdown as a result of the pandemic, and our coursework had become fully online. During my Physics 1 final, I attempted to access information online while taking the exam, which was not permitted.  I was caught doing so and reported to the Dean of Students for Academic Dishonesty. A few months later, during the Fall of 2020, I had a meeting with the Dean and the instructor of the course, where we discussed my transgressions and what the consequences would be. I was placed on Academic Probation, had a mark of Academic Dishonesty placed on my record, and wrote a two page essay detailing what I had done wrong, the lessons I had learned, and what I would do if I was to be placed in that situation again. This was the biggest mistake I have made in my academic career, and I deeply regret having made it. I was not only upset for shooting myself in the foot by cheating, I was more upset at myself for being in a position where I felt the need to cheat. `: 1 (0.2%)
- `I received an academic integrity violation warning in Cell Biology. In preparation for the midterm my sophomore year, I created a study guide that covered all class material in great detail. During group study sessions, my classmates and I discussed important concepts using my study guide as an outline. When taking the open-book, online exam, I utilized my study guide the best I could. However, this study guide was shared to the classmates I worked with and I was naive to use the same study material, as I was responsible for sharing my study guide. Studying in groups is a valuable learning method, but it is a different story when that leads to a gateway of cheating. I should have been aware that sharing a study guide was a risk factor for both myself and my classmates. I pushed my boundaries to an extent I now realize I should not have, and it was an experience that fundamentally changed my mindset on the need to be more cognizant of my own behavior and those around me.`: 1 (0.2%)
- `During the fall of my junior year of college, I was found to have unlawfully collaborated with others on weekly assignments in Principles of the Nervous System for which I was given academic probation. Although the violation was unintentional, it occurred because I had a lack of understanding about my learning style. When I engaged in the course permitted discussions with other students, I wrote the ideas we had discussed in my notes and used the ideas in my notes for my assignment. My reflection after receiving the violation helped me understand that I needed to change the way I completed assignments to avoid any chance of having similar ideas to other students. As a whole, I deeply regret my academic integrity violation. Since receiving this violation, I have taken numerous courses that involve weekly assignments with discussion and worked as a chemistry TA in charge of grading quizzes and exams. Equally importantly, I learned how to be empathetic while dealing with personal issues.`: 1 (0.2%)
- `When I took Organic Chemistry, my assigned lab partner and I were accused of working together on a pre-lab assignment which was supposed to be worked on individually. These pre-lab reports were to be completed prior to the day we performed that specific lab experiment. For one of these pre-lab reports, my lab partner was confused on what needed to be done so I decided to explain the instructions to him and give him a summary of what was expected. Although we worked on it individually, we ended up having almost similar calculations and as a result, we were accused of working on the report together. I took responsibility for my actions and got a grade of zero on that assignment. I realize now that I should not have given him that summary. This taught me that it is important to assess the type of assistance required in any given situation before jumping in to help. Since this incident, I have not had any other violations.`: 1 (0.2%)
- `In 2000, more than two decades ago, I plagiarized a paragraph of text on an essay. It was an obvious violation and I accepted responsibility and the consequences, which were a failing grade in the class and a one-year hold on my diploma. Though there is no excuse for such an act, I was under deadline for multiple papers and was overwhelmed. I should have asked for a meeting with the professor to explain that I had taken on too much that semester and to see if I could get a deadline extension on the paper. I remember how I felt at the time--the shame and remorse are easy to recall. I know that it took a long time for me to find forgiveness for myself. In those days I was less assertive and had a hard time showing vulnerability, which are issues that I have worked on in therapy. I'm grateful that I learned a difficult lesson like this relatively early in life as I believe it made me a more empathic person. I understand how it feels to make a regrettable decision and need a second chance.`: 1 (0.2%)
- `Freshman year in 2018, I received a low-level alcohol infraction. I received a message from a friend to join them and others in a dorm to play card games that included alcohol. I accepted, and a few minutes after I arrived the resident assistants appeared and we were written up. Before joining the room, I was unaware the card games included alcohol. Still, I made the illogical decision to stay in that environment. This was a short-sighted act and I take full responsibility for my actions. It was the last of any type of misconduct. I met with the conduct board and explained that I was only in the presence of alcohol. Afterward, I wrote a letter detailing the harms of drinking alcohol. The situation was resolved and I am currently in good standing with the university. I deeply regret this incident as it is detrimental to my reputation as a good student._x000D_
_x000D_
This incident taught me that it is important which type of people I associate with and allowed me to mature professionally.`: 1 (0.2%)

**3 - Research** (Top 10 values):
- `No Research`: 401 (100.0%)

**LOR - Offer Committee Letter** (Top 10 values):
- `No`: 237 (59.1%)
- `Yes`: 164 (40.9%)

**LOR - Letter Types Submitting** (Top 10 values):
- `Three Individual Letters`: 228 (56.9%)
- `Committee Letter`: 141 (35.2%)
- `Letter Packet`: 32 (8.0%)

**LOR - Not Submitting Committee Letter Reason** (Top 10 values):
- `When I was studying at Fresno State, the committee letter required an MCAT score. However, during that application window for the committee letter, I was still studying for my initial exam. `: 1 (0.2%)
- `I've chosen to submit three individual letters as opposed to my Committee Letter because Duke does not provide written committee letters that equate to letters of recommendation. Instead, they are concise summaries of our time at Duke. I feel that my individual letters may provide much more insight into my character, abilities, and goals. `: 1 (0.2%)
- `Some of those individuals who I worked most closely with as an undergraduate (Dr. Nicholas Worley and Ryan Heffernan) are no longer employed by Boston College. In addition, as I received a graduate degree from Georgetown University, my letter from that program's director (and my advisor), Dr. Jennifer Whitney, would not be included by this office. Further, I was told by the Pre-Health Office that, even had I requested their services, they would prefer to begin the committee process following the completion of my graduate degree, and as my graduate program ended in August 2022, no committee letter could have been submitted in time for this application cycle. It is my hope that the three letters I have included will provide helpful insight to the Committee on my academic readiness for medical school and motivation for a career as a physician.`: 1 (0.2%)
- `Being two years removed from my undergraduate program, I found it was more valuable and representative to receive letters of recommendation from clinical faculty I have worked with and professors I have had after my time in school.`: 1 (0.2%)
- `Last year when I was deciding to apply to medical school, I was juggling schoolwork, research, and familial pressure to make a decision. I still wasn't sure if I wanted to apply this year or the next because I was trying to plan out my medical career. I was weighing the pros and cons of taking a gap year. My school's deadline to apply for the premedical committee was early November, and I still wasn't ready by then to decide. Once the deadline passed and I had made my choice, I reached out to them but they said I would have to wait until next year so I just decided to apply without them.`: 1 (0.2%)
- `I'm not currently enrolled at the University of Tampa, so I was unaware of the March 2022 deadline to request a Committee Letter for this application cycle. `: 1 (0.2%)
- `I was a graduate of the Class of 2020 and had to leave campus mid-semester to complete my studies virtually. While proud that I graduated on time and avoided having to take any post-bacc courses, this was a tumultuous time both personally and academically. My last few months of undergrad did not play out as expected, which would have included obtaining a committee letter from my institution and completing my medical school application in a traditional timeline. However, by way of several virtual post-grad meetings, I did work with my advising department to assemble a letter packet instead. `: 1 (0.2%)
- `Unfortunately I missed the deadline for having a committee letter`: 1 (0.2%)
- `I am choosing not to submit a committee letter from Texas Tech University. I transferred to Texas Tech in the Fall of 2019, and after one semester, the Covid-19 pandemic started. Because of this, I had very little face-to-face interaction with my professors, and I believe it would have been difficult for them to assess me as a student and classmate accurately. `: 1 (0.2%)
- `Harvard Extension School's (HES) premed program accepts US citizens and permanent residents only. When I started taking courses at HES, I was not a permanent resident of the US yet. So I was not eligible to apply to the premed program. I received my greencard in August 2021. By then it was too late to apply to the program. That is why I was not eligible to request a letter from the Committee.`: 1 (0.2%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| application_id | 401 | 101861.80 | 3033.50 | 97034.00 | 99304.00 | 101837.00 | 104457.00 | 107399.00 |
| App Year | 401 | 2023.00 | 0.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 |
| AMCAS ID | 401 | 15219108.26 | 377750.72 | 13278986.00 | 15039509.00 | 15273506.00 | 15477871.00 | 15758293.00 |
| 3 - Reflect Experience | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Hope to Gain | 0 | nan | nan | nan | nan | nan | nan | nan |
| 6 - Addtl Info | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - # Summers | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - # Semesters | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - # Years | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - Abstract(s) | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - Conference Presentation(s) | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - Poster Presentation(s) | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - Publication(s) | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Employer 1 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 1 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 1 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Employer 2 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 2 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 2 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Employer 3 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 3 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 3 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Volunteer 1 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 1 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 1 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Volunteer 2 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 2 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 2 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Volunteer 3 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 3 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 3 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| Citizenship - Signature Date | 401 | 44760.69 | 407.41 | 36643.00 | 44759.00 | 44771.00 | 44800.00 | 44880.00 |

### 2024 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| application_id | int64 | 613 | 0.0% |
| App Year | int64 | 1 | 0.0% |
| AMCAS ID | int64 | 613 | 0.0% |
| Last Name | object | 546 | 0.0% |
| First Name | object | 478 | 0.0% |
| Middle Name | object | 305 | 36.7% |
| 1 - Personal Attributes / Life Experiences | object | 613 | 0.0% |
| 2 - Challenging Situation | object | 613 | 0.0% |
| 3 - Reflect Experience | float64 | 0 | 100.0% |
| 4 - Hope to Gain | float64 | 0 | 100.0% |
| 5 - Employed Undergrad | object | 2 | 0.0% |
| 5 - Employment Hours | object | 3 | 13.9% |
| 5 - Employment Duration | object | 4 | 13.9% |
| 6 - Direct Care Experience | object | 2 | 0.0% |
| 6 - Experiences | object | 609 | 0.7% |
| 6 - Addtl Info | float64 | 0 | 100.0% |
| 7 - COVID Impact | object | 531 | 13.4% |
| 8 - Institutional Action / Crime | object | 2 | 0.0% |
| 8 - Details | object | 10 | 98.4% |
| 3 - Research | object | 1 | 0.0% |
| 3 - # Summers | float64 | 0 | 100.0% |
| 3 - # Semesters | float64 | 0 | 100.0% |
| 3 - # Years | float64 | 0 | 100.0% |
| 3 - Abstract(s) | float64 | 0 | 100.0% |
| 3 - Conference Presentation(s) | float64 | 0 | 100.0% |
| 3 - Poster Presentation(s) | float64 | 0 | 100.0% |
| 3 - Publication(s) | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Employer 1 | float64 | 0 | 100.0% |
| 4 - Employer 1 Direct Patient | float64 | 0 | 100.0% |
| 4 - Employer 1 Duration | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Employer 2 | float64 | 0 | 100.0% |
| 4 - Employer 2 Direct Patient | float64 | 0 | 100.0% |
| 4 - Employer 2 Duration | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Employer 3 | float64 | 0 | 100.0% |
| 4 - Employer 3 Direct Patient | float64 | 0 | 100.0% |
| 4 - Employer 3 Duration | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Volunteer 1 | float64 | 0 | 100.0% |
| 4 - Volunteer 1 Direct Patient | float64 | 0 | 100.0% |
| 4 - Volunteer 1 Duration | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Volunteer 2 | float64 | 0 | 100.0% |
| 4 - Volunteer 2 Direct Patient | float64 | 0 | 100.0% |
| 4 - Volunteer 2 Duration | float64 | 0 | 100.0% |
| 4 - Healthcare Experience - Volunteer 3 | float64 | 0 | 100.0% |
| 4 - Volunteer 3 Direct Patient | float64 | 0 | 100.0% |
| 4 - Volunteer 3 Duration | float64 | 0 | 100.0% |
| LOR - Offer Committee Letter | object | 2 | 0.0% |
| LOR - Letter Types Submitting | object | 3 | 0.0% |
| LOR - Not Submitting Committee Letter Reason | object | 32 | 94.8% |
| LOR - Which Three Letters | object | 252 | 56.8% |
| Citizenship - Signature | object | 611 | 0.0% |
| Citizenship - Signature Date | int64 | 108 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  application_id: 109007
  App Year: 2024
  AMCAS ID: 15210814
  Last Name: Lo Presti
  First Name: Gianna
  Middle Name: Angela
  1 - Personal Attributes / Life Experiences: Nothing teaches you how to work with others quite like being in a hospital. Mostly because you don‚Äôt have a choice. When I was a hospital volunteer, I interacted with patients, doctors, and nurses from all different backgrounds on a daily basis. There was a large Spanish-speaking population, so many patients did not speak English. It was difficult at first, as I did not know how to interact with them. I unfortunately do not speak Spanish, and I feared that I would not be able to help these patients. But I just had to adjust. Beliefs, life experiences, languages, and attitudes impact how we give and receive care, and they should be respected and accommodated. I put aside my biases and preconceived notions and opened myself up to new ideas and experiences. I made use of translators, all the while trying to pick up phrases here and there. It taught me that my experiences are not universal, and they shouldn‚Äôt be. We each bring something valuable with us and we should learn from each other.
  2 - Challenging Situation: It was not until I reached college that I realized how much food insecurity impacted the community. I volunteered with organizations such as Meals on Wheels, Food Recovery Network, and the Cleveland Food Bank, which showed me just how much of our health is determined by food. Thanksgiving especially was eye-opening. I took a shift at the food bank, where we made hundreds of meal kits to hand out. They were all gone by the end of the night. Each person said thank you to all of us for giving them what they needed to have a nice holiday with their families. At first, it seemed like such a little thing, but talking with the families made me realize just how much it meant to them. It is easy to take food for granted. Being there showed me how much even one good meal can make someone‚Äôs day. I am grateful that I was able to give these families some good food and a good holiday, and I am so glad that organizations like the food bank exist to help those who struggle with food insecurity. 
  3 - Reflect Experience: nan
  4 - Hope to Gain: nan
Row 2:
  application_id: 109011
  App Year: 2024
  AMCAS ID: 15659473
  Last Name: White
  First Name: Clotilde
  Middle Name: nan
  1 - Personal Attributes / Life Experiences: A few years ago, I attended a wedding where I met a friend-of-a-friend for the first time. Prior to meeting, I was told that we held very different political views. With only that in mind, I decided I wasn‚Äôt going to like him. However, when I finally met him, he was the nicest person at the gathering. I struggled to hold these conflicting views of him in my mind; the one where he was funny and friendly, and the other where we disagreed on basic human rights. I learned that making such judgements about others is divisive, and only serves to worsen the chasms that can occur between people with opposing views. I‚Äôve also learned it‚Äôs impossible to define a person simply by what they believe, without leaving room for effective communication and understanding. While I felt embarrassed and guilty after realizing how wrong I had been, this experience helped me reassess my prejudices about those who I disagree with, which will lead to better interactions with those unlike myself in the future.
  2 - Challenging Situation: As a volunteer for the People‚Äôs Center, a community health clinic, I‚Äôm responsible for tracking social determinants of health across patients to assess the needs of individuals and of the community. By tracking this information, I‚Äôm able to work with administrators at the clinic to determine what programs and help should be offered by the clinic to assist with the largest areas of insecurity. These areas include helping with food insecurity, assisting with transportation to the clinic, and working with those who are unemployed to find a job if they desire help. While these changes often only affect one person at a time, I know my work in this area has helped make a difference in the lives of those who come to the clinic by communicating their needs to those who can help. As much as it disheartens me to see the struggles of so many, I use these emotions to fuel me through my work as I know the best way to help these patients is by getting resources to them through the clinic. 
  3 - Reflect Experience: nan
  4 - Hope to Gain: nan
Row 3:
  application_id: 109021
  App Year: 2024
  AMCAS ID: 14324637
  Last Name: Chapman
  First Name: Nicholas
  Middle Name: nan
  1 - Personal Attributes / Life Experiences: In street medicine, we focus on medically stabilizing patients regardless of their background, cultural, and socioeconomic status, as the focus is to heal patients. A particular example is when I was with one of our physicians looking for a patient who lived in the riverbed after being involved in a gang fight. The plan was to do a vitals check-up and deliver medication; however, the patient spoke Spanish and very little English. So, my task was to guide the physician, due to my comfortability with the area, and to speak in Spanish to find the patient. As I began speaking to the patient next to their tent, I found out he also had a leg wound that we needed to clean. We collected vitals, delivered his meds, and cleaned the wound. His involvement with gangs, sadly, could have been a byproduct of the difficulties of navigating the system. Working with these marginalized and underserved patients, I have learned skills that I would apply in the care of the Chicago‚Äôs west side patients.
  2 - Challenging Situation: At USC, transfer students faced systemic inequality, especially in academic opportunity. Exclusion from a policy for grade replacement in freshman courses with below a C- led transfers to a disadvantage in GPA, impacting students for graduate program applications, honors qualifications, and internship opportunities. Recognizing this disparity, I established a transfer ambassador program within TSC and coordinated meetings with the deans of each USC College to assess the needs of transfer students. As a result, we developed a comprehensive survey that is still used today as a major resource for statistical backing to get transfer advocacy projects off the ground. I then developed the Transfer Student Forgiveness Policy, which required me to lead discussions with the USC vice-provost, provost, and student governments. Once I graduated, the policy was enacted, and now first-semester USC transfer students have equal academic opportunity for their future goals as their peers.
  3 - Reflect Experience: nan
  4 - Hope to Gain: nan
```

#### Categorical Column Distributions

**App Year** (Top 10 values):
- `2024`: 613 (100.0%)

**5 - Employed Undergrad** (Top 10 values):
- `Yes`: 528 (86.1%)
- `No`: 85 (13.9%)

**5 - Employment Hours** (Top 10 values):
- `Part-time (less than 20 hours)`: 269 (43.9%)
- `Part-time (20 hours or more)`: 230 (37.5%)
- `Full-time`: 29 (4.7%)

**5 - Employment Duration** (Top 10 values):
- `More than 3 Academic Years`: 202 (33.0%)
- `1 Academic Year`: 136 (22.2%)
- `2 Academic Years`: 108 (17.6%)
- `Less Than 1 Academic Year`: 82 (13.4%)

**6 - Direct Care Experience** (Top 10 values):
- `Yes`: 609 (99.3%)
- `No`: 4 (0.7%)

**8 - Institutional Action / Crime** (Top 10 values):
- `No`: 603 (98.4%)
- `Yes`: 10 (1.6%)

**8 - Details** (Top 10 values):
- `The week before final exams my freshman year of college, my instructor told me that I would receive a failing grade in my chemistry course. After excelling in my exams in the lecture portion, an accusation of plagiarism resulting from my failure to cite sources in my lab reports was enough to sabotage my final grade. The regret and anger I felt towards myself for trying to submit perfect (albeit dishonest) lab reports almost made me abandon the pre-med track. In the last 7 years since then, I have demonstrated an upward trajectory in both successfully retaking chemistry and other challenging science courses. Additionally, I have published papers and abstracts, presented at research conferences, gained valuable clinical experiences, and currently work as a program manager in homeless services overseeing government contracts and large amounts of funding. This setback, once viewed as a catastrophic failure, has become an opportunity for introspection, growth, and redirection.`: 1 (0.2%)
- `On June 13, 2022, I received a speeding ticket in Gwinnett County, Georgia on my way home from class. All speeding tickets in the state of Georgia are considered misdemeanors. I plead guilty, paid the required fine, and attended mandated driver education courses. I am currently an active driver in the state of Georgia and the United States, and I implement the material I learned during the courses into my day-to-day driving.`: 1 (0.2%)
- `During my second year at UC Santa Cruz, I was enrolled in an online Statistics Lab course (AMS 7L) that lacked in-person sections or lectures. The course was structured in such a way that collaboration with fellow students was allowed as long as we completed the work ourselves. As a result, I would sometimes meet up with two friends from the class and we would go through the lab together to make sure we understood how to do that week's lab assignment._x000D_
_x000D_
After going through the lab, we would then split-up and complete the assignments individually. Unfortunately, due to our use of a shared "base" number during these collaborative sessions, as subsequent answers depended on the previous answer, we unknowingly produced similar answers on three of the labs. At the time, I was not aware we were ending up with similar answers and had no intention to do so._x000D_
_x000D_
Consequently of doing so unknowingly, I was issued a warning from the Provost and was told to not work on the assignments together again.`: 1 (0.2%)
- `As a freshman on April 13, 2020, I was cited for using my peer‚Äôs work in part of my submission for Introduction to Theatre (THEA 101). As a result of this action, I received a 0 on this assignment. This incident served as a pivotal moment as I reflected on my actions. I realized that such an action not only undermines the integrity of the education system but also hinders my individual growth and development. I had let myself down with this mistake and sought to employ my best judgment in my work and daily life moving forward._x000D_
_x000D_
Becoming a teacher for ENG 100, an introductory course required to be taken by all freshmen in engineering, allowed me to channel this lesson into a tangible impact. By emphasizing the importance of maintaining integrity and sharing my experience, I aimed to instill ethical habits early on in the college careers of freshmen and want to continue such mentorship opportunities through Rush‚Äôs curriculum rooted in justice and fairness. _x000D_
`: 1 (0.2%)
- `In Winter quarter of 2021, my lab partner and I collaborated on an online Organic Chemistry lab assignment. Since my classmate was short on time, I allowed her to plagiarize some of my answers. We accepted our consequences and received zero credit on the assignment. For the remainder of the year, I was placed on academic probation. I then took an Academic Integrity class in Spring Quarter of 2021 and was reminded of the importance of moral values and integrity. The class also reminded me how allowing others to plagiarize my work is still a violation of academic integrity and that in order to set a good example to others, I need to first be able to uphold my values of honesty, integrity, and responsibility. Since then, I have personally grown and reflected on my actions and am committed to upholding these values. I have worked my hardest to change and will never forget the mistake I made. I will never again share my work for others to claim or ever claim another person's work as my own.`: 1 (0.2%)
- `I was put on academic probation the spring of 2020 for plagiarizing from an open-source online repository part of a homework assignment ‚ÄúHomepage + Finance‚Äù due on Nov. 22, 2019 for my class ‚ÄúIntroduction to Programming.‚Äù The Nov. 23 weekend was the annual Harvard-Yale Football game, hosted that year at Yale. I stayed at Harvard to host a group of church friends who would fly in the night of Nov. 22 to visit. I had planned inadequately to have my assignment finished before my homework partners and teaching fellows left for Yale, so as my friends arrived, I was still struggling to finish the assignment on time. The pressure to maintain my "A" in the course along with the embarrassment of being unavailable as a host eventually led me to plagiarize the online source. I learned how even when I fail to meet my own performance standards, it is better to be honest than self-preserving. Being unwilling to shoulder a late-penalty kept me from properly learning the material of the assignment.`: 1 (0.2%)
- `In September 2020, I googled solutions for an online quiz (MCELLBI 102). While the disciplinary action was expunged from my records, my course grade was dropped one letter. I received a zero on the quiz and was required to submit a reflective paper._x000D_
_x000D_
Since then, I have demonstrated continued honesty and sought to help others reflect on their mistakes. While teaching a Genetics and Ethics course, I recall a student who submitted placeholders on discussion posts and edited them after deadlines. During my sensitive conversation with them, I sought to educate them and remind myself of the value of assessments, fairness, and growth._x000D_
_x000D_
I have internalized that patients‚Äô lives will depend on my commitment to integrity ‚Äì which includes my content mastery, study habits, and behavior demonstrated. I refuse to let my mistakes dictate the exceptional care that I hope to provide. I am committed to not taking shortcuts as a physician, regardless of any misguidedly perceived short-term benefits.`: 1 (0.2%)
- `As mentioned in my application, I received a DUI during my undergraduate studies in Fall of 2019. I was grateful no one was hurt and ashamed of this poor decision. I self-reported the incident to my college and was subsequently suspended from school at the end of my fall semester. I had to form a new mindset. I refused to give up and continued learning, studying, and finding enjoyment in my extracurricular activities. With a newfound resolve, I was actually encouraged, knowing that I had made positive changes in my life, such as coaching at my local soccer club and honing my learning strategies to succeed in college. I returned to school the following semester, focused and ready to learn, harnessing my love of the subject matter to overcome outcome-based stress and continuing to look for ways to improve myself. Getting through this period of my life through self-improvement leads me to believe there is no challenge I cannot overcome as long as I maintain a self-reflecting attitude. _x000D_
`: 1 (0.2%)
- `Five years ago, after I was sexually assaulted, I created an Instagram post that was open to about seven people, jokingly telling them to beat my abuser up. I was inappropriately venting my pain and I genuinely did not want him to want him to get hurt. He found the post and reported it to my school. I knew that what I had done was wrong so I admitted it during the disciplinary meeting. As a result, I was placed on probation for a semester. _x000D_
_x000D_
I deeply regret my actions and I have learned a lot from my mistakes. Since then, I have also volunteered as a sexual assault/domestic violence advocate to support other survivors. `: 1 (0.2%)
- `I indicated I received institutional action on my AMCAS application as a precaution. In my freshman year, I was in the dorms with two guys. One of the guys decided to take one of the hall rules posted in the halls and bring it into our room. The residence assistant discovered the stolen sign the same night, and our entire dorm had to meet with the head resident assistant to discuss who took the sign and the punishment. The roommate who took the sign took full responsibility for his actions; as such, no measures were taken against me or my other roommate. I wanted to share this with complete transparency as it was the only occurrence of any disciplinary action I had undergone in my education. _x000D_
 `: 1 (0.2%)

**3 - Research** (Top 10 values):
- `No Research`: 613 (100.0%)

**LOR - Offer Committee Letter** (Top 10 values):
- `No`: 405 (66.1%)
- `Yes`: 208 (33.9%)

**LOR - Letter Types Submitting** (Top 10 values):
- `Three Individual Letters`: 395 (64.4%)
- `Committee Letter`: 176 (28.7%)
- `Letter Packet`: 42 (6.9%)

**LOR - Not Submitting Committee Letter Reason** (Top 10 values):
- `My school has a Health Professions Committee, but I am not using this service to receive a letter of recommendation. I wanted my letters to be personable, which is why I chose to ask professors I have interacted with to be my letter-writers. I feel I made personal connections with these professors and developed strong relationships with them, so I felt a combination of these letters would be better than using the service my school provides.`: 1 (0.2%)
- `I was not eligible to receive a Committee letter from my institution.`: 1 (0.2%)
- `Not available`: 1 (0.2%)
- `I have submitted two individual letters of recommendation in addition to a committee packet from Fordham University.`: 1 (0.2%)
- `Since I graduated a year earlier and took a gap year to study for the MCAT, travel, and gain more clinical experience, it was challenging to obtain a committee letter. However, I am confident that the three letters I have will represent me effectively. These letters are from my professor, a teaching assistant who offered me a research position in her lab, and the doctor I work with, all from different aspects of my life, but all of whom have a close relationship with me and are familiar with my personality and abilities.`: 1 (0.2%)
- `I have been out of school for several years now. `: 1 (0.2%)
- `MSU-Bozeman only writes committee letters for alumni who graduated within the last two years. I completed my premedical post-baccalaureate program in 2019. `: 1 (0.2%)
- `I chose to give three individual letters because I fostered great relationships with my biochemistry professors and my research advisor. They were the most influential staff in my undergraduate experience, and I wouldn't be where I am without them, both academically and personally. I don't feel like my application would have been complete without the words from Dr. Silveira, Dr. Everse, and Dr. Gramling.`: 1 (0.2%)
- `Although I have previously applied to the College of the Holy Cross' Health Professions Committee for review, received a rating of "Recommended" for medical school applications, and was guaranteed a composite letter of recommendation, I was unaware that I would need to apply again to the committee in order for them to write me a composite letter for this application cycle. Thus, I missed their deadline and they were unwilling to write a letter for me in this cycle due solely to time constraints on their end. Instead, Professor Miles Cahill, the chair of the Holy Cross Health Professions Committee, agreed to send a letter packet with an associated cover letter. Therefore it is not by choice that I am not submitting a committee letter but rather due to my misunderstanding of the school's policy and time constraints alone. `: 1 (0.2%)
- `As I prepared to apply for a Committee Letter in the fall semester of my senior year at Emory University, I noticed significant areas for improvement in my narrative and application. Given the hiatus created by the COVID-19 pandemic, I did not have clinical or shadowing experiences that would support my interests in medicine, ultimately leading to my decision not to obtain a Committee Letter at this time. The following semester, I began working as a medical assistant at Modern Ob/Gyn while completing final courses for my undergraduate degree, conducting an independent study under Dr. Ristaino, and working as an organic chemistry lab assistant. Upon graduating, I knew I could not apply to obtain a Committee Letter as an alumnus, so I stayed in contact with each letter writer to receive individual letters for this application cycle. _x000D_
`: 1 (0.2%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| application_id | 613 | 114372.55 | 3506.67 | 109007.00 | 111307.00 | 114069.00 | 116780.00 | 121972.00 |
| App Year | 613 | 2024.00 | 0.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 |
| AMCAS ID | 613 | 15463699.57 | 409149.24 | 13149516.00 | 15280062.00 | 15519360.00 | 15750866.00 | 16091417.00 |
| 3 - Reflect Experience | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Hope to Gain | 0 | nan | nan | nan | nan | nan | nan | nan |
| 6 - Addtl Info | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - # Summers | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - # Semesters | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - # Years | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - Abstract(s) | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - Conference Presentation(s) | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - Poster Presentation(s) | 0 | nan | nan | nan | nan | nan | nan | nan |
| 3 - Publication(s) | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Employer 1 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 1 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 1 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Employer 2 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 2 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 2 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Employer 3 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 3 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Employer 3 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Volunteer 1 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 1 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 1 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Volunteer 2 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 2 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 2 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Healthcare Experience - Volunteer 3 | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 3 Direct Patient | 0 | nan | nan | nan | nan | nan | nan | nan |
| 4 - Volunteer 3 Duration | 0 | nan | nan | nan | nan | nan | nan | nan |
| Citizenship - Signature Date | 613 | 45148.49 | 56.25 | 44081.00 | 45131.00 | 45141.00 | 45162.00 | 45246.00 |

### Schema Consistency Across Years

| Column | 2022 | 2023 | 2024 | Notes |
|--------|------|------|------|-------|
| 1 - Personal Attributes / Life Experiences | ✓ | ✓ | ✓ |  |
| 2 - Challenging Situation | ✓ | ✓ | ✓ |  |
| 3 - # Semesters | ✓ | ✓ | ✓ |  |
| 3 - # Summers | ✓ | ✓ | ✓ |  |
| 3 - # Years | ✓ | ✓ | ✓ |  |
| 3 - Abstract(s) | ✓ | ✓ | ✓ |  |
| 3 - Conference Presentation(s) | ✓ | ✓ | ✓ |  |
| 3 - Poster Presentation(s) | ✓ | ✓ | ✓ |  |
| 3 - Publication(s) | ✓ | ✓ | ✓ |  |
| 3 - Reflect Experience | ✓ | ✓ | ✓ |  |
| 3 - Research | ✓ | ✓ | ✓ |  |
| 4 - Employer 1 Direct Patient | ✓ | ✓ | ✓ |  |
| 4 - Employer 1 Duration | ✓ | ✓ | ✓ |  |
| 4 - Employer 2 Direct Patient | ✓ | ✓ | ✓ |  |
| 4 - Employer 2 Duration | ✓ | ✓ | ✓ |  |
| 4 - Employer 3 Direct Patient | ✓ | ✓ | ✓ |  |
| 4 - Employer 3 Duration | ✓ | ✓ | ✓ |  |
| 4 - Healthcare Experience - Employer 1 | ✓ | ✓ | ✓ |  |
| 4 - Healthcare Experience - Employer 2 | ✓ | ✓ | ✓ |  |
| 4 - Healthcare Experience - Employer 3 | ✓ | ✓ | ✓ |  |
| 4 - Healthcare Experience - Volunteer 1 | ✓ | ✓ | ✓ |  |
| 4 - Healthcare Experience - Volunteer 2 | ✓ | ✓ | ✓ |  |
| 4 - Healthcare Experience - Volunteer 3 | ✓ | ✓ | ✓ |  |
| 4 - Hope to Gain | ✓ | ✓ | ✓ |  |
| 4 - Volunteer 1 Direct Patient | ✓ | ✓ | ✓ |  |
| 4 - Volunteer 1 Duration | ✓ | ✓ | ✓ |  |
| 4 - Volunteer 2 Direct Patient | ✓ | ✓ | ✓ |  |
| 4 - Volunteer 2 Duration | ✓ | ✓ | ✓ |  |
| 4 - Volunteer 3 Direct Patient | ✓ | ✓ | ✓ |  |
| 4 - Volunteer 3 Duration | ✓ | ✓ | ✓ |  |
| 5 - Employed Undergrad | ✓ | ✓ | ✓ |  |
| 5 - Employment Duration | ✓ | ✓ | ✓ |  |
| 5 - Employment Hours | ✓ | ✓ | ✓ |  |
| 6 - Addtl Info | ✓ | ✓ | ✓ |  |
| 6 - Direct Care Experience | ✓ | ✓ | ✓ |  |
| 6 - Experiences | ✓ | ✓ | ✓ |  |
| 7 - COVID Impact | ✓ | ✓ | ✓ |  |
| 8 - Details | ✓ | ✓ | ✓ |  |
| 8 - Institutional Action / Crime | ✓ | ✓ | ✓ |  |
| AMCAS ID | ✓ | ✓ | ✓ |  |
| App Year | ✓ | ✓ | ✓ |  |
| Citizenship - Signature | ✓ | ✓ | ✓ |  |
| Citizenship - Signature Date | ✓ | ✓ | ✓ |  |
| First Name | ✓ | ✓ | ✓ |  |
| LOR - Letter Types Submitting | ✓ | ✓ | ✓ |  |
| LOR - Not Submitting Committee Letter Reason | ✓ | ✓ | ✓ |  |
| LOR - Offer Committee Letter | ✓ | ✓ | ✓ |  |
| LOR - Which Three Letters | ✓ | ✓ | ✓ |  |
| Last Name | ✓ | ✓ | ✓ |  |
| Middle Name | ✓ | ✓ | ✓ |  |
| application_id | ✓ | ✓ | ✓ |  |

================================================================================
## FILE: 11. Military.xlsx
================================================================================

### Year-over-Year Overview

| Year | Rows | Columns | Status |
|------|------|---------|--------|
| 2022 | 0 | 0 | ✓ OK |
| 2023 | 8 | 7 | ✓ OK |
| 2024 | 5 | 7 | ✓ OK |

### 2022 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|

#### Sample Data (First 3 Rows)

```
```

### 2023 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| app_year | int64 | 1 | 0.0% |
| amcas_id | int64 | 8 | 0.0% |
| Last | object | 7 | 0.0% |
| First | object | 8 | 0.0% |
| military_service_descr | object | 1 | 0.0% |
| military_service_status_descr | object | 3 | 0.0% |
| military_service_status_other_descr | float64 | 0 | 100.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  app_year: 2023
  amcas_id: 13804254
  Last: Gonzalez
  First: Jordan
  military_service_descr: Yes
  military_service_status_descr: Veteran
  military_service_status_other_descr: nan
Row 2:
  app_year: 2023
  amcas_id: 14918343
  Last: Mohammed
  First: Hawarit
  military_service_descr: Yes
  military_service_status_descr: US Reserves or National Guard
  military_service_status_other_descr: nan
Row 3:
  app_year: 2023
  amcas_id: 15212852
  Last: Scully
  First: Christopher
  military_service_descr: Yes
  military_service_status_descr: Veteran
  military_service_status_other_descr: nan
```

#### Categorical Column Distributions

**app_year** (Top 10 values):
- `2023`: 8 (100.0%)

**amcas_id** (Top 10 values):
- `13804254`: 1 (12.5%)
- `14918343`: 1 (12.5%)
- `15212852`: 1 (12.5%)
- `15236199`: 1 (12.5%)
- `15284397`: 1 (12.5%)
- `15325850`: 1 (12.5%)
- `15595786`: 1 (12.5%)
- `15679302`: 1 (12.5%)

**Last** (Top 10 values):
- `Gonzalez`: 2 (25.0%)
- `Mohammed`: 1 (12.5%)
- `Scully`: 1 (12.5%)
- `Annan`: 1 (12.5%)
- `Alteva`: 1 (12.5%)
- `Angeles`: 1 (12.5%)
- `Amaru`: 1 (12.5%)

**First** (Top 10 values):
- `Jordan`: 1 (12.5%)
- `Hawarit`: 1 (12.5%)
- `Christopher`: 1 (12.5%)
- `Diego`: 1 (12.5%)
- `Isaac`: 1 (12.5%)
- `Gergana`: 1 (12.5%)
- `John`: 1 (12.5%)
- `Anthony`: 1 (12.5%)

**military_service_descr** (Top 10 values):
- `Yes`: 8 (100.0%)

**military_service_status_descr** (Top 10 values):
- `Veteran`: 4 (50.0%)
- `US Reserves or National Guard`: 3 (37.5%)
- `Active Duty`: 1 (12.5%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| app_year | 8 | 2023.00 | 0.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 |
| amcas_id | 8 | 15132122.88 | 585709.91 | 13804254.00 | 15139224.75 | 15260298.00 | 15393334.00 | 15679302.00 |
| military_service_status_other_descr | 0 | nan | nan | nan | nan | nan | nan | nan |

### 2024 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| app_year | int64 | 1 | 0.0% |
| amcas_id | int64 | 5 | 0.0% |
| Last | object | 5 | 0.0% |
| First | object | 5 | 0.0% |
| military_service_descr | object | 1 | 0.0% |
| military_service_status_descr | object | 3 | 0.0% |
| military_service_status_other_descr | float64 | 0 | 100.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  app_year: 2024
  amcas_id: 13149516
  Last: Young
  First: Matthew
  military_service_descr: Yes
  military_service_status_descr: Active Duty
  military_service_status_other_descr: nan
Row 2:
  app_year: 2024
  amcas_id: 15094147
  Last: Esquivel
  First: Benjamin
  military_service_descr: Yes
  military_service_status_descr: Veteran
  military_service_status_other_descr: nan
Row 3:
  app_year: 2024
  amcas_id: 15734835
  Last: Qamar
  First: Kashf
  military_service_descr: Yes
  military_service_status_descr: US Reserves or National Guard
  military_service_status_other_descr: nan
```

#### Categorical Column Distributions

**app_year** (Top 10 values):
- `2024`: 5 (100.0%)

**amcas_id** (Top 10 values):
- `13149516`: 1 (20.0%)
- `15094147`: 1 (20.0%)
- `15734835`: 1 (20.0%)
- `15874116`: 1 (20.0%)
- `15943234`: 1 (20.0%)

**Last** (Top 10 values):
- `Young`: 1 (20.0%)
- `Esquivel`: 1 (20.0%)
- `Qamar`: 1 (20.0%)
- `Lee`: 1 (20.0%)
- `Gistand`: 1 (20.0%)

**First** (Top 10 values):
- `Matthew`: 1 (20.0%)
- `Benjamin`: 1 (20.0%)
- `Kashf`: 1 (20.0%)
- `Ji Ho`: 1 (20.0%)
- `Triniti`: 1 (20.0%)

**military_service_descr** (Top 10 values):
- `Yes`: 5 (100.0%)

**military_service_status_descr** (Top 10 values):
- `Active Duty`: 2 (40.0%)
- `Veteran`: 2 (40.0%)
- `US Reserves or National Guard`: 1 (20.0%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| app_year | 5 | 2024.00 | 0.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 |
| amcas_id | 5 | 15159169.60 | 1172628.62 | 13149516.00 | 15094147.00 | 15734835.00 | 15874116.00 | 15943234.00 |
| military_service_status_other_descr | 0 | nan | nan | nan | nan | nan | nan | nan |

### Schema Consistency Across Years

| Column | 2022 | 2023 | 2024 | Notes |
|--------|------|------|------|-------|
| First | ✗ | ✓ | ✓ | Added in 2023 |
| Last | ✗ | ✓ | ✓ | Added in 2023 |
| amcas_id | ✗ | ✓ | ✓ | Added in 2023 |
| app_year | ✗ | ✓ | ✓ | Added in 2023 |
| military_service_descr | ✗ | ✓ | ✓ | Added in 2023 |
| military_service_status_descr | ✗ | ✓ | ✓ | Added in 2023 |
| military_service_status_other_descr | ✗ | ✓ | ✓ | Added in 2023 |

================================================================================
## FILE: 12. GPA Trend.xlsx
================================================================================

### Year-over-Year Overview

| Year | Rows | Columns | Status |
|------|------|---------|--------|
| 2022 | 437 | 3 | ✓ OK |
| 2023 | 401 | 3 | ✓ OK |
| 2024 | 613 | 3 | ✓ OK |

### 2022 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| AMCAS ID | int64 | 437 | 0.0% |
| Total_GPA_Trend | float64 | 2 | 45.1% |
| BCPM_GPA_Trend | float64 | 2 | 47.8% |

#### Sample Data (First 3 Rows)

```
Row 1:
  AMCAS ID: 12950085
  Total_GPA_Trend: 1.0
  BCPM_GPA_Trend: 1.0
Row 2:
  AMCAS ID: 13099483
  Total_GPA_Trend: nan
  BCPM_GPA_Trend: nan
Row 3:
  AMCAS ID: 13489485
  Total_GPA_Trend: 1.0
  BCPM_GPA_Trend: 1.0
```

#### Categorical Column Distributions

**Total_GPA_Trend** (Top 10 values):
- `1.0`: 196 (44.9%)
- `0.0`: 44 (10.1%)

**BCPM_GPA_Trend** (Top 10 values):
- `1.0`: 186 (42.6%)
- `0.0`: 42 (9.6%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| AMCAS ID | 437 | 15011632.22 | 363254.26 | 12950085.00 | 14880945.00 | 15057778.00 | 15243303.00 | 15499135.00 |
| Total_GPA_Trend | 240 | 0.82 | 0.39 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| BCPM_GPA_Trend | 228 | 0.82 | 0.39 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### 2023 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| AMCAS ID | int64 | 401 | 0.0% |
| Total_GPA_Trend | float64 | 2 | 45.6% |
| BCPM_GPA_Trend | float64 | 2 | 46.4% |

#### Sample Data (First 3 Rows)

```
Row 1:
  AMCAS ID: 13278986
  Total_GPA_Trend: nan
  BCPM_GPA_Trend: 1.0
Row 2:
  AMCAS ID: 13767033
  Total_GPA_Trend: nan
  BCPM_GPA_Trend: 0.0
Row 3:
  AMCAS ID: 13769330
  Total_GPA_Trend: 0.0
  BCPM_GPA_Trend: 0.0
```

#### Categorical Column Distributions

**Total_GPA_Trend** (Top 10 values):
- `1.0`: 190 (47.4%)
- `0.0`: 28 (7.0%)

**BCPM_GPA_Trend** (Top 10 values):
- `1.0`: 183 (45.6%)
- `0.0`: 32 (8.0%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| AMCAS ID | 401 | 15219108.26 | 377750.72 | 13278986.00 | 15039509.00 | 15273506.00 | 15477871.00 | 15758293.00 |
| Total_GPA_Trend | 218 | 0.87 | 0.34 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| BCPM_GPA_Trend | 215 | 0.85 | 0.36 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### 2024 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| AMCAS ID | int64 | 613 | 0.0% |
| Total_GPA_Trend | float64 | 2 | 55.0% |
| BCPM_GPA_Trend | float64 | 2 | 52.2% |

#### Sample Data (First 3 Rows)

```
Row 1:
  AMCAS ID: 13149516
  Total_GPA_Trend: 1.0
  BCPM_GPA_Trend: 1.0
Row 2:
  AMCAS ID: 13573284
  Total_GPA_Trend: 0.0
  BCPM_GPA_Trend: 0.0
Row 3:
  AMCAS ID: 13596519
  Total_GPA_Trend: nan
  BCPM_GPA_Trend: 1.0
```

#### Categorical Column Distributions

**Total_GPA_Trend** (Top 10 values):
- `1.0`: 216 (35.2%)
- `0.0`: 60 (9.8%)

**BCPM_GPA_Trend** (Top 10 values):
- `1.0`: 220 (35.9%)
- `0.0`: 73 (11.9%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| AMCAS ID | 613 | 15463699.57 | 409149.24 | 13149516.00 | 15280062.00 | 15519360.00 | 15750866.00 | 16091417.00 |
| Total_GPA_Trend | 276 | 0.78 | 0.41 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| BCPM_GPA_Trend | 293 | 0.75 | 0.43 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### Schema Consistency Across Years

| Column | 2022 | 2023 | 2024 | Notes |
|--------|------|------|------|-------|
| AMCAS ID | ✓ | ✓ | ✓ |  |
| BCPM_GPA_Trend | ✓ | ✓ | ✓ |  |
| Total_GPA_Trend | ✓ | ✓ | ✓ |  |

================================================================================
## FILE: 2. Language.xlsx
================================================================================

### Year-over-Year Overview

| Year | Rows | Columns | Status |
|------|------|---------|--------|
| 2022 | 1,004 | 5 | ✓ OK |
| 2023 | 916 | 5 | ✓ OK |
| 2024 | 1,472 | 5 | ✓ OK |

### 2022 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_id | int64 | 437 | 0.0% |
| Lang_Desc | object | 57 | 0.0% |
| Proficiency | object | 5 | 0.0% |
| Language_usage_Desc | object | 5 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2022
  Amcas_id: 15121499
  Lang_Desc: Spanish
  Proficiency: Basic
  Language_usage_Desc: Never
Row 2:
  App_Year: 2022
  Amcas_id: 14443340
  Lang_Desc: French
  Proficiency: Basic
  Language_usage_Desc: Never
Row 3:
  App_Year: 2022
  Amcas_id: 15366937
  Lang_Desc: Hebrew
  Proficiency: Basic
  Language_usage_Desc: Never
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2022`: 1,004 (100.0%)

**Proficiency** (Top 10 values):
- `Native/functionally native`: 542 (54.0%)
- `Basic`: 158 (15.7%)
- `Good`: 118 (11.8%)
- `Advanced`: 102 (10.2%)
- `Fair`: 84 (8.4%)

**Language_usage_Desc** (Top 10 values):
- `Always`: 414 (41.2%)
- `Never`: 216 (21.5%)
- `Often`: 193 (19.2%)
- `From time to time`: 109 (10.9%)
- `Rarely`: 72 (7.2%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 1004 | 2022.00 | 0.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 |
| Amcas_id | 1004 | 15008542.90 | 375903.47 | 12950085.00 | 14880602.00 | 15071001.00 | 15237074.25 | 15499135.00 |

### 2023 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_id | int64 | 401 | 0.0% |
| Lang_Desc | object | 52 | 0.0% |
| Proficiency | object | 5 | 0.0% |
| Language_usage_Desc | object | 5 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2023
  Amcas_id: 14938390
  Lang_Desc: French
  Proficiency: Basic
  Language_usage_Desc: Never
Row 2:
  App_Year: 2023
  Amcas_id: 14555162
  Lang_Desc: French
  Proficiency: Basic
  Language_usage_Desc: Never
Row 3:
  App_Year: 2023
  Amcas_id: 15183698
  Lang_Desc: Spanish
  Proficiency: Basic
  Language_usage_Desc: From time to time
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2023`: 916 (100.0%)

**Proficiency** (Top 10 values):
- `Native/functionally native`: 502 (54.8%)
- `Basic`: 159 (17.4%)
- `Good`: 93 (10.2%)
- `Advanced`: 82 (9.0%)
- `Fair`: 80 (8.7%)

**Language_usage_Desc** (Top 10 values):
- `Always`: 396 (43.2%)
- `Never`: 209 (22.8%)
- `Often`: 148 (16.2%)
- `From time to time`: 89 (9.7%)
- `Rarely`: 74 (8.1%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 916 | 2023.00 | 0.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 |
| Amcas_id | 916 | 15214754.99 | 380228.84 | 13278986.00 | 15033897.00 | 15270157.00 | 15477868.75 | 15758293.00 |

### 2024 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_id | int64 | 613 | 0.0% |
| Lang_Desc | object | 61 | 0.0% |
| Proficiency | object | 5 | 0.0% |
| Language_usage_Desc | object | 5 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2024
  Amcas_id: 15790885
  Lang_Desc: Spanish
  Proficiency: Basic
  Language_usage_Desc: Never
Row 2:
  App_Year: 2024
  Amcas_id: 15790885
  Lang_Desc: French
  Proficiency: Basic
  Language_usage_Desc: Never
Row 3:
  App_Year: 2024
  Amcas_id: 15821528
  Lang_Desc: Greek
  Proficiency: Basic
  Language_usage_Desc: Never
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2024`: 1,472 (100.0%)

**Proficiency** (Top 10 values):
- `Native/functionally native`: 781 (53.1%)
- `Basic`: 205 (13.9%)
- `Good`: 189 (12.8%)
- `Advanced`: 158 (10.7%)
- `Fair`: 139 (9.4%)

**Language_usage_Desc** (Top 10 values):
- `Always`: 623 (42.3%)
- `Never`: 376 (25.5%)
- `Often`: 229 (15.6%)
- `From time to time`: 143 (9.7%)
- `Rarely`: 101 (6.9%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 1472 | 2024.00 | 0.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 |
| Amcas_id | 1472 | 15467139.59 | 403783.27 | 13149516.00 | 15272309.00 | 15520050.00 | 15752779.00 | 16091417.00 |

### Schema Consistency Across Years

| Column | 2022 | 2023 | 2024 | Notes |
|--------|------|------|------|-------|
| Amcas_id | ✓ | ✓ | ✓ |  |
| App_Year | ✓ | ✓ | ✓ |  |
| Lang_Desc | ✓ | ✓ | ✓ |  |
| Language_usage_Desc | ✓ | ✓ | ✓ |  |
| Proficiency | ✓ | ✓ | ✓ |  |

================================================================================
## FILE: 3. Parents.xlsx
================================================================================

### Year-over-Year Overview

| Year | Rows | Columns | Status |
|------|------|---------|--------|
| 2022 | 863 | 7 | ✓ OK |
| 2023 | 795 | 7 | ✓ OK |
| 2024 | 1,198 | 7 | ✓ OK |

### 2022 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_id | int64 | 437 | 0.0% |
| Gender | object | 2 | 0.0% |
| Living | object | 3 | 0.0% |
| Edu_Level | object | 17 | 0.0% |
| School_Name | object | 302 | 32.1% |
| Occupation | object | 102 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2022
  Amcas_id: 12950085
  Gender: Male
  Living: Yes
  Edu_Level: Associates Degree (AS,AN,etc.)
  School_Name: San Joaquin Delta College
  Occupation: Production Occupations
Row 2:
  App_Year: 2022
  Amcas_id: 12950085
  Gender: Female
  Living: Yes
  Edu_Level: High School Graduate (high school diploma or equivalent)
  School_Name: nan
  Occupation: Not Applicable
Row 3:
  App_Year: 2022
  Amcas_id: 13099483
  Gender: Male
  Living: Yes
  Edu_Level: Some college, but no degree
  School_Name: Other (not listed)
  Occupation: Primary, Secondary, or Special Education School Teacher
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2022`: 863 (100.0%)

**Gender** (Top 10 values):
- `Female`: 439 (50.9%)
- `Male`: 424 (49.1%)

**Living** (Top 10 values):
- `Yes`: 838 (97.1%)
- `No`: 20 (2.3%)
- `Do Not Know`: 5 (0.6%)

**Edu_Level** (Top 10 values):
- `Bachelor Degree (BA,BS,etc)`: 220 (25.5%)
- `Masters Degree`: 167 (19.4%)
- `High School Graduate (high school diploma or equivalent)`: 102 (11.8%)
- `Doctorate of Medicine (MD)`: 92 (10.7%)
- `Less Than High School`: 58 (6.7%)
- `Some college, but no degree`: 54 (6.3%)
- `Associates Degree (AS,AN,etc.)`: 52 (6.0%)
- `Doctor of Philosophy (Phd)`: 43 (5.0%)
- `Doctor of Jurisprudence`: 29 (3.4%)
- `Doctor of Dental Science(DDS,DMD)`: 9 (1.0%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 863 | 2022.00 | 0.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 |
| Amcas_id | 863 | 15014629.09 | 363610.27 | 12950085.00 | 14898533.00 | 15063869.00 | 15244194.00 | 15499135.00 |

### 2023 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_id | int64 | 400 | 0.0% |
| Gender | object | 3 | 0.0% |
| Living | object | 3 | 0.0% |
| Edu_Level | object | 21 | 0.0% |
| School_Name | object | 283 | 44.1% |
| Occupation | object | 99 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2023
  Amcas_id: 13278986
  Gender: Woman
  Living: Yes
  Edu_Level: Associates Degree (AS,AN,etc.)
  School_Name: Other (not listed)
  Occupation: Other Office and Administrative Support Occupation
Row 2:
  App_Year: 2023
  Amcas_id: 13278986
  Gender: Man
  Living: Yes
  Edu_Level: Bachelor Degree (BA,BS,etc)
  School_Name: Other (not listed)
  Occupation: Chief Executive
Row 3:
  App_Year: 2023
  Amcas_id: 13767033
  Gender: Man
  Living: Yes
  Edu_Level: High School Graduate (high school diploma or equivalent)
  School_Name: nan
  Occupation: Factory Worker / Dry Cleaner
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2023`: 795 (100.0%)

**Gender** (Top 10 values):
- `Woman`: 405 (50.9%)
- `Man`: 388 (48.8%)
- `Decline to Answer`: 2 (0.3%)

**Living** (Top 10 values):
- `Yes`: 773 (97.2%)
- `No`: 18 (2.3%)
- `Do Not Know`: 4 (0.5%)

**Edu_Level** (Top 10 values):
- `Bachelor Degree (BA,BS,etc)`: 225 (28.3%)
- `Masters Degree`: 152 (19.1%)
- `Doctorate of Medicine (MD)`: 96 (12.1%)
- `High School Graduate (high school diploma or equivalent)`: 95 (11.9%)
- `Less Than High School`: 55 (6.9%)
- `Some college, but no degree`: 47 (5.9%)
- `Associates Degree (AS,AN,etc.)`: 39 (4.9%)
- `Doctor of Jurisprudence`: 22 (2.8%)
- `Doctor of Philosophy (Phd)`: 18 (2.3%)
- `Doctor of Pharmacy`: 9 (1.1%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 795 | 2023.00 | 0.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 |
| Amcas_id | 795 | 15219416.58 | 380293.79 | 13278986.00 | 15042391.50 | 15273523.00 | 15477860.00 | 15758293.00 |

### 2024 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_id | int64 | 611 | 0.0% |
| Gender | object | 3 | 0.0% |
| Living | object | 3 | 0.0% |
| Edu_Level | object | 19 | 0.0% |
| School_Name | object | 363 | 45.3% |
| Occupation | object | 117 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2024
  Amcas_id: 13149516
  Gender: Woman
  Living: Yes
  Edu_Level: High School Graduate (high school diploma or equivalent)
  School_Name: nan
  Occupation: Other Transportation Occupation
Row 2:
  App_Year: 2024
  Amcas_id: 13573284
  Gender: Woman
  Living: Yes
  Edu_Level: Masters Degree
  School_Name: California Baptist University
  Occupation: Registered Nurse
Row 3:
  App_Year: 2024
  Amcas_id: 13573284
  Gender: Man
  Living: Yes
  Edu_Level: Bachelor Degree (BA,BS,etc)
  School_Name: nan
  Occupation: Not Applicable
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2024`: 1,198 (100.0%)

**Gender** (Top 10 values):
- `Woman`: 605 (50.5%)
- `Man`: 592 (49.4%)
- `Another Gender Identity`: 1 (0.1%)

**Living** (Top 10 values):
- `Yes`: 1,163 (97.1%)
- `No`: 33 (2.8%)
- `Do Not Know`: 2 (0.2%)

**Edu_Level** (Top 10 values):
- `Bachelor Degree (BA,BS,etc)`: 352 (29.4%)
- `Masters Degree`: 289 (24.1%)
- `High School Graduate (high school diploma or equivalent)`: 130 (10.9%)
- `Doctorate of Medicine (MD)`: 108 (9.0%)
- `Some college, but no degree`: 74 (6.2%)
- `Less Than High School`: 70 (5.8%)
- `Doctor of Philosophy (Phd)`: 45 (3.8%)
- `Associates Degree (AS,AN,etc.)`: 44 (3.7%)
- `Doctor of Jurisprudence`: 30 (2.5%)
- `MD/PhD`: 23 (1.9%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 1198 | 2024.00 | 0.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 |
| Amcas_id | 1198 | 15470087.67 | 401902.40 | 13149516.00 | 15288967.00 | 15519547.00 | 15752186.75 | 16091417.00 |

### Schema Consistency Across Years

| Column | 2022 | 2023 | 2024 | Notes |
|--------|------|------|------|-------|
| Amcas_id | ✓ | ✓ | ✓ |  |
| App_Year | ✓ | ✓ | ✓ |  |
| Edu_Level | ✓ | ✓ | ✓ |  |
| Gender | ✓ | ✓ | ✓ |  |
| Living | ✓ | ✓ | ✓ |  |
| Occupation | ✓ | ✓ | ✓ |  |
| School_Name | ✓ | ✓ | ✓ |  |

================================================================================
## FILE: 4. Siblings.xlsx
================================================================================

### Year-over-Year Overview

| Year | Rows | Columns | Status |
|------|------|---------|--------|
| 2022 | 776 | 4 | ✓ OK |
| 2023 | 757 | 5 | ✓ OK |
| 2024 | 1,077 | 4 | ✓ OK |

### 2022 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_ID | int64 | 437 | 0.0% |
| Age | float64 | 49 | 4.2% |
| Gender | object | 3 | 4.2% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2022
  Amcas_ID: 12950085
  Age: 28.0
  Gender: Male
Row 2:
  App_Year: 2022
  Amcas_ID: 12950085
  Age: 27.0
  Gender: Male
Row 3:
  App_Year: 2022
  Amcas_ID: 13099483
  Age: 33.0
  Gender: Female
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2022`: 776 (100.0%)

**Age** (Top 10 values):
- `25.0`: 56 (7.2%)
- `20.0`: 54 (7.0%)
- `22.0`: 50 (6.4%)
- `19.0`: 42 (5.4%)
- `18.0`: 40 (5.2%)
- `27.0`: 39 (5.0%)
- `17.0`: 37 (4.8%)
- `26.0`: 35 (4.5%)
- `21.0`: 34 (4.4%)
- `24.0`: 31 (4.0%)

**Gender** (Top 10 values):
- `Male`: 381 (49.1%)
- `Female`: 361 (46.5%)
- `Decline to Answer`: 1 (0.1%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 776 | 2022.00 | 0.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 |
| Amcas_ID | 776 | 14998972.13 | 373144.02 | 12950085.00 | 14866516.00 | 15063869.00 | 15242694.00 | 15499135.00 |
| Age | 743 | 23.83 | 7.67 | 1.00 | 19.00 | 23.00 | 28.00 | 59.00 |

### 2023 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_ID | int64 | 401 | 0.0% |
| Age | float64 | 53 | 4.1% |
| Gender | object | 4 | 4.1% |
| yn | object | 1 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2023
  Amcas_ID: 13278986
  Age: 26.0
  Gender: Woman
  yn: Y
Row 2:
  App_Year: 2023
  Amcas_ID: 13767033
  Age: 30.0
  Gender: Man
  yn: Y
Row 3:
  App_Year: 2023
  Amcas_ID: 13767033
  Age: 24.0
  Gender: Woman
  yn: Y
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2023`: 757 (100.0%)

**Gender** (Top 10 values):
- `Man`: 384 (50.7%)
- `Woman`: 333 (44.0%)
- `Another Gender Identity`: 6 (0.8%)
- `Decline to Answer`: 3 (0.4%)

**yn** (Top 10 values):
- `Y`: 757 (100.0%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 757 | 2023.00 | 0.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 |
| Amcas_ID | 757 | 15209986.75 | 392264.46 | 13278986.00 | 15039509.00 | 15273506.00 | 15477852.00 | 15758293.00 |
| Age | 726 | 23.79 | 8.20 | 1.00 | 19.00 | 23.00 | 28.00 | 60.00 |

### 2024 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_ID | int64 | 613 | 0.0% |
| Age | float64 | 49 | 5.6% |
| Gender | object | 4 | 5.6% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2024
  Amcas_ID: 13149516
  Age: 38.0
  Gender: Woman
Row 2:
  App_Year: 2024
  Amcas_ID: 13149516
  Age: 34.0
  Gender: Woman
Row 3:
  App_Year: 2024
  Amcas_ID: 13573284
  Age: 31.0
  Gender: Woman
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2024`: 1,077 (100.0%)

**Age** (Top 10 values):
- `20.0`: 75 (7.0%)
- `21.0`: 67 (6.2%)
- `24.0`: 62 (5.8%)
- `19.0`: 61 (5.7%)
- `18.0`: 61 (5.7%)
- `25.0`: 57 (5.3%)
- `17.0`: 55 (5.1%)
- `26.0`: 52 (4.8%)
- `27.0`: 46 (4.3%)
- `22.0`: 45 (4.2%)

**Gender** (Top 10 values):
- `Man`: 554 (51.4%)
- `Woman`: 457 (42.4%)
- `Another Gender Identity`: 5 (0.5%)
- `Decline to Answer`: 1 (0.1%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 1077 | 2024.00 | 0.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 |
| Amcas_ID | 1077 | 15461694.79 | 434360.83 | 13149516.00 | 15281868.00 | 15519447.00 | 15757337.00 | 16091417.00 |
| Age | 1017 | 22.80 | 7.67 | 1.00 | 18.00 | 22.00 | 27.00 | 54.00 |

### Schema Consistency Across Years

| Column | 2022 | 2023 | 2024 | Notes |
|--------|------|------|------|-------|
| Age | ✓ | ✓ | ✓ |  |
| Amcas_ID | ✓ | ✓ | ✓ |  |
| App_Year | ✓ | ✓ | ✓ |  |
| Gender | ✓ | ✓ | ✓ |  |
| yn | ✗ | ✓ | ✗ | Added in 2023 |

================================================================================
## FILE: 5. Academic Records.xlsx
================================================================================

### Year-over-Year Overview

| Year | Rows | Columns | Status |
|------|------|---------|--------|
| 2022 | 25,084 | 13 | ✓ OK |
| 2023 | 22,490 | 13 | ✓ OK |
| 2024 | 35,803 | 13 | ✓ OK |

### 2022 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_id | int64 | 437 | 0.0% |
| School_Name | object | 534 | 0.0% |
| Status | object | 7 | 0.0% |
| Academic_Year | int64 | 30 | 0.0% |
| Term | object | 19 | 0.0% |
| class | object | 20 | 0.0% |
| Course_Num | object | 16,224 | 2.9% |
| Course_Name | object | 14,767 | 0.0% |
| Course_Type | object | 13 | 79.8% |
| Credit_Hours | float64 | 62 | 4.2% |
| Semester_Hours | float64 | 33 | 18.2% |
| Status_order | int64 | 7 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2022
  Amcas_id: 12950085
  School_Name: Evergreen Valley College
  Status: HS
  Academic_Year: 2001
  Term: SS
  class: Math
  Course_Num: MATH-11R 202
  Course_Name: Review of Introductory Algebra
  Course_Type: nan
Row 2:
  App_Year: 2022
  Amcas_id: 12950085
  School_Name: Evergreen Valley College
  Status: HS
  Academic_Year: 2002
  Term: S2
  class: Computer Science/Technology
  Course_Num: CIT-010 206
  Course_Name: Intro to Computing/Info Tech
  Course_Type: nan
Row 3:
  App_Year: 2022
  Amcas_id: 12950085
  School_Name: Evergreen Valley College
  Status: HS
  Academic_Year: 2002
  Term: SS
  class: Math
  Course_Num: MATH-013 204 I
  Course_Name: Intermediate Algebra
  Course_Type: nan
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2022`: 25,084 (100.0%)

**Status** (Top 10 values):
- `FR`: 6,444 (25.7%)
- `SO`: 5,265 (21.0%)
- `SR`: 5,192 (20.7%)
- `JR`: 5,183 (20.7%)
- `GR`: 1,311 (5.2%)
- `PB`: 1,060 (4.2%)
- `HS`: 629 (2.5%)

**Academic_Year** (Top 10 values):
- `2018`: 4,801 (19.1%)
- `2017`: 4,626 (18.4%)
- `2019`: 3,902 (15.6%)
- `2016`: 3,630 (14.5%)
- `2020`: 2,433 (9.7%)
- `2015`: 1,972 (7.9%)
- `2014`: 1,209 (4.8%)
- `2013`: 676 (2.7%)
- `2021`: 436 (1.7%)
- `2012`: 423 (1.7%)

**Term** (Top 10 values):
- `S1`: 9,217 (36.7%)
- `S2`: 7,749 (30.9%)
- `Q1`: 1,807 (7.2%)
- `Q3`: 1,554 (6.2%)
- `Q2`: 1,542 (6.1%)
- `SS`: 1,323 (5.3%)
- `QS`: 428 (1.7%)
- `T1`: 351 (1.4%)
- `41`: 310 (1.2%)
- `T2`: 284 (1.1%)

**class** (Top 10 values):
- `Biology`: 6,088 (24.3%)
- `Chemistry`: 4,050 (16.1%)
- `Behavioral & Social Sciences`: 2,467 (9.8%)
- `Math`: 1,720 (6.9%)
- `Health Sciences`: 1,546 (6.2%)
- `Physics`: 1,516 (6.0%)
- `English Language & Literature`: 1,278 (5.1%)
- `Other`: 1,059 (4.2%)
- `Foreign Languages & Literature`: 1,007 (4.0%)
- `Fine Arts`: 744 (3.0%)

**Course_Type** (Top 10 values):
- `Pass/Fail (PF)`: 1,777 (7.1%)
- `Advance Placement (AP)`: 1,400 (5.6%)
- `Honors (H)`: 647 (2.6%)
- `Current/Future (CC)`: 497 (2.0%)
- `Repeat (R)`: 243 (1.0%)
- `Withdrawal (W)`: 230 (0.9%)
- `Exempt (EX)`: 127 (0.5%)
- `Intl Baccalaureate (IB)`: 82 (0.3%)
- `Audit (AU)`: 23 (0.1%)
- `Deferred Grade (DG)`: 20 (0.1%)

**Semester_Hours** (Top 10 values):
- `3.0`: 7,488 (29.9%)
- `4.0`: 4,848 (19.3%)
- `2.7`: 2,343 (9.3%)
- `1.0`: 1,849 (7.4%)
- `2.0`: 1,650 (6.6%)
- `3.3`: 891 (3.6%)
- `5.0`: 440 (1.8%)
- `1.3`: 241 (1.0%)
- `0.7`: 178 (0.7%)
- `3.5`: 125 (0.5%)

**Status_order** (Top 10 values):
- `2`: 6,444 (25.7%)
- `3`: 5,265 (21.0%)
- `5`: 5,192 (20.7%)
- `4`: 5,183 (20.7%)
- `8`: 1,311 (5.2%)
- `6`: 1,060 (4.2%)
- `1`: 629 (2.5%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 25084 | 2022.00 | 0.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 |
| Amcas_id | 25084 | 14992163.39 | 385663.56 | 12950085.00 | 14865618.00 | 15050045.00 | 15234730.00 | 15499135.00 |
| Academic_Year | 25084 | 2016.84 | 3.06 | 1979.00 | 2016.00 | 2017.00 | 2019.00 | 2022.00 |
| Credit_Hours | 24026 | 3.41 | 6.65 | 0.00 | 2.00 | 3.00 | 4.00 | 300.00 |
| Semester_Hours | 20515 | 2.97 | 0.99 | 0.50 | 2.70 | 3.00 | 4.00 | 15.00 |
| Status_order | 25084 | 3.70 | 1.61 | 1.00 | 2.00 | 4.00 | 5.00 | 8.00 |

### 2023 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_id | int64 | 401 | 0.0% |
| School_Name | object | 480 | 0.0% |
| Status | object | 7 | 0.0% |
| Academic_Year | int64 | 29 | 0.0% |
| Term | object | 21 | 0.0% |
| class | object | 20 | 0.0% |
| Course_Num | object | 14,344 | 2.3% |
| Course_Name | object | 13,373 | 0.0% |
| Course_Type | object | 14 | 79.9% |
| Credit_Hours | float64 | 59 | 3.8% |
| Semester_Hours | float64 | 35 | 18.4% |
| Status_order | int64 | 7 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2023
  Amcas_id: 13278986
  School_Name: University of California-Los Angeles
  Status: FR
  Academic_Year: 2008
  Term: Q1
  class: Chemistry
  Course_Num: CHEM 14A
  Course_Name: EQUILBR & ACIDS & BASES
  Course_Type: nan
Row 2:
  App_Year: 2023
  Amcas_id: 13278986
  School_Name: University of California-Los Angeles
  Status: FR
  Academic_Year: 2008
  Term: Q1
  class: History
  Course_Num: HIST 1C
  Course_Name: WESTERN CIVILIZATION
  Course_Type: nan
Row 3:
  App_Year: 2023
  Amcas_id: 13278986
  School_Name: University of California-Los Angeles
  Status: FR
  Academic_Year: 2008
  Term: Q1
  class: Math
  Course_Num: MATH 3A
  Course_Name: CALC LIFE SCI STDT
  Course_Type: Withdrawal (W)
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2023`: 22,490 (100.0%)

**Status** (Top 10 values):
- `FR`: 6,093 (27.1%)
- `SO`: 4,904 (21.8%)
- `SR`: 4,732 (21.0%)
- `JR`: 4,582 (20.4%)
- `GR`: 986 (4.4%)
- `PB`: 826 (3.7%)
- `HS`: 367 (1.6%)

**Academic_Year** (Top 10 values):
- `2019`: 4,086 (18.2%)
- `2018`: 4,056 (18.0%)
- `2020`: 3,536 (15.7%)
- `2017`: 3,198 (14.2%)
- `2021`: 2,157 (9.6%)
- `2016`: 1,733 (7.7%)
- `2015`: 1,099 (4.9%)
- `2014`: 754 (3.4%)
- `2013`: 464 (2.1%)
- `2022`: 337 (1.5%)

**Term** (Top 10 values):
- `S1`: 8,321 (37.0%)
- `S2`: 6,798 (30.2%)
- `Q1`: 1,568 (7.0%)
- `Q2`: 1,319 (5.9%)
- `Q3`: 1,251 (5.6%)
- `SS`: 1,178 (5.2%)
- `T1`: 493 (2.2%)
- `QS`: 413 (1.8%)
- `T2`: 413 (1.8%)
- `41`: 235 (1.0%)

**class** (Top 10 values):
- `Biology`: 5,585 (24.8%)
- `Chemistry`: 3,653 (16.2%)
- `Behavioral & Social Sciences`: 2,078 (9.2%)
- `Math`: 1,514 (6.7%)
- `Physics`: 1,342 (6.0%)
- `Health Sciences`: 1,332 (5.9%)
- `English Language & Literature`: 1,165 (5.2%)
- `Other`: 1,160 (5.2%)
- `Foreign Languages & Literature`: 1,063 (4.7%)
- `Fine Arts`: 681 (3.0%)

**Course_Type** (Top 10 values):
- `Pass/Fail (PF)`: 1,651 (7.3%)
- `Advance Placement (AP)`: 1,291 (5.7%)
- `Honors (H)`: 411 (1.8%)
- `Current/Future (CC)`: 388 (1.7%)
- `Repeat (R)`: 258 (1.1%)
- `Withdrawal (W)`: 215 (1.0%)
- `Intl Baccalaureate (IB)`: 106 (0.5%)
- `Exempt (EX)`: 100 (0.4%)
- `Military Credit (MC)`: 43 (0.2%)
- `Incomplete (I)`: 17 (0.1%)

**Semester_Hours** (Top 10 values):
- `3.0`: 6,965 (31.0%)
- `4.0`: 4,237 (18.8%)
- `2.7`: 1,710 (7.6%)
- `1.0`: 1,704 (7.6%)
- `2.0`: 1,570 (7.0%)
- `3.3`: 973 (4.3%)
- `5.0`: 475 (2.1%)
- `1.3`: 199 (0.9%)
- `0.7`: 136 (0.6%)
- `3.5`: 85 (0.4%)

**Status_order** (Top 10 values):
- `2`: 6,093 (27.1%)
- `3`: 4,904 (21.8%)
- `5`: 4,732 (21.0%)
- `4`: 4,582 (20.4%)
- `8`: 986 (4.4%)
- `6`: 826 (3.7%)
- `1`: 367 (1.6%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 22490 | 2023.00 | 0.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 |
| Amcas_id | 22490 | 15190453.29 | 405164.14 | 13278986.00 | 15013472.00 | 15263455.00 | 15466767.00 | 15758293.00 |
| Academic_Year | 22490 | 2017.74 | 2.87 | 1995.00 | 2017.00 | 2018.00 | 2020.00 | 2023.00 |
| Credit_Hours | 21644 | 3.88 | 9.10 | 0.00 | 2.00 | 3.00 | 4.00 | 300.00 |
| Semester_Hours | 18361 | 2.98 | 0.99 | 0.40 | 2.70 | 3.00 | 4.00 | 12.00 |
| Status_order | 22490 | 3.65 | 1.54 | 1.00 | 2.00 | 3.00 | 5.00 | 8.00 |

### 2024 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_id | int64 | 613 | 0.0% |
| School_Name | object | 609 | 0.0% |
| Status | object | 7 | 0.0% |
| Academic_Year | int64 | 25 | 0.0% |
| Term | object | 19 | 0.0% |
| class | object | 20 | 0.0% |
| Course_Num | object | 20,401 | 2.7% |
| Course_Name | object | 19,064 | 0.0% |
| Course_Type | object | 14 | 78.7% |
| Credit_Hours | float64 | 67 | 2.8% |
| Semester_Hours | float64 | 43 | 18.6% |
| Status_order | int64 | 7 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2024
  Amcas_id: 13149516
  School_Name: University of California-Santa Barbara
  Status: FR
  Academic_Year: 2005
  Term: Q1
  class: Chemistry
  Course_Num: CHEM 1A
  Course_Name: GEN CHEM
  Course_Type: nan
Row 2:
  App_Year: 2024
  Amcas_id: 13149516
  School_Name: University of California-Santa Barbara
  Status: FR
  Academic_Year: 2005
  Term: Q1
  class: Chemistry
  Course_Num: CHEM 1AL
  Course_Name: GEN. CHEMISTRY LABS
  Course_Type: nan
Row 3:
  App_Year: 2024
  Amcas_id: 13149516
  School_Name: University of California-Santa Barbara
  Status: FR
  Academic_Year: 2005
  Term: Q1
  class: Engineering
  Course_Num: CMPSC5JA
  Course_Name: INTRO COMP PROG ORG
  Course_Type: nan
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2024`: 35,803 (100.0%)

**Status** (Top 10 values):
- `FR`: 9,501 (26.5%)
- `SO`: 7,644 (21.4%)
- `SR`: 7,411 (20.7%)
- `JR`: 7,157 (20.0%)
- `GR`: 1,853 (5.2%)
- `PB`: 1,171 (3.3%)
- `HS`: 1,066 (3.0%)

**Academic_Year** (Top 10 values):
- `2020`: 7,144 (20.0%)
- `2019`: 6,745 (18.8%)
- `2021`: 5,439 (15.2%)
- `2018`: 4,985 (13.9%)
- `2022`: 3,177 (8.9%)
- `2017`: 2,769 (7.7%)
- `2016`: 1,770 (4.9%)
- `2015`: 1,038 (2.9%)
- `2014`: 659 (1.8%)
- `2023`: 578 (1.6%)

**Term** (Top 10 values):
- `S1`: 12,529 (35.0%)
- `S2`: 10,331 (28.9%)
- `Q1`: 3,039 (8.5%)
- `Q2`: 2,461 (6.9%)
- `Q3`: 2,321 (6.5%)
- `SS`: 2,137 (6.0%)
- `QS`: 611 (1.7%)
- `T1`: 537 (1.5%)
- `41`: 507 (1.4%)
- `42`: 430 (1.2%)

**class** (Top 10 values):
- `Biology`: 8,764 (24.5%)
- `Chemistry`: 5,926 (16.6%)
- `Behavioral & Social Sciences`: 3,361 (9.4%)
- `Math`: 2,451 (6.8%)
- `Health Sciences`: 2,265 (6.3%)
- `Physics`: 2,208 (6.2%)
- `English Language & Literature`: 1,808 (5.0%)
- `Other`: 1,682 (4.7%)
- `Foreign Languages & Literature`: 1,519 (4.2%)
- `Fine Arts`: 1,128 (3.2%)

**Course_Type** (Top 10 values):
- `Pass/Fail (PF)`: 2,738 (7.6%)
- `Advance Placement (AP)`: 2,235 (6.2%)
- `Honors (H)`: 888 (2.5%)
- `Current/Future (CC)`: 674 (1.9%)
- `Repeat (R)`: 373 (1.0%)
- `Withdrawal (W)`: 313 (0.9%)
- `Exempt (EX)`: 206 (0.6%)
- `Intl Baccalaureate (IB)`: 119 (0.3%)
- `Deferred Grade (DG)`: 34 (0.1%)
- `Audit (AU)`: 15 (0.0%)

**Semester_Hours** (Top 10 values):
- `3.0`: 11,176 (31.2%)
- `4.0`: 5,872 (16.4%)
- `2.7`: 3,407 (9.5%)
- `1.0`: 2,728 (7.6%)
- `2.0`: 2,432 (6.8%)
- `3.3`: 1,626 (4.5%)
- `5.0`: 677 (1.9%)
- `1.3`: 342 (1.0%)
- `0.7`: 286 (0.8%)
- `1.5`: 103 (0.3%)

**Status_order** (Top 10 values):
- `2`: 9,501 (26.5%)
- `3`: 7,644 (21.4%)
- `5`: 7,411 (20.7%)
- `4`: 7,157 (20.0%)
- `8`: 1,853 (5.2%)
- `6`: 1,171 (3.3%)
- `1`: 1,066 (3.0%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 35803 | 2024.00 | 0.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 |
| Amcas_id | 35803 | 15433420.18 | 442373.05 | 13149516.00 | 15250571.00 | 15516570.00 | 15739724.00 | 16091417.00 |
| Academic_Year | 35803 | 2018.83 | 2.64 | 2000.00 | 2018.00 | 2019.00 | 2021.00 | 2024.00 |
| Credit_Hours | 34795 | 3.65 | 8.06 | 0.00 | 2.00 | 3.00 | 4.00 | 100.00 |
| Semester_Hours | 29139 | 2.92 | 0.98 | 0.00 | 2.70 | 3.00 | 3.30 | 16.00 |
| Status_order | 35803 | 3.65 | 1.61 | 1.00 | 2.00 | 3.00 | 5.00 | 8.00 |

### Schema Consistency Across Years

| Column | 2022 | 2023 | 2024 | Notes |
|--------|------|------|------|-------|
| Academic_Year | ✓ | ✓ | ✓ |  |
| Amcas_id | ✓ | ✓ | ✓ |  |
| App_Year | ✓ | ✓ | ✓ |  |
| Course_Name | ✓ | ✓ | ✓ |  |
| Course_Num | ✓ | ✓ | ✓ |  |
| Course_Type | ✓ | ✓ | ✓ |  |
| Credit_Hours | ✓ | ✓ | ✓ |  |
| School_Name | ✓ | ✓ | ✓ |  |
| Semester_Hours | ✓ | ✓ | ✓ |  |
| Status | ✓ | ✓ | ✓ |  |
| Status_order | ✓ | ✓ | ✓ |  |
| Term | ✓ | ✓ | ✓ |  |
| class | ✓ | ✓ | ✓ |  |

================================================================================
## FILE: 6. Experiences.xlsx
================================================================================

### Year-over-Year Overview

| Year | Rows | Columns | Status |
|------|------|---------|--------|
| 2022 | 5,904 | 13 | ✓ OK |
| 2023 | 5,454 | 13 | ✓ OK |
| 2024 | 8,501 | 13 | ✓ OK |

### 2022 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_id | int64 | 437 | 0.0% |
| Exp_Type | object | 17 | 0.0% |
| Exp_Name | object | 5,004 | 0.0% |
| Start_Date | int64 | 195 | 0.0% |
| End_Date | float64 | 130 | 9.2% |
| Dates | object | 2,701 | 0.0% |
| Total_Hours | int64 | 757 | 0.0% |
| Org_Name | object | 4,454 | 8.4% |
| Is_Meaningful | object | 2 | 0.0% |
| Exp_Desc | object | 5,887 | 0.3% |
| Meaningful_Desc | object | 1,300 | 78.0% |
| row_number | int64 | 5,904 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2022
  Amcas_id: 12950085
  Exp_Type: Publications
  Exp_Name: First Author Publication: Journal of Pediatrics
  Start_Date: 44075
  End_Date: nan
  Dates: 9/2020
  Total_Hours: 0
  Org_Name: Journal of Pediatrics
  Is_Meaningful: Yes
Row 2:
  App_Year: 2022
  Amcas_id: 12950085
  Exp_Type: Research/Lab
  Exp_Name: Stanford Clinical and Translational Research Program
  Start_Date: 43191
  End_Date: 44774.0
  Dates: 4/2018 - 8/2022
  Total_Hours: 7000
  Org_Name: Stanford - Clinical and Translational Research Program
  Is_Meaningful: Yes
Row 3:
  App_Year: 2022
  Amcas_id: 12950085
  Exp_Type: Teaching/Tutoring/Teaching Assistant
  Exp_Name: Evergreen Valley College: Tutor
  Start_Date: 41153
  End_Date: 43252.0
  Dates: 9/2012 - 6/2018
  Total_Hours: 1000
  Org_Name: Evergreen Valley College
  Is_Meaningful: Yes
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2022`: 5,904 (100.0%)

**Exp_Type** (Top 10 values):
- `Community Service/Volunteer - Medical/Clinical`: 799 (13.5%)
- `Community Service/Volunteer - Not Medical/Clinical`: 763 (12.9%)
- `Research/Lab`: 726 (12.3%)
- `Physician Shadowing/Clinical Observation`: 497 (8.4%)
- `Paid Employment - Medical/Clinical`: 479 (8.1%)
- `Paid Employment - Not Medical/Clinical`: 454 (7.7%)
- `Leadership - Not Listed Elsewhere`: 429 (7.3%)
- `Teaching/Tutoring/Teaching Assistant`: 360 (6.1%)
- `Extracurricular Activities`: 352 (6.0%)
- `Hobbies`: 249 (4.2%)

**Is_Meaningful** (Top 10 values):
- `No`: 4,604 (78.0%)
- `Yes`: 1,300 (22.0%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 5904 | 2022.00 | 0.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 |
| Amcas_id | 5904 | 15008135.03 | 364144.29 | 12950085.00 | 14869074.00 | 15057778.00 | 15243303.00 | 15499135.00 |
| Start_Date | 5904 | 43148.61 | 1039.78 | 25051.00 | 42736.00 | 43313.00 | 43831.00 | 44409.00 |
| End_Date | 5362 | 43868.84 | 736.70 | 36100.00 | 43466.00 | 43952.00 | 44378.00 | 44774.00 |
| Total_Hours | 5904 | 745.76 | 3495.26 | 0.00 | 72.00 | 200.00 | 600.00 | 99999.00 |
| row_number | 5904 | 86439.39 | 48634.08 | 17.00 | 44117.25 | 88285.50 | 130044.75 | 166507.00 |

### 2023 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_id | int64 | 401 | 0.0% |
| Exp_Type | object | 18 | 0.0% |
| Exp_Name | object | 4,661 | 0.0% |
| Start_Date | int64 | 194 | 0.0% |
| End_Date | float64 | 122 | 9.8% |
| Dates | object | 2,220 | 0.0% |
| Total_Hours | int64 | 735 | 0.0% |
| Org_Name | object | 4,110 | 6.2% |
| Is_Meaningful | object | 2 | 0.0% |
| Exp_Desc | object | 5,451 | 0.1% |
| Meaningful_Desc | object | 1,196 | 78.1% |
| row_number | int64 | 5,454 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2023
  Amcas_id: 13278986
  Exp_Type: Research/Lab
  Exp_Name: Research Specialist
  Start_Date: 43009
  End_Date: 44713.0
  Dates: 10/2017 - 6/2022
  Total_Hours: 8000
  Org_Name: UCLA School of Medicine, Hematology/Oncology
  Is_Meaningful: Yes
Row 2:
  App_Year: 2023
  Amcas_id: 13278986
  Exp_Type: Research/Lab
  Exp_Name: Student Researcher
  Start_Date: 42217
  End_Date: 42614.0
  Dates: 8/2015 - 9/2016
  Total_Hours: 1100
  Org_Name: UCLA AIDS Institute
  Is_Meaningful: Yes
Row 3:
  App_Year: 2023
  Amcas_id: 13278986
  Exp_Type: Community Service/Volunteer - Not Medical/Clinical
  Exp_Name: Co-Founder of Mentoring and Health Education Program
  Start_Date: 41000
  End_Date: 41456.0
  Dates: 4/2012 - 7/2013
  Total_Hours: 400
  Org_Name: Mentoring and Health Education Program
  Is_Meaningful: Yes
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2023`: 5,454 (100.0%)

**Exp_Type** (Top 10 values):
- `Community Service/Volunteer - Not Medical/Clinical`: 696 (12.8%)
- `Research/Lab`: 683 (12.5%)
- `Community Service/Volunteer - Medical/Clinical`: 628 (11.5%)
- `Paid Employment - Medical/Clinical`: 622 (11.4%)
- `Physician Shadowing/Clinical Observation`: 420 (7.7%)
- `Leadership - Not Listed Elsewhere`: 407 (7.5%)
- `Paid Employment - Not Medical/Clinical`: 381 (7.0%)
- `Extracurricular Activities`: 340 (6.2%)
- `Teaching/Tutoring/Teaching Assistant`: 307 (5.6%)
- `Honors/Awards/Recognitions`: 274 (5.0%)

**Is_Meaningful** (Top 10 values):
- `No`: 4,258 (78.1%)
- `Yes`: 1,196 (21.9%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 5454 | 2023.00 | 0.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 |
| Amcas_id | 5454 | 15214529.83 | 379577.94 | 13278986.00 | 15033897.00 | 15271905.00 | 15477868.00 | 15758293.00 |
| Start_Date | 5454 | 43522.04 | 996.86 | 32874.00 | 43101.00 | 43678.00 | 44197.00 | 44774.00 |
| End_Date | 4920 | 44133.39 | 673.21 | 39722.00 | 43800.00 | 44348.00 | 44682.00 | 44805.00 |
| Total_Hours | 5454 | 701.67 | 3768.75 | 0.00 | 60.00 | 180.00 | 500.00 | 99999.00 |
| row_number | 5454 | 81312.12 | 45798.93 | 140.00 | 41229.25 | 82865.50 | 122708.00 | 157166.00 |

### 2024 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_id | int64 | 613 | 0.0% |
| Exp_Type | object | 19 | 0.0% |
| Exp_Name | object | 7,118 | 0.0% |
| Start_Date | int64 | 219 | 0.0% |
| End_Date | float64 | 134 | 9.7% |
| Dates | object | 2,975 | 0.0% |
| Total_Hours | int64 | 923 | 0.0% |
| Org_Name | object | 6,244 | 7.7% |
| Is_Meaningful | object | 2 | 0.0% |
| Exp_Desc | object | 8,493 | 0.1% |
| Meaningful_Desc | object | 1,824 | 78.5% |
| row_number | int64 | 8,501 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2024
  Amcas_id: 13149516
  Exp_Type: Physician Shadowing/Clinical Observation
  Exp_Name: Intensive Critical Care Unit shadowing
  Start_Date: 44986
  End_Date: 45078.0
  Dates: 3/2023 - 6/2023
  Total_Hours: 64
  Org_Name: Brooke Army Medical Center
  Is_Meaningful: Yes
Row 2:
  App_Year: 2024
  Amcas_id: 13149516
  Exp_Type: Military Service
  Exp_Name: Department Chief, Organ Support
  Start_Date: 44682
  End_Date: 45047.0
  Dates: 5/2022 - 5/2023
  Total_Hours: 2000
  Org_Name: U.S. Army Institute of Surgical Research
  Is_Meaningful: Yes
Row 3:
  App_Year: 2024
  Amcas_id: 13149516
  Exp_Type: Research/Lab
  Exp_Name: University Scientific Research
  Start_Date: 39873
  End_Date: 43252.0
  Dates: 3/2009 - 7/2010 (960 hrs), 9/2011 - 6/2018 (14560 hrs)
  Total_Hours: 15520
  Org_Name: University of California, Riverside
  Is_Meaningful: Yes
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2024`: 8,501 (100.0%)

**Exp_Type** (Top 10 values):
- `Community Service/Volunteer - Not Medical/Clinical`: 1,136 (13.4%)
- `Community Service/Volunteer - Medical/Clinical`: 1,058 (12.4%)
- `Research/Lab`: 1,023 (12.0%)
- `Paid Employment - Medical/Clinical`: 861 (10.1%)
- `Physician Shadowing/Clinical Observation`: 655 (7.7%)
- `Leadership - Not Listed Elsewhere`: 618 (7.3%)
- `Paid Employment - Not Medical/Clinical`: 588 (6.9%)
- `Teaching/Tutoring/Teaching Assistant`: 486 (5.7%)
- `Extracurricular Activities`: 432 (5.1%)
- `Honors/Awards/Recognitions`: 399 (4.7%)

**Is_Meaningful** (Top 10 values):
- `No`: 6,677 (78.5%)
- `Yes`: 1,824 (21.5%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 8501 | 2024.00 | 0.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 |
| Amcas_id | 8501 | 15460878.69 | 407453.26 | 13149516.00 | 15277361.00 | 15518696.00 | 15750077.00 | 16091417.00 |
| Start_Date | 8501 | 43859.03 | 1058.91 | 35065.00 | 43466.00 | 44044.00 | 44562.00 | 45139.00 |
| End_Date | 7680 | 44529.67 | 684.37 | 36831.00 | 44256.00 | 44713.00 | 45047.00 | 45200.00 |
| Total_Hours | 8501 | 663.88 | 3139.65 | 0.00 | 70.00 | 200.00 | 515.00 | 99999.00 |
| row_number | 8501 | 90039.97 | 49679.02 | 14.00 | 46351.00 | 93521.00 | 133154.00 | 171648.00 |

### Schema Consistency Across Years

| Column | 2022 | 2023 | 2024 | Notes |
|--------|------|------|------|-------|
| Amcas_id | ✓ | ✓ | ✓ |  |
| App_Year | ✓ | ✓ | ✓ |  |
| Dates | ✓ | ✓ | ✓ |  |
| End_Date | ✓ | ✓ | ✓ |  |
| Exp_Desc | ✓ | ✓ | ✓ |  |
| Exp_Name | ✓ | ✓ | ✓ |  |
| Exp_Type | ✓ | ✓ | ✓ |  |
| Is_Meaningful | ✓ | ✓ | ✓ |  |
| Meaningful_Desc | ✓ | ✓ | ✓ |  |
| Org_Name | ✓ | ✓ | ✓ |  |
| Start_Date | ✓ | ✓ | ✓ |  |
| Total_Hours | ✓ | ✓ | ✓ |  |
| row_number | ✓ | ✓ | ✓ |  |

================================================================================
## FILE: 9. Personal Statement.xlsx
================================================================================

### Year-over-Year Overview

| Year | Rows | Columns | Status |
|------|------|---------|--------|
| 2022 | 437 | 3 | ✓ OK |
| 2023 | 401 | 3 | ✓ OK |
| 2024 | 613 | 3 | ✓ OK |

### 2022 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| app_year | int64 | 1 | 0.0% |
| amcas_id | int64 | 437 | 0.0% |
| personal_statement | object | 437 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  app_year: 2022
  amcas_id: 12950085
  personal_statement: While waiting for our turn to speak with the young girl’s family, I reviewed the important sections of the consent form with my teammate, Sandy. As this was her first time coordinating a complex clinical trial, she was finding it difficult to approach families for consent. When it was finally our turn, I was initially worried that after hours of pre-op testing, the family would not have the energy to listen and consent to our study. However, when I greeted the family, I found them welcoming and focused on doing what was best for their child. I introduced myself and my colleague and expressed my gratitude for the opportunity to discuss our study. They explained to us the challenges of raising a child with congenital heart disease and how worried and powerless they felt about their child’s upcoming surgery. I expressed admiration for their courage and resilience and reassured them that many parents feel this lack of control when they entrust their child to an expert surgical team.  Only then did I introduce our study and explain how it could benefit children like their daughter in the future. I noticed a change in their demeanor as they expressed eagerness to participate in the study, hopefully providing them with some agency under these difficult circumstances. Sandy followed up with the consent form and afterwards I emphasized how important it was to take the time to make the interpersonal connection. Seeing how thrilled she was with her first successful consent reminded me of all the mentors that helped me along my own path.

When I graduated from UC Berkeley, I had dreams of immediately taking the next step towards becoming a physician. However, my parents needed my financial support and without it my two younger brothers would not have been able to attend college. I willingly put my dreams on hold and spent the next six years working to support my family. During this time, my English professor provided me with an opportunity as a teaching assistant for her college courses and guided me towards tutoring as a means to provide for my family. Under her mentorship, I designed lesson plans, gave several lectures and provided 1:1 tutoring for her students. Because many of her students were immigrants they found English intimidating, and I saw firsthand the importance of tailoring education to each individual’s learning style. I applied these concepts when tutoring my own students and found that, in time, I fostered stronger relationships. Many of my students looked to me as a mentor as they navigated through their early academic careers. It was gratifying to watch them succeed, and graduate to bigger and better things. Despite a busy work schedule, I also used this time to confirm my passion for medicine, devoting most of my free time to shadowing a cardiologist at a local hospital. 

After my brothers graduated from college, I finally returned to pursuing a career in medicine full-time. When a research coordinator position in cardiology became available, I was fortunate to join Stanford’s Clinical and Translational Research Program. This opportunity allowed me to be involved in several clinical trials, including a multi-center NIH study aimed at discovering the genetic factors underlying congenital heart defects. I worked closely with these patients and their families, from their initial pre-operative visit through to their hospital discharge, witnessing state-of-the-art medical care and the importance of compassionate doctor-patient interactions. Building on the communication skills I honed as a tutor, I developed meaningful relationships with these families and had the privilege of following their journey to recovery. Their resilience was inspiring, particularly those children with genetic syndromes in addition to their already complex congenital heart disease, and motivated me to learn more about their conditions and outcomes.

Under the mentorship of Dr. Doff McElhinney, the program’s director, I designed and completed my own clinical research project on the surgical outcomes for patients with Alagille syndrome and complex pulmonary artery disease. Through this project, I developed many research skills and collaborated with prominent experts in this field. I learned to be impartial and critical in my data analysis and concise and clear in my writing. While this project was challenging, my motivation only increased as I worked towards completion, realizing that I was in a small way contributing to our knowledge with a first-author publication in the Journal of Pediatric. This experience, and Dr. McElhinney’s mentorship, solidified my determination to become a physician and opened my eyes to the power of clinical research to touch the lives of real patients. 

My mentors have allowed me to advance along my career path and confirm my passion for medicine. They have also inspired me to create a similar impact with my own mentees. In addition, my time at Stanford has provided me with a deep appreciation for the medical field and the impact of clinical research on patient care. I aspire to be like the compassionate physicians whom I work with daily and I hope to be given the opportunity to mentor the next generation of young doctors-to-be, as I have been mentored.
Row 2:
  app_year: 2022
  amcas_id: 13099483
  personal_statement: I was born and raised in Shirati, a small village in the East African nation of Tanzania. When I was ten, we lived in nearby Roche, a much smaller remote village without a health clinic. The village saw only a car or two a day, an event so special that all of us children would run to the roadside to watch. Bicycles were common, and a few were modified with a strapped-on wooden chair to create makeshift “bicycle ambulances.” These were the only means to transport the most critically ill patients to Shirati Hospital two hours away. The bicycle ambulance operators had no medical training and the patients rarely made it to the hospital alive.

Over the years, I imagined how the bicycle ambulance scenario could be different if there were better access to health care in Roche. While attending Colby College, I volunteered as an interpreter at Dr. Esther Kawira’s medical clinic in Sota village near Shirati. This was the first time I actively participated in patient care. I particularly remember a seven-year-old girl who presented with a large facial tumor. Dr. Kawira explained that it was Burkitt lymphoma, one of the fastest-growing tumors that is also very responsive to chemotherapy. After only 48 hours of chemotherapy, the massive facial disfiguring tumor was drastically reduced, and her face looked normal. Even more reassuring, the chemotherapy drugs used to treat her were affordable. However, not all tumors are as responsive to treatment as Burkitt lymphoma. It is the successes in treating cancers like Burkitt lymphoma and the challenges in treating other cancers that motivated me to pursue a Ph.D. in biomedical research.

My Ph.D. research focused on investigating the mechanisms underlying the development of an adult blood cancer called myelodysplastic syndrome (MDS). MDS patients tend to develop chemotherapy-resistant acute myeloid leukemia. As I probed deeper into the genetics of MDS in my laboratory work, I looked for opportunities to engage in direct patient contact to learn how I could better tailor my research to fill the gaps in cancer treatment. Therefore, I included four physician-scientists in my doctoral thesis committee, including my mentor Dr. Walter. My thesis committee and lab provided an environment for rich clinically relevant discussions that inspired me to perform research that could be translated to the bedside to benefit MDS patients. In addition to this training environment, a two-year Markey Pathway Fellowship Award during my Ph.D. training played a significant role in my decision to pursue a medical degree.

The Markey Pathway introduced me to the scientific aspects of human disease through a series of disease-oriented lectures not generally covered in graduate courses. The Pathway was unique in that it also provided an opportunity for me to directly interact with clinicians, patients, and families during a clinical mentorship. I learned first-hand that successful patient care involves communication between the clinical care team, patients, patient families, and researchers. During a visit with an Alzheimer’s patient, the physician had to rely on the husband’s observations at home to assess symptoms and develop a care plan. I also witnessed challenges that arise when priorities of a patient and physician are not aligned. During a visit with a patient that had diabetes, the doctor’s immediate concern was managing the blood sugar levels, but when I asked the patient, she was most worried about her deteriorating eyesight. While my research training taught me to listen to the data, the Markey Pathway experience highlighted the importance of recognizing the patient’s needs when communicating with patients and families. The Markey Pathway experience solidified my desire to become a physician and pursue a career where I could care for patients with a disease while running a laboratory focused on understanding pathobiology to improve outcomes. 

I am certain that my passion for medicine, clinical exposure to date, and basic science experience have prepared me for pursuing a physician-scientist career. As a physician-scientist, I will be able to engage with all essential stakeholders in a patient’s care and have a unique perspective to improve patient outcomes by balancing both clinical and the research information. As I am surrounded by ambulances, laboratories, and health care facilities at Washington University, I am reminded of the bicycle ambulances back home. My dream is to improve patient outcomes through clinical care and research. Obtaining a medical degree is a key next step to achieve my goal of serving patients and advancing science.
Row 3:
  app_year: 2022
  amcas_id: 13489485
  personal_statement: Sam Iam was a brilliant young man, but he grew bored easily. The line he drew between use and abuse was thin. We arrived at Tufts University with a similar perspective: naive and sheltered. Most young adults run with the freedom college grants; we chose to fly with ours. Instead of preparing for exams, we were sneaking into bars and witnessing too many sunrises. It was exhilarating and irresponsible, particularly because our studies were involved. First, it was academic probation I, and then academic probation II. My early marks reflect my lackluster effort. Eventually, the idea of wasted potential bothered me. I paddled back to accountability, while Sam sailed further into dangerous waters.

One day, Sam sailed too far. When I saw the police cars blocking the street, I knew I had to call his mother. I sat on the steps outside Sam’s apartment with our friends, watching paramedics through the open front door. We did not have much to say. Before long, we saw them bring our friend out. They struggled to keep his body raised as he swung from side to side in the tarp that held him. I stood there, helpless, with the realization that nothing could be done to bring my friend back.

How could I tell a mother that her son was gone? That phone call to Sam's mother forever changed me. “I am sorry,” I said again and again. The phrase echoed uselessly, but there was nothing left to say. The feeling of helplessness frustrated and overwhelmed me. I realized that while I had turned back to seriously working toward my dream of a medical career, I had watched Sam decline and die in a medical crisis. I knew if Sam had had better access to healthcare -- to facilities that accepted and believed in him, to institutions with proven protocols, to providers that cared for him with continuity -- his outcome could have been different.

In 2015 I applied to medical schools -- energized with a refreshed motivation -- and was rejected. The desire to grow and learn reignited an old hobby: I spent time making clothes. For two years I channeled my creative energy in Milan, learning to plan, pattern, cut, sew, manage a business, please customers, and speak Italian. I traveled with a box full of my designs. Some paid for my work, but I was just as happy to put a shirt on someone’s back if they could not afford it. “They will protect you,” I told them all, referring to the clothes, watching the designs come to life when worn. While designing and starting a business were rewarding, serving a need in my community was even more fulfilling. To this day volunteering at the Olneyville Food Center allows me to contribute to my community by helping lower-income families find healthy food.

Wanting to make a difference beyond fabric and thread, I re-examined the role of a physician through a different lens and took action to educate myself. Sam’s tragedy reinforced my fear of wasted potential, and I realized I needed a plan if a career in medicine was my goal. While I had achieved grades I was proud of with renewed focus, I knew improving my academics was only the first step. I needed to obtain clinical exposure and research experience.

Working as a medical secretary in urgent care taught me how non-emergent complaints are triaged and treated, while primary care taught me the importance of building history. I monitor high-risk patients during my overnight shifts at the ED, documenting their activity and alerting the charge nurse as needed. While researching Alzheimer’s Disease, we conduct trials aimed at halting disease progression. It turns out needing to refocus towards the end of college allowed for invaluable work experience and real-world perspective.

I found myself capable of channeling my ambition and tackling achievable goals. My interest in medicine was sparked by my experience with childhood asthma, school laboratory experiments, and high school science courses, but it took more for it to ignite. Floundering in college and the tragedy of losing my friend was the fuel I needed. The circuitous route that led to this application furthers my resolve to become a physician. As a physician I want to represent those, like my friend Sam, who find difficulty accessing care and end up paying the steepest price - their health or even their lives.
```

#### Categorical Column Distributions

**app_year** (Top 10 values):
- `2022`: 437 (100.0%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| app_year | 437 | 2022.00 | 0.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 |
| amcas_id | 437 | 15011632.22 | 363254.26 | 12950085.00 | 14880945.00 | 15057778.00 | 15243303.00 | 15499135.00 |

### 2023 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| app_year | int64 | 1 | 0.0% |
| amcas_id | int64 | 401 | 0.0% |
| personal_statement | object | 401 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  app_year: 2023
  amcas_id: 13278986
  personal_statement: Tuesday mornings were the highlight of my week at the UCLA AIDS Institute. With a cup of coffee in one hand and my notebook in the other, I was always ready to absorb the discussions that clinicians and scientists held on the advancements of novel therapies for HIV/AIDS during our weekly institute-wide seminars. As clinicians debated the merits of treatments such as HAART and CAR-T, they drew from their experiences in treating patients and their concern for them. Working towards a career in medicine but new to translational research, I found myself reflecting on what it meant to bridge the gap between science and medicine and felt my aspirations for becoming a physician fully crystallize.
 
I was initially drawn to studying HIV because I had seen firsthand how destructive a virus could be. When I was a pre-teen, my dad fell acutely ill from his hepatitis B (HBV) infection, which was endemic to his native country of South Korea. I will always remember how my mom choked back her emotions to explain to me why Appa was in the hospital. Having met someone who had lost her dad to HBV just a year prior, I instinctively braced for the worst and felt my youthful light-heartedness dissipate as I trudged into a premature adulthood. It hurt to learn that if the HBV vaccine had been developed earlier, it might have prevented my dad’s infection. My dad’s doctors were eventually able to control the virus and prescribed a drug that had newly been approved for HBV. Unfortunately, the pill caused harsh side effects in my dad and it would be years until a more tolerable alternative became available. From watching my dad become a fraction of the person he had been before his illness, I learned how critical the prevention of an illness was and how existing treatments had their drawbacks and limits.
 
I entered UCLA determined to learn about the preventative care that could be so pivotal to a person’s life. First as a member, eventually as club president, I volunteered in a community outreach club and served at local health fairs throughout Los Angeles. I joined health professionals to care for patients, many of whom had limited access to medical attention beyond these fairs, and measured blood pressures, explained what to expect during a mammogram and comforted anxious patients as they had their blood drawn. While talking to patients, I often found myself using the same reassuring voice and approachable body language I saw in the physicians working alongside me. At one event, I met a woman and her daughter at the flu vaccine booth and we communicated through a mix of broken English and Spanish. As I explained why annual flu vaccines were beneficial for both her and the community, I noticed that despite nodding along, she was turning away. Recognizing parallels in our immigrant backgrounds and how multigenerational households are more common in these demographics, I asked if they happened to live with any grandparents to which they answered “yes”. Because the elderly are more susceptible to serious illness from the flu, it was safer if everyone in a household were immunized. Instantly, the vaccine that the woman seemed ambivalent towards became her imperative. A potentially lifesaving vaccine was readily available to this family, but if it were not for my cultural sensitivity and respectful persuasion, it might as well not have existed. I decided then that as a physician, one of my highest responsibilities would be to treat patients with an understanding of their backgrounds and unique circumstances.
 
At the fairs, I also met patients who had fallen through the imperfect safety net of preventive health and who, like my dad, were inflicted with the slow burn of an incurable or chronic condition. Even with treatment, some of these conditions could progressively worsen. At the time, I had come to accept this as an unfortunate fact. It was when, at the Institute, I met the physicians who tackled HIV/AIDS at both the bench and bedside that I saw how I would be able to help change this notion. As a physician, I would directly treat patients while simultaneously advancing treatments through research to broaden the possibilities of care for those left with few options. 
 
Today, I conduct translational research at UCLA where I discover and validate novel cancer treatments with the same passion as when I first felt the thrill of being at the frontiers of medicine. The cancer cells I examine under the microscope daily are my domain, and each incremental discovery I make builds a case for the capabilities of modern medicine. I am driven by the clarity with which I can envision myself comforting patients and their families as I combat their cancer cells with an arsenal of clinical knowledge. While my journey towards a medical education has been a long and nontraditional one, the additional courses I took and excelled at through UCLA Extension and the diverse clinical and research experiences I gained have enriched my perspective and equipped me with the skillsets that I will need in my chosen field. As I take the next step towards my medical career, memories of my own family’s experiences and the stories of the patients I’ve had the privilege of meeting over the years keep me committed to my path forward with unwavering conviction.
Row 2:
  app_year: 2023
  amcas_id: 13767033
  personal_statement: During the 2006 FIFA World Cup, my family observed Leo slowly stop yelling “GOLAZO!”. Subsequently, he started jumping and flapping when he was happy or excited. Leo’s developmental regression and repetitive behaviors at two years old were the first warning signs. Since the closest developmental pediatrician had a two-year waiting list, we searched for another who was two hours away but only had a 6-month waiting list. The longer the waitlist to see a developmental pediatrician – the more time Leo would go without preventative therapies. When Leo finally received his diagnosis of Autism Spectrum Disorder (ASD), I could see my father distancing himself as I witnessed how my mother solely carried the burden of having a child with additional needs. During the emotional whirlwind, my parents faced the tribulation of navigating the American healthcare system as Spanish speakers. I could sense my parents’ struggle due to their lack of social support and financial resources. I wanted to lift my parents’ burden while providing agency for my younger brother, who was eight years old and non-verbal. I was determined to find a way to help my younger brother, Leonardo, communicate. Over my two semesters of American Sign Language (ASL), I was able to teach Leo many simple signs such as “please,” “thank you,” “more,” “help,” and “I love you .” To our amazement, ASL bridged the gap in verbal communication. By the end of the year, Leo would not stop asking, “More Cheerios, please!”. This experience, coupled with years of learning how to care for Leo’s unique needs, drives my passion for pursuing a career as a developmental pediatrician. 

When pursuing a career in medicine, I seek to amplify access to healthcare for underserved, minority communities. My parents needed a professional who spoke Spanish, comprehended their culturally-informed perspectives on ASD, and could effectively communicate medical knowledge using a culturally humble approach. Nevertheless, their difficulties stem from systemic inequity that demands a global overhaul across the healthcare system. I contributed to this significant issue by practicing Medical English with Cuban doctors who recently immigrated to the United States. I spent two hours a week for a year building an English medical-specific vocabulary with them as they studied to pass the Step1 exam. Despite their credentials, it disheartened me that language was a high barrier for them to practice in this country where there are Spanish-speaking communities. Moving forward into medical school, I strive to use my Spanish speaking skills and Latinx identity to traverse language and cultural gaps between the medical system and minorities. 

As a queer, non-binary Latinx, I value understanding intersectionality and individuals through their multiple identities. Every Wednesday afternoon, I spent time with 12-year-old Areli – a young Latinx with a single working mother, a recent diagnosis of ASD, and a fierce mistrust towards doctors. Areli can speak English, but with me, she chose to talk in Spanish out of comfort. We worked through math homework, chatted about her crushes, and explored the Mutter Museum. On the brink of puberty, Areli often asked me questions about her changing body, menstruation, sex, gender, and even her attraction toward other girls. Areli showed me how language, cultural humility, and vulnerability could serve us when trying to bridge the most distrustful gaps. In building rapport with Areli, I developed a relationship that allowed me to offer her a new perspective on how seeking medical advice can be safe.

Finally, my passion for medicine comes from a desire to improve the accessibility of research for underserved minority populations. The barriers for minorities in research became more evident as I made my way through posters and presentations at the International Society for Autism Research (INSAR) Annual Meeting in 2018 and 2019. During the conferences, I would my time perusing the demographics of others’ experiments, where I frequently found myself disappointed in the lack of diversity in research. However, as a Clinical Research Assistant at the Center for Autism Research (CAR), I have been able to make an impact on ASD research perceptions in the Latinx community. Telemundo 62 reached out to CAR looking for a Spanish speaker to present our research for their Enfoque segment. I was the only person at my workplace who spoke Spanish. Though apprehensive, I knew this would be an opportunity to make ASD and research a more approachable topic for the Latinx community. 

A career in medicine would allow me to help others, use critical problem-solving, and do what I do best—connect with those who are often misunderstood and neglected. The compassion I gained while raising Leo compelled me to seek experiences that have given me the confidence to become a physician. Mentoring Areli, tutoring Cuban doctors, and working at CAR have reinforced my commitment to becoming a bilingual developmental pediatrician. I intend to plunge headfirst into the medical field, lead by example, and show others how to deliver culturally sensitive care. Ultimately, I hope not just to become a doctor but an advocate and change-maker working towards a more equitable medical system.
Row 3:
  app_year: 2023
  amcas_id: 13769330
  personal_statement: Going to see a doctor was an ordeal for my family. We were on Medicaid and there were a select few clinics who accepted this insurance. My mother could not afford a babysitter, so when one of us needed to go to the doctor all three children went to the doctor. My mother would hold onto my brother with one hand, hold me with the other, and carry the baby in a baby carrier strapped to her chest. My mother spoke very little English, so many things were lost in translation with the pediatricians. I tried to help with the English that I learned in primary school but there is only so much a child can do. The situation was complicated by my older brother’s autism diagnosis. We were already struggling with communication issues, and now there was a nonverbal child with a Spanish speaking mother in a mainly English speaking world just trying to get help for him. But one day my mother met a pediatrician who would unknowingly start me on my path to medicine, Dr. JoAnn Ruiz. She was the first pediatrician that I met who spoke Spanish. As I watched her treat my autistic brother, her soft and quiet interactions with him settled something within me. Dr. Ruiz did more than treat our physical ailments, she provided hope and guidance. Reflecting upon this as I grew older, I realized that I wanted to dedicate my life to pursuing a career as a physician. 
Throughout my college years I noticed there were very few Latinx mentors who worked in medicine. It made navigating pre-med difficult. My situation, that many other first generation Latinx youth experience, made me become self-reliant. That unfortunately made it hard for me to understand when it was time to ask for help, how to ask for help, and how to not feel undeserving of help. I felt as if I was falling behind. As I continued gathering clinical experience I was given the opportunity to shadow a physician. Dr. Jacqueline Olivo was the first Latina physician I ever worked with throughout all of my clinical and volunteering activities. She was not surprised. As Dr. Olivo began to mentor me, she stressed the need to understand oneself and why they wanted to be a doctor. Through reflection I realized that there was more than treating a patient in a clinic setting. A physician is also a mentor and advocate. I saw the need in the Latinx community for more Spanish speaking doctors who identify as Latinx. Anyone can learn Spanish, but that is completely different to understanding the struggles that Latinx people go through when it comes to their health. Dr. Olivo would also go on to introduce me to the most inspiring organization I have ever been part of: The Medical Organization for Latino Advancement.
During MOLA’s 2019 symposium I was overcome with emotion when I saw a room full of Latinx students and professionals. Dr. Pilar Ortega, the president of MOLA, spoke about how lack of representation affects both our health and aspirations. It makes us believe that there is no space for us in a field predominantly populated by people who don’t look like us, or sound like us. But we belong just as much as anyone else. When I had the opportunity to volunteer for them during the COVID pandemic, I saw their message in practice. We wrote letters to advocate towards allowing International Medical graduates to practice medicine during the COVID crisis, we had multiple events to promote masking and vaccination in the Latinx community, I organized virtual interviews with Latinx health professionals so they could discuss how the pandemic was affecting the Latinx community and how history and disparities was affecting that change.
I decided to go back to school to study Public Health, because I wanted to learn how our current health system operated. Everything from where you live, what food is available to you, safety, culture, and how much income you earn greatly affects your health. Through my studies I began to make connections to my experiences and how they have affected me in ways that were out of my control. I heard so many stories about the deterioration of physician/ patient relationships because some doctors just didn’t understand the culture or language of their patients, even when the doctor had good intentions. Or how peoples’ symptoms or concerns were brushed aside because of their race or gender. But I know there are doctors out there trying to make a difference. I saw it with my pediatrician and each of the doctors involved in MOLA. 
I appreciate every challenge that I faced because it allowed me to become the person that I am today. While my interest in medicine was birthed by witnessing how impactful a physician can be to a patient and their family, I was also motivated through understanding the disparities faced by Latinx patients. I want patients to see themselves reflected in their doctors. Through each experience my understanding of a physician’s role in society has evolved. A physician treats but also uses their platform to advocate for better healthcare and advocate for the betterment of disadvantaged communities. I believe my medical education would help me achieve that dream.
```

#### Categorical Column Distributions

**app_year** (Top 10 values):
- `2023`: 401 (100.0%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| app_year | 401 | 2023.00 | 0.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 |
| amcas_id | 401 | 15219108.26 | 377750.72 | 13278986.00 | 15039509.00 | 15273506.00 | 15477871.00 | 15758293.00 |

### 2024 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| app_year | int64 | 1 | 0.0% |
| amcas_id | int64 | 613 | 0.0% |
| personal_statement | object | 613 | 0.0% |

#### Sample Data (First 3 Rows)

```
Row 1:
  app_year: 2024
  amcas_id: 13149516
  personal_statement: Boom! Pop, pop, pop! I dashed to a berm and dove for cover. “Are you hurt? Can you come to me?” I shouted. The only reply I heard was cries of pain. As soon as the shooting stopped, I rushed to my injured comrade to provide life-saving interventions. That was just the first 30 seconds of a simulated medical training I participated in at Fort Hill during the months-long experience. However, I took home something from training I did not arrive there with: an appreciation for the fragility of life. Etched in my mind was a holistic understanding of the body’s needs to sustain life and how those needs may rank when competing injuries demand your attention. I left my military training captivated by the power of medicine.

I am an Army Officer and Biochemist at the Institute of Surgical Research (ISR). As Department Chief, I lead a staff with a mission to advance medicine through research in organ failure and life support measures. I internalized and processed my encounter at Fort Hill, then applied that knowledge to shaping future medicine as Department Chief--a big responsibility, but as I acclimated, I became fascinated with our clinically-based approach.

In line with my role at the ISR, I attend rounds in the Intensive Care Unit (ICU) at Brooke Army Medical Center. One day, a young, healthy person arrived at the hospital in critical condition with a lung infection. I watched her go from clinging to life, to walking the hospital floor on life support, to being discharged, disease free. The physicians encouraged the patient and her family. They meticulously planned and applied interventions that changed the patient’s course from dire to healthy. For me, this again highlighted my appreciation for medicine and my passion for acquiring a medical degree to better serve in my leadership role in the military.

My time at the ISR was not the beginning of my journey in medicine. The desire formulated mid-way through my undergraduate studies. It started with an immunology course, which transformed the mundane concept of a cell from high school biology into a purposeful lymphocyte with a mission to protect life. Next, I joined a research lab studying embryonic development, where I watched indiscernible molecular blobs under a microscope form into complex, remarkable lifeforms. Then, through biochemistry studies, I pieced the knowledge of seemingly unrelated pathways and enzyme kinetics towards understanding a better working system that breathes life into a person. Naturally, I applied to medical school in 2010, but my financial circumstances as a first-generation college graduate from a low socioeconomic background prevented me from moving forward. However, I overcame this barrier by seeking other opportunities to contribute to the field of medicine.

In 2011, I entered the Biochemistry and Molecular Biology Ph.D. program at the University of California, Riverside. I committed to using my scientific training as a Ph.D. student to support the development of future medical therapies. In addition, my graduate training sharpened my problem-solving acumen. My thesis-based research utilized stem cells to study the roles of non-coding RNAs in embryonic development and their relationship to cancer. The graduate work resulted in a publication proposing cancer markers for clear cell renal cell carcinoma, the most common and deadly form of kidney cancer.

As a scientist, I’ve enjoyed contributing to patient care through translational medicine in academia and military service. My path has not been direct, but experience has shown me that medicine is a meaningful way I can help others and contribute to communities with limited access to medicine. While breakthrough scientific discoveries contribute multiplicatively to society, the day-to-day efforts isolate you from the people you are helping. Often, I witness researchers lose sight of the healing mission in their pursuit of academic discovery. I understand the toils of medicine carry significant loss. Still, the rewarding prospect of saving lives that would otherwise be lost provides invaluable contributions to society that I want to be a part of.

My role at the ISR has helped me see myself as a physician, and medical school is the next step to enhance my understanding of medicine to support patients better. My experiences have enriched my knowledge and ardor for patient care; observing the highly complex and coordinated efforts to save lives and the compassion that physicians provide patients and families has shown me first-hand the rigor and rewards of a medical career, rekindling and reinforcing my desire to practice it.

My scientific and military background enriched my understanding and made me an apt candidate for medical school. I am older, mature, and willing to commit to the rigor of medical school and practice. My dedication, desire for knowledge and problem-solving, leadership ability, and compassion for others makes me an outstanding choice for a future physician.
Row 2:
  app_year: 2024
  amcas_id: 13573284
  personal_statement: I have been a lover of literature for as long as I can remember. My earliest memories are of my father telling me bedtime stories, like the one about Anansi, the Spider who stole the yams from the feast, hiding them under his cap and burning his scalp, teaching us the consequences of greed. Like many Nigerians, my father believed that the answers to life’s most elusive questions can be found in a well-told story. I was eight years old when, shortly after my family and I immigrated to the United States, my father suffered a life-altering stroke, plummeting my family into the realities of Western medicine. New to the country and without relatives, childcare was not an option for my parents, so my days were filled with extended hospital visits that turned my short bedtime stories into long elaborate stories told at my father’s hospital bedside. While my father instilled in me a love for fiction, it was the real-life stories of illness, resilience, and recovery around me that turned me into a storyteller and ignited my passion for medicine.

In the summer after my sophomore year of college my mother and I visited a friend who had recently lost her baby. I sat silently as a group of African women, whom I had come to know as “aunties,” gathered around a kitchen table. I listened as many of them shared their own stories of child loss. My mother bemoaned her own experience of loss—the understaffed maternity ward of the Nigerian hospital, the absence of doctors, and the inexperienced midwife who profusely apologized as she handed my mother a motionless daughter. As I watched the aunties bond over their shared experiences of suffering and loss, acutely aware that their emotions and sentiments mirrored that of women around the world that looked like me, I began to believe that healing is possible when we understand that we are not alone—an understanding, which I gained through the transformative power of sharing one’s story. 

Driven by a passion for storytelling and an interest in global health, I enrolled at Duke University’s Global Health Institute, obtained a Master of Science, and pursued a career as a qualitative researcher.  

During my time as a research specialist at a high-risk obstetrics clinic at Duke University School of Medicine, I interviewed dozens of women with a history of preterm birth, collecting their stories as data. I heard heartbreaking stories of loss, suffering, pain, homelessness, and violence. I also heard stories of redemption, faith, and, most often, hope. Interwoven throughout these stories, I saw the role of the doctors that cared for them—the doctors that made patients feel seen, validated, and understood, and those that did not. As I interviewed women, analyzed the data, attended their clinic visits, and witnessed their deliveries, I began to understand how the healthcare system, particularly doctors, impacted the stories that women told about their experiences. I began to see medicine as an ecosystem in which every person that interacts with a patient has the potential to transform the narrative. As a researcher, I developed protocols, built databases, and analyzed data but it was the patient visits that brought me the most joy because I believed that within this ecosystem, I was part of something bigger than myself. 

I’ll never forget the day that one of my research participants, Sara, a young black woman, went into labor at just 28 weeks of pregnancy.  Less than two weeks prior, she had told me the story of her previous preterm birth that resulted in the loss of her child, the doctors that cared for her and provided an experience that she would go on to appreciate, and her hopes and dreams for this pregnancy, dreams of making it to term and her fear that it would not. Having arrived before her husband, I sat by her side during the procedure and watched as her fears became reality. I watched the obstetricians remove a two-pound baby from Sara’s body and the pediatricians rush into action, ultimately saving Sara’s baby’s life. I was transported back to the summer I sat at the table with the aunties, to the day I learned about the power of a story, but this time I knew that I didn't want to tell the story, I wanted to rewrite the narrative. I wanted to pursue a career as a physician to change how the story ends. 

I want to become a doctor because within the complicated ecosystem of medicine, doctors have the power to change the narrative. I can't go back in time and change  the stories of the women in my family, but I can impact the lives of future patients. My career as a qualitative researcher taught me many lessons: I learned the importance of listening deeply and analytically, I learned the power of nonjudgement because everyone is carrying a story within them, and, most importantly, I learned that through empathy and intentional action, we can impact the stories of the those around us for the better. These lessons are ones that I will take into my career in medicine. I carry the stories of  the women in my family, the dozens of women I have interviewed, and the hundreds of transcripts I have analyzed. It's been my privilege to be their storyteller and as I move forward in life, I look forward to a career practicing medicine and editing the chapters of those to come.
Row 3:
  app_year: 2024
  amcas_id: 13596519
  personal_statement: The worst thing that can happen to an athlete is suffering a career-ending injury. For me, however, it was the impetus for my calling to medicine. In high school being an athlete was a significant part of my identity, which led me to pursue physical therapy (PT) as a path to care for and rehabilitate athletes, like myself, so that they could continue to excel in the sports they loved. I chose to attend a PT program at Gannon University (GU), while also earning a spot on the collegiate water polo team. Unfortunately, during my sophomore year I developed wrist pain that grew worse throughout the season. My orthopedic surgeon found that I had torn three ligaments completely, ruptured my joint capsule, and developed a large ganglion cyst. Ultimately, he recommended I stop playing altogether to avoid a worse injury. I was devastated, but this injury was pivotal for me as it allowed me to identify my calling to medicine and seek diverse experiences that strengthened my desire and informed my pursuit of medicine.

As a patient during my wrist injury, I was able to compare and contrast the roles of PTs and physicians with respect to patient care. I recognized that as a physician my ability to care for people would be greatly expanded, not only in terms of who I could help (i.e., the patient population), but also in how I could help (i.e., the tools available to me to diagnose, treat, and aid in the prevention of disease). During my recuperation, I decided to transfer from GU to Loyola University Chicago (LUC) to switch to a pre-med track.

Equipped with the passion to pursue medicine at LUC, I engaged in many healthcare-related experiences to gain insight into the medical field. Volunteering with Global Brigades in Nicaragua was especially meaningful because of “Tina,” a pregnant woman seeking prenatal care, who had come to our pop-up clinic with a headache, nausea, and blurry vision. Dr. Mike, the physician I was observing, suspected she could have preeclampsia and immediately escorted her to the hospital using our caravan, so she could receive proper care. I often reflect on this experience and am saddened to think about what would have happened to Tina if there was no accessible pop-up clinic that day. Growing up in a middle-class suburb, I had not encountered barriers in access to care before, but Tina’s story expanded my world view and informed the kind of physician I strive to be–one who advocates for those facing healthcare barriers and who actively works to address and alleviate these barriers for patients and their families. 

Upon graduating from LUC, my mom was diagnosed with breast cancer and I became her primary caretaker. Though this was a scary and uncertain time, my mom and I were deeply comforted by her oncologist, Dr. Kim, who thoroughly explained my mom’s treatment options, welcomed our questions and concerns, and empowered my mom to participate in her treatment plan as a member of the healthcare team. Dr. Kim’s care for my mom felt like finally being able to exhale after holding your breath for a long time–a relief–which I hope to one day provide for my patients and their families. I am incredibly lucky to say that my mom has since made a full recovery.

Motivated by this experience, I sought to further my understanding of breast cancer and the ongoing effort to combat it by working in biomedical research. As a research specialist at LUC, I saw how our goal in the development of novel drugs to treat metastatic breast cancer was guided by clinical studies showing that a subset of breast cancer patients develop resistance to existing drugs available during their course of treatment. Ultimately, my four years in research enabled me to see the interplay between clinical medicine and research, and to understand that to provide quality healthcare is to be well-versed in academic research. 

Working in laboratory-based research also enabled me to recognize that I desire patient interaction not found in the lab, so I sought out more clinical opportunities. While shadowing Dr. Ignace at the Gerald L. Ignace Indian Health Center an encounter that struck me was with a patient named “Diane.” During the visit, Dr. Ignace not only addressed Diane’s chief complaint of neck pain but made the further effort to inquire about how the pain was affecting her other body systems and aspects of her life, including her appetite, mental health, ability to work, sleep, etc., and connect her with the appropriate resources. Witnessing Dr. Ignace’s personal rapport with his patients and holistic approach to practicing medicine has been invaluable in shaping the physician I aspire to become.

The worst thing that can happen to an athlete was the catalyst that sparked my interest in medicine. My experiences since then have taught me a great deal about the roles and responsibilities of physicians, reaffirmed my desire to become a physician, and informed the kind of physician I am driven to be. Prepared with the resilience and work ethic of an athlete, the heart of a caregiver, the passion of a volunteer, the analytical eye of a researcher, and the inquisitive mindset of a student, I now excitedly embark on my journey to medical school.
```

#### Categorical Column Distributions

**app_year** (Top 10 values):
- `2024`: 613 (100.0%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| app_year | 613 | 2024.00 | 0.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 |
| amcas_id | 613 | 15463699.57 | 409149.24 | 13149516.00 | 15280062.00 | 15519360.00 | 15750866.00 | 16091417.00 |

### Schema Consistency Across Years

| Column | 2022 | 2023 | 2024 | Notes |
|--------|------|------|------|-------|
| amcas_id | ✓ | ✓ | ✓ |  |
| app_year | ✓ | ✓ | ✓ |  |
| personal_statement | ✓ | ✓ | ✓ |  |

================================================================================
## FILE: Schools
================================================================================

### Year-over-Year Overview

| Year | Rows | Columns | Status |
|------|------|---------|--------|
| 2022 | 1,069 | 14 | ✓ OK |
| 2023 | 921 | 14 | ✓ OK |
| 2024 | 1,455 | 14 | ✓ OK |

### 2022 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_ID | int64 | 437 | 0.0% |
| Coll_Short_Desc | object | 539 | 0.0% |
| City | object | 370 | 0.0% |
| State | object | 44 | 5.9% |
| Country | object | 26 | 0.0% |
| Prog_Type_Desc | object | 4 | 0.0% |
| Major | object | 228 | 0.0% |
| Degree | object | 155 | 0.0% |
| School_Hours | float64 | 287 | 0.9% |
| Minor | object | 122 | 0.0% |
| Attend_Start_Date | object | 106 | 0.0% |
| Attend_End_date | object | 102 | 0.0% |
| School_Primary_Undergrad_ind | object | 1 | 59.1% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2022
  Amcas_ID: 12950085
  Coll_Short_Desc: Evergreen Valley College
  City: San Jose
  State: CA
  Country: USA
  Prog_Type_Desc: Junior College
  Major: No Major
  Degree: No Degree Expected
  School_Hours: 68.0
Row 2:
  App_Year: 2022
  Amcas_ID: 12950085
  Coll_Short_Desc: University of California-Berkeley
  City: Berkeley
  State: CA
  Country: USA
  Prog_Type_Desc: Undergraduate
  Major: Molecular Environmental Biology
  Degree: Bachelor of Science -  5/2010
  School_Hours: 123.0
Row 3:
  App_Year: 2022
  Amcas_ID: 13099483
  Coll_Short_Desc: Colby College
  City: Waterville
  State: ME
  Country: USA
  Prog_Type_Desc: Undergraduate
  Major: Mathematical Sciences; Chemistry: Biochemistry
  Degree: Bachelor of Arts -  5/2009
  School_Hours: 133.0
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2022`: 1,069 (100.0%)

**State** (Top 10 values):
- `CA`: 314 (29.4%)
- `IL`: 65 (6.1%)
- `MA`: 65 (6.1%)
- `NY`: 63 (5.9%)
- `MI`: 39 (3.6%)
- `PA`: 36 (3.4%)
- `MN`: 35 (3.3%)
- `FL`: 32 (3.0%)
- `TX`: 30 (2.8%)
- `VA`: 27 (2.5%)

**Country** (Top 10 values):
- `USA`: 1,004 (93.9%)
- `GBR`: 12 (1.1%)
- `ESP`: 11 (1.0%)
- `IRL`: 6 (0.6%)
- `FRA`: 5 (0.5%)
- `ITA`: 5 (0.5%)
- `TWN`: 2 (0.2%)
- `AUS`: 2 (0.2%)
- `CAN`: 2 (0.2%)
- `ISR`: 2 (0.2%)

**Prog_Type_Desc** (Top 10 values):
- `Undergraduate`: 735 (68.8%)
- `Postbaccalaureate Undergraduate`: 127 (11.9%)
- `Junior College`: 110 (10.3%)
- `Graduate`: 97 (9.1%)

**School_Primary_Undergrad_ind** (Top 10 values):
- `Y`: 437 (40.9%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 1069 | 2022.00 | 0.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 | 2022.00 |
| Amcas_ID | 1069 | 14971439.09 | 397582.66 | 12950085.00 | 14840489.00 | 15035470.00 | 15229576.00 | 15499135.00 |
| School_Hours | 1059 | 57.46 | 52.09 | 0.00 | 8.00 | 34.20 | 112.00 | 191.00 |

### 2023 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_ID | int64 | 401 | 0.0% |
| Coll_Short_Desc | object | 489 | 0.0% |
| City | object | 343 | 0.0% |
| State | object | 45 | 4.8% |
| Country | object | 24 | 0.0% |
| Prog_Type_Desc | object | 4 | 0.0% |
| Major | object | 213 | 0.0% |
| Degree | object | 163 | 0.0% |
| School_Hours | float64 | 250 | 1.0% |
| Minor | object | 113 | 0.0% |
| Attend_Start_Date | object | 111 | 0.0% |
| Attend_End_date | object | 112 | 0.0% |
| School_Primary_Undergrad_ind | object | 1 | 56.5% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2023
  Amcas_ID: 13278986
  Coll_Short_Desc: University of California-Los Angeles
  City: Los Angeles
  State: CA
  Country: USA
  Prog_Type_Desc: Undergraduate
  Major: Biology
  Degree: Bachelor of Science -  6/2013
  School_Hours: 161.5
Row 2:
  App_Year: 2023
  Amcas_ID: 13278986
  Coll_Short_Desc: University of California-Los Angeles Extension
  City: Los Angeles
  State: CA
  Country: USA
  Prog_Type_Desc: Postbaccalaureate Undergraduate
  Major: No Major
  Degree: No Degree Expected
  School_Hours: 85.9
Row 3:
  App_Year: 2023
  Amcas_ID: 13767033
  Coll_Short_Desc: Franklin & Marshall College
  City: Lancaster
  State: PA
  Country: USA
  Prog_Type_Desc: Undergraduate
  Major: Neuroscience
  Degree: Bachelor of Arts -  5/2017
  School_Hours: 112.0
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2023`: 921 (100.0%)

**State** (Top 10 values):
- `CA`: 249 (27.0%)
- `IL`: 59 (6.4%)
- `MA`: 58 (6.3%)
- `NY`: 50 (5.4%)
- `MI`: 43 (4.7%)
- `FL`: 33 (3.6%)
- `WI`: 31 (3.4%)
- `TX`: 28 (3.0%)
- `VA`: 27 (2.9%)
- `PA`: 24 (2.6%)

**Country** (Top 10 values):
- `USA`: 874 (94.9%)
- `ESP`: 8 (0.9%)
- `GBR`: 4 (0.4%)
- `FRA`: 3 (0.3%)
- `CAN`: 3 (0.3%)
- `DEU`: 3 (0.3%)
- `IRL`: 3 (0.3%)
- `CHN`: 2 (0.2%)
- `CZE`: 2 (0.2%)
- `ARG`: 2 (0.2%)

**Prog_Type_Desc** (Top 10 values):
- `Undergraduate`: 666 (72.3%)
- `Postbaccalaureate Undergraduate`: 103 (11.2%)
- `Junior College`: 80 (8.7%)
- `Graduate`: 72 (7.8%)

**School_Primary_Undergrad_ind** (Top 10 values):
- `Y`: 401 (43.5%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 921 | 2023.00 | 0.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 | 2023.00 |
| Amcas_ID | 921 | 15166114.25 | 429609.05 | 13278986.00 | 14995931.00 | 15258548.00 | 15457219.00 | 15758293.00 |
| School_Hours | 912 | 60.03 | 53.70 | 0.00 | 7.00 | 36.00 | 115.22 | 233.00 |

### 2024 Detailed Analysis

#### Column Schema

| Column Name | Data Type | Unique Values | Missing % |
|-------------|-----------|---------------|----------|
| App_Year | int64 | 1 | 0.0% |
| Amcas_ID | int64 | 613 | 0.0% |
| Coll_Short_Desc | object | 615 | 0.0% |
| City | object | 414 | 0.0% |
| State | object | 46 | 3.7% |
| Country | object | 23 | 0.0% |
| Prog_Type_Desc | object | 4 | 0.0% |
| Major | object | 290 | 0.0% |
| Degree | object | 196 | 0.0% |
| School_Hours | float64 | 367 | 0.7% |
| Minor | object | 174 | 0.0% |
| Attend_Start_Date | object | 123 | 0.0% |
| Attend_End_date | object | 119 | 0.0% |
| School_Primary_Undergrad_ind | object | 1 | 57.9% |

#### Sample Data (First 3 Rows)

```
Row 1:
  App_Year: 2024
  Amcas_ID: 13149516
  Coll_Short_Desc: Joint Services Transcript-Main Program
  City: Ft Leavenworth
  State: FL
  Country: USA
  Prog_Type_Desc: Undergraduate
  Major: No Major
  Degree: No Degree Expected
  School_Hours: 0.0
Row 2:
  App_Year: 2024
  Amcas_ID: 13149516
  Coll_Short_Desc: University of California-Santa Barbara
  City: Santa Barbara
  State: CA
  Country: USA
  Prog_Type_Desc: Undergraduate
  Major: No Major
  Degree: No Degree Expected
  School_Hours: 34.4
Row 3:
  App_Year: 2024
  Amcas_ID: 13149516
  Coll_Short_Desc: University of California-Riverside
  City: Riverside
  State: CA
  Country: USA
  Prog_Type_Desc: Undergraduate
  Major: Biochemistry
  Degree: Bachelor of Science -  8/2010
  School_Hours: 95.1
```

#### Categorical Column Distributions

**App_Year** (Top 10 values):
- `2024`: 1,455 (100.0%)

**State** (Top 10 values):
- `CA`: 427 (29.3%)
- `IL`: 103 (7.1%)
- `FL`: 84 (5.8%)
- `TX`: 71 (4.9%)
- `MA`: 57 (3.9%)
- `NY`: 56 (3.8%)
- `MI`: 47 (3.2%)
- `OH`: 42 (2.9%)
- `NC`: 38 (2.6%)
- `PA`: 36 (2.5%)

**Country** (Top 10 values):
- `USA`: 1,395 (95.9%)
- `ESP`: 12 (0.8%)
- `GBR`: 10 (0.7%)
- `CAN`: 6 (0.4%)
- `AUS`: 4 (0.3%)
- `ITA`: 4 (0.3%)
- `KOR`: 3 (0.2%)
- `FRA`: 3 (0.2%)
- `CUB`: 2 (0.1%)
- `DNK`: 2 (0.1%)

**Prog_Type_Desc** (Top 10 values):
- `Undergraduate`: 1,025 (70.4%)
- `Junior College`: 173 (11.9%)
- `Postbaccalaureate Undergraduate`: 142 (9.8%)
- `Graduate`: 115 (7.9%)

**School_Primary_Undergrad_ind** (Top 10 values):
- `Y`: 613 (42.1%)

#### Numeric Statistics

| Column | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|--------|-------|------|-----|-----|-----|-----|-----|-----|
| App_Year | 1455 | 2024.00 | 0.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 | 2024.00 |
| Amcas_ID | 1455 | 15398096.01 | 467934.63 | 13149516.00 | 15210814.00 | 15505605.00 | 15723416.00 | 16091417.00 |
| School_Hours | 1445 | 58.88 | 53.35 | 0.00 | 7.00 | 35.00 | 114.00 | 213.00 |

### Schema Consistency Across Years

| Column | 2022 | 2023 | 2024 | Notes |
|--------|------|------|------|-------|
| Amcas_ID | ✓ | ✓ | ✓ |  |
| App_Year | ✓ | ✓ | ✓ |  |
| Attend_End_date | ✓ | ✓ | ✓ |  |
| Attend_Start_Date | ✓ | ✓ | ✓ |  |
| City | ✓ | ✓ | ✓ |  |
| Coll_Short_Desc | ✓ | ✓ | ✓ |  |
| Country | ✓ | ✓ | ✓ |  |
| Degree | ✓ | ✓ | ✓ |  |
| Major | ✓ | ✓ | ✓ |  |
| Minor | ✓ | ✓ | ✓ |  |
| Prog_Type_Desc | ✓ | ✓ | ✓ |  |
| School_Hours | ✓ | ✓ | ✓ |  |
| School_Primary_Undergrad_ind | ✓ | ✓ | ✓ |  |
| State | ✓ | ✓ | ✓ |  |

---

## Data Quality Observations

### 2022 Quality Issues

**1. Applicants.xlsx:**
- HIGH MISSINGNESS: 'Prev_Applied_Rush' is 83.3% null
- HIGH MISSINGNESS: 'Eo_Level' is 72.3% null
- HIGH MISSINGNESS: 'Hrdshp_Comments' is 73.7% null
- HIGH MISSINGNESS: 'Inst_Action_Desc' is 93.4% null
- HIGH MISSINGNESS: 'Prev_Matric_Sschool' is 100.0% null
- HIGH MISSINGNESS: 'Prev_Matric_Year' is 99.8% null
- HIGH MISSINGNESS: 'Prev_Matric_Desc' is 100.0% null
- HIGH MISSINGNESS: 'Felony_Desc' is 100.0% null
- HIGH MISSINGNESS: 'Misdemeanor_Desc' is 98.4% null
- HIGH MISSINGNESS: 'Military_Discharge_Desc' is 100.0% null
- HIGH MISSINGNESS: 'Military_Service_Status' is 100.0% null
- EMPTY COLUMN: 'Prev_Matric_Sschool' is completely null
- EMPTY COLUMN: 'Prev_Matric_Desc' is completely null
- EMPTY COLUMN: 'Felony_Desc' is completely null
- EMPTY COLUMN: 'Military_Discharge_Desc' is completely null
- EMPTY COLUMN: 'Military_Service_Status' is completely null
- CONSTANT: 'Appl_Year' has only 1 unique value
- CONSTANT: 'Prev_Matric_Ind' has only 1 unique value
- CONSTANT: 'Prev_Matric_Year' has only 1 unique value
- CONSTANT: 'Investigation_Ind' has only 1 unique value
- CONSTANT: 'Felony_Ind' has only 1 unique value
- CONSTANT: 'Military_Discharge_Ind' has only 1 unique value
- CONSTANT: 'Military_HON_Discharge_Ind' has only 1 unique value
- CONSTANT: 'HealthCare_Ind' has only 1 unique value
- CONSTANT: 'Military_Service' has only 1 unique value

**10. Secondary Application.xlsx:**
- HIGH MISSINGNESS: '6 - Addtl Info' is 100.0% null
- HIGH MISSINGNESS: '8 - Details' is 96.6% null
- HIGH MISSINGNESS: '3 - # Summers' is 100.0% null
- HIGH MISSINGNESS: '3 - # Semesters' is 100.0% null
- HIGH MISSINGNESS: '3 - # Years' is 100.0% null
- HIGH MISSINGNESS: '3 - Abstract(s)' is 100.0% null
- HIGH MISSINGNESS: '3 - Conference Presentation(s)' is 100.0% null
- HIGH MISSINGNESS: '3 - Poster Presentation(s)' is 100.0% null
- HIGH MISSINGNESS: '3 - Publication(s)' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Employer 1' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 1 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 1 Duration' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Employer 2' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 2 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 2 Duration' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Employer 3' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 3 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 3 Duration' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Volunteer 1' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 1 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 1 Duration' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Volunteer 2' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 2 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 2 Duration' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Volunteer 3' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 3 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 3 Duration' is 100.0% null
- HIGH MISSINGNESS: 'LOR - Not Submitting Committee Letter Reason' is 95.2% null
- HIGH MISSINGNESS: 'LOR - Which Three Letters' is 55.1% null
- EMPTY COLUMN: '6 - Addtl Info' is completely null
- EMPTY COLUMN: '3 - # Summers' is completely null
- EMPTY COLUMN: '3 - # Semesters' is completely null
- EMPTY COLUMN: '3 - # Years' is completely null
- EMPTY COLUMN: '3 - Abstract(s)' is completely null
- EMPTY COLUMN: '3 - Conference Presentation(s)' is completely null
- EMPTY COLUMN: '3 - Poster Presentation(s)' is completely null
- EMPTY COLUMN: '3 - Publication(s)' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Employer 1' is completely null
- EMPTY COLUMN: '4 - Employer 1 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Employer 1 Duration' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Employer 2' is completely null
- EMPTY COLUMN: '4 - Employer 2 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Employer 2 Duration' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Employer 3' is completely null
- EMPTY COLUMN: '4 - Employer 3 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Employer 3 Duration' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Volunteer 1' is completely null
- EMPTY COLUMN: '4 - Volunteer 1 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Volunteer 1 Duration' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Volunteer 2' is completely null
- EMPTY COLUMN: '4 - Volunteer 2 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Volunteer 2 Duration' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Volunteer 3' is completely null
- EMPTY COLUMN: '4 - Volunteer 3 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Volunteer 3 Duration' is completely null
- CONSTANT: 'App Year' has only 1 unique value
- CONSTANT: '6 - Direct Care Experience' has only 1 unique value
- CONSTANT: '3 - Research' has only 1 unique value

**2. Language.xlsx:**
- CONSTANT: 'App_Year' has only 1 unique value

**3. Parents.xlsx:**
- CONSTANT: 'App_Year' has only 1 unique value

**4. Siblings.xlsx:**
- CONSTANT: 'App_Year' has only 1 unique value

**5. Academic Records.xlsx:**
- HIGH MISSINGNESS: 'Course_Type' is 79.8% null
- CONSTANT: 'App_Year' has only 1 unique value

**6. Experiences.xlsx:**
- HIGH MISSINGNESS: 'Meaningful_Desc' is 78.0% null
- CONSTANT: 'App_Year' has only 1 unique value

**8. Schools.xlsx:**
- HIGH MISSINGNESS: 'School_Primary_Undergrad_ind' is 59.1% null
- CONSTANT: 'App_Year' has only 1 unique value
- CONSTANT: 'School_Primary_Undergrad_ind' has only 1 unique value

**9. Personal Statement.xlsx:**
- CONSTANT: 'app_year' has only 1 unique value

### 2023 Quality Issues

**1. Applicants.xlsx:**
- HIGH MISSINGNESS: 'Prev_Applied_Rush' is 88.3% null
- HIGH MISSINGNESS: 'Eo_Level' is 74.8% null
- HIGH MISSINGNESS: 'Hrdshp_Comments' is 76.3% null
- HIGH MISSINGNESS: 'Inst_Action_Desc' is 95.0% null
- HIGH MISSINGNESS: 'Prev_Matric_Sschool' is 100.0% null
- HIGH MISSINGNESS: 'Prev_Matric_Year' is 99.5% null
- HIGH MISSINGNESS: 'Prev_Matric_Desc' is 100.0% null
- HIGH MISSINGNESS: 'Felony_Desc' is 100.0% null
- HIGH MISSINGNESS: 'Misdemeanor_Desc' is 99.8% null
- HIGH MISSINGNESS: 'Military_Discharge_Desc' is 100.0% null
- HIGH MISSINGNESS: 'Military_Service_Status' is 98.0% null
- EMPTY COLUMN: 'Prev_Matric_Sschool' is completely null
- EMPTY COLUMN: 'Prev_Matric_Desc' is completely null
- EMPTY COLUMN: 'Felony_Desc' is completely null
- EMPTY COLUMN: 'Military_Discharge_Desc' is completely null
- CONSTANT: 'Appl_Year' has only 1 unique value
- CONSTANT: 'Prev_Matric_Ind' has only 1 unique value
- CONSTANT: 'Prev_Matric_Year' has only 1 unique value
- CONSTANT: 'Felony_Ind' has only 1 unique value
- CONSTANT: 'Misdemeanor_Desc' has only 1 unique value
- CONSTANT: 'Military_Discharge_Ind' has only 1 unique value
- CONSTANT: 'HealthCare_Ind' has only 1 unique value

**10. Secondary Application.xlsx:**
- HIGH MISSINGNESS: '3 - Reflect Experience' is 100.0% null
- HIGH MISSINGNESS: '4 - Hope to Gain' is 100.0% null
- HIGH MISSINGNESS: '6 - Addtl Info' is 100.0% null
- HIGH MISSINGNESS: '8 - Details' is 98.2% null
- HIGH MISSINGNESS: '3 - # Summers' is 100.0% null
- HIGH MISSINGNESS: '3 - # Semesters' is 100.0% null
- HIGH MISSINGNESS: '3 - # Years' is 100.0% null
- HIGH MISSINGNESS: '3 - Abstract(s)' is 100.0% null
- HIGH MISSINGNESS: '3 - Conference Presentation(s)' is 100.0% null
- HIGH MISSINGNESS: '3 - Poster Presentation(s)' is 100.0% null
- HIGH MISSINGNESS: '3 - Publication(s)' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Employer 1' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 1 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 1 Duration' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Employer 2' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 2 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 2 Duration' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Employer 3' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 3 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 3 Duration' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Volunteer 1' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 1 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 1 Duration' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Volunteer 2' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 2 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 2 Duration' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Volunteer 3' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 3 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 3 Duration' is 100.0% null
- HIGH MISSINGNESS: 'LOR - Not Submitting Committee Letter Reason' is 94.3% null
- HIGH MISSINGNESS: 'LOR - Which Three Letters' is 55.9% null
- EMPTY COLUMN: '3 - Reflect Experience' is completely null
- EMPTY COLUMN: '4 - Hope to Gain' is completely null
- EMPTY COLUMN: '6 - Addtl Info' is completely null
- EMPTY COLUMN: '3 - # Summers' is completely null
- EMPTY COLUMN: '3 - # Semesters' is completely null
- EMPTY COLUMN: '3 - # Years' is completely null
- EMPTY COLUMN: '3 - Abstract(s)' is completely null
- EMPTY COLUMN: '3 - Conference Presentation(s)' is completely null
- EMPTY COLUMN: '3 - Poster Presentation(s)' is completely null
- EMPTY COLUMN: '3 - Publication(s)' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Employer 1' is completely null
- EMPTY COLUMN: '4 - Employer 1 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Employer 1 Duration' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Employer 2' is completely null
- EMPTY COLUMN: '4 - Employer 2 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Employer 2 Duration' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Employer 3' is completely null
- EMPTY COLUMN: '4 - Employer 3 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Employer 3 Duration' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Volunteer 1' is completely null
- EMPTY COLUMN: '4 - Volunteer 1 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Volunteer 1 Duration' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Volunteer 2' is completely null
- EMPTY COLUMN: '4 - Volunteer 2 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Volunteer 2 Duration' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Volunteer 3' is completely null
- EMPTY COLUMN: '4 - Volunteer 3 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Volunteer 3 Duration' is completely null
- CONSTANT: 'App Year' has only 1 unique value
- CONSTANT: '6 - Direct Care Experience' has only 1 unique value
- CONSTANT: '3 - Research' has only 1 unique value

**11. Military.xlsx:**
- HIGH MISSINGNESS: 'military_service_status_other_descr' is 100.0% null
- EMPTY COLUMN: 'military_service_status_other_descr' is completely null
- CONSTANT: 'app_year' has only 1 unique value
- CONSTANT: 'military_service_descr' has only 1 unique value

**2. Language.xlsx:**
- CONSTANT: 'App_Year' has only 1 unique value

**3. Parents.xlsx:**
- CONSTANT: 'App_Year' has only 1 unique value

**4. Siblings.xlsx:**
- CONSTANT: 'App_Year' has only 1 unique value
- CONSTANT: 'yn' has only 1 unique value

**5. Academic Records.xlsx:**
- HIGH MISSINGNESS: 'Course_Type' is 79.9% null
- CONSTANT: 'App_Year' has only 1 unique value

**6. Experiences.xlsx:**
- HIGH MISSINGNESS: 'Meaningful_Desc' is 78.1% null
- CONSTANT: 'App_Year' has only 1 unique value

**8. Schools.xlsx:**
- HIGH MISSINGNESS: 'School_Primary_Undergrad_ind' is 56.5% null
- CONSTANT: 'App_Year' has only 1 unique value
- CONSTANT: 'School_Primary_Undergrad_ind' has only 1 unique value

**9. Personal Statement.xlsx:**
- CONSTANT: 'app_year' has only 1 unique value

### 2024 Quality Issues

**1. Applicants.xlsx:**
- HIGH MISSINGNESS: 'Prev_Applied_Rush' is 85.3% null
- HIGH MISSINGNESS: 'Eo_Level' is 78.8% null
- HIGH MISSINGNESS: 'Hrdshp_Comments' is 100.0% null
- HIGH MISSINGNESS: 'Inst_Action_Desc' is 93.8% null
- HIGH MISSINGNESS: 'Prev_Matric_Sschool' is 99.8% null
- HIGH MISSINGNESS: 'Prev_Matric_Year' is 99.3% null
- HIGH MISSINGNESS: 'Prev_Matric_Desc' is 99.8% null
- HIGH MISSINGNESS: 'Felony_Desc' is 100.0% null
- HIGH MISSINGNESS: 'Misdemeanor_Desc' is 99.5% null
- HIGH MISSINGNESS: 'Military_Discharge_Desc' is 100.0% null
- HIGH MISSINGNESS: 'Military_Service_Status' is 99.2% null
- EMPTY COLUMN: 'Hrdshp_Comments' is completely null
- EMPTY COLUMN: 'Felony_Desc' is completely null
- EMPTY COLUMN: 'Military_Discharge_Desc' is completely null
- CONSTANT: 'Appl_Year' has only 1 unique value
- CONSTANT: 'Disadvantanged_Ind' has only 1 unique value
- CONSTANT: 'Prev_Matric_Sschool' has only 1 unique value
- CONSTANT: 'Prev_Matric_Desc' has only 1 unique value
- CONSTANT: 'Investigation_Ind' has only 1 unique value
- CONSTANT: 'Felony_Ind' has only 1 unique value
- CONSTANT: 'Military_Discharge_Ind' has only 1 unique value
- CONSTANT: 'HealthCare_Ind' has only 1 unique value

**10. Secondary Application.xlsx:**
- HIGH MISSINGNESS: '3 - Reflect Experience' is 100.0% null
- HIGH MISSINGNESS: '4 - Hope to Gain' is 100.0% null
- HIGH MISSINGNESS: '6 - Addtl Info' is 100.0% null
- HIGH MISSINGNESS: '8 - Details' is 98.4% null
- HIGH MISSINGNESS: '3 - # Summers' is 100.0% null
- HIGH MISSINGNESS: '3 - # Semesters' is 100.0% null
- HIGH MISSINGNESS: '3 - # Years' is 100.0% null
- HIGH MISSINGNESS: '3 - Abstract(s)' is 100.0% null
- HIGH MISSINGNESS: '3 - Conference Presentation(s)' is 100.0% null
- HIGH MISSINGNESS: '3 - Poster Presentation(s)' is 100.0% null
- HIGH MISSINGNESS: '3 - Publication(s)' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Employer 1' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 1 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 1 Duration' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Employer 2' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 2 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 2 Duration' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Employer 3' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 3 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Employer 3 Duration' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Volunteer 1' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 1 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 1 Duration' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Volunteer 2' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 2 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 2 Duration' is 100.0% null
- HIGH MISSINGNESS: '4 - Healthcare Experience - Volunteer 3' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 3 Direct Patient' is 100.0% null
- HIGH MISSINGNESS: '4 - Volunteer 3 Duration' is 100.0% null
- HIGH MISSINGNESS: 'LOR - Not Submitting Committee Letter Reason' is 94.8% null
- HIGH MISSINGNESS: 'LOR - Which Three Letters' is 56.8% null
- EMPTY COLUMN: '3 - Reflect Experience' is completely null
- EMPTY COLUMN: '4 - Hope to Gain' is completely null
- EMPTY COLUMN: '6 - Addtl Info' is completely null
- EMPTY COLUMN: '3 - # Summers' is completely null
- EMPTY COLUMN: '3 - # Semesters' is completely null
- EMPTY COLUMN: '3 - # Years' is completely null
- EMPTY COLUMN: '3 - Abstract(s)' is completely null
- EMPTY COLUMN: '3 - Conference Presentation(s)' is completely null
- EMPTY COLUMN: '3 - Poster Presentation(s)' is completely null
- EMPTY COLUMN: '3 - Publication(s)' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Employer 1' is completely null
- EMPTY COLUMN: '4 - Employer 1 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Employer 1 Duration' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Employer 2' is completely null
- EMPTY COLUMN: '4 - Employer 2 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Employer 2 Duration' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Employer 3' is completely null
- EMPTY COLUMN: '4 - Employer 3 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Employer 3 Duration' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Volunteer 1' is completely null
- EMPTY COLUMN: '4 - Volunteer 1 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Volunteer 1 Duration' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Volunteer 2' is completely null
- EMPTY COLUMN: '4 - Volunteer 2 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Volunteer 2 Duration' is completely null
- EMPTY COLUMN: '4 - Healthcare Experience - Volunteer 3' is completely null
- EMPTY COLUMN: '4 - Volunteer 3 Direct Patient' is completely null
- EMPTY COLUMN: '4 - Volunteer 3 Duration' is completely null
- CONSTANT: 'App Year' has only 1 unique value
- CONSTANT: '3 - Research' has only 1 unique value

**11. Military.xlsx:**
- HIGH MISSINGNESS: 'military_service_status_other_descr' is 100.0% null
- EMPTY COLUMN: 'military_service_status_other_descr' is completely null
- CONSTANT: 'app_year' has only 1 unique value
- CONSTANT: 'military_service_descr' has only 1 unique value

**12. GPA Trend.xlsx:**
- HIGH MISSINGNESS: 'Total_GPA_Trend' is 55.0% null
- HIGH MISSINGNESS: 'BCPM_GPA_Trend' is 52.2% null

**2. Language.xlsx:**
- CONSTANT: 'App_Year' has only 1 unique value

**3. Parents.xlsx:**
- CONSTANT: 'App_Year' has only 1 unique value

**4. Siblings.xlsx:**
- CONSTANT: 'App_Year' has only 1 unique value

**5. Academic Records.xlsx:**
- HIGH MISSINGNESS: 'Course_Type' is 78.7% null
- CONSTANT: 'App_Year' has only 1 unique value

**6. Experiences.xlsx:**
- HIGH MISSINGNESS: 'Meaningful_Desc' is 78.5% null
- CONSTANT: 'App_Year' has only 1 unique value

**8. School.xlsx:**
- HIGH MISSINGNESS: 'School_Primary_Undergrad_ind' is 57.9% null
- CONSTANT: 'App_Year' has only 1 unique value
- CONSTANT: 'School_Primary_Undergrad_ind' has only 1 unique value

**9. Personal Statement.xlsx:**
- CONSTANT: 'app_year' has only 1 unique value

---

## Feature Engineering Recommendations

### Column Classification

#### Identifiers (DO NOT use as features)
- Applicant_ID, Application_ID, Record_ID
- School codes, Institution IDs
- Any personally identifiable information

#### Protected Attributes (Potential bias concerns)
- Race, Ethnicity
- Gender
- Age, Date of Birth
- Citizenship status
- Geographic location (ZIP, city, state)
- Disadvantaged/URiM status flags

#### Numeric Features (ML-ready)
- Test scores: MCAT, GPA (overall, science, non-science)
- Counts: number of experiences, languages, siblings, schools attended
- Durations: months/hours of experience, gap years
- Academic: credit hours, course grades, GPA trends

#### Categorical Features (Need encoding)
- Application type, status, decision
- School type, degree type, major
- Experience categories, types
- Binary Yes/No flags
- State, region codes

#### Text Features (Need NLP)
- Personal statements
- Secondary application essays
- Experience descriptions
- School names

#### Temporal Features
- Application submission dates
- Decision dates
- Academic year progressions
- GPA trends over time

### Data Cleaning Priorities

**HIGH PRIORITY:**
1. Standardize column names across all years
2. Handle missing value strategy (drop, impute, or use as signal)
3. Validate ID consistency across related tables
4. Parse and standardize all date columns
5. Identify and document all schema changes year-over-year

**MEDIUM PRIORITY:**
6. Encode categorical variables consistently
7. Aggregate child tables to applicant level
8. Text preprocessing for essays
9. Create derived features (experience diversity, GPA trends, etc.)
10. Outlier detection and handling

**LOW PRIORITY:**
11. Validate business logic constraints
12. Create comprehensive data dictionary
13. Version control for transformations

### Temporal Training Strategy

For predictive modeling:
- **Training set:** 2022 + 2023 data
- **Test set:** 2024 data
- **Validation:** Cross-validation within 2022+2023
- **Caution:** Check for distribution shifts between years
- **Recommendation:** Analyze year-over-year consistency in target variable distributions
