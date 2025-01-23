# EDA: Exploratory Data Analysis for ASC AC Project- Rebecca Higbee Hull

# This is for 2022 only. Each row is a student. Each row is unique.

data <- read.csv("01_exploratory_powerschool_data.csv")


summary(data)


#distribution of overall gpa
hist_data <- hist(data$overall_gpa, breaks = 10, col = "blue", main = "Overall GPA Distribution", xlab = "Overall GPA")
# Add counts on top of each bar
text(hist_data$mids, hist_data$counts, labels = hist_data$counts, pos = 3, col = "black", cex = 0.8)

#Average overall gpa (excluding 0s)
mean(data$overall_gpa[data$overall_gpa != 0])
# 3.26 is the average overall gpa excluding 0s

#Median overall gpa (excluding 0s)
median(data$overall_gpa[data$overall_gpa != 0])
# 3.51 is the median overall gpa exlcuding 0s

#SD overall gpa (excluding 0s)
sd(data$overall_gpa[data$overall_gpa != 0])
# 0.78 is the sd of overall gpa excluding 0s

#Each row is a unique student.
length(data$a) == length(unique(data$a))


# Create a histogram with bin width of 10 and adjust x-axis limits
hist_obj <- hist(data$days_attended, 
                 breaks = seq(0, 180, by = 10), 
                 col = "lightblue", 
                 main = "Days Attended Distribution", 
                 xlab = "Days Attended", 
                 xlim = c(0, 180))

# Add counts on top of each bar
counts <- hist_obj$counts
bar_centers <- hist_obj$mids

text(x = bar_centers, y = counts, labels = counts, pos = 3, cex = 0.8, col = "black")

summary(data$days_attended)
boxplot(data$days_attended)


#sum of ac_ind
sum(data$ac_ind)
#1977 / 7277 students have taken AC before (ac_ind column). That's roughly 27%.

# Create a bar plot for ac_count
counts <- table(data$ac_count)  # Get the frequency count of each ac_count value
bar_centers <- barplot(counts, 
                       main = "Distribution of AC Count per Student", 
                       xlab = "AC Count", 
                       ylab = "Frequency", 
                       col = "lightblue", 
                       border = "black")

# Add counts on top of each bar
text(x = bar_centers, y = counts, labels = counts, pos = 3, cex = 0.8, col = "black")
mean(data$ac_count)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Distribution of ac_gpa
hist_data <- hist(data$ac_gpa, breaks = 10, col = "blue", main = "AC GPA Distribution", xlab = "AC GPA")

# Add counts on top of each bar
text(hist_data$mids, hist_data$counts, labels = hist_data$counts, pos = 3, col = "black", cex = 0.8)

# Average ac_gpa (excluding 0s)
mean_ac_gpa <- mean(data$ac_gpa[data$ac_gpa != 0])
print(paste("Average AC GPA (excluding 0s):", mean_ac_gpa))

# Median ac_gpa (excluding 0s)
median_ac_gpa <- median(data$ac_gpa[data$ac_gpa != 0])
print(paste("Median AC GPA (excluding 0s):", median_ac_gpa))

# SD ac_gpa (excluding 0s)
sd_ac_gpa <- sd(data$ac_gpa[data$ac_gpa != 0])
print(paste("SD of AC GPA (excluding 0s):", sd_ac_gpa))


#grade counts
# Filter out rows where current_grade is 0
filtered_data <- data[data$current_grade != 0, ]

# Create a bar plot for current_grade
counts <- table(filtered_data$current_grade)  # Get the frequency count of each current_grade value

# Find the maximum count value to adjust the y-axis range
max_count <- max(counts)

# Create the bar plot with adjusted y-axis limits
bar_centers <- barplot(counts, 
                       main = "Distribution of Current Grade (Excluding 0)", 
                       xlab = "Current Grade", 
                       ylab = "Frequency", 
                       col = "lightblue", 
                       border = "black", 
                       ylim = c(0, max_count * 1.1))  # Increase y-axis by 10% to ensure visibility

# Add counts on top of each bar
text(x = bar_centers, y = counts, labels = counts, pos = 3, cex = 0.8, col = "black")

