import argparse
from bullet_list_builder import BulletListBuilder
from message import MsgArg, GlobalArgs


class FailMsgArg(MsgArg):
    PARSER_NAME = "fail"

    workflow: str
    commit_sha: str
    ref: str
    actor: str
    run_id: str
    commit_msg: str | None
    extra_msg: str | None
    channel_id: str | None
    thread_ts: str | None

    def __init__(
        self,
        workflow: str,
        commit_sha: str,
        ref: str,
        actor: str,
        run_id: str,
        commit_msg: str | None,
        extra_msg: str | None,
        channel_id: str | None = None,
        thread_ts: str | None = None,
    ):
        self.workflow = workflow
        self.commit_sha = commit_sha
        self.ref = ref
        self.actor = actor
        self.run_id = run_id
        self.commit_msg = FailMsgArg.normalize(commit_msg)
        self.extra_msg = FailMsgArg.normalize(extra_msg)
        self.channel_id = channel_id
        self.thread_ts = thread_ts
        
    @staticmethod
    def normalize(text: str | None) -> str | None:
        if text is None:
            return None

        text = text.strip()

        if text:
            return text

        return None

    @staticmethod
    def build_subparser(subparsers: argparse._SubParsersAction):
        parser = subparsers.add_parser(
            FailMsgArg.PARSER_NAME,
            help="실패한 워크플로우 실행에 대한 메시지를 생성합니다.",
        )
        parser.add_argument("--workflow", required=True, help="워크플로우 이름")
        parser.add_argument(
            "--commit-sha", required=True, help="해당 워크플로우를 유발한 커밋"
        )
        parser.add_argument("--ref", required=True, help="해당 워크플로우를 유발한 ref")
        parser.add_argument(
            "--actor", required=True, help="해당 워크플로우를 유발한 사용자"
        )
        parser.add_argument(
            "--run-id", required=True, help="해당 워크플로우 실행의 run id"
        )
        parser.add_argument(
            "--commit-msg", help="해당 워크플로우를 유발한 커밋의 메시지"
        )
        parser.add_argument(
            "--channel_id", help="메시지를 보낼 채널 ID", required=True
        )
        parser.add_argument(
            "--thread-ts", help="메시지를 보낼 스레드의 타임스탬프"
        )
        parser.add_argument("--extra-msg", help="추가 정보")

    @staticmethod
    def from_args(args):
        return FailMsgArg(
            args.workflow,
            args.commit_sha,
            args.ref,
            args.actor,
            args.run_id,
            args.commit_msg,
            args.extra_msg,
            args.channel_id,
            args.thread_ts,
        )

    # 메세지 간의 경계가 슬랙에서 뚜렷하지 않아서 코드 블록으로 감쌈
    # 마크 다운 인젝션 문제가 있는 코드임
    # 고려해본 대안:
    #  - divider는 선이 얇아서 가시성이 뚜렷하지 않음
    #  - header는 볼드체인데 가시성이 뚜렷하지 않음
    #  - `text`는 text에 개행이 들어가면 깨져서 사용할 수 없음
    @staticmethod
    def addHeader(blocks: list, text):
        blocks.insert(
            0,
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{text}```",
                },
            },
        )

    def build_blocks(self, global_args: GlobalArgs):
        blocks = []
        self.addHeader(blocks, f"{self.workflow} 성공")

        if self.extra_msg:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": f"추가정보:\n{self.extra_msg}",
                    },
                }
            )

        if self.commit_msg:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": f"커밋 메시지:\n{self.commit_msg}",
                    },
                }
            )

        builder = BulletListBuilder()

        builder.add_text_item("COMMIT", self.commit_sha)
        builder.add_text_item("REF", self.ref)
        builder.add_text_item("USER", self.actor)
        builder.add_hyperlink(
            f"https://github.com/{global_args.repository}/commit/{self.commit_sha}",
            "Commit URL",
        )
        builder.add_hyperlink(
            f"https://github.com/{global_args.repository}/actions/runs/{self.run_id}",
            "Run URL",
        )

        blocks.append(builder.build())
        return blocks

    def build_msg(self, global_args: GlobalArgs):
        dict = {
            "text": f"서버패치 결과 스레드 댓글 워크플로우 {self.workflow} 테스트",
            "blocks": self.build_blocks(global_args),
        }
        if global_args.channel_id:
            dict["channel"] = global_args.channel_id
        if global_args.thread_ts:
            dict["thread_ts"] = global_args.thread_ts
            dict["reply_broadcast"] = True

        return dict
