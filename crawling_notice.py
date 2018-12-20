from selenium import webdriver
from bs4 import BeautifulSoup

def Notice_Crawling () :
    driver = webdriver.Chrome("C:/taekhwan/chromedriver.exe")
    driver.get("https://edu.ssafy.com/comm/login/SecurityLoginForm.do")
    driver.implicitly_wait(3)

    # 아이디, 패스워드 입력
    driver.find_element_by_xpath("//*[@id='userId']").send_keys("b2narae@gmail.com")
    driver.find_element_by_xpath("//*[@id='userPwd']").send_keys("sam!3821819")
    driver.find_element_by_xpath("//*[@id='wrap']/div/div/div[4]/form/div/div[2]/div[3]/a").click()
    driver.implicitly_wait(10)

    # 알림함 목록
    driver.get("https://edu.ssafy.com/edu/mycampus/notification/notificationList.do")
    new_value = driver.find_element_by_css_selector('#paging > li.num.is-active').text

    attend = []
    note = []
    notice = []
    question = []
    time_sorted = {}

    while 1 :
        old_value = new_value
        print(" 작업중 ====== ")

        # ============== page source 받아 오기! =================
        sourcecode = driver.page_source # page source 받기 (str)
        soup = BeautifulSoup(sourcecode, 'html.parser') # 실제 코드

        # ============== 게시글 개수 파악! =================
        for all_list in soup.find_all('li', class_="position-base"):
            soup2 = BeautifulSoup(str(all_list), 'html.parser')

        # ============== for 문 불필요 =================
            if (len(soup2.find_all('img', {'alt' : '읽음'})) != 0) :
                for category in soup2.find_all('span', class_="text-group"):
                    cate = category.get_text()
                    content = soup2.find_all('a', class_="title")[0].get_text()
                    time_idx = soup2.find_all('span', class_="time")[0].get_text().replace('\t','').replace('\n','').replace(' ', '')
                    time_date = time_idx[:10]
                    time_clock = time_idx[10:]

                    time_sorted[time_idx] = content

                    print(''.join(time_date).join(' 날'))
                    print(''.join(time_clock).join(' 시'))

                    # print(type(content)) # string
                    if cate == '출석':
                        attend.append(content)
                    elif cate == '쪽지':
                        note.append(content)
                    elif cate == '공지':
                        notice.append(content)
                    elif cate == '1:1문의':
                        question.append(content)

        driver.find_element_by_css_selector("#paging > li.next > a").click()
        new_value = driver.find_element_by_css_selector('#paging > li.num.is-active').text

        if old_value == new_value:
            break
        else:
            print("한 페이지 끝 ======")

    print()

'''
    print("======================")
    print("카테고리별 분류")
    print(attend)
    print(note)
    print(notice)
    print(question)

    print("======================")
    print("시간별 분류")
    print(time_sorted) #시간 순서대로 가져옴
'''

if __name__ == '__main__':
    print("here")
    practice()
    #Notice_Crawling()