#~~~~~~~~~~~~~
# Filter out rows where current_school is 0
filtered_data <- data[data$current_school != 0, ]

# Create a bar plot for current_school
counts <- table(filtered_data$current_school)  # Get the frequency count of each current_school value

# Find the maximum count value to adjust the y-axis range
max_count <- max(counts)

# Create the bar plot with adjusted y-axis limits
bar_centers <- barplot(counts, 
                       main = "Distribution of Current School (Excluding 0)", 
                       xlab = "Current School", 
                       ylab = "Frequency", 
                       col = "lightblue", 
                       border = "black", 
                       ylim = c(0, max_count * 1.1))  # Increase y-axis by 10% to ensure visibility

# Add counts on top of each bar
text(x = bar_centers, y = counts, labels = counts, pos = 3, cex = 0.8, col = "black")

#~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a bar plot for gender
counts <- table(data$gender)  # Get the frequency count of each gender value

# Find the maximum count value to adjust the y-axis range
max_count <- max(counts)

# Create the bar plot with adjusted y-axis limits
bar_centers <- barplot(counts, 
                       main = "Distribution of Gender", 
                       xlab = "Gender", 
                       ylab = "Frequency", 
                       col = "lightblue", 
                       border = "black", 
                       ylim = c(0, max_count * 1.1))  # Increase y-axis by 10% to ensure visibility

# Add counts on top of each bar
text(x = bar_centers, y = counts, labels = counts, pos = 3, cex = 0.8, col = "black")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Example for 'ethnicity' column
counts_ethnicity <- table(data$ethnicity)  # Get the frequency count of 'N' and 'Y'

# Find the maximum count value to adjust the y-axis range
max_count_ethnicity <- max(counts_ethnicity)

# Create the bar plot with adjusted y-axis limits
bar_centers_ethnicity <- barplot(counts_ethnicity, 
                                 main = "Distribution of Ethnicity", 
                                 xlab = "Ethnicity", 
                                 ylab = "Frequency", 
                                 col = "lightblue", 
                                 border = "black", 
                                 ylim = c(0, max_count_ethnicity * 1.1))  # Increase y-axis by 10%

# Add counts on top of each bar
text(x = bar_centers_ethnicity, y = counts_ethnicity, labels = counts_ethnicity, pos = 3, cex = 0.8, col = "black")

#~~~~~~~~~~~~~~~~~~~
# Get the frequency count of 'N' and 'Y' in 'amerindian_alaskan'
counts_amerindian <- table(data$amerindian_alaskan)

# Find the maximum count value to adjust the y-axis range
max_count_amerindian <- max(counts_amerindian)

# Create the bar plot with adjusted y-axis limits
bar_centers_amerindian <- barplot(counts_amerindian, 
                                  main = "Distribution of Amerindian Alaskan",
                                  xlab = "Amerindian Alaskan", 
                                  ylab = "Frequency", 
                                  col = "lightblue", 
                                  border = "black", 
                                  ylim = c(0, max_count_amerindian * 1.1))  # Increase y-axis by 10%

# Add counts on top of each bar
text(x = bar_centers_amerindian, y = counts_amerindian, labels = counts_amerindian, pos = 3, cex = 0.8, col = "black")


# For 'asian' column
counts_asian <- table(data$asian)
max_count_asian <- max(counts_asian)
bar_centers_asian <- barplot(counts_asian, 
                             main = "Distribution of Asian",
                             xlab = "Asian", 
                             ylab = "Frequency", 
                             col = "lightblue", 
                             border = "black", 
                             ylim = c(0, max_count_asian * 1.1))  # Increase y-axis by 10%
text(x = bar_centers_asian, y = counts_asian, labels = counts_asian, pos = 3, cex = 0.8, col = "black")

# For 'black_african_amer' column
counts_black_african <- table(data$black_african_amer)
max_count_black_african <- max(counts_black_african)
bar_centers_black_african <- barplot(counts_black_african, 
                                     main = "Distribution of Black African American",
                                     xlab = "Black African American", 
                                     ylab = "Frequency", 
                                     col = "lightblue", 
                                     border = "black", 
                                     ylim = c(0, max_count_black_african * 1.1))  # Increase y-axis by 10%
text(x = bar_centers_black_african, y = counts_black_african, labels = counts_black_african, pos = 3, cex = 0.8, col = "black")

# For 'hawaiian_pacific_isl' column
counts_hawaiian <- table(data$hawaiian_pacific_isl)
max_count_hawaiian <- max(counts_hawaiian)
bar_centers_hawaiian <- barplot(counts_hawaiian, 
                                main = "Distribution of Hawaiian Pacific Islander",
                                xlab = "Hawaiian Pacific Islander", 
                                ylab = "Frequency", 
                                col = "lightblue", 
                                border = "black", 
                                ylim = c(0, max_count_hawaiian * 1.1))  # Increase y-axis by 10%
text(x = bar_centers_hawaiian, y = counts_hawaiian, labels = counts_hawaiian, pos = 3, cex = 0.8, col = "black")

# For 'white' column
counts_white <- table(data$white)
max_count_white <- max(counts_white)
bar_centers_white <- barplot(counts_white, 
                             main = "Distribution of White",
                             xlab = "White", 
                             ylab = "Frequency", 
                             col = "lightblue", 
                             border = "black", 
                             ylim = c(0, max_count_white * 1.1))  # Increase y-axis by 10%
text(x = bar_centers_white, y = counts_white, labels = counts_white, pos = 3, cex = 0.8, col = "black")
############################################################


# For 'migrant' column
counts_migrant <- table(data$migrant)
max_count_migrant <- max(counts_migrant)
bar_centers_migrant <- barplot(counts_migrant, 
                               main = "Distribution of Migrant",
                               xlab = "Migrant", 
                               ylab = "Frequency", 
                               col = "lightblue", 
                               border = "black", 
                               ylim = c(0, max_count_migrant * 1.1))  # Increase y-axis by 10%
text(x = bar_centers_migrant, y = counts_migrant, labels = counts_migrant, pos = 3, cex = 0.8, col = "black")

# For 'gifted' column
counts_gifted <- table(data$gifted)
max_count_gifted <- max(counts_gifted)
bar_centers_gifted <- barplot(counts_gifted, 
                              main = "Distribution of Gifted",
                              xlab = "Gifted", 
                              ylab = "Frequency", 
                              col = "lightblue", 
                              border = "black", 
                              ylim = c(0, max_count_gifted * 1.1))  # Increase y-axis by 10%
text(x = bar_centers_gifted, y = counts_gifted, labels = counts_gifted, pos = 3, cex = 0.8, col = "black")

# For 'services_504' column
counts_services_504 <- table(data$services_504)
max_count_services_504 <- max(counts_services_504)
bar_centers_services_504 <- barplot(counts_services_504, 
                                    main = "Distribution of Services 504",
                                    xlab = "Services 504", 
                                    ylab = "Frequency", 
                                    col = "lightblue", 
                                    border = "black", 
                                    ylim = c(0, max_count_services_504 * 1.1))  # Increase y-axis by 10%
text(x = bar_centers_services_504, y = counts_services_504, labels = counts_services_504, pos = 3, cex = 0.8, col = "black")

# For 'military_child' column
counts_military_child <- table(data$military_child)
max_count_military_child <- max(counts_military_child)
bar_centers_military_child <- barplot(counts_military_child, 
                                      main = "Distribution of Military Child",
                                      xlab = "Military Child", 
                                      ylab = "Frequency", 
                                      col = "lightblue", 
                                      border = "black", 
                                      ylim = c(0, max_count_military_child * 1.1))  # Increase y-axis by 10%
text(x = bar_centers_military_child, y = counts_military_child, labels = counts_military_child, pos = 3, cex = 0.8, col = "black")

