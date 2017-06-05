from datetime import datetime
from pytz import timezone

FILENAME = "log.txt"

'''
Writes a message to the log file

content: String - message being logged
'''
def log_message(content):
    with open(FILENAME, "a") as fp:
        fp.write(timestamp() + " | " + content + "\n")

'''
Writes a request to a log file

message: Object - message object of requester
'''
def log_request(message, request_name=None):
    content = ""
    if request_name != None:
        content += request_name.title() + " "

    content += "from " + message.author.name + "(" + message.author.id + ") "
    content += "in " + message.server.name + " #" + message.channel.name

    log_message(content)

'''
Gets the current timestamp

return: String - timestamp
'''
def timestamp():
    time = datetime.now(timezone("US/Eastern"))
    return time.strftime("%Y-%m-%d %I:%M:%S %p")
