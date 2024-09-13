# Antecedents to and Effects of Participating in Advanced Coursework


## Description

This project investigates the factors that lead to student involvement
in advanced educational programs and the outcomes associated with such
participation. The primary objectives are to identify the demographic,
socioeconomic, and institutional variables that serve as precursors to
enrollment in these programs and to analyze the impact that
participation has on students’ academic and career trajectories. By
conducting a comprehensive analysis of student data from middle school
through high school graduation, this project seeks to provide actionable
insights that can inform district policy and program development.

### Project I: Antecedents to Participation

#### Phase I: Develop a Comprehensive Longitudinal Dataset (3 September – 7 October)

The ASC will data engineer and clean a longitudinal data set that tracks
student information from middle school through high school graduation.
We will merge and combine year-over-year student data, ensuring that it
is prepared for correlation and machine learning analysis to support the
understanding of factors influencing participation in enriched
educational activities.

#### Phase II: Data Analysis and Model Building (7 October – 1 November)

We will identify critical correlates and predictors of participation in
enrichment programs. This phase will analyze demographic, socioeconomic,
and institutional factors (teachers, courses, programs, and other
principal components) that influence student participation in advanced
placement, continuing education, and CTE pathways within the Cache
County School District. In concert with this analysis, we will perform a
detailed market heterogeneity analysis to identify distinct segments
within the student population and the factors that may influence or
predict participation in these programs.

#### Phase III: Presentation and Recommended Actions (1 November – 2 December)

The ASC will develop and deliver a comprehensive presentation that
outlines key findings, insights, and recommendations based on the
analysis conducted to provide actionable steps and strategies for the
district to implement to achieve the desired outcomes.

### Project II: Outcomes Associated with Participation

#### Phase I: Expand Dataset with National Clearing House Data (6 January – 3 February)

We will perform the data engineering required to expand the longitudinal
dataset by incorporating detailed data from the National Student
Clearinghouse. This engineering will include individual student
information on university enrollment, technical college enrollment,
graduation, etc. Integrating this additional data will enable a
comprehensive analysis of post-secondary outcomes, allowing for a better
understanding of how these enriched educational experiences and
demographic factors correlate with long-term academic and career
success.

#### Phase II: Data Analysis and Model Building (3 February – 1 March)

Using participation in enrichment programs as the independent variable,
we will find correlates and predictors of post-graduation success. This
analysis will explore involvement in education, training, and other
metrics of success. In concert with this analysis, we will perform a
detailed market heterogeneity analysis to identify distinct segments
within the student population and the factors that may influence or
predict post-high school success.

#### Phase III: Presentation and Recommended Actions (1 March – 15 April)

The ASC will develop and deliver a comprehensive presentation that
outlines key findings, insights, and recommendations based on the
analysis conducted to provide actionable steps and strategies for the
district to implement to achieve the desired outcomes.

## Project Organization

- `/code` Scripts with prefixes (e.g., `01_import-data.py`,
  `02_clean-data.py`) and functions in `/code/src`.
- `/data` Simulated and real data, the latter not pushed.
- `/figures` PNG images and plots.
- `/output` Output from model runs, not pushed.
- `/presentations` Presentation slides.
- `/private` A catch-all folder for miscellaneous files, not pushed.
- `/venv` Project library.
- `/writing` Case studies and the paper.
- `requirements.txt` Information on the reproducible environment.

## Reproducible Environment

Every package you install lives in your system library, accessible to
all projects. However, packages change. Add a reproducible environment
by creating a project library using venv.

For more details on using GitHub, Quarto, etc. see [ASC
Training](https://github.com/marcdotson/asc-training).
