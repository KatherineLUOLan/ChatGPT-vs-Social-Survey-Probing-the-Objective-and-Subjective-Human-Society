#-------------------------200 group and compare with cencus-------------------------------------------
library(dplyr)
library(Rmisc)
library(ggplot2) 
setwd('/Users/luyu/Library/CloudStorage/OneDrive-HKUST(Guangzhou)/GPT-survey/中文模型/gpt_200_30times')
data <- read.csv("china_cencus_gpt_6000.csv")
# recode the numeric vairables
data$gender <- as.numeric(factor(data$Gender, levels = c("Male", "Female"))) - 1

data$region <- as.numeric(factor(data$Region, levels = c("Urban", "Rural"))) - 1

data$age_group <- cut(data$Age, 
                      breaks = c(13, 59, Inf), 
                      labels = c("14-59", "60+"), 
                      right = TRUE)

data$edu <- as.numeric(factor(data$Edu, levels = c(
  "Below primary school",
  "Primary school",
  "Middle school",
  "High school (including technical school)",
  "Junior college",
  "Bachelor's degree",
  "Graduate degree or above"
), labels = c(1, 2, 3, 4, 5, 5, 5)))

#calculate mean and plot-200
calculate_means <- function(data, n) {
  split_data <- split(data, ceiling(seq_along(data)/n))
  means <- sapply(split_data, mean, na.rm = TRUE)
  return(means)
}
#----------------plot gender---------------------
gender_means <- calculate_means(data$gender, 200)
# 计算数据的均值和标准差
mean_gender <- mean(gender_means)
sd_gender <- sd(gender_means)
# 计算置信区间
ci_lower_gen <- mean_gender - 1.96 * sd_gender
ci_upper_gen <- mean_gender + 1.96 * sd_gender
# 生成用于绘制正态分布曲线的x值
x_gender <- seq(mean_gender - 3 * sd_gender, mean_gender + 3 * sd_gender, length=100)
# 计算正态分布概率密度
y_gender <- dnorm(x_gender, mean=mean_gender, sd=sd_gender)
#画分布图
png(filename = "gender_distribution.png", width =2200 , height = 1635, res = 300)
par(family = "Georgia", font = 1)
hist(gender_means, 
     main="", 
     xlab="Gender Means", 
     col="#b2a8cb",  # 设置填充颜色为透
     breaks=2,
     prob=TRUE,
     ylim = c(0,200),
     xlim = c(0.485,0.51)) # 设定分段数为10，可以根据需要调整

# 绘制正态分布曲线/置信区间以及
lines(x_gender, y_gender,col = "black",lwd=1)
abline(v=mean_gender, col = "black", lwd = 2.5, lty = 3) 
abline(v=ci_lower_gen, col = "darkgray", lwd = 2, lty = 3)
abline(v=ci_upper_gen, col = "darkgray", lwd = 2, lty = 3)
abline(v=0.4876, col = "red", lwd = 2.5, lty = 3)
legend("topleft",  
       legend=c("95%CI", "Mean of GPT sampling", "Census value"), 
       col=c("darkgray", "black", "red"), 
       lty=3, 
       lwd=2,
       bty="n",
       xpd = TRUE,
       inset = c(-0.05, -0.15),
       cex=0.6)
text(x = 0.5017, y=200,labels = "50.17%(female)", pos = 4, col = "black",cex=0.7)
text(x = 0.4876, y=200, labels = "48.76%", pos = 4, col = "black", cex=0.7)
dev.off()


#--------------------plot age-------------------
age_means <- calculate_means(data$Age, 200)
#计算数据的均值和标准差
mean_age <- mean(age_means)
sd_age <- sd(age_means)
#计算ci
ci_lower_age <- mean_age - 1.96 * sd_age
ci_upper_age <- mean_age + 1.96 * sd_age
#计算概率分布密度
x_age <- seq(mean_age - 3 * sd_age, mean_age + 3* sd_age, length=100)
y_age <- dnorm(x_age, mean=mean_age, sd=sd_age)
#画图
png(filename = "age_distribution.png",width =2200 , height = 1635, res = 300)
par(family = "Georgia", font = 1)
hist(age_means, 
     main="", 
     xlab="Age Means", 
     col="#b2a8cb",  # 设置填充颜色为透明
     breaks=10,
     ylim=c(0,1.2),
     xlim=c(37,40),
     prob=TRUE) 
