from selenium import webdriver
from bs4 import BeautifulSoup
import sys
import os
import getpass
import time

login_url = "https://cas.id.ubc.ca/ubc-cas/login?TARGET=https%3A%2F%2Fssc.adm.ubc.ca%2Fsscportal%2Fservlets%2FSRVSSCFramework"


def calculateGPA():
    driver = webdriver.Chrome(os.getcwd() + '/chromedriver')
    login(driver)

    # navigate
    driver.find_element_by_name("submit").click()
    time.sleep(5)
    driver.find_element_by_link_text("Your Grades Summary").click()
    # time.sleep(5)
    iFrame = driver.find_element_by_name("iframe-main")
    driver.switch_to.frame(iFrame)

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    soup.prettify(formatter=lambda s: s.replace(u'\xa0', ' '))
    smallSoup = soup.find('div', {'id' : 'tabs-all'})
    subjectData = smallSoup.find_all('td', {'class' : 'listRow'})
    subjectDataGrade = smallSoup.find_all('td', {'class': 'listRow grade'})

    count = 0
    actualCourse = 0
    accumulativeCredit = 0.0
    GPA = 0
    gradeList = []
    totalGrade = 0
    thisGPA = 0
    thisCredit = 0

    for subject in subjectDataGrade:
        thisData = subject.get_text()
        if thisData != '&nbsp;' and thisData != '' and thisData != ' ':
            gradeList.append(int(thisData))

    for subject in subjectData:
        thisData = subject.get_text()
        if thisData != 'Program':
            if count % 11 == 3:
                if thisData != '&nbsp;' and thisData != '' and thisData != ' ':
                    thisGPA = mapToGPA(thisData)
                    creditDFail = False
                else:
                    creditDFail = True
            elif count % 11 == 8:
                if not creditDFail and thisData != ' ' and thisData != '':
                    thisCredit = int(float(thisData))
                    accumulativeCredit = accumulativeCredit + thisCredit
                    GPA = GPA + float("{0:.2f}".format(thisGPA)) * thisCredit
                    totalGrade += gradeList[actualCourse] * thisCredit
                    actualCourse += 1
                else:
                    thisCredit = 0
        else:
            print('Total credits so far is ' + str(accumulativeCredit))
            print('Your GPA is ' + str(float("{0:.3f}".format(GPA / accumulativeCredit))))
            sys.exit()
        count = count + 1
    print('Total credits so far is ' + str(accumulativeCredit))
    print('Your GPA is ' + str(float("{0:.3f}".format(GPA / accumulativeCredit))))
    print('Your Accumulative Average is ' + str(float("{0:.3f}".format(totalGrade / accumulativeCredit))))


def login(driver):
    driver.get(login_url)

    username = input("Please enter your SSC username: ")
    password = getpass.getpass("Please enter your password: ")
    login_credential = [username, password]

    username = driver.find_element_by_id("username")
    username.clear()
    username.send_keys(login_credential[0])

    password = driver.find_element_by_id("password")
    password.clear()
    password.send_keys(login_credential[1])


def mapToGPA(letterGrade):
    return {
        'A+': 4.3,
        'A' : 4,
        'A-': 3.7,
        'B+': 3.3,
        'B' : 3,
        'B-': 2.7,
        'C+': 2.3,
        'C' : 2,
        'C-': 1.7,
        'D' : 1,
        'F' : 0,
        ''  : 0,
        ' ' : 0
    }[letterGrade]



def alternativeLoginMethod():
    import requests
    from lxml import html
    payload = {
        "username": "xxxx",
        "password": "xxxx",
    }

    session_request = requests.session()
    result = session_request.get(login_url)
    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='execution']/@value")))[0]
    result = session_request.post(
        login_url,
        data=payload,
        headers=dict(referer=login_url)
    )

    print(result.ok)                                # to check if successfully logged in



if __name__ == "__main__":
    calculateGPA()
