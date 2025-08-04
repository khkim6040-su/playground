from abc import ABC, abstractmethod
import argparse


class GlobalArgs:
    pretty: bool
    repository: str
    test: bool
    channel_id: str | None
    thread_ts: str | None

    def __init__(self, pretty: bool, repository: str, test: bool, channel_id: str | None, thread_ts: str | None):
        self.pretty = pretty
        self.repository = repository
        self.test = test
        self.channel_id = channel_id
        self.thread_ts = thread_ts

    @staticmethod
    def from_args(args):
        return GlobalArgs(args.pretty, args.repository, args.test, args.channel_id, args.thread_ts)

    @staticmethod
    def build_parser(parser):
        parser.add_argument(
            "--pretty", action="store_true", help="JSON을 보기 좋게 출력", default=False
        )
        parser.add_argument("--repository", required=True, help="GitHub 레포지토리")
        parser.add_argument("--test", action="store_true", help="테스트용 메시지")
        parser.add_argument("--channel-id", required=False, help="메시지를 보낼 Slack 채널 ID")
        parser.add_argument(
            "--thread-ts", required=False, help="스레드 댓글을 달 메세지의 타임스탬프. channel_id와 함께 사용되어야 함"
        )


class MsgArg(ABC):
    @staticmethod
    @abstractmethod
    def build_subparser(subparsers: argparse._SubParsersAction):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def from_args(args):
        raise NotImplementedError

    @abstractmethod
    def build_msg(self, global_args: GlobalArgs) -> dict:
        raise NotImplementedError
