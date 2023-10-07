import time
import requests

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

class RequestBody(BaseModel):
    field: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def download(url:str):
    # Create a Chrome WebDriver instance (you need to specify the path to chromedriver)
    service = Service(executable_path='./chromedriver')
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1200x800")
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the webpage with the splash screen
    driver.get(url)

    # Wait for the dynamic content to load (you may need to adjust the wait time)
    time.sleep(5)  # Wait for 5 seconds to load the page

    # Get the current page source after the dynamic content has loaded
    page_source = driver.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find and extract <img> tags or perform further processing
    img_tags = soup.find_all('img',class_='x5yr21d xu96u03 x10l6tqk x13vifvy x87ps6o xh8yej3')
    img = img_tags[0]
    img_url = img['src']
    '''Download the image via the url using the requests library'''
    r = requests.get(img_url)

    filename = "instagram"+".png"
    with open(filename,'wb') as f: 
        f.write(r.content)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/getimage")
async def download_instagram_post(request: RequestBody):
    item_dict = request.dict()
    instagram_url = item_dict['field']
    download(instagram_url)
    
    return "success"
