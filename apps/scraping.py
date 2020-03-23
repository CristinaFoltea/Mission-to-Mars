# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import datetime as dt
import pandas as pd 

def scrape_all():
  # Initiate headless driver for deployment
  browser = Browser("chrome", executable_path="chromedriver", headless="true")
  news_title, news_paragraph = mars_news(browser)
  # Run all scraping functions and store results in dictionary
  data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        'hemi_data': mars_hemispheres(browser)
  }
  return data

### Mars news
def mars_news(browser):

  # Visit the mars nasa news site
  url = 'https://mars.nasa.gov/news/'
  browser.visit(url)
  # Optional delay for loading the page
  browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

  # Convert the browser html to a soup object and then quit the browser
  html = browser.html
  news_soup = BeautifulSoup(html, 'html.parser')
  try:
    slide_elem = news_soup.select_one('ul.item_list li.slide')
    slide_elem.find("div", class_='content_title')
    # Use the parent element to find the first <a> tag and save it as  `news_title`
    news_title = slide_elem.find("div", class_='content_title').get_text()
    # Use the parent element to find the paragraph text
    news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
  except AttributeError:
    return None, None
  return news_title, news_p
  
### Featured Images
def featured_image(browser):
  # Visit URL
  url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
  browser.visit(url)

  # Find and click the full image button
  full_image_elem = browser.find_by_id('full_image')
  full_image_elem.click()

  # Find the more info button and click that
  browser.is_element_present_by_text('more info', wait_time=1)
  more_info_elem = browser.find_link_by_partial_text('more info')
  more_info_elem.click()

  # Parse the resulting html with soup
  html = browser.html
  img_soup = BeautifulSoup(html, 'html.parser')

  try:
    # Find the relative image url
    img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    img_url_rel
  except AttributeError:
   return None
  
  # Use the base URL to create an absolute URL
  img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
  return img_url

### Mars facts
def mars_facts():
  try:
    # use 'read_html" to scrape the facts table into a dataframe
    df = pd.read_html('http://space-facts.com/mars/')[0]
  except BaseException:
    return None
  df.columns=['description', 'value']
  df.set_index('description', inplace=True)
  return df.to_html()

def mars_hemispheres(browser):
  # Visit mars hemispheres page
  url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
  browser.visit(url)

  # Parse the resulting html with soup
  html = browser.html
  hm_soup = BeautifulSoup(html, 'html.parser')

  # empty list that will contain the collected data
  list_hm = []

  # Get list of individual hemisphere element
  try:
    wrapper = hm_soup.select_one("#product-section")
    list_hm_el = wrapper.select(".item")
  except BaseException:
    return [
        {
            "title": "kitty1",
            "image_url": "https://live.staticflickr.com/3397/3551189653_501acccd41_b.jpg"
        },
        {
            "title": "kitty2",
            "image_url": "https://live.staticflickr.com/3397/3551189653_501acccd41_b.jpg"
        },
        {
            "title": "kitty3",
            "image_url": "https://live.staticflickr.com/3397/3551189653_501acccd41_b.jpg"
        },
        {
            "title": "kitty4",
            "image_url": "https://live.staticflickr.com/3397/3551189653_501acccd41_b.jpg"
        }
    ]

  # loop though the list to gather extra data for individual hemisphere
  for index, hm in enumerate(list_hm_el):
    # instantiate a new hemisphere object 
    hemi = {
        'title': "",
        'image_url': ""
    }
    try:
      title_el = hm.select_one('.description h3')
      title = title_el.get_text()
      link = browser.find_by_css('.description')[index].find_by_tag("a")
      link.click()
      img_soup = BeautifulSoup(browser.html, 'html.parser')
      img_src = img_soup.select_one('#wide-image img.wide-image').get("src")
      # insert new data
      hemi = {
        'title': title,
        'image_url': f'https://astrogeology.usgs.gov/{img_src}'
      }
    except BaseException:
      continue
    list_hm.append(hemi)
    browser.back()
  return list_hm


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())