import time
from nyct_gtfs import NYCTFeed
import re
import n2w

def is_now_active(alert):
    for active_period in list(alert.active_period):
        return active_period.start < time.time() < active_period.end or (active_period.start<time.time() and active_period.end==0)


def print_alerts(alert_texts):
    """
    Return the string that contains the alerts in a clear format from alert_texts.

    :param alert_texts: dict(string)
    :return: string
    """

    result=""

    for key in alert_texts.keys():
        if len(alert_texts[key]) == 1:
            result+=f"For the {key} train, there is one alert. \n"
        else:
            result+=f"For the {key} train, there are {n2w.convert(len(alert_texts[key]))} alerts. \n"
        for alert_counter, alert in enumerate(alert_texts[key]):
            result+=f"Number {n2w.convert(alert_counter + 1)}, {alert} \n"

    if result=="":
        result="There are no alerts for your selected lines."

    return result


def parse_alerts(feed, lines):
    """
    Parses the Service Alerts feed from the MTA API. Select the lines that
    user is interested in. Then, store the alerts received from the feed into
    alert_texts

    :param feed: The real-time GTFS feed accessed using the MTA API
    :param lines: String of all lines in concern
    :return: alert_texts: Dictionary that stores the alerts of lines of interest
    """

    alert_texts = {}
    for entity in feed._feed.entity:
        for informed_entity in list(entity.alert.informed_entity):
            if is_now_active(entity.alert):
                try:
                    # filter out alerts related to elevators
                    if informed_entity.agency_id == "MTASBWY" and informed_entity.route_id in lines:
                        header_text = \
                            list(entity.alert.header_text.translation)[0]
                        # remove html tags
                        header_text.text = re.sub(re.compile('<.*?>'), '',
                                                  header_text.text)

                        if informed_entity.route_id not in alert_texts:
                            alert_texts[informed_entity.route_id] = [
                                header_text.text]
                        else:
                            alert_texts[informed_entity.route_id].append(
                                header_text.text)

                # elevators don't have agency_id attribute
                except AttributeError:
                    continue
    return alert_texts


def check_subway(lines):
    """
    Accepts input from Alexa's memory and output a string to serve as speaker
    output

    :param lines: list(char)
    :return: string
    """
    with open("api_file.bin", encoding="utf-8") as binary_file:
        # Read the whole file at once
        api_key = binary_file.read()

    feed = NYCTFeed(lines[0], api_key=str(api_key))
    feed._feed_url = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts"
    feed.refresh()

    alert_texts = parse_alerts(feed, lines)

    return print_alerts(alert_texts)