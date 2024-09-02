#load libraries
library(plyr)
library(ggplot2)
library(BayesFactor)
library(psych)

#read in first experiment
d<-read.csv("experiments/game_1.csv")
#norm to max number
d$max1<-max(d$points1)*10
d$max2<-max(d$points2)*10
#get the game infor
info<-read.csv('144_games_info.csv', sep=";" )
#pre-assign info
d$fam<-info$game_family[1]
#looping through all games
for (i in 2:144){
  #load in new game data
  dummy<-read.csv(paste0("experiments/game_", i, '.csv'))
  #renormalize
  dummy$max1<-max(dummy$points1)*10
  dummy$max2<-max(dummy$points2)*10
  #assign family info
  dummy$fam<-info$game_family[i]
  #bind together
  d<-rbind(d, dummy)
}

#get data frame
dd<-d[(d$player1=="act_gpt4" & d$player2=="act_llama2") | (d$player1=="act_llama2" & d$player2=="act_gpt4"),]
#get gpt
gpt<-c(subset(dd, player1=="act_gpt4" & round==10)$total1, subset(dd, player2=="act_gpt4"& round==10)$total2)
#get claude
claude<-c(subset(dd, player2=="act_llama2" & round==10)$total1, subset(dd, player2=="act_llama2" & round==10)$total2)
#t test for difference
t.test(gpt-claude)
#Bayes factor
ttestBF(gpt-claude)

#get data frame
dd<-d[(d$player1=="act_gpt4" & d$player2=="act_gpt35") | (d$player1=="act_claude2" & d$player2=="act_gpt4"),]
#get gpt4
gpt4<-c(subset(dd, player1=="act_gpt4" & round==10)$total1, subset(dd, player2=="act_claude2"& round==10)$total2)
#get gpt3
gpt3<-c(subset(dd, player2=="act_gpt35" & round==10)$total1, subset(dd, player2=="act_gpt35" & round==10)$total2)
#t-test
t.test(gpt4-gpt3)
#Bayes factor
ttestBF(gpt4-gpt3)

#data frame
dd<-d[(d$player1=="act_gpt4" & d$player2=="act_claude1") | (d$player1=="act_gpt4" & d$player2=="act_claude1"),]
#get gpt
gpt<-c(subset(dd, player1=="act_gpt4" & round==10)$total1, subset(dd, player2=="act_gpt4"& round==10)$total2)
#get claude
claude<-c(subset(dd, player2=="act_gpt4" & round==10)$total1, subset(dd, player2=="act_claude1" & round==10)$total2)
#t-test
t.test(gpt-claude)
#Bayes factor
ttestBF(gpt-claude)

#get data frame
dd<-d[(d$player1=="act_gpt4" & d$player2=="act_claude2") | (d$player1=="act_claude2" & d$player2=="act_gpt4"),]
#get score for gpt
gpt<-c(subset(dd, player1=="act_gpt4" & round==10)$total1, subset(dd, player2=="act_gpt4"& round==10)$total2)
#get score for claude
claude<-c(subset(dd, player2=="act_claude2" & round==10)$total1, subset(dd, player2=="act_claude2" & round==10)$total2)
#t-test
t.test(gpt-claude)
#Bayes factor
ttestBF(gpt-claude)


#Example of how we get Cohen's d and its 95%CIs
t2d(6.2925, n1=length(gpt))
d.ci(0.3707891, n1=length(gpt)) 


#data for prisoners dilemma
d<-read.csv('./pd/experiment_pd.csv')
#gpt4
gpt4<-c(subset(d, player1=="act_gpt4")$points1, subset(d, player2=="act_gpt4" & round==10)$points2)
#all other models
allothers<-c(subset(d, player1!="act_gpt4")$points1, subset(d, player2!="act_gpt4" & round==10)$points2)
#t-test
t.test(gpt4,allothers)
#Cohen's d
cohen.d(c(gpt4,allothers), c(rep(1, length(gpt4)), rep(2, length(allothers))))
#Bayes factor
ttestBF(gpt4,allothers)

#Battle of the Sexes
d<-read.csv('./bos/experiment_bos.csv')
#gpt4
gpt4<-c(subset(d, player1=="act_gpt4")$points1, subset(d, player2=="act_gpt4" & round==10)$points2)
#all other models
allothers<-c(subset(d, player1!="act_gpt4")$points1, subset(d, player2!="act_gpt4" & round==10)$points2)
#t test
t.test(gpt4,allothers)
#Cohen's d
cohen.d(c(gpt4,allothers), c(rep(1, length(gpt4)), rep(2, length(allothers))))
#Bayes factor
ttestBF(gpt4,allothers)