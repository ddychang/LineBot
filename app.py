from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, MemberJoinedEvent
import os

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 用户状态字典，用来存储每个用户的状态
user_state = {}

questions_answers = {
   '百合':{
        "介紹一下百合": "百合（Yuri）是一種日本文化中常見的術語，用來描述女性之間的浪漫關係或者情感聯繫，通常在動漫、漫畫、文學等媒體中出現。 這種關係可以是友情、戀愛、或者兩者兼而有之，但總體上強調的是女性之間的情感紐帶和親密關係。 百合作品通常描繪女性之間的互動、感情發展和愛情故事，成為了日本流行文化中一個重要的子類別。 ",
        "百合的類型": "百合作品的形式多種多樣，可以是輕鬆的校園愛情故事，也可以是深沉的人生探索，甚至還有奇幻或科幻題材的作品。 它們涵蓋了不同年齡段和興趣領域的讀者，並且在文化中有著廣泛的影響。",
        "主要受眾": "儘管百合作品的主要受眾是女性，但男性讀者也存在，並且這些作品有時候也能夠提供對女性情感和友誼的深刻理解。 在近年來，百合文化也逐漸引起了國際社會的關注，成為了跨越文化界限的文化現象。",
        "推薦一個百合作品": "《終將成為你》（Yagate Kimi ni Naru / Bloom Into You）：讲述了一个对浪漫情感感到迷茫的女孩和一个对她表达爱意的女孩之间的故事，是一部深刻而感人的作品。",
    }
}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'




@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()
    if user_id not in user_state:
        user_state[user_id] = None

    if msg == '介紹百合':
        user_state[user_id] = '百合'
        line_bot_api.reply_message(event.reply_token, TextSendMessage("請輸入想要查詢的關鍵字?"))
    else:
        current_state = user_state[user_id]
        if current_state and msg in questions_answers[current_state]:
            reply = questions_answers[current_state][msg]
            line_bot_api.reply_message(event.reply_token, TextSendMessage(reply))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage("未找到相關答案，請重新輸入相對應的關鍵字"))
@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
