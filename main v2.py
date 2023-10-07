from selenium import webdriver
from bs4 import BeautifulSoup
import time
import requests
from selenium.webdriver.chrome.options import Options
#from webdriver_manager.chrome import ChromeDriverManager

import torch
import torchvision
from torchvision import models
from torchvision import transforms
from PIL import Image

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
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')  # Run Chrome in headless mode (no GUI)
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('start-maximized')
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('--disable-extension')
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

@app.post("/predict")
async def predict():
    filename = "instagram"+".png"

    model = models.vgg16(pretrained=False)
    model.classifier[6].out_features = 5
    for parameters in model.features.parameters():
        parameters.requires_grad = False

    #model = torch.load('vgg16_5epoch.pth', map_location=torch.device('cpu'))
    model.load_state_dict(torch.load('./vgg16_5epoch.pth', map_location=torch.device('cpu')))
    model.eval()

    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),  # Resize the image to the model's input size
        transforms.ToTensor(),           # Convert to PyTorch tensor
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize if needed
    ])

    # Load and preprocess a single image
    image = Image.open(filename).convert('RGB')
    image = preprocess(image)
    image = image.unsqueeze(0)  # Add a batch dimension

    with torch.no_grad():
        outputs = model(image)

    _, predicted = torch.max(outputs.data, 1)
    predicted = predicted.item()

    if predicted == 0:
        return 'Fitness/Yoga'
    elif predicted == 1:
        return 'Food'
    elif predicted == 2:
        return 'House/Interior'
    elif predicted == 3:
        return 'Pets'
    else:
        return 'Travel'