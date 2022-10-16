from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
from selenium.webdriver.common.by import By
import re as re

class Scraping:  

    def get_data(self):
        page = input("Enter the Company Linkedin URL: ")
        company_name = page[33:-1]

        #See if existing user credential file exists or create one 
        try:
            f= open("linkedin_credentials.txt","r")
            contents = f.read()
            username = contents.replace("=",",").split(",")[1]
            password = contents.replace("=",",").split(",")[3]
        except:
            f= open("linkedin_credentials.txt","w+")
            username = input('Enter your linkedin username: ')
            password = input('Enter your linkedin password: ')
            f.write("username={}, password={}".format(username,password))
            f.close()

        browser = webdriver.Chrome('dashboard\drivers\chromedriver.exe')


        #Open login page
        browser.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')

        #Enter login info:
        elementID = browser.find_element(By.ID,'username')
        elementID.send_keys(username)

        elementID = browser.find_element(By.ID,'password')
        elementID.send_keys(password)
        elementID.submit()

        #Go to company post webpage
        browser.get(page + 'posts/')


        #Simulate scrolling to capture all posts
        SCROLL_PAUSE_TIME = 1.5

        # Get scroll height
        last_height = browser.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break #up
            last_height = new_height

        """# Beautiful soup"""

        #Check out page source code
        company_page = browser.page_source  


        #Use Beautiful Soup to get access tags
        linkedin_soup = bs(company_page.encode("utf-8"), "html")
        linkedin_soup.prettify()

        #Find the post blocks
        containers = linkedin_soup.findAll("div",{"class":["ember-view",  "occludable-update"]})

        post_dates = []
        post_texts = []
        post_likes = []
        post_comments = []
        video_views = []
        media_links = []
        media_type = []


        #Looping through the posts and appending them to the lists
        for container in containers:
            
            #Try function to make sure its a post and not a promotion
            try:
                posted_date = container.find("span",{"class":"visually-hidden"})
                text_box = container.find("div",{"class":["feed-shared-inline-show-more-text",
            "feed-shared-update-v2__description"]})

                # if text_box:
                #     print(text_box)
                #     # break
                

                text = text_box.find("span",{"dir":"ltr"})
                print(text)
                
                new_likes = container.findAll("li", {"class":["social-details-social-counts__reactions", "social-details-social-counts__item"]})
                new_comments = container.findAll("li", {"class": ["social-details-social-counts__comments", "social-details-social-counts__item"]})

                #Appending date and text to lists
                post_dates.append(posted_date.text.strip())
                post_texts.append(text_box.text.strip())


                #Determining media type and collecting relevant info for each type
                try:
                    video_box = container.findAll("div",{"class": ["feed-shared-update-v2__content", "feed-shared-linkedin-video ember-view"]})
                    video_link = video_box[0].find("video", {"class":"vjs-tech"})
                    media_links.append(video_link['src'])
                    media_type.append("Video")
                except:
                    try:
                        image_box = container.findAll("div",{"class": "feed-shared-image__container"})
                        image_link = image_box[0].find("img", {"class":["ivm-view-attr__img--centered feed-shared-image__image", "feed-shared-image__image--constrained", "lazy-image ember-view"]})
                        media_links.append(image_link['src'])
                        media_type.append("Image")
                    except:
                        try:
                            image_box = container.findAll("div",{"class": "feed-shared-image__container"})
                            image_link = image_box[0].find("img", {"class":["ivm-view-attr__img--centered", "feed-shared-image__image", "lazy-image ember-view"]})
                            media_links.append(image_link['src'])
                            media_type.append("Image")
                        except:
                            try:
                                article_box = container.findAll("div",{"class": "feed-shared-article__description-container"})
                                article_link = article_box[0].find('a', href=True)
                                media_links.append(article_link['href'])
                                media_type.append("Article")
                            except:
                                try:
                                    video_box = container.findAll("div",{"class": "feed-shared-external-video__meta"})          
                                    video_link = video_box[0].find('a', href=True)
                                    media_links.append(video_link['href'])
                                    media_type.append("Youtube Video")   
                                except:
                                    try:
                                        poll_box = container.findAll("div",{"class": ["feed-shared-update-v2__content", "overflow-hidden", "feed-shared-poll", "ember-view"]})
                                        media_links.append("None")
                                        media_type.append("Other: Poll, Shared Post, etc")
                                    except:
                                        media_links.append("None")
                                        media_type.append("Unknown")



                #Getting Video Views. (The folling three lines prevents class name overlap)
                view_container2 = set(container.findAll("li", {'class':["social-details-social-counts__item"]}))
                view_container1 = set(container.findAll("li", {'class':["social-details-social-counts__reactions","social-details-social-counts__comments social-details-social-counts__item"]}))
                result = view_container2 - view_container1

                view_container = []
                for i in result:
                    view_container += i

                try:
                    video_views.append(view_container[1].text.strip().replace(' Views',''))

                except:
                    video_views.append('N/A')

                
                #Appending likes and comments if they exist
                try:
                    post_likes.append(new_likes[0].text.strip())
                except:
                    post_likes.append(0)
                    pass

                try:
                    post_comments.append(new_comments[0].text.strip())                           
                except:                                                           
                    post_comments.append(0)
                    pass
            
            except:
                pass

        comment_count = []
        for i in post_comments:
            s = str(i).replace('Comment','').replace('s','').replace(' ','')
            comment_count += [s]

        # !pip install xlsxwriter
        data = {
            "Date Posted": post_dates,
            "Media Type": media_type,
            "Post Text": post_texts,
            "Post Likes": post_likes,
            "Post Comments": comment_count,
            "Video Views": video_views,
            "Media Links": media_links
        }

        df = pd.DataFrame(data)


        #Exporting as csv file to program folder
        df.to_csv("{}_posts.csv".format(company_name), encoding='utf-8', index=False)

        #Export to Excel file to program folder
        writer = pd.ExcelWriter("{}_posts.xlsx".format(company_name), engine='xlsxwriter')
        df.to_excel(writer, index =False)
        writer.save()


# scrap = Scraping()
# scrap.get_data()

