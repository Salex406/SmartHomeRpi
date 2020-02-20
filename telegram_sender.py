import sys
import telepot
import logging
 
#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                    level=logging.INFO)

#logger = logging.getLogger(__name__)
 
telepot.api.set_proxy('http://127.0.0.1:8118')
 
text = sys.argv[1]
chat_id = 725739430  #telegram id
TOKEN = "723878232:AAGdicggv2sGpZ5EZnRbmNZHd0Uvy_rS89o"
bot = telepot.Bot(TOKEN)
bot.sendMessage(chat_id, str(text))