lines(x_age, y_age,col = "black",lwd=1)
abline(v=mean_age, col = "black", lwd = 2.5, lty = 3) 
abline(v=ci_lower_age, col = "darkgray", lwd = 2, lty = 3)
abline(v=ci_upper_age, col = "darkgray", lwd = 2, lty = 3)
abline(v=39.3, col = "red", lwd = 2.5, lty = 3) 
legend("topleft",  
       legend=c("95%CI", "Mean of GPT sampling", "Census value"), 
       col=c("darkgray", "black", "red"), 
       lty=2, 
       lwd=2,
       bty="n",
       xpd = TRUE,
       inset = c(-0.05, -0.15),
       cex=0.6)
text(x = 39.93, y=1.1,labels = "39.93", pos = 4, col = "black",cex=0.6)
text(x = 39.3, y=1.1, labels = "39.3(ACS 2020 mean)", pos = 4, col = "black", cex=0.6)
dev.off()


#--------------------plot education-------------------
edu_means <- calculate_means(data$edu, 200)
#计算数据的均值和标准差
mean_edu <- mean(edu_means)
sd_edu <- sd(edu_means)
#计算ci
ci_lower_edu <- mean_edu - 1.96 * sd_edu
ci_upper_edu <- mean_edu + 1.96 * sd_edu
#计算概率分布密度
x_edu <- seq(mean_edu - 3 * sd_edu, mean_edu + 3* sd_edu, length=100)
y_edu <- dnorm(x_edu, mean=mean_edu, sd=sd_edu)
#画图
png(filename = "edu_distribution.png", width =2200 , height = 1635, res = 300)
par(family = "Georgia", font = 1)
hist(edu_means, 
     main="", 
     xlab="Education Means", 
     col="#b2a8cb",
     breaks = 6,
     prob=TRUE,
     ylim=c(0,8),
     xlim=c(3,4.2))
lines(x_edu, y_edu,col = "black",lwd=1)
abline(v=mean_edu, col = "black", lwd = 2.5, lty = 3) 
abline(v=ci_lower_edu, col = "darkgray", lwd = 2, lty = 3)
abline(v=ci_upper_edu, col = "darkgray", lwd = 2, lty = 3)
abline(v=3.01, col = "red", lwd = 2.5, lty = 3) 
legend("topleft",  
       legend=c("95%CI", "Mean of GPT sampling", "Census value"), 
       col=c("darkgray", "black", "red"), 
       lty=2, 
       lwd=2,
       bty="n",
       xpd = TRUE,
       inset = c(-0.05, -0.15),
       cex=0.6)
text(x = 3.01, y=8,labels = "3.01", pos = 4, col = "black",cex=0.7)
text(x = 3.90 , y=8, labels = "3.90", pos = 4, col = "black", cex=0.7)
dev.off()

#---------plot region-------
region_means <- calculate_means(data$region, 200)
#计算数据的均值和标准差
mean_region <- mean(region_means)
sd_region <- sd(region_means)
#计算ci
ci_lower_region <- mean_region - 1.96 * sd_region
ci_upper_region <- mean_region + 1.96 * sd_region
#计算概率分布密度
x_region <- seq(mean_region - 3 * sd_region, mean_region + 3* sd_region, length=100)
y_region <- dnorm(x_region, mean=mean_region, sd=sd_region)

png(filename = "region_distribution.png", width =2200 , height = 1635, res = 300)
par(family = "Georgia", font = 1)
hist(region_means, 
     main="", 
     xlab="Region Means", 
     col="#b2a8cb",
     breaks = 4,
     prob=TRUE,
     ylim = c(0,35),
     xlim = c(0.35,0.5))
