# DAG for Advanced Coursework ASC Project

# Import the dagitty library after it's installed
library(dagitty)

# Groups:

# Advantage (also includes disadvantage) (it's mainly disadvantages): military, 
#      migrant, immigrant, refugee, ethnicity,
#      is 1%, extended school year, regular %, reading intervention, ELL 
#      Student, ELL Parent, & home status.

# School: school & environment

# Attendance: school membership & % days attended

# Test_Scores: test scores & civics exam

# Teacher

# Overall_GPA

# AC_Ind



dag <- dagitty("
dag {
  Teacher -> Test_Scores
  Teacher -> AC_Ind
  Teacher -> Overall_GPA
  Test_Scores -> Overall_GPA
  Test_Scores -> AC_Ind
  Attendance -> Overall_GPA
  School -> Teacher
  School -> Test_Scores
  School -> Overall_GPA
  School -> AC_Ind
  Advantage -> Test_Scores
  Advantage -> Overall_GPA
  Advantage -> Attendance
  Advantage -> AC_Ind
  Overall_GPA -> AC_Ind
}
")

plot( dag )
