from message import GlobalArgs
from message_fail import FailMsgArg
from message_server_patch import ServerPatchMsgArg
from message_simple import SimpleMsgArg
import argparse
import json
import sys


def build_parser():
    parser = argparse.ArgumentParser(description="Slack CI 메시지 빌더")

    GlobalArgs.build_parser(parser)

    subparsers = parser.add_subparsers(dest="subparser_name")

    FailMsgArg.build_subparser(subparsers)
    ServerPatchMsgArg.build_subparser(subparsers)
    SimpleMsgArg.build_subparser(subparsers)

    return parser


def main(args):
    parser = build_parser()
    args = parser.parse_args(args)
    global_args = GlobalArgs.from_args(args)

    if args.subparser_name == FailMsgArg.PARSER_NAME:
        sub_args = FailMsgArg.from_args(args)
        dict = sub_args.build_msg(global_args)

    elif args.subparser_name == ServerPatchMsgArg.PARSER_NAME:
        sub_args = ServerPatchMsgArg.from_args(args)
        dict = sub_args.build_msg(global_args)

    elif args.subparser_name == SimpleMsgArg.PARSER_NAME:
        sub_args = SimpleMsgArg.from_args(args)
        dict = sub_args.build_msg(global_args)
    else:
        raise SyntaxError("Invalid subparser_name")

    if global_args.test:
        dict["blocks"].insert(
            0,
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*👀 이 메시지는 테스트 메시지입니다!*",
                },
            },
        )

    if global_args.pretty:
        return json.dumps(dict, indent=2, ensure_ascii=False)
    else:
        return json.dumps(dict, ensure_ascii=False)


if __name__ == "__main__":
    result = main(sys.argv[1:])
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(result)
