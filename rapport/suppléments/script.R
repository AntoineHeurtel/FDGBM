#importation des données
data = read.table("tauxIdentité-R.csv", h=T, sep="\t", dec=",")

#renommage des header
colnames(data)[1] <- 'taux'
colnames(data)[2] <- 'sensibilité'
colnames(data)[3] <- 'SeIC95'
colnames(data)[4] <- 'spécificité'
colnames(data)[5] <- 'SpIC95'
colnames(data)[6] <- 'précision'
colnames(data)[7] <- 'PrIC95'


#graphique
plot(x = data$taux, y = data$sensibilité, col = 'purple', type = "b", pch = 3, lty = 1,
     #main = 'Évolution des valeurs de sensibilité, spécificité et de la précision\nen fonction du taux',
     ylab = 'valeur', xlab = 'taux d’identité') #ylim = c(0,1.05)
points(x=data$taux, y = data$spécificité, col = 'red', type = "b", pch = 3, lty = 1)
points(x=data$taux, y = data$précision, col = 'green', type = "b", pch = 3, lty = 1)

legend('bottomleft', legend=c("sensibilité", "spécificité", "précision"),
       col=c("purple", "red", "green"), lty = 1)

#IC 95
segments(x0 = data$taux, y0 = data$sensibilité - data$SeIC95/2,
         x1 = data$taux, y1 = data$sensibilité + data$SeIC95/2,
         col = "purple", lty = 3)
segments(x0 = data$taux, y0 = data$spécificité - data$SpIC95/2,
         x1 = data$taux, y1 = data$spécificité + data$SpIC95/2,
         col = "red", lty = 3)
segments(x0 = data$taux, y0 = data$précision - data$PrIC95/2,
         x1 = data$taux, y1 = data$précision + data$PrIC95/2,
         col = "green", lty = 3)
legend('bottomleft', legend=c("sensibilité", "spécificité", "précision", "IC95"),
       col=c("purple", "red", "green","purple"), lty=c(1,1,1,3))
