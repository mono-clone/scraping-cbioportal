import os
import sys
import time
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager


def make_dir(dir_name: str):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def rename_tsv(dir_name: str, id: str):
    if os.path.exists(dir_name):
        os.rename("{0}/table.tsv".format(dir_name), "{0}/{1}.tsv".format(dir_name, id))


class WebDriverModule(object):
    def __init__(self, save_dir):
        self.save_dir = save_dir
        make_dir(os.getcwd() + save_dir)

    def getFirefoxDriver(self) -> WebDriver:
        return webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=self.getFirefoxOptions(),
        )

    def getFirefoxOptions(self) -> webdriver.FirefoxOptions:
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", os.getcwd() + self.save_dir)
        return options


def scraping_pathways():
    _save_dir = "results/mutations"

    patient_ids = pd.read_csv("patient_ids.csv").values
    patient_ids = patient_ids.tolist()

    webDriverModule = WebDriverModule(_save_dir)
    driver = webDriverModule.getFirefoxDriver()

    for patient_id in patient_ids:
        patient_id = patient_id[0]
        # webドライバーの取得
        # スクレイピング先URL
        url = "https://www.cbioportal.org/patient/pathways?studyId=brca_metabric&caseId={0}".format(
            patient_id
        )
        driver.get(url)
        print(driver.current_url)

        # スクレイピング開始
        driver.implicitly_wait(60)
        # チェックボックスのクリック
        element = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div[2]/div/div/div/div/div/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div[2]/div/label/input",
        )
        driver.execute_script("arguments[0].click();", element)

        # データダウンロードボタンのクリック
        driver.implicitly_wait(60)
        element = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div[2]/div/div/div/div/div/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div[1]/div[1]/div/span/div/button[2]",
        )
        driver.execute_script("arguments[0].click();", element)
        time.sleep(1)
        # ダウンロードしたファイルのrename
        rename_tsv(os.getcwd() + _save_dir, patient_id)

    driver.quit()


def scraping_mutation():
    _save_dir = "results/mutation"

    patient_ids = pd.read_csv("patient_ids.csv").values
    patient_ids = patient_ids.tolist()

    webDriverModule = WebDriverModule(_save_dir)
    driver = webDriverModule.getFirefoxDriver()

    for patient_id in patient_ids:
        patient_id = patient_id[0]
        # webドライバーの取得
        # スクレイピング先URL
        url = "https://www.cbioportal.org/patient/summary?studyId=brca_metabric&caseId={0}".format(
            patient_id
        )
        driver.get(url)
        print(driver.current_url)

        # データダウンロードボタンのクリック
        driver.implicitly_wait(60)
        element = driver.find_element(
            By.CSS_SELECTOR,
            "span.pull-right:nth-child(1) > div:nth-child(1) > button:nth-child(2)",
        )
        driver.execute_script("arguments[0].click();", element)
        time.sleep(1)
        # ダウンロードしたファイルのrename
        rename_tsv(os.getcwd() + _save_dir, patient_id)
    driver.quit()


def scraping_cna():
    _save_dir = "results/cna"

    patient_ids = pd.read_csv("patient_ids.csv").values
    patient_ids = patient_ids.tolist()

    webDriverModule = WebDriverModule(_save_dir)
    driver = webDriverModule.getFirefoxDriver()

    for patient_id in patient_ids:
        patient_id = patient_id[0]
        # webドライバーの取得
        # スクレイピング先URL
        url = "https://www.cbioportal.org/patient/summary?studyId=brca_metabric&caseId={0}".format(
            patient_id
        )
        driver.get(url)
        print(driver.current_url)

        try:
            # データダウンロードボタンのクリック
            driver.implicitly_wait(10)
            element = driver.find_element(
                By.CSS_SELECTOR,
                "span.pull-right:nth-child(3) > div:nth-child(1) > button:nth-child(2)",
            )
            driver.execute_script("arguments[0].click();", element)
            time.sleep(1)
            # ダウンロードしたファイルのrename
            rename_tsv(os.getcwd() + _save_dir, patient_id)
        # データが空っぽの場合がある
        except NoSuchElementException:
            driver.implicitly_wait(10)
            element = driver.find_element(
                By.CSS_SELECTOR,
                "html.cbioportal-frontend body.Firefox div#reactRoot div div.contentWrapper div.mainContainer div.contentWidth.noMargin div#mainColumn div div.patientViewPage div#patientViewPageTabs.msk-tabs.posRelative.mainTabs div.tab-content div.msk-tab div div.alert.alert-info p",
            )
            if element.text == "Sample1 not profiled for copy number alterations":
                print(patient_id, ": ", element.text)
                continue
            # 偶発的にelementを取得できなかった場合
            else:
                print("error")
                return
    driver.quit()


if __name__ == "__main__":
    # scraping_pathways()
    # scraping_mutation()
    scraping_cna()
