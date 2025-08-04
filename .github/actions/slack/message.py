from abc import ABC, abstractmethod
import argparse


class GlobalArgs:
    pretty: bool
    repository: str
    test: bool

    def __init__(self, pretty: bool, repository: str, test: bool):
        self.pretty = pretty
        self.repository = repository
        self.test = test

    @staticmethod
    def from_args(args):
        return GlobalArgs(args.pretty, args.repository, args.test)

    @staticmethod
    def build_parser(parser):
        parser.add_argument(
            "--pretty", action="store_true", help="JSON을 보기 좋게 출력", default=False
        )
        parser.add_argument("--repository", required=True, help="GitHub 레포지토리")
        parser.add_argument("--test", action="store_true", help="테스트용 메시지")


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
