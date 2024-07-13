#A re-write of the hacker text gen i made a while ago

import random
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import pygame
import copy

FONT_SCALE = 500
WIDTH = 1920
HEIGHT = 1080
FONT = "HackerTextGen/Hacked-KerX.ttf"
ONES_AND_ZEROS_FONT_SIZE = 10
GREEN = (0, 255, 0)


def GenerateTextImage(text):
    #Generates an image of the text
    #The text will always be the same font and size, and then scaled to a WIDTHxHEIGHT image
    #The text will be centered in the image
    #The image will be black and white
    #Handel multiple Lines
    texts = text.split("\n")

    font = ImageFont.truetype(FONT, FONT_SCALE)
    #Create a black image
    img = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
    img.fill(255)
    #Get the size of the text
    #Get the center of the image
    lefts, tops, rights, bottoms = [], [], [], []
    for text in texts:
        left, top, right, bottom = font.getbbox(text)
        lefts.append(left)
        tops.append(top)
        rights.append(right)
        bottoms.append(bottom)
    
    left = min(lefts)
    top = min(tops)
    right = max(rights)
    bottom = max(bottoms)
    width = right - left
    height = 0
    for i in range(len(bottoms)):
        height += bottoms[i] - tops[i]
        


    #Scale the font to fit the image
    fontSize = FONT_SCALE
    while width > WIDTH:
        fontSize -= fontSize * 0.1
        font = ImageFont.truetype(FONT, fontSize)
        lefts, tops, rights, bottoms = [], [], [], []
        for text in texts:
            left, top, right, bottom = font.getbbox(text)
            lefts.append(left)
            tops.append(top)
            rights.append(right)
            bottoms.append(bottom)
        left = min(lefts)
        top = min(tops)
        right = max(rights)
        bottom = max(bottoms)
        width = right - left
        height = 0
        for i in range(len(bottoms)):
            height += bottoms[i] - tops[i]
    while height > HEIGHT:
        fontSize -= fontSize * 0.1
        font = ImageFont.truetype(FONT, fontSize)
        lefts, tops, rights, bottoms = [], [], [], []
        for text in texts:
            left, top, right, bottom = font.getbbox(text)
            lefts.append(left)
            tops.append(top)
            rights.append(right)
            bottoms.append(bottom)
        left = min(lefts)
        top = min(tops)
        right = max(rights)
        bottom = max(bottoms)
        width = right - left
        height = 0
        for i in range(len(bottoms)):
            height += bottoms[i] - tops[i]

    #get the centers based on the new font size, and where it is in the message
    centers = []
    for text in texts:
        numMessages = len(texts)
        left, top, right, bottom = font.getbbox(text)
        width = right - left
        height = bottom - top
        center = (int((WIDTH - width) / 2), int((HEIGHT - height * numMessages) / 2 + height * texts.index(text)))
        centers.append(center)

    #Create a PIL image
    pilImg = Image.fromarray(img)
    draw = ImageDraw.Draw(pilImg)
    #Load the font
    #Draw the text
    for i in range(len(texts)):
        draw.text(centers[i], texts[i], font = font, fill = (0, 0, 0))
    #Convert the PIL image back to a cv2 image
    img = np.array(pilImg)
    return img

def ShowImage(img):
    #Shows an image
    cv2.imshow("Image", img)
    cv2.waitKey(0)

def ProcessImage(img, width, height, threshold = 0.5):
    #converts the image to an array, size width x height, and splitting the image into Trues and Falses based on the threshold
    #if the group of pixels in the section of the image adverages to a value greater than the threshold, it will be True, otherwise False
    #(The thershhold is a value between 0 and 1, based on how black the pixel is)
    #returns a list of lists of booleans

    #convert the image to a black and white image
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #split the image into chunks of width x height
    h, w = img.shape[:2]
    chunkH = int(h/height)
    chunkW = int(w/width)
    values = []
    for i in range(height):
        for j in range(width):
            #get the chunk
            chunk = img[i*chunkH:(i+1)*chunkH, j*chunkW:(j+1)*chunkW]
            #calculate the average grey value
            grey = np.mean(chunk)
            if grey > threshold * 255:
                values.append(True)
            else:
                values.append(False)
    return values

