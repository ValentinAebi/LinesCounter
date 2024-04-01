import os
import sys
from typing import List, Dict
from tabulate import tabulate


def is_excluded_filepath(filepath: str) -> bool:
    return (filepath.endswith(".git")
            or filepath.startswith("idea/")
            or filepath.endswith(".venv"))


class Report:
    total_lines: int
    non_empty_lines: int
    file_ext: str

    def __init__(self, total_lines: int, non_empty_lines: int, file_ext: str):
        self.total_lines = total_lines
        self.non_empty_lines = non_empty_lines
        self.file_ext = file_ext

    def to_data(self):
        return [self.file_ext, self.total_lines, self.non_empty_lines]


def combine_reports(reports: List[Report]) -> List[Report]:
    reports_by_ext: Dict[str, Report] = dict()
    for curr_report in reports:
        if curr_report.file_ext in reports_by_ext:
            target_report = reports_by_ext[curr_report.file_ext]
            target_report.total_lines += curr_report.total_lines
            target_report.non_empty_lines += curr_report.non_empty_lines
        else:
            reports_by_ext[curr_report.file_ext] = curr_report
    return list(reports_by_ext.values())


def analyze(filepath: str) -> List[Report]:
    if is_excluded_filepath(filepath):
        return []
    elif os.path.isdir(filepath):
        return combine_reports([r for f in os.listdir(filepath) for r in analyze(filepath + "/" + f)])
    else:
        _, file_ext = os.path.splitext(filepath)
        try:
            with open(filepath, "r") as file:
                lines_cnt = 0
                non_empty_lines_cnt = 0
                for line in file:
                    line: str
                    lines_cnt += 1
                    if len(line.strip()) > 0:
                        non_empty_lines_cnt += 1
            return [Report(total_lines=lines_cnt, non_empty_lines=non_empty_lines_cnt, file_ext=file_ext)]
        except UnicodeDecodeError:
            return []


def main(args: List[str]):
    if len(args) != 1:
        print("the script takes exactly one argument, the path to the root directory of the project", file=sys.stderr)
        exit(-1)
    root_dir = args[0]
    reports = analyze(root_dir)
    reports.sort(key=lambda r: -r.total_lines)
    print("\nNote: lines with comments only are considered non-empty")
    print(tabulate(
        [r.to_data() for r in reports],
        headers=["Extension", "Lines", "Non-empty lines"],
        tablefmt="simple_grid"
    ))


if __name__ == "__main__":
    main(sys.argv[1:])
