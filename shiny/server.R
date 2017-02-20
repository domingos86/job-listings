library(shiny)
library(leaflet)
library(leaflet.extras)
library(dplyr)

# library(htmltools)
# library(htmlwidgets)
# 
# heatPlugin <- htmlDependency("Leaflet.heat", "99.99.99",
#                              src = c(href = "http://leaflet.github.io/Leaflet.heat/dist/"),
#                              script = "leaflet-heat.js"
# )
# 
# registerPlugin <- function(map, plugin) {
#   map$dependencies <- c(map$dependencies, list(plugin))
#   map
# }

companies_locations <- read.csv('data/company_job_locations.csv')
companies_locations <- companies_locations %>%
  select(company, latitude, longitude) %>%
  group_by(company, latitude, longitude) %>%
  summarize(quantity = n())

aggregator_locations <- read.csv('data/aggregator_job_locations.csv')
aggregator_locations$date_posted <- as.Date(aggregator_locations$date_posted)
max_date <- max(aggregator_locations$date_posted)
aggregator_locations['week'] = trunc((max_date - aggregator_locations$date_posted) / 7)
aggregator_locations <- aggregator_locations %>%
  group_by(week, latitude, longitude) %>%
  summarize(quantity = n()) %>% ungroup()

col_names = c('A', 'B', 'C', 'D', 'E', 'F')
locations_index <- unique(aggregator_locations[c('latitude', 'longitude')])
locations_index[3] = 0
colnames(locations_index)[3] = col_names[1]
for(i in 1:5) {
  locations_index <- locations_index %>%
    left_join(aggregator_locations %>% filter(week == i - 1) %>%
                select(longitude, latitude, quantity),
              by = c('longitude', 'latitude'))
  col = col_names[i+1]
  colnames(locations_index)[3+i] = col
  locations_index[col] <- replace(locations_index[col],
                                    which(is.na(locations_index[col]),
                                          arr.ind = T), 0)
  locations_index[col] <- locations_index[col] + locations_index[col_names[i]]
}

update_companiesMap <- function(map, companiesGroup = c('apple', 'facebook', 'amazon')) {
  locations <- companies_locations %>% filter(company %in% companiesGroup) %>%
    group_by(latitude, longitude) %>% summarize(quantity = sum(quantity))
  return(map %>% removeWebGLHeatmap(layerId = 'heat') %>%
           addWebGLHeatmap(lng = ~longitude, lat = ~latitude, intensity = ~quantity,
                           size = 40000, opacity = 0.8, layerId = 'heat',
                           alphaRange = 0.01, data = locations))
}

update_aggregatorsMap <- function(map, date_slider = c(0, 4), size_slider = 10000) {
  locations <- locations_index %>%
    select(longitude, latitude)
  locations['quantity'] = locations_index[col_names[date_slider[2]+1]] -
    locations_index[col_names[date_slider[1]+1]]
  return(map %>% removeWebGLHeatmap(layerId = 'heat') %>%
           addWebGLHeatmap(lng = ~longitude, lat = ~latitude, intensity = ~quantity,
                           size = size_slider, opacity = 0.8, layerId = 'heat',
                           alphaRange = 0.01, data = locations))
}

# update_aggregatorsMap <- function(map, date_slider = c(0, 4), size_slider = 10000) {
#   locations <- locations_index %>%
#     select(longitude, latitude)
#   locations['quantity'] = locations_index[col_names[date_slider[2]+1]] -
#     locations_index[col_names[date_slider[1]+1]]
#   return(map %>% registerPlugin(heatPlugin) %>%
#            onRender("function(el, x, data) {
#     if(\"heat_layer\" in window) {
#       heat_layer.remove();
#     }
#     data = HTMLWidgets.dataframeToD3(data);
#     data = data.map(function(val) { return [val.lat, val.long, val.mag]; });
#     heat_layer = L.heatLayer(data, {radius: 25}).addTo(this);
#   }", data = locations %>% select(lat = latitude, long = longitude, mag = quantity)))
# }

shinyServer(function(input, output, session) {

  output$companiesMap = renderLeaflet({
    leaflet() %>% addProviderTiles('Hydda.Base') %>%
      addProviderTiles('Stamen.TonerHybrid') %>%
      setView(-95, 37, 4) %>% update_companiesMap()
  })
  
  observe({
    leafletProxy('companiesMap', session) %>% update_companiesMap(input$companiesGroup)
    })
  
  output$aggregatorsMap = renderLeaflet({
    leaflet() %>% addProviderTiles('Hydda.Base') %>%
      addProviderTiles('Stamen.TonerHybrid') %>%
      setView(-95, 37, 4) %>% update_aggregatorsMap()
  })
  
  observe({
    leafletProxy('aggregatorsMap', session) %>%
      update_aggregatorsMap(input$date_slider, round(10^(input$size_slider/4)))
  })
  
  #output$size_output <- renderText(input$size_slider)
})