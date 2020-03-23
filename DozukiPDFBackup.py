# Program for crawling Dozuki sites and exporting guides in PDF
# format while retaining perceived file-structure.
# Released 03/22/2020 Matei Jordache
#
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import time, bs4, requests, os
#
browser = webdriver.Firefox()
dozukiurl = "https://company.dozuki.com" # URL to start collecting guides at. Use root directory to get all.
dozukiemail = "name@work.com" # Email for login
dozukipwd = "dozukipassword" # Password for login
dirpath = ["/tmp/DozukiBackup/"] # First element of list is root path of backups

# Waiting routine, still needs work (document.readyState return "complete" before finishing jams up timing)
def waitload():
    time.sleep(3)
    #wait = WebDriverWait(browser, 10)
    #try:
    #    wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'html')))
    #    time.sleep(2)
    #except TimeoutException:
    #    time.sleep(0.5)
# Reouting to fix filepath
def appendpath(cattag):
    global dirpath, soup
    soup = bs4.BeautifulSoup(browser.page_source, features="html.parser") # Get HTML from page
    try:
        categorytitle = soup.find(cattag).text  # Find the title of category or guide
    except AttributeError:
        waitload()
        appendpath(cattag) # Retry to make the soup
    categorytitle = categorytitle.strip() # Remove whitespace
    dirpath.append(dirpath[-1] + categorytitle.replace('/','_').replace(' ', '') + '/') #Format name and add to directory
# Category routine
def categoryscrape():
    global dirpath, soup
    appendpath('h1')
    subcategory = browser.find_elements_by_class_name('categoryAnchor') #see if there are subcategories
    waitload()
    for i in range(len(subcategory)): # Run through all subcategories
        try:
            browser.find_elements_by_class_name('categoryAnchor')[i].click() # Choose a category
            waitload()
            categoryscrape() # Repeat to check for more subcategories
        except IndexError: # Catch if try to click before page loaded fully
            waitload() # Wait and then try again
            i = i-1 # So we don't jump to the next element after catch error
    waitload()
    # Sifting guides from other content
    guide = browser.find_elements_by_class_name('cell') # Discover how many guides to set length
    waitload()
    for j in range(len(guide)): # Run through all the perceived guides
        try:
            wikitext = soup.find_all(class_="pageTitle wikiTitle originalText bordered") # Wikis look like guides
            if  wikitext != []: # If wiki, go back and try next
                browser.execute_script("window.history.go(-1)")
            else:
                browser.find_elements_by_class_name('cell')[j].click() # Embedded documents look more like guides than wikis
                waitload()
                pdffile = browser.find_elements_by_tag_name('iframe')
                if pdffile == []: # Capture guide
                    waitload()
                    guidescrape()
                else: # Not a guide, some other embedded content
                    browser.execute_script("window.history.go(-1)")
                    waitload()
        except IndexError: # Catch if try to choose element before page fully loaded
            waitload()
            j = j-1 # So we don't skip any elements after catching error
            continue
    browser.execute_script("window.history.go(-1)") # Go up a directory in the filepath on Dozuki
    dirpath.pop(-1) # Go up a directory in the filepath for storage
    waitload()
#Guide routine
def guidescrape():
    global dirpath, soup
    appendpath('h1') # Create filename append to path
    browser.find_element_by_link_text('Options').click()
    browser.find_element_by_link_text('Download PDF').click()
    dlurl = browser.current_url # Pass url to requests to download outside browser
    response = requests.get(dlurl)
    guidepath = dirpath[-1] # Chop off / to add file extension
    os.makedirs(dirpath[-2], exist_ok=True) # Check if directory exists and create if not there
    with open(guidepath[:-1] + ".pdf", 'wb') as f:
        f.write(response.content) # Write .pdf to file
    print(guidepath[:-1] + ".pdf") # So we can see what guides got processed
    dirpath.pop(-1) # Stop specifying this guide
    browser.execute_script("window.history.go(-2)") # Go back to parent directory from PDF page
    waitload()
# Login and initialization
browser.get(dozukiurl)
loginElem = browser.find_element_by_id('email')
loginElem.send_keys(dozukiemail)
pwdElem = browser.find_element_by_id('password')
pwdElem.send_keys(dozukipwd)
pwdElem.submit()
waitload()
categoryscrape()
browser.quit() # All done, close everything up
