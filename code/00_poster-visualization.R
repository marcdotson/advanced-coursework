# Load packages.
library(tidyverse)

# Load 2023 data only.
# courses <- read_csv("data/poster-visualization/transcript-courses.csv")
course_member <- read_csv("data/poster-visualization/course-membership.csv")
course_master <- read_csv("data/poster-visualization/course-master.csv")
student <- read_csv("data/poster-visualization/student-table.csv")
transcript <- read_csv("data/poster-visualization/student-transcript.csv")

adv_courses <- course_member |> 
  select(StudentNumber, CourseRecordID) |> 
  left_join(
    course_master |> 
      select(CourseRecordID, CourseTitle)
  ) |> 
  mutate(AdvInd = str_detect(CourseTitle, "AP")) |> 
  select(StudentNumber, AdvInd) |> 
  group_by(StudentNumber) |> 
  summarize(AdvCount = sum(AdvInd))

data <- adv_courses |> 
  left_join(transcript, join_by(StudentNumber)) |> 
  left_join(student, join_by(StudentNumber)) |>
  filter(Gender != "U") |> 
  mutate(
    EllParentLangage_New = ifelse(EllParentLanguage == "ENG", "ENG", "OTH"),
    EllNativeLanguage_New = ifelse(EllNativeLanguage == "ENG", "ENG", "OTH"),
    AdvInd = ifelse(AdvCount >= 1, "Yes", "No"),
    Gender_New = ifelse(Gender == "F", "Female", "Male"),
    Ethnicity_New = ifelse(Ethnicity == "N", "Not Hispanic", "Hispanic")
  ) |> 
  drop_na(AdvInd)

data |> count(AdvInd)

data |> 
  ggplot(aes(x = AdvInd, y = CumulativeUnweightedGPA)) +
  geom_jitter(size = 2, alpha = 0.15) +
  geom_smooth(method = "lm")
  # facet_grid(~ SchoolMembership)

data |> 
  # count(AdvInd, Gender_New, Ethnicity_New) |> 
  # count(AdvInd, Gender_New) |> 
  count(AdvInd) |> 
  pivot_wider(names_from = AdvInd, values_from = n) |> 
  mutate(Total = No + Yes) |> 
  mutate(Prop_Yes = Yes / Total)

data |> 
  ggplot(aes(x = CumulativeUnweightedGPA, fill = AdvInd)) +
  geom_histogram(alpha = 1) +
  # facet_grid(Ethnicity_New ~ Gender_New, scales = "free") +
  # facet_wrap( ~ Gender_New, scales = "free") +
  facet_wrap( ~ Gender_New, scales = "free") +
  scale_fill_brewer(name = "Taking AP") +
  theme_minimal() +
  theme(legend.position = "bottom") +
  labs(
    title = "Secondary School GPA Distributions",
    subtitle = "2023 Cache County School District Data",
    x = "Cumulative GPAs",
    y = ""
  )

ggsave("figures/gpa-distributions.jpg", width = 5, height = 3, units = "in")

data |> 
  filter(AdvInd == "Yes") |> 
  count(Gender_New, Ethnicity_New) |> 
  # bind_rows(
  #   data |> count(AdvInd, Gender_New) |> rename(temp = Gender_New),
  #   data |> count(AdvInd, Ethnicity_New) |> rename(temp = Ethnicity_New)
  # ) |> 
  ggplot(aes(x = Gender_New, y = n, fill = Ethnicity_New)) +
  geom_col(position = "fill")
  # facet_grid(Ethnicity_New ~ Gender_New, scales = "free")
