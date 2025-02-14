# DAG for Advanced Coursework ASC Project

# Import the dagitty library after it's installed
library(dagitty)

# Groups:

# Disadvantage: military, migrant, immigrant, refugee, ethnicity,
#      is 1%, extended school year, regular %, reading intervention, ELL 
#      Student, ELL Parent, & home status.

# School: school & environment

# Attendance: school membership & % days attended

# Grades: test score, civics exam, & overall_gpa

# Teacher

# AC_Ind


dag <- dagitty("
dag {
  Teacher -> AC_Ind
  Teacher -> Grades
  Attendance -> Grades
  School -> Teacher
  School -> Grades
  School -> AC_Ind
  Disadvantage -> Grades
  Disadvantage -> Attendance
  Disadvantage -> AC_Ind
  Overall_GPA -> AC_Ind
}
")

plot( dag )
