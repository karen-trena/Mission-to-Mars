
# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

#we need to connect to Mongo and establish communication between our code and the database we're using
def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True) #When we were testing our code in Jupyter, headless was set as False so we could see the scraping in action. Now that we are deploying our code into a usable web app, we don't need to watch the script work (though it's totally okay if you still want to).
    hemisphere_image_urls = hemisphere(browser) ##ADDED FOR CHALLENGE

#Next, we're going to set our news title and paragraph variables (remember, this function will return two values).
    news_title, news_paragraph = mars_news(browser)
#This line of code tells Python that we'll be using our mars_news function to pull this data.

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemisphere_image_urls 
    } #HEMISPHERES WAS ADDED FOR CHALLENGE
    #This dictionary does two things: It runs all of the functions we've created—featured_image(browser), for example—and it also stores all of the results. When we create the HTML template, we'll create paths to the dictionary's values, which lets us present our data on our template. We're also adding the date the code was run last by adding "last_modified": dt.datetime.now(). For this line to work correctly, we'll also need to add import datetime as dt to our imported dependencies at the beginning of our code.


    # Stop webdriver and return data
    browser.quit()
    return data
    #To finish up the function, there are two more things to do. The first is to end the WebDriver using the line browser.quit(). You can quit the automated browser by physically closing it, but there's a chance it won't fully quit in the background. By using code to exit the browser, you'll know that all of the processes have been stopped.
    #Second, the return statement needs to be added. This is the final line that will signal that the function is complete, and it will be inserted directly beneath browser.quit(). We want to return the data dictionary created earlier, so our return statement will simply read return data


def mars_news(browser):
    #we'll assign the url and instruct the browser to visit it
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # With the following line, browser.is_element_present_by_css('div.list_text', wait_time=1), we are accomplishing two things.
    # 
    # One is that we're searching for elements with a specific combination of tag (div) and attribute (list_text). As an example, ul.item_list would be found in HTML as ul class="item_list"
    # 
    # Secondly, we're also telling our browser to wait one second before searching for components. The optional delay is useful because sometimes dynamic pages take a little while to load, especially if they are image-heavy.

    #we'll set up the HTML parser:
    html = browser.html
    news_soup = soup(html, 'html.parser')
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title,news_p


def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Run this code to make sure it's working correctly. A new automated browser should open to the featured images webpage. 
    # Next, we want to click the "Full Image" button. This button will direct our browser to an image slideshow. Let's take a look at the button's HTML tags and attributes with the DevTools
    # This is a fairly straightforward HTML tag: the <button> element has two classes (btn and btn-outline-light) and a string reading "FULL IMAGE". First, let's use the dev tools to search for all the button elements.

    # Since there are only three buttons, and we want to click the full-size image button, we can go ahead and use the HTML tag in our code.
    # In the next cell, let's type the following:

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')


    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None


    #Let's add the base URL to our code.

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    return img_url


def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

def hemisphere_urls(browser): #ADDED FOR CHALLENGE ALL THE WAY BEFORE if __name__ == "__main__":
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    hemisphere_image_urls = []

    for i in range(4):
        hemisphere = {}
    
        # Find the elements on each loop to avoid a stale element exception
        browser.find_by_tag("a.product-item h3")[i].click()
        
        # Find the Sample image anchor tag and extract the href
        sample_elem = browser.links.find_by_text('Sample').first
        hemisphere['img_url'] = sample_elem['href']
        
        # Get Hemisphere title
        hemisphere['title'] = browser.find_by_css("h2.title").text
        
        # Append hemisphere object to list
        hemisphere_image_urls.append(hemisphere)
        
        browser.back()
    print(hemisphere_image_urls)

    return hemisphere_image_urls


#This last block of code tells Flask that our script is complete and ready for action. The print statement will print out the results of our scraping to our terminal after executing the code.
if __name__ == "__main__":

    # If running as script, print scraped data
    #print(scrape_all())
    scrape_all()