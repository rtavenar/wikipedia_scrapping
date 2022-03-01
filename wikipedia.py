# -*- coding: utf-8 -*-
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup, Tag, NavigableString, Comment
import pickle
from multiprocessing import Pool, cpu_count
import time

# Définition des fonctions


def parseURL(mon_url):
    # Ouvrir avec openurl mon_url
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    req = Request(mon_url,headers={'User-Agent':user_agent})
    try: # gestion des exceptions avec un bloc try/except
        html = urlopen(req)
    except (HTTPError, URLError) as e:
        sys.exit(e) # sortie du programme avec affichage de l’erreur
    bsObj = BeautifulSoup(html, "lxml") # en utilisant le parser de lxml

    #Acceder au grand titre h1 qui a l'id firstHeading 
    titre = bsObj.find("h1",id="firstHeading").get_text()
    #Acceder au texte 
    masoupe = bsObj.find("div",id="mw-content-text")
    texte = getSelectedText(masoupe)
    return(mon_url,titre,texte)

def getSelectedText(montag):
    texte = ""
    # boucle sur les enfants de monTag
    for c in montag.children:
        # si l'enfant est un NavigableString : on récupère le texte
        # dans c.string, et on retire les espaces en trop (.strip())
        if type(c) == NavigableString:
            texte += " "+(c.string).strip()
        # si l'enfant est un tag et qu'il est valide
        # on va chercher le texte à l'intérieur
        # et on le rajoute au texte déjà récupéré
        elif type(c) == Tag and validTag(c):
            texte += getSelectedText(c)
    return texte


def validTag(tag):
    if tag.name == "style" or tag.name=="sup":
        return False
    if "class" in tag.attrs :
        for elem in tag.attrs["class"]: #Parcours de toutes les class
            if elem in ['toc', 'homonymie', 'metadata','mw-editsection', 'mwe-math-element', 'bandeau-portail', 'printfooter']:
                return False
    return True

if __name__ == '__main__':


    #Question 1 : ouverture de la page Energies renouvelables
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    full_url = 'https://fr.wikipedia.org/wiki/Cat%C3%A9gorie:%C3%89nergie_renouvelable'

    req = Request(full_url,headers={'User-Agent':user_agent})
    try: # gestion des exceptions avec un bloc try/except
        html = urlopen(req)
    except (HTTPError, URLError) as e:
        sys.exit(e) # sortie du programme avec affichage de l’erreur


    #Récupération de tous les liens
    bsObj = BeautifulSoup(html, "lxml") # en utilisant le parser de lxml
    # print(bsObj.prettify())
    liens = bsObj.find("div",id="mw-pages").find("div",class_="mw-category").find_all("a")
    # print(liens)

    l_url = ["https://fr.wikipedia.org"+lien.attrs["href"] for lien in liens]
    # print(l_url)

    #Test de parseURL
    #print(parseURL("https://fr.wikipedia.org/wiki/Hors_r%C3%A9seau"))


    # - Appeler parseURL sur tous les éléments de la liste l_url. On utilisera la programmation parallele
    res = []
    with Pool(cpu_count()-1) as p :
        res = p.map(parseURL,l_url)
    #print(res)

   # - Stocker le resultat dans une liste et dump le resultat dans un fichier
    with open('info_energie.pick', 'wb') as pickFile:
        pickle.dump(res, pickFile)

 

