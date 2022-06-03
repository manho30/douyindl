
import re


'''
deternmine the url inside of text
'''
def find_url(string):
    try:
        url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    except:
        url = None
    return url
    
# debug
print(find_url('vkyjgkivutk'))