import argparse
import collections
import json
import os
import re

parser = argparse.ArgumentParser(description="Process access.log")
parser.add_argument(dest="log", action="store", help="Path to log file or directory")

args = parser.parse_args()


def logs_parser(logs):
    dict_ip = {"TOTAL": 0, "METHOD": {"POST": 0, "GET": 0, "DELETE": 0, "PUT": 0, "HEAD": 0, "OPTIONS": 0}}
    dict_ip_requests = collections.defaultdict(lambda: {"REQUESTS_QUANTITY": 0})
    list_ip_duration = []

    with open(logs) as log:

        for line in log:
            method = re.search(r"\] \"(POST|GET|PUT|DELETE|HEAD|OPTIONS)", line)
            ip = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line).group()
            duration = int(line.split()[-1])
            date = re.search(r"\[\d.*?\]", line)
            url = re.search(r"\"http.*?\"", line)

            dict_ip["TOTAL"] += 1

            if method is not None:

                dict_ip["METHOD"][method.group(1)] += 1
                dict_ip_requests[ip]["REQUESTS_QUANTITY"] += 1

                dict_long = {"METHOD": method.group(1),
                             "URL": "-",
                             "IP": ip,
                             "DURATION": duration,
                             "DATE": date.group(0).split(" ")[0].lstrip("["),

                             }

                if url is not None:
                    dict_long["URL"] = url.group(0).strip("\"")

                list_ip_duration.append(dict_long)

        top3request = dict(sorted(dict_ip_requests.items(), key=lambda x: x[1]["REQUESTS_QUANTITY"], reverse=True)[0:3])
        top3long = sorted(list_ip_duration, key=lambda x: x["DURATION"], reverse=True)[0:3]

        result = {"requests_quantity": dict_ip["TOTAL"],
                  "quantity_by_http": dict_ip["METHOD"],
                  "top3_ip_with_requests": top3request,
                  "top3_longest_requests": top3long
                  }

        with open("result.json", "w") as file:
            result = json.dumps(result, indent=4)
            file.write(result)
            print(result)


if args.log is not None:
    if os.path.isfile(args.log):
        logs_parser(logs=args.log)

    elif os.path.isdir(args.log):
        for file in os.listdir(args.log):
            if file.endswith(".log"):
                path_to_logfile = os.path.join(args.log, file)
                logs_parser(logs=path_to_logfile)

    else:
        print("Введен некорректный путь к файлу с логом")