lines(x_region, y_region,col = "black",lwd=1)
abline(v=mean_region, col = "black", lwd = 2.5, lty = 3) 
abline(v=ci_lower_region, col = "darkgray", lwd = 2, lty = 3)
abline(v=ci_upper_region, col = "darkgray", lwd = 2, lty = 3)
abline(v=0.361, col = "red", lwd = 2.5, lty = 3) 
legend("topleft",  
       legend=c("95%CI", "Mean of GPT sampling", "Census value"), 
       col=c("darkgray", "black", "red"), 
       lty=2, 
       lwd=2,
       bty="n",
       xpd = TRUE,
       inset = c(-0.05, -0.15),
       cex=0.6)
text(x = 0.361, y=35,labels = "36.1%(%rural)", pos = 4, col = "black",cex=0.7)
text(x = 0.426, y=35, labels = "42.6%", pos = 4, col = "black", cex=0.7)
dev.off()

#--------------------add dummy variable and plot-------
data$age_14_59 <- ifelse(data$age_group == '14-59', 1, 0)
data$age_60 <- ifelse(data$age_group == '60+', 1, 0)

# Create eductaion dummy variables
data$edu <- as.numeric(factor(data$Edu, levels = c(
  "Below primary school",
  "Primary school",
  "Middle school",
  "High school (including technical school)",
  "Junior college",
  "Bachelor's degree",
  "Graduate degree or above"
), labels = c(1, 2, 2, 2, 3, 3, 3)))

data$low_edu <- ifelse(data$edu == '1', 1, 0)
data$middle_edu <- ifelse(data$edu == '2', 1, 0)
data$high_edu <- ifelse(data$edu == '3', 1, 0)
#-----------------age categorical plot--------------------------
#-----------------age 14-59--------------------------
age_14_59_means <- calculate_means(data$age_14_59, 200)
# 计算 age_18_24 的均值和标准差
mean_age_14_59 <- mean(age_14_59_means)
sd_age_14_59 <- sd(age_14_59_means)
ci_lower_age_14_59 <- mean_age_14_59 - 1.96 * sd_age_14_59
ci_upper_age_14_59 <- mean_age_14_59 + 1.96 * sd_age_14_59

x_age_14_59 <- seq(mean_age_14_59 - 3 * sd_age_14_59, mean_age_14_59 + 3 * sd_age_14_59, length=100)
y_age_14_59 <- dnorm(x_age_14_59, mean=mean_age_14_59, sd=sd_age_14_59)

# 画图
png(filename = "age1_distribution.png", width = 2200, height = 1635, res = 300)
par(family = "Georgia", font = 1)
hist(age_14_59_means, 
     main="", 
     xlab="Age 14-59 Means", 
     col="#b2a8cb",
     breaks=5,
     prob=TRUE,
     ylim=c(0,60),
     xlim=c(0.75,1))

lines(x_age_14_59, y_age_14_59, col = "black", lwd=1)
abline(v=mean_age_14_59, col = "black", lwd = 2.5, lty = 3) 
abline(v=ci_lower_age_14_59, col = "darkgray", lwd = 2, lty = 3)
abline(v=ci_upper_age_14_59, col = "darkgray", lwd = 2, lty = 3)
abline(v=0.772, col = "red", lwd = 2.5, lty = 3) 

legend("topleft",  
       legend=c("95%CI", "Mean of GPT sampling", "Census value"), 
       col=c("darkgray", "black", "red"), 
       lty=2, 
       lwd=2,
       bty="n",
       xpd = TRUE,
       inset = c(-0.05, -0.15),
       cex=0.6)

text(x = 0.772, y = 60, labels = "77.2%", pos = 4, col = "black", cex = 0.7)
text(x = 0.934, y = 60, labels = "93.4%", pos = 4, col = "black", cex = 0.7)

dev.off()

#-----------------age 60 and more--------------------------
age_60_means <- calculate_means(data$age_60, 200)
mean_age_60 <- mean(age_60_means)
sd_age_60 <- sd(age_60_means)
# 计算置信区间
ci_lower_age_60 <- mean_age_60 - 1.96 * sd_age_60
ci_upper_age_60 <- mean_age_60 + 1.96 * sd_age_60

