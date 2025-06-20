library(magrittr)
library(dplyr)

MC <- function(L_max, L_min = 112.6482, nDigits=4){
  # Function to find michelson contrast using L_min as the background luminance in PsychoPy units
  michelson_contrast <- (L_max-L_min) / (L_max+L_min)
  michelson_contrast %<>% round(nDigits)
  return(michelson_contrast)
}

toCandela <- function(x, nDigits = 10){
  CandelaPerMeterSquared <- (x * 112.417) + 112.6482
  CandelaPerMeterSquared %<>% round(nDigits)
  return(CandelaPerMeterSquared)
}

 penalized_accuracy <- function(p, fp, epsilon=1e-6){
  score = (p - fp) / (1 - fp + epsilon)
  return(max(0, min(1, score))) # Ensures results stay between 0 and 1
}

files <- list.files("../Experiment_outputs",full.names = TRUE) %>% subset(endsWith(.,'.csv'))

data <- lapply(files, function(f) 
  read.csv(f, stringsAsFactors = TRUE)) %>% 
  bind_rows() %>% 
  subset(!endsWith(as.character(label),'_null'))
data$label %<>% droplevels()

data$id %<>% as.factor()
data$FC_michelson <- data$FC %>% toCandela %>% MC
data$FC_michelson_c <- scale(data$FC_michelson, scale = F) %>% c()
data$TC_michelson <- data$TC %>% toCandela %>% MC
data$TC_michelson_c <- scale(data$TC_michelson,scale = F) %>% c()

data$TC_f <- ggplot2::cut_number(data$TC_michelson, n = 3, labels = c('Low','Medium','High'))
# We must set the cutoff values over the entire data frame so all participants have the same cutoff values
medRange <- data[which(data$TC_f == 'Medium'),'TC_michelson'] %>% range()

baselines <- data %>% 
  filter(label == '100') %>% 
  group_by(id) %>% 
  summarise(baseline = unique(FC_michelson),
            .groups = 'drop')  # Assuming 1 value per id  


dfGLM <- data %>% 
  group_by(id,label,FC_michelson,TC_michelson) %>% # Summarise data to get mean responses
  summarise(responseRate = mean(response),
            weights = n(),
            .groups = 'drop') %>%
  mutate(FC_michelson_c = FC_michelson - weighted.mean(FC_michelson,weights),
         TC_michelson_c = TC_michelson - weighted.mean(TC_michelson,weights)) %>%
  left_join(baselines, by = "id")

df2Way <- data %>% 
  group_by(id,label,FC_michelson,TC_f) %>% 
  summarise(responseRate = mean(response),
            weights = n(),
            .groups = 'drop') %>%
  mutate(FC_michelson_c = FC_michelson - weighted.mean(FC_michelson,weights)) %>%
  left_join(baselines, by = "id")



write.csv(dfGLM,"dfGLM.csv", row.names = F)
write.csv(df2Way,"df2Way.csv", row.names = F)
