"""
A Simple Slido Voting Bot
"""
from argparse import ArgumentParser
from requests.exceptions import HTTPError
from json import JSONDecodeError
from typing import Optional, Tuple
from random import randint
from time import sleep

import settings
import requests

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
settings.setup_logger(logger)

def log(message: str):
    # add telegram support
    for msg in message.split('\n'):
        logger.info(msg)


class SlidoService:
    def __init__(self, slido_url: str) -> None:
        self.event_hash: str = self._parse_event_hash(slido_url)
        self.uuid: str = self._get_uuid_from_event_hash(self.event_hash)
        self.access_token: str = None
        self.event_id: str = None
        self.event_section_id: str = None
        self.question_ids: list = None

    def __post(self, url: str, json: dict = None, headers: dict = None, cookies: dict = None) -> Optional[dict]:
        response = requests.post(url, json=json, headers=headers, cookies=cookies)
        result = None
        log(
            f'POST "{url.replace(settings.API, "")}" - {response.status_code}\n'
            f'Request json: {json}\n'
            f'Request headers: {headers}\n'
            f'Request cookies: {cookies}\n'
        )
        try:
            response.raise_for_status()
            result: dict = response.json()
        except (HTTPError, JSONDecodeError):
            log(
                f'Request failed...\n'
            )
        return result

    def __get(self, url: str, params: dict = None, headers: dict = None) -> Optional[dict]:
        response = requests.get(url, params=params, headers=headers)
        result = None        
        log(
            f'GET "{url}" - {response.status_code}\n'
            f'Request params: {params}\n'
            f'Request headers: {headers}\n'
        )
        try:
            response.raise_for_status()
            result: dict = response.json()
        except (HTTPError, JSONDecodeError):
            log(
                f'Request failed...\n'
            )
        return result

    def _parse_event_hash(self, url: str) -> str:
        # TODO: Validate URL

        # logic to extract url hash
        event_hash = url.split('/event/')[1]
        if '/' in event_hash:
            event_hash = event_hash.split('/')[0]
        print(f'Event Hash: {event_hash}')
        return event_hash

    def _get_uuid_from_event_hash(self, event_hash: str) -> str:
        url = f"{settings.API}/app/events"
        params = dict(hash=event_hash)
        result = self.__get(url, params=params)

        uuid = result.get('uuid', None)
        if uuid is None:
            raise Exception

        self.uuid = uuid
        print(f'UUID: {uuid}')
        return uuid

    def _get_access_token(self) -> str:
        uuid = self.uuid
        if uuid is None:
            # raise error for uuid not set (part of user input)
            raise Exception

        url = f"{settings.API}/events/{uuid}/auth"
        headers = settings.get_headers()
        result = self.__post(url, headers=headers)

        if result is not None:
            access_token = result.get('access_token', None)
        else:
            access_token = None        
        
        self.access_token = access_token
        return access_token, headers

    def _get_event_details(self) -> Tuple[str]:
        uuid = self.uuid
        if uuid is None:
            # raise error for uuid not set (part of user input)
            raise Exception
        
        access_token = self.access_token
        if access_token is None:
            access_token, headers = self._get_access_token()

        url = f"{settings.API}/events/{uuid}/summary"
        headers = dict(authorization=f"Bearer {access_token}")
        headers.update(settings.get_headers())
        result = self.__get(url, headers=headers)

        # TODO: add support for multiple sections
        event_section_uuids = [
            section_id for section_id in result.get('bySection').keys()
        ]
        event_section_uuid = event_section_uuids[0]

        url = f"{settings.API}/events/{uuid}/sections/{event_section_uuid}/statusbar"
        headers = dict(authorization=f"Bearer {access_token}")
        headers.update(settings.get_headers())
        result = self.__get(url, headers=headers)

        event_id = result.get('event_id')
        event_section_id = result.get('event_section_id')
        self.event_id = event_id
        self.event_section_id = event_section_id

        return event_id, event_section_id

    def ask_question(self, question: str) -> dict:
        uuid = self.uuid
        if uuid is None:
            # raise error for uuid not set (part of user input)
            raise Exception
        
        access_token = self.access_token
        if access_token is None:
            access_token, headers = self._get_access_token()
        
        event_id = self.event_id
        event_section_id = self.event_section_id
        if event_id is None or event_section_id is None:
            event_id, event_section_id = self._get_event_details()

        url = f"{settings.API}/events/{self.uuid}/questions"
        data = {
            "event_id": event_id,
            "event_section_id": event_section_id,
            "is_anonymous": True,
            "text": question
        }
        headers = dict(authorization=f"Bearer {access_token}")
        headers.update(settings.get_headers())
        result = self.__post(url, json=data, headers=headers)

        return result

    def vote_questions(
        self,
        question_list: list,
        vote_count: int,
        retry_count: int = 3,
        random_sleep_duration: int = 2
    ) -> None:
        uuid = self.uuid
        if uuid is None:
            # raise error for uuid not set (part of user input)
            raise Exception
        
        access_token = self.access_token
        if access_token is None:
            access_token, headers = self._get_access_token()


        #question_list = ['84261034','84261027','84261016', '84260998','84260981','84260958','84260953','84260946','84260907','84260882','84140435','84117351','84261022']
        for i in range(vote_count):
            log(f'Executing vote {i}')
            sleep(randint(2, random_sleep_duration))  # to bypass rate limiter
            access_token, headers = self._get_access_token()
            sleep(randint(2, random_sleep_duration))  # to bypass rate limiter

            headers = dict(authorization=f"Bearer {access_token}")
            headers.update(settings.get_headers())


            for question_id in question_list:
                retry_count = 3
                url = f"{settings.API}/events/{uuid}/questions/{question_id}/like"
                data = {"score": 1}
                cookie = {"Slido.EventAuthTokens": "{uuid},{access_token}"}

                while retry_count > 0:
                    result = self.__post(url, headers=headers, json=data, cookies=cookie)
                    sleep(1+ (0.1*randint(1, 5)))  # to bypass rate limiter
                    if result is None:
                        print(f'Failed to vote for question {question_id}, retrying...')
                        sleep(1+ (0.1*randint(1, 5)))  # to bypass rate limiter
                        retry_count -= 1
                        continue
                    print(f'Voted for question {question_id}')
                    break


# Instantiate the parser
def setup_parsers() -> ArgumentParser:
    parser = ArgumentParser(description='A Simple Slido Voter Bot')
    parser.add_argument('-u', metavar='<url>', nargs=1,
                        required=True, help='url for event')
    parser.add_argument('-v', metavar='<vote count>', nargs=1, type=int,
                        required=True, help='number of votes to add to each question')
    parser.add_argument('-q', metavar='<question list>', nargs='+',
                        required=True, help='list of question ids to vote for (space separated)')
    return parser


def main():
    parser = setup_parsers()
    args = parser.parse_args()
    slido_url = args.u[0]
    vote_count = int(args.v[0])
    question_list = args.q
    print(f'Question List: {question_list}')
    
    slido_service = SlidoService(slido_url)
    from time import time
    start = time()
    slido_service.vote_questions(question_list, vote_count)
    duration = time() - start
    print(f'TOTAL TIME TAKEN: {round(duration, 2)}s')


if __name__ == '__main__':
    main()