# 计算概率分布密度
x_age_60 <- seq(mean_age_60 - 3 * sd_age_60, mean_age_60 + 3 * sd_age_60, length=100)
y_age_60 <- dnorm(x_age_60, mean=mean_age_60, sd=sd_age_60)

# 画图
png(filename = "age4_distribution.png", width = 2200, height = 1635, res = 300)
par(family = "Georgia", font = 1)
hist(age_60_means, 
     main="", 
     xlab="Age 60 and above Means", 
     col="#b2a8cb",
     breaks=5,
     prob=TRUE,
     ylim=c(0,50),
     xlim=c(0.0,0.25))

# 绘制正态分布曲线
lines(x_age_60, y_age_60, col = "black", lwd=1)

# 绘制均值和置信区间
abline(v=mean_age_60, col = "black", lwd = 2.5, lty = 3) 
abline(v=ci_lower_age_60, col = "darkgray", lwd = 2, lty = 3)
abline(v=ci_upper_age_60, col = "darkgray", lwd = 2, lty = 3)
abline(v=0.228, col = "red", lwd = 2.5, lty = 3) 

# 添加图例
legend("topleft",  
       legend=c("95%CI", "Mean of GPT sampling", "Census value"), 
       col=c("darkgray", "black", "red"), 
       lty=2, 
       lwd=2,
       bty="n",
       xpd = TRUE,
       inset = c(-0.05, -0.15),
       cex=0.6)

# 添加文本
text(x = 0.228, y = 50, labels = "22.8%", pos = 4, col = "black", cex = 0.7)
text(x = 0.067, y = 50, labels = "6.7%", pos = 4, col = "black", cex = 0.7)

# 关闭设备
dev.off()

#-----------------edu categorical plot--------------------------
#------------------low_edu
low_edu_means <- calculate_means(data$low_edu, 200)
#计算数据的均值和标准差
mean_low_edu <- mean(low_edu_means)
sd_low_edu <- sd(low_edu_means)

#计算ci
ci_lower_low_edu <- mean_low_edu - 1.96 * sd_low_edu
ci_upper_low_edu <- mean_low_edu + 1.96 * sd_low_edu
#计算概率分布密度
x_low_edu <- seq(mean_low_edu - 3 * sd_low_edu, mean_low_edu + 3 * sd_low_edu, length = 100)
y_low_edu <- dnorm(x_low_edu, mean=mean_low_edu, sd=sd_low_edu)
#画图
png(filename = "low_edu_distribution.png", width = 2200, height = 1635, res = 300)
par(family = "Georgia", font = 1)
hist(low_edu_means, 
     main="", 
     xlab="Low Education Means", 
     col="#b2a8cb",
     breaks=5,
     prob=TRUE,
     ylim=c(0,40),
     xlim = c(0.02,0.12))
lines(x_low_edu, y_low_edu, col = "black", lwd = 1)


# 绘制均值和置信区间
abline(v = mean_low_edu, col = "black", lwd = 2.5, lty = 3) 
abline(v = ci_lower_low_edu, col = "darkgray", lwd = 2, lty = 3)
abline(v = ci_upper_low_edu, col = "darkgray", lwd = 2, lty = 3)
abline(v=0.1017, col = "red", lwd = 2.5, lty = 3) 
legend("topleft",  
       legend = c("95%CI", "Mean of GPT sampling", "Census value"), 
       col = c("darkgray", "black", "red"), 
       lty = 2, 
       lwd = 2,
       bty = "n",
       xpd = TRUE,
       inset = c(-0.05, -0.15),
       cex = 0.6)
text(x = 0.1017, y=40, labels = "10.17%", pos = 4, col = "black", cex=0.7)
text(x = 0.062, y=40, labels = "6.2%", pos = 4, col = "black", cex=0.7)
dev.off()