def ShowProcessedImage(values, valueWidth, valueHeight, width, height):
    #Shows the processed image, scaled to a width x height image
    #Just creates black or white rectangles based on the values
    img = np.zeros((height, width, 3), np.uint8)
    img.fill(0)
    h, w = img.shape[:2]
    chunkH = int(h/valueHeight)
    chunkW = int(w/valueWidth)

    for i in range(valueHeight):
        for j in range(valueWidth):
            if values[i * valueWidth + j]:
                cv2.rectangle(img, (j*chunkW, i*chunkH), ((j+1)*chunkW, (i+1)*chunkH), (255, 255, 255), -1)
    cv2.imshow("Image", img)
    cv2.waitKey(0)

    

def main():
    #Generate a random string of text
    texts = ["Hacker Voice", "Im In"] #Text has a strange gap at the top, but it's fine
    #Generate the image
    imgs = []
    for text in texts:
        imgs.append(GenerateTextImage(text))

    #Show the image
    values = []
    for img in imgs:
        values.append(ProcessImage(img, 240, 135))

    #Create the pygame window
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    #Create a clock
    clock = pygame.time.Clock()
    
    #set the background to black
    screen.fill((0, 0, 0))
    #Create a font
    font = pygame.font.Font(FONT, ONES_AND_ZEROS_FONT_SIZE)
    OneImage = font.render("1", True, GREEN)
    ZeroImage = font.render("0", True, GREEN)
    numberImages = [OneImage, ZeroImage]
    index = 0
    TickRate = 20
    TimePerImage = 10
    timer = TimePerImage * TickRate #seconds

    currentValues = copy.deepcopy(values[0])
    goalValues = copy.deepcopy(values[0])
    indexesToChange = []

    def Update():
        nonlocal index
        nonlocal timer
        nonlocal currentValues
        nonlocal goalValues
        nonlocal indexesToChange
        # timer -= 1 
        # if timer <= 0:
        #     timer = TimePerImage * TickRate
        #     index = (index + 1) % len(values)
        #     goalValues = values[index]
        #     #add all the indexes that are different to the indexesToChange
        #     indexesToChange = []
        #     for i in range(len(currentValues)):
        #         if currentValues[i] != goalValues[i]:
        #             indexesToChange.append(i)
        if currentValues != goalValues:
            #randomly change between 10 - 20 values to the goal values
            for i in range(random.randint(100, 200)):
                if indexesToChange:
                    choice = random.choice(indexesToChange)
                    currentValues[choice] = goalValues[choice]
                    indexesToChange.remove(choice)

        #set the background to black
        screen.fill((0, 0, 0))
        #Draw the image
        for i in range(len(currentValues)):
            if not currentValues[i]:
                screen.blit(random.choice(numberImages), (i % 240 * 8, i // 240 * 8))
        #Update the screen
        pygame.display.flip()

    
    #Based on the values, we will draw a 1 or 0. We have to make sure they stay in the bounds of the screen
    #Certain sizes may compress the 1s and 0s too much, but we'll just ignore that for now
    # for i in range(len(values)):
    #     if not values[i]:
    #         screen.blit(random.choice(numberImages), (i % 240 * 8, i // 240 * 8))
    # #Update the screen
    # pygame.display.flip()
    # #Wait for the user to close the window
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    index += 1
                    if index >= len(values):
                        index = 0
                    goalValues = copy.deepcopy(values[index])
                    #add all the indexes that are different to the indexesToChange
                    indexesToChange = []
                    for i in range(len(currentValues)):
                        if currentValues[i] != goalValues[i]:
                            indexesToChange.append(i)
        clock.tick(TickRate)
        Update()
        if values[0] == values[1]:
            bp=1

    
    



if __name__ == "__main__":
    main()

