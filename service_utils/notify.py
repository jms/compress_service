from pubnub import Pubnub


def callback(message, channel):
    print(message)


def error(message):
    print("ERROR : " + str(message))


def connect(pubnub, message):
    print("CONNECTED")
    print pubnub.publish(channel='service_channel', message=message)


def reconnect(message):
    print("RECONNECTED")


def disconnect(message):
    print("DISCONNECTED")


def start_pubnub():
    pubnub = Pubnub(publish_key="pub-c-175764f3-155a-4678-adba-948f6a350717",
                    subscribe_key="sub-c-f75f9c02-517c-11e5-85f6-0619f8945a4f")

    pubnub.subscribe(channels='service_channel', callback=callback, error=callback,
                     connect=connect, reconnect=reconnect, disconnect=disconnect)

    return pubnub
