library(shiny)
library(shinydashboard)
library(leaflet)

# JScode <-
#   "$(document).ready(function() {
#   // wait a few ms to allow other scripts to execute
#     setTimeout(function(){
#       var vals = [];
#       var powStart = 0;
#       var powStop = 5;
#       for (i = powStart; i <= powStop; i+=0.25) {
#         var val = Math.pow(10, i);
#         val = parseFloat(val.toFixed(0));
#         vals.push(val);
#       }
#       $('#size_slider').data('ionRangeSlider').update({'values':vals})
#     }, 5)})})"

shinyUI(dashboardPage(
  dashboardHeader(title = "Scraped jobs"),
  dashboardSidebar(#tags$head(tags$script(HTML(JScode))),
    # sidebarUserPanel("Domingos Lopes"),
    sidebarMenu(id = "menu",
      menuItem("Scraped companies", tabName = "companies"),
      menuItem("Scraped aggregators", tabName = "aggregators")),
    conditionalPanel(
      condition = "input.menu == 'companies'",
      checkboxGroupInput("companiesGroup", label = h3("Select companies"), 
                         choices = list("Amazon" = 'amazon',
                                        "Apple" = 'apple',
                                        "Facebook" = 'facebook'),
                         selected = c('amazon', 'apple', 'facebook'))),
    conditionalPanel(
      condition = "input.menu == 'aggregators'",
      sliderInput("date_slider", label = "Weeks in the past",
                  min = 0, max = 5, value = c(0, 4), step = 1, round = T),
      sliderInput("size_slider", label = "Heatmap point size (log)",
                  min = 8, max = 24, step = 1, value = 16, round = T)
    )
  ),
  dashboardBody(
    tags$head(
      tags$link(rel = "stylesheet", type = "text/css", href = "custom.css")
    ),
    tabItems(
      tabItem(tabName = "companies", leafletOutput("companiesMap")),
      tabItem(tabName = "aggregators", leafletOutput("aggregatorsMap"))
    )
  )
))