# For 'refugee_student' column
counts_refugee_student <- table(data$refugee_student)
max_count_refugee_student <- max(counts_refugee_student)
bar_centers_refugee_student <- barplot(counts_refugee_student, 
                                       main = "Distribution of Refugee Student",
                                       xlab = "Refugee Student", 
                                       ylab = "Frequency", 
                                       col = "lightblue", 
                                       border = "black", 
                                       ylim = c(0, max_count_refugee_student * 1.1))  # Increase y-axis by 10%
text(x = bar_centers_refugee_student, y = counts_refugee_student, labels = counts_refugee_student, pos = 3, cex = 0.8, col = "black")

# For 'immigrant' column
counts_immigrant <- table(data$immigrant)
max_count_immigrant <- max(counts_immigrant)
bar_centers_immigrant <- barplot(counts_immigrant, 
                                 main = "Distribution of Immigrant",
                                 xlab = "Immigrant", 
                                 ylab = "Frequency", 
                                 col = "lightblue", 
                                 border = "black", 
                                 ylim = c(0, max_count_immigrant * 1.1))  # Increase y-axis by 10%
text(x = bar_centers_immigrant, y = counts_immigrant, labels = counts_immigrant, pos = 3, cex = 0.8, col = "black")

# For 'reading_intervention' column
counts_reading_intervention <- table(data$reading_intervention)
max_count_reading_intervention <- max(counts_reading_intervention)
bar_centers_reading_intervention <- barplot(counts_reading_intervention, 
                                            main = "Distribution of Reading Intervention",
                                            xlab = "Reading Intervention", 
                                            ylab = "Frequency", 
                                            col = "lightblue", 
                                            border = "black", 
                                            ylim = c(0, max_count_reading_intervention * 1.1))  # Increase y-axis by 10%
text(x = bar_centers_reading_intervention, y = counts_reading_intervention, labels = counts_reading_intervention, pos = 3, cex = 0.8, col = "black")

# For 'passed_civics_exam' column
counts_passed_civics_exam <- table(data$passed_civics_exam)
max_count_passed_civics_exam <- max(counts_passed_civics_exam)
bar_centers_passed_civics_exam <- barplot(counts_passed_civics_exam, 
                                          main = "Distribution of Passed Civics Exam",
                                          xlab = "Passed Civics Exam", 
                                          ylab = "Frequency", 
                                          col = "lightblue", 
                                          border = "black", 
                                          ylim = c(0, max_count_passed_civics_exam * 1.1))  # Increase y-axis by 10%
text(x = bar_centers_passed_civics_exam, y = counts_passed_civics_exam, labels = counts_passed_civics_exam, pos = 3, cex = 0.8, col = "black")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Assuming your data frame is named 'data' and it has columns from teacher_1 to teacher_22

# Step 1: Select the teacher columns
teacher_columns <- data[, grep("^teacher_", colnames(data))]

# Step 2: Combine all the teacher columns into a single vector
teacher_ids <- as.vector(t(teacher_columns))

# Step 3: Remove any NA or empty values (if necessary)
teacher_ids <- teacher_ids[!is.na(teacher_ids) & teacher_ids != ""]

# Step 4: Count occurrences of each teacher ID
teacher_count <- table(teacher_ids)

# Step 5: View the count of each teacher ID
print(teacher_count)
###################
# Assuming your data frame is named 'data' and it has columns from teacher_1 to teacher_22
library(knitr)

# Step 1: Select the teacher columns
teacher_columns <- data[, grep("^teacher_", colnames(data))]

# Step 2: Combine all the teacher columns into a single vector
teacher_ids <- as.vector(t(teacher_columns))

# Step 3: Remove any NA or empty values (if necessary)
teacher_ids <- teacher_ids[!is.na(teacher_ids) & teacher_ids != ""]

# Step 4: Count occurrences of each teacher ID
teacher_count <- table(teacher_ids)

# Step 5: Convert the table to a data frame for a better display
teacher_count_df <- as.data.frame(teacher_count)

# Step 6: Rename the columns for better readability
colnames(teacher_count_df) <- c("Teacher_ID", "Count")

# Step 7: Print the table in a nice format
kable(teacher_count_df, format = "html", caption = "Teacher ID Count Table")








################################################################################
#compare ac gpa to overall gpa

