
import fbchat
#subclass fbchat.Client and override required methods
class FacebookBot(fbchat.Client):

    def __init__(self,email, password, debug=True, user_agent=None):
        fbchat.Client.__init__(self,email, password, debug, user_agent)

    def on_message_new(self, mid, author_id, message, metadata, recipient_id, thread_type):
        self.markAsDelivered(author_id, mid) #mark delivered
        self.markAsRead(author_id) #mark read

        print("%s said: %s"%(author_id, message))
        #if you are not the author, echo
        if str(author_id) != str(self.uid):
            self.send(recipient_id,message,message_type=thread_type)



fbbot = FacebookBot("xxx", "xxx")
me = fbbot.getAllUsers()[0]
print(fbbot.getThreadList(0))
# fbbot.send(me.uid,"Hej")
# fbbot.send(1605811792768607,"I am in ping mode", message_type='group')
fbbot.listen()


# 1605811792768607