#------------------middle_edu
middle_edu_means <- calculate_means(data$middle_edu, 200)
#计算数据的均值和标准差
mean_middle_edu <- mean(middle_edu_means)
sd_middle_edu <- sd(middle_edu_means)

#计算ci
ci_lower_middle_edu <- mean_middle_edu - 1.96 * sd_middle_edu
ci_upper_middle_edu <- mean_middle_edu + 1.96 * sd_middle_edu
#计算概率分布密度
x_middle_edu <- seq(mean_middle_edu - 3 * sd_middle_edu, mean_middle_edu + 3 * sd_middle_edu, length = 100)
y_middle_edu <- dnorm(x_middle_edu, mean=mean_middle_edu, sd=sd_middle_edu)
#画图
png(filename = "Medium_edu_distribution.png", width = 2200, height = 1635, res = 300)
par(family = "Georgia", font = 1)
hist(middle_edu_means, 
     main="", 
     xlab="Medium Education Means", 
     col = "#b2a8cb",
     breaks=5,
     prob=TRUE,
     ylim=c(0,35),
     xlim = c(0.3,0.8))
lines(x_middle_edu, y_middle_edu, col = "black", lwd = 1)

# 绘制均值和置信区间
abline(v = mean_middle_edu, col = "black", lwd = 2.5, lty = 3) 
abline(v = ci_lower_middle_edu, col = "darkgray", lwd = 2, lty = 3)
abline(v = ci_upper_middle_edu, col = "darkgray", lwd = 2, lty = 3)
abline(v=0.7436, col = "red", lwd = 2.5, lty = 3) 
legend("topleft",  
       legend = c("95%CI", "Mean of GPT sampling", "Census value"), 
       col = c("darkgray", "black", "red"), 
       lty = 2, 
       lwd = 2,
       bty = "n",
       xpd = TRUE,
       inset = c(-0.07, -0.15),
       cex = 0.6)
text(x = 0.7436, y=35, labels = "74.36%", pos = 4, col = "black", cex=0.7)
text(x = 0.474, y=35, labels = "47.1%", pos = 4, col = "black", cex=0.7)
dev.off()

#------------------high_edu
high_edu_means <- calculate_means(data$high_edu, 200)
#计算数据的均值和标准差
mean_high_edu <- mean(high_edu_means)
sd_high_edu <- sd(high_edu_means)

#计算ci
ci_lower_high_edu <- mean_high_edu - 1.96 * sd_high_edu
ci_upper_high_edu <- mean_high_edu + 1.96 * sd_high_edu
#计算概率分布密度
x_high_edu <- seq(mean_high_edu - 3 * sd_high_edu, mean_high_edu + 3 * sd_high_edu, length = 100)
y_high_edu <- dnorm(x_high_edu, mean = mean_high_edu, sd = sd_high_edu)
#画图
png(filename = "high_edu_distribution.png", width = 2200, height = 1635, res = 300)
par(family = "Georgia", font = 1)
hist(high_edu_means, 
     main="", 
     xlab="High Education Means", 
     col = "#b2a8cb",
     breaks=5,
     prob=TRUE,
     ylim=c(0,30),
     xlim = c(0.1,0.6))
lines(x_high_edu, y_high_edu, col = "black", lwd = 1)
abline(v = mean_high_edu, col = "black", lwd = 2.5, lty = 3) 
abline(v = ci_lower_high_edu, col = "darkgray", lwd = 2, lty = 3)
abline(v = ci_upper_high_edu, col = "darkgray", lwd = 2, lty = 3)
abline(v=0.1547, col = "red", lwd = 2.5, lty = 3) 
legend("topleft",  
       legend = c("95%CI", "Mean of GPT sampling", "Census value"), 
       col = c("darkgray", "black", "red"), 
       lty = 2, 
       lwd = 2,
       bty = "n",
       xpd = TRUE,
       inset = c(-0.05, -0.15),
       cex = 0.6)
text(x = 0.1547, y=30, labels = "15.47%", pos = 4, col = "black", cex=0.7)
text(x = 0.4642, y=30, labels = "46.2%", pos = 4, col = "black", cex=0.7)
dev.off()

