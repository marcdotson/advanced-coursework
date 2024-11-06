import polars as pl
import seaborn.objects as so

survey = pl.read_csv(
  'data/teacher-survey/Advanced Coursework Teacher Survey_October 23, 2024_16.45.csv', 
  skip_rows_after_header = 2
)



# S1 Which of the following course types do you currently teach?
# In your opinion, how do each of the following factors impact a student's decision to enroll in advanced courses?
# Q1_1 Previous academic success
# Q1_2 Previous school attended
# Q1_3 Class attendance
# Q1_4 Teacher encouragement
# Q1_5 Social expectations
# Q1_6 Moving schools
# Q2 In your own words, please describe the factors that impact a student's decision to enroll in advanced courses. How might these factors impact each other? Your answer does not have to include the factors from the previous question.



# In your opinion, how do each of the following factors impact a student's performance in advanced courses?
# Q3_1 Previous academic success
# Q3_2 Previous school attended
# Q3_3 Class attendance
# Q3_4 Teacher encouragement
# Q3_5 Social expectations
# Q3_6 Moving schools
# Q4 In your own words, please describe the factors that impact a student's performance in advanced courses. How might these factors impact each other? Your answer does not have to include the factors from the previous question.




# Q1: What program are you in? - Selected Choice
(survey
  .group_by(pl.col('S1'))
  .agg(n = pl.len())
)

(so.Plot(survey, x = 'S1')
  .add(so.Bar(), so.Hist())
)

# Most of the students are Data Analytics students, which isn't surprising as DATA 5600
# is a required course for the major.

# Q2: Have you already taken Making Decisions with Data (DATA 3100)?
(survey
 .group_by(pl.col('Q2'))
 .agg(n = pl.len())
)

(so.Plot(survey, x = 'Q2')
  .add(so.Bar(), so.Hist())
)

(survey
 .group_by(pl.col('Q1', 'Q2'))
 .agg(n = pl.len())
)

(so.Plot(survey, x = 'Q1', color = 'Q2')
  .add(so.Bar(), so.Hist(), so.Dodge())
)

# Most students have taken DATA 3100, but the "Other" group may have not. It is a prerequisite.

# Q3: How would you summarize what you learned in DATA 3100?
# Business statistics. Probability, sampling, graph types, hypothesis tests, confidence intervals,
# and p-values. Comparison made to AP Stats.

# Q4: Have you already taken Introduction to Modern Data Analytics (DATA 3300)?
(survey
 .group_by(pl.col('Q4'))
 .agg(n = pl.len())
)

(so.Plot(survey, x = 'Q4')
  .add(so.Bar(), so.Hist())
)

(survey
 .group_by(pl.col('Q1', 'Q4'))
 .agg(n = pl.len())
)

(so.Plot(survey, x = 'Q1', color = 'Q4')
  .add(so.Bar(), so.Hist(), so.Dodge())
)

# A good number of students have not taken DATA 3300. Evidence that we really should require it as
# a prerequisite for DATA 5600. None of the "Other" students specifically.

# Q5: How would you summarize what you learned in DATA 3300?
# Business case studies using Python, including data cleaning. SQL and Jupyter Notebooks as well. High 
# level on models, with a focus on unsupervised methods.

# Q6: Have you already taken Introduction to Python Programming (DATA 3500)?
(survey
 .group_by(pl.col('Q6'))
 .agg(n = pl.len())
)

(so.Plot(survey, x = 'Q6')
  .add(so.Bar(), so.Hist())
)

(survey
 .group_by(pl.col('Q1', 'Q6'))
 .agg(n = pl.len())
)

(so.Plot(survey, x = 'Q1', color = 'Q6')
  .add(so.Bar(), so.Hist(), so.Dodge())
)

# A surprising number of students are taking DATA 3500. Probably because its a corequisite!

# Q7: How would you summarize what you learned in DATA 3500?
# Basic Python programming. For and while loops. If/else statements. APIs.

# Q8: What kind of business decisions are you most interested in learning to inform (e.g., investments, online advertising, new product development)?
# Digital marketing, branding, advertisements, investments, new product development, financial risk.

# Q9: Have you had any internship or job experience analyzing data?
(survey
 .group_by(pl.col('Q9'))
 .agg(n = pl.len())
)

(so.Plot(survey, x = 'Q9')
  .add(so.Bar(), so.Hist())
)

(survey
 .group_by(pl.col('Q1', 'Q9'))
 .agg(n = pl.len())
)

(so.Plot(survey, x = 'Q1', color = 'Q9')
  .add(so.Bar(), so.Hist(), so.Dodge())
)

# About half have had experience, but our Data Analytics majors have had the *least* experience.

# Q10: What kind of business decisions have you informed (e.g., investments, online advertising, new product development)?
# Applications all over the place.

# Q11: What's your dream job?
# Almost entirely data-focused roles.

# Q12: Where are you on a scale from extremely nervous to extremely excited about taking DATA 5600?
(survey
 .group_by(pl.col('Q12'))
 .agg(n = pl.len())
)

(so.Plot(survey, y = 'Q12')
  .add(so.Bars(), so.Hist())
)

(survey
 .group_by(pl.col('Q1', 'Q12'))
 .agg(n = pl.len())
)

(so.Plot(survey, color = 'Q1', y = 'Q12')
  .add(so.Bars(), so.Hist(), so.Dodge())
)

# Mostly excited, with the Data Analytics majors more middle-of-the-road than others.

# Q13: What are you most nervous about for this semester of Regression and Machine Learning?
# Typical things. Time management, how rigorous the course might be, support for programming,
# remembering things from prerequisites that may have been a long time ago.

# Q14: What are you most excited about for this semester of Regression and Machine Learning?
# Learning to model, especially as it builds on other classes, including the programming.

# Q15: What is your biggest question about taking Regression and Machine Learning?
# Application of modeling, how assignments will shake out, how difficult it is, how much theory vs.
# programming will the course be, making conclusions with models.

# Q16: What times would work best for office hours this semester? For the purposes of this question, morning means before noon, early afternoon means between noon and 3 pm, and late afternoon means after 3 pm. (Select all that apply.)
# Q17: Would you like me to provide printed copies of the slides for you to take written notes?
(survey
 .group_by(pl.col('Q17'))
 .agg(n = pl.len())
)

(so.Plot(survey, x = 'Q17')
  .add(so.Bar(), so.Hist())
)

(survey
 .group_by(pl.col('Q1', 'Q17'))
 .agg(n = pl.len())
)

(so.Plot(survey, x = 'Q1', color = 'Q17')
  .add(so.Bar(), so.Hist(), so.Dodge())
)

# Q18: How old are you?
(survey
  .select(pl.col('Q18'))
  .mean()
)

(survey
 .group_by(pl.col(['Q1']))
 .agg(
   avg_age = pl.col('Q18').mean()
  )
 .sort(pl.col('avg_age'), descending = True)
)

# Q19: What is your gender?
(survey
 .group_by(pl.col('Q19'))
 .agg(n = pl.len())
)

(so.Plot(survey, x = 'Q19')
  .add(so.Bar(), so.Hist())
)

(survey
 .group_by(pl.col('Q1', 'Q19'))
 .agg(n = pl.len())
)

(so.Plot(survey, x = 'Q1', color = 'Q19')
  .add(so.Bar(), so.Hist(), so.Dodge())
)

# Most male, especially among Data Analytics students.
