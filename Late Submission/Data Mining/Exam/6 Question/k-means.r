#install.packages("factoextra")
data <- read.csv("D:/MSIT/Data Science/DataScience_2019501051/Late Submission/Data Mining/Exam/6 Question/Liver_data.csv",header=FALSE)
#seed - to randomly assign centroids. 
# k means custering startswith randomly assigning centroids
set.seed(123)

#no of centers = 4
#nstart - how many random sets should be chosen for 4 centers
#iter.max - maximum number of iterations allowed
res.km <- kmeans(scale(data[,-7]), 4, nstart = 25,iter.max=10)
#print(res.km)

#plotting and assigning points
fviz_cluster(res.km, data = data[, -7],
      
             palette = c("#2E9FDF", "#273746", "#E7B800","#D35400"),
             geom = "point",
             ellipse.type = "convex", 
             ggtheme = theme_bw()
)