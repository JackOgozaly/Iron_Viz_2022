library(tidyverse)
library(gganimate)


coord_data <- read_csv('C:\\Users\\jogoz\\OneDrive\\Desktop\\Iron Viz 2022\\Moma_Data\\gif_coords2.csv')

coord_data %>% 
  group_by(Name) %>% 
  count()


coord_data$Order <- ifelse(coord_data$Name == 'Mona Lisa',1, NaN)
coord_data$Order <- ifelse(coord_data$Name == 'Gator Statue', 2, coord_data$Order)
coord_data$Order <- ifelse(coord_data$Name == 'starry', 3, coord_data$Order)
coord_data$Order <- ifelse(coord_data$Name == 'Sistine', 4, coord_data$Order)
coord_data$Order <- ifelse(coord_data$Name == 'great_wave', 5, coord_data$Order)
coord_data$Order <- ifelse(coord_data$Name == 'napoleon', 6, coord_data$Order)

coord_data %>% 
  filter(Order == 5) %>% 
  ggplot(mapping=aes(X, Y), size=0) + geom_point(color="#FFFFFF") + theme(panel.background = element_rect(fill = 'black'),
                                                                           panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
                                                                           axis.title =element_blank(),
                                                                           axis.text=element_blank(),
                                                                           axis.ticks=element_blank())





p <- ggplot(coord_data, mapping=aes(X, Y)) + geom_point(color="#FFFFFF", size=.5) + theme(panel.background = element_rect(fill = 'black'),
                                                                                          panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
                                                                                          axis.title =element_blank(),
                                                                                          axis.text=element_blank(),
                                                                                          axis.ticks=element_blank())

anim <- p + 
  transition_states(Order,
                    transition_length = 2,
                    state_length = 3, 
                    wrap= TRUE) + enter_fade() + view_follow()


anim <- animate(
  plot = anim,
  render = gifski_renderer(),
  nframes= 300,
  duration = 15,
  fps = 20)


anim


anim_save(filename="linked_gif.gif", anim)

