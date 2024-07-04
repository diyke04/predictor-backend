import asyncio
from aiosmtpd.controller import Controller
from email.message import EmailMessage

class CustomHandler:
    async def handle_DATA(self, server, session, envelope):
        print('Message from:', envelope.mail_from)
        print('Message to:', envelope.rcpt_tos)
        print('Message data:', envelope.content.decode('utf8', errors='replace'))
        return '250 Message accepted for delivery'

    async def handle_message(self, message):
        print("message",message)
        pass  # This method is required but can be left empty if not used

def main():
    handler = CustomHandler()
    controller = Controller(handler, hostname='localhost', port=1025)
    controller.start()
    print("SMTP server running at localhost:1025")
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        controller.stop()

if __name__ == '__main__':
    main()
