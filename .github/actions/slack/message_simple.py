import argparse
from message import MsgArg, GlobalArgs


class SimpleMsgArg(MsgArg):
    PARSER_NAME = "simple"
    msg: str
    push_msg: str

    def __init__(self, msg: str, push_msg: str):
        self.msg = msg
        self.push_msg = push_msg

    @staticmethod
    def build_subparser(subparsers):
        parser = subparsers.add_parser(
            SimpleMsgArg.PARSER_NAME,
            help="간단한 메시지를 생성합니다.",
        )
        parser.add_argument("--msg", required=True, help="메시지 본문")
        parser.add_argument("--push-msg", required=True, help="푸시 알림 메시지")

    @staticmethod
    def from_args(args):
        return SimpleMsgArg(args.msg, args.push_msg)

    def build_msg(self, global_args):
        dict = {
            "text": self.push_msg,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{self.msg}```",  # 슬랙에서 메세지간 구분이 뚜렷하지 않아서 코드 블록으로 감쌈, 마크다운 인젝션 문제 있음
                    },
                },
            ],
        }

        return dict