cor(data$ac_gpa, data$overall_gpa, use = "complete.obs")
# r = 0.525

# ac gpa vs overall gpa scatterplot
library(ggplot2)
ggplot(data, aes(x = overall_gpa, y = ac_gpa)) +
  geom_point() +
  labs(
    title = "AC GPA vs Overall GPA",
    x = "Overall GPA",
    y = "AC GPA"
  )

#scatterplot again but without points with ac gpa = 0 (so only students who have taken ac)
ggplot(subset(data, ac_gpa != 0), aes(x = overall_gpa, y = ac_gpa)) +
  geom_point() +
  labs(
    title = "AC GPA vs Overall GPA (Filtered to exclude ac gpa of 0)",
    x = "Overall GPA",
    y = "AC GPA"
  )


#####
# Install ggpmisc if not already installed
install.packages("ggpmisc")
library(ggplot2)
library(ggpmisc)

# Filter data where ac_gpa != 0
filtered_data <- subset(data, ac_gpa != 0)

# Create scatter plot with regression line and equation
ggplot(filtered_data, aes(x = overall_gpa, y = ac_gpa)) +
  geom_point() +
  geom_smooth(method = "lm", color = "blue", se = FALSE) + # Add regression line
  stat_poly_eq(
    aes(label = paste(..eq.label.., ..rr.label.., sep = "~~~")),
    formula = y ~ x,
    parse = TRUE
  ) +
  labs(
    title = "AC GPA vs Overall GPA (Filtered to exclude AC GPA of 0)",
    x = "Overall GPA",
    y = "AC GPA"
  )

# Calculate the correlation
r_value <- cor(filtered_data$overall_gpa, filtered_data$ac_gpa, use = "complete.obs")
print(r_value)
# r = 0.69 for the ac gpa vs overall gpa for those who have an ac gpa
#######




# not filtered out ac gpa of 0. Makes a boxplot

install.packages("tidyr")  # Install if you don't have it
library(tidyr)             # Load the package

install.packages("reshape2")  # Install if you don't have it
library(reshape2)

data_long <- melt(data, measure.vars = c("ac_gpa", "overall_gpa"), 
                  variable.name = "GPA_Type", value.name = "GPA")

ggplot(data_long, aes(x = GPA_Type, y = GPA)) +
  geom_boxplot(fill = c("lightgreen", "lightblue")) +
  labs(
    title = "Boxplot of AC GPA and Overall GPA",
    x = "GPA Type",
    y = "GPA"
  )

###################

#boxplot of the data with filtered ac gpa of 0 out.

filtered_data <- subset(data, ac_gpa != 0)
library(ggplot2)
library(tidyr)

# Transform data into long format for boxplot
filtered_long <- pivot_longer(
  filtered_data,
  cols = c(ac_gpa, overall_gpa),
  names_to = "GPA_Type",
  values_to = "GPA"
)

# Create the boxplot
ggplot(filtered_long, aes(x = GPA_Type, y = GPA)) +
  geom_boxplot(fill = c("lightgreen", "lightblue")) +
  labs(
    title = "Boxplot of AC GPA and Overall GPA (Filtered Data)",
    x = "GPA Type",
    y = "GPA"
  )

#get summary statistics for ac gpa and overal gpa

# Filter the data to exclude rows where ac_gpa == 0
filtered_data <- subset(data, ac_gpa != 0)

# Calculate mean and median for ac_gpa and overall_gpa using base R
mean_ac_gpa <- mean(filtered_data$ac_gpa, na.rm = TRUE)
median_ac_gpa <- median(filtered_data$ac_gpa, na.rm = TRUE)
mean_overall_gpa <- mean(filtered_data$overall_gpa, na.rm = TRUE)
median_overall_gpa <- median(filtered_data$overall_gpa, na.rm = TRUE)

# Print the summary statistics
cat("Mean AC GPA:", mean_ac_gpa, "\n")
cat("Median AC GPA:", median_ac_gpa, "\n")
cat("Mean Overall GPA:", mean_overall_gpa, "\n")
cat("Median Overall GPA:", median_overall_gpa, "\n")




