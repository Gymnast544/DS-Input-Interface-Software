import xml.etree.ElementTree as ET
import pygame
pygame.init()





class Skin:
    def __init__(self, xmlpath):
        self.xmlpath = xmlpath
        tree = ET.parse(xmlpath)
        self.tree = tree#possibly useful in case debugging is wanted
        root = tree.getroot()
        self.rootattribs = root.attrib
        self.name = root.attrib['name']
        self.author = root.attrib['author']
        print(root.attrib)
        self.backgrounds = []
        self.buttons = {}
        for elem in root:
            if elem.tag=='background':
                #It's a color variant
                background = pygame.image.load(elem.attrib['image'])
                name = elem.attrib['name']
                self.backgrounds.append((name, background))
            elif elem.tag=='button':
                name = elem.attrib['name']
                image = pygame.image.load(elem.attrib['image'])
                pos = (elem.attrib['x'], elem.attrib['y'])
                self.buttons[elem.attrib['name']] = (pos, image)
        


niceskin = Skin("skin.xml")
