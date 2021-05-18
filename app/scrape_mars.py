from splinter import Browser
from selenium import webdriver
import os
import pandas as pd
import requests
import pymongo
import json
from bs4 import BeautifulSoup as soup
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo


def scraper():
    executable_path = {'executable_path': '/Users/danlarson/Documents/git/Trilogy/In-Class/Homework/12-Web-Scraping-and-Document-Databases/web-scraping-challenge/app/chromedriver'}
    options = webdriver.ChromeOptions()
    browser = Browser('chrome', **executable_path, headless=True, options=options)

    news_title, news_p = news(browser)

    data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image": mars_image(browser),
        "facts": get_facts(),
        "hems": hems(browser),
        # "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def news(browser):

    mars_news = 'https://mars.nasa.gov/news/'
    news_title = []
    news_p = []
    browser.visit(mars_news)
    browser.is_element_present_by_css('div.list_text', wait_time=3)
    
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('div.list_text')
        news_title = slide_elem.find("div", class_="content_title").get_text()
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()
        return news_title, news_p

    except AttributeError:
        return None, None


def mars_image(browser):
    featured_images = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(featured_images)
    featured_image_url = []
    button = browser.find_by_tag('button')[1]
    button.click()
    html = browser.html
    img_url = soup(html, 'html.parser')
    img = img_url.find('img', class_='fancybox-image').get('src')
    featured_image_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img}'
    return featured_image_url

def get_facts():
    mars_data = pd.read_html('https://space-facts.com/mars/')
    mars_df = pd.DataFrame(mars_data[1])

    mars_df.columns = ['Description', 'Mars', 'Earth']
    mars_df.set_index('Description', inplace=True)
    return mars_df.to_html(classes="table table-striped")
    

def hems(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url + 'index.html')
    hem_image_urls = []
    for i in range(4):
        browser.find_by_css("a.product-item img")[i].click()
        hemi = scrape_hems(browser.html)
        hemi['img_url'] = url + hemi['img_url']
        hem_image_urls.append(hemi)
        browser.back()

    return hem_image_urls


def scrape_hems(html_text):
    hemi = soup(html_text, "html.parser")
    try:
        title = hemi.find("h2", class_="title").get_text()
        sample = hemi.find("a", text="Sample").get("href")

    except AttributeError:
        title = None
        sample = None

    hemispheres = {
        "title": title,
        "img_url": sample
    }

    return hemispheres