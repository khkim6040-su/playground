#!/usr/bin/env python3
import argparse
import sys

def check_map_data():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="데이터 이름 (CoreVersionMap 등)")
    parser.add_argument("--data", required=True, help="세미콜론(;)으로 구분된 값 리스트")
    args = parser.parse_args()

    name = args.name
    data = args.data.strip()

    # 데이터 없으면 그냥 통과
    if not data:
        return

    values = data.split(";")

    # 하이픈 체크
    for value in values:
        if "-" not in value:
            print(f"입력된 {name}에 하이픈 '-'이 포함되지 않은 값이 있습니다: {value}")
            return

    # 중복 키 체크 (첫 하이픈 앞 부분만 키로 사용)
    keys = [v.split("-", 1)[0] for v in values]
    duplicates = set(k for k in keys if keys.count(k) > 1)
    if duplicates:
        print(f"입력된 {name}에 중복된 키가 있습니다: {','.join(duplicates)}")
        return

    # 에러 없으면 빈 출력으로 정상 종료
    return


if __name__ == "__main__":
    check_map_data()