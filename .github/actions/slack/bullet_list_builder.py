class BulletListBuilder:
    def __init__(self):
        self.bullet_list = []

    def add_text_item(self, key: str, value: str):
        item = {
            "type": "rich_text_section",
            "elements": [
                {"type": "text", "text": f"{key}: "},
                {"type": "text", "text": value},
            ],
        }
        self.bullet_list.append(item)

    def add_hyperlink(self, url: str, alt_text: str):
        item = {
            "type": "rich_text_section",
            "elements": [{"type": "link", "url": url, "text": alt_text}],
        }
        self.bullet_list.append(item)

    def build(self) -> dict:
        dict = {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_list",
                    "style": "bullet",
                    "indent": 0,
                    "elements": [],
                }
            ],
        }

        for item in self.bullet_list:
            dict["elements"][0]["elements"].append(item)

        return dict
