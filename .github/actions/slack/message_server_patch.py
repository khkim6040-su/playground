from bullet_list_builder import BulletListBuilder
from message import MsgArg


class ServerPatchMsgArg(MsgArg):
    PARSER_NAME = "server-patch"

    environment: str
    server_name: str
    docker_image: str
    static_data: str
    run_id: str

    def __init__(
        self,
        environment: str,
        server_name: str,
        docker_image: str,
        static_data: str,
        run_id: str,
    ):
        self.environment = environment
        self.server_name = server_name
        self.docker_image = docker_image
        self.static_data = static_data
        self.run_id = run_id

    @staticmethod
    def build_subparser(subparsers):
        parser = subparsers.add_parser(ServerPatchMsgArg.PARSER_NAME)
        parser.add_argument("--environment", required=True, help="서버 환경")
        parser.add_argument("--server-name", required=True, help="서버 이름")
        parser.add_argument("--docker-image", required=True, help="도커 이미지")
        parser.add_argument("--static-data", required=True, help="스태틱 데이터")
        parser.add_argument(
            "--run-id", required=True, help="해당 워크플로우 실행의 run id"
        )

    @staticmethod
    def from_args(args):
        return ServerPatchMsgArg(
            args.environment,
            args.server_name,
            args.docker_image,
            args.static_data,
            args.run_id,
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

    def build_msg(self, global_args):
        dict = {
            "text": f"🚀 {self.environment} 패치 완료",
            "blocks": [],
        }

        self.addHeader(dict["blocks"], f"🚀 {self.environment} 패치 완료")

        builder = BulletListBuilder()
        builder.add_text_item("Server 이름", self.server_name)
        builder.add_text_item("도커 이미지", self.docker_image)
        builder.add_text_item("스태틱 데이터", self.static_data)
        builder.add_hyperlink(
            f"https://github.com/{global_args.repository}/actions/runs/{self.run_id}",
            "Run URL",
        )

        dict["blocks"].append(builder.build())

        return dict
