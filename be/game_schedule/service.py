import dataclasses
import os
import time
from datetime import datetime

from fastapi import HTTPException
from selenium.webdriver.common.by import By

from common.model import MatchModel
from common.mongodb.client import db
from common.selenium import get_webdriver


class ScheduleService:

    def crawl_schedule(self, category="epl") -> list[MatchModel]:

        driver = get_webdriver()

        try:
            matches: list[MatchModel] = []
            today = datetime.now()
            current_month = today.month
            current_year = today.year

            # 스포츠 종목에 따른 URL 구조 설정
            sport_type = "wfootball" if category == "epl" else "basketball"

            for i in range(6):
                target_month = (current_month + i) % 12 or 12
                target_year = current_year + (current_month + i - 1) // 12

                date = datetime(target_year, target_month,
                                1).strftime("%Y-%m-%d")
                url = f"""https://m.sports.naver.com/{
                sport_type}/schedule/index?category={category}&date={date}"""
                driver.get(url)
                time.sleep(2)

                elements = driver.find_elements(
                    By.CSS_SELECTOR, ".ScheduleLeagueType_title__2Kalm"
                )
                match_elements = driver.find_elements(
                    By.CSS_SELECTOR, ".ScheduleLeagueType_match_list__1-n6x"
                )

                for date_element, match_element in zip(elements, match_elements):
                    match_date = date_element.text
                    li_elements = match_element.find_elements(
                        By.CSS_SELECTOR, "li")

                    for li in li_elements:
                        try:
                            match_time = li.find_element(
                                By.CSS_SELECTOR, ".MatchBox_time__nIEfd"
                            )
                            match_status = li.find_element(
                                By.CSS_SELECTOR, ".MatchBox_status__2pbzi"
                            )
                            match_area = li.find_element(
                                By.CSS_SELECTOR, ".MatchBox_match_area__39dEr"
                            )
                            match_areas = match_area.find_elements(
                                By.CSS_SELECTOR, ".MatchBoxTeamArea_team__3aB4O"
                            )
                            link = match_area.find_element(
                                By.CSS_SELECTOR, "a"
                            ).get_attribute("href")
                            actual_time = (
                                match_time.get_attribute("textContent")
                                .strip()
                                .split("\n")[-1][-5:]
                            )

                            # URL에서 날짜 추출 (YYYYMMDD)
                            match_date = link.split("/")[4][:8]
                            year = match_date[:4]
                            month = match_date[4:6]
                            day = match_date[6:8]

                            # 문자열 조합
                            # datetime 객체 생성
                            dt = datetime.strptime(f"{year}-{month}-{day}-{actual_time}", "%Y-%m-%d-%H:%M")
                            match_info = MatchModel(
                                date_time=dt,
                                status=match_status.text,
                                home_team=match_areas[0].text,
                                away_team=match_areas[1].text,
                                league=category.upper(),
                                cheer_url=f"{link}/cheer"
                            )
                            matches.append(match_info)

                        except Exception as e:
                            print(f"매치 파싱 오류: {e}")
                            continue

                time.sleep(1)

            return matches

        finally:
            driver.quit()

    async def update_schedule(self, category: str = 'epl') -> list[MatchModel]:
        try:
            matches: list[MatchModel] = self.crawl_schedule(category)
            db['matches'].insert_many([dataclasses.asdict(match) for match in matches])
            return matches
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_schedules(self, category: str = 'epl') -> list[MatchModel]:
        try:
            matches: list[dict] = db['matches'].find({}, {'_id': 0}).to_list()
            return list(map(lambda x: MatchModel(**x), matches))
        except FileNotFoundError:
            # 파일이 없으면 새로 크롤링
            return await self.update_schedule(category)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def init(self):
        # 서버 시작시 data 디렉토리 확인 및 생성
        if not os.path.exists("data"):
            os.makedirs("data")

        # EPL 스케줄 데이터 확인
        try:
            with open("data/epl_schedule.json", "r", encoding="utf-8"):
                pass
        except FileNotFoundError:
            await self.update_schedule("